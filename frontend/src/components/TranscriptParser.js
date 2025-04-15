import React, { useState } from 'react';
import './TranscriptParser.css';

const TranscriptParser = ({ onParseComplete, onError }) => {
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [parsedActions, setParsedActions] = useState(null);

  const handleTranscriptChange = (e) => {
    setTranscript(e.target.value);
  };

  const handleParse = async () => {
    if (!transcript.trim()) {
      onError('Please enter a transcript to parse');
      return;
    }

    setIsProcessing(true);
    setParsedActions(null);

    try {
      const response = await fetch('http://localhost:8000/api/parse-command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ transcript })
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setParsedActions(data.actions);
      onParseComplete(data);
    } catch (error) {
      console.error('Error parsing transcript:', error);
      onError('Failed to parse transcript. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleConfirmAction = async (action, index) => {
    try {
      const response = await fetch('http://localhost:8000/api/execute-action', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Update the action status in the UI
      const updatedActions = [...parsedActions];
      updatedActions[index] = {
        ...updatedActions[index],
        status: 'completed',
        result: data
      };
      setParsedActions(updatedActions);
    } catch (error) {
      console.error('Error executing action:', error);
      onError(`Failed to execute action: ${error.message}`);
    }
  };

  const handleSkipAction = (index) => {
    const updatedActions = [...parsedActions];
    updatedActions[index] = {
      ...updatedActions[index],
      status: 'skipped'
    };
    setParsedActions(updatedActions);
  };

  return (
    <div className="transcript-parser">
      <h2>Teams Meeting Transcript Parser</h2>
      
      <div className="transcript-input-container">
        <label htmlFor="transcript-input">Paste your Teams meeting transcript:</label>
        <textarea
          id="transcript-input"
          className="transcript-input"
          value={transcript}
          onChange={handleTranscriptChange}
          placeholder="Paste your Teams meeting transcript here..."
          rows={10}
        />
        <button 
          className="parse-button"
          onClick={handleParse}
          disabled={isProcessing || !transcript.trim()}
        >
          {isProcessing ? 'Parsing...' : 'Parse Transcript'}
        </button>
      </div>

      {isProcessing && (
        <div className="processing-indicator">
          <span className="processing-spinner"></span>
          Analyzing transcript...
        </div>
      )}

      {parsedActions && parsedActions.length > 0 && (
        <div className="parsed-actions">
          <h3>Identified Actions</h3>
          <p>The following actions were identified from your transcript:</p>
          
          <div className="actions-list">
            {parsedActions.map((action, index) => (
              <div 
                key={index} 
                className={`action-item ${action.status || 'pending'}`}
              >
                <div className="action-header">
                  <h4>{action.action_type === 'create' ? 'Create Issue' : 
                       action.action_type === 'comment' ? 'Add Comment' : 
                       action.action_type === 'update' ? 'Update Issue' : 
                       action.action_type === 'search' ? 'Search Issues' : 
                       action.action_type}</h4>
                  <span className="action-status">{action.status || 'pending'}</span>
                </div>
                
                <div className="action-details">
                  {action.action_type === 'create' && (
                    <>
                      <p><strong>Project:</strong> {action.project_key}</p>
                      <p><strong>Summary:</strong> {action.summary}</p>
                      <p><strong>Description:</strong> {action.description}</p>
                    </>
                  )}
                  
                  {action.action_type === 'comment' && (
                    <>
                      <p><strong>Issue:</strong> {action.issue_key}</p>
                      <p><strong>Comment:</strong> {action.comment}</p>
                    </>
                  )}
                  
                  {action.action_type === 'update' && (
                    <>
                      <p><strong>Issue:</strong> {action.issue_key}</p>
                      <p><strong>Fields to update:</strong></p>
                      <pre>{JSON.stringify(action.fields, null, 2)}</pre>
                    </>
                  )}
                  
                  {action.action_type === 'search' && (
                    <>
                      <p><strong>JQL Query:</strong> {action.jql}</p>
                    </>
                  )}
                </div>
                
                {action.status === 'completed' && (
                  <div className="action-result">
                    <p><strong>Result:</strong> {JSON.stringify(action.result)}</p>
                  </div>
                )}
                
                {!action.status && (
                  <div className="action-actions">
                    <button 
                      className="confirm-button"
                      onClick={() => handleConfirmAction(action, index)}
                    >
                      Confirm
                    </button>
                    <button 
                      className="skip-button"
                      onClick={() => handleSkipAction(index)}
                    >
                      Skip
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TranscriptParser; 