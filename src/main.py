"""
Command line runner for the Music Recommender Simulation.

Runs the recommender for several user profiles (typical and adversarial)
and prints the top results with the reasons behind each score.
"""

from src.recommender import load_songs, recommend_songs


def profile(genre: str, mood: str, energy: float, acoustic: bool) -> dict:
    return {
        "favorite_genre": genre,
        "favorite_mood": mood,
        "target_energy": energy,
        "likes_acoustic": acoustic,
    }


PROFILES = {
    # Typical listeners
    "High-Energy Pop": profile("pop", "happy", 0.9, False),
    "Chill Lofi": profile("lofi", "chill", 0.4, True),
    "Deep Intense Rock": profile("rock", "intense", 0.92, False),
    # Adversarial / edge cases
    "Conflicting (sad but 0.9 energy)": profile("lofi", "sad", 0.9, True),
    "Unknown genre (bossa nova)": profile("bossa nova", "relaxed", 0.3, True),
    "Dead-center (everything 0.5)": profile("pop", "chill", 0.5, False),
}


def show(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    print(f"=== {name} ===")
    print(f"prefs: {user_prefs}\n")
    for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k=k), start=1):
        print(f"{rank}. {song['title']} [{song['genre']}/{song['mood']}] - Score: {score:.2f}")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")
    for name, prefs in PROFILES.items():
        show(name, prefs, songs)


if __name__ == "__main__":
    main()
