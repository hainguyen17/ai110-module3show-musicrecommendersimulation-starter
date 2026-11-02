# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

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

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
