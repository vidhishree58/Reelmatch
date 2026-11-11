# Reelmatch: Movie Recommender (Flask + React)

Website khulte hi saari movies (24 ek baar mein, "Load more" se aur). Kisi movie pe click karo to details aur **Similar movies** (TF-IDF + cosine similarity) dikhti hain.

```
movie-recommender/
├── backend/    Flask API + precomputed ML model (model/*.json)
└── frontend/   React + Vite
```

## 1. TMDB API key (poster ke liye)
1. https://www.themoviedb.org pe free account banao
2. Settings → API → "API Key (v3 auth)" copy karo

Bina key ke bhi sab chalega, bas posters ki jagah movie ka naam dikhega.

## 2. Local run (VS Code)

**Backend** (terminal 1)
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env         # Mac/Linux: cp .env.example .env
# .env kholkar TMDB_API_KEY daalo
python app.py                  # http://localhost:5000/api/health
```

**Frontend** (terminal 2)
```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

## 3. Deploy

### Backend → Render
1. Code GitHub pe push karo
2. Render → New → **Web Service** → repo select karo
3. Settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Environment variables:
   - `TMDB_API_KEY` = tumhari key
   - `FRONTEND_URL` = Vercel URL (frontend deploy ke baad daalna, jaise `https://reelmatch.vercel.app`, end mein `/` nahi)
5. Deploy ke baad `https://<naam>.onrender.com/api/health` kholkar check karo

Free plan pe Render 15 min inactivity ke baad sleep karta hai, to pehli request 30-50 sec le sakti hai.

### Frontend → Vercel
1. Vercel → Add New → Project → wahi repo
2. Root Directory: `frontend` (Framework: Vite apne aap detect ho jayega)
3. Environment variable: `VITE_API_URL` = Render ka URL (end mein `/` nahi)
4. Deploy
5. Vercel URL ko Render ke `FRONTEND_URL` mein daalo aur Render redeploy karo

## Model kaise kaam karta hai
`backend/build_model.py`: genres, keywords, cast, director aur overview ko ek text "soup" mein jodta hai, TF-IDF vectors banata hai, cosine similarity se har movie ki top 12 similar movies nikalta hai. Ye pehle se chalakar `model/*.json` mein save hai, isliye server halka hai aur deploy pe pandas/sklearn nahi chahiye.

Model dobara banana ho to Kaggle CSVs `backend/data/` mein rakho aur:
```bash
pip install -r requirements-build.txt
python build_model.py
```
