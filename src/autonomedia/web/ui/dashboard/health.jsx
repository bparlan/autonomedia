// src/autonomedia/web/ui/dashboard/health.jsx

import React, { useState, useEffect } from 'react';

const HealthDashboard = () => {
  const [healthStatus, setHealthStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await fetch('/api/health');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setHealthStatus(data);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
  }, []);

  const getStatusClass = (status) => {
    return status === 'healthy' ? 'status-healthy' : 'status-unhealthy';
  };

  return (
    <div>
      <h1>Infrastructure Health Dashboard</h1>
      {loading && <p>Loading health status...</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {!loading && !error && healthStatus && (
        <div>
          <h2>System Status</h2>
          <ul>
            <li>Database: <span className={getStatusClass(healthStatus.database)}>{healthStatus.database || 'N/A'}</span></li>
            <li>Runtime: <span className={getStatusClass(healthStatus.runtime)}>{healthStatus.runtime || 'N/A'}</span></li>
            <li>Tests: <span className={getStatusClass(healthStatus.tests)}>{healthStatus.tests || 'N/A'}</span></li>
            <li>Source: <span className={getStatusClass(healthStatus.src)}>{healthStatus.src || 'N/A'}</span></li>
          </ul>
        </div>
      )}
      {!loading && !error && !healthStatus && (
        <p>No health data available.</p>
      )}
    </div>
  );
};

export default HealthDashboard;
