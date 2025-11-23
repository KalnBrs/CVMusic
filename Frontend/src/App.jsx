import { useState } from 'react'
import './App.css'

import LandingPage from './pages/LandingPage/LandingPage.jsx';
import SongPage from './pages/SongPage/SongPage.jsx';
import CamSetup from './pages/CamSetup/CamSetup.jsx';

import NavBar from './Components/NavBar/index.jsx'

import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import PlayingPage from './pages/PlayingPage/PlayingPage.jsx';
import ChordExplorerPage from './pages/ChordExplorerPage/ChordExplorerPage.jsx';
import CameraSetupChordsPage from './pages/CamSetupChords/CamSetupChords.jsx';


function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <NavBar />
      <div className='w-full h-10 bg-[#D4EEF7]'></div>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/song-select" element={<SongPage />} />
          <Route path="/cam" element={<CamSetup />}/>
          <Route path="/cam-chords" element={<CameraSetupChordsPage />}/>

          <Route path="/sheet-view" element={<PlayingPage />}/>
          <Route path="/chords" element={<ChordExplorerPage />}/>

        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
