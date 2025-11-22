export default function DropDown({ name, listOfOptions = [] }) {
  return (
    <div className="flex flex-col mb-4">
      <p className="text-[#1F8AAD] font-medium mb-3 text-end pr-2">{name}:</p>

      <select
        name={name}
        id={name}
        className="px-4 py-3 rounded-xl border border-[#BEE4F3] bg-[#F5FBFD] focus:outline-none focus:ring-2 focus:ring-[#26ACD9] transition cursor-pointer"
      >
        {listOfOptions.map((opt, idx) =>
          typeof opt === "string" ? (
            <option key={idx} value={opt}>
              {opt}
            </option>
          ) : (
            <option key={opt.value ?? idx} value={opt.value ?? opt.label}>
              {opt.label ?? opt.value}
            </option>
          )
        )}
      </select>
    </div>
  );
}
