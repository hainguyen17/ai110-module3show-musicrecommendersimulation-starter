# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

### How real-world recommenders work

Platforms like Spotify and YouTube combine two main approaches. **Collaborative filtering** predicts what you'll like from the behavior of other users: if people who liked and skipped the same songs as you also loved a track you haven't heard, it gets recommended. It needs no knowledge of the music itself, but it needs lots of users and struggles with brand-new songs (the "cold start" problem). **Content-based filtering** looks at the attributes of the songs you already like (tempo, energy, mood, genre, acousticness) and finds other songs with similar attributes. It works for new songs and a single user, but it can trap you in a bubble of "more of the same."

The data behind these systems falls into two groups:

- **Behavioral signals:** likes, skips, replays, playlist adds, listening time, search history
- **Song attributes:** genre, mood, tempo, energy, valence, danceability, acousticness (and, in production, audio embeddings and lyrics)

My version is **purely content-based**. A simulator with ten songs and one user has no crowd to learn from, so it prioritizes how closely a song's *vibe* matches the user's stated taste. Mood and genre set the overall feel, and energy fine-tunes it.

### Features

**`Song`** (from `data/songs.csv`): `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`. The score uses `genre`, `mood`, `energy`, and `acousticness`. The rest are kept for display and later experiments.

**`UserProfile`**: `favorite_genre`, `favorite_mood`, `target_energy` (0.0 to 1.0), `likes_acoustic` (bool).

### Algorithm Recipe

**Scoring Rule** (one song vs. the user, max 5.0 points):

| Component | Rule | Points |
|---|---|---|
| Genre | exact match with `favorite_genre` | +2.0 |
| Mood | exact match with `favorite_mood` | +1.0 |
| Energy | `1 - abs(song.energy - target_energy)` | 0 to 1.5 (scaled) |
| Acousticness | `song.acousticness` if `likes_acoustic`, else `1 - song.acousticness` | 0 to 0.5 (scaled) |

Energy is scored by **closeness**, not magnitude. A user who wants 0.4 energy should not prefer a 0.9 song just because it is higher, so the reward shrinks the further the song is from the target in either direction.

Genre is weighted above mood because it is a stronger, more stable signal of taste: someone who likes lofi rarely wants metal, even when the moods match. Mood is more situational and can shift from day to day. These weights are a starting guess and will be tested in the experiments below.

**Ranking Rule** (all songs): score every song in the catalog, sort by score descending, and return the top `k`. The Scoring Rule judges a single song in isolation and produces a number. It cannot say which songs to recommend. The Ranking Rule uses those numbers to compare the whole catalog and pick the best few. A recommender needs both: scoring makes songs comparable, and ranking turns the comparison into a list.

### Dataset

`data/songs.csv` now has 18 songs. I added 8 songs covering genres and moods missing from the starter set: hip hop (confident), r&b (romantic), country (nostalgic), classical (melancholy), edm (euphoric), metal (angry), reggae (uplifting), and folk (peaceful). The existing numeric columns (`energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`) are unchanged.

### Taste profile

```python
user_prefs = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.40,
    "likes_acoustic": True,
}
```

This profile separates "chill lofi" from "intense rock" well. Hand-scoring it, *Library Rain* (lofi, chill, energy 0.35, acousticness 0.86) gets about 4.9 of 5.0, while *Storm Runner* (rock, intense, energy 0.91, acousticness 0.10) gets about 0.8, because it matches on nothing but a little energy proximity. The profile is narrow in one way: only three songs are lofi, so the top 3 will be mostly lofi and the rest of the list is decided by energy and acousticness alone. To check the opposite end, I will also test a second profile (`rock`, `intense`, energy 0.90, `likes_acoustic=False`) and a "conflicting" one (e.g. `lofi` with energy 0.95).

### Data flow

```
INPUT                     PROCESS (loop over every row)                 OUTPUT
user_prefs  ──►  for song in songs.csv:                      ──►  sort by score, descending
                   score = genre (+2.0)                            take top K
                         + mood  (+1.0)                            show title, score, and reasons
                         + energy closeness (up to 1.5)
                         + acousticness fit (up to 0.5)
                   keep (song, score, reasons)
```

### Expected biases

- **Genre dominates.** A +2.0 genre match is 40% of the maximum score, so a song with a perfect mood and energy match in a different genre (e.g. *Midnight Coding*-style vibes labeled "ambient") can lose to a poor same-genre song.
- **Exact-match labels are all-or-nothing.** "chill" vs. "relaxed" or "pop" vs. "indie pop" score 0 even though a listener would call them close.
- **Tiny, uneven catalog.** Most genres have one song, so users who like lofi get more variety than users who like jazz or metal.
- **No behavior data.** The system can't learn from skips or replays, so it never discovers that a user's taste differs from what they stated, and it will keep recommending the same kind of song (a filter bubble).

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Default profile: `pop` / `happy` / energy 0.8 / not acoustic (`python -m src.main`):

```
Loaded songs: 18

Top recommendations:

1. Sunrise City by Neon Echo - Score: 4.88
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.82 vs target 0.80 (+1.47)
     - acousticness fit (+0.41)

2. Gym Hero by Max Pulse - Score: 3.78
     - genre match (+2.0)
     - energy 0.93 vs target 0.80 (+1.30)
     - acousticness fit (+0.47)

3. Rooftop Lights by Indigo Parade - Score: 2.77
     - mood match (+1.0)
     - energy 0.76 vs target 0.80 (+1.44)
     - acousticness fit (+0.33)

4. Concrete Crown by Verse Valley - Score: 1.91
     - energy 0.78 vs target 0.80 (+1.47)
     - acousticness fit (+0.44)

5. Night Drive Loop by Neon Echo - Score: 1.81
     - energy 0.75 vs target 0.80 (+1.42)
     - acousticness fit (+0.39)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



