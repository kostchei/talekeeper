/**
 * File: frontend/src/components/ActionLog.js
 * Path: /frontend/src/components/ActionLog.js
 * 
 * Action Log Component - Displays timestamped action/combat log entries with auto-scroll.
 * 
 * Pseudo Code:
 * 1. Initialize with entries array prop and create scroll reference
 * 2. Auto-scroll to bottom when new entries are added via useEffect
 * 3. Display placeholder text when no entries exist
 * 4. Render each entry with timestamp and message formatting
 * 5. Handle various entry formats (objects with message/text or plain strings)
 * 
 * AI Agents: Simple display component for game action logging.
 */

import React, { useEffect, useRef } from 'react';

const ActionLog = ({ entries = [] }) => {
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [entries]);

  return (
    <div className="action-log">
      <h3>Action Log</h3>
      <div className="log-entries" ref={logRef}>
        {entries.length === 0 ? (
          <div className="log-entry system">Actions will appear here...</div>
        ) : (
          entries.map((entry, index) => (
            <div key={index} className="log-entry">
              <span className="timestamp">
                {new Date(entry.timestamp || Date.now()).toLocaleTimeString()}
              </span>
              <span className="message">
                {entry.message || entry.text || entry}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ActionLog;

