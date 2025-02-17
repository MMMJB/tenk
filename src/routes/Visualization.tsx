import { useRef, useState, useEffect } from "react";

import Keyboard from "../components/Keyboard";
import Word from "../components/Word";

import type { Finger, Letter } from "../utils";
import type { SentencePrediction } from "../utils/prediction";

import { letterToFinger } from "../utils";
import { fingersToPossibleWords, predictSentence } from "../utils/prediction";
import { trie } from "../main";

const space = letterToFinger(" ") as Finger;

export default function Page() {
  const [words, setWords] = useState<number[][]>([[]]);
  const [predictions, setPredictions] = useState<string[][]>([]);
  const [rankedPredictions, setRankedPredictions] = useState<
    Record<string, number>[]
  >([]);

  const numWords = useRef(1);

  function onKeyPress(e: KeyboardEvent) {
    if (e.ctrlKey || e.metaKey) return;

    if (e.key === "Backspace")
      setWords((p) => {
        const lastWord = p[p.length - 1];

        if (lastWord.length === 0) {
          numWords.current--;

          setPredictions((p) => p.slice(0, -1));
          return p.slice(0, -1);
        }

        return [...p.slice(0, -1), lastWord.slice(0, -1)];
      });
    else {
      const finger = letterToFinger(e.key as Letter);

      setWords((p) => {
        if (finger === space) return [...p, []];

        const lastWord = p[p.length - 1];
        return [...p.slice(0, -1), [...lastWord, finger]];
      });
    }
  }

  useEffect(() => {
    document.addEventListener("keydown", onKeyPress);

    return () => document.removeEventListener("keydown", onKeyPress);
  }, []);

  useEffect(() => {
    if (numWords.current === words.length) return;
    numWords.current = words.length;

    if (words.length < 2) return;

    const fingersForNewestFinishedWord = words[words.length - 2];
    let possibleWords: Set<string> | undefined = undefined;

    for (let i = 0; i < fingersForNewestFinishedWord.length; i++) {
      const finger = fingersForNewestFinishedWord[i];

      possibleWords = fingersToPossibleWords(
        finger,
        trie,
        possibleWords,
        i === 0,
        i === fingersForNewestFinishedWord.length - 1
      );
    }

    setPredictions((p) => [...p, [...(possibleWords ?? [])]]);
  }, [words]);

  async function predict() {
    const { probabilities } = (await predictSentence(
      predictions,
      "external"
    )) as SentencePrediction;

    setRankedPredictions(probabilities);
  }

  return (
    <>
      <Keyboard />
      <div className="sentence">
        {words
          .filter((word) => word.length)
          .map((word, i) => (
            <Word
              key={i}
              locked={i < words.length - 1}
              predictions={predictions[i] ?? []}
              rankedPredictions={rankedPredictions[i]}
            >
              {word.join(" ")}
            </Word>
          ))}
        <div className="word static">
          <button onClick={predict}>Predict</button>
        </div>
      </div>
    </>
  );
}
