/**
 * File: frontend/src/components/ActivityPanel.js
 * Path: /frontend/src/components/ActivityPanel.js
 * 
 * Activity Panel Component - Provides action buttons for different game activities.
 * 
 * Pseudo Code:
 * 1. Receive onAction callback and current locationType props
 * 2. Render activity selection header
 * 3. Display rest buttons (town/wilderness) with location-based enabling
 * 4. Show shopping button enabled only in town locations
 * 5. Execute onAction callback with activity type when buttons clicked
 * 
 * AI Agents: Simple UI component for game activity selection.
 */

import React from 'react';

const ActivityPanel = ({ onAction, locationType }) => {
  return (
    <div className="activity-panel">
      <h3>Choose Activity</h3>
      <div className="activity-buttons">
        <button className="btn" onClick={() => onAction('rest_town')} disabled={locationType !== 'town'}>
          Rest in Town
        </button>
        <button className="btn" onClick={() => onAction('rest_wilderness')} disabled={locationType !== 'wilderness'}>
          Rest in Wilderness
        </button>
        <button className="btn" onClick={() => onAction('shop')} disabled={locationType !== 'town'}>
          Shop in Town
        </button>
      </div>
    </div>
  );
};

export default ActivityPanel;

