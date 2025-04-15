import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TranscriptParser from '../TranscriptParser';

describe('TranscriptParser Component', () => {
  const mockOnParseComplete = jest.fn();
  const mockOnError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn();
  });

  it('renders transcript input and parse button', () => {
    render(
      <TranscriptParser 
        onParseComplete={mockOnParseComplete}
        onError={mockOnError}
      />
    );

    expect(screen.getByPlaceholderText('Paste your Teams meeting transcript here...')).toBeInTheDocument();
    expect(screen.getByText('Parse Transcript')).toBeInTheDocument();
  });

  it('handles empty transcript submission', async () => {
    render(
      <TranscriptParser 
        onParseComplete={mockOnParseComplete}
        onError={mockOnError}
      />
    );

    const parseButton = screen.getByText('Parse Transcript');
    fireEvent.click(parseButton);

    expect(mockOnError).toHaveBeenCalledWith('Please enter a transcript to parse');
  });

  it('successfully parses a transcript', async () => {
    const mockResponse = {
      actions: [
        {
          action_type: 'create',
          project_key: 'TEST',
          summary: 'Test task',
          description: 'Test description'
        }
      ]
    };

    global.fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })
    );

    render(
      <TranscriptParser 
        onParseComplete={mockOnParseComplete}
        onError={mockOnError}
      />
    );

    const input = screen.getByPlaceholderText('Paste your Teams meeting transcript here...');
    fireEvent.change(input, { target: { value: 'Test transcript' } });

    const parseButton = screen.getByText('Parse Transcript');
    fireEvent.click(parseButton);

    await waitFor(() => {
      expect(screen.getByText('Identified Actions')).toBeInTheDocument();
      expect(screen.getByText('Create Issue')).toBeInTheDocument();
      expect(screen.getByText('Test task')).toBeInTheDocument();
    });

    expect(mockOnParseComplete).toHaveBeenCalledWith(mockResponse);
  });

  it('handles API errors gracefully', async () => {
    global.fetch.mockImplementationOnce(() =>
      Promise.reject(new Error('API Error'))
    );

    render(
      <TranscriptParser 
        onParseComplete={mockOnParseComplete}
        onError={mockOnError}
      />
    );

    const input = screen.getByPlaceholderText('Paste your Teams meeting transcript here...');
    fireEvent.change(input, { target: { value: 'Test transcript' } });

    const parseButton = screen.getByText('Parse Transcript');
    fireEvent.click(parseButton);

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Failed to parse transcript. Please try again.');
    });
  });

  it('handles action confirmation', async () => {
    const mockResponse = {
      actions: [
        {
          action_type: 'create',
          project_key: 'TEST',
          summary: 'Test task',
          description: 'Test description'
        }
      ]
    };

    const mockConfirmResponse = {
      success: true,
      issue_key: 'TEST-123'
    };

    global.fetch
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockResponse)
        })
      )
      .mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockConfirmResponse)
        })
      );

    render(
      <TranscriptParser 
        onParseComplete={mockOnParseComplete}
        onError={mockOnError}
      />
    );

    // Parse transcript
    const input = screen.getByPlaceholderText('Paste your Teams meeting transcript here...');
    fireEvent.change(input, { target: { value: 'Test transcript' } });
    fireEvent.click(screen.getByText('Parse Transcript'));

    // Wait for actions to appear
    await waitFor(() => {
      expect(screen.getByText('Create Issue')).toBeInTheDocument();
    });

    // Confirm action
    fireEvent.click(screen.getByText('Confirm'));

    await waitFor(() => {
      expect(screen.getByText('completed')).toBeInTheDocument();
    });
  });

  it('handles action skipping', async () => {
    const mockResponse = {
      actions: [
        {
          action_type: 'create',
          project_key: 'TEST',
          summary: 'Test task',
          description: 'Test description'
        }
      ]
    };

    global.fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })
    );

    render(
      <TranscriptParser 
        onParseComplete={mockOnParseComplete}
        onError={mockOnError}
      />
    );

    // Parse transcript
    const input = screen.getByPlaceholderText('Paste your Teams meeting transcript here...');
    fireEvent.change(input, { target: { value: 'Test transcript' } });
    fireEvent.click(screen.getByText('Parse Transcript'));

    // Wait for actions to appear
    await waitFor(() => {
      expect(screen.getByText('Create Issue')).toBeInTheDocument();
    });

    // Skip action
    fireEvent.click(screen.getByText('Skip'));

    await waitFor(() => {
      expect(screen.getByText('skipped')).toBeInTheDocument();
    });
  });
}); 