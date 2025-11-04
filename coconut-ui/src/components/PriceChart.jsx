import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";

function PriceChart({ data }) {
  return (
    <LineChart width={900} height={350} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="market" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="periodAvg" stroke="#0088FE" name="Average" />
      <Line type="monotone" dataKey="periodMin" stroke="#00C49F" name="Min" />
      <Line type="monotone" dataKey="periodMax" stroke="#FF8042" name="Max" />
    </LineChart>
  );
}

export default PriceChart;
