# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**: a small recommender that matches songs to a listener's vibe.

---

## 2. Intended Use

**Goal.** Given a listener's favorite genre, favorite mood, wanted energy level, and taste for acoustic sound, suggest the 5 songs from a small catalog that fit best. It also says why each song was picked.

**Intended use.**
- Classroom exploration of how a recommender turns data into a ranked list.
- Showing how scoring rules and weights change results.

**Not intended for.**
- Real listeners or a real music app. The catalog has only 18 songs.
- Judging music quality or an artist's worth.
- Any decision that affects people, such as paying artists or choosing who gets exposure.

**Assumptions about the user.** The listener knows their own taste and can describe it in four values. Real people are messier than that.

---

## 3. How the Model Works  

The recommender compares every song in the catalog to a short description of what the listener likes, gives each song points, and shows the highest-scoring songs.

A listener's taste is four things: a favorite genre, a favorite mood, how energetic they want the music to be (0 is very calm, 1 is very intense), and whether they like acoustic sounds. For each song, the model awards:

- **2 points** if the genre matches the favorite genre
- **1 point** if the mood matches the favorite mood
- **Up to 1.5 points for energy**, more the closer the song's energy is to what the listener wants. A song that is too calm loses points just like a song that is too intense.
- **Up to 0.5 points for acoustic feel**, using how acoustic the song sounds if the listener likes that, or how electronic it sounds if they don't

The best possible score is 5. Genre counts most because it is the steadiest sign of taste, and mood counts less because it shifts from day to day. Every score comes with a plain-language list of reasons, so the listener can see why a song was picked. Songs are then sorted from highest to lowest score and the top five are shown.

The model never learns from skips or likes. It only follows the preferences it is given, which is why it is a simple content-based simulation and not a real streaming recommender.

---

## 4. Data

- **Size:** 18 songs in `data/songs.csv`. I wrote the 8 extra songs myself, with help from an AI assistant. They are made up, not real tracks.
- **Features per song:** genre, mood, energy, tempo, valence, danceability, acousticness. The score uses genre, mood, energy and acousticness. The rest are stored but unused.
- **Genres:** pop, indie pop, lofi, rock, ambient, jazz, synthwave, hip hop, r&b, country, classical, edm, metal, reggae, folk.
- **Moods:** happy, chill, intense, relaxed, moody, focused, confident, romantic, nostalgic, melancholy, euphoric, angry, uplifting, peaceful.
- **Limits:** most genres have one song, lofi has three. There are no lyrics, no language, no artist popularity, and no listening history. Moods and genres are single labels picked by me, so they are opinions.

---

## 5. Strengths

- It works well for clear, consistent tastes. Chill Lofi and Deep Intense Rock gave lists I would agree with.
- Opposite listeners get opposite lists. Lofi and Rock shared no songs.
- Every pick comes with reasons, like "genre match (+2.0)". You can always see why a song ranked where it did.
- The energy rule rewards being *close* to the target, not just high or low.
- It handles messy input, like " Lofi" or "CHILL", and never crashes on missing preferences.

---

## 6. Limitations and Bias

The biggest weakness I found is that genre is worth too much. A genre match gives 2 of the 5 possible points, so it can outweigh what the listener says about how the music should feel. The clearest case is the "conflicting" profile: the listener wants lofi but energy 0.9, and the system still returns three quiet, slow lofi songs at the top because they match the genre label, even though they are the opposite of "high energy." The same thing happens in the "dead-center" profile, where *Gym Hero* (one of the loudest songs in the catalog) ranks second for someone who asked for medium energy, only because it is labeled pop. Because the catalog is tiny, with one to three songs per genre, this also means the genre label mostly decides the first few slots and the rest of the list is filled by whatever is closest in energy. Finally, mood and genre are matched as exact words, so "sad" (which is not in the catalog) earns zero points, and "indie pop" gets no credit for a pop fan.

---

## 7. Evaluation

**Profiles tested** (full terminal output is in the README):

- **High-Energy Pop** (pop, happy, energy 0.9)
- **Chill Lofi** (lofi, chill, energy 0.4, likes acoustic)
- **Deep Intense Rock** (rock, intense, energy 0.92)
- **Conflicting** (lofi, "sad", energy 0.9): tries to trick the system with preferences that pull in opposite directions
- **Unknown genre** (bossa nova, relaxed, energy 0.3): a genre that is not in the catalog
- **Dead-center** (pop, chill, energy 0.5): no strong taste in any direction

