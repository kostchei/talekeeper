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

