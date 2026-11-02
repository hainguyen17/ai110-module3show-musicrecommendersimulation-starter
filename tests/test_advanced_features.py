import pytest

from src.main import PROFILES, format_table, main
from src.recommender import MODES, Weights, load_songs, recommend_songs, score_song

POP = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8, "likes_acoustic": False}


def song(**kw):
    base = dict(id=1, title="T", artist="A", genre="pop", mood="happy", energy=0.8, tempo_bpm=120,
                valence=0.8, danceability=0.8, acousticness=0.2, popularity=50, release_decade=2000,
                mood_tags=["warm", "nostalgic"], language="en", is_instrumental=0)
    base.update(kw)
    return base


@pytest.fixture(scope="module")
def songs():
    return load_songs("data/songs.csv")


# Challenge 1: advanced features
class TestAdvancedFeatures:
    def test_loader_parses_new_columns(self, songs):
        s = songs[0]
        assert isinstance(s["popularity"], int) and 0 <= s["popularity"] <= 100
        assert isinstance(s["release_decade"], int) and s["release_decade"] % 10 == 0
        assert isinstance(s["mood_tags"], list) and s["mood_tags"]
        assert s["is_instrumental"] in (0, 1) and s["language"]

    def test_unset_preferences_change_nothing(self):
        plain, _ = score_song(POP, song())
        assert plain == pytest.approx(score_song({**POP, "preferred_tags": None, "preferred_decade": None}, song())[0])

    def test_tags_reward_overlap(self):
        prefs = {**POP, "preferred_tags": ["warm", "nostalgic"]}
        both, _ = score_song(prefs, song(mood_tags=["warm", "nostalgic"]))
        one, _ = score_song(prefs, song(mood_tags=["warm"]))
        none, _ = score_song(prefs, song(mood_tags=["dark"]))
        assert both > one > none

    def test_decade_closer_is_better(self):
        prefs = {**POP, "preferred_decade": 2000}
        same, _ = score_song(prefs, song(release_decade=2000))
        near, _ = score_song(prefs, song(release_decade=2010))
        far, _ = score_song(prefs, song(release_decade=1960))
        assert same > near > far
        assert far == pytest.approx(score_song(POP, song())[0])  # no negative points

    def test_popularity_closer_is_better(self):
        prefs = {**POP, "target_popularity": 90}
        assert score_song(prefs, song(popularity=88))[0] > score_song(prefs, song(popularity=20))[0]

    def test_language_and_instrumental(self):
        base = score_song(POP, song())[0]
        assert score_song({**POP, "preferred_language": "EN"}, song())[0] > base
        assert score_song({**POP, "prefers_instrumental": True}, song(is_instrumental=1))[0] > base
        assert score_song({**POP, "prefers_instrumental": True}, song(is_instrumental=0))[0] == pytest.approx(base)

    def test_old_style_song_without_new_fields_still_scores(self):
        old = {k: v for k, v in song().items() if k not in ("popularity", "release_decade", "mood_tags", "language", "is_instrumental")}
        assert score_song({**POP, "preferred_decade": 2000, "preferred_tags": ["warm"]}, old)[0] > 0


# Challenge 2: scoring modes
class TestModes:
    def test_default_is_balanced(self, songs):
        a = recommend_songs(POP, songs, k=5)
        b = recommend_songs(POP, songs, k=5, mode="balanced")
        assert a == b

    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError):
            score_song(POP, song(), mode="vibes-only")

    def test_custom_weights_object_accepted(self):
        assert score_song(POP, song(), mode=Weights(genre=0.0, mood=0.0))[0] < score_song(POP, song())[0]

    def test_genre_first_rewards_genre_more(self):
        gap = lambda m: score_song(POP, song(genre="pop"), m)[0] - score_song(POP, song(genre="rock"), m)[0]
        assert gap("genre-first") > gap("balanced") > gap("mood-first")

    def test_mood_first_rewards_mood_more(self):
        gap = lambda m: score_song(POP, song(mood="happy"), m)[0] - score_song(POP, song(mood="angry"), m)[0]
        assert gap("mood-first") > gap("balanced")

    def test_energy_focused_follows_energy(self, songs):
        prefs = {"favorite_genre": "lofi", "favorite_mood": "sad", "target_energy": 0.9, "likes_acoustic": True}
        top = recommend_songs(prefs, songs, k=3, mode="energy-focused")
        assert all(s["energy"] >= 0.82 for s, _, _ in top)

    def test_modes_actually_differ(self, songs):
        orders = {m: [s["id"] for s, _, _ in recommend_songs(PROFILES["Conflicting (sad but 0.9 energy)"], songs, mode=m)] for m in MODES}
        assert len({tuple(o) for o in orders.values()}) > 1

    def test_every_mode_scores_nonnegative(self, songs):
        for m in MODES:
            assert all(sc >= 0 for _, sc, _ in recommend_songs(POP, songs, k=18, mode=m))


# Challenge 3: diversity
class TestDiversity:
    def test_off_by_default_matches_plain_ranking(self, songs):
        assert recommend_songs(POP, songs) == recommend_songs(POP, songs, diversity=False)

    def test_same_artist_penalized(self):
        twins = [song(id=1, title="A1", artist="X"), song(id=2, title="A2", artist="X"), song(id=3, title="B1", artist="Y", energy=0.75)]
        plain = [s["id"] for s, _, _ in recommend_songs(POP, twins, k=3)]
        diverse = recommend_songs(POP, twins, k=3, diversity=True)
        assert plain == [1, 2, 3]
        assert [s["id"] for s, _, _ in diverse] == [1, 3, 2]
        assert any("diversity penalty" in expl for _, _, expl in diverse)

    def test_fewer_repeated_artists_in_top5(self, songs):
        prefs = PROFILES["Chill Lofi"]
        artists = lambda r: [s["artist"] for s, _, _ in r]
        plain, diverse = artists(recommend_songs(prefs, songs)), artists(recommend_songs(prefs, songs, diversity=True))
        assert len(set(diverse)) >= len(set(plain))

    def test_still_returns_k_items(self, songs):
        assert len(recommend_songs(POP, songs, k=7, diversity=True)) == 7

    def test_k_zero(self, songs):
        assert recommend_songs(POP, songs, k=0, diversity=True) == []


# Challenge 4: table
class TestTable:
    def test_table_contains_reasons_and_columns(self, songs):
        out = format_table(recommend_songs(POP, songs, k=3))
        for text in ("Title", "Artist", "Score", "Reasons", "genre match", "Sunrise City"):
            assert text in out

    def test_table_lines_are_aligned(self, songs):
        lines = format_table(recommend_songs(POP, songs, k=5)).split("\n")
        assert len({len(l) for l in lines}) == 1

    def test_cli_flags_run(self, capsys):
        main(["--mode", "mood-first", "--diversity", "--table", "--profile", "lofi"])
        out = capsys.readouterr().out
        assert "Chill Lofi" in out and "mood-first" in out and "+--" in out
