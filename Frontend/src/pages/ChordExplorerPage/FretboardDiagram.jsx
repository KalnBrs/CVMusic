export default function FretboardDiagram({ diagram, tab }) {
  const maxFret = Math.max(...diagram.map(pos => pos.fret), 4); // minimum 4 frets
  const stringNames = ["e", "B", "G", "D", "A", "E"]; // low E → high e

  return (
    <div className="relative w-full bg-white border border-[#D4EEF7] rounded-xl h-48">

      {/* Frets */}
      {Array.from({ length: maxFret }, (_, i) => i + 1).map(fret => (
        <div
          key={fret}
          className="absolute left-0 w-full border-t border-gray-300"
          style={{ top: `${(fret / maxFret) * 100}%` }}
        />
      ))}

      {/* Strings */}
      {Array.from({ length: 6 }, (_, idx) => 6 - idx).map((string, i) => (
        <div
          key={string}
          className="absolute top-0 h-full border-l border-gray-300"
          style={{ left: `${(i / 5) * 100}%` }}
        />
      ))}

      {/* String Names */}
      {stringNames.map((name, i) => (
        <div
          key={i}
          className="absolute text-[#7DCDE8] text-sm font-semibold"
          style={{ left: `${(i / 5) * 100}%`, top: "-28px", transform: "translateX(-50%)" }}
        >
          {name}
        </div>
      ))}

      {/* TAB numbers */}
      {tab.map((num, idx) => {
        const flippedIdx = 5 - idx; // flip string order
        return (
          <div
            key={idx}
            className="absolute text-gray-700 text-sm font-semibold"
            style={{ left: `${(flippedIdx / 5) * 100}%`, top: "-8px", transform: "translateX(-50%)" }}
          >
            {num}
          </div>
        );
      })}

      {/* Finger positions using TAB */}
      {tab.map((num, idx) => {
        if (num === "X" || num === "0") return null; // skip muted or open strings
        const flippedIdx = 5 - idx;
        return (
          <div
            key={idx}
            className="absolute bg-[#26ACD9] w-5 h-5 rounded-full shadow-md"
            style={{
              left: `${(flippedIdx / 5) * 100}%`,
              top: `${(parseInt(num) / maxFret) * 100}%`,
              transform: "translate(-50%, -50%)"
            }}
          />
        );
      })}

    </div>
  );
}
