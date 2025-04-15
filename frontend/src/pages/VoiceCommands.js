import React, { useState } from 'react';
import AudioRecorder from '../components/AudioRecorder';
import './VoiceCommands.css';

const VoiceCommands = () => {
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);

  const handleRecordingComplete = async (audioBlob) => {
    try {
      setIsProcessing(true);
      setError(null);

      // Create form data with the audio file
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');

      // Send to backend for processing
      const response = await fetch('http://localhost:8000/api/transcribe', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process audio');
      }

      const data = await response.json();
      setTranscript(data.transcript);
    } catch (err) {
      setError('Error processing audio. Please try again.');
      console.error('Error processing audio:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="voice-commands">
      <h1>Voice Commands</h1>
      <p className="description">
        Use your voice to interact with Jira. Record a command and we'll process it for you.
      </p>

      <AudioRecorder onRecordingComplete={handleRecordingComplete} />

      {isProcessing && (
        <div className="processing-status">
          <div className="spinner"></div>
          <p>Processing your command...</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {transcript && (
        <div className="transcript-result">
          <h2>Recognized Command</h2>
          <p>{transcript}</p>
        </div>
      )}
    </div>
  );
};

export default VoiceCommands; 