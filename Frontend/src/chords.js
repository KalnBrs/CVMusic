const chords = [
  // =========================
  // C CHORD FAMILY
  // =========================
  {
    name: "C",
    variations: [
      { type: "Major", tab: ["X", "3", "2", "0", "1", "0"], diagram: [{ string: 2, fret: 1 }, { string: 4, fret: 2 }, { string: 5, fret: 3 }] },
      { type: "Minor", tab: ["X", "3", "1", "0", "1", "3"], diagram: [{ string: 1, fret: 3 }, { string: 2, fret: 1 },{ string: 4, fret: 1 }, { string: 5, fret: 3 }] },
      { type: "7", tab: ["X", "3", "2", "3", "1", "0"], diagram: [{ string: 2, fret: 1 }, { string: 3, fret: 3 }, { string: 4, fret: 2 }, { string: 5, fret: 3 }] },
      { type: "maj7", tab: ["X", "X", "2", "4", "1", "3"], diagram: [{ string: 1, fret: 3 }, { string: 2, fret: 1 }, { string: 3, fret: 4 }, { string: 4, fret: 2 }] },
      { type: "sus2", tab: ["X", "3", "5", "5", "3", "3"], diagram: [{ string: 1, fret: 3 }, { string: 2, fret: 3 }, { string: 3, fret: 5 }, { string: 3, fret: 5 }, { string: 5, fret: 3 }] },
      { type: "sus4", tab: ["X", "3", "3", "0", "1", "X"], diagram: [{ string: 1, fret: 1 }, { string: 4, fret: 3 }, { string: 5, fret: 3 }] },
      { type: "add9", tab: ["X", "5", "7", "5", "7", "8"], diagram: [{ string: 2, fret: 1 }, { string: 4, fret: 2 }, { string: 5, fret: 3 }, { string: 1, fret: 3 }] }
    ]
  },

  // =========================
  // D CHORD FAMILY
  // =========================
  {
    name: "D",
    variations: [
      { type: "Major", tab: ["X", "X", "0", "2", "3", "2"], diagram: [{ string: 1, fret: 2 }, { string: 2, fret: 3 }, { string: 3, fret: 2 }] },
      { type: "Minor", tab: ["X", "X", "0", "2", "3", "1"], diagram: [{ string: 1, fret: 1 }, { string: 2, fret: 3 }, { string: 3, fret: 2 }] },
      { type: "7", tab: ["X", "X", "0", "2", "1", "2"], diagram: [{ string: 1, fret: 2 }, { string: 2, fret: 3 }, { string: 3, fret: 2 }, { string: 5, fret: 1 }] },
      { type: "maj7", tab: ["X", "X", "0", "1", "1", "1"], diagram: [{ string: 1, fret: 2 }, { string: 2, fret: 2 }, { string: 3, fret: 2 }] },
      { type: "sus2", tab: ["X", "X", "0", "2", "3", "0"], diagram: [{ string: 2, fret: 3 }, { string: 3, fret: 2 }] },
      { type: "sus4", tab: ["X", "X", "0", "2", "3", "3"], diagram: [{ string: 1, fret: 3 }, { string: 2, fret: 3 }, { string: 3, fret: 2 }] }
    ]
  },

  // =========================
  // E CHORD FAMILY
  // =========================
  {
    name: "E",
    variations: [
      { type: "Major", tab: ["0", "2", "2", "1", "0", "0"], diagram: [{ string: 3, fret: 1 }, { string: 4, fret: 2 }, { string: 5, fret: 2 }] },
      { type: "Minor", tab: ["0", "2", "2", "0", "0", "0"], diagram: [{ string: 4, fret: 2 }, { string: 5, fret: 2 }] },
      { type: "7", tab: ["0", "2", "1", "0", "0", "0"], diagram: [{ string: 3, fret: 1 }, { string: 5, fret: 2 }] },
      { type: "maj7", tab: ["0", "X", "1", "1", "0", "X"], diagram: [{ string: 3, fret: 1 }, { string: 4, fret: 1 }, { string: 5, fret: 2 }] },
      { type: "sus2", tab: ["X", "X", "2", "4", "5", "2"], diagram: [{ string: 2, fret: 2 }, { string: 3, fret: 2 }, { string: 4, fret: 1 }] },
      { type: "sus4", tab: ["0", "2", "2", "2", "0", "0"], diagram: [{ string: 2, fret: 2 }, { string: 3, fret: 2 }, { string: 4, fret: 2 }] },
      { type: "add9", tab: ["X", "7", "6", "4", "7", "4"], diagram: [{ string: 2, fret: 2 }, { string: 3, fret: 1 }, { string: 4, fret: 1 }] }
    ]
  },

  // =========================
  // F CHORD FAMILY
  // =========================
  {
    name: "F",
    variations: [
      { type: "Major (barre)", tab: ["1", "3", "3", "2", "1", "1"], diagram: [{ string: 1, fret: 1 }, { string: 2, fret: 1 }, { string: 3, fret: 2 }, { string: 4, fret: 3 }, { string: 5, fret: 3 }, { string: 6, fret: 1 }] },
      { type: "Minor (barre)", tab: ["1", "3", "3", "1", "1", "1"], diagram: [{ string: 1, fret: 1 }, { string: 2, fret: 1 }, { string: 3, fret: 1 }, { string: 4, fret: 3 }, { string: 5, fret: 3 }, { string: 6, fret: 1 }] },
      { type: "7", tab: ["1", "3", "1", "2", "1", "1"], diagram: [{ string: 1, fret: 1 }, { string: 2, fret: 1 }, { string: 3, fret: 2 }, { string: 4, fret: 1 }, { string: 5, fret: 3 }, { string: 6, fret: 1 }] }
    ]
  },

  // =========================
  // G CHORD FAMILY
  // =========================
  {
    name: "G",
    variations: [
      { type: "Major", tab: ["3", "2", "0", "0", "0", "3"], diagram: [{ string: 1, fret: 3 }, { string: 5, fret: 2 }, { string: 6, fret: 3 }] },
      { type: "Minor", tab: ["3", "5", "5", "3", "3", "3"], diagram: [{ string: 1, fret: 3 }, { string: 2, fret: 3 }, { string: 3, fret: 3 }, { string: 5, fret: 2 }] },
      { type: "7", tab: ["3", "3", "0", "0", "0", "1"], diagram: [{ string: 1, fret: 1 }, { string: 6, fret: 3 }] },
      { type: "sus2", tab: ["X", "X", "5", "7", "8", "5"], diagram: [{ string: 1, fret: 3 }, { string: 5, fret: 3 }, { string: 6, fret: 3 }] },
      { type: "sus4", tab: ["1", "5", "5", "5", "3", "3"], diagram: [{ string: 1, fret: 3 }, { string: 2, fret: 5 }, { string: 3, fret: 5 }, { string: 4, fret: 5 }, { string: 5, fret: 3 }, { string: 6, fret: 3 }] },
      { type: "add9", tab: ["X", "10", "9", "7", "10", "7"], diagram: [{ string: 1, fret: 3 }, { string: 2, fret: 2 }, { string: 5, fret: 3 }, { string: 6, fret: 3 }] }
    ]
  },

  // =========================
  // A CHORD FAMILY
  // =========================
  {
    name: "A",
    variations: [
      { type: "Major", tab: ["X", "0", "2", "2", "2", "X"], diagram: [{ string: 2, fret: 2 }, { string: 3, fret: 2 }, { string: 4, fret: 2 }] },
      { type: "Minor", tab: ["X", "0", "2", "2", "1", "0"], diagram: [{ string: 2, fret: 1 }, { string: 3, fret: 2 }, { string: 4, fret: 2 }] },
      { type: "7", tab: ["X", "0", "2", "0", "2", "X"], diagram: [{ string: 2, fret: 2 }, { string: 4, fret: 2 }] },
      { type: "sus2", tab: ["X", "0", "2", "2", "0", "0"], diagram: [{ string: 2, fret: 2 }, { string: 3, fret: 2 }, { string: 4, fret: 1 }] },
      { type: "sus4", tab: ["X", "0", "2", "2", "3", "0"], diagram: [{ string: 2, fret: 2 }, { string: 3, fret: 2 }, { string: 4, fret: 3 }] },
      { type: "add9", tab: ["5", "4", "2", "4", "2", "X"], diagram: [{ string: 2, fret: 2 }, { string: 3, fret: 1 }, { string: 4, fret: 2 }] }
    ]
  },

  // =========================
  // B CHORD FAMILY
  // =========================
  {
    name: "B",
    variations: [
      { type: "Major (barre)", tab: ["2", "4", "4", "4", "2", "X"], diagram: [{ string: 1, fret: 2 }, { string: 2, fret: 4 }, { string: 3, fret: 4 }, { string: 4, fret: 4 }, { string: 5, fret: 2 }] },
      { type: "Minor (barre)", tab: ["2", "3", "4", "4", "2", "X"], diagram: [{ string: 1, fret: 2 }, { string: 2, fret: 3 }, { string: 3, fret: 4 }, { string: 4, fret: 4 }, { string: 5, fret: 2 }] },
      { type: "7", tab: ["2", "4", "2", "4", "2", "X"], diagram: [{ string: 1, fret: 2 }, { string: 2, fret: 4 }, { string: 3, fret: 2 }, { string: 4, fret: 4 }, { string: 5, fret: 2 }] }
    ]
  },

  // =========================
  // POWER CHORDS
  // =========================
  {
    name: "Power Chords",
    variations: [
      { type: "C5", tab: ["X", "3", "5", "5", "X", "X"], diagram: [{ string: 2, fret: 3 }, { string: 3, fret: 5 }, { string: 4, fret: 5 }] },
      { type: "D5", tab: ["X", "5", "7", "7", "X", "X"], diagram: [{ string: 2, fret: 5 }, { string: 3, fret: 7 }, { string: 4, fret: 7 }] },
      { type: "E5", tab: ["0", "2", "2", "1", "X", "X"], diagram: [{ string: 1, fret: 0 }, { string: 2, fret: 2 }, { string: 3, fret: 2 }, { string: 4, fret: 1 }] }
    ]
  }
];


export default chords;