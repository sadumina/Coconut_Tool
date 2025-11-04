import { useState } from "react";
import FileUploader from "../components/FileUploader";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function UploadPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async (file) => {
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);   // ✅ must match backend


    try {
      const res = await axios.post("http://localhost:8000/upload-pdf", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      localStorage.setItem("parsedData", JSON.stringify(res.data));
      navigate("/dashboard");

    // eslint-disable-next-line no-unused-vars
    } catch (error) {
      alert("Upload failed ❌");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "40px" }}>
      <h1>📄 Upload PDF (2025 - 01)</h1>
      <p>Upload the monthly coconut price report.</p>

      <FileUploader onFileUpload={handleUpload} />

      {loading && <p>Processing PDF... Please wait ⏳</p>}
    </div>
  );
}

export default UploadPage;
