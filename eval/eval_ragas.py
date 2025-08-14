from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset
from retriever import HybridRetriever
from llm import generate_answer

EXAMPLES = [
    {"question":"Explain the auth flow with code.", "ground_truth":"Auth uses JWT via /login -> token -> Authorization: Bearer"},
]

def run_ragas(collection: str = "default", k: int = 5):
    retr = HybridRetriever(collection)
    rows = []
    for ex in EXAMPLES:
        ctx = retr.query(ex["question"], k=k)
        ans = generate_answer(ex["question"], ctx)
        rows.append({
            "question": ex["question"],
            "answer": ans,
            "contexts": [c.get("doc","") for c in ctx],
            "ground_truth": ex["ground_truth"],
        })
    ds = Dataset.from_list(rows)
    result = evaluate(ds, metrics=[faithfulness, answer_relevancy, context_precision])
    return result

if __name__ == "__main__":
    print(run_ragas().to_pandas())
