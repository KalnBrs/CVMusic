const express = require('express');
const cors = require('cors');
const multer = require('multer');
const axios = require('axios');
const Busboy = require('busboy');
const fs = require('fs');
const app = express();
const FormData = require('form-data');
const { Readable } = require('stream');

app.use(express.json())
app.use(cors({
  origin: '*',
  credentials: true,
}))

// const songRoute = require('./Routes/song')
// const chordRoute = require('./Routes/chord')

app.get('/', (req, res) => {
  res.send('Welcome to the API')
})

const upload = multer({ storage: multer.memoryStorage() });

app.post('/analyze-frame', (req, res) => {
  const busboy = Busboy({ headers: req.headers });
  let fileBuffer = Buffer.alloc(0);
  let filename = '';

  busboy.on('file', (fieldname, file, info) => {
    filename = info.filename;

    file.on('data', (chunk) => {
      fileBuffer = Buffer.concat([fileBuffer, chunk]);
    });

    file.on('end', () => {
      console.log(`Received file: ${filename} (${fileBuffer.length} bytes)`);
    });
  });

  busboy.on('finish', async () => {
    try {
      // Wrap buffer in readable stream
      const { Readable } = require('stream');
      const stream = Readable.from(fileBuffer);

      // Prepare form-data for Python API
      const formData = new FormData();
      formData.append('file', stream, { filename });

      // Send to Python API
      const response = await axios.post(
        'http://localhost:8000/analyze-frame',
        formData,
        { headers: formData.getHeaders() }
      );

      res.json(response.data);
    } catch (err) {
      console.error(err);
      res.status(500).send('Error sending frame to Python API');
    }
  });

  req.pipe(busboy);
});

module.exports = app