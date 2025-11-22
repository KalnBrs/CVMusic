import { useState } from 'react'
import './App.css'

import LandingPage from './pages/LandingPage/LandingPage.jsx';
import SongPage from './pages/SongPage/SongPage.jsx';

import NavBar from './Components/NavBar/index.jsx'

import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';


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

        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
