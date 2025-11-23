import { useRef, useEffect, useState } from "react";

export default function LiveVideoPanel() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);

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

  const sendToApi = (imageBlob) => {
    const formData = new FormData();
    formData.append("image", imageBlob, "captured-frame.jpeg");

    fetch("http://ec2-54-91-59-31.compute-1.amazonaws.com:8000/analyze-frame", {
      method: "POST",
      body: formData,
    })
      .then(response => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then(data => {
        console.log("Success:", data);
      })
      .catch(error => {
        console.error("Error:", error);
      });
  };

  const captureAndSend = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext("2d");

      // This is where you use the videoRef as the image source for the canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert the canvas content to a Blob
      canvas.toBlob((blob) => {
        if (blob) {
          // Send the Blob to the API
          sendToApi(blob);

          // Optional: also store the image locally for display
          const imageDataUrl = URL.createObjectURL(blob);
          setCapturedImage(imageDataUrl);
        }
      }, "image/jpeg", 0.9);
    }
  };

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
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>

      <div className="mt-4 text-center">
        <button
          onClick={captureAndSend}
          className="bg-[#1F8AAD] hover:bg-[#1A7790] text-white font-bold py-2 px-4 rounded"
        >
          Capture and Send to API
        </button>
      </div>

      {capturedImage && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold text-[#1F8AAD] mb-2 text-center">
            Captured Image
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
