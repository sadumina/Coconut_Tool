function FileUploader({ onFileUpload }) {
  return (
    <div>
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => onFileUpload(e.target.files[0])}
      />
    </div>
  );
}

export default FileUploader;
