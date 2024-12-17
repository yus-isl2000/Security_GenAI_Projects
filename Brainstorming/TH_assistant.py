from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import json
import webbrowser
import time
import pywinctl
from threading import Thread
import random  # Mock LLM API response

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
    "to_do": {
        "today": ["Update Incident Report", "Respond to Critical Alert"],
        "near_term": ["Draft Threat Hunt Summary"],
        "medium_term": ["Review Quarterly Security Trends"],
        "long_term": ["Prepare Budget Proposal"]
    },
    "email_calendar": {
        "emails": ["Security Alert", "Team Sync at 2 PM"],
        "calendar": ["9 AM: Threat Meeting", "3 PM: Product Update"]
    },
    "investigations": ["Investigate Phishing Campaign", "APT29 Analysis"],
    "threat_hunts": [
        {"name": "Beacon Detection", "progress": "50%"},
        {"name": "Insider Threat", "progress": "20%"}
    ],
    "gap_filling":["Missing agent for X"],
    "workflow_monitoring": {}
}

# Function registry for agents
agent_functions = {}

def register_agent(name):
    def decorator(func):
        agent_functions[name] = func
        return func
    return decorator

# Mock LLM API response
def call_mock_llm(tasks):
    return sorted(tasks, key=lambda _: random.random())

@register_agent("to_do")
def to_do_agent(new_input: str = None):
    if new_input:
        tasks = new_input.split("\n")
        mock_data["to_do"]["today"].extend(tasks)
        # Mock LLM response for reordering tasks
        all_tasks = mock_data["to_do"]["today"]
        reordered = call_mock_llm(all_tasks)
        mock_data["to_do"]["today"] = reordered
    return mock_data["to_do"]

@register_agent("email_calendar")
def email_calendar_agent(new_input: str = None):
    if new_input:
        mock_data["email_calendar"]["emails"].append(new_input)
        reordered_emails = call_mock_llm(mock_data["email_calendar"]["emails"])
        mock_data["email_calendar"]["emails"] = reordered_emails
    return mock_data["email_calendar"]

@register_agent("threat_hunts")
def threat_hunts_agent():
    return mock_data["threat_hunts"]

@register_agent("investigations")
def investigations_agent(new_input: str = None):
    if new_input:
        mock_data["investigations"].append(new_input)
        mock_data["investigations"] = call_mock_llm(mock_data["investigations"])
    return mock_data["investigations"]

@app.post("/input/{module}")
async def input_to_agent(module: str, new_input: str = Form(...)):
    if module in agent_functions:
        result = agent_functions[module](new_input)
        return {"status": "success", "module": module, "data": result}
    return {"status": "error", "message": "Agent not found"}

@app.get("/refresh/{module}")
async def refresh(module: str):
    agent = agent_functions.get(module)
    if agent:
        return {"status": "success", "module": module, "data": agent()}
    return {"status": "error", "message": "Agent not found"}


# Workflow Monitoring Agent
workflow_data = {}
@register_agent("workflow_monitoring")
def monitor_workflow():
    while True:
        try:
            active_window = pywinctl.getActiveWindow()
            window_title = active_window.title if active_window else "Unknown Window"

            current_time = time.time()
            if window_title in workflow_data:
                workflow_data[window_title]["time_spent"] += 1
            else:
                workflow_data[window_title] = {"time_spent": 1, "last_active": current_time}

            mock_data["workflow_monitoring"] = workflow_data
            time.sleep(1)  # Check every second
        except Exception as e:
            print(f"Error in workflow monitoring: {e}")
            time.sleep(1)


@app.get("/workflow_monitoring")
async def get_workflow_monitoring():
    """Get real-time workflow monitoring data."""
    return mock_data["workflow_monitoring"]

@app.get("/", response_class=HTMLResponse)
async def index():
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Assistant Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f9; }}
            div {{ margin: 20px 0; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }}
        </style>
    </head>
    <body>
        <h1>AI Assistant Dashboard</h1>

        <div>
            <h2>To-Do List</h2>
            <ul id="to-do-list">
                {"".join([f"<li>{task}</li>" for task in mock_data['to_do']['today']])}
            </ul>
            <form action="/input/to_do" method="post">
                <label>Add New Tasks:</label><br>
                <textarea name="new_input" rows="4" cols="50"></textarea><br>
                <button type="submit">Submit</button>
            </form>
        </div>

        <div>
            <h2>Email & Calendar</h2>
            <ul>
                {"".join([f"<li>{email}</li>" for email in mock_data['email_calendar']['emails']])}
            </ul>
            <form action="/input/email_calendar" method="post">
                <label>Add New Email:</label><br>
                <textarea name="new_input" rows="2" cols="50"></textarea><br>
                <button type="submit">Submit</button>
            </form>
        </div>

        <div>
            <h2>Investigations</h2>
            <ul>
                {"".join([f"<li>{task}</li>" for task in mock_data['investigations']])}
            </ul>
            <form action="/input/investigations" method="post">
                <label>Add Investigation Task:</label><br>
                <textarea name="new_input" rows="2" cols="50"></textarea><br>
                <button type="submit">Submit</button>
            </form>

        <div id="threat-hunts">
            <h2>Threat Hunts</h2>
            <ul>
                {"".join([f"<li>{hunt['name']}: {hunt['progress']}</li>" for hunt in mock_data['threat_hunts']])}
            </ul>
            <button onclick="refresh('threat_hunts')">Refresh</button>
        </div>


        <div id="gap-filling">
            <h2>Gap Filling</h2>
            <ul>
                {"".join([f"<li>{gap}</li>" for gap in mock_data['gap_filling']])}
            </ul>
            <button onclick="refresh('gap_filling')">Refresh</button>
        </div>

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

    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    Thread(target=monitor_workflow, daemon=True).start()
    Thread(target=lambda: webbrowser.open("http://127.0.0.1:8000")).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
