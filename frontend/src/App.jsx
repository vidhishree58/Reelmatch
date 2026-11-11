import { useCallback, useEffect, useRef, useState } from "react";
import { fetchMovies } from "./api.js";
import MovieCard from "./MovieCard.jsx";
import MovieModal from "./MovieModal.jsx";

export default function App() {
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState(""); // debounced value
  const [movies, setMovies] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [openId, setOpenId] = useState(null);
  const reqId = useRef(0);

  // Search box: wait 400ms after typing stops, then call the API
  useEffect(() => {
    const t = setTimeout(() => setSearch(query.trim()), 400);
    return () => clearTimeout(t);
  }, [query]);

  const load = useCallback(async (q, p) => {
    const mine = ++reqId.current;
    setLoading(true);
    setError("");
    try {
      const data = await fetchMovies({ q, page: p });
      if (mine !== reqId.current) return; // ignore outdated responses
      setMovies((prev) => (p === 1 ? data.results : [...prev, ...data.results]));
      setHasMore(data.has_more);
      setTotal(data.total);
    } catch (e) {
      if (mine === reqId.current) setError(e.message);
    } finally {
      if (mine === reqId.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    setPage(1);
    load(search, 1);
  }, [search, load]);

  const loadMore = () => {
    const next = page + 1;
    setPage(next);
    load(search, next);
  };

  return (
    <>
      <header className="top">
        <h1>Reelmatch</h1>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search movies by name…"
          aria-label="Movie search"
        />
      </header>

      <main>
        <p className="count">
          {search
            ? `${total} movies found for "${search}"`
            : `${total.toLocaleString()} movies. Click any movie to see similar ones.`}
        </p>

        {error && (
          <div className="state error">
            {error} <button onClick={() => load(search, page)}>Try again</button>
          </div>
        )}

        <div className="grid">
          {movies.map((m) => (
            <MovieCard key={m.id} movie={m} onOpen={setOpenId} />
          ))}
        </div>

        {loading && <p className="state">Loading…</p>}
        {!loading && !error && movies.length === 0 && (
          <p className="state">No movies found. Try a different name.</p>
        )}
        {!loading && hasMore && (
          <button className="more" onClick={loadMore}>Load more</button>
        )}
      </main>

      {openId && <MovieModal id={openId} onClose={() => setOpenId(null)} onOpen={setOpenId} />}
    </>
  );
}