1. Overview
We will build a web-based application that allows a user to:

Authenticate with Jira (using OAuth).

Select a Jira project to work with.

Use voice commands (record audio, send to Deepgram for transcription) to query tasks, create or update tasks, and comment on tasks in Jira.

Manually paste a Teams meeting transcript to have the system parse out potential action items or updates.

The LLM will help identify relevant tasks in the chosen Jira project and propose updates.

2. High-Level Architecture
pgsql
Copy
+--------------------+           +--------------------+            +---------------------+
|     React Frontend | --------> |  Python Backend    | ---------> | Jira Cloud API      |
| (Voice UI & forms) |           | (Flask/FastAPI)    |            | (OAuth, REST)       |
+--------------------+           +--------------------+            +---------------------+
         |                         ^   |
         v                         |   v
    Deepgram API <--------------- (Backend processes audio -> text)
         ^
         |
    LLM (OpenAI) <----> (Backend for natural language parsing & context management)

+-----------------------------+
|  Supabase (DB & Auth info) |
+-----------------------------+
React Frontend

Collects user login data or triggers OAuth sign-in to Jira.

Lets the user select a Jira project from a dropdown.

Provides a “Start Recording” button:

Records short audio clips.

Sends them to the backend for transcription.

Displays recognized text, parsed commands, and summary of actions before execution.

Allows manual paste of Teams transcripts.

Python Backend

Web framework: Flask or FastAPI (preferred for modern async support).

Session & State: Manages user’s active session, including:

OAuth tokens from Jira.

“Currently open” task or context for voice commands.

In-memory ephemeral store for user chat logs (or Redis/DB if needed).

Integrations:

Deepgram for audio transcription:

Receives short audio files from the frontend.

Sends them to Deepgram, gets the transcript, returns it to the LLM or direct to the user.

OpenAI for NLU and conversation flow:

Receives user’s transcript and conversation context.

Determines user intent (query tasks, update tasks, comment, etc.).

Summarizes or identifies tasks from transcripts (Teams).

Jira:

Manages user OAuth tokens in Supabase.

Sends/receives data from Jira Cloud (GET tasks, CREATE/UPDATE tasks, POST comments, etc.).

Supabase (DB)

Stores user info and Jira OAuth tokens.

Minimal usage for now (ephemeral logs are in-memory).

Allows future expansion for more robust data (logging commands, usage metrics, etc.).

3. Detailed Steps
3.1. Authentication & User Management
User Registration Flow (Prototype Level)

On first visit:

The user can click “Sign in with Jira.”

We redirect them to Atlassian’s OAuth page.

They log in using their Jira credentials, including MFA if their Jira is set up that way.

Atlassian returns an access token to our backend.

We store that token in Supabase (linked to the user’s ID).

We create a session (secure cookie or JWT) so the user doesn’t have to log in repeatedly.

Token Refresh

If the Atlassian token expires, the user may be prompted to re-authenticate.

For the prototype, we can skip automatic token refresh and just re-initiate if calls fail.

3.2. Project Selection
Fetch Projects

After login, the backend uses the user’s Jira token to list all projects the user has access to.

Project Dropdown

The frontend populates a dropdown with project names.

Once selected, the user’s subsequent queries/actions will be scoped to that project.

3.3. Voice Recording & Transcription
Frontend Flow

Start Recording button uses the Web Audio API to capture a short audio clip.

When the user stops recording (or after a timeout), the frontend sends the audio file to the backend (e.g., in WAV format).

Backend Transcription

The Python server sends the audio clip to Deepgram’s API.

Deepgram returns a text transcript.

The backend routes the transcript to the LLM with the user’s conversation context.

3.4. Natural Language Understanding & Command Parsing
LLM Prompt Construction

The backend maintains a conversation “memory” (in a Python dictionary or simple in-memory store):

The user’s last voice transcript and prior transcripts/commands.

The “currently open” task (if any).

Additional context about the chosen Jira project.

The LLM (OpenAI) receives a prompt that includes:

