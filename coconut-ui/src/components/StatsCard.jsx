function StatsCard({ market, min, max, avg, weekly }) {
  return (
    <div style={{ width: "260px", padding: "18px", border: "1px solid #ddd", borderRadius: "12px" }}>
      <h3>{market}</h3>
      <p>Min: {min}</p>
      <p>Max: {max}</p>
      <p>Avg: {avg}</p>
      <p>Weekly: {weekly}</p>
    </div>
  );
}

export default StatsCard;
