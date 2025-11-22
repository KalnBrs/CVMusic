import { useRef, useState, useEffect } from "react";

export default function PlayingPage({ song }) {
  const videoRef = useRef(null);
  const overlayRef = useRef(null);

  const [paused, setPaused] = useState(false)

  const [cameraStatus, setCameraStatus] = useState("Not Connected");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Example: finger positions from backend (x, y on canvas)
  const [fingerPositions, setFingerPositions] = useState([]);

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
      setCameraStatus("Connected");
    } catch (err) {
      console.error(err);
      setError("Unable to access camera.");
      setCameraStatus("Error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getVideo();
  }, []);

  // Example: overlay drawing function
  useEffect(() => {
    const canvas = overlayRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const drawOverlay = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      fingerPositions.forEach(pos => {
        ctx.fillStyle = "rgba(255,0,0,0.6)";
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 12, 0, Math.PI * 2);
        ctx.fill();
      });

      requestAnimationFrame(drawOverlay);
    };

    drawOverlay();
  }, [fingerPositions]);

  return (
    <div className="min-h-screen bg-[#E9F7FB] px-6 py-10 flex flex-col items-center">
      <h1 className="text-4xl font-bold text-[#1F8AAD] mb-6 text-center">
        {song?.name || "Playing"} 
      </h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 w-full">
        <div className="bg-white rounded-2xl shadow-md border border-[#D4EEF7] p-4 flex items-center justify-center flex-col">
          <video
            ref={videoRef}
            className="w-full h-full object-cover rounded-xl"
            style={{ transform: "scaleX(-1)" }}
          />
          <canvas
            ref={overlayRef}
            className="absolute top-0 left-0 w-full h-full pointer-events-none"
          />
          {loading && (
            <p className="absolute text-[#1F8AAD] font-bold text-lg">Loading Camera...</p>
          )}
        </div>

        <div className="bg-white rounded-2xl shadow-md border border-[#D4EEF7] p-6 flex flex-col">
          <h2 className="text-2xl font-semibold text-[#1F8AAD] mb-4">
            Sheet Music
          </h2>

          <div className="bg-[#A8DEF0] rounded-xl flex-1 p-4 overflow-auto">
            <p className="text-[#7BAFBE] text-center">[Music sheet will display here]</p>
          </div>

          <div className="mt-6 flex justify-center items-center">
            <button className="px-6 py-3 bg-gradient-to-r from-[#26ACD9] to-[#00D4FF] text-white rounded-full hover:opacity-90 active:scale-95 transition-all" style={{ transform: "scaleX(-1)" }}>
              <img src="/fast-forward.png" alt="" className="w-5 h-5" />
            </button>
            <button onClick={() => setPaused(!paused)} className="px-6 py-3 text-white rounded-full hover:scale-[1.05] active:scale-95 transition-all">
              {paused ? (<img src="/pause.png" className="w-5 h-5" />) : (<img src="/play-button-arrowhead.png" className="w-5 h-5" />)}
              {/* Play and pause  */}
            </button>
            <button className="px-6 py-3 bg-gradient-to-r from-[#26ACD9] to-[#00D4FF] text-white rounded-full shadow-lg hover:opacity-90 active:scale-95 transition-all">
              <img src="/fast-forward.png" alt="" className="w-5 h-5" />
            </button>
          </div>
          <div className="flex flex-row justify-center items-center gap-2 mt-3">
            <button className="py-3  text-white rounded-full  hover:scale-[1.1] active:scale-95 transition-all">
              <p className="text-black text-2xl">⬅</p>
            </button>
            <p>Step</p>
            <button className="py-3 text-white rounded-full hover:scale-[1.1] active:scale-95 transition-all">
              <p className="text-black text-2xl" style={{transform: "scaleX(-1)"}}>⬅</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