The user’s current voice transcript (“What are my open tasks?”).

The relevant context (active project, possibly last known open task, etc.).

Instructions to parse out the user’s intent (query, comment, status update, etc.) and generate a structured JSON or text output describing the action the user is requesting.

Parsing Logic

The LLM’s response might look like:

json
Copy
{
  "action": "query_tasks",
  "filters": {"assignee": "current_user", "status": "open"}
}
Or:

json
Copy
{
  "action": "update_comment",
  "task_id": "PROJECT-123",
  "comment": "Testing complete."
}
This structured output is used by the backend to build a confirmation UI.

3.5. Confirmation & Execution
Backend Returns Proposed Action

The backend sends the proposed action back to the React front end along with the recognized text and any tasks found.

Frontend Confirms with User

Displays: “You asked to add a comment to PROJECT-123: ‘Testing complete.’ Is that correct?”

Confirm or Cancel button.

Backend Executes

If the user confirms, we call the Jira API using the user’s OAuth token:

E.g., POST /rest/api/3/issue/PROJECT-123/comment

On success, we return a success message to the front end.

3.6. Query Responses & Display
Query (e.g., “What are my open tasks?”)

The backend calls Jira to get relevant issues (based on the LLM parsing).

Returns them to the frontend as a list.

The front end displays them in a simple table with Task ID, Summary, Status, etc.

3.7. Pasting Teams Transcript
UI for Transcript Paste

A small text box or modal where the user can paste in the entire transcript from Teams.

LLM Parsing

The system calls the LLM with the entire transcript, instructing it to identify:

Potential tasks or action items.

Which user might own them (if it can infer from context).

Any direct references to existing Jira issues (by ID) or the need for new issues.

Proposed Actions

The LLM might respond with:

json
Copy
[
  {
    "action": "create_issue",
    "summary": "Implement new login flow",
    "description": "Mentioned by John in the meeting...",
    "assignee": "John"
  },
  {
    "action": "update_comment",
    "task_id": "PROJECT-456",
    "comment": "Need to finalize QA by Friday."
  }
]
The front end shows each proposed action, allowing the user to confirm or revise.

Confirm/Execute

Same confirm mechanism as voice commands.

4. Tech Stack Breakdown
Frontend

React with JavaScript.

Audio recording via the MediaRecorder API.

HTTP requests to the Python backend (likely via fetch or axios).

State management (e.g., React’s useState or Redux if needed, but might be overkill for a prototype).

Backend

Python with FastAPI (or Flask if simpler) for quickly building endpoints.

Requests or an HTTP client library to call:

Deepgram for speech transcription.

OpenAI for LLM calls.

Jira REST API.

Supabase

Store user records, OAuth tokens (encrypted or hashed if possible).

Store minimal session data if needed. Alternatively, store in-memory session state in the backend for a quick prototype.

Deepgram

Need an API key, used server-side to transcribe audio files.

OpenAI

Need an API key, used server-side to parse commands and generate structured responses.

Jira

Use OAuth 2.0 with Atlassian to get an access token.

Expose routes in the backend to fetch projects, fetch issues, create/update issues, etc.

5. Implementation Outline
Setup & Configuration

Environment Variables:

DEEPGRAM_API_KEY

OPENAI_API_KEY

JIRA_CLIENT_ID / JIRA_CLIENT_SECRET (for OAuth)

SUPABASE_URL

SUPABASE_ANON_KEY (or service key if we handle more advanced logic)

Backend (FastAPI Example)

Install dependencies:

bash
Copy
pip install fastapi uvicorn requests pydantic python-jose
Main entrypoint (main.py):

python
Copy
from fastapi import FastAPI, Request, UploadFile, File
from routes import auth, transcription, commands

app = FastAPI()

app.include_router(auth.router, prefix="/auth")
app.include_router(transcription.router, prefix="/transcribe")
app.include_router(commands.router, prefix="/commands")
Auth Router:

Handles Jira OAuth redirect, token exchange, storing tokens in Supabase, and returning session info.

Transcription Router:

