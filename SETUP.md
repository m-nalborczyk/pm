# Setup Instructions

## Environment Variables

This project requires an OpenRouter API key for AI functionality.

### Setup Steps

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Get your OpenRouter API key:
   - Visit https://openrouter.ai/keys
   - Create a new API key
   - Copy the key

3. Edit `.env` and replace `your_api_key_here` with your actual API key:
   ```
   OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
   ```

4. **Important**: Never commit the `.env` file to git. It's already in `.gitignore`.

## Running the Application

See the main README.md for instructions on running the application with Docker.