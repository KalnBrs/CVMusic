import ChordItem from "./ChordItem";

export default function ChordList({ chords }) {
  return (
    <div className="space-y-6">
      {chords.map(chord => <ChordItem key={chord.name} chord={chord} />)}
    </div>
  );
}
