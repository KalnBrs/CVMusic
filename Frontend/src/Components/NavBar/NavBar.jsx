export default function NavBar() {
  return (
    <nav className="flex fixed top-0 z-50 w-full h-10 justify-center items-center bg-[#A8DEF0]/70 gap-5">
      
      {/* <a href="/song-select" className="text-[#26ACD9] font-bold">Song Select</a> */}
      <a href="/"><img src="/guitar.png" alt="" className="h-[22px] w-[22px]"/></a>
      <a href="/cam-chords" className="text-[#26ACD9] font-bold">Chord Explore</a>

    </nav>
  )
}