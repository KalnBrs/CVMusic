import { useState } from "react";
import FretboardDiagram from "./FretboardDiagram";

export default function VariationItem({ variation, chord, setCurrCord }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-[#F5FBFD] border border-[#BEE4F3] rounded-xl p-4 shadow-inner">
      <div
        className="flex justify-between items-center cursor-pointer"
        onClick={() => setExpanded(prev => !prev)}
      >
        <p className="text-xl font-semibold text-[#1F8AAD]">{variation.type}</p>
        <span className="text-xl text-[#1F8AAD]">{expanded ? "−" : "+"}</span>
      </div>

      {expanded && <div className="mt-4"><FretboardDiagram diagram={variation.diagram} tab={variation.tab} /></div>}
      <button

        onClick={() => setCurrCord({"name": chord.name, "tab": variation.tab, "variation": variation.type})}
        className="mt-2 px-4 py-2 bg-[#1F8AAD] text-white rounded-lg hover:bg-[#166b86] transition"
      >
        Select Chord
      </button>
    </div>
  );
}
