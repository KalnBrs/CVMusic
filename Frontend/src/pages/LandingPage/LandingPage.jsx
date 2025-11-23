import { useEffect } from "react";

export default function LandingPage() {
  useEffect(() => {
    const init = async () => {
      try {
        const res = await fetch('http://ec2-54-91-59-31.compute-1.amazonaws.com:8000');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const contentType = res.headers.get('content-type') || '';
        const data = contentType.includes('application/json') ? await res.json() : await res.text();
        console.log('Fetched data:', data);
      } catch (err) {
        console.error('Fetch error:', err);
      }
    };
    init()
  }, [])

  return (
  <div className="min-h-screen bg-[#E9F7FB] text-black flex flex-col items-center px-6 py-20">
    <h1 className="text-6xl font-extrabold bg-linear-to-r from-[#26ACD9] to-[#00D4FF] bg-clip-text text-transparent mb-10">
      AI Guitar Tutor
    </h1>


    <div className=" max-w-3xl p-2 rounded-2xl bg-[#A8DEF0] border border-[#7DCDE8] shadow-xl flex items-center justify-center mb-10">
      <img src="/raf,360x360,075,t,fafafa_ca443f4786.u7.jpg" alt="" />
    </div>


    <p className="text-center text-lg text-black max-w-2xl mb-10">
      Learn guitar with <span className="text-[#1F8AAD] font-semibold">real-time AI feedback</span>, live finger tracking, and synced music sheets.
    </p>

    <div className="flex flex-row gap-10">
      <button className="bg-linear-to-r from-[#26ACD9] to-[#00D4FF] text-white text-lg font-medium px-10 py-3 rounded-full shadow-lg hover:opacity-90 active:scale-95 transition-all">
        <a href="/song-select">Start Playing ▶</a>
      </button>
      <button className="bg-linear-to-r from-[#00D4FF] to-[#26ACD9] text-white text-lg font-medium px-10 py-3 rounded-full shadow-lg hover:opacity-90 active:scale-95 transition-all">
        <a href="/cam-chords">Open Chords ▶</a>
      </button>
    </div>
  </div>

  );
}