I also ran 7 hand-labelled profiles through a grader (`tests/eval_quality.py`) and 27 automated tests.

**Do the results feel right?** For the three typical profiles, yes. Chill Lofi returns the three lofi songs, then ambient and jazz, which is what I would put on a "quiet study" playlist. Deep Intense Rock puts *Storm Runner* far ahead, and the rest of its list is loud, intense songs from other genres.

**What surprised me.** *Gym Hero* keeps showing up. For a "Happy Pop" fan, it is second even though it is an intense workout song, not a happy one. The reason is simple arithmetic. The system gives 2 points for "pop," and *Gym Hero* is labeled pop. It misses the "happy" point (1.0), but it is also very high energy, which is exactly what this listener asked for. *Rooftop Lights* is genuinely happy and has similar energy, but its genre is "indie pop," a different word, so it gets zero genre points and falls to third. A person would probably swap them. Another surprise was that the "sad" mood did nothing: no song is labeled "sad," so that part of the profile was simply ignored.

**Why *Sunrise City* wins for High-Energy Pop** (checking by hand): 2.0 genre + 1.0 mood + 1.38 energy (0.82 is close to 0.9) + 0.41 for a non-acoustic sound = 4.79.

**Experiment: double the importance of energy, halve genre** (genre 2.0 to 1.0, energy 1.5 to 3.0; the highest possible score becomes 5.5, a perfect song still scores exactly 5.5, and no score goes negative, so the math stays valid). I ran this without changing the saved code.

| Profile | Top 3 with energy x2, genre /2 |
|---|---|
| High-Energy Pop | Sunrise City, Gym Hero, Rooftop Lights |
| Chill Lofi | Midnight Coding, Library Rain, Focus Flow |
| Deep Intense Rock | Storm Runner, Gym Hero, Pulse Cathedral |
| Conflicting (sad but 0.9 energy) | Storm Runner, Gym Hero, Midnight Coding |
| Unknown genre (bossa nova) | Coffee Shop Stories, Pine Hollow, Spacewalk Thoughts |
| Dead-center (everything 0.5) | Midnight Coding, Library Rain, Sunrise City |

The change made the results more accurate, not just different. In the conflicting profile, *Storm Runner* and *Gym Hero* (high energy) now lead instead of the quiet lofi songs. In the dead-center profile, *Gym Hero* drops out of the top 5 and calm songs rise. Typical profiles barely moved. On the hand-labelled grader the average score rose from 98.0 to 98.4. The tradeoff is that genre now matters less, so a listener who truly wants "only jazz" gets less strictly jazz. I kept the original weights in the code for now.

**Profile-by-profile comparisons**

