import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Layout.css';

const Layout = ({ children }) => {
  const location = useLocation();
  
  return (
    <div className="layout">
      <header className="header">
        <div className="logo">
          <Link to="/">Jira Voice Assistant</Link>
        </div>
        <nav className="nav">
          <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
            Home
          </Link>
          <Link to="/voice" className={location.pathname === '/voice' ? 'active' : ''}>
            Voice Commands
          </Link>
          <Link to="/transcript" className={location.pathname === '/transcript' ? 'active' : ''}>
            Transcript Parser
          </Link>
        </nav>
      </header>
      <main className="main-content">
        {children}
      </main>
      <footer className="footer">
        <p>&copy; 2024 Jira Voice Assistant. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Layout; 