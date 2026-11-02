"""Quality grader: NDCG@5 against hand-labelled relevance (2=great, 1=ok, 0=bad).
Run: python -m tests.eval_quality   (labels are the author's judgment, not ground truth)"""
import math
from src.recommender import load_songs, recommend_songs

def P(g, m, e, a): return {"favorite_genre": g, "favorite_mood": m, "target_energy": e, "likes_acoustic": a}

PROFILES = {
    "pop/happy":        (P("pop", "happy", 0.8, False),   {"Sunrise City": 2, "Rooftop Lights": 2, "Gym Hero": 1, "Concrete Crown": 1}),
    "lofi/chill":       (P("lofi", "chill", 0.4, True),   {"Library Rain": 2, "Midnight Coding": 2, "Focus Flow": 2, "Spacewalk Thoughts": 1, "Coffee Shop Stories": 1, "Pine Hollow": 1}),
    "rock/intense":     (P("rock", "intense", 0.92, False), {"Storm Runner": 2, "Gym Hero": 1, "Iron Requiem": 1, "Pulse Cathedral": 1}),
    "jazz/relaxed":     (P("jazz", "relaxed", 0.35, True), {"Coffee Shop Stories": 2, "Library Rain": 1, "Spacewalk Thoughts": 1, "Pine Hollow": 1, "Moonlit Sonata": 1}),
    "metal/angry":      (P("metal", "angry", 0.97, False), {"Iron Requiem": 2, "Storm Runner": 1, "Gym Hero": 1, "Pulse Cathedral": 1}),
    "synthwave/moody":  (P("synthwave", "moody", 0.75, False), {"Night Drive Loop": 2, "Concrete Crown": 1, "Rooftop Lights": 1, "Storm Runner": 1}),
    "MESSY Lofi/Chill": (P(" Lofi", "CHILL ", 0.4, True), {"Library Rain": 2, "Midnight Coding": 2, "Focus Flow": 2, "Spacewalk Thoughts": 1, "Coffee Shop Stories": 1, "Pine Hollow": 1}),
}

def ndcg(titles, rel, k=5):
    dcg = sum(rel.get(t, 0) / math.log2(i + 2) for i, t in enumerate(titles[:k]))
    ideal = sorted(rel.values(), reverse=True)[:k]
    return dcg / sum(r / math.log2(i + 2) for i, r in enumerate(ideal))

def grade(verbose=True):
    songs, results = load_songs("data/songs.csv"), {}
    for name, (prefs, rel) in PROFILES.items():
        try:
            titles = [s["title"] for s, _, _ in recommend_songs(prefs, songs, k=5)]
            results[name] = ndcg(titles, rel)
            if verbose: print(f"  {name:18s} {results[name]*100:5.1f}  {titles}")
        except Exception as e:
            results[name] = 0.0
            if verbose: print(f"  {name:18s}   0.0  CRASH {type(e).__name__}: {e}")
    avg = sum(results.values()) / len(results) * 100
    print(f"  AVERAGE NDCG@5: {avg:.1f}")
    return avg

if __name__ == "__main__":
    grade()
