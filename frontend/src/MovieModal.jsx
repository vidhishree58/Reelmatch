import { useEffect, useState } from "react";
import { fetchMovie } from "./api.js";
import MovieCard from "./MovieCard.jsx";

export default function MovieModal({ id, onClose, onOpen }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setData(null);
    setError("");
    fetchMovie(id).then(setData).catch((e) => setError(e.message));
    const body = document.querySelector(".modal");
    if (body) body.scrollTop = 0;
  }, [id]);

  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  const m = data?.movie;

  return (
    <div className="backdrop" onClick={onClose}>
      <div className="modal" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
        <button className="close" onClick={onClose} aria-label="Band karo">✕</button>

        {error && <p className="state error">{error}</p>}
        {!data && !error && <p className="state">Loading…</p>}

        {m && (
          <>
            <div className="detail">
              <div className="detail-poster">
                {m.poster ? <img src={m.poster} alt={m.title} /> : <div className="no-poster">{m.title}</div>}
              </div>
              <div className="detail-info">
                <h2>{m.title}</h2>
                <p className="sub">
                  {m.year}
                  {m.runtime ? ` • ${m.runtime} min` : ""} • ★ {m.rating} ({m.votes.toLocaleString()} votes)
                </p>
                <div className="chips">
                  {m.genres.map((g) => (
                    <span key={g} className="chip">{g}</span>
                  ))}
                </div>
                {m.tagline && <p className="tagline">{m.tagline}</p>}
                <p className="overview">{m.overview}</p>
                {m.director && <p className="credit"><b>Director:</b> {m.director}</p>}
                {m.cast.length > 0 && <p className="credit"><b>Cast:</b> {m.cast.join(", ")}</p>}
              </div>
            </div>

            <h3 className="similar-title">Similar movies</h3>
            <div className="grid small">
              {data.similar.map((s) => (
                <MovieCard key={s.id} movie={s} onOpen={onOpen} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
