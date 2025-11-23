const express = require('express');
const { findChordSongId } = require('../Controllers/songControlers');

const router = express.Router();
router.use(express.json())

router.param('id', findChordSongId) 

router.get('/:id', (req, res) => {
  res.json(req.chords)
})

module.exports = router;
