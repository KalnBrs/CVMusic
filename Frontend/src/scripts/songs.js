async function getSongs() {
  const res = await fetch(
    "http://ec2-54-91-59-31.compute-1.amazonaws.com:8000/api/songs",
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!res.ok) {
    throw new Error(`Failed to fetch songs: ${res.status}`);
  }

  return await res.json();
}

async function getSongCords(id) {
  const res = await fetch (
    `http://ec2-54-91-59-31.compute-1.amazonaws.com:8000/api/chords/${id}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    }
  )
  return await res.json()
}

export { getSongs, getSongCords };
