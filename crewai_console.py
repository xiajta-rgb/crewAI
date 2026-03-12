import os
import json
import uuid
from pathlib import Path
from datetime import datetime

project_dir = Path(__file__).parent.absolute()
data_dir = project_dir / "data"
data_dir.mkdir(exist_ok=True)
os.environ["CREWAI_STORAGE_DIR"] = str(data_dir)

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

app = Flask(__name__, static_folder='.')
CORS(app)

QWEN_API_KEY = "sk-Nzg1LTEyODUyNTMzOTgyLTE3NzMyODM0OTQwMzA="
SERPER_API_KEY = "2dfc4669c627f419495740a8cab6a6942db04101"

os.environ["SERPER_API_KEY"] = SERPER_API_KEY
os.environ["LITELLM_DROP_PARAMS"] = "True"
os.environ["LITELLM_MAX_PARALLEL"] = "1"
os.environ["LITELLM_KEY"] = QWEN_API_KEY
os.environ["LITELLM_API_BASE"] = "https://api.scnet.cn/api/llm/v1"

llm = LLM(model="Qwen3-30B-A3B", api_key=QWEN_API_KEY, base_url="https://api.scnet.cn/api/llm/v1")
search_tool = SerperDevTool()

HISTORY_FILE = project_dir / "research_history.json"

agent_configs = [
    {"name": "行业研究专家", "role": "亚马逊跨境电商行业研究专家", "goal": "深入了解亚马逊跨境电商行业趋势、竞争格局、市场机会", "backstory": "你是一位资深的亚马逊跨境电商行业研究专家，拥有8年以上亚马逊平台运营和研究经验。", "tools": True},
    {"name": "调研企划专家", "role": "调研企划专家", "goal": "制定精准的调研计划和市场进入策略", "backstory": "你是一位专业的调研企划专家，擅长制定亚马逊跨境电商的市场调研计划和市场进入策略。", "tools": False},
    {"name": "调研技术专家", "role": "调研技术专家", "goal": "运用先进的技术工具进行深度市场调研", "backstory": "你是一位调研技术专家，精通各种市场调研工具和方法，擅长关键词分析、竞品监控等。", "tools": True},
    {"name": "报告撰写专家", "role": "调研报告撰写专家", "goal": "将复杂的调研结果转化为专业易懂的报告", "backstory": "你是一位专业的调研报告撰写专家，擅长将技术性的调研数据转化为清晰、有说服力的商业报告。", "tools": False}
]

task_configs = [
    {"name": "行业调研", "description": "调研{target}在亚马逊跨境电商行业的整体状况", "expected_output": "详细的行业调研报告"},
    {"name": "市场分析", "description": "对{target}进行细分市场分析", "expected_output": "细分市场分析报告"},
    {"name": "企划方案", "description": "制定{target}的市场进入策略", "expected_output": "市场企划方案"},
    {"name": "技术调研", "description": "运用技术工具进行{target}深度调研", "expected_output": "技术调研报告"},
    {"name": "报告撰写", "description": "整合{target}所有调研结果，撰写报告", "expected_output": "完整调研报告"}
]

def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def add_to_history(study_id, topic, agents, tasks, result):
    history = load_history()
    history.append({
        "id": study_id,
        "topic": topic,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "agents": agents,
        "tasks": tasks,
        "result": str(result) if result is not None else ""
    })
    save_history(history)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/styles.css')
def styles():
    return send_from_directory('.', 'styles.css')

@app.route('/app.js')
def js():
    return send_from_directory('.', 'app.js')

@app.route('/api/data')
def get_data():
    return jsonify({
        "agents": agent_configs,
        "tasks": task_configs,
        "history": load_history()
    })

@app.route('/api/agent', methods=['POST'])
def save_agent():
    data = request.json
    idx = data.get('index')
    if 0 <= idx < len(agent_configs):
        agent_configs[idx] = data.get('data')
    return jsonify({"success": True})

@app.route('/api/task', methods=['POST'])
def save_task():
    data = request.json
    idx = data.get('index')
    if 0 <= idx < len(task_configs):
        task_configs[idx] = data.get('data')
    return jsonify({"success": True})

@app.route('/api/research', methods=['POST'])
def run_research():
    topic = request.json.get('topic', '').strip()
    if not topic:
        return jsonify({"success": False, "error": "请输入调研主题"})
    
    try:
        agents = []
        for config in agent_configs:
            agent = Agent(
                role=config['role'],
                goal=config['goal'],
                backstory=config['backstory'],
                verbose=True,
                llm=llm,
                tools=[search_tool] if config['tools'] else []
            )
            agents.append(agent)

        tasks = []
        for i, config in enumerate(task_configs):
            agent_idx = min(i, len(agents) - 1)
            task = Task(
                description=config['description'].format(target=topic),
                agent=agents[agent_idx],
                expected_output=config['expected_output']
            )
            tasks.append(task)

        crew = Crew(
            name=f"亚马逊{topic}调研团队",
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
            cache=False
        )

        result = crew.kickoff()
        
        study_id = str(uuid.uuid4())[:8]
        agent_names = [a.role for a in agents]
        task_descriptions = [t.description for t in tasks]
        add_to_history(study_id, topic, agent_names, task_descriptions, result)
        
        return jsonify({
            "success": True,
            "result": str(result),
            "history": load_history()
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
