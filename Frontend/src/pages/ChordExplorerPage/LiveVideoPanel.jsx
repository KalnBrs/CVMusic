import { useRef, useEffect, useState } from "react";
import { captureAndSend } from "../../scripts/imageSend";

export default function LiveVideoPanel() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);
  const isSendingRef = useRef(false);

  const [testCounter, setCount] = useState(0)

  const [capturedImage, setCapturedImage] = useState(null);
  const [isActive, setIsActive] = useState(false);
  const [status, setStatus] = useState("Idle");
  const FPS = 3; // throttled frames per second

  // Initialize webcam
  useEffect(() => {
    let localStream = null;
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        localStream = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }
      })
      .catch(err => console.error("Camera error:", err));

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (localStream) localStream.getTracks().forEach(track => track.stop());
    };
  }, []);

  const startSending = () => {
    if (intervalRef.current) return; // already running
    setIsActive(true);
    intervalRef.current = setInterval(async () => {
      if (isSendingRef.current) return; // skip if previous frame still processing
      isSendingRef.current = true;
      setStatus("Sending...");
      try {
        const response = await captureAndSend(videoRef, canvasRef, setCapturedImage);
        if (response?.status === 200) {
          setStatus("Received ✅");
          setCount(testCounter + 1)
        } else {
          setStatus("Error ❌");
        }
      } catch (err) {
        console.error("Error sending frame:", err);
        setStatus("Error ❌");
      } finally {
        isSendingRef.current = false;
      }
    }, 1000 / FPS);
  };

  const pauseSending = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsActive(false);
    setStatus("Idle");
  };

  return (
    <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-md border border-[#D4EEF7]">
      <h2 className="text-2xl font-semibold text-[#1F8AAD] mb-4 text-center">
        Live Guitar View
      </h2>

      <div className="w-full aspect-video overflow-hidden rounded-xl bg-[#A8DEF0] relative">
        <video
          ref={videoRef}
          className="w-full h-full object-cover"
          style={{ transform: "scaleX(-1)" }}
          autoPlay
          muted
        />
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>

      {/* Status text */}
      <p className="mt-2 text-center text-gray-700 font-medium">
        Status: <span className="font-bold text-[#1F8AAD]">{status}</span>
      </p>

      <div className="mt-4 text-center space-x-4">
        {!isActive ? (
          <button
            onClick={startSending}
            className="bg-[#1F8AAD] hover:bg-[#1A7790] text-white font-bold py-2 px-4 rounded"
          >
            Start
          </button>
        ) : (
          <button
            onClick={pauseSending}
            className="bg-[#FF6B6B] hover:bg-[#E55B5B] text-white font-bold py-2 px-4 rounded"
          >
            Pause
          </button>
        )}
      </div>
      <p>{testCounter}</p>

      {capturedImage && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold text-[#1F8AAD] mb-2 text-center">
            Last Captured Frame
          </h3>
          <img
            src={capturedImage}
            alt="Captured frame"
            className="w-full rounded-xl shadow-md"
            onLoad={() => URL.revokeObjectURL(capturedImage)}
          />
        </div>
      )}
    </div>
  );
}
