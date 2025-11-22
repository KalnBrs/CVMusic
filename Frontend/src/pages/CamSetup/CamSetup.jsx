import { useEffect, useRef, useState } from "react";
import { ThreeDots } from "react-loader-spinner";

export default function CameraSetupPage() {
  const videoRef = useRef(null);
  const [cameraStatus, setCameraStatus] = useState("Not Connected");

  const [cameras, setCameras] = useState([]);
  const [selectedCam, setSelectedCam] = useState(null);

  const [loading, setLoading] = useState(false)



  const [specs, setSpecs] = useState({
    width: null,
    height: null,
    fps: null,
    deviceId: null
  });

  const [error, setError] = useState(null);

  const getVideo = async () => {
    setLoading(true);
    setError(null);
    navigator.mediaDevices
      .getUserMedia({
        video: { width: 1920, height: 1080 }
      })
      .then(stream => {
        let video = videoRef.current;
        if (!video) throw new Error("Video element not ready");
        
        video.srcObject = stream;
        video.play();

        const track = stream.getVideoTracks()[0];
        const settings = track.getSettings();
        
        setLoading(false)
        setSpecs({
          width: settings.width,
          height: settings.height,
          fps: settings.frameRate,
          deviceId: settings.deviceId
        });

        setCameraStatus("Connected");
      })
      .catch(err => {
        console.error(err);
        setCameraStatus("Error");
        setError("Unable to access camera.");
        setLoading(false)
      })
  };

  const getCameras = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      
      // Filter only video inputs (webcams)
      const videoDevices = devices.filter(device => device.kind === "videoinput");

      console.log(videoDevices);
      setCameras(videoDevices); // array of { deviceId, label, kind }
    } catch (err) {
      console.error("Error fetching devices:", err);
    }
  };

  useEffect(() => {
    getCameras()
  }, [videoRef])

  return (
    <div className="min-h-screen bg-[#E9F7FB] text-black px-6 py-14 flex flex-col items-center">
      
      <h1 className="text-4xl font-bold text-[#1F8AAD] mb-6 text-center">
        Set Up Your Camera
      </h1>

      <p className="text-lg text-gray-700 max-w-2xl text-center mb-10">
        Position your guitar in view. We will use your webcam to detect 
        hand placement and track finger movement in real time.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 max-w-6xl w-full">

        <div className="bg-white rounded-2xl shadow-md border border-[#D4EEF7] p-6 flex flex-col items-center">
          <h2 className="text-2xl font-semibold text-[#1F8AAD] mb-4">
            Camera Preview
          </h2>

          <div className="w-full aspect-video bg-[#A8DEF0] rounded-xl flex items-center justify-center text-[#7BAFBE] overflow-hidden">
            <video
              ref={videoRef}
              className="w-full h-full object-cover"
              style={{ transform: "scaleX(-1)" }}
            />
            {loading && (
              <div className="justify-center absolute">
              <ThreeDots
                height="80"
                width="80"
                color="#1F8AAD"
              />
              </div>
            )}
          </div>

          {error && <p className="text-red-600 mt-4 font-bold">{error}</p>}
          
          <div className="flex flex-row justify-between w-full items-center mt-6">
            <button
              onClick={getVideo}
              className=" px-6 py-3 bg-gradient-to-r from-[#26ACD9] to-[#00D4FF] text-white rounded-full text-lg font-medium shadow-lg hover:opacity-90 active:scale-95 transition-all"
            >
              Turn On Camera
            </button>
            <div className="flex flex-col items-center">
              <p className="text-[#1F8AAD] font-medium self-center text-xl pr-2">Media Source: </p>
              <select name="" id="" onChange={e => setSelectedCam(e.target.value )} 
                className="px-4  py-2 rounded-xl border border-[#BEE4F3] bg-[#F5FBFD] focus:outline-none focus:ring-2 focus:ring-[#26ACD9] transition cursor-pointer self-center">
                {cameras.map(cam => (
                  <option key={cam.deviceId} value={cam.deviceId}>
                    {cam.label || `Camera ${cam.deviceId}`}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-md border border-[#D4EEF7] p-6 flex flex-col justify-between">

          <div>
            <h2 className="text-2xl font-semibold text-[#1F8AAD] mb-4">
              Instructions
            </h2>

            <ul className="space-y-3 text-gray-700">
              <li>• Ensure your room is well lit.</li>
              <li>• Hold your guitar so the fretboard is clearly visible.</li>
              <li>• Keep your hands within the camera’s frame.</li>
              <li>• Position your device on a stable surface.</li>
            </ul>

            <h3 className="mt-8 text-xl font-semibold text-[#1F8AAD] mb-2">
              Camera Status
            </h3>

            <div className="bg-[#F5FBFD] border border-[#BEE4F3] rounded-xl p-4 shadow-inner space-y-1">
              <p>
                • Status:{" "}
                <span className="font-medium">
                  {cameraStatus}
                </span>
              </p>
              
              <p>
                • Resolution:{" "}
                <span className="font-medium">
                  {specs.width && specs.height
                    ? `${specs.width} × ${specs.height}`
                    : "—"}
                </span>
              </p>

              <p>
                • FPS:{" "}
                <span className="font-medium">
                  {specs.fps ?? "—"}
                </span>
              </p>

              <p>
                • Device ID:{" "}
                <span className="font-medium break-all">
                  {specs.deviceId ?? "—"}
                </span>
              </p>
            </div>
          </div>

          <a
            href="/sheet-view"
            className="mt-10 w-full text-center bg-gradient-to-r from-[#26ACD9] to-[#00D4FF] text-white px-8 py-3 rounded-full text-lg shadow-lg hover:opacity-90 active:scale-95 transition-all"
          >
            Continue ▶
          </a>

        </div>
      </div>
    </div>
  );
}
