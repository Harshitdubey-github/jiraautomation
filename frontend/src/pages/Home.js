import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
  return (
    <div className="home">
      <h1>Welcome to Jira Voice Assistant</h1>
      <p>Use voice commands or paste meeting transcripts to manage your Jira tasks efficiently.</p>
      
      <div className="features">
        <div className="feature-card">
          <h2>Voice Commands</h2>
          <p>Use natural language to query, update, and create Jira tasks.</p>
          <Link to="/voice" className="feature-link">Try Voice Commands</Link>
        </div>
        
        <div className="feature-card">
          <h2>Transcript Parser</h2>
          <p>Paste your Teams meeting transcripts to extract action items and tasks.</p>
          <Link to="/transcript" className="feature-link">Parse Transcript</Link>
        </div>
      </div>
    </div>
  );
};

export default Home; 