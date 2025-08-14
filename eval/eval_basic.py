import time, json, statistics
from retriever import HybridRetriever

TESTS = [
    {"q": "Where is the HTTP client initialized?", "expect": ["client", "http", "init"]},
    {"q": "How to configure database URL?", "expect": ["DATABASE_URL", "env", "config"]},
]

def run(collection: str = "default", k: int = 5):
    retr = HybridRetriever(collection)
    latencies = []
    hits_at_1 = 0
    for t in TESTS:
        t0 = time.time()
        res = retr.query(t["q"], k=k)
        lat = time.time()-t0
        latencies.append(lat)
        text = "\n".join([r.get("doc","") for r in res])
        if any(any(w.lower() in text.lower() for w in t["expect"])):
            hits_at_1 += 1
    return {
        "avg_latency": statistics.mean(latencies) if latencies else None,
        "hits@1_proxy": hits_at_1/len(TESTS)
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
