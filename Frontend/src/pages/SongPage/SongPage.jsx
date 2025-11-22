import DropDown from "../../Components/DropDown";
import SongComponent from "../../Components/SongComponent";

export default function SongPage() {
  return (
    <div className="min-h-screen bg-[#E9F7FB] text-black px-6 py-16">
      <h1 className="text-4xl font-bold text-center text-[#1F8AAD] mb-10">
        Choose a Song
      </h1>

      {/* Search + Filters */}
      <div className="flex max-w-3xl mx-auto bg-white p-6 rounded-2xl shadow-md border border-[#D4EEF7] mb-10 flex-row justify-between">
        <div className="mb-6 w-120 justify-self-start">
          <p className="text-lg font-medium text-[#1F8AAD] mb-2 pl-2">Search Songs: </p>
          <input
            type="text"
            placeholder="Enter song name..."
            className="w-full px-4 py-3 rounded-xl border border-[#BEE4F3] bg-[#F5FBFD] focus:outline-none focus:ring-2 focus:ring-[#26ACD9] transition"
          />
        </div>

        <div className="justify-self-end">
        <DropDown
          name="Difficulty"
          listOfOptions={["Any", "Easy", "Intermediate", "Hard"]}
        />
        </div>
      </div>

      {/* Song List */}
      <div className="max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* Example song — eventually map songs here */}
        <SongComponent
          name="Amazing Grace"
          author="Traditional"
          time="2:48"
          difficulty="Easy"
          img=""
        />
        <SongComponent
          name="Canon in D"
          author="Pachelbel"
          time="3:55"
          difficulty="Intermediate"
          img=""
        />
      </div>
    </div>
  );
}
