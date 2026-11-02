import csv
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import asdict, dataclass, field


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
    popularity: int = 50
    release_decade: int = 2020
    mood_tags: List[str] = field(default_factory=list)
    language: str = "en"
    is_instrumental: int = 0


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
    preferred_tags: Optional[List[str]] = None
    preferred_decade: Optional[int] = None
    target_popularity: Optional[int] = None
    preferred_language: Optional[str] = None
    prefers_instrumental: Optional[bool] = None


@dataclass(frozen=True)
class Weights:
    """Points each feature can earn. A scoring mode is just one of these."""
    genre: float = 2.0
    mood: float = 1.0
    energy: float = 1.5
    acoustic: float = 0.5
    tags: float = 0.5
    decade: float = 0.5
    popularity: float = 0.5
    language: float = 0.25
    instrumental: float = 0.25


# Strategy pattern: each mode is a Weights object; score_song takes one as a parameter.
MODES: Dict[str, Weights] = {
    "balanced": Weights(),
    "genre-first": Weights(genre=3.0, mood=0.5, energy=1.0),
    "mood-first": Weights(genre=1.0, mood=2.5, energy=1.0, tags=1.0),
    "energy-focused": Weights(genre=0.5, mood=0.5, energy=3.0),
}
DEFAULT_MODE = "balanced"

# Kept for backward compatibility and tests: the balanced-mode values.
GENRE_POINTS = MODES[DEFAULT_MODE].genre
MOOD_POINTS = MODES[DEFAULT_MODE].mood
ENERGY_POINTS = MODES[DEFAULT_MODE].energy
ACOUSTIC_POINTS = MODES[DEFAULT_MODE].acoustic

# Diversity re-ranking: points removed per already-chosen song that shares the attribute.
ARTIST_PENALTY = 1.0
GENRE_PENALTY = 0.5


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
    """Read the songs CSV into a list of dicts with numeric and list columns converted."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            row["tempo_bpm"] = int(row["tempo_bpm"])
            for key in ("energy", "valence", "danceability", "acousticness"):
                row[key] = float(row[key])
            if "popularity" in row:
                row["popularity"] = int(row["popularity"])
                row["release_decade"] = int(row["release_decade"])
                row["is_instrumental"] = int(row["is_instrumental"])
                row["mood_tags"] = [t for t in row["mood_tags"].split("|") if t]
            songs.append(row)
    return songs


def _norm(value) -> str:
    """Lowercase and trim a label so 'Lofi ' matches 'lofi'."""
    return str(value or "").strip().lower()


def get_weights(mode: Union[str, Weights]) -> Weights:
    """Look up a scoring mode by name, or pass a Weights object straight through."""
    if isinstance(mode, Weights):
        return mode
    try:
        return MODES[_norm(mode)]
    except KeyError:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {', '.join(MODES)}")


def score_song(user_prefs: Dict, song: Dict, mode: Union[str, Weights] = DEFAULT_MODE) -> Tuple[float, List[str]]:
    """Score one song against user preferences, returning (score, reasons)."""
    w = get_weights(mode)
    score = 0.0
    reasons = []

    if _norm(song["genre"]) == _norm(user_prefs.get("favorite_genre")):
        score += w.genre
        reasons.append(f"genre match (+{w.genre:.1f})")

    if _norm(song["mood"]) == _norm(user_prefs.get("favorite_mood")):
        score += w.mood
        reasons.append(f"mood match (+{w.mood:.1f})")

    target = user_prefs.get("target_energy")
    if target is not None:
        energy_pts = w.energy * (1 - abs(song["energy"] - target))
        score += energy_pts
        reasons.append(f"energy {song['energy']:.2f} vs target {target:.2f} (+{energy_pts:.2f})")

    acoustic_fit = song["acousticness"] if user_prefs.get("likes_acoustic") else 1 - song["acousticness"]
    acoustic_pts = w.acoustic * acoustic_fit
    score += acoustic_pts
    reasons.append(f"acousticness fit (+{acoustic_pts:.2f})")

    # Optional preferences: skipped entirely when the user does not set them.
    wanted_tags = {_norm(t) for t in user_prefs.get("preferred_tags") or []}
    if wanted_tags:
        have = {_norm(t) for t in song.get("mood_tags", [])}
        hits = sorted(wanted_tags & have)
        if hits:
            pts = w.tags * len(hits) / len(wanted_tags)
            score += pts
            reasons.append(f"mood tags {'+'.join(hits)} (+{pts:.2f})")

    decade = user_prefs.get("preferred_decade")
    if decade is not None and "release_decade" in song:
        pts = w.decade * max(0.0, 1 - abs(song["release_decade"] - decade) / 30)
        if pts > 0:
            score += pts
            reasons.append(f"{song['release_decade']}s vs preferred {decade}s (+{pts:.2f})")

    pop_target = user_prefs.get("target_popularity")
    if pop_target is not None and "popularity" in song:
        pts = w.popularity * (1 - abs(song["popularity"] - pop_target) / 100)
        score += pts
        reasons.append(f"popularity {song['popularity']} vs target {pop_target} (+{pts:.2f})")

    language = user_prefs.get("preferred_language")
    if language and _norm(song.get("language")) == _norm(language):
        score += w.language
        reasons.append(f"language match (+{w.language:.2f})")

    wants_instrumental = user_prefs.get("prefers_instrumental")
    if wants_instrumental is not None and "is_instrumental" in song:
        if bool(song["is_instrumental"]) == bool(wants_instrumental):
            score += w.instrumental
            reasons.append(f"instrumental preference match (+{w.instrumental:.2f})")

    return score, reasons


def _diverse_top_k(scored: List[Tuple[Dict, float, List[str]]], k: int) -> List[Tuple[Dict, float, str]]:
    """Greedy re-rank: each pick lowers the score of songs sharing its artist or genre."""
    remaining = list(scored)
    chosen: List[Tuple[Dict, float, str]] = []
    while remaining and len(chosen) < k:
        def adjusted(item):
            song, score, _ = item
            same_artist = sum(1 for c, _, _ in chosen if c["artist"] == song["artist"])
            same_genre = sum(1 for c, _, _ in chosen if c["genre"] == song["genre"])
            return score - ARTIST_PENALTY * same_artist - GENRE_PENALTY * same_genre, same_artist, same_genre

        best = min(remaining, key=lambda it: (-adjusted(it)[0], it[0].get("id", 0)))
        adj, same_artist, same_genre = adjusted(best)
        reasons = list(best[2])
        if same_artist:
            reasons.append(f"diversity penalty: artist already picked (-{ARTIST_PENALTY * same_artist:.1f})")
        if same_genre:
            reasons.append(f"diversity penalty: genre already picked (-{GENRE_PENALTY * same_genre:.1f})")
        chosen.append((best[0], adj, "; ".join(reasons)))
        remaining.remove(best)
    return chosen


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: Union[str, Weights] = DEFAULT_MODE,
    diversity: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top k as (song, score, explanation)."""
    if k <= 0:
        return []
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode)
        scored.append((song, score, reasons))
    if diversity:
        return _diverse_top_k(scored, k)
    scored.sort(key=lambda item: (-item[1], item[0].get("id", 0)))
    return [(song, score, "; ".join(reasons)) for song, score, reasons in scored[:k]]
