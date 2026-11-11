# Reelmatch: Movie Recommendation System

A full-stack movie discovery app. Browse thousands of movies, search by title, and open any movie to see its details along with **similar movies** recommended by a content-based machine learning model.

**Live demo:** _add your Netlify URL here after deployment_

## Features

- Browse 4,800+ movies with posters, ratings and release years
- Search movies by title
- "Load more" pagination for fast page loads
- Movie detail view with overview, genres, cast, director and runtime
- Content-based recommendations: the 10 most similar movies for every title
- Responsive dark-themed interface

## Tech Stack

| Layer | Technology |
|---|---|
| Machine learning | Python, pandas, scikit-learn (TF-IDF, cosine similarity) |
| Backend | Flask, Flask-CORS, Requests, Gunicorn |
| Frontend | React 18, Vite |
| Posters | Wikipedia API (no key needed), optional TMDB API |
| Deployment | Render (backend), Netlify (frontend) |
| Dataset | [TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) |

## Project Structure

```
movie-recommender/
├── backend/
│   ├── app.py                 # Flask API
│   ├── build_model.py         # Builds the recommendation model from the CSVs
│   ├── model/
│   │   ├── movies.json        # Movie metadata (generated)
│   │   └── similar.json       # Top similar movies per title (generated)
│   ├── data/                  # Place the Kaggle CSV files here
│   ├── requirements.txt       # Runtime dependencies
│   ├── requirements-build.txt # Extra dependencies for rebuilding the model
│   └── Procfile
├── frontend/
│   ├── src/                   # React components and styles
│   ├── index.html
│   └── package.json
└── README.md
```

## How the Recommendation Model Works

The recommender is **content-based**: it compares movies using their own attributes, not user ratings or history.

1. `build_model.py` reads the movies and credits CSV files and merges them.
2. For each movie, genres, keywords, top cast, director and overview are combined into a single text document. Genres, cast and director are repeated to give them more weight.
3. The text is converted into TF-IDF vectors (scikit-learn).
4. Cosine similarity is computed between all movies.
5. The 12 closest movies for each title are saved to `model/similar.json`.

The model is generated once and the results are stored as JSON. The deployed server only loads these files, so it starts quickly and does not need pandas or scikit-learn.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Service status and number of loaded movies |
| GET | `/api/movies?q=&page=&size=` | Paginated movie list; `q` filters by title (`size` max 48) |
| GET | `/api/movie/<id>` | Movie details and 10 similar movies |

## Running Locally

**Prerequisites:** Python 3.9+ and Node.js 18+.

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The API runs at `http://localhost:5000`. Verify it at `http://localhost:5000/api/health`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`. By default it connects to the backend at `http://localhost:5000` (configurable via `VITE_API_URL` in `frontend/.env`).

## Configuration

**Backend** (`backend/.env`, see `.env.example`)

| Variable | Required | Description |
|---|---|---|
| `TMDB_API_KEY` | No | If set, posters are fetched from TMDB. Otherwise Wikipedia is used. |
| `FRONTEND_URL` | No | Allowed frontend origin for CORS. Defaults to `*`; set it to your Netlify URL in production. |

**Frontend** (`frontend/.env`)

| Variable | Description |
|---|---|
| `VITE_API_URL` | Base URL of the backend API |

## Deployment

### Backend on Render

1. Push the project to GitHub.
2. In Render, create a new **Web Service** and select the repository.
3. Configure:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Deploy, then confirm that `https://<your-service>.onrender.com/api/health` responds.
5. Once the frontend is live, add the environment variable `FRONTEND_URL` (the Netlify URL, no trailing slash). Optionally add `TMDB_API_KEY` as well.

### Frontend on Netlify

1. In Netlify, choose **Add new site → Import an existing project** and select the same repository.
2. Configure:
   - **Base directory:** `frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `dist`
3. Add the environment variable `VITE_API_URL` with the Render service URL (no trailing slash). This must be set before the build, because Vite embeds it at build time.
4. Deploy.

If the backend URL changes later, update `VITE_API_URL` and trigger a new deploy with a cleared cache.

## Rebuilding the Model

To regenerate the model from the dataset:

1. Download the TMDB 5000 dataset from Kaggle and place `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv` in `backend/data/`.
2. Run:

```bash
cd backend
pip install -r requirements-build.txt
python build_model.py
```

## Limitations

- The dataset contains movies up to 2017, so newer releases are not included.
- Recommendations are content-based only and do not use user ratings or personalisation.
- Wikipedia is a free poster source, so a few movies may show a text placeholder instead of a poster. Adding a TMDB API key improves poster coverage.
- On Render's free plan the server sleeps after inactivity, so the first request can take 30-50 seconds. The in-memory poster cache is also cleared on restart.

## Acknowledgements

- [TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) on Kaggle
- Poster images via Wikipedia and The Movie Database (TMDB)