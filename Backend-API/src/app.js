const cors = require('cors')
const express = require('express');
const app = express();

app.use(express.json())
app.use(cors({
  origin: 'https://snap-stat.vercel.app/',
  credentials: true,
}))

app.get('/', (req, res) => {
  res.send('Welcome to the API')
})

module.exports = app