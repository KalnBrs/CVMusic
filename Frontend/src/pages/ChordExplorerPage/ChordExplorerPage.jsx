import chords from "../../chords";
import LiveVideoPanel from "./LiveVideoPanel";
import ChordList from "./ChordList";

import { useState } from "react";

export default function ChordExplorerPage() {
  const [currCord, setCurrCord] = useState(null)

  return (
    <div className="min-h-screen bg-[#E9F7FB] px-6 py-10">
      <h1 className="text-4xl font-bold text-[#1F8AAD] text-center mb-10">Chord Explorer</h1>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-10">
        <LiveVideoPanel currCord={currCord} />
        <div>
          <ChordList chords={chords} setCurrCord={setCurrCord} />
        </div>
      </div>
    </div>
  );
}
