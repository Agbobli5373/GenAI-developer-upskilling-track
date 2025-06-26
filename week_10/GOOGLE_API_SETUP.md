# Getting Your Google Gemini API Key

To use Google Gemini with your RAG monitoring system, you'll need to get an API key from Google AI Studio.

## Steps to Get Your API Key

1. **Visit Google AI Studio**

   - Go to [https://aistudio.google.com/](https://aistudio.google.com/)

2. **Sign In**

   - Sign in with your Google account

3. **Get API Key**

   - Click on "Get API key" in the left sidebar
   - Click "Create API key"
   - Select an existing Google Cloud project or create a new one
   - Copy the generated API key

4. **Set Up Your Environment**
   - Open your `.env` file in the project root
   - Replace `your_google_api_key_here` with your actual API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

## Alternative: Using Google Cloud Console

If you prefer using Google Cloud Console:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Generative AI API
4. Go to "APIs & Services" > "Credentials"
5. Click "Create Credentials" > "API Key"
6. Copy the API key and add it to your `.env` file

## Security Notes

- ⚠️ **Never commit your API key to version control**
- Keep your `.env` file in `.gitignore`
- Restrict your API key usage in Google Cloud Console if possible
- Monitor your usage to avoid unexpected charges

## Free Tier Limits

Google Gemini offers a generous free tier:

- 15 requests per minute
- 1 million tokens per minute
- 1,500 requests per day

This should be sufficient for development and testing of your RAG monitoring system.

## Testing Your Setup

After adding your API key, you can test the system by running:

```bash
python setup_system.py
```

This will verify that your configuration is working correctly.
