# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

**VibeMatch 1.0** is a content-based music recommender that runs in the terminal. You describe a listener with a favorite genre, a favorite mood, a target energy level, and a preference for acoustic sound. It scores all 18 songs in `data/songs.csv` and prints the top 5, with the reasons for each score (for example, "genre match (+2.0)"). I tested it with typical and adversarial profiles, ran a weight experiment, and wrote up the results in the [Model Card](model_card.md).

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

Terminal output of `python -m src.main`, which runs six profiles (three typical, three adversarial):

```
Loaded songs: 18

=== High-Energy Pop ===
prefs: {'favorite_genre': 'pop', 'favorite_mood': 'happy', 'target_energy': 0.9, 'likes_acoustic': False}

1. Sunrise City [pop/happy] - Score: 4.79
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.82 vs target 0.90 (+1.38)
     - acousticness fit (+0.41)
2. Gym Hero [pop/intense] - Score: 3.93
     - genre match (+2.0)
     - energy 0.93 vs target 0.90 (+1.46)
     - acousticness fit (+0.47)
3. Rooftop Lights [indie pop/happy] - Score: 2.62
     - mood match (+1.0)
     - energy 0.76 vs target 0.90 (+1.29)
     - acousticness fit (+0.33)
4. Storm Runner [rock/intense] - Score: 1.93
     - energy 0.91 vs target 0.90 (+1.48)
     - acousticness fit (+0.45)
5. Pulse Cathedral [edm/euphoric] - Score: 1.89
     - energy 0.96 vs target 0.90 (+1.41)
     - acousticness fit (+0.48)

=== Chill Lofi ===
prefs: {'favorite_genre': 'lofi', 'favorite_mood': 'chill', 'target_energy': 0.4, 'likes_acoustic': True}

1. Library Rain [lofi/chill] - Score: 4.85
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.35 vs target 0.40 (+1.42)
     - acousticness fit (+0.43)
2. Midnight Coding [lofi/chill] - Score: 4.82
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.42 vs target 0.40 (+1.47)
     - acousticness fit (+0.35)
3. Focus Flow [lofi/focused] - Score: 3.89
     - genre match (+2.0)
     - energy 0.40 vs target 0.40 (+1.50)
     - acousticness fit (+0.39)
4. Spacewalk Thoughts [ambient/chill] - Score: 2.78
     - mood match (+1.0)
     - energy 0.28 vs target 0.40 (+1.32)
     - acousticness fit (+0.46)
5. Coffee Shop Stories [jazz/relaxed] - Score: 1.90
     - energy 0.37 vs target 0.40 (+1.46)
     - acousticness fit (+0.45)

=== Deep Intense Rock ===
prefs: {'favorite_genre': 'rock', 'favorite_mood': 'intense', 'target_energy': 0.92, 'likes_acoustic': False}

1. Storm Runner [rock/intense] - Score: 4.93
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.91 vs target 0.92 (+1.48)
     - acousticness fit (+0.45)
2. Gym Hero [pop/intense] - Score: 2.96
     - mood match (+1.0)
     - energy 0.93 vs target 0.92 (+1.48)
     - acousticness fit (+0.47)
3. Pulse Cathedral [edm/euphoric] - Score: 1.92
     - energy 0.96 vs target 0.92 (+1.44)
     - acousticness fit (+0.48)
4. Iron Requiem [metal/angry] - Score: 1.90
     - energy 0.97 vs target 0.92 (+1.43)
     - acousticness fit (+0.47)
5. Sunrise City [pop/happy] - Score: 1.76
     - energy 0.82 vs target 0.92 (+1.35)
     - acousticness fit (+0.41)

=== Conflicting (sad but 0.9 energy) ===
prefs: {'favorite_genre': 'lofi', 'favorite_mood': 'sad', 'target_energy': 0.9, 'likes_acoustic': True}

1. Focus Flow [lofi/focused] - Score: 3.14
     - genre match (+2.0)
     - energy 0.40 vs target 0.90 (+0.75)
     - acousticness fit (+0.39)
2. Midnight Coding [lofi/chill] - Score: 3.14
     - genre match (+2.0)
     - energy 0.42 vs target 0.90 (+0.78)
     - acousticness fit (+0.35)
3. Library Rain [lofi/chill] - Score: 3.10
     - genre match (+2.0)
     - energy 0.35 vs target 0.90 (+0.67)
     - acousticness fit (+0.43)
4. Storm Runner [rock/intense] - Score: 1.53
     - energy 0.91 vs target 0.90 (+1.48)
     - acousticness fit (+0.05)
5. Gym Hero [pop/intense] - Score: 1.48
     - energy 0.93 vs target 0.90 (+1.46)
     - acousticness fit (+0.03)

=== Unknown genre (bossa nova) ===
prefs: {'favorite_genre': 'bossa nova', 'favorite_mood': 'relaxed', 'target_energy': 0.3, 'likes_acoustic': True}

1. Coffee Shop Stories [jazz/relaxed] - Score: 2.84
     - mood match (+1.0)
     - energy 0.37 vs target 0.30 (+1.40)
     - acousticness fit (+0.45)
2. Pine Hollow [folk/peaceful] - Score: 1.96
     - energy 0.30 vs target 0.30 (+1.50)
     - acousticness fit (+0.46)
3. Spacewalk Thoughts [ambient/chill] - Score: 1.93
     - energy 0.28 vs target 0.30 (+1.47)
     - acousticness fit (+0.46)
4. Moonlit Sonata [classical/melancholy] - Score: 1.85
     - energy 0.22 vs target 0.30 (+1.38)
     - acousticness fit (+0.47)
5. Library Rain [lofi/chill] - Score: 1.85
     - energy 0.35 vs target 0.30 (+1.42)
     - acousticness fit (+0.43)

=== Dead-center (everything 0.5) ===
prefs: {'favorite_genre': 'pop', 'favorite_mood': 'chill', 'target_energy': 0.5, 'likes_acoustic': False}

1. Sunrise City [pop/happy] - Score: 3.43
     - genre match (+2.0)
     - energy 0.82 vs target 0.50 (+1.02)
     - acousticness fit (+0.41)
2. Gym Hero [pop/intense] - Score: 3.33
     - genre match (+2.0)
     - energy 0.93 vs target 0.50 (+0.85)
     - acousticness fit (+0.47)
3. Midnight Coding [lofi/chill] - Score: 2.52
     - mood match (+1.0)
     - energy 0.42 vs target 0.50 (+1.38)
     - acousticness fit (+0.15)
4. Library Rain [lofi/chill] - Score: 2.34
     - mood match (+1.0)
     - energy 0.35 vs target 0.50 (+1.27)
     - acousticness fit (+0.07)
5. Spacewalk Thoughts [ambient/chill] - Score: 2.21
     - mood match (+1.0)
     - energy 0.28 vs target 0.50 (+1.17)
     - acousticness fit (+0.04)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

**Weight shift: energy x2, genre /2** (genre 2.0 to 1.0, energy 1.5 to 3.0; the max score becomes 5.5 and the math stays valid).

- The conflicting profile (lofi, energy 0.9) went from three quiet lofi songs on top to *Storm Runner* and *Gym Hero*, which fit the high energy it asked for.
- In the dead-center profile (energy 0.5), *Gym Hero* dropped out of the top 5.
- Typical profiles barely changed. The hand-labelled grader's average rose from 98.0 to 98.4.
- Verdict: more accurate, not just different. I kept the original weights in the code.

**Related genres and moods get half credit.** Two tries: broad groups scored 92.6 (down from 98.0), and narrow near-synonym pairs scored 97.7. Both were worse, so I reverted.

**Different users.** Six profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock, Conflicting, Unknown genre, Dead-center) gave sensible, different lists. Pair-by-pair comparisons are in the [Model Card](model_card.md).

---

## Limitations and Risks

- **Genre counts too much.** It is 2 of 5 points, so *Gym Hero* (pop, intense) ranks second for happy pop fans, ahead of the truly happy *Rooftop Lights* (indie pop).
- **Labels match by exact word.** "Indie pop" gets no credit for "pop", and a mood like "sad" that is not in the catalog is ignored.
- **Tiny catalog.** 18 songs, with one to three per genre, so the first slots are mostly decided by genre.
- **No lyrics, language, or listening history.** It cannot learn from skips or replays, so it can keep repeating the same kind of song.

More detail is in the [Model Card](model_card.md).

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Passing tests did not mean good recommendations. My code passed every test while *Gym Hero* kept appearing for happy pop fans, because one rule (genre = 2 points) quietly outweighed what listeners said they wanted. Recommenders turn labels and numbers into a ranking, so whatever the scoring rewards most becomes the system's taste.

Bias can show up in simple places: a catalog with few songs per genre, exact-word label matches that give no credit to "indie pop" for a pop fan, and a profile that ignores a mood it has never seen. See the [Model Card](model_card.md) for the full reflection.
