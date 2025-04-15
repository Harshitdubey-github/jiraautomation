import React, { useState, useRef, useEffect } from 'react';
import './AudioRecorder.css';

const AudioRecorder = ({ onTranscriptionComplete, onError }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await sendAudioToServer(audioBlob);
        
        // Stop all tracks in the stream
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prevTime => prevTime + 1);
      }, 1000);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      onError('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Clear timer
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const sendAudioToServer = async (audioBlob) => {
    setIsProcessing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.wav');
      
      const response = await fetch('http://localhost:8000/api/transcribe', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      onTranscriptionComplete(data);
    } catch (error) {
      console.error('Error sending audio to server:', error);
      onError('Failed to process audio. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="audio-recorder">
      <div className="recorder-controls">
        {!isRecording && !isProcessing ? (
          <button 
            className="record-button"
            onClick={startRecording}
            aria-label="Start Recording"
          >
            <span className="record-icon"></span>
            Start Recording
          </button>
        ) : isRecording ? (
          <button 
            className="stop-button"
            onClick={stopRecording}
            aria-label="Stop Recording"
          >
            <span className="stop-icon"></span>
            Stop Recording
          </button>
        ) : (
          <button className="processing-button" disabled>
            <span className="processing-icon"></span>
            Processing...
          </button>
        )}
      </div>
      
      {isRecording && (
        <div className="recording-indicator">
          <span className="recording-dot"></span>
          Recording: {formatTime(recordingTime)}
        </div>
      )}
      
      {isProcessing && (
        <div className="processing-indicator">
          <span className="processing-spinner"></span>
          Transcribing audio...
        </div>
      )}
    </div>
  );
};

export default AudioRecorder; 