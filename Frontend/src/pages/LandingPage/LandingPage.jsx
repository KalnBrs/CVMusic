export default function LandingPage() {
  return (
  <div className="min-h-screen bg-[#E9F7FB] text-black flex flex-col items-center px-6 py-20">
    {/* Logo / Title */}
    <h1 className="text-6xl font-extrabold bg-linear-to-r from-[#26ACD9] to-[#00D4FF] bg-clip-text text-transparent mb-10">
      AI Guitar Tutor
    </h1>


    {/* Hero Graphic Placeholder */}
    <div className="w-full max-w-3xl h-64 rounded-2xl bg-[#A8DEF0] border border-[#7DCDE8] shadow-xl flex items-center justify-center mb-10">
      <span className="text-[#A1A1AA] text-lg">Guitar Illustration Placeholder</span>
    </div>


    {/* Subtitle */}
    <p className="text-center text-lg text-black max-w-2xl mb-10">
      Learn guitar with <span className="text-[#1F8AAD] font-semibold">real-time AI feedback</span>, live finger tracking, and synced music sheets.
    </p>


    {/* Start Button */}
    <button className="bg-gradient-to-r from-[#26ACD9] to-[#00D4FF] text-white text-lg font-medium px-10 py-3 rounded-full shadow-lg hover:opacity-90 active:scale-95 transition-all">
      <a href="/song-select">Start Playing ▶</a>
    </button>
  </div>
  );
}