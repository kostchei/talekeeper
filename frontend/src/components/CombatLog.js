/**
 * File: frontend/src/components/CombatLog.js
 * Path: /frontend/src/components/CombatLog.js
 * 
 * Combat Log Component
 * 
 * Pseudo Code:
 * 1. Display chronological list of combat events
 * 2. Show attack rolls, damage dealt, and status effects
 * 3. Auto-scroll to newest entries
 * 4. Color-code different types of log entries
 * 5. Provide combat history for reference
 * 
 * AI Agents: Combat event logging with formatting and auto-scroll.
 */

import React, { useEffect, useRef } from 'react';

const CombatLog = ({ entries = [] }) => {
  const logRef = useRef(null);

  useEffect(() => {
    // Auto-scroll to bottom when new entries are added
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [entries]);

  const formatLogEntry = (entry) => {
    const timestamp = new Date(entry.timestamp || Date.now()).toLocaleTimeString();
    
    let className = 'log-entry';
    if (entry.type === 'damage') className += ' damage';
    else if (entry.type === 'healing') className += ' healing';
    else if (entry.type === 'miss') className += ' miss';
    else if (entry.type === 'critical') className += ' critical';
    else if (entry.type === 'system') className += ' system';

    return { className, timestamp };
  };

  return (
    <div className="combat-log">
      <h3>Combat Log</h3>
      <div className="log-entries" ref={logRef}>
        {entries.length === 0 ? (
          <div className="log-entry system">
            Combat log will appear here...
          </div>
        ) : (
          entries.map((entry, index) => {
            const { className, timestamp } = formatLogEntry(entry);
            
            return (
              <div key={index} className={className}>
                <span className="timestamp">{timestamp}</span>
                <span className="message">
                  {typeof entry === 'string' ? entry : entry.message || entry.text || 'Unknown action'}
                </span>
              </div>
            );
          })
        )}
      </div>
      
      <div className="log-controls">
        <button 
          className="clear-log"
          onClick={() => {
            // TODO: Implement log clearing
            console.log('Clear log not yet implemented');
          }}
        >
          Clear Log
        </button>
      </div>
    </div>
  );
};

export default CombatLog;