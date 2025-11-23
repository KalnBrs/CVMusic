const pool = require('../Config/db')

const findSongId = async (req, res, next, value) => {
  try {
    const result = await pool.query('SELECT * FROM songs WHERE song_id = $1', [value])
    if (result.rows.length === 0) return res.sendStatus(404)
    req.song = result.rows[0]
    next()
  } catch (err) {
    console.log(err)
    res.sendStatus(500)
  }
}

const getAllSongs = async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM songs;')
    if (result.rows.length === 0) return res.status(404).send(' No Games ')
    res.json(result.rows[0])
  } catch {
    res.sendStatus(500)
  }
}

export { getAllSongs, findSongId }