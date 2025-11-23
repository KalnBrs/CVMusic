import { useEffect, useState } from "react";
import DropDown from "../../Components/DropDown";
import SongComponent from "../../Components/SongComponent";
import { getSongs } from "../../scripts/songs";

export default function SongPage() {
  const [songs, setSongs] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredSongs, setFilteredSongs] = useState([]);

  useEffect(() => {
    async function init() {
      try {
        const allSongs = await getSongs();
        setSongs(allSongs);
        setFilteredSongs(allSongs);
      } catch (err) {
        console.error("Failed to load songs:", err);
      }
    }
    init();
  }, []);

  // Update filtered songs whenever the search term changes
  useEffect(() => {
    if (!searchTerm) {
      setFilteredSongs(songs);
    } else {
      const term = searchTerm?.toLowerCase();
      const filtered = songs.filter(
        (song) =>
          song.title.toLowerCase().includes(term) ||
          song.artist.toLowerCase().includes(term)
      );
      setFilteredSongs(filtered);
    }
  }, [searchTerm, songs]);

  return (
    <div className="min-h-screen bg-[#E9F7FB] text-black px-6 py-16">
      <h1 className="text-4xl font-bold text-center text-[#1F8AAD] mb-10">
        Choose a Song
      </h1>

      {/* Search + Filters */}
      <div className="flex max-w-3xl mx-auto bg-white p-6 rounded-2xl shadow-md border border-[#D4EEF7] mb-10 flex-row justify-between">
        <div className="mb-6 w-full justify-self-start">
          <p className="text-lg font-medium text-[#1F8AAD] mb-2 pl-2">
            Search Songs:
          </p>
          <input
            type="text"
            placeholder="Enter song name or author..."
            className="w-full px-4 py-3 rounded-xl border border-[#BEE4F3] bg-[#F5FBFD] focus:outline-none focus:ring-2 focus:ring-[#26ACD9] transition"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Song List */}
      <div className="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-6">
        {filteredSongs.map((song, index) => (
          <SongComponent
            key={index}
            id={song.id}
            name={song.title}
            author={song.artist}
            time={song.time || ""}
            difficulty={song.difficulty || "Any"}
            img={song.img || ""}
          />
        ))}
      </div>
    </div>
  );
}
