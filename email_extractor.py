#!/usr/bin/env python3
"""
Email Information Extractor

This module extracts phone numbers, company categories, and sender positions
from email content using OpenAI and regex patterns.
"""

import re
import logging
from typing import List, Optional, Dict, Any
import openai

logger = logging.getLogger(__name__)

class EmailExtractor:
    def __init__(self, openai_client: Dict[str, Any]):
        """
        Initialize the email extractor
        
        Args:
            openai_client: Dictionary containing OpenAI client and model info
        """
        self.openai_client = openai_client
        
        # Korean phone number patterns
        self.phone_patterns = [
            r'(?:전화|휴대폰|핸드폰|연락처|Tel|Phone|Mobile|HP|M\.P)\s*:?\s*([0-9]{2,3}-[0-9]{3,4}-[0-9]{4})',
            r'(?:T|전화)\s*[\.:]\s*([0-9]{2,3}-[0-9]{3,4}-[0-9]{4})',
            r'([0-9]{3}-[0-9]{4}-[0-9]{4})',  # 010-1234-5678 format
            r'([0-9]{2,3}-[0-9]{3,4}-[0-9]{4})',  # General Korean format
            r'(\+82-[0-9]{1,2}-[0-9]{3,4}-[0-9]{4})',  # International format
            r'(\+82\s?[0-9]{1,2}\s?[0-9]{3,4}\s?[0-9]{4})',  # International with spaces
        ]
        
        # Common job position keywords in Korean and English
        self.position_keywords = [
            # Management
            r'(?:대표이사|대표|CEO|사장|부사장|이사|상무|전무|회장|부회장)',
            r'(?:팀장|부팀장|팀원|매니저|Manager|Director|VP|Vice President)',
            r'(?:과장|차장|부장|실장|센터장|지점장|본부장)',
            
            # Marketing & Sales
            r'(?:마케팅|영업|세일즈|Sales|Marketing|MD|상품기획)',
            r'(?:브랜드매니저|Brand Manager|마케터|Marketer)',
            r'(?:영업대표|영업팀장|Sales Rep|Account Manager)',
            
            # Development & Tech
            r'(?:개발자|Developer|프로그래머|Programmer|엔지니어|Engineer)',
            r'(?:기술|테크|Tech|CTO|개발팀장)',
            
            # Design & Creative
            r'(?:디자이너|Designer|크리에이티브|Creative|아트디렉터|Art Director)',
            
            # HR & Admin
            r'(?:인사|HR|총무|경영지원|기획|Planning)',
            
            # Others
            r'(?:컨설턴트|Consultant|어시스턴트|Assistant|매니저|Manager)',
            r'(?:담당자|책임자|주임|사원|직원|Staff)',
        ]
        
        # Industry/company category keywords
        self.category_keywords = [
            # Technology
            'IT', '소프트웨어', 'Software', '테크', 'Tech', '개발', 'Development',
            '플랫폼', 'Platform', '솔루션', 'Solution', '시스템', 'System',
            
            # E-commerce & Retail
            '이커머스', 'E-commerce', '온라인쇼핑', '쇼핑몰', '리테일', 'Retail',
            '패션', 'Fashion', '뷰티', 'Beauty', '코스메틱', 'Cosmetic',
            
            # Media & Entertainment
            '미디어', 'Media', '엔터테인먼트', 'Entertainment', '콘텐츠', 'Content',
            '방송', 'Broadcasting', '게임', 'Game', '영화', 'Movie',
            
            # Food & Beverage
            '식품', 'Food', '음료', 'Beverage', 'F&B', '레스토랑', 'Restaurant',
            '카페', 'Cafe', '요식업', '외식',
            
            # Finance & Insurance
            '금융', 'Finance', '은행', 'Bank', '보험', 'Insurance', '투자', 'Investment',
            '핀테크', 'Fintech', '증권', 'Securities',
            
            # Healthcare & Pharma
            '헬스케어', 'Healthcare', '의료', 'Medical', '병원', 'Hospital',
            '제약', 'Pharmaceutical', '바이오', 'Bio',
            
            # Education
            '교육', 'Education', '학습', 'Learning', '에듀테크', 'Edtech',
            '대학교', 'University', '학원', 'Academy',
            
            # Manufacturing
            '제조', 'Manufacturing', '생산', 'Production', '공장', 'Factory',
            '자동차', 'Automotive', '전자', 'Electronics',
            
            # Real Estate & Construction
            '부동산', 'Real Estate', '건설', 'Construction', '건축', 'Architecture',
            
            # Marketing & Advertising
            '마케팅', 'Marketing', '광고', 'Advertising', '홍보', 'PR',
            '에이전시', 'Agency', '브랜딩', 'Branding',
            
            # Logistics & Transportation
            '물류', 'Logistics', '운송', 'Transportation', '배송', 'Delivery',
            
            # Others
            '컨설팅', 'Consulting', '서비스', 'Service', '스타트업', 'Startup',
            'NGO', '비영리', 'Non-profit', '정부', 'Government'
        ]
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """
        Extract phone numbers from text using regex patterns
        
        Args:
            text: Input text to search for phone numbers
            
        Returns:
            List of found phone numbers
        """
        phone_numbers = []
        
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean up the phone number
                cleaned = re.sub(r'[^\d\-\+]', '', match)
                if len(cleaned) >= 10:  # Minimum valid phone number length
                    phone_numbers.append(cleaned)
        
        # Remove duplicates while preserving order
        unique_phones = []
        for phone in phone_numbers:
            if phone not in unique_phones:
                unique_phones.append(phone)
        
        return unique_phones
    
    def extract_positions_regex(self, text: str) -> List[str]:
        """
        Extract job positions from text using regex patterns
        
        Args:
            text: Input text to search for positions
            
        Returns:
            List of found positions
        """
        positions = []
        
        for pattern in self.position_keywords:
            matches = re.findall(pattern, text, re.IGNORECASE)
            positions.extend(matches)
        
        # Remove duplicates
        unique_positions = list(set(positions))
        return unique_positions
    
    def extract_categories_regex(self, text: str) -> List[str]:
        """
        Extract company categories from text using regex patterns
        
        Args:
            text: Input text to search for categories
            
        Returns:
            List of found categories
        """
        categories = []
        
        for keyword in self.category_keywords:
            if re.search(keyword, text, re.IGNORECASE):
                categories.append(keyword)
        
        # Remove duplicates
        unique_categories = list(set(categories))
        return unique_categories
    
    def extract_with_openai(self, subject: str, body: str, sender_info: str = "") -> Dict[str, Any]:
        """
        Extract phone numbers, positions, and categories using OpenAI
        
        Args:
            subject: Email subject
            body: Email body content
            sender_info: Sender information (name, email, etc.)
            
        Returns:
            Dictionary containing extracted information
        """
        try:
            prompt = f"""
Extract the following information from this email. If any information is not available, return null for that field.

Email Information:
Sender: {sender_info}
Subject: {subject}
Body: {body}

Please extract and return in JSON format:
1. phone_numbers: Array of phone numbers found in the email (Korean or international format)
2. sender_position: The job title/position of the sender (e.g., "마케팅 팀장", "CEO", "Sales Manager")
3. company_categories: Array of business categories/industries mentioned (e.g., ["IT", "마케팅", "E-commerce"])

Return only valid JSON without any additional text:
{{
    "phone_numbers": ["phone1", "phone2"] or null,
    "sender_position": "position" or null,
    "company_categories": ["category1", "category2"] or null
}}
"""

            response = self.openai_client['client'].chat.completions.create(
                model=self.openai_client['model'],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                import json
                extracted_data = json.loads(content)
                return extracted_data
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse OpenAI JSON response: {content}")
                return {"phone_numbers": None, "sender_position": None, "company_categories": None}
            
        except Exception as e:
            logger.error(f"Error extracting with OpenAI: {e}")
            return {"phone_numbers": None, "sender_position": None, "company_categories": None}
    
    def extract_all_information(self, subject: str, body: str, sender_info: str = "") -> Dict[str, Any]:
        """
        Extract all information using both regex and OpenAI, combining results
        
        Args:
            subject: Email subject
            body: Email body content
            sender_info: Sender information
            
        Returns:
            Combined extraction results
        """
        # Combine subject and body for analysis
        full_text = f"{subject} {body} {sender_info}"
        
        # Extract using regex
        regex_phones = self.extract_phone_numbers(full_text)
        regex_positions = self.extract_positions_regex(full_text)
        regex_categories = self.extract_categories_regex(full_text)
        
        # Extract using OpenAI
        openai_results = self.extract_with_openai(subject, body, sender_info)
        
        # Combine results
        all_phones = regex_phones.copy()
        if openai_results.get('phone_numbers'):
            all_phones.extend(openai_results['phone_numbers'])
        
        all_positions = regex_positions.copy()
        if openai_results.get('sender_position'):
            all_positions.append(openai_results['sender_position'])
        
        all_categories = regex_categories.copy()
        if openai_results.get('company_categories'):
            all_categories.extend(openai_results['company_categories'])
        
        # Remove duplicates and clean up
        unique_phones = list(set(all_phones)) if all_phones else None
        unique_positions = list(set(all_positions)) if all_positions else None
        unique_categories = list(set(all_categories)) if all_categories else None
        
        return {
            'phone_numbers': unique_phones,
            'sender_position': unique_positions[0] if unique_positions else None,  # Take first position
            'company_categories': unique_categories
        }

def test_extractor():
    """Test function for the email extractor"""
    # Mock OpenAI client for testing
    mock_client = {
        'client': None,  # Would be actual OpenAI client
        'model': 'gpt-3.5-turbo'
    }
    
    extractor = EmailExtractor(mock_client)
    
    # Test email content
    test_subject = "마케팅 제안서 - ABC 테크놀로지"
    test_body = """
    안녕하세요, ABC 테크놀로지 마케팅팀장 김철수입니다.
    
    저희는 IT 솔루션 및 소프트웨어 개발 전문 회사입니다.
    
    연락처: 010-1234-5678
    이메일: kimcs@abctech.co.kr
    
    감사합니다.
    """
    test_sender = "김철수 <kimcs@abctech.co.kr>"
    
    # Test regex extraction
    phones = extractor.extract_phone_numbers(test_body)
    positions = extractor.extract_positions_regex(test_body + test_sender)
    categories = extractor.extract_categories_regex(test_subject + test_body)
    
    print("=== Test Results ===")
    print(f"Phone numbers: {phones}")
    print(f"Positions: {positions}")
    print(f"Categories: {categories}")

if __name__ == "__main__":
    test_extractor()