const BASE = import.meta.env.VITE_API_URL || "http://localhost:5000";

async function get(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error("Server se data nahi aaya. Thodi der baad try karo.");
  return res.json();
}

export const fetchMovies = ({ q = "", page = 1 }) =>
  get(`/api/movies?page=${page}&size=24&q=${encodeURIComponent(q)}`);

export const fetchMovie = (id) => get(`/api/movie/${id}`);
