import "./TrailerModal.css";

export default function TrailerModal({ videoId, onClose }) {
  if (!videoId) return null;

  const youtubeUrl = `https://www.youtube.com/embed/${videoId}`;

  return (
    <div className="modal-bg" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <iframe
          width="100%"
          height="400"
          src={youtubeUrl}
          title="YouTube Trailer"
          allowFullScreen
        />
        <button className="close-btn" onClick={onClose}>Cerrar</button>
      </div>
    </div>
  );
}
