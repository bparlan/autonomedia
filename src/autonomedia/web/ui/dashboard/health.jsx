import React, { useState, useEffect } from 'react';

const HealthDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [healthData, setHealthData] = useState(null);

  useEffect(() => {
    const fetchHealthData = async () => {
      try {
        const response = await fetch('/api/health');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setHealthData(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchHealthData();
  }, []);

  if (loading) {
    return (
      <div className="health-dashboard">
        <h1>Infrastructure Health Dashboard</h1>
        <p>Loading health status...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="health-dashboard">
        <h1>Infrastructure Health Dashboard</h1>
        <p style={{ color: 'red' }}>Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="health-dashboard">
      <h1>Infrastructure Health Dashboard</h1>
      {!healthData ? (
        <p>No health data available</p>
      ) : (
        <div>
          <h2>System Status</h2>
          <ul>
            <li>
              Database: <span className={healthData.database === 'healthy' ? 'status-healthy' : 'status-unhealthy'}>
                {healthData.database}
              </span>
            </li>
            <li>
              Runtime: <span className={healthData.runtime === 'healthy' ? 'status-healthy' : 'status-unhealthy'}>
                {healthData.runtime}
              </span>
            </li>
            <li>
              Tests: <span className={healthData.tests === 'healthy' ? 'status-healthy' : 'status-unhealthy'}>
                {healthData.tests}
              </span>
            </li>
            <li>
              Source: <span className={healthData.src === 'healthy' ? 'status-healthy' : 'status-unhealthy'}>
                {healthData.src}
              </span>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default HealthDashboard;
// Test utility functions
export const getHealthStatus = (data) => {
  if (!data) return null;
  
  const status = {};
  for (const [component, value] of Object.entries(data)) {
    status[component] = {
      value,
      isHealthy: value === 'healthy',
      isUnhealthy: value === 'unhealthy',
      valid: ['healthy', 'unhealthy'].includes(value)
    };
  }
  
  return status;
};

export const validateHealthData = (data) => {
  if (!data || typeof data !== 'object') {
    return { valid: false, error: 'Invalid health data' };
  }
  
  const requiredFields = ['database', 'runtime', 'tests', 'src'];
  const missingFields = requiredFields.filter(field => !(field in data));
  if (missingFields.length > 0) {
    return { valid: false, error: `Missing fields: ${missingFields.join(', ')}` };
  }
  
  const invalidFields = {};
  for (const [component, value] of Object.entries(data)) {
    if (value !== 'healthy' && value !== 'unhealthy') {
      invalidFields[component] = value;
    }
  }
  
  if (Object.keys(invalidFields).length > 0) {
    return { valid: false, error: `Invalid values: ${JSON.stringify(invalidFields)}` };
  }
  
  return { valid: true };
};

export const getHealthyComponents = (data) => {
  if (!data) return [];
  return Object.entries(data)
    .filter(([_, value]) => value === 'healthy')
    .map(([component]) => component);
};

export const getUnhealthyComponents = (data) => {
  if (!data) return [];
  return Object.entries(data)
    .filter(([_, value]) => value === 'unhealthy')
    .map(([component]) => component);
};

export const hasAllHealthy = (data) => {
  if (!data) return false;
  return Object.values(data).every(value => value === 'healthy');
};

export const hasCriticalFailure = (data) => {
  if (!data) return false;
  return Object.values(data).some(value => value === 'unhealthy');
};
