import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional, Dict, Any
import requests
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langgraph.graph import Graph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

app = FastAPI()

class RacePredictionRequest(BaseModel):
    date: date
    race_name: str

class RacePredictionAgent:
    def __init__(self):
        self.llm = OpenAI(temperature=0.7)
        self.search_tool = ToolNode(self.search_race_info)
        self.analyze_tool = ToolNode(self.analyze_race_info)
        self.workflow = self.create_workflow()

    def create_workflow(self) -> Graph:
        """LangGraphを使用してエージェントのワークフローを作成"""
        workflow = Graph()

        # ノードの定義
        workflow.add_node("generate_query", self.generate_search_query)
        workflow.add_node("search", self.search_tool)
        workflow.add_node("analyze", self.analyze_tool)
        workflow.add_node("evaluate", self.evaluate_results)

        # エッジの定義
        workflow.add_edge("generate_query", "search")
        workflow.add_edge("search", "analyze")
        workflow.add_edge("analyze", "evaluate")

        # 条件付きエッジ
        workflow.add_conditional_edges(
            "evaluate",
            self.decide_next_step,
            {
                "continue": "search",
                "complete": END
            }
        )

        # エントリーポイント
        workflow.set_entry_point("generate_query")
        return workflow.compile()

    def generate_search_query(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """検索クエリを生成"""
        prompt = PromptTemplate(
            input_variables=["date", "race_name"],
            template="""
            以下の情報から最適な検索クエリを生成してください：
            日付: {date}
            レース名: {race_name}
            
            検索クエリ:
            """
        )
        query = self.llm(prompt.format(
            date=state["date"],
            race_name=state["race_name"]
        ))
        return {"query": query.strip(), **state}

    def search_race_info(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """WEB検索を実行"""
        api_key = os.getenv("TAVILY_API_KEY")
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.get(f"https://api.tavily.com/search?q={state['query']}", headers=headers)
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Body: {response.text}")
        response.raise_for_status()
        results = response.json()
        
        snippets = [result["snippet"] for result in results.get("items", [])[:3]]
        
        return {"search_results": "\n".join(snippets), **state}

    def analyze_race_info(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """取得した情報を分析"""
        prompt = PromptTemplate(
            input_variables=["info"],
            template="""
            以下のレース情報を分析して、予想結果を生成してください。
            情報が不十分な場合は、その旨を記載してください。
            
            情報:
            {info}
            
            予想結果:
            """
        )
        analysis = self.llm(prompt.format(info=state["search_results"]))
        return {"analysis": analysis, **state}

    def evaluate_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """分析結果を評価し、次のアクションを決定"""
        prompt = PromptTemplate(
            input_variables=["analysis"],
            template="""
            以下の分析結果を評価し、追加の情報が必要かどうか判断してください。
            必要な場合は「continue」、不要な場合は「complete」と返答してください。
            
            分析結果:
            {analysis}
            
            判断:
            """
        )
        decision = self.llm(prompt.format(analysis=state["analysis"]))
        return {"decision": decision.strip().lower(), **state}

    def decide_next_step(self, state: Dict[str, Any]) -> str:
        """次のステップを決定"""
        return state["decision"]

    def predict(self, date: str, race_name: str) -> Dict[str, Any]:
        """予想を実行"""
        initial_state = {"date": date, "race_name": race_name}
        return self.workflow.invoke(initial_state)

@app.get("/healthcheck")
async def healthcheck():
    return {"message": "hello world"}

@app.post("/predict")
async def predict_race(race: RacePredictionRequest):
    try:
        agent = RacePredictionAgent()
        result = agent.predict(str(race.date), race.race_name)
        
        return {
            "date": str(race.date),
            "race_name": race.race_name,
            "prediction": result["analysis"],
            "search_queries": result.get("queries", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
