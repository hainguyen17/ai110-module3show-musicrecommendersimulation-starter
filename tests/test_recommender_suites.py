import copy
import pytest

from src.recommender import (
    Recommender, Song, UserProfile, load_songs, recommend_songs, score_song,
)

CSV = "data/songs.csv"
POP = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8, "likes_acoustic": False}


def song(**kw):
    base = dict(id=1, title="T", artist="A", genre="pop", mood="happy", energy=0.8,
                tempo_bpm=120, valence=0.8, danceability=0.8, acousticness=0.2)
    base.update(kw)
    return base


@pytest.fixture(scope="module")
def songs():
    return load_songs(CSV)


# Suite 1: loading
class TestLoading:
    def test_row_count(self, songs):
        assert len(songs) == 18

    def test_numeric_types(self, songs):
        for s in songs:
            assert isinstance(s["id"], int) and isinstance(s["tempo_bpm"], int)
            for k in ("energy", "valence", "danceability", "acousticness"):
                assert isinstance(s[k], float) and 0.0 <= s[k] <= 1.0

    def test_required_fields(self, songs):
        for s in songs:
            assert {"title", "artist", "genre", "mood"} <= s.keys()


# Suite 2: scoring
class TestScoring:
    def test_genre_match_worth_two(self):
        a, _ = score_song(POP, song(genre="pop"))
        b, _ = score_song(POP, song(genre="rock"))
        assert a - b == pytest.approx(2.0)

    def test_mood_match_worth_one(self):
        a, _ = score_song(POP, song(mood="happy"))
        b, _ = score_song(POP, song(mood="angry"))
        assert a - b == pytest.approx(1.0)

    def test_energy_closer_is_better_both_directions(self):
        near, _ = score_song(POP, song(energy=0.75))
        far_hi, _ = score_song(POP, song(energy=1.0))
        far_lo, _ = score_song(POP, song(energy=0.3))
        assert near > far_hi and near > far_lo

    def test_energy_is_symmetric(self):
        hi, _ = score_song(POP, song(energy=0.9))
        lo, _ = score_song(POP, song(energy=0.7))
        assert hi == pytest.approx(lo)

    def test_acoustic_preference_flips(self):
        acoustic = song(acousticness=0.9)
        no, _ = score_song({**POP, "likes_acoustic": False}, acoustic)
        yes, _ = score_song({**POP, "likes_acoustic": True}, acoustic)
        assert yes > no

    def test_score_bounds(self, songs):
        for s in songs:
            score, _ = score_song(POP, s)
            assert 0.0 <= score <= 5.0

    def test_perfect_song_near_max(self):
        score, _ = score_song(POP, song(acousticness=0.0))
        assert score == pytest.approx(5.0)

    def test_reasons_returned(self):
        score, reasons = score_song(POP, song())
        assert isinstance(reasons, list) and reasons
        assert any("genre" in r for r in reasons) and any("mood" in r for r in reasons)

    def test_reasons_sum_to_score(self):
        import re
        score, reasons = score_song(POP, song(energy=0.6, acousticness=0.5))
        total = sum(float(re.search(r"\+(\d+\.\d+)\)", r).group(1)) for r in reasons)
        assert total == pytest.approx(score, abs=0.03)


# Suite 3: ranking
class TestRanking:
    def test_sorted_descending(self, songs):
        recs = recommend_songs(POP, songs, k=10)
        scores = [r[1] for r in recs]
        assert scores == sorted(scores, reverse=True)

    def test_k_respected(self, songs):
        assert len(recommend_songs(POP, songs, k=3)) == 3

    def test_k_larger_than_catalog(self, songs):
        assert len(recommend_songs(POP, songs, k=100)) == len(songs)

    def test_input_not_mutated(self, songs):
        before = copy.deepcopy(songs)
        recommend_songs(POP, songs, k=5)
        assert songs == before

    def test_deterministic_ties(self):
        twins = [song(id=i, title=f"S{i}") for i in (3, 1, 2)]
        a = [r[0]["id"] for r in recommend_songs(POP, twins, k=3)]
        b = [r[0]["id"] for r in recommend_songs(POP, list(reversed(twins)), k=3)]
        assert a == b

    def test_return_shape(self, songs):
        s, score, expl = recommend_songs(POP, songs, k=1)[0]
        assert isinstance(s, dict) and isinstance(score, float) and isinstance(expl, str) and expl


# Suite 4: OOP parity
class TestOOPParity:
    def test_class_matches_functional(self, songs):
        objs = [Song(**s) for s in songs]
        user = UserProfile("lofi", "chill", 0.4, True)
        prefs = {"favorite_genre": "lofi", "favorite_mood": "chill", "target_energy": 0.4, "likes_acoustic": True}
        got = [s.id for s in Recommender(objs).recommend(user, k=5)]
        want = [r[0]["id"] for r in recommend_songs(prefs, songs, k=5)]
        assert got == want

    def test_explanation_mentions_match(self, songs):
        objs = [Song(**s) for s in songs]
        user = UserProfile("pop", "happy", 0.8, False)
        assert "genre" in Recommender(objs).explain_recommendation(user, objs[0])


# Suite 5: robustness
class TestRobustness:
    def test_case_and_whitespace_insensitive(self):
        messy = {**POP, "favorite_genre": " Pop ", "favorite_mood": "HAPPY"}
        a, _ = score_song(messy, song())
        b, _ = score_song(POP, song())
        assert a == pytest.approx(b)

    def test_missing_optional_prefs_do_not_crash(self):
        score, _ = score_song({"favorite_genre": "pop"}, song())
        assert score >= 2.0

    def test_empty_catalog(self):
        assert recommend_songs(POP, [], k=5) == []

    def test_k_zero(self, songs):
        assert recommend_songs(POP, songs, k=0) == []

    def test_negative_k_is_safe(self, songs):
        assert recommend_songs(POP, songs, k=-1) == []

