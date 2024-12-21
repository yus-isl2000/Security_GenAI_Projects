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
import requests
import os


#export API_KEY=
API_KEY = os.getenv('API_KEY')

def call_gemini_api(prompt, api_key):
    # Define the endpoint URL
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'

    # Define the headers
    headers = {
        'Content-Type': 'application/json'
    }

    # Define the payload
    payload = {
        'contents': [
            {
                'parts': [
                    {
                        'text': prompt
                    }
                ]
            }
        ]
    }

    try:
        # Make the POST request
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the JSON response
        result = response.json()
        candidates = result.get('candidates', [])

        # If you want to extract the 'text' from the first candidate's content parts
        if candidates:
            first_candidate = candidates[0]
            content = first_candidate.get('content', {})
            parts = content.get('parts', [])
            if parts:
                text = parts[0].get('text', '')
                return text
            else:
                print("No parts found in the first candidate's content.")
        else:
            print("No candidates found in the response.")

        return result

    except requests.exceptions.RequestException as e:
        print(f'HTTP Request failed: {e}')
        return None

print(call_gemini_api("hi!",API_KEY))
exit(0)

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
    "gap_filling": ["Missing Endpoint Coverage", "No Log Data for Server 3"],
    "workflow_monitoring": {},
    "threat_hunts": [
        {"name": "Beacon Detection", "progress": "50%"},
        {"name": "Insider Threat", "progress": "20%"}
    ]
}

# Function registry for agents
agent_functions = {}

def register_agent(name):
    def decorator(func):
        agent_functions[name] = func
        return func
    return decorator

# Mock LLM API response with prompts
def call_mock_llm(prompt: str, data: list):
    result = call_gemini_api(f"LLM Prompt: {prompt}\nData: {data}", API_KEY)
    print(result)
    return result.splitlines() if result else data

@register_agent("to_do")
def to_do_agent(new_input: str = None):
    prompt = "Prioritize the following tasks. Consider any new tasks provided and integrate them into the appropriate priority order."
    if new_input:
        tasks = new_input.split("\n")
        mock_data["to_do"]["today"].extend(tasks)
        all_tasks = mock_data["to_do"]["today"]
        mock_data["to_do"]["today"] = call_mock_llm(prompt, all_tasks)
    return mock_data["to_do"]

@register_agent("email_calendar")
def email_calendar_agent(new_input: str = None):
    prompt = "Sort the emails by importance and ensure calendar entries remain updated."
    if new_input:
        mock_data["email_calendar"]["emails"].append(new_input)
        mock_data["email_calendar"]["emails"] = call_mock_llm(prompt, mock_data["email_calendar"]["emails"])
    return mock_data["email_calendar"]

@register_agent("investigations")
def investigations_agent(new_input: str = None):
    prompt = "Build a Threat Hunting Report based on the provided initial investigation input."
    if new_input:
        mock_data["investigations"].append(new_input)
        mock_data["investigations"] = call_mock_llm(prompt, mock_data["investigations"])
    return mock_data["investigations"]

@register_agent("gap_filling")
def gap_filling_agent(new_input: str = None):
    prompt = "Analyze gaps in the system and suggest actionable items for filling missing areas."
    if new_input:
        mock_data["gap_filling"].append(new_input)
        mock_data["gap_filling"] = call_mock_llm(prompt, mock_data["gap_filling"])
    return mock_data["gap_filling"]

@register_agent("threat_hunts")
def threat_hunts_agent(new_input: str = None):
    placeholder_prompt = "Analyze new threat hunt input and update progress accordingly."
    if new_input:
        mock_data["threat_hunts"].append({"name": new_input, "progress": "0%"})
    return mock_data["threat_hunts"]

