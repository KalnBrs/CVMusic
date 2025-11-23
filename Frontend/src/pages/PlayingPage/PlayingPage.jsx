import { useRef, useState, useEffect } from "react";
import { useParams } from 'react-router-dom';
import { getSongCords } from "../../scripts/songs";
import FretboardDiagram from "../ChordExplorerPage/FretboardDiagram";

export default function PlayingPage({ song }) {
  const { id } = useParams();

  const videoRef = useRef(null);
  const overlayRef = useRef(null);

  const [paused, setPaused] = useState(true);
  const [loading, setLoading] = useState(false);
  const [chords, setChords] = useState([]);
  const [currentChordIndex, setCurrentChordIndex] = useState(0);
  const [fingerPositions, setFingerPositions] = useState([]);
  const [error, setError] = useState(null);
  const [currentTime, setCurrentTime] = useState(0); // track song time in beats
  const intervalRef = useRef(null);

  // Start camera
  const getVideo = async () => {
    setLoading(true);
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 360 },
      });
      const video = videoRef.current;
      if (!video) throw new Error("Video element not ready");
      video.srcObject = stream;
      await video.play();
    } catch (err) {
      console.error(err);
      // setError("Unable to access camera.");
    } finally {
      setLoading(false);
    }
  };

  // Fetch song chords
  useEffect(() => {
    getVideo();

    async function init() {
      try {
        const res = await getSongCords(id);
        setChords(res || []);
        if (res?.length > 0) {
          setFingerPositions(res[0].exact_notes || []);
        }
      } catch (err) {
        console.error(err);
        setError("Failed to load chords");
      }
    }
    init();
  }, [id]);

  // Draw finger positions on camera overlay
  useEffect(() => {
    const canvas = overlayRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const drawOverlay = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      fingerPositions.forEach(pos => {
        ctx.fillStyle = "rgba(255,0,0,0.6)";
        ctx.beginPath();
        ctx.arc(pos.x || 0, pos.y || 0, 12, 0, Math.PI * 2);
        ctx.fill();
      });
      requestAnimationFrame(drawOverlay);
    };

    drawOverlay();
  }, [fingerPositions]);

  // Update current chord based on currentTime
  useEffect(() => {
    if (!paused && chords.length > 0) {
      intervalRef.current = setInterval(() => {
        setCurrentTime(prev => prev + 1); // increment 1 beat per second
      }, 1000);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [paused, chords]);

  // Update chord index when currentTime changes
  useEffect(() => {
    if (!chords || chords.length === 0) return;

    // Find the chord whose beat_time is <= currentTime
    let index = chords.findIndex((chord, i) => {
      const nextChord = chords[i + 1];
      return chord.beat_time <= currentTime && (!nextChord || currentTime < nextChord.beat_time);
    });
    if (index === -1) index = chords.length - 1; // fallback to last chord

    setCurrentChordIndex(index);
    setFingerPositions(chords[index]?.exact_notes || []);
  }, [currentTime, chords]);

  // Manual step forward/back
  const nextChord = () => {
    if (!chords || chords.length === 0) return;
    const nextIndex = (currentChordIndex + 1) % chords.length;
    setCurrentChordIndex(nextIndex);
    setFingerPositions(chords[nextIndex].exact_notes || []);
    setCurrentTime(chords[nextIndex].beat_time || currentTime);
  };

  const prevChord = () => {
    if (!chords || chords.length === 0) return;
    const prevIndex = (currentChordIndex - 1 + chords.length) % chords.length;
    setCurrentChordIndex(prevIndex);
    setFingerPositions(chords[prevIndex].exact_notes || []);
    setCurrentTime(chords[prevIndex].beat_time || currentTime);
  };

  // Map exact_notes to FretboardDiagram tab
  const tab = Array(6).fill("0"); // default open strings
  fingerPositions.forEach(pos => {
    if (pos.string >= 1 && pos.string <= 6) {
      const index = 6 - pos.string; // reverse to match FretboardDiagram string order
      tab[index] = pos.fret.toString();
    }
  });

  return (
    <div className="min-h-screen bg-[#E9F7FB] px-6 py-10 flex flex-col items-center">
      <h1 className="text-4xl font-bold text-[#1F8AAD] mb-6 text-center">
        {song?.name || "Playing"}
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 w-full">
        {/* Camera */}
        <div className="bg-white rounded-2xl shadow-md border border-[#D4EEF7] p-4 flex items-center justify-center flex-col relative">
          <video
            ref={videoRef}
            className="w-full h-full object-cover rounded-xl"
            style={{ transform: "scaleX(-1)" }}
          />
          <canvas
            ref={overlayRef}
            className="absolute top-0 left-0 w-full h-full pointer-events-none"
          />
          {loading && <p className="absolute text-[#1F8AAD] font-bold text-lg">Loading Camera...</p>}
          {error && <p className="absolute text-red-500 font-bold">{error}</p>}
        </div>

        {/* Fingerboard */}
        <div className="bg-white rounded-2xl shadow-md border border-[#D4EEF7] p-6 flex flex-col items-center">
          <h2 className="text-2xl font-semibold text-[#1F8AAD] mb-4">Fingerboard</h2>
          <FretboardDiagram diagram={fingerPositions} tab={tab} />
          <div className="mt-6 flex justify-center items-center gap-4">
            <button onClick={prevChord} className="px-4 py-2 bg-gray-200 rounded-full">⬅</button>
            <button onClick={() => setPaused(!paused)} className="px-4 py-2 bg-blue-400 text-white rounded-full">
              {paused ? "Play" : "Pause"}
            </button>
            <button onClick={nextChord} className="px-4 py-2 bg-gray-200 rounded-full">➡</button>
          </div>
          <p className="mt-3 text-[#7BAFBE] text-lg font-semibold">
            Current Chord: {chords[currentChordIndex]?.chord_name || "N/A"}
          </p>
          <p className="text-[#7BAFBE] text-sm mt-1">
            Beat Time: {chords[currentChordIndex]?.beat_time ?? currentTime}
          </p>
        </div>
      </div>
    </div>
  );
}
