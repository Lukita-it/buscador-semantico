import { useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTrailer, setSelectedTrailer] = useState(null);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ q: query, k: 12 }),
      });

      const data = await res.json();
      setResults(data.results || []);
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div className="page">
      {/* --------- Search Section ---------- */}
      <div className="search-container">
        <h1 className="title">Buscador Semántico de Películas</h1>

        <div className="search-box">
          <input
            type="text"
            placeholder="Buscar películas por título, género, descripción..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && search()}
          />
          <button onClick={search}>Buscar</button>
        </div>
      </div>

      {/* --------- Results Section ---------- */}
      {loading ? (
        <p className="loading">Buscando...</p>
      ) : (
        <div className="cards-container">
          {results.map((movie, i) => (
            <div key={i} className="movie-card">
              <img
                className="poster"
                src={movie.poster || "https://via.placeholder.com/350x500?text=No+Image"}
                alt={movie.title_es}
              />

              <div className="movie-info">
                <h2>{movie.title_es}</h2>
                <p><strong>Género:</strong> {movie.genre_es}</p>
                <p><strong>Año:</strong> {movie.year}</p>
                <p><strong>Director:</strong> {movie.director_es}</p>
                <p><strong>Actores:</strong> {movie.actors_es}</p>

                <p className="description">{movie.description_es}</p>

                {/* --- AQUÍ ESTÁ EL CAMBIO --- */}
                <div className="watch-on">
                  <strong>Disponible en:</strong>
                  {/* Verificamos que exista array, tenga datos y NO sea el mensaje de error "No disponible" */}
                  {movie.watch_on && 
                   movie.watch_on.length > 0 && 
                   movie.watch_on[0] !== "No disponible" ? (
                    <ul className="platform-list">
                      {movie.watch_on.map((plataforma, idx) => (
                        <li key={idx} className="platform-badge">
                          {plataforma}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <span className="watch-none"> No disponible en plataformas digitales.</span>
                  )}
                </div>
                {/* --------------------------- */}

                {/* Trailer Button (sin cambios) */}
                {movie.trailer_id ? (
                  <button
                    className="trailer-btn"
                    onClick={() => setSelectedTrailer(movie.trailer_id)}
                  >
                    Ver Trailer 🎬
                  </button>
                ) : (
                  <p className="notrailer">Trailer no disponible</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* -------- Trailer Modal ---------- */}
      {selectedTrailer && (
        <div className="modal" onClick={() => setSelectedTrailer(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <iframe
              width="100%"
              height="100%"
              src={`https://www.youtube.com/embed/${selectedTrailer}`}
              title="Trailer"
              allowFullScreen
            ></iframe>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