# Workflow Monitoring Agent
workflow_data = {}
@register_agent("workflow_monitoring")
def monitor_workflow():
    while True:
        try:
            active_window = pywinctl.getActiveWindow()
            window_title = active_window.title
            current_time = time.time()
            if window_title:
                if window_title in workflow_data:
                    workflow_data[window_title]["time_spent"] += 1
                else:
                    workflow_data[window_title] = {"time_spent": 1, "last_active": current_time}
            mock_data["workflow_monitoring"] = workflow_data
            time.sleep(1)
        except Exception as e:
            print(f"Error in workflow monitoring: {e}")
            time.sleep(1)

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

@app.get("/workflow_monitoring")
async def get_workflow_monitoring():
    return mock_data["workflow_monitoring"]

@app.get("/", response_class=HTMLResponse)
async def index():
    html_content = f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
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
            <ul id=\"to-do-list\">
                {"".join([f"<li>{task}</li>" for task in mock_data['to_do']['today']])}
            </ul>
            <form onsubmit=\"submitForm(event, 'to_do', 'to-do-list')\">
                <label>Add New Tasks:</label><br>
                <textarea name=\"new_input\" rows=\"4\" cols=\"50\"></textarea><br>
                <button type=\"submit\">Submit</button>
            </form>
            <button onclick=\"refreshData('to_do', 'to-do-list')\">Refresh</button>
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
                <label>Start New Investigation:</label><br>
                <textarea name="new_input" rows="2" cols="50"></textarea><br>
                <button type="submit">Submit</button>
            </form>
        </div>

        <div>
            <h2>Gap Filling</h2>
            <ul>
                {"".join([f"<li>{gap}</li>" for gap in mock_data['gap_filling']])}
            </ul>
            <form action="/input/gap_filling" method="post">
                <label>Fill Missing Gaps:</label><br>
                <textarea name="new_input" rows="2" cols="50"></textarea><br>
                <button type="submit">Submit</button>
            </form>
        </div>

        <div id="threat-hunts">
            <h2>Threat Hunts</h2>
            <ul>
                {"".join([f"<li>{hunt['name']}: {hunt['progress']}</li>" for hunt in mock_data['threat_hunts']])}
            </ul>
            <form action="/input/threat_hunts" method="post">
                <label>Add New Threat Hunt:</label><br>
                <textarea name="new_input" rows="2" cols="50"></textarea><br>
                <button type="submit">Submit</button>
            </form>
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

        <script>
            async function submitForm(event, module, listId) {{
                event.preventDefault();
                const formData = new FormData(event.target);
                const newInput = formData.get('new_input');
                
                const response = await fetch(`/input/${{module}}`, {{
                    method: "POST",
                    body: new URLSearchParams({{ new_input: newInput }}),
                }});

                const result = await response.json();
                if (result.status === "success") {{
                    const listElement = document.getElementById(listId);
                    listElement.innerHTML = result.data
                        .map((item) => `<li>${{item}}</li>`)
                        .join("");
                }} else {{
                    alert(result.message || "Error updating data.");
                }}
            }}

            async function refreshData(module, listId) {{
                const response = await fetch(`/refresh/${{module}}`);
                const result = await response.json();
                if (result.status === "success") {{
                    const listElement = document.getElementById(listId);
                    if (Array.isArray(result.data)) {{
                        listElement.innerHTML = result.data
                            .map((item) => `<li>${{item}}</li>`)
                            .join("");
                    }} else if (typeof result.data === "object") {{
                        listElement.innerHTML = Object.entries(result.data)
                            .map(([key, value]) => `<li>${{key}}: ${{value}}</li>`)
                            .join("");
                    }}
                }} else {{
                    alert(result.message || "Error refreshing data.");
                }}
            }}

            async function getWorkflowData() {{
                const response = await fetch(`/workflow_monitoring`);
                const workflowList = await response.json();
                const workflowElement = document.getElementById("workflow-list");

                workflowElement.innerHTML = Object.entries(workflowList)
                    .map(
                        ([window, data]) =>
                            `<li>${{window}}: ${{data.time_spent}} seconds</li>`
                    )
                    .join("");
            }}

            setInterval(getWorkflowData, 5000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Launch the workflow monitoring agent in a separate thread
Thread(target=monitor_workflow, daemon=True).start()

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
