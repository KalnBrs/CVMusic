export default function SongComponent({
  name,
  author,
  time,
  difficulty,
  img
}) {
  return (
    <div className="bg-white rounded-2xl shadow-md border border-[#D4EEF7] p-6 hover:shadow-lg hover:scale-[1.02] transition-all">
      <div className="w-full h-40 bg-[#A8DEF0] rounded-xl flex items-center justify-center mb-4 overflow-hidden">
        {img ? (
          <img src={img} alt={name} className="w-full h-full object-cover" />
        ) : (
          <span className="text-[#7BAFBE]">Cover Art</span>
        )}
      </div>

      <p className="text-xl font-semibold text-[#1F8AAD]">{name}</p>
      <p className="text-sm text-gray-600">By {author}</p>

      <div className="flex justify-between items-center mt-4 text-sm font-medium text-gray-700">
        <div>
          <span className="pr-3">⏱ {time}</span>
          <span
            className={`px-3 py-1 rounded-full text-white ${
              difficulty === "Easy"
                ? "bg-[#4ADE80]"
                : difficulty === "Intermediate"
                ? "bg-[#FBBF24]"
                : "bg-[#EF4444]"
            }`}
          >
            {difficulty}
          </span>
        </div>
        <button className="bg-[#176782] px-3 py-2 rounded-2xl text-[#E9F7FB] hover:bg-[#26ACD9] transition duration-300 ease-in-out">
          <a href="">Play Song</a>
        </button>
      </div>
    </div>
  );
}
