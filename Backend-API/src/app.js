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

const songRoute = require('./Routes/song')
app.use("/api/songs", songRoute)
// const chordRoute = require('./Routes/chord')

app.get('/', (req, res) => {
  res.send('Welcome to the API')
})

app.post('/analyze-frame', (req, res) => {
  const busboy = Busboy({ headers: req.headers });

  let fileBuffer = Buffer.alloc(0);
  let filename = '';
  let chordTab = null; // Will store chord tab from frontend

  // Handle files
  busboy.on('file', (fieldname, file, info) => {
    filename = info.filename;

    file.on('data', chunk => {
      fileBuffer = Buffer.concat([fileBuffer, chunk]);
    });

    file.on('end', () => {
      console.log(`Received file: ${filename} (${fileBuffer.length} bytes)`);
    });
  });

  // Handle fields
  busboy.on('field', (fieldname, val) => {
    if (fieldname === 'file') { // Make sure the frontend uses this key
      try {
        chordTab = JSON.parse(val); // Convert JSON string to array/object
        console.log("Received chord tab:", chordTab);
      } catch (err) {
        console.error("Invalid chord tab JSON:", val);
      }
    }
  });

  busboy.on('finish', async () => {
    try {
      const stream = Readable.from(fileBuffer);

      const formData = new FormData();
      formData.append('frame', stream, { filename });
      formData.append('chord_tab', JSON.stringify(chordTab)); // Use the received chord tab

      const response = await axios.post(
        'http://localhost:3000/api/process_frame',
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