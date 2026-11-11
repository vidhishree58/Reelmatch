import json, os, time
from concurrent.futures import ThreadPoolExecutor

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()
HERE = os.path.dirname(os.path.abspath(__file__))
TMDB_KEY = os.getenv("TMDB_API_KEY", "")  # optional
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")  # set to your Vercel URL after deploying

app = Flask(__name__)
CORS(app, origins=FRONTEND_URL if FRONTEND_URL != "*" else "*")

with open(os.path.join(HERE, "model", "movies.json"), encoding="utf-8") as f:
    MOVIES = json.load(f)
with open(os.path.join(HERE, "model", "similar.json")) as f:
    SIMILAR = json.load(f)

BY_ID = {m["id"]: m for m in MOVIES}

# ---------- Poster cache (memory + file) ----------
CACHE_FILE = os.path.join(HERE, "posters_cache.json")
try:
    with open(CACHE_FILE, encoding="utf-8") as f:
        POSTERS = {int(k): v for k, v in json.load(f).items()}
except (OSError, ValueError):
    POSTERS = {}  # movie id -> poster url (or None if the movie has no poster)


def save_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(POSTERS, f)
    except OSError:
        pass  # cache is only an optimisation, ignore write errors


# ---------- Poster sources ----------
WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_HEADERS = {"User-Agent": "Reelmatch/1.0 (student project)"}


def poster_from_tmdb(movie_id):
    """Returns (url, ok). ok=False means the request failed, so don't cache it."""
    r = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}",
        params={"api_key": TMDB_KEY},
        timeout=6,
    )
    if r.status_code == 404:
        return None, True
    if not r.ok:
        return None, False
    path = r.json().get("poster_path")
    return ("https://image.tmdb.org/t/p/w342" + path if path else None), True


def poster_from_wikipedia(movie):
    """Returns (url, ok). ok=False means the request failed, so don't cache it."""
    r = requests.get(
        WIKI_API,
        params={
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": f"{movie['title']} {movie['year']} film",
            "gsrlimit": 3,
            "prop": "pageimages",
            "piprop": "thumbnail",
            "pilicense": "any",
            "pithumbsize": 342,
        },
        headers=WIKI_HEADERS,
        timeout=8,
    )
    if r.status_code != 200:
        return None, False
    data = r.json()
    if "error" in data:
        return None, False
    pages = sorted(
        data.get("query", {}).get("pages", {}).values(),
        key=lambda p: p.get("index", 99),
    )
    for p in pages:  # first search result that has an image
        src = p.get("thumbnail", {}).get("source")
        if src:
            return src, True
    return None, True  # request worked, but no image found


def fetch_poster(movie):
    mid = movie["id"]
    if mid in POSTERS:
        return POSTERS[mid]
    for attempt in range(2):  # one retry if the request fails
        try:
            if TMDB_KEY:
                url, ok = poster_from_tmdb(mid)
            else:
                url, ok = poster_from_wikipedia(movie)
        except (requests.RequestException, ValueError):
            url, ok = None, False
        if ok:
            POSTERS[mid] = url  # cache only successful lookups
            return url
        if attempt == 0:
            time.sleep(0.7)
    return None  # failed twice: not cached, will retry on next request


def with_posters(movies):
    with ThreadPoolExecutor(max_workers=4) as ex:
        posters = list(ex.map(fetch_poster, movies))
    save_cache()
    return [dict(m, poster=p) for m, p in zip(movies, posters)]


def card(m):
    """Light data for list views."""
    return {k: m[k] for k in ("id", "title", "year", "rating", "genres")}


# ---------- Routes ----------
@app.get("/")
def home():
    return jsonify(message="Reelmatch API is running. Try /api/movies")


@app.get("/api/health")
def health():
    return jsonify(
        status="ok",
        movies=len(MOVIES),
        tmdb_key_set=bool(TMDB_KEY),
        posters_cached=len(POSTERS),
    )


@app.get("/api/movies")
def movies():
    q = request.args.get("q", "").strip().lower()
    try:
        page = max(int(request.args.get("page", 1)), 1)
        size = min(max(int(request.args.get("size", 24)), 1), 48)
    except ValueError:
        return jsonify(error="Invalid page or size"), 400
    pool = [m for m in MOVIES if q in m["title"].lower()] if q else MOVIES
    start = (page - 1) * size
    chunk = pool[start : start + size]
    return jsonify(
        total=len(pool),
        page=page,
        has_more=start + size < len(pool),
        results=with_posters([card(m) for m in chunk]),
    )


@app.get("/api/movie/<int:movie_id>")
def movie(movie_id):
    m = BY_ID.get(movie_id)
    if not m:
        return jsonify(error="Movie not found"), 404
    sims = [card(BY_ID[i]) for i in SIMILAR.get(str(movie_id), [])[:10] if i in BY_ID]
    detail = with_posters([m])[0]
    return jsonify(movie=detail, similar=with_posters(sims))


if __name__ == "__main__":
    app.run(debug=True, port=5000)