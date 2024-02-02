"use client"
import React, { useState, useEffect } from 'react';

const ImageUpload = () => {
  const [selectedFile, setSelectedFile] = useState();
  const [previewUrl, setPreviewUrl] = useState();
  const [objectData, setObjectData] = useState([]);

  const submitHandler = async (event) => {
    event.preventDefault();

    const formData = new FormData();
    formData.append('file', selectedFile);

    const response = await fetch('http://localhost:8001/detection/img_object_detection_to_img', {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const contentImage = await response.blob();
      setPreviewUrl(URL.createObjectURL(contentImage));
      console.log('Imagen subida con éxito');
    } else {
      console.error('Error al subir la imagen');
    }
  };

  const fetchObjectData = async () => {
    const response = await fetch('http://localhost:8001/detection/img_object_detection_to_json');
    if (response.ok) {
      const data = await response.json();
      setObjectData(data.detect_objects);
    } else {
      console.error('Error al obtener los datos del objeto');
    }
  };

  useEffect(() => {
    fetchObjectData();
  }, []);

  const fileChangeHandler = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  return (
    <div className="container mx-auto">
      <form onSubmit={submitHandler}>
        <input type="file" onChange={fileChangeHandler} />
        {previewUrl && <img src={previewUrl} alt="Preview" />}
        <button type="submit">Subir imagen</button>
      </form>

      <div className="mt-4">
        <h2 className="text-xl font-bold">Object Data:</h2>
        <ul>
          {objectData.map((object, index) => (
            <li key={index}>
              Name: {object.name}, Confidence: {object.confidence}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ImageUpload;