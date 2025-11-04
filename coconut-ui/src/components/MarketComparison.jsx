function MarketComparison({ data }) {
  return (
    <table border="1" cellPadding="10" style={{ marginTop: "30px" }}>
      <thead>
        <tr>
          <th>Market</th>
          <th>Min</th>
          <th>Max</th>
          <th>Average</th>
          <th>Weekly Trend</th>
        </tr>
      </thead>
      <tbody>
        {data.map((market, index) => (
          <tr key={index}>
            <td>{market.market}</td>
            <td>{market.periodMin}</td>
            <td>{market.periodMax}</td>
            <td>{market.periodAvg}</td>
            <td>{market.weeklyPrice}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default MarketComparison;
