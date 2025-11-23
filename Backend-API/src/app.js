const cors = require('cors')
const express = require('express');
const app = express();

app.use(express.json())
app.use(cors({
  origin: '*',
  credentials: true,
}))

const songRoute = require('./Routes/song')
const chordRoute = require('./Routes/chord')

app.get('/', (req, res) => {
  res.send('Welcome to the API')
})

app.post('/analyze-frame', (req, res) => {
  // calls the cord analyze
})

module.exports = app