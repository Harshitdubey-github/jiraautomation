import React, { useState, useEffect } from 'react';
import './App.css';
import ProjectSelector from './components/ProjectSelector';
import AudioRecorder from './components/AudioRecorder';
import TranscriptionDisplay from './components/TranscriptionDisplay';
import ActionConfirmation from './components/ActionConfirmation';
import TranscriptParser from './components/TranscriptParser';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [parsedCommand, setParsedCommand] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('voice'); // 'voice' or 'transcript'

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = () => {
    // Redirect to Jira OAuth login
    window.location.href = 'http://localhost:8000/api/auth/login';
  };

  const handleProjectSelect = (project) => {
    setSelectedProject(project);
  };

  const handleTranscriptionComplete = (data) => {
    setTranscription(data.transcription);
    setParsedCommand(data.command);
  };

  const handleTranscriptionError = (errorMessage) => {
    setError(errorMessage);
  };

  const handleConfirmAction = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/jira/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ 
          action: parsedCommand,
          projectKey: selectedProject?.key
        })
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setError(null);
      setTranscription('');
      setParsedCommand(null);
      alert('Action completed successfully!');
    } catch (error) {
      console.error('Error executing action:', error);
      setError(`Failed to execute action: ${error.message}`);
    }
  };

  const handleCancelAction = () => {
    setParsedCommand(null);
  };

  const handleEditTranscription = (editedText) => {
    setTranscription(editedText);
    // Re-parse the edited transcription
    parseTranscription(editedText);
  };

  const parseTranscription = async (text) => {
    try {
      const response = await fetch('http://localhost:8000/api/transcribe/parse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ 
          transcription: text,
          projectKey: selectedProject?.key
        })
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setParsedCommand(data.command);
      setError(null);
    } catch (error) {
      console.error('Error parsing transcription:', error);
      setError(`Failed to parse transcription: ${error.message}`);
    }
  };

  const handleTranscriptParseComplete = (data) => {
    // Handle the parsed actions from Teams transcript
    console.log('Parsed actions:', data);
  };

  if (!isAuthenticated) {
    return (
      <div className="app-container">
        <div className="login-container">
          <h1>Jira Voice Assistant</h1>
          <p>Sign in with your Jira account to continue</p>
          <button className="login-button" onClick={handleLogin}>
            Sign in with Jira
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Jira Voice Assistant</h1>
        {selectedProject && (
          <div className="project-info">
            <span>Project: </span>
            <strong>{selectedProject.name}</strong>
            <span className="project-key">({selectedProject.key})</span>
          </div>
        )}
      </header>

      <main className="app-content">
        {!selectedProject ? (
          <ProjectSelector onProjectSelect={handleProjectSelect} />
        ) : (
          <>
            <div className="tabs">
              <button 
                className={`tab-button ${activeTab === 'voice' ? 'active' : ''}`}
                onClick={() => setActiveTab('voice')}
              >
                Voice Commands
              </button>
              <button 
                className={`tab-button ${activeTab === 'transcript' ? 'active' : ''}`}
                onClick={() => setActiveTab('transcript')}
              >
                Teams Transcript
              </button>
            </div>

            {activeTab === 'voice' ? (
              <div className="voice-command-section">
                <AudioRecorder 
                  onTranscriptionComplete={handleTranscriptionComplete}
                  onError={handleTranscriptionError}
                />

                {error && (
                  <div className="error-message">
                    {error}
                  </div>
                )}

                {transcription && (
                  <TranscriptionDisplay 
                    transcription={transcription}
                    parsedCommand={parsedCommand}
                    onConfirm={handleConfirmAction}
                    onCancel={handleCancelAction}
                    onEdit={handleEditTranscription}
                  />
                )}

                {parsedCommand && !transcription && (
                  <ActionConfirmation 
                    action={parsedCommand}
                    onConfirm={handleConfirmAction}
                    onCancel={handleCancelAction}
                    onEdit={() => setParsedCommand(null)}
                  />
                )}
              </div>
            ) : (
              <TranscriptParser 
                onParseComplete={handleTranscriptParseComplete}
                onError={handleTranscriptionError}
              />
            )}
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>Jira Voice Assistant &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;
