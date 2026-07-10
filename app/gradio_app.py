"""Gradio 聊天界面：为 EcomAgent 提供 Web UI。

启动方式：
  python app/gradio_app.py

默认访问 http://127.0.0.1:7860
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import gradio as gr
from app.agent.chat import EcomAgent

# 全局单例 Agent
_agent: EcomAgent | None = None

INTENT_LABELS = {
    "order_query": "📦 订单查询",
    "return_request": "↩️ 退换货",
    "product_consult": "🔍 商品咨询",
    "complaint": "⚠️ 投诉",
    "after_sale": "🔧 售后服务",
    "promotion": "🎉 优惠活动",
    "account": "👤 账户问题",
    "greeting": "💬 打招呼",
    "other": "其他",
}


def get_agent() -> EcomAgent:
    global _agent
    if _agent is None:
        _agent = EcomAgent()
    return _agent


def respond(message: str, history: list):
    """Gradio 聊天回调：输入消息 → 返回回复。"""
    agent = get_agent()
    result = agent.chat(message)

    intent_label = INTENT_LABELS.get(result.intent.value, result.intent.value)
    meta = (
        f"*意图: {intent_label} | 置信度: {result.confidence:.0%}*"
        + (" | ⚠️ 建议转人工" if result.requires_human else "")
    )

    reply = result.reply
    if result.follow_up_question:
        reply += f"\n\n❓ {result.follow_up_question}"

    return f"{reply}\n\n——\n{meta}"


# ---------- Gradio UI ----------

with gr.Blocks(
    title="并夕夕 · 智能客服 小夕",
    fill_height=True,
) as demo:
    gr.Markdown(
        """
    # 🛍️ 并夕夕 · 智能客服「小夕」

    支持工具调用 + 政策检索 + 用户记忆 + 技能编排
    """
    )

    chatbot = gr.ChatInterface(
        fn=respond,
        title="",
        description="",
    )

    gr.Markdown(
        """
    **💡 对话示例：**
    - 📦 `帮我查一下 ORD-20240115-001`
    - 🚚 `ORD-20240115-001 的物流到哪了`
    - 🔍 `有没有 Nike 运动鞋`
    - ↩️ `我要退款 ORD-20240120-002`
    - 📖 `退换货几天内有效`
    """
    )


if __name__ == "__main__":
    import atexit

    @atexit.register
    def cleanup():
        global _agent
        if _agent is not None:
            _agent.save()
            _agent.close()
            _agent = None

    demo.launch(server_name="127.0.0.1", server_port=7860, theme=gr.themes.Soft())
