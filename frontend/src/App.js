import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [uploadProgress, setUploadProgress] = useState(0);

  async function uploadFile(event) {
    event.preventDefault();
    const file = event.target.elements.file.files[0];
    const filename = file.name;
    const fileSize = file.size;
    const chunkSize = 80 * 1024 * 1024; // 100 MB
    const chunks = Math.ceil(fileSize / chunkSize);
    const url = "http://0.0.0.0:8000";


    const { data } = await axios.post(`${url}/initiate-upload?filename=${filename}`);
    const { upload_id: uploadId } = data;



    const parts = [];
    let offset = 0;
    for (let i = 0; i < chunks; i++) {
      const chunk = file.slice(offset, offset + chunkSize);
      parts.push(chunk);
      offset += chunkSize;
    }

    await Promise.all(parts.map(async (chunk, index) => {
      const formData = new FormData();
      formData.append("chunk", chunk);
      console.log(offset, 'as')
      return axios.post(`${url}/upload-chunk?filename=${filename}&chunk_number=${index}&upload_id=${uploadId}&chunks=${chunks}`, formData);
    }));



    await axios.post(`${url}/complete-upload?filename=${filename}&upload_id=${uploadId}`
  );
  setUploadProgress(100);
  }

  return (
    <form onSubmit={uploadFile}>
      <div className="form-group">
        <label htmlFor="fileUpload">Choose a file to upload:</label>
        <input
          type="file"
          id="fileUpload"
          name="file"
          className="form-control-file"
        />
      </div>
      <button type="submit" className="btn btn-primary">
        Upload
      </button>
      {uploadProgress > 0 && (
        <progress max="100" value={uploadProgress} className="mt-2" />
      )}
    </form>
  );
}

export default App;