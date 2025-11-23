import { useRef, useEffect } from "react";

export default function LiveVideoPanel() {
  const videoRef = useRef(null);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }
      })
      .catch(err => console.error("Camera error:", err));
  }, []);

  return (
    <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-md border border-[#D4EEF7] h-150">
      <h2 className="text-2xl font-semibold text-[#1F8AAD] mb-4 text-center">
        Live Guitar View
      </h2>

      <div className="w-full aspect-video overflow-hidden rounded-xl bg-[#A8DEF0]">
        <video
          ref={videoRef}
          className="w-full h-full object-cover"
          style={{ transform: "scaleX(-1)" }}
        />
      </div>
    </div>
  );
}
