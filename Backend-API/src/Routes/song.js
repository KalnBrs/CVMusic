const express = require('express');
const { getAllSongs, findSongId } = require('../Controllers/songControlers');

const router = express.Router();
router.use(express.json())

router.get('/', getAllSongs)

router.param('id', findSongId) // Find the id

router.get('/:id', (req, res) => {
  res.json(req.song)
})

// router.post('/', ) // Create a song

module.exports = router;