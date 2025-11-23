import { useRef, useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getSongCords } from "../../scripts/songs";
import FretboardDiagram from "../ChordExplorerPage/FretboardDiagram";
import { captureAndSend } from "../../scripts/imageSend";

export default function PlayingPage({ song }) {
  const { id } = useParams();

  const videoRef = useRef(null);
  const overlayRef = useRef(null);
  const captureRef = useRef(null);
  const intervalRef = useRef(null);
  const isSendingRef = useRef(false);
  const streamRef = useRef(null);

  const [paused, setPaused] = useState(true);
  const [loading, setLoading] = useState(false);
  const [chords, setChords] = useState([]);
  const [currentChordIndex, setCurrentChordIndex] = useState(0);
  const [currSpots, setCurrSpots] = useState([]);
  const [currCorners, setCurrCorners] = useState({});
  const [status, setStatus] = useState("Idle");
  const [frameCount, setFrameCount] = useState(0);
  const [error, setError] = useState(null);

  const FPS = 5;

  // --- Initialize camera ---
  useEffect(() => {
    let mounted = true;

    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (!mounted) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        const video = videoRef.current;
        if (video) {
          video.srcObject = stream;
          video.onloadedmetadata = () => video.play().catch(() => {});
        }
      } catch (err) {
        console.error("Camera error:", err);
        setError("Unable to access camera.");
      }
    }

    startCamera();
    return () => {
      mounted = false;
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }
    };
  }, []);

  // --- Fetch song chords ---
  useEffect(() => {
    setLoading(true);
    async function fetchChords() {
      try {
        const res = await getSongCords(id);
        setChords(res || []);
      } catch (err) {
        console.error(err);
        setError("Failed to load chords");
      } finally {
        setLoading(false);
      }
    }
    fetchChords();
  }, [id]);

  // --- Draw overlay ---
  useEffect(() => {
    const overlay = overlayRef.current;
    const video = videoRef.current;
    if (!overlay || !video) return;

    const drawOverlay = () => {
      overlay.width = video.videoWidth || overlay.clientWidth || 640;
      overlay.height = video.videoHeight || overlay.clientHeight || 480;

      const ctx = overlay.getContext("2d");
      if (!ctx) return;
      ctx.clearRect(0, 0, overlay.width, overlay.height);

      // Draw notes
      currSpots.forEach((spot) => {
        const x = spot?.x ?? spot?.X ?? spot?.[0];
        const y = spot?.y ?? spot?.Y ?? spot?.[1];
        if (x == null || y == null) return;

        const radius = Math.max(6, Math.round(Math.min(overlay.width, overlay.height) * 0.012));
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(255,70,70,0.9)";
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = "white";
        ctx.stroke();

        if (spot.label || spot.idx != null) {
          ctx.font = `${Math.max(12, Math.round(radius * 0.9))}px sans-serif`;
          ctx.fillStyle = "white";
          const label = spot.label ?? spot.idx ?? "";
          ctx.fillText(label, x + radius + 4, y + radius / 2);
        }
      });

      // Draw corners
      Object.values(currCorners).forEach((corner) => {
        if (!corner) return;
        const x = corner?.x ?? corner?.X ?? corner?.[0];
        const y = corner?.y ?? corner?.Y ?? corner?.[1];
        if (x == null || y == null) return;

        const radius = Math.max(6, Math.round(Math.min(overlay.width, overlay.height) * 0.012));
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(70,255,70,0.9)";
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = "white";
        ctx.stroke();
      });

      requestAnimationFrame(drawOverlay);
    };

    drawOverlay();
  }, [currSpots, currCorners]);

  // --- Capture and send frame ---
  const captureFrame = () => {
    const video = videoRef.current;
    const capture = captureRef.current;
    if (!video || !capture) return null;
    capture.width = video.videoWidth || 640;
    capture.height = video.videoHeight || 480;
    const ctx = capture.getContext("2d");
    ctx.drawImage(video, 0, 0, capture.width, capture.height);
    return capture;
  };

  const startSending = () => {
    if (intervalRef.current) return;
    setPaused(false);
    setStatus("Sending...");

    intervalRef.current = setInterval(async () => {
      if (isSendingRef.current) return;
      isSendingRef.current = true;

      try {
        const captureCanvas = captureFrame();
        if (!captureCanvas) return;

        const response = await captureAndSend(captureCanvas, chords[currentChordIndex]);
        if (!response || response.status !== 200) {
          setStatus("Error ❌");
          return;
        }

        const data = await response.json();
        setCurrSpots(data.notes ?? []);
        setCurrCorners(data.corners ?? {});
        setFrameCount((c) => c + 1);
        setStatus("Received ✅");
      } catch (err) {
        console.error(err);
        setStatus("Error ❌");
      } finally {
        isSendingRef.current = false;
      }
    }, Math.round(1000 / FPS));
  };

  const pauseSending = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = null;
    isSendingRef.current = false;
    setPaused(true);
    setStatus("Idle");
  };

  const nextChord = () => {
    const nextIndex = (currentChordIndex + 1) % chords.length;
    setCurrentChordIndex(nextIndex);
  };

  const prevChord = () => {
    const prevIndex = (currentChordIndex - 1 + chords.length) % chords.length;
    setCurrentChordIndex(prevIndex);
  };

  // Map notes to FretboardDiagram
  const tab = Array(6).fill("0");
  (currSpots || []).forEach((pos) => {
    if (pos.string >= 1 && pos.string <= 6) {
      tab[6 - pos.string] = pos.fret?.toString() ?? "0";
    }
  });

  return (
    <div className="min-h-screen bg-[#E9F7FB] px-6 py-10 flex flex-col items-center">
      <h1 className="text-4xl font-bold text-[#1F8AAD] mb-6 text-center">
        {song?.name || "Playing"}
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 w-full">
        {/* Camera */}
        <div className="bg-white rounded-2xl shadow-md border border-[#D4EEF7] p-4 flex flex-col items-center relative">
          <video
            ref={videoRef}
            className="w-full h-full object-cover rounded-xl"
            style={{ transform: "scaleX(-1)" }}
          />
          <canvas ref={captureRef} style={{ display: "none" }} />
          <canvas
            ref={overlayRef}
            className="absolute top-0 left-0 w-full h-full pointer-events-none"
            style={{ transform: "scaleX(-1)" }}
          />
          <div className="mt-4 flex gap-2">
            <button onClick={prevChord} className="px-4 py-2 bg-gray-200 rounded-full">⬅</button>
            <button onClick={paused ? startSending : pauseSending} className="px-4 py-2 bg-blue-400 text-white rounded-full">
              {paused ? "Play" : "Pause"}
            </button>
            <button onClick={nextChord} className="px-4 py-2 bg-gray-200 rounded-full">➡</button>
          </div>
          <p className="mt-2 text-[#7BAFBE] font-semibold">Status: {status}</p>
        </div>

        {/* Fingerboard */}
        <div className="bg-white rounded-2xl shadow-md border border-[#D4EEF7] p-6 flex flex-col items-center">
          <h2 className="text-2xl font-semibold text-[#1F8AAD] mb-4">Fingerboard</h2>
          <FretboardDiagram diagram={currSpots} tab={tab} />
          <p className="mt-3 text-[#7BAFBE] text-lg font-semibold">
            Current Chord: {chords[currentChordIndex]?.chord_name || "N/A"}
          </p>
        </div>
      </div>
    </div>
  );
}