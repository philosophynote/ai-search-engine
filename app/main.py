from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from langgraph.graph import StateGraph, END
from app.state import AgentState
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from app.steps import steps_node
from app.search import search_node
from app.summarize import summarize_node
from app.extract import extract_node

def route(state):
    """
    ルーティング関数: 次に実行するノードを決定する
    """
    if not state.get("steps"):
        return END
    current_step = next(
        (step for step in state["steps"] if step["status"] == "pending"), None
    )
    if not current_step:
        return "summarize_node"
    if current_step["type"] == "search":
        return "search_node"
    raise ValueError(f"Unknown step type: {current_step['type']}")


# グラフの初期化およびノードの登録
workflow = StateGraph(AgentState)
workflow.add_node("steps_node", steps_node)
workflow.add_node("search_node", search_node)
workflow.add_node("summarize_node", summarize_node)
workflow.add_node("extract_node", extract_node)
workflow.set_entry_point("steps_node")
workflow.add_conditional_edges(
    "steps_node", route, ["summarize_node", "search_node", END]
)
workflow.add_edge("search_node", "extract_node")
workflow.add_conditional_edges("extract_node", route, ["summarize_node", "search_node"])
workflow.add_edge("summarize_node", END)

# チェックポイント（Persistence）用 MemorySaver の生成とグラフのコンパイル
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# FastAPI アプリケーションの定義
app = FastAPI()


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


@app.post("/search", response_model=QueryResponse)
async def search(request: QueryRequest):
    # AgentState（初期状態）を生成
    initial_state = AgentState(
        messages=[HumanMessage(content=request.question)],
        steps=[],  # 初回は空リスト
        answer=None,
        model="openai",  # 使用するモデルを指定
    )
    # チェックポイント用の設定（新規実行の場合は空文字列）
    config = {
        "configurable": {"thread_id": "1", "checkpoint_ns": "", "checkpoint_id": ""}
    }
    try:
        # グラフを非同期で実行
        final_state = await graph.ainvoke(initial_state, config=config)
        print(final_state)
        try:
            answer = final_state["steps"][-1]["result"]
        except (KeyError, IndexError):
            answer = "回答が生成されませんでした。"
        return QueryResponse(answer=answer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
