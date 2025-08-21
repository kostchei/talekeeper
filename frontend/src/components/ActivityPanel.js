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

