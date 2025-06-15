
const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

// Ruta para testear conexión con microservicio Python
app.post('/api/sentiment/reddit', async (req, res) => {
  const fetch = require('node-fetch');
  try {
    const response = await fetch('http://localhost:5000/sentiment/reddit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body)
    });
    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: 'Error comunicando con microservicio' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Backend Express escuchando en puerto ${PORT}`);
});
