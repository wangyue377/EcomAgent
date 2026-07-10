"""意图路由器：分析用户消息，决定分发给哪个子 Agent。"""

from typing import List, Optional

from openai import OpenAI

from app.prompts.agents import ROUTER_PROMPT

VALID_AGENTS = {"presale", "postsale", "complaint"}
DEFAULT_AGENT = "postsale"


class Router:
    """使用 LLM 对用户意图分类，路由到对应的子 Agent。"""

    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    def route(self, user_input: str, history: Optional[List[dict]] = None) -> str:
        """返回子 Agent 标识: "presale" / "postsale" / "complaint"。

        先做关键词预检（快速匹配，不依赖 LLM），
        LLM 兜底（复杂/模糊场景）。
        """

        # ------ 关键词预检（按优先级：投诉 > 售后 > 售前）------
        text = user_input.strip().lower()

        # 1. 投诉关键词（最高优先级）
        complaint_kw = ["投诉", "赔偿", "举报", "差评"]
        if any(w in text for w in complaint_kw):
            return "complaint"

        # 2. 售后关键词（查询已有订单/物流/退款，优先级高于售前）
        postsale_kw = ["订单", "物流", "退款", "退货", "发货", "快递",
                       "签收", "运单", "还没到", "怎么还没", "到哪了",
                       "配送", "在途", "揽收", "派送", "物流信息"]
        if any(w in text for w in postsale_kw):
            return "postsale"

        # 3. 售前关键词（购买意图、商品推荐）
        presale_kw = ["想买", "想入手", "有推荐", "推荐一", "推荐几", "推荐个",
                      "推荐吗", "推荐一下", "多少钱", "性价比", "哪个好",
                      "怎么样", "有没有", "想看看", "有什么好", "能推荐",
                      "该选", "怎么选", "种草"]
        if any(w in text for w in presale_kw):
            return "presale"

        # ------ LLM 兜底（模糊/复杂场景） ------
        recent_context = ""
        if history:
            recent = [
                m for m in history[-4:]
                if m.get("role") in ("user", "assistant")
            ]
            if recent:
                lines = []
                for m in recent:
                    role = "用户" if m["role"] == "user" else "客服"
                    content = m.get("content", "")
                    if content and len(content) < 200:
                        lines.append(f"{role}: {content}")
                if lines:
                    recent_context = "\n最近对话：\n" + "\n".join(lines) + "\n"

        prompt = ROUTER_PROMPT.format(user_input=user_input)
        if recent_context:
            prompt = recent_context + "\n" + prompt

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=10,
        )

        raw = (response.choices[0].message.content or "").strip().lower()

        # 同时匹配英文标识和中文别名
        aliases = {
            "presale": ["presale", "售前", "商品", "推荐", "购买"],
            "postsale": ["postsale", "售后", "订单", "物流", "退款", "退货"],
            "complaint": ["complaint", "投诉", "赔偿", "不满"],
        }
        for agent_key, keywords in aliases.items():
            for kw in keywords:
                if kw in raw:
                    return agent_key

        return DEFAULT_AGENT
