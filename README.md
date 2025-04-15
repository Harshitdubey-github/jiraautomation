# Jira Voice Assistant

A voice-enabled Jira assistant that allows users to interact with Jira using voice commands or by parsing Teams meeting transcripts.

## Features

- **Voice Commands**: Record audio and convert it to Jira actions
- **Teams Transcript Parsing**: Paste Teams meeting transcripts to extract action items
- **Jira Integration**: Create, update, and query Jira issues
- **Project Selection**: Choose which Jira project to work with
- **Confirmation Workflow**: Review and confirm actions before execution

## Tech Stack

- **Frontend**: React with JavaScript
- **Backend**: Python with FastAPI
- **Integrations**: 
  - Deepgram for audio transcription
  - OpenAI for command parsing
  - Jira API for task management
  - Supabase for authentication and data storage

## Getting Started

### Prerequisites

- Node.js (v14+)
- Python (v3.8+)
- Jira account with API access
- Deepgram API key
- OpenAI API key
- Supabase account

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/jira-voice-assistant.git
   cd jira-voice-assistant
   ```

2. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

3. Install backend dependencies:
   ```
   cd ../backend
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create `.env` files in both frontend and backend directories
   - See `.env.example` files for required variables

5. Start the development servers:
   - Frontend: `cd frontend && npm start`
   - Backend: `cd backend && uvicorn main:app --reload`

## Deployment

This project is configured for deployment on Vercel:

1. Push your code to GitHub
2. Connect your GitHub repository to Vercel
3. Configure environment variables in Vercel
4. Deploy!

## Testing

Run frontend tests:
```
cd frontend
npm test
```

Run backend tests:
```
cd backend
pytest
```

## License

MIT

## Acknowledgements

- [Deepgram](https://deepgram.com/) for audio transcription
- [OpenAI](https://openai.com/) for natural language processing
- [Atlassian](https://www.atlassian.com/) for Jira API
- [Supabase](https://supabase.io/) for authentication and database 