- **Pop vs. Lofi:** no songs in common in the top 5. Pop gets bright, loud songs (*Sunrise City*, *Gym Hero*); lofi gets quiet, acoustic ones (*Library Rain*, *Midnight Coding*). This makes sense: genre, energy and acoustic taste all point in opposite directions.
- **Pop vs. Rock:** both want high energy, so they share *Storm Runner*, *Gym Hero*, *Pulse Cathedral* and *Sunrise City*. The genre decides who is first (*Sunrise City* vs. *Storm Runner*). *Gym Hero* is second for both because it is pop (matches the pop fan) and intense (matches the rock fan's mood).
- **Pop vs. Conflicting:** both ask for energy 0.9, but Conflicting gets quiet lofi songs on top, while Pop gets loud ones. Only *Storm Runner* and *Gym Hero* are shared, and they are at the bottom of the Conflicting list. This shows genre beating energy.
- **Pop vs. Unknown genre:** no overlap. Bossa nova matches nothing, so only mood and energy decide, and the list is calm, acoustic and mixed (jazz, folk, ambient). That is a reasonable fallback, but the user is not told their genre was not found.
- **Pop vs. Dead-center:** both start with *Sunrise City* and *Gym Hero*. Dead-center asked for chill, medium energy, so *Gym Hero* in second place is a poor match; it is there only because it is pop.
- **Lofi vs. Rock:** completely different lists, which is the sanity check I wanted. A relaxed study listener and a gym listener should not get the same songs.
- **Lofi vs. Conflicting:** both are lofi, so the same three lofi songs lead, but scores drop from about 4.8 to about 3.1 because "sad" and energy 0.9 earn nothing. Positions 4 and 5 switch from quiet ambient and jazz to loud rock and pop, because energy is the only thing left to match.
- **Lofi vs. Unknown genre:** both like quiet acoustic music, so they share *Library Rain*, *Spacewalk Thoughts* and *Coffee Shop Stories*. Without a genre bonus, jazz moves to first place. It makes sense: the "quiet and acoustic" cluster appears whether or not the genre matches.
- **Lofi vs. Dead-center:** Dead-center's "chill" mood pulls in *Midnight Coding*, *Library Rain* and *Spacewalk Thoughts*, which are also on the lofi list. The pop genre still puts *Sunrise City* and *Gym Hero* on top.
- **Rock vs. Conflicting:** only *Storm Runner* and *Gym Hero* are shared. Both want high energy, but Rock's genre and mood match puts those songs first; Conflicting's lofi genre pushes them down to fourth and fifth.
- **Rock vs. Unknown genre:** no overlap, at opposite ends of the energy scale. Fine.
- **Rock vs. Dead-center:** the only shared songs are *Sunrise City* and *Gym Hero*. Dead-center is a pop listener at medium energy, so this overlap is mostly the pop label again.
- **Conflicting vs. Unknown genre:** both like acoustic sound and share *Library Rain*. Conflicting is steered by its lofi genre; Unknown genre has no genre match, so mood and energy decide and the list is more varied (jazz, folk, ambient, classical).
- **Conflicting vs. Dead-center:** Conflicting's top three are lofi; Dead-center's are pop first, then lofi. They share *Midnight Coding* and *Library Rain*, which are the only songs with both low-ish energy and a chill feel.
- **Unknown genre vs. Dead-center:** they share *Library Rain* and *Spacewalk Thoughts*. Dead-center is led by pop songs; Unknown genre is led by *Coffee Shop Stories* because relaxed, low-energy acoustic songs fit best when no genre matches.

**In plain words, why *Gym Hero* shows up for "Happy Pop" fans:** the system is like a store clerk who first asks "what section do you shop in?" and only then asks about the mood. *Gym Hero* is in the pop section, and it is lively like the listener wanted, so it beats any happy song that sits in a nearby section. The fix is to make the clerk care more about the feel of the music than about the shelf label.

---

## 8. Future Work

1. **Lower the genre weight.** My experiment (genre halved, energy doubled) gave better results for the conflicting and dead-center profiles. I kept the original weights for now, but this is the first change I would make.
2. **Give partial credit to similar labels.** "Indie pop" should count a little for a pop fan, and "relaxed" a little for "chill." My first try used broad groups and made results worse, so the groups need to be small and careful.
3. **Add variety and use more features.** Use tempo, valence and danceability, and avoid filling the top 5 with the same genre.
4. **Learn from behavior.** Let skips and replays adjust the profile, as real apps do.

---

## 9. Personal Reflection

**Biggest learning moment.** The test results showed me that "the code works" and "the recommendations are good" are two different things. All my tests passed, yet *Gym Hero* kept showing up for happy pop fans. I only saw why when I added tricky profiles, like a listener who wants "lofi" but energy 0.9. One weight, genre at 2.0, was quietly deciding too much.

**How AI helped, and when I double-checked it.** The AI wrote the first version of the code, the extra songs, the test suites and the first draft of this card quickly. I still had to check it. My second improvement idea (related genres and moods) passed all its tests but made the rankings worse, so I threw it out and kept the earlier version. Tests alone were not enough. I also saw that the grader I wrote uses labels I made up myself, so its numbers are a sanity check, not proof. The starter `main.py` also had an import that failed with the command in the instructions, which I only found by running it.

**What surprised me.** A few additions and a sort can feel like a real recommendation. Seeing "genre match, mood match, energy close" next to a song makes the list feel thoughtful, even though it is only arithmetic. That also shows how easy it would be for a real system to look smarter or fairer than it is.

**What I would try next.** Try the lower genre weight for real, add small partial credit for similar labels, use tempo and valence, and build a bigger catalog so one genre cannot dominate. Then I would test with real people to see if they agree with the lists.
