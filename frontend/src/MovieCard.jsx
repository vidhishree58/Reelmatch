export default function MovieCard({ movie, onOpen }) {
  return (
    <button className="card" onClick={() => onOpen(movie.id)} aria-label={`${movie.title} kholo`}>
      <div className="poster">
        {movie.poster ? (
          <img src={movie.poster} alt="" loading="lazy" />
        ) : (
          <div className="no-poster">{movie.title}</div>
        )}
        <span className="rating">★ {movie.rating}</span>
      </div>
      <div className="meta">
        <strong>{movie.title}</strong>
        <span>{movie.year}</span>
      </div>
    </button>
  );
}
