import { useState } from "react";
import VariationItem from "./VariationItem";

export default function ChordItem({ chord }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white rounded-2xl border border-[#D4EEF7] shadow-md p-6">
      <div
        className="flex justify-between items-center cursor-pointer"
        onClick={() => setExpanded(prev => !prev)}
      >
        <h2 className="text-2xl font-semibold text-[#1F8AAD]">{chord.name} Chord</h2>
        <span className="text-2xl text-[#1F8AAD]">{expanded ? "−" : "+"}</span>
      </div>

      {expanded && <div className="mt-6 space-y-4">{chord.variations.map(v => <VariationItem key={v.type} variation={v} />)}</div>}
    </div>
  );
}
