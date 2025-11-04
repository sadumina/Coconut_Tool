import { BrowserRouter, Routes, Route } from "react-router-dom";
import UploadPage from "./pages/UploadPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import ComparePage from "./pages/ComparePage.jsx";
import SettingsPage from "./pages/SettingsPage.jsx";   // ✅ MUST have .jsx

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/compare" element={<ComparePage />} />
        <Route path="/settings" element={<SettingsPage />} /> {/* ✅ */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
