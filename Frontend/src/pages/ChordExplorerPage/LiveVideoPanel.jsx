import { useRef, useEffect, useState } from "react";
import { captureAndSend } from "../../scripts/imageSend";

export default function LiveVideoPanel({ currCord }) {
  const videoRef = useRef(null);
  const overlayRef = useRef(null); // visible overlay canvas used to draw points
  const captureRef = useRef(null); // hidden capture canvas used by captureAndSend
  const intervalRef = useRef(null);
  const isSendingRef = useRef(false);
  const streamRef = useRef(null); // keep stream to stop on unmount

  const [currSpots, setCurrSpots] = useState([]); // always an array for easier drawing
  const [currCorners, setCurrCorners] = useState({}); // object with TL, TR, BL, BR
  const [capturedImage, setCapturedImage] = useState(null);
  const [isActive, setIsActive] = useState(false);
  const [status, setStatus] = useState("Idle");
  const [frameCount, setFrameCount] = useState(0);

  const FPS = 5; // throttled frames per second

  // --- Initialize webcam safely ---
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
        if (!video) return;
        if (video.srcObject !== stream) {
          video.srcObject = stream;
          video.onloadedmetadata = () => {
            const p = video.play();
            if (p && typeof p.catch === "function") {
              p.catch((err) => {
                if (err?.name !== "AbortError") console.warn("Video play error:", err);
              });
            }
          };
        }
      } catch (err) {
        console.error("Camera error:", err);
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

  // --- Resize overlay canvas whenever video size changes ---
  useEffect(() => {
    function resizeOverlay() {
      const video = videoRef.current;
      const overlay = overlayRef.current;
      if (!video || !overlay) return;
      overlay.width = video.videoWidth || overlay.clientWidth;
      overlay.height = video.videoHeight || overlay.clientHeight;
    }

    const v = videoRef.current;
    if (v) v.addEventListener("loadedmetadata", resizeOverlay);
    window.addEventListener("resize", resizeOverlay);
    resizeOverlay();

    return () => {
      if (v) v.removeEventListener("loadedmetadata", resizeOverlay);
      window.removeEventListener("resize", resizeOverlay);
    };
  }, []);

  // --- Draw currSpots and currCorners on overlay ---
  useEffect(() => {
    const overlay = overlayRef.current;
    const video = videoRef.current;
    if (!overlay || !video) return;

    overlay.width = video.videoWidth || overlay.clientWidth || 640;
    overlay.height = video.videoHeight || overlay.clientHeight || 480;

    const ctx = overlay.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, overlay.width, overlay.height);

    // Draw notes
    if (Array.isArray(currSpots)) {
      currSpots.forEach((spot) => {
        let x = null, y = null;
        if (Array.isArray(spot) && spot.length >= 2) [x, y] = spot;
        else if (spot && typeof spot === "object") x = spot.x ?? spot.X ?? spot[0], y = spot.y ?? spot.Y ?? spot[1];
        if (x == null || y == null || Number.isNaN(x) || Number.isNaN(y)) return;

        const radius = Math.max(6, Math.round(Math.min(overlay.width, overlay.height) * 0.012));
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(255, 70, 70, 0.9)";
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
    }

    // Draw corners
    if (currCorners && typeof currCorners === "object") {
      Object.values(currCorners).forEach((corner) => {
        if (!corner) return;
        const x = corner.x ?? corner.X ?? corner[0];
        const y = corner.y ?? corner.Y ?? corner[1];
        if (x == null || y == null || Number.isNaN(x) || Number.isNaN(y)) return;

        const radius = Math.max(6, Math.round(Math.min(overlay.width, overlay.height) * 0.012));
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(70, 255, 70, 0.9)";
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = "white";
        ctx.stroke();
      });
    }
  }, [currSpots, currCorners]);

  // --- Start sending frames ---
  const startSending = () => {
    if (intervalRef.current) return;
    setIsActive(true);
    setStatus("Sending...");

    intervalRef.current = setInterval(async () => {
      if (isSendingRef.current) return;
      isSendingRef.current = true;
      setStatus("Sending...");

      try {
        if (!videoRef.current || !captureRef.current) {
          setStatus("Idle");
          return;
        }

        const response = await captureAndSend(videoRef, captureRef, setCapturedImage, currCord);
        if (!response) {
          setStatus("Error ❌");
          return;
        }

        if (response.status === 200) {
          setStatus("Received ✅");
          let data = null;
          try {
            data = await response.json();
          } catch (err) {
            console.warn("Failed to parse JSON:", err);
          }

          if (!data) {
            setCurrSpots([]);
            setCurrCorners({});
          } else if (Array.isArray(data)) {
            setCurrSpots(data);
            setCurrCorners({});
          } else {
            setCurrSpots(data.notes ?? []);
            setCurrCorners(data.corners ?? {});
          }

          setFrameCount((c) => c + 1);
        } else {
          setStatus("Error ❌");
        }
      } catch (err) {
        console.error("Error sending frame:", err);
        setStatus("Error ❌");
      } finally {
        isSendingRef.current = false;
      }
    }, Math.round(1000 / FPS));
  };

  const pauseSending = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    isSendingRef.current = false;
    setIsActive(false);
    setStatus("Idle");
  };

  // --- Cleanup captured image URL ---
  useEffect(() => {
    return () => {
      if (capturedImage && typeof capturedImage === "string") {
        try { URL.revokeObjectURL(capturedImage); } catch (_) {}
      }
    };
  }, [capturedImage]);

  return (
    <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-md border border-[#D4EEF7]">
      <h2 className="text-2xl font-semibold text-[#1F8AAD] mb-4 text-center">Live Guitar View</h2>

      <div className="w-full aspect-video overflow-hidden rounded-xl bg-[#A8DEF0] relative">
        <video
          ref={videoRef}
          className="w-full h-full object-cover"
          style={{ transform: "scaleX(-1)" }}
          autoPlay
          muted
          playsInline
        />
        <canvas ref={captureRef} style={{ display: "none" }} />
        <canvas
          ref={overlayRef}
          className="absolute top-0 left-0 w-full h-full pointer-events-none"
          style={{ transform: "scaleX(-1)" }}
        />
      </div>

      <div className="flex flex-row justify-center gap-4 mt-3">
        <p className="mt-2 text-center text-gray-700 font-medium">
          Status: <span className="font-bold text-[#1F8AAD]">{status}</span>
        </p>
        <p className="mt-2 text-center text-gray-700 font-medium">
          Current Cord:{" "}
          <span className="font-bold text-[#1F8AAD]">
            {currCord?.name ?? "N/A"} - {currCord?.variation ?? "N/A"}
          </span>
        </p>
        <p className="mt-2 text-center text-gray-700 font-medium">
          Frames: <span className="font-bold text-[#1F8AAD]">{frameCount}</span>
        </p>
      </div>

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

      {capturedImage && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold text-[#1F8AAD] mb-2 text-center">Last Captured Frame</h3>
          <img
            src={capturedImage}
            alt="Captured frame"
            className="w-full rounded-xl shadow-md"
            onLoad={() => { try { URL.revokeObjectURL(capturedImage); } catch (_) {} }}
            style={{ transform: "scaleX(-1)" }}
          />
        </div>
      )}
    </div>
  );
}
