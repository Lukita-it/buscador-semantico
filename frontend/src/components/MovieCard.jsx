import ProvidersTag from "./ProvidersTag";
import "./MovieCard.css";

export default function MovieCard({ movie, onTrailer }) {
  return (
    <div className="movie-card">

      <div className="poster-wrapper">
        {movie.poster ? (
          <img src={movie.poster} alt={movie.title_es} className="poster" />
        ) : (
          <div className="poster placeholder">Sin póster</div>
        )}
      </div>

      <div className="movie-info">
        <h3>{movie.title_es}</h3>
        <p className="genre">{movie.genre_es}</p>
        <p className="desc">{movie.description_es}</p>

        <ProvidersTag providers={movie.providers_es} />

        <button className="trailer-btn" onClick={onTrailer}>
          ▶ Ver Trailer
        </button>
      </div>

    </div>
  );
}
