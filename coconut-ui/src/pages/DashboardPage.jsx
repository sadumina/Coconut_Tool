import { useEffect, useState } from "react";
import StatsCard from "../components/StatsCard";
import PriceChart from "../components/PriceChart";
import axios from "axios";
import { Link } from "react-router-dom";

function DashboardPage() {
  const [marketData, setMarketData] = useState([]);

  useEffect(() => {
  const markets = ["Sri Lanka", "India", "Indonesia", "Thailand"];

  Promise.all(
    markets.map((market) =>
      axios.get(
        `http://localhost:8000/analytics?product=Coconut Shell Charcoal&market=${market}`
      )
    )
  )
    .then((responses) => {
      const formatted = responses.map((res) => ({
        market: res.data.market,
        min: res.data.min,
        max: res.data.max,
        avg: res.data.avg,
        weekly: res.data.latest_price,
      }));
      setMarketData(formatted);
    })
    .catch((err) => console.error("❌ API Error:", err));
}, []);


  return (
    <div style={{ padding: "40px" }}>
      <h1>📊 Coconut Price Dashboard</h1>
      <p>Overview: Min / Max / Average / Weekly Trend</p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "20px", marginTop: "20px" }}>
        {marketData.map((market, index) => (
          <StatsCard
            key={index}
            market={market.market}
            min={market.periodMin}
            max={market.periodMax}
            avg={market.periodAvg}
            weekly={market.weeklyPrice}
          />
        ))}
      </div>

      <PriceChart data={marketData} />

      <Link to="/compare">
        <button style={{ marginTop: "30px", padding: "12px 20px" }}>
          📈 Compare Markets →
        </button>
      </Link>
    </div>
  );
}

export default DashboardPage;