Endpoint: POST /transcribe/audio

Accepts file upload from the frontend, calls Deepgram, returns transcript.

Commands Router:

Endpoint: POST /commands/parse

Takes the transcript + current conversation context, calls OpenAI, returns structured action.

Endpoint: POST /commands/execute

Accepts a confirmed action and calls Jira to perform the update/comment creation, etc.

Helper Modules:

jira.py for Jira REST calls (CRUD).

supabase.py for DB interactions (storing tokens, retrieving user info).

llm.py for building LLM prompts and calling OpenAI.

Frontend (React)

Project Structure:

pgsql
Copy
src/
├── components/
|   ├── AudioRecorder.js
|   ├── ProjectSelector.js
|   ├── ActionConfirmation.js
|   └── TranscriptParser.js
├── pages/
|   └── Home.js
├── App.js
└── index.js
AudioRecorder.js:

Provides “Start Recording” / “Stop” functionality.

Sends resulting audio blob to backend.

Receives transcript → triggers command parse → shows user the proposed action.

ProjectSelector.js:

On component mount, calls the backend to get the list of Jira projects.

Renders a dropdown for the user to select a project.

ActionConfirmation.js:

Displays the “intent” and “action” the LLM parsed.

Has “Confirm” or “Cancel” button → calls backend to execute or abort.

TranscriptParser.js (for Teams transcripts):

Text area for user to paste transcript.

Button to parse transcript → calls backend LLM route → returns proposed actions.

6. Key Considerations
Security

Make sure to store Jira tokens securely in Supabase.

Use HTTPS for all communication, especially for audio uploads.

Confirmation Flow

Always show the user what the system plans to do (including task ID) before calling the Jira API.

User Experience

Keep it simple: minimal confusion about what the system is doing behind the scenes.

Provide fallback text-based input if voice transcription fails.

Edge Cases

LLM might misunderstand user commands. Provide a way for the user to revise the recognized text or the parsed command.

Rate Limits

Both Deepgram and OpenAI have usage/pricing constraints.

This is a prototype, so likely not an issue, but keep in mind for production scale.

7. Future Enhancements
Live Streaming

Instead of recording short clips, we could stream audio to Deepgram for real-time transcription (requires more complex front-end code).

Microsoft Graph Integration

Automate retrieval of Teams meeting transcripts (no manual copy-paste).

Conversation Memory in DB

If you want the conversation context to persist across browser sessions, store partial chat logs in Supabase or a dedicated memory store (Redis).

Advanced Logging

Store user queries, transcripts, LLM outputs for analytics or debugging.

Custom Fine-tuning

Fine-tune LLM on your own team’s usage patterns or Jira fields for better command recognition.

8. Example Usage Flow
User navigates to app → clicks “Sign in with Jira”.

Select Project: The user picks PROJECT-XYZ.

Voice Query:

Click “Start Recording” → speak: “What are my open tasks?”

Audio clip → sent to backend → Deepgram → transcript returned.

Backend calls OpenAI to parse → Action is [query_tasks, assignee = me, status = open].

Frontend shows “I found an intent to list your open tasks. Confirm?”

User confirms → backend calls Jira → returns list of tasks → UI displays tasks.

Voice Update:

Another recording: “Update TASK-12 with comment ‘Stand-up is done, QA pending.’”

Transcript + context → LLM identifies “update_comment” for “TASK-12.”

UI shows “Add comment: ‘Stand-up is done, QA pending’ to TASK-12?”

Confirm → update in Jira → success response.

Teams Transcript:

User pastes the daily stand-up text into the TranscriptParser component.

The system calls the LLM to identify tasks/updates.

UI displays a list of proposed new tasks or comments to existing tasks.

User confirms or edits each item, then the system executes them in Jira.

9. Conclusion
This plan outlines a lightweight yet powerful voice-enabled Jira companion. By focusing on:

React for the front-end,

Python (FastAPI) for the back-end,

Deepgram for transcription,

OpenAI for NLU,

Jira OAuth for secure access,