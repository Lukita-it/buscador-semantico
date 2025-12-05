import "./SearchBar.css";

export default function SearchBar({ query, setQuery, onSearch }) {
  return (
    <div className="search-container">
      <input
        className="search-input"
        placeholder="Busca una película: terror, comedia, romance, robots..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <button className="search-btn" onClick={onSearch}>
        Buscar
      </button>
    </div>
  );
}
