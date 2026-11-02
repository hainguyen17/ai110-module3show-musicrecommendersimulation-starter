"""
Command line runner for the Music Recommender Simulation.

Runs the recommender for several user profiles (typical and adversarial)
and prints the top results with the reasons behind each score.

Options:
    --mode {balanced,genre-first,mood-first,energy-focused}   scoring strategy
    --diversity                                               penalize repeated artists/genres
    --table                                                   print results as an ASCII table
    --profile NAME                                            run only profiles whose name contains NAME
"""

import argparse
import textwrap
from typing import List, Tuple

from src.recommender import MODES, DEFAULT_MODE, load_songs, recommend_songs


def profile(genre: str, mood: str, energy: float, acoustic: bool, **extras) -> dict:
    return {
        "favorite_genre": genre,
        "favorite_mood": mood,
        "target_energy": energy,
        "likes_acoustic": acoustic,
        **extras,
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
    # Uses the advanced song features (tags, decade, popularity, language, instrumental)
    "Nostalgic 2000s Folk (advanced)": profile(
        "folk", "peaceful", 0.4, True,
        preferred_tags=["nostalgic", "warm"], preferred_decade=2000,
        target_popularity=50, preferred_language="en", prefers_instrumental=False,
    ),
}


def show(name: str, user_prefs: dict, songs: list, k: int = 5, mode: str = DEFAULT_MODE, diversity: bool = False) -> None:
    print(f"=== {name} ===")
    print(f"prefs: {user_prefs}\n")
    for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k=k, mode=mode, diversity=diversity), start=1):
        print(f"{rank}. {song['title']} [{song['genre']}/{song['mood']}] - Score: {score:.2f}")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def format_table(results: List[Tuple[dict, float, str]], reason_width: int = 52) -> str:
    """Format recommendations as an ASCII table: rank, title, artist, genre/mood, score, reasons."""
    header = ["#", "Title", "Artist", "Genre/Mood", "Score", "Reasons"]
    rows = []
    for rank, (song, score, explanation) in enumerate(results, start=1):
        reasons = textwrap.wrap("; ".join(explanation.split("; ")), reason_width) or [""]
        rows.append([[str(rank)], [song["title"]], [song["artist"]], [f"{song['genre']}/{song['mood']}"], [f"{score:.2f}"], reasons])

    widths = [max(len(header[i]), *(len(line) for row in rows for line in row[i])) for i in range(len(header))]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def line(cells):
        return "| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths)) + " |"

    out = [sep, line(header), sep]
    for row in rows:
        for i in range(max(len(cell) for cell in row)):
            out.append(line([cell[i] if i < len(cell) else "" for cell in row]))
        out.append(sep)
    return "\n".join(out)


def show_table(name: str, user_prefs: dict, songs: list, k: int = 5, mode: str = DEFAULT_MODE, diversity: bool = False) -> None:
    print(f"=== {name} (mode: {mode}{', diversity on' if diversity else ''}) ===")
    print(format_table(recommend_songs(user_prefs, songs, k=k, mode=mode, diversity=diversity)))
    print()


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--mode", choices=list(MODES), default=DEFAULT_MODE, help="scoring strategy")
    parser.add_argument("--diversity", action="store_true", help="penalize repeated artists and genres")
    parser.add_argument("--table", action="store_true", help="print results as an ASCII table")
    parser.add_argument("--profile", help="run only profiles whose name contains this text")
    args = parser.parse_args(argv)

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")
    printer = show_table if args.table else show
    for name, prefs in PROFILES.items():
        if args.profile and args.profile.lower() not in name.lower():
            continue
        printer(name, prefs, songs, mode=args.mode, diversity=args.diversity)


if __name__ == "__main__":
    main()
