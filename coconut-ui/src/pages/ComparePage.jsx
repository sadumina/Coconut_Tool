import { useState, useEffect } from "react";
import MarketComparison from "../components/MarketComparison";
import axios from "axios";

function ComparePage() {
  const [markets] = useState(["Sri Lanka", "India"]);
  const [period] = useState("2025-01");
  const [data, setData] = useState([]);

  useEffect(() => {
    Promise.all(
      markets.map((market) =>
        axios.get(`http://localhost:8000/prices?market=${market}&period=${period}`)
      )
    ).then((responses) => {
      const merged = responses.map((res, i) => ({
        market: markets[i],
        ...res.data,
      }));
      setData(merged);
    });
  }, [markets, period]);

  return (
    <div style={{ padding: "40px" }}>
      <h1>📈 Compare Market Prices</h1>
      <MarketComparison data={data} />
    </div>
  );
}

export default ComparePage;
