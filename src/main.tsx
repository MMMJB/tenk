import "./index.css";

// import { StrictMode } from 'react'
import App from "./App.tsx";

import type { Letter } from "./utils";

import { createRoot } from "react-dom/client";
import trie from "./utils/loadWords";
import { fingersToPossibleSentences } from "./utils/prediction.ts";
import { letterToFinger } from "./utils";

const sentence = "foxes are known for being smart";
const sentenceToLetters = sentence
  .split("")
  .map((letter) => letterToFinger(letter as Letter));

const prediction = fingersToPossibleSentences(sentenceToLetters, trie);
console.log(prediction);

createRoot(document.getElementById("root")!).render(
  // <StrictMode>
  <App />
  //</StrictMode>,
);
