import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import AudioRecorder from '../AudioRecorder';

// Mock the MediaRecorder API
const mockMediaRecorder = {
  start: jest.fn(),
  stop: jest.fn(),
  state: 'inactive',
  ondataavailable: null,
  onstop: null,
};

global.MediaRecorder = jest.fn(() => mockMediaRecorder);
global.URL.createObjectURL = jest.fn();

// Mock getUserMedia
const mockGetUserMedia = jest.fn(() => Promise.resolve({
  getTracks: () => [{
    stop: jest.fn()
  }]
}));
global.navigator.mediaDevices = {
  getUserMedia: mockGetUserMedia
};

describe('AudioRecorder Component', () => {
  const mockOnTranscriptionComplete = jest.fn();
  const mockOnError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders start recording button initially', () => {
    render(
      <AudioRecorder 
        onTranscriptionComplete={mockOnTranscriptionComplete}
        onError={mockOnError}
      />
    );
    
    expect(screen.getByText('Start Recording')).toBeInTheDocument();
  });

  it('shows stop button when recording', async () => {
    render(
      <AudioRecorder 
        onTranscriptionComplete={mockOnTranscriptionComplete}
        onError={mockOnError}
      />
    );

    const startButton = screen.getByText('Start Recording');
    await act(async () => {
      fireEvent.click(startButton);
    });

    expect(screen.getByText('Stop Recording')).toBeInTheDocument();
    expect(mockGetUserMedia).toHaveBeenCalledWith({ audio: true });
  });

  it('handles recording errors gracefully', async () => {
    mockGetUserMedia.mockRejectedValueOnce(new Error('Permission denied'));

    render(
      <AudioRecorder 
        onTranscriptionComplete={mockOnTranscriptionComplete}
        onError={mockOnError}
      />
    );

    const startButton = screen.getByText('Start Recording');
    await act(async () => {
      fireEvent.click(startButton);
    });

    expect(mockOnError).toHaveBeenCalledWith('Could not access microphone. Please check permissions.');
  });

  it('stops recording when stop button is clicked', async () => {
    render(
      <AudioRecorder 
        onTranscriptionComplete={mockOnTranscriptionComplete}
        onError={mockOnError}
      />
    );

    // Start recording
    const startButton = screen.getByText('Start Recording');
    await act(async () => {
      fireEvent.click(startButton);
    });

    // Stop recording
    const stopButton = screen.getByText('Stop Recording');
    await act(async () => {
      fireEvent.click(stopButton);
    });

    expect(mockMediaRecorder.stop).toHaveBeenCalled();
    expect(screen.getByText('Start Recording')).toBeInTheDocument();
  });

  it('shows processing state while transcribing', async () => {
    // Mock a delayed response from the server
    global.fetch = jest.fn(() => 
      new Promise(resolve => 
        setTimeout(() => 
          resolve({
            ok: true,
            json: () => Promise.resolve({ transcript: 'Test transcript' })
          }), 100)
        )
      )
    );

    render(
      <AudioRecorder 
        onTranscriptionComplete={mockOnTranscriptionComplete}
        onError={mockOnError}
      />
    );

    // Start and stop recording
    const startButton = screen.getByText('Start Recording');
    await act(async () => {
      fireEvent.click(startButton);
    });

    const stopButton = screen.getByText('Stop Recording');
    await act(async () => {
      fireEvent.click(stopButton);
    });

    // Check for processing state
    expect(screen.getByText('Processing...')).toBeInTheDocument();
  });
}); 