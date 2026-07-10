function barClass(value: number) {
  if (value >= 78) return "high";
  if (value >= 55) return "medium";
  return "low";
}

export function ScoreBreakdown({ rows }: { rows: Array<{ label: string; value: number }> }) {
  return (
    <div className="score-bars">
      {rows.map((row) => {
        const value = Math.round(row.value);
        return (
          <div className="score-bar-row" key={row.label}>
            <span className="score-bar-label">{row.label}</span>
            <span className="score-bar-track">
              <span className={`score-bar-fill ${barClass(value)}`} style={{ width: `${Math.max(2, Math.min(100, value))}%` }} />
            </span>
            <span className="score-bar-value">{value}</span>
          </div>
        );
      })}
    </div>
  );
}
