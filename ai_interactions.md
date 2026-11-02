# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

Stretch features attempted: Challenge 1 (advanced song features), Challenge 2 (scoring modes), Challenge 3 (diversity penalty), Challenge 4 (summary table). Work was done on the `experiment/advanced-features` branch.

---

## Agentic Workflow (SF8): Challenge 1, Advanced Song Features

**What task did you give the agent?**

Add 5 or more new song attributes to `data/songs.csv`, update the scoring logic in `src/recommender.py` to use them, and keep the existing profiles and tests working.

**Prompts used:**

- "Introduce 5 or more complex attributes to your dataset that are not currently present in the baseline data, such as Song Popularity (0-100), Release Decade, or Detailed Mood Tags. Update both data/songs.csv and the scoring logic in src/recommender.py so scoring accounts for the new attributes."
- Follow-up constraint chosen during the work: new preferences must be optional, so profiles that do not set them score exactly as before.

**What did the agent generate or change?**

- `data/songs.csv`: five new columns for all 18 songs: `popularity` (0-100), `release_decade`, `mood_tags` (pipe-separated, e.g. `nostalgic|warm`), `language`, `is_instrumental` (0/1). The values are invented estimates.
- `src/recommender.py`:
  - `load_songs` converts the new columns (ints, and a list for tags).
  - `Song` and `UserProfile` got the new fields with defaults, so the starter tests still construct them.
  - `score_song` adds optional points: tag overlap (up to 0.5, in proportion to how many wanted tags match), decade closeness (up to 0.5, reaching zero at 30 years apart), popularity closeness (up to 0.5), language match (+0.25), and instrumental match (+0.25). Each has a reason string.
- `src/main.py`: a seventh profile, "Nostalgic 2000s Folk (advanced)", that sets all five new preferences.
- `tests/test_advanced_features.py`: 7 tests for these features.

**What did you verify or fix manually?**

- Checked the first six profiles' terminal output is byte-for-byte identical to the saved output from before the change, and that the original 27 tests and the NDCG grader (98.0) were unchanged.
- Read the advanced profile's reasons by hand. Example: *Pine Hollow* gets tags +0.25 (only "nostalgic" of the two wanted tags), decade +0.33 (2010s vs 2000s), popularity +0.49 (48 vs 50). That matches the formulas.
- One test I first wrote was wrong, not the code: the "other artist" song in the diversity test was too weak to ever beat a repeated artist, so the test failed. I fixed the test data.
- Still to check yourself: whether the made-up tags, decades and popularity values feel right to you.

---

## Design Pattern (SF10): Challenge 2, Multiple Scoring Modes

**Which design pattern did you use?**

A simple **Strategy pattern**. The "strategy" is a frozen `Weights` dataclass (points for genre, mood, energy, acousticness, and the optional features). A scoring mode is one `Weights` object, and `score_song` takes the mode as a parameter.

**How did AI help you brainstorm or implement it?**

- Prompt: "Build two or more different ranking strategies (e.g., Genre-First, Mood-First, Energy-Focused) so a user can switch modes in main.py, using a simple Strategy pattern that keeps the code modular."
- The AI compared two designs: (a) a class per mode with its own `score` method, and (b) one scoring function that takes a weights object. I went with (b) because the modes differ only in numbers, not in logic, so classes would add code without adding flexibility. A new mode is one line in `MODES`.
- The AI wrote the implementation and the four modes: `balanced` (the original weights), `genre-first`, `mood-first`, `energy-focused`.

**How does the pattern appear in your final code?**

- `Weights` and the `MODES` dictionary in `src/recommender.py`.
- `get_weights(mode)` accepts a mode name or a `Weights` object, and raises a clear error for unknown names.
- `score_song(..., mode=...)` and `recommend_songs(..., mode=...)`.
- `main.py --mode {balanced,genre-first,mood-first,energy-focused}`.
- Checked on real data: for the "Conflicting" profile (lofi, energy 0.9), `energy-focused` puts *Storm Runner* and *Gym Hero* first, while the other modes put quiet lofi songs first. 8 tests cover the modes.

---

## Challenge 3: Diversity Penalty

**Prompt used:** "Implement a Diversity Penalty that prevents the recommender from suggesting too many songs from the same artist or genre. Penalize a song's score if its artist is already present in the top recommendations list."

**What the AI generated:** `_diverse_top_k` in `src/recommender.py`, a greedy re-rank. It picks the best song, then lowers the score of each remaining song by 1.0 per already-chosen song with the same artist and 0.5 per same genre, and repeats. The penalty appears in the reasons (for example, "diversity penalty: artist already picked (-1.0)"). It is off by default (`diversity=False`, CLI `--diversity`).

**Verification:** For "Chill Lofi", *Focus Flow* (same artist and genre as songs already picked) drops from third to fifth, and *Spacewalk Thoughts* and *Coffee Shop Stories* move up. 5 tests cover this.

**Trade-off to note:** The penalty sizes (1.0 and 0.5) are my guesses. A penalty that is too large would push out a truly great second song from the same artist.

---

## Challenge 4: Visual Summary Table

**Prompt used:** "Suggest a way to use a library like tabulate or simple ASCII formatting to display the top recommendations. The table must include the reasons for each score."

**What the AI generated:** `format_table` in `src/main.py`, plain ASCII with no new dependency (the project does not list `tabulate` in `requirements.txt`). Columns: rank, title, artist, genre/mood, score, reasons. Long reasons wrap onto extra lines inside the cell. Run with `--table`.

**Verification:** A test checks that every line of the table has the same width, and that the reasons and column headers are present.
