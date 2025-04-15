import React from 'react';
import './ActionConfirmation.css';

const ActionConfirmation = ({ action, onConfirm, onCancel, onEdit }) => {
  const renderActionDetails = () => {
    switch (action.action) {
      case 'query_tasks':
        return (
          <div className="action-details">
            <p><strong>Action:</strong> Query Tasks</p>
            {action.filters && (
              <div className="filters-container">
                <p><strong>Filters:</strong></p>
                <ul>
                  {Object.entries(action.filters).map(([key, value]) => (
                    <li key={key}>
                      <strong>{key}:</strong> {value}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );
      
      case 'create_issue':
        return (
          <div className="action-details">
            <p><strong>Action:</strong> Create Issue</p>
            <p><strong>Summary:</strong> {action.summary}</p>
            {action.description && (
              <p><strong>Description:</strong> {action.description}</p>
            )}
            {action.assignee && (
              <p><strong>Assignee:</strong> {action.assignee}</p>
            )}
            {action.priority && (
              <p><strong>Priority:</strong> {action.priority}</p>
            )}
          </div>
        );
      
      case 'update_comment':
        return (
          <div className="action-details">
            <p><strong>Action:</strong> Add Comment</p>
            <p><strong>Task ID:</strong> {action.task_id}</p>
            <p><strong>Comment:</strong> {action.comment}</p>
          </div>
        );
      
      case 'update_status':
        return (
          <div className="action-details">
            <p><strong>Action:</strong> Update Status</p>
            <p><strong>Task ID:</strong> {action.task_id}</p>
            <p><strong>New Status:</strong> {action.status}</p>
          </div>
        );
      
      default:
        return (
          <div className="action-details">
            <p><strong>Action:</strong> {action.action}</p>
            <pre>{JSON.stringify(action, null, 2)}</pre>
          </div>
        );
    }
  };

  return (
    <div className="action-confirmation">
      <h3>Confirm Action</h3>
      
      <div className="confirmation-content">
        <div className="action-summary">
          <p>Please confirm the following action:</p>
          {renderActionDetails()}
        </div>
        
        <div className="confirmation-actions">
          <button 
            className="confirm-button"
            onClick={onConfirm}
          >
            Confirm
          </button>
          <button 
            className="edit-button"
            onClick={onEdit}
          >
            Edit
          </button>
          <button 
            className="cancel-button"
            onClick={onCancel}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default ActionConfirmation; 