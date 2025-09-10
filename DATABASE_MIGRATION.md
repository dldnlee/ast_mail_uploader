# Database Migration: Add Gmail Message ID

## 🎯 Purpose
Add a `gmail_message_id` field to the `mail_history` table to prevent processing duplicate emails.

## 📊 Required Migration

### Step 1: Add Column to Supabase
Run this SQL in your Supabase SQL Editor:

```sql
-- Add gmail_message_id column to mail_history table
ALTER TABLE mail_history 
ADD COLUMN gmail_message_id TEXT;

-- Create unique index to prevent duplicates
CREATE UNIQUE INDEX idx_mail_history_gmail_message_id 
ON mail_history(gmail_message_id);

-- Add comment for documentation
COMMENT ON COLUMN mail_history.gmail_message_id 
IS 'Unique Gmail message ID to prevent duplicate processing';
```

### Step 2: Optional - Backfill Existing Data
If you have existing emails and want to prevent reprocessing them, you can set placeholder IDs:

```sql
-- Update existing records with placeholder IDs
-- This prevents reprocessing but doesn't provide real Gmail IDs
UPDATE mail_history 
SET gmail_message_id = 'legacy-' || id::text 
WHERE gmail_message_id IS NULL;
```

## 🔧 What This Enables

### Before Migration:
- ❌ Same emails processed multiple times
- ❌ Duplicate entries in database
- ❌ Wasted API calls and processing time

### After Migration:
- ✅ **Duplicate Detection**: Checks Gmail message ID before processing
- ✅ **Skip Processed Emails**: Logs and skips already processed emails
- ✅ **Efficient Processing**: Only new emails are processed
- ✅ **Database Integrity**: Unique constraint prevents duplicates

## 📋 Updated Table Schema

```sql
-- Updated mail_history table structure
CREATE TABLE mail_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  original_content TEXT,
  summarized_content TEXT,
  received_date TIMESTAMP,
  company_entity_id UUID REFERENCES company_entity(id),
  receiver_mail TEXT,
  gmail_message_id TEXT UNIQUE,  -- ← NEW FIELD
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🚀 How It Works

1. **Check First**: Before processing any email, check if `gmail_message_id` exists
2. **Skip if Found**: If exists, log "already processed" and skip
3. **Process if New**: If not found, process email and save with Gmail message ID
4. **Prevent Duplicates**: Unique index ensures no duplicate Gmail message IDs

## ⚠️ Important Notes

- **Run migration before using updated code**
- **Existing emails won't have Gmail message IDs** (unless backfilled)
- **New processing will be duplicate-free**
- **Safe to run multiple times** - duplicate index creation will be ignored

## 🧪 Testing

After migration, test duplicate prevention:
1. Process some emails
2. Run processor again with same query
3. Should see "already processed, skipping..." messages
4. No duplicate entries in database

## 🔄 Rollback (if needed)

```sql
-- Remove the column and index if needed
DROP INDEX IF EXISTS idx_mail_history_gmail_message_id;
ALTER TABLE mail_history DROP COLUMN IF EXISTS gmail_message_id;
```