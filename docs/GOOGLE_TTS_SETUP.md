# Google Cloud Text-to-Speech Setup Guide

Complete guide to set up Google Cloud Text-to-Speech API for XiAvi Speech AI.

---

## 📋 Prerequisites

- Google account
- Credit card (for Google Cloud verification - won't be charged during free tier)
- 10-15 minutes

---

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**

   - Visit: https://console.cloud.google.com/

2. **Create New Project**

   - Click the project dropdown at the top (next to "Google Cloud" logo)
   - Click **"NEW PROJECT"**
   - Enter project details:
     - **Project name**: `xiavi-speech-ai` (or your preferred name)
     - **Organization**: Leave as "No organization" (unless you have one)
   - Click **"CREATE"**
   - Wait for the project to be created (takes ~10 seconds)

3. **Select Your New Project**
   - Click the project dropdown again
   - Select your newly created project

---

### Step 2: Enable Text-to-Speech API

1. **Open API Library**

   - In the left sidebar, click **"APIs & Services"** → **"Library"**
   - Or go directly to: https://console.cloud.google.com/apis/library

2. **Find Text-to-Speech API**

   - In the search bar, type: `Cloud Text-to-Speech API`
   - Click on **"Cloud Text-to-Speech API"**

3. **Enable the API**
   - Click the blue **"ENABLE"** button
   - Wait for activation (~5 seconds)
   - You should see "API enabled" message

---

### Step 3: Create Service Account

A service account is a special account that your application uses to authenticate with Google Cloud.

1. **Navigate to Service Accounts**

   - In the left sidebar, click **"IAM & Admin"** → **"Service Accounts"**
   - Or go to: https://console.cloud.google.com/iam-admin/serviceaccounts

2. **Create Service Account**
   - Click **"+ CREATE SERVICE ACCOUNT"** at the top
3. **Enter Service Account Details**

   - **Service account name**: `xiavi-tts-service`
   - **Service account ID**: Will auto-populate (e.g., `xiavi-tts-service@...`)
   - **Description**: `Text-to-Speech service for XiAvi Speech AI`
   - Click **"CREATE AND CONTINUE"**

4. **Grant Permissions**
   - In "Grant this service account access to project" section:
     - Click **"Select a role"** dropdown
     - Search for: `Cloud Text-to-Speech User`
     - Select **"Cloud Text-to-Speech User"**
   - Click **"CONTINUE"**
   - Click **"DONE"** (skip optional user access step)

---

### Step 4: Create and Download JSON Key

1. **Open Service Account**

   - You should now see your service account in the list
   - Click on the **service account email** (e.g., `xiavi-tts-service@...`)

2. **Go to Keys Tab**

   - Click on the **"KEYS"** tab at the top

3. **Create New Key**

   - Click **"ADD KEY"** dropdown
   - Select **"Create new key"**

4. **Download JSON Key**
   - Select **"JSON"** format (should be selected by default)
   - Click **"CREATE"**
   - A JSON file will automatically download to your computer
   - **⚠️ IMPORTANT**: This file contains sensitive credentials - keep it secure!

---

### Step 5: Add Key to Your Project

1. **Rename the Downloaded File**

   - Find the downloaded file (usually in `Downloads/` folder)
   - It will have a name like: `xiavi-speech-ai-1a2b3c4d5e6f.json`
   - Rename it to: `google-tts-key.json`

2. **Move to Backend Folder**

   - Move the file to your project's backend folder:

   ```
   XiAvSpeechAI/backend/google-tts-key.json
   ```

3. **Verify File Location**

   - Your backend folder should now have:

   ```
   backend/
   ├── google-tts-key.json  ← Your new credentials file
   ├── .env
   ├── manage.py
   └── ...
   ```

4. **Check .gitignore (Security Check)**
   - Open `.gitignore` in the root project folder
   - Verify it contains:
   ```
   **/google-tts-key.json
   ```
   - If not present, add it immediately!

---

### Step 6: Configure Environment Variables

1. **Open .env File**

   - Navigate to `backend/.env`

2. **Add/Update GOOGLE_APPLICATION_CREDENTIALS**

   ```env
   # Google Cloud TTS
   GOOGLE_APPLICATION_CREDENTIALS=google-tts-key.json
   ```

3. **Verify Other Required Variables**
   Your `.env` should also have:

   ```env
   # Database
   DB_NAME=xiav_speech_ai
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432

   # Django
   SECRET_KEY=your-secret-key
   DEBUG=True

   # API Keys
   DEEPGRAM_API_KEY=your_deepgram_api_key
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_APPLICATION_CREDENTIALS=google-tts-key.json
   ```

---

### Step 7: Test the Setup

1. **Activate Virtual Environment**

   ```powershell
   cd backend
   .\venv\Scripts\activate
   ```

2. **Run Test Script**

   ```powershell
   python setup_google_tts.py
   ```

3. **Expected Output**

   ```
   ✅ Google Cloud TTS is working!
   Available voices: 412

   Sample voices:
     - en-US-Journey-D (MALE)
     - en-US-Journey-F (FEMALE)
     - en-US-Neural2-A (FEMALE)
     - en-US-Neural2-C (FEMALE)
     - en-US-Neural2-D (MALE)

   Testing voice: en-US-Neural2-D
   Audio saved to: test_audio.mp3
   ✅ Test successful! Audio file created.
   ```

4. **Verify Credentials**

   ```powershell
   python check_google_creds.py
   ```

   Expected output:

   ```
   ✓ Service account email: xiavi-tts-service@xiavi-speech-ai.iam.gserviceaccount.com
   ✓ Project ID: xiavi-speech-ai
   ✓ Text-to-Speech API: Enabled
   ✓ Successfully generated test audio
   ```

5. **Test in Django**

   ```powershell
   python manage.py shell
   ```

   Then in the Python shell:

   ```python
   from services.google_tts_service import GoogleTTSService

   tts = GoogleTTSService()
   audio_data = tts.synthesize_speech("Hello, this is a test.")
   print(f"Generated {len(audio_data)} bytes of audio")
   ```

   You should see: `Generated XXXXX bytes of audio`

---

## ✅ Verification Checklist

Before proceeding, make sure:

- [ ] Google Cloud project created
- [ ] Cloud Text-to-Speech API enabled
- [ ] Service account created with "Cloud Text-to-Speech User" role
- [ ] JSON key downloaded and renamed to `google-tts-key.json`
- [ ] Key file placed in `backend/` folder
- [ ] `google-tts-key.json` is in `.gitignore`
- [ ] File shows with yellow/gray icon in VS Code (means it's gitignored)
- [ ] `.env` file has `GOOGLE_APPLICATION_CREDENTIALS=google-tts-key.json`
- [ ] `setup_google_tts.py` runs successfully
- [ ] `check_google_creds.py` runs successfully
- [ ] Django can import and use the TTS service

---

## 🔒 Security Best Practices

### DO ✅

- Keep `google-tts-key.json` in `.gitignore`
- Store credentials locally only
- Use environment variables for configuration
- Rotate keys periodically (every 90 days recommended)
- Use different service accounts for dev/staging/production
- Set appropriate IAM roles (least privilege principle)

### DON'T ❌

- Never commit `google-tts-key.json` to git
- Don't share the JSON key file
- Don't hardcode credentials in code
- Don't give service accounts more permissions than needed
- Don't use production credentials in development
- Don't upload the key to public repositories

---

## 🆘 Troubleshooting

### Error: "Could not automatically determine credentials"

**Cause**: Django can't find the credentials file

**Solutions**:

1. Check that `google-tts-key.json` exists in `backend/` folder
2. Verify `.env` has: `GOOGLE_APPLICATION_CREDENTIALS=google-tts-key.json`
3. Make sure you're running commands from `backend/` directory
4. Try using absolute path in `.env`:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=C:\Users\YourName\Projects\XiAvSpeechAI\backend\google-tts-key.json
   ```

---

### Error: "Permission denied" or "403 Forbidden"

**Cause**: Service account doesn't have proper permissions

**Solutions**:

1. Go to IAM & Admin → Service Accounts
2. Click on your service account
3. Verify it has "Cloud Text-to-Speech User" role
4. If not, go to IAM → Grant Access → Add the role

---

### Error: "API has not been enabled"

**Cause**: Text-to-Speech API is not enabled for your project

**Solutions**:

1. Go to APIs & Services → Library
2. Search for "Cloud Text-to-Speech API"
3. Click "ENABLE"
4. Wait 1-2 minutes for activation

---

### Error: "Invalid JSON key file"

**Cause**: The JSON file is corrupted or incomplete

**Solutions**:

1. Re-download the JSON key from Google Cloud Console
2. Don't open or edit the JSON file manually
3. Ensure the entire file was downloaded (check file size > 2KB)

---

### Error: "Project not found" or "Invalid project ID"

**Cause**: Project ID mismatch or deleted project

**Solutions**:

1. Check the `project_id` field in `google-tts-key.json` matches your active project
2. Go to Google Cloud Console and verify project still exists
3. Create a new project if the old one was deleted

---

## 💰 Pricing Information

### Free Tier (Always Free)

- **WaveNet voices**: 1 million characters per month
- **Standard voices**: 4 million characters per month

### After Free Tier

- **WaveNet voices**: $16.00 per 1 million characters
- **Neural2 voices**: $16.00 per 1 million characters
- **Standard voices**: $4.00 per 1 million characters
- **Studio voices**: $160.00 per 1 million characters

**Example Usage**:

- Average conversation: ~500-1000 characters
- 1000 conversations = 500,000 - 1,000,000 characters
- **Within free tier for development!**

For more details: https://cloud.google.com/text-to-speech/pricing

---

## 🔄 Key Management

### When to Rotate Keys

- Every 90 days (recommended)
- When a key is compromised
- When team members leave
- Before moving to production

### How to Rotate Keys

1. **Create new key**:

   - Go to Service Accounts → Select account → Keys
   - Click "ADD KEY" → "Create new key"
   - Download new JSON file

2. **Update your project**:

   - Replace old `google-tts-key.json` with new one
   - Restart Django server

3. **Delete old key**:
   - In Google Cloud Console, find the old key
   - Click ⋮ (three dots) → "Delete"
   - Confirm deletion

---

## 🔍 Additional Resources

- [Google Cloud TTS Documentation](https://cloud.google.com/text-to-speech/docs)
- [Available Voices](https://cloud.google.com/text-to-speech/docs/voices)
- [SSML Guide](https://cloud.google.com/text-to-speech/docs/ssml)
- [Audio Profiles](https://cloud.google.com/text-to-speech/docs/audio-profiles)
- [Best Practices](https://cloud.google.com/text-to-speech/docs/best-practices)

---

## 📞 Need Help?

If you encounter issues not covered here:

1. Check the [Google Cloud Status Dashboard](https://status.cloud.google.com/)
2. Review [Google Cloud TTS Quotas](https://cloud.google.com/text-to-speech/quotas)
3. Check Django logs for detailed error messages
4. Verify your Google Cloud billing account is active
5. Contact Google Cloud Support if needed

---

**Last Updated**: December 8, 2025  
**Version**: 1.0
