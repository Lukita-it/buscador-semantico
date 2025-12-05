import "./ProvidersTag.css";

export default function ProvidersTag({ providers }) {
  if (!providers) return null;

  const list = providers.split(",").map((p) => p.trim());

  return (
    <div className="providers-list">
      {list.map((p, idx) => (
        <span key={idx} className="provider-tag">
          {p}
        </span>
      ))}
    </div>
  );
}
