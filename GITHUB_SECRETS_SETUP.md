# GitHub Secrets Setup Guide

This guide shows how to configure GitHub Secrets for secure credential management in your automated builds.

## 🔐 Required Secrets

You need to add these secrets to your GitHub repository for the build to work:

### Required Secrets
1. **`SUPABASE_URL`** - Your Supabase project URL
2. **`SUPABASE_KEY`** - Your Supabase project API key  
3. **`OPENAI_API_KEY`** - Your OpenAI API key

### Optional Secrets
4. **`OPENAI_MODEL`** - OpenAI model to use (default: `gpt-3.5-turbo`)
5. **`GMAIL_CREDENTIALS_JSON`** - Your Gmail API credentials as JSON string
6. **`GMAIL_TOKEN_PATH`** - Token file path (default: `token.json`)
7. **`GMAIL_CREDENTIALS_PATH`** - Credentials file path (default: `credentials.json`)

## 📝 How to Add Secrets

### Step 1: Go to Repository Settings
1. Navigate to your GitHub repository
2. Click **Settings** tab
3. Go to **Secrets and variables** → **Actions**

### Step 2: Add Repository Secrets
Click **New repository secret** for each of the following:

#### SUPABASE_URL
- **Name**: `SUPABASE_URL`
- **Secret**: `https://your-project.supabase.co`

#### SUPABASE_KEY
- **Name**: `SUPABASE_KEY` 
- **Secret**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (your anon/public key)

#### OPENAI_API_KEY
- **Name**: `OPENAI_API_KEY`
- **Secret**: `sk-proj-...` (your OpenAI API key)

#### GMAIL_CREDENTIALS_JSON (Optional but Recommended)
- **Name**: `GMAIL_CREDENTIALS_JSON`
- **Secret**: Copy your entire `credentials.json` file content as a single line:
```json
{"installed":{"client_id":"your-client-id.googleusercontent.com","project_id":"your-project","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"your-client-secret","redirect_uris":["http://localhost"]}}
```

## 🔍 How to Get Your Values

### Supabase Credentials
1. Go to [Supabase Dashboard](https://app.supabase.com/)
2. Select your project
3. Go to **Settings** → **API**
4. Copy **Project URL** and **anon/public key**

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Navigate to **API Keys**
3. Create a new secret key

### Gmail API Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop application)
4. Download the JSON file
5. Copy the entire file content as one line

## ✅ Verification

After adding secrets, your workflow will:
1. ✅ Create `.env` file from secrets during build
2. ✅ Create `credentials.json` from secret (if provided)
3. ✅ Embed both files in the executable
4. ✅ Users get a fully configured executable

## 🚫 Security Benefits

- ✅ **Credentials never in Git history**
- ✅ **Secrets encrypted by GitHub** 
- ✅ **Only accessible during builds**
- ✅ **Masked in workflow logs**
- ✅ **Can be rotated anytime**

## 🔄 Updating Secrets

To update any credential:
1. Go to repository **Settings** → **Secrets**
2. Click the secret name
3. Click **Update**
4. Enter new value
5. Next build will use updated credentials

## 🚀 After Setup

Once secrets are configured:
```bash
git push
git tag v1.0.0
git push origin v1.0.0
```

Your executables will be built with embedded credentials from GitHub Secrets! 🎉