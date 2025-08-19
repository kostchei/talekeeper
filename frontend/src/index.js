/**
 * File: frontend/src/index.js
 * Path: /frontend/src/index.js
 * 
 * React Application Entry Point
 * 
 * Pseudo Code:
 * 1. Import React and ReactDOM for rendering
 * 2. Import main App component and base styles
 * 3. Create root DOM element and render App component
 * 4. Set up error boundaries and performance monitoring
 * 5. Enable React strict mode for development warnings
 * 
 * AI Agents: This is the React entry point. App component handles all routing.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/main.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);