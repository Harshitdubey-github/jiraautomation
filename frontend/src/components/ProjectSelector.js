import React, { useState, useEffect } from 'react';
import './ProjectSelector.css';

const ProjectSelector = ({ onProjectSelect, selectedProject }) => {
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch projects from the backend
        const response = await fetch('http://localhost:8000/api/jira/projects', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            // Add authorization header if needed
            // 'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch projects');
        }

        const data = await response.json();
        setProjects(data);
      } catch (err) {
        setError('Error loading projects. Please try again.');
        console.error('Error fetching projects:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProjects();
  }, []);

  const handleProjectChange = (event) => {
    const projectId = event.target.value;
    const project = projects.find(p => p.id === projectId);
    onProjectSelect(project);
  };

  return (
    <div className="project-selector">
      <label htmlFor="project-select">Select Jira Project</label>
      
      {isLoading ? (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <span>Loading projects...</span>
        </div>
      ) : error ? (
        <div className="error-message">
          {error}
        </div>
      ) : (
        <select 
          id="project-select" 
          value={selectedProject?.id || ''} 
          onChange={handleProjectChange}
          className="project-dropdown"
        >
          <option value="" disabled>Choose a project</option>
          {projects.map(project => (
            <option key={project.id} value={project.id}>
              {project.name} ({project.key})
            </option>
          ))}
        </select>
      )}
      
      {selectedProject && (
        <div className="selected-project-info">
          <h3>Selected Project</h3>
          <div className="project-details">
            <p><strong>Name:</strong> {selectedProject.name}</p>
            <p><strong>Key:</strong> {selectedProject.key}</p>
            {selectedProject.description && (
              <p><strong>Description:</strong> {selectedProject.description}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectSelector; 