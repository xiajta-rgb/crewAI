import os
import time
from pathlib import Path

project_dir = Path(__file__).parent.absolute()
data_dir = project_dir / "data"
data_dir.mkdir(exist_ok=True)
os.environ["CREWAI_STORAGE_DIR"] = str(data_dir)

from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

QWEN_API_KEY = "sk-Nzg1LTEyODUyNTMzOTgyLTE3NzMyODM0OTQwMzA="
SERPER_API_KEY = "2dfc4669c627f419495740a8cab6a6942db04101"

os.environ["SERPER_API_KEY"] = SERPER_API_KEY
os.environ["LITELLM_DROP_PARAMS"] = "True"
os.environ["LITELLM_MAX_PARALLEL"] = "1"
os.environ["LITELLM_KEY"] = QWEN_API_KEY
os.environ["LITELLM_API_BASE"] = "https://api.scnet.cn/api/llm/v1"
os.environ["LITELLM_MODEL_ALIASES"] = '{"qwen3-30b-a3b": "Qwen3-30B-A3B"}'

time.sleep(2)

llm = LLM(
    model="Qwen3-30B-A3B",
    api_key=QWEN_API_KEY,
    base_url="https://api.scnet.cn/api/llm/v1"
)

search_tool = SerperDevTool()

researcher = Agent(
    role="亚马逊跨境电商行业研究专家",
    goal="深入了解亚马逊跨境电商行业趋势、竞争格局、市场机会",
    backstory="你是一位资深的亚马逊跨境电商行业研究专家，拥有8年以上亚马逊平台运营和研究经验。你精通亚马逊各站点的市场动态，擅长分析行业趋势、竞争对手状况以及市场机会。",
    verbose=True,
    llm=llm,
    tools=[search_tool]
)

planner = Agent(
    role="调研企划专家",
    goal="制定精准的调研计划和市场进入策略",
    backstory="你是一位专业的调研企划专家，擅长制定亚马逊跨境电商的市场调研计划和市场进入策略。",
    verbose=True,
    llm=llm
)

tech_researcher = Agent(
    role="调研技术专家",
    goal="运用先进的技术工具进行深度市场调研",
    backstory="你是一位调研技术专家，精通各种市场调研工具和方法，擅长关键词分析、竞品监控等。",
    verbose=True,
    llm=llm,
    tools=[search_tool]
)

report_writer = Agent(
    role="调研报告撰写专家",
    goal="将复杂的调研结果转化为专业易懂的报告",
    backstory="你是一位专业的调研报告撰写专家，擅长将技术性的调研数据转化为清晰、有说服力的商业报告。",
    verbose=True,
    llm=llm
)

task1 = Task(
    description="调研智能家居产品在亚马逊跨境电商行业的整体状况，包括市场规模、主要参与者、增长趋势",
    agent=researcher,
    expected_output="详细的行业调研报告"
)

task2 = Task(
    description="对智能家居产品进行细分市场分析，包括目标客户群体、竞争对手、产品差异化机会",
    agent=researcher,
    expected_output="细分市场分析报告"
)

task3 = Task(
    description="制定智能家居产品的市场进入策略，包括产品选择、定价策略、物流方案、推广计划",
    agent=planner,
    expected_output="市场企划方案"
)

task4 = Task(
    description="运用技术工具进行智能家居产品深度调研，包括关键词分析、竞品监控、趋势预测",
    agent=tech_researcher,
    expected_output="技术调研报告"
)

task5 = Task(
    description="整合所有调研结果，撰写完整的智能家居产品市场调研报告",
    agent=report_writer,
    expected_output="完整调研报告"
)

crew = Crew(
    name="亚马逊智能家居产品调研团队",
    agents=[researcher, planner, tech_researcher, report_writer],
    tasks=[task1, task2, task3, task4, task5],
    process=Process.sequential,
    verbose=True,
    memory=False,
    cache=False
)

print("🚀 开始执行 Crew...")
result = crew.kickoff()
print("\n✅ 执行完成！")
print("=" * 50)
print(result)
