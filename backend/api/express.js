//File: backend/api/express.js

const express = require("express");
const axios = require("axios");

const app = express();
app.use(express.json());

app.post("/api/v1/text-adapter", async (req, res) => {
  const { texto, nivel } = req.body;
  try {
    const response = await axios.post("http://localhost:5001/api/adaptar-texto", { texto, nivel });
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: "Error al adaptar el texto", details: error.message });
  }
});

const PORT = 5000;
app.listen(PORT, () => {
  console.log(`Servidor Express escuchando en el puerto ${PORT}`);
});
