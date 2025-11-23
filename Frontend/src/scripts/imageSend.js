const sendToApi = async (imageBlob) => {
  if (!(imageBlob instanceof Blob)) {
    console.error("sendToApi received invalid blob:", imageBlob);
    return;
  }

  const formData = new FormData();
  formData.append("image", imageBlob, "captured-frame.jpeg");

  const response = await fetch("http://localhost:8000/analyze-frame", {
    method: "POST",
    body: formData,
  });

  const data = await response.json();
  console.log("API Response:", data);

  const imageDataUrl = URL.createObjectURL(imageBlob);
  setCapturedImage(imageDataUrl);
};

const captureAndSend = async (videoRef, canvasRef, setCapturedImage, currCord) => {
  const video = videoRef.current;
  const canvas = canvasRef.current;
  if (!video || !canvas) return;

  // wait for video metadata
  if (video.videoWidth === 0 || video.videoHeight === 0) {
    await new Promise(resolve => {
      const onLoaded = () => {
        video.removeEventListener("loadedmetadata", onLoaded);
        resolve();
      };
      video.addEventListener("loadedmetadata", onLoaded);
    });
  }

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  return new Promise((resolve, reject) => {
    canvas.toBlob(async (blob) => {
      if (!blob) return reject(new Error("No blob created"));
      try {
        const formData = new FormData();
        formData.append("image", blob, "captured-frame.jpeg");
        formData.append("file", JSON.stringify(currCord))

        const response = await fetch("http://ec2-54-91-59-31.compute-1.amazonaws.com:8000/analyze-frame", {
          method: "POST",
          body: formData
        });

        // const data = await response.json();
        const imageDataUrl = URL.createObjectURL(blob);
        setCapturedImage(imageDataUrl);

        resolve(response); // return the fetch Response object
      } catch (err) {
        reject(err);
      }
    }, "image/jpeg", 0.9);
  });
};

export { captureAndSend }