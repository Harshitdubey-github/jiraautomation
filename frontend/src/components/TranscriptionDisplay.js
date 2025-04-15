import React, { useState } from 'react';
import './TranscriptionDisplay.css';

const TranscriptionDisplay = ({ transcription, parsedCommand, onConfirm, onCancel, onEdit }) => {
  const [editedTranscription, setEditedTranscription] = useState(transcription);
  const [isEditing, setIsEditing] = useState(false);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = () => {
    onEdit(editedTranscription);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedTranscription(transcription);
    setIsEditing(false);
  };

  return (
    <div className="transcription-display">
      <div className="transcription-section">
        <h3>Transcription</h3>
        {isEditing ? (
          <div className="edit-container">
            <textarea
              value={editedTranscription}
              onChange={(e) => setEditedTranscription(e.target.value)}
              className="transcription-edit"
            />
            <div className="edit-actions">
              <button onClick={handleSave} className="save-button">Save</button>
              <button onClick={handleCancel} className="cancel-button">Cancel</button>
            </div>
          </div>
        ) : (
          <div className="transcription-content">
            <p>{transcription}</p>
            <button onClick={handleEdit} className="edit-button">Edit</button>
          </div>
        )}
      </div>

      {parsedCommand && (
        <div className="command-section">
          <h3>Parsed Command</h3>
          <div className="command-content">
            <pre>{JSON.stringify(parsedCommand, null, 2)}</pre>
            <div className="command-actions">
              <button onClick={onConfirm} className="confirm-button">Confirm</button>
              <button onClick={onCancel} className="cancel-button">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TranscriptionDisplay; 