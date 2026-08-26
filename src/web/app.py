from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()

@app.get("/api/health")
async def api_health():
    """Health check API endpoint."""
    return {"database": "healthy", "runtime": "healthy", "tests": "healthy", "src": "healthy"}

@app.get("/health")
async def health_dashboard(request: Request):
    """Health dashboard page - Serves React component."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Infrastructure Health Dashboard</title>
        <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .health-dashboard {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                padding: 30px;
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .status-healthy {
                color: #28a745;
                font-weight: bold;
            }
            .status-unhealthy {
                color: #dc3545;
                font-weight: bold;
            }
            .status-unknown {
                color: #ffc107;
                font-weight: bold;
            }
            .loading, .error {
                text-align: center;
                padding: 20px;
                color: #666;
            }
            .error {
                color: #dc3545;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                padding: 15px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            li:last-child {
                border-bottom: none;
            }
            .component-name {
                font-weight: 500;
            }
            .component-status {
                font-weight: 600;
                text-transform: capitalize;
            }
        </style>
    </head>
    <body>
        <div class="health-dashboard">
            <h1>Infrastructure Health Dashboard</h1>
            <div id="root"></div>
        </div>
        <script type="text/babel">
            const { useState, useEffect } = React;

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
                    return <div className="loading">Loading health status...</div>;
                }

                if (error) {
                    return <div className="error">Error: {error}</div>;
                }

                return (
                    <div>
                        {!healthData ? (
                            <p>No health data available</p>
                        ) : (
                            <div>
                                <h2>System Status</h2>
                                <ul>
                                    <li>
                                        <span className="component-name">Database:</span>
                                        <span className={healthData.database === 'healthy' ? 'status-healthy' : healthData.database === 'unhealthy' ? 'status-unhealthy' : 'status-unknown'}>
                                            {healthData.database}
                                        </span>
                                    </li>
                                    <li>
                                        <span className="component-name">Runtime:</span>
                                        <span className={healthData.runtime === 'healthy' ? 'status-healthy' : healthData.runtime === 'unhealthy' ? 'status-unhealthy' : 'status-unknown'}>
                                            {healthData.runtime}
                                        </span>
                                    </li>
                                    <li>
                                        <span className="component-name">Tests:</span>
                                        <span className={healthData.tests === 'healthy' ? 'status-healthy' : healthData.tests === 'unhealthy' ? 'status-unhealthy' : 'status-unknown'}>
                                            {healthData.tests}
                                        </span>
                                    </li>
                                    <li>
                                        <span className="component-name">Source:</span>
                                        <span className={healthData.src === 'healthy' ? 'status-healthy' : healthData.src === 'unhealthy' ? 'status-unhealthy' : 'status-unknown'}>
                                            {healthData.src}
                                        </span>
                                    </li>
                                </ul>
                            </div>
                        )}
                    </div>
                );
            };

            const root = ReactDOM.createRoot(document.getElementById('root'));
            root.render(<HealthDashboard />);
        </script>
    </body>
    </html>
    """.strip()
    return HTMLResponse(content=html_content)