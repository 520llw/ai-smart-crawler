"""
AI爬虫Agent - 自主决策与执行
基于LangGraph的ReAct模式实现
"""

import asyncio
from typing import TypedDict, Annotated, Sequence
from dataclasses import dataclass
import operator

# 尝试导入LangGraph，如果没有则使用简化版
try:
    from langgraph.graph import StateGraph, END
    from langchain_openai import ChatOpenAI
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️ LangGraph未安装，将使用简化版Agent")

from ai_crawler import AICrawler, CrawlTask, CrawlResult, CrawlStrategy


class AgentState(TypedDict):
    """Agent状态定义"""
    messages: Annotated[Sequence, operator.add]
    current_url: str
    task_instruction: str
    crawl_results: list
    extracted_data: dict
    next_step: str
    completed: bool


@dataclass
class AgentTask:
    """Agent任务定义"""
    instruction: str  # 自然语言指令，如"搜索arxiv上关于脑肿瘤分割的论文"
    max_steps: int = 5
    require_structured: bool = True


class CrawlerAgent:
    """爬虫Agent - 自主执行复杂爬取任务"""
    
    def __init__(self, openai_api_key: str = None):
        self.crawler = AICrawler(openai_api_key)
        self.llm = None
        
        if LANGGRAPH_AVAILABLE and openai_api_key:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=openai_api_key
            )
            self.workflow = self._build_workflow()
        else:
            self.workflow = None
    
    def _build_workflow(self):
        """构建LangGraph工作流"""
        if not LANGGRAPH_AVAILABLE:
            return None
        
        workflow = StateGraph(AgentState)
        
        # 定义节点
        workflow.add_node("plan", self._plan_step)
        workflow.add_node("crawl", self._crawl_step)
        workflow.add_node("extract", self._extract_step)
        workflow.add_node("verify", self._verify_step)
        
        # 定义边
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "crawl")
        workflow.add_edge("crawl", "extract")
        workflow.add_conditional_edges(
            "extract",
            self._should_verify,
            {"verify": "verify", "end": END}
        )
        workflow.add_edge("verify", END)
        
        return workflow.compile()
    
    def _plan_step(self, state: AgentState) -> AgentState:
        """规划步骤 - 分析任务并制定计划"""
        instruction = state["task_instruction"]
        
        # 使用LLM分析指令，提取关键信息
        if self.llm:
            prompt = f"""
分析以下爬虫任务，提取关键信息：
任务: {instruction}

请分析：
1. 目标网站是什么？
2. 需要提取什么数据？
3. 需要几步完成？
4. 是否需要处理分页/动态内容？

以JSON格式返回：{{"target_site": "...", "data_to_extract": "...", "steps": [...]}}
"""
            response = self.llm.invoke(prompt)
            # 简化处理，实际应解析JSON
            state["messages"] = state.get("messages", []) + [{"role": "planner", "content": response.content}]
        
        state["next_step"] = "crawl"
        return state
    
    def _crawl_step(self, state: AgentState) -> AgentState:
        """执行爬取"""
        url = state["current_url"]
        
        # 异步执行爬取
        task = CrawlTask(url=url, strategy=CrawlStrategy.DYNAMIC)
        result = asyncio.run(self.crawler.crawl(task))
        
        state["crawl_results"] = state.get("crawl_results", []) + [result]
        state["next_step"] = "extract"
        return state
    
    def _extract_step(self, state: AgentState) -> AgentState:
        """数据提取"""
        instruction = state["task_instruction"]
        results = state.get("crawl_results", [])
        
        if not results:
            state["extracted_data"] = {}
            return state
        
        content = results[-1].markdown
        
        # 使用LLM提取结构化数据
        if self.llm:
            prompt = f"""
根据以下指令从网页内容中提取数据：
指令: {instruction}

网页内容:
{content[:3000]}  # 限制长度

请以JSON格式返回提取的数据。
"""
            response = self.llm.invoke(prompt)
            state["extracted_data"] = {"raw_extraction": response.content}
        else:
            state["extracted_data"] = {"content": content}
        
        state["next_step"] = "verify"
        return state
    
    def _verify_step(self, state: AgentState) -> AgentState:
        """验证结果"""
        data = state.get("extracted_data", {})
        
        # 简单验证
        if data and len(str(data)) > 10:
            state["completed"] = True
        else:
            state["completed"] = False
        
        return state
    
    def _should_verify(self, state: AgentState) -> str:
        """决策是否继续验证"""
        if state.get("completed"):
            return "end"
        return "verify"
    
    # ============ 简化版Agent（无LangGraph）============
    
    async def execute_simple(self, task: AgentTask) -> dict:
        """简化版执行 - 不依赖LangGraph"""
        print(f"🤖 Agent开始执行任务: {task.instruction}")
        
        # 步骤1: 解析指令，提取URL
        url = self._extract_url_from_instruction(task.instruction)
        if not url:
            return {"error": "无法从指令中提取URL"}
        
        print(f"📍 识别到目标URL: {url}")
        
        # 步骤2: 爬取页面
        crawl_task = CrawlTask(
            url=url,
            instruction=task.instruction if task.require_structured else ""
        )
        result = await self.crawler.crawl(crawl_task)
        
        if not result.success:
            return {"error": result.error}
        
        print(f"✅ 页面爬取成功，内容长度: {len(result.markdown)}")
        
        # 步骤3: 返回结果
        return {
            "success": True,
            "url": url,
            "content_preview": result.markdown[:500],
            "structured_data": result.structured_data,
            "metadata": result.metadata
        }
    
    def _extract_url_from_instruction(self, instruction: str) -> str:
        """从自然语言指令中提取URL"""
        import re
        
        # 匹配URL模式
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        match = re.search(url_pattern, instruction)
        
        if match:
            return match.group(0)
        
        # 常见网站映射
        site_mapping = {
            'arxiv': 'https://arxiv.org',
            'github': 'https://github.com',
            'google': 'https://www.google.com',
            'baidu': 'https://www.baidu.com',
        }
        
        for site, url in site_mapping.items():
            if site in instruction.lower():
                return url
        
        return None


async def agent_demo():
    """Agent演示"""
    print("\n" + "=" * 50)
    print("🤖 AI爬虫Agent演示")
    print("=" * 50)
    
    agent = CrawlerAgent()
    
    # 示例任务
    task = AgentTask(
        instruction="获取 https://example.com 的页面标题和主要内容",
        require_structured=True
    )
    
    result = await agent.execute_simple(task)
    
    print("\n📊 执行结果:")
    print(f"成功: {result.get('success')}")
    print(f"URL: {result.get('url')}")
    print(f"内容预览:\n{result.get('content_preview', '')[:300]}...")
    
    if result.get('structured_data'):
        print(f"\n结构化数据: {result['structured_data']}")


if __name__ == "__main__":
    asyncio.run(agent_demo())
