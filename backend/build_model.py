"""
Model banane ki script (ek baar chalani hai).
Input : data/tmdb_5000_movies.csv + data/tmdb_5000_credits.csv
Output: model/movies.json  (saari movies ki info)
        model/similar.json (har movie ki top 12 similar movies)
Run   : python build_model.py
"""
import ast, json, os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

HERE = os.path.dirname(os.path.abspath(__file__))
movies = pd.read_csv(os.path.join(HERE, "data", "tmdb_5000_movies.csv"))
credits = pd.read_csv(os.path.join(HERE, "data", "tmdb_5000_credits.csv"))

df = movies.merge(credits[["movie_id", "cast", "crew"]], left_on="id", right_on="movie_id")


def names(text, limit=None):
    try:
        items = ast.literal_eval(text)
    except Exception:
        return []
    out = [i["name"] for i in items]
    return out[:limit] if limit else out


def director(text):
    try:
        for i in ast.literal_eval(text):
            if i.get("job") == "Director":
                return i["name"]
    except Exception:
        pass
    return ""


df["genre_list"] = df["genres"].apply(names)
df["keyword_list"] = df["keywords"].apply(names)
df["cast_list"] = df["cast"].apply(lambda t: names(t, 4))
df["director"] = df["crew"].apply(director)
df["overview"] = df["overview"].fillna("")
df["year"] = df["release_date"].fillna("").str[:4]


def squash(xs):  # "Science Fiction" -> "ScienceFiction" taaki ek hi token bane
    return [x.replace(" ", "") for x in xs]


def soup(r):
    # genres/director/cast ko repeat karke weight badhate hain
    return " ".join(
        squash(r.genre_list) * 3
        + squash(r.keyword_list)
        + squash(r.cast_list) * 2
        + [r.director.replace(" ", "")] * 3
        + [r.overview]
    )


df["soup"] = df.apply(soup, axis=1)

tfidf = TfidfVectorizer(stop_words="english", min_df=2)
matrix = tfidf.fit_transform(df["soup"])
sim = linear_kernel(matrix, matrix)  # cosine similarity (TF-IDF already normalised)

TOP_N = 12
similar = {}
for i in range(len(df)):
    idx = sim[i].argsort()[::-1][1 : TOP_N + 1]
    similar[int(df.iloc[i]["id"])] = [int(df.iloc[j]["id"]) for j in idx]

out = []
for _, r in df.iterrows():
    out.append(
        {
            "id": int(r["id"]),
            "title": r["title"],
            "year": r["year"],
            "rating": round(float(r["vote_average"]), 1),
            "votes": int(r["vote_count"]),
            "popularity": round(float(r["popularity"]), 1),
            "genres": r["genre_list"],
            "overview": r["overview"],
            "tagline": r["tagline"] if isinstance(r["tagline"], str) else "",
            "director": r["director"],
            "cast": r["cast_list"],
            "runtime": int(r["runtime"]) if pd.notna(r["runtime"]) else None,
        }
    )

# Homepage pe popular movies pehle dikhein
out.sort(key=lambda m: m["popularity"], reverse=True)

os.makedirs(os.path.join(HERE, "model"), exist_ok=True)
with open(os.path.join(HERE, "model", "movies.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
with open(os.path.join(HERE, "model", "similar.json"), "w") as f:
    json.dump(similar, f, separators=(",", ":"))
print(f"Done: {len(out)} movies")
