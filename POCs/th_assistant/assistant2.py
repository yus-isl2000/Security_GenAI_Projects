from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import json
import webbrowser
import time
import psutil
from threading import Thread

app = FastAPI()

# Allow cross-origin requests (for local development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (HTML, CSS, JS)
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Dummy data to simulate agent outputs
mock_data = {
    "email_calendar": {
        "emails": ["Important: Security Incident", "Meeting Reminder: Team Sync"],
        "calendar": ["10:00 AM - Security Briefing", "2:00 PM - Product Launch"]
    },
    "to_do": {
        "today": ["Update Incident Report", "Respond to Critical Alert"],
        "near_term": ["Draft Threat Hunt Summary"],
        "medium_term": ["Review Quarterly Security Trends"],
        "long_term": ["Prepare Budget Proposal"]
    },
    "investigations": [
        {"name": "APT29 Analysis", "status": "In Progress"},
        {"name": "Phishing Campaign", "status": "Pending"}
    ],
    "threat_hunts": [
        {"name": "Beacon Detection", "progress": "50%"},
        {"name": "Insider Threat", "progress": "20%"}
    ],
    "threat_intel": [
        "Ransomware Trends 2024",
        "Emerging Techniques: Fileless Malware"
    ],
    "gap_filling": ["Missing data for Endpoint Coverage"],
    "workflow_monitoring": {}
}

# Workflow Monitoring Agent
workflow_data = {}
def monitor_workflow():
    while True:
        active_window = "Unknown"
        try:
            for proc in psutil.process_iter(['name', 'pid']):
                if "chrome" in proc.info['name'].lower():  # Example for tracking Chrome
                    active_window = f"Browser: {proc.info['name']}"
                    break
        except Exception as e:
            active_window = f"Error: {str(e)}"
        
        current_time = time.time()
        if active_window in workflow_data:
            workflow_data[active_window]["time_spent"] += 1
        else:
            workflow_data[active_window] = {"time_spent": 1, "last_active": current_time}
        
        mock_data["workflow_monitoring"] = workflow_data
        time.sleep(1)  # Check every second

@app.get("/workflow_monitoring")
async def get_workflow_monitoring():
    """Get real-time workflow monitoring data."""
    return mock_data["workflow_monitoring"]

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main dashboard page."""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Assistant Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 0;
                background-color: #f4f4f9;
            }}
            h1 {{
                color: #0056b3;
            }}
            div {{
                background: #fff;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }}
            button {{
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #0056b3;
            }}
            ul {{
                list-style-type: none;
                padding: 0;
            }}
            li {{
                margin: 5px 0;
            }}
        </style>
    </head>
    <body>
        <h1>AI Assistant Dashboard</h1>
        <div id="email-calendar">
            <h2>Email & Calendar</h2>
            <p>Emails: {', '.join(mock_data['email_calendar']['emails'])}</p>
            <p>Calendar: {', '.join(mock_data['email_calendar']['calendar'])}</p>
            <button onclick="refresh('email_calendar')">Refresh</button>
        </div>

        <div id="to-do">
            <h2>To-Do List</h2>
            <ul>
                <li><strong>Today:</strong> {', '.join(mock_data['to_do']['today'])}</li>
                <li><strong>Near-term:</strong> {', '.join(mock_data['to_do']['near_term'])}</li>
                <li><strong>Medium-term:</strong> {', '.join(mock_data['to_do']['medium_term'])}</li>
                <li><strong>Long-term:</strong> {', '.join(mock_data['to_do']['long_term'])}</li>
            </ul>
            <button onclick="refresh('to_do')">Refresh</button>
        </div>

        <div id="investigations">
            <h2>Investigations</h2>
            <ul>
                {"".join([f"<li>{inv['name']}: {inv['status']}</li>" for inv in mock_data['investigations']])}
            </ul>
            <button onclick="refresh('investigations')">Refresh</button>
        </div>

        <div id="threat-hunts">
            <h2>Threat Hunts</h2>
            <ul>
                {"".join([f"<li>{hunt['name']}: {hunt['progress']}</li>" for hunt in mock_data['threat_hunts']])}
            </ul>
            <button onclick="refresh('threat_hunts')">Refresh</button>
        </div>

        <div id="threat-intel">
            <h2>Threat Intel Research</h2>
            <ul>
                {"".join([f"<li>{intel}</li>" for intel in mock_data['threat_intel']])}
            </ul>
            <button onclick="refresh('threat_intel')">Refresh</button>
        </div>

        <div id="gap-filling">
            <h2>Gap Filling</h2>
            <ul>
                {"".join([f"<li>{gap}</li>" for gap in mock_data['gap_filling']])}
            </ul>
            <button onclick="refresh('gap_filling')">Refresh</button>
        </div>

        <div id="workflow-monitoring">
            <h2>Workflow Monitoring</h2>
            <ul id="workflow-list"></ul>
                <script>
                    async function fetchWorkflowData() {{
                        const response = await fetch('/workflow_monitoring');
                        const data = await response.json();
                        const list = document.getElementById('workflow-list');
                        list.innerHTML = '';
                        Object.entries(data).forEach(([key, value]) => {{
                            if (value.time_spent !== undefined) {{
                                list.innerHTML += `<li>${{key}}: ${{value.time_spent}}s</li>`;
                            }}
                        }});
                    }}
                    setInterval(fetchWorkflowData, 3000);
                    fetchWorkflowData();
                </script>
        </div>

        <script>
            function refresh(module) {{
                alert('Refreshing ' + module + ' module!');
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/refresh/{module}")
async def refresh(module: str):
    """Endpoint to simulate refreshing a module."""
    return {"status": "success", "module": module, "data": mock_data.get(module, "Unknown module")}

if __name__ == "__main__":
    # Launch browser automatically
    Thread(target=lambda: webbrowser.open("http://127.0.0.1:8000")).start()
    # Start the workflow monitoring thread
    Thread(target=monitor_workflow, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
