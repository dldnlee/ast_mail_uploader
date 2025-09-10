#!/usr/bin/env python3
"""
Gmail Mail Processor for Supabase Integration

This script processes Gmail messages, extracts sender information,
summarizes content using OpenAI, and stores data in Supabase tables.
"""

import os
import json
import base64
import logging
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from email.mime.text import MIMEText
from email.utils import parseaddr

import openai
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from supabase import create_client, Client
from email_validator import validate_email, EmailNotValidError
from email_extractor import EmailExtractor

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Load environment variables from embedded .env file or local one
env_path = get_resource_path('.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()  # Try local .env as fallback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailProcessor:
    def __init__(self):
        self.supabase: Client = self._init_supabase()
        self.gmail_service = self._init_gmail_service()
        self.openai_client = self._init_openai()
        self.email_extractor = EmailExtractor(self.openai_client)
        self.user_email = self._get_user_email()
        
    def _init_supabase(self) -> Client:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        return create_client(url, key)
    
    def _init_gmail_service(self):
        creds = None
        token_path = os.getenv('GMAIL_TOKEN_PATH', 'token.json')
        
        # Try to find credentials.json - first check for embedded, then local
        embedded_credentials = get_resource_path('credentials.json')
        local_credentials = 'credentials.json'
        
        if os.path.exists(embedded_credentials):
            credentials_path = embedded_credentials
        elif os.path.exists(local_credentials):
            credentials_path = local_credentials
        else:
            credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(f"Gmail credentials file not found at {credentials_path}. Please ensure credentials.json exists or is properly embedded.")
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def _init_openai(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        
        client = openai.OpenAI(api_key=api_key)
        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        return {'client': client, 'model': model}
    
    def _get_user_email(self) -> str:
        try:
            profile = self.gmail_service.users().getProfile(userId='me').execute()
            return profile['emailAddress']
        except Exception as e:
            logger.error(f"Error getting user email: {e}")
            return 'unknown@example.com'
    
    def _extract_email_from_address(self, address: str) -> Optional[str]:
        try:
            name, email_addr = parseaddr(address)
            if email_addr:
                validate_email(email_addr)
                return email_addr.lower()
        except (EmailNotValidError, Exception) as e:
            logger.warning(f"Invalid email address {address}: {e}")
        return None
    
    def _extract_name_from_address(self, address: str) -> Optional[str]:
        name, email_addr = parseaddr(address)
        return name.strip() if name.strip() else None
    
    def find_or_create_company_entity(self, email: str, name: Optional[str] = None, 
                                    subject: str = "", body_content: str = "") -> Optional[str]:
        try:
            response = self.supabase.table('company_entity').select('id, phone_num, position, category').eq('email', email).execute()
            
            if response.data:
                existing_entity = response.data[0]
                logger.info(f"Found existing company entity for {email}")
                
                # Check if we need to update missing information
                needs_update = (
                    not existing_entity.get('phone_num') or 
                    not existing_entity.get('position') or 
                    not existing_entity.get('category')
                )
                
                if needs_update and (subject or body_content):
                    # Extract additional information
                    sender_info = f"{name} <{email}>" if name else email
                    extracted_info = self.email_extractor.extract_all_information(subject, body_content, sender_info)
                    
                    update_data = {}
                    if not existing_entity.get('phone_num') and extracted_info.get('phone_numbers'):
                        update_data['phone_num'] = extracted_info['phone_numbers'][0]  # Take first phone
                    
                    if not existing_entity.get('position') and extracted_info.get('sender_position'):
                        update_data['position'] = extracted_info['sender_position']
                    
                    if not existing_entity.get('category') and extracted_info.get('company_categories'):
                        update_data['category'] = extracted_info['company_categories']
                    
                    # Update if we have new information
                    if update_data:
                        update_response = self.supabase.table('company_entity').update(update_data).eq('id', existing_entity['id']).execute()
                        if update_response.data:
                            logger.info(f"Updated company entity {email} with extracted info: {update_data}")
                
                return existing_entity['id']
            
            # Create new entity with extracted information
            sender_info = f"{name} <{email}>" if name else email
            extracted_info = self.email_extractor.extract_all_information(subject, body_content, sender_info)
            
            entity_data = {
                'email': email,
                'name': name or email.split('@')[0],
                'company': email.split('@')[1] if '@' in email else None,
                'phone_num': extracted_info.get('phone_numbers', [None])[0] if extracted_info.get('phone_numbers') else None,
                'position': extracted_info.get('sender_position'),
                'category': extracted_info.get('company_categories')
            }
            
            response = self.supabase.table('company_entity').insert(entity_data).execute()
            
            if response.data:
                logger.info(f"Created new company entity for {email} with extracted info")
                return response.data[0]['id']
            
        except Exception as e:
            logger.error(f"Error managing company entity for {email}: {e}")
        
        return None
    
    def summarize_email_content(self, subject: str, body: str) -> str:
        try:
            prompt = f"""
            Summarize this email in Korean with 2-3 sentences. Focus on main purpose, key information, and action items. Return ONLY the summary text without any explanations, thinking process, or formatting:
            
            Subject: {subject}
            Body: {body}...
            """

            response = self.openai_client['client'].chat.completions.create(
                model=self.openai_client['model'],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            return content
            
        except Exception as e:
            logger.error(f"Error summarizing email: {e}")
            return f"요약 생성 실패: {subject}"
    
    def _decode_message_part(self, part: Dict) -> str:
        data = part.get('body', {}).get('data', '')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        return ''
    
    def _extract_text_from_message(self, payload: Dict) -> str:
        text_content = ""
        
        if payload.get('mimeType') == 'text/plain':
            text_content = self._decode_message_part(payload)
        elif payload.get('mimeType') == 'text/html':
            html_content = self._decode_message_part(payload)
            text_content = re.sub(r'<[^>]+>', '', html_content)
        elif payload.get('parts'):
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    text_content += self._decode_message_part(part)
                elif part.get('mimeType') == 'text/html':
                    html_content = self._decode_message_part(part)
                    text_content += re.sub(r'<[^>]+>', '', html_content)
        
        return text_content.strip()
    
    def process_email(self, message_id: str) -> bool:
        try:
            message = self.gmail_service.users().messages().get(
                userId='me', 
                id=message_id,
                format='full'
            ).execute()
            
            payload = message['payload']
            headers = payload.get('headers', [])
            
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_address = next((h['value'] for h in headers if h['name'] == 'From'), '')
            date_header = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            email_addr = self._extract_email_from_address(from_address)
            sender_name = self._extract_name_from_address(from_address)
            
            if not email_addr:
                logger.warning(f"Could not extract valid email from: {from_address}")
                return False
            
            body_content = self._extract_text_from_message(payload)
            
            company_entity_id = self.find_or_create_company_entity(email_addr, sender_name, subject, body_content)
            if not company_entity_id:
                logger.error(f"Failed to create/find company entity for {email_addr}")
                return False
            
            original_content = f"From: {from_address}\nSubject: {subject}\n\n{body_content}"
            
            summary = self.summarize_email_content(subject, body_content)
            
            received_date = None
            if date_header:
                try:
                    from email.utils import parsedate_to_datetime
                    received_date = parsedate_to_datetime(date_header).isoformat()
                except:
                    logger.warning(f"Could not parse date: {date_header}")
            
            mail_data = {
                'title': subject,
                'original_content': original_content,
                'summarized_content': summary,
                'received_date': received_date,
                'company_entity_id': company_entity_id,
                'receiver_mail': self.user_email
            }
            
            response = self.supabase.table('mail_history').insert(mail_data).execute()
            
            if response.data:
                logger.info(f"Successfully processed email: {subject}")
                return True
            else:
                logger.error(f"Failed to insert mail history for: {subject}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing email {message_id}: {e}")
            return False
    
    def get_messages(self, query: str = '', max_results: int = 100) -> List[str]:
        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            return [msg['id'] for msg in messages]
            
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            return []
    
    def process_all_messages(self, query: str = '', max_results: int = 100):
        logger.info(f"Starting to process emails with query: '{query}', max_results: {max_results}")
        
        message_ids = self.get_messages(query, max_results)
        logger.info(f"Found {len(message_ids)} messages to process")
        
        processed_count = 0
        failed_count = 0
        
        for i, message_id in enumerate(message_ids, 1):
            logger.info(f"Processing message {i}/{len(message_ids)}: {message_id}")
            
            if self.process_email(message_id):
                processed_count += 1
            else:
                failed_count += 1
        
        logger.info(f"Processing completed. Processed: {processed_count}, Failed: {failed_count}")

def main():
    processor = GmailProcessor()
    
    query = input("Enter Gmail search query (press Enter for all recent emails): ").strip()
    
    max_results_input = input("Enter maximum number of emails to process (default: 10): ").strip()
    max_results = int(max_results_input) if max_results_input.isdigit() else 10
    
    processor.process_all_messages(query, max_results)

if __name__ == "__main__":
    main()