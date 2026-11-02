import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import asdict, dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

GENRE_POINTS = 2.0
MOOD_POINTS = 1.0
ENERGY_POINTS = 1.5
ACOUSTIC_POINTS = 0.5


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the k songs with the highest score for the given user."""
        prefs = asdict(user)
        ranked = sorted(self.songs, key=lambda s: score_song(prefs, asdict(s))[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain in one line why a song scored the way it did for the user."""
        _, reasons = score_song(asdict(user), asdict(song))
        return "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Read the songs CSV into a list of dicts with numeric columns converted."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            row["tempo_bpm"] = int(row["tempo_bpm"])
            for key in ("energy", "valence", "danceability", "acousticness"):
                row[key] = float(row[key])
            songs.append(row)
    return songs


def _norm(value) -> str:
    """Lowercase and trim a label so 'Lofi ' matches 'lofi'."""
    return str(value or "").strip().lower()


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences, returning (score, reasons)."""
    score = 0.0
    reasons = []

    if _norm(song["genre"]) == _norm(user_prefs.get("favorite_genre")):
        score += GENRE_POINTS
        reasons.append(f"genre match (+{GENRE_POINTS:.1f})")

    if _norm(song["mood"]) == _norm(user_prefs.get("favorite_mood")):
        score += MOOD_POINTS
        reasons.append(f"mood match (+{MOOD_POINTS:.1f})")

    target = user_prefs.get("target_energy")
    if target is not None:
        energy_pts = ENERGY_POINTS * (1 - abs(song["energy"] - target))
        score += energy_pts
        reasons.append(f"energy {song['energy']:.2f} vs target {target:.2f} (+{energy_pts:.2f})")

    acoustic_fit = song["acousticness"] if user_prefs.get("likes_acoustic") else 1 - song["acousticness"]
    acoustic_pts = ACOUSTIC_POINTS * acoustic_fit
    score += acoustic_pts
    reasons.append(f"acousticness fit (+{acoustic_pts:.2f})")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top k as (song, score, explanation)."""
    if k <= 0:
        return []
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))
    return sorted(scored, key=lambda item: (-item[1], item[0].get("id", 0)))[:k]
