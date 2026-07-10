export default function Loading() {
  return (
    <div className="stack" aria-busy="true" aria-live="polite">
      <div className="skeleton skeleton-title" />
      <section className="grid cols-4">
        <div className="card skeleton-card" />
        <div className="card skeleton-card" />
        <div className="card skeleton-card" />
        <div className="card skeleton-card" />
      </section>
      <div className="card skeleton-block" />
    </div>
  );
}
