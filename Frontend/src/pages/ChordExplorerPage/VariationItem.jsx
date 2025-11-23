import { useState } from "react";
import FretboardDiagram from "./FretboardDiagram";

export default function VariationItem({ variation }) {
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
    </div>
  );
}
