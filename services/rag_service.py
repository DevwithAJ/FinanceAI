from __future__ import annotations

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DEFAULT_KNOWLEDGE = [
    {"topic": "50/30/20 budgeting", "text": "A common budgeting framework allocates about 50% of take-home income to needs, 30% to wants, and 20% to savings and debt reduction. It is a flexible starting point, not a mandatory rule."},
    {"topic": "emergency fund", "text": "Emergency savings can be built in stages: first a small buffer, then roughly one month of essential costs, then gradually toward several months depending on job stability, dependents and risk."},
    {"topic": "debt", "text": "Debt reduction usually starts with keeping all minimum payments current, avoiding new high-cost debt, and directing extra cash either to the highest interest debt or the smallest balance for motivation."},
    {"topic": "credit score", "text": "Healthy credit habits include paying on time, using only a modest portion of available revolving credit, limiting unnecessary applications, and reviewing credit reports for errors."},
    {"topic": "investing", "text": "Before taking more investment risk, many people prioritize near-term expenses, expensive debt and emergency savings. Investments should match time horizon, liquidity needs and risk tolerance."},
    {"topic": "forecast", "text": "FinanceAI transaction forecasts estimate future income, expenses and savings from recorded monthly patterns. Short histories are less reliable and unexpected events can make forecasts inaccurate."},
    {"topic": "anomaly detection", "text": "Anomaly detection flags transactions that look unusual compared with the user's own history. A flag is a review prompt, not proof of fraud or wrongdoing."},
    {"topic": "loan risk", "text": "FinanceAI loan risk is an experimental historical model output. It is not a lending decision, approval recommendation, interest-rate recommendation, or substitute for regulated underwriting."},
    {"topic": "credit stress", "text": "The FinanceAI credit-stress model is an experimental financial-stress proxy. It does not represent an official credit bureau score or a probability of default."},
    {"topic": "goals", "text": "A savings goal becomes easier to act on when it has a target amount, current amount and target date. The remaining amount divided by the months left gives a useful monthly contribution target."},
    {"topic": "net worth", "text": "Net worth is total assets and investments minus liabilities. Tracking it over time can show long-term financial direction even when month-to-month cash flow varies."},
]

# Extra retrieval words make the offline assistant usable for common Hindi/Hinglish
# phrasing without pretending to be a translation model.
TOPIC_ALIASES = {
    "50/30/20 budgeting": "budget bajat kharcha kharch planning monthly plan zarurat needs wants bachat savings",
    "emergency fund": "emergency fund bachat backup paisa safety buffer आपातकालीन फंड बचत",
    "debt": "debt loan karz udhar emi repayment कर्ज ऋण",
    "credit score": "credit score cibil utilization payment history क्रेडिट स्कोर सिबिल",
    "investing": "investment invest nivesh sip mutual fund निवेश एसआईपी",
    "forecast": "forecast future agla month 30 60 90 din bhavishya अनुमान भविष्य",
    "anomaly detection": "anomaly unusual spending unusual transaction fraud alert ajeeb kharcha असामान्य खर्च",
    "loan risk": "loan risk repayment risk loan profile ऋण जोखिम",
    "credit stress": "credit stress financial stress pressure तनाव वित्तीय दबाव",
    "goals": "goal lakshya target saving plan bike laptop education लक्ष्य बचत",
    "net worth": "net worth assets liabilities sampatti karz कुल संपत्ति",
}


class LocalRAG:
    def __init__(self, root):
        self.root = Path(root)
        knowledge_file = self.root / "knowledge" / "finance_knowledge.json"
        if knowledge_file.exists():
            try:
                loaded = json.loads(knowledge_file.read_text(encoding="utf-8"))
                self.docs = loaded if isinstance(loaded, list) and loaded else DEFAULT_KNOWLEDGE
            except Exception:
                self.docs = DEFAULT_KNOWLEDGE
        else:
            self.docs = DEFAULT_KNOWLEDGE

        texts = []
        for doc in self.docs:
            topic = str(doc.get("topic", ""))
            text = str(doc.get("text", ""))
            aliases = TOPIC_ALIASES.get(topic.lower(), TOPIC_ALIASES.get(topic, ""))
            texts.append(f"{topic} {text} {aliases}")

        self.vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(texts)

    def retrieve(self, query, top_k=3):
        query = (query or "finance").strip()
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix)[0]
        order = scores.argsort()[::-1][: max(1, int(top_k))]
        return [
            {**self.docs[int(i)], "similarity": round(float(scores[int(i)]), 4)}
            for i in order
            if scores[int(i)] > 0
        ]

    def answer(self, query, context=None):
        hits = self.retrieve(query, 3)
        context = context or {}
        lines: list[str] = []

        month = context.get("month")
        if month:
            lines.append(
                "Current-month account snapshot: "
                f"income ₹{float(month.get('income', 0) or 0):,.0f}, "
                f"expenses ₹{float(month.get('expense', 0) or 0):,.0f}, "
                f"balance ₹{float(month.get('balance', 0) or 0):,.0f}, "
                f"savings rate {float(month.get('savings_rate', 0) or 0):.1f}%."
            )

        if context.get("health_score") is not None:
            level = context.get("health_level") or "not labeled"
            lines.append(
                f"Latest FinanceAI health score: {float(context['health_score']):.0f}/100 ({level})."
            )

        if context.get("net_worth") is not None:
            lines.append(f"Tracked net worth: ₹{float(context['net_worth'] or 0):,.0f}.")

        if context.get("active_goals") is not None:
            lines.append(f"Active financial goals: {int(context['active_goals'] or 0)}.")

        categories = context.get("top_expense_categories") or []
        if categories:
            category_text = ", ".join(
                f"{row.get('category', 'Other')} ₹{float(row.get('total', 0) or 0):,.0f}"
                for row in categories[:5]
            )
            lines.append(f"Top current-month expense categories: {category_text}.")

        credit = context.get("credit_stress")
        if credit and credit.get("score") is not None:
            lines.append(
                f"Latest Credit Stress research signal: {float(credit['score']) * 100:.1f}/100 "
                f"({credit.get('label') or 'saved result'})."
            )

        loan = context.get("loan_risk")
        if loan and loan.get("score") is not None:
            lines.append(
                f"Latest Loan Risk research signal: {float(loan['score']) * 100:.1f}/100 "
                f"({loan.get('label') or 'saved result'})."
            )

        if hits:
            lines.append("Relevant FinanceAI knowledge: " + " ".join(str(h.get("text", "")) for h in hits[:2]))
        else:
            lines.append(
                "FinanceAI can explain budgets, savings, debt, goals, forecasts, anomalies, net worth, "
                "Credit Stress and the experimental Loan Risk model."
            )

        lines.append(
            "Use this as educational guidance and verify important financial decisions with appropriate official or professional sources."
        )
        return "\n\n".join(lines), hits
