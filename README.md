# Gmail Mail Processor for Supabase

This Python script processes Gmail messages and stores them in Supabase with AI-generated summaries.

## Features

- Fetches emails from Gmail using the Gmail API
- Extracts sender information and creates/finds company entities in Supabase
- Summarizes email content using OpenAI API
- Stores email history with summaries in Supabase
- Handles duplicate company entities based on email addresses

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase service role key
- `OPENAI_API_KEY`: Your OpenAI API key
- `GMAIL_CREDENTIALS_PATH`: Path to Gmail API credentials file (default: credentials.json)
- `GMAIL_TOKEN_PATH`: Path to Gmail token file (default: token.json)

### 3. Gmail API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create credentials (OAuth 2.0 client ID) for a desktop application
5. Download the credentials file and save it as `credentials.json` in the project root
6. Run the script - it will open a browser window for OAuth authentication

### 4. OpenAI API Setup

1. Sign up for an OpenAI account at [https://openai.com/](https://openai.com/)
2. Create an API key in your account settings
3. Add the key to your `.env` file

### 5. Supabase Setup

The script expects these tables to exist in your Supabase database:

#### company_entity
- `id` (uuid, primary key)
- `name` (text)
- `email` (text, nullable)
- `company` (text, nullable)
- `position` (text, nullable)
- `phone_num` (text, nullable)
- `category` (text array, nullable)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)

#### mail_history
- `id` (uuid, primary key)
- `title` (text, nullable)
- `original_content` (text, nullable)
- `summarized_content` (text, nullable)
- `received_date` (timestamptz, nullable)
- `company_entity_id` (uuid, foreign key to company_entity.id)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)

## Usage

### Basic Usage

```bash
python gmail_processor.py
```

The script will prompt you for:
1. Gmail search query (optional - press Enter for recent emails)
2. Maximum number of emails to process (default: 10)

### Gmail Search Queries

You can use Gmail's search syntax:
- `from:example@company.com` - emails from specific sender
- `subject:invoice` - emails with "invoice" in subject
- `newer_than:7d` - emails newer than 7 days
- `has:attachment` - emails with attachments

### Programmatic Usage

```python
from gmail_processor import GmailProcessor

processor = GmailProcessor()

# Process all recent emails
processor.process_all_messages(max_results=50)

# Process emails with specific query
processor.process_all_messages(query="from:client@company.com", max_results=20)
```

## How It Works

1. **Email Fetching**: Uses Gmail API to fetch emails based on search criteria
2. **Email Parsing**: Extracts sender email, name, subject, body, and date
3. **Entity Management**: Creates or finds existing company entities by email address
4. **Content Summarization**: Uses OpenAI to generate Korean summaries of email content
5. **Data Storage**: Stores processed emails and summaries in Supabase

## Error Handling

The script includes comprehensive error handling:
- Invalid email addresses are skipped
- Failed API calls are logged and retried where appropriate
- Database errors are caught and logged
- Processing continues even if individual emails fail

## Security Notes

- Never commit your `.env` file or credentials files to version control
- Use environment variables for all sensitive configuration
- The Gmail token is automatically refreshed when expired
- Consider using service account authentication for production use