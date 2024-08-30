import { useRef, useState, useEffect, useMemo } from "react";

import Word from "../components/Word";

import type { APISentencePrediction } from "../utils/prediction";
import type { Finger, Letter } from "../utils";

import { letterToFinger } from "../utils";
import { fingersToPossibleWords, predictSentence } from "../utils/prediction";
import { trie } from "../main";

type Sentence = {
  prefix: string;
  sentence: string;
  sentenceFingers: number[];
  prediction: string[];
};

const space = letterToFinger(" ") as Finger;

export default function Page() {
  const prefixComplete = useRef(false);

  const [pastSentences, setPastSentences] = useState<Sentence[]>([]);
  const [currentSentence, setCurrentSentence] = useState<Sentence>({
    prefix: "",
    sentence: "",
    sentenceFingers: [],
    prediction: [],
  });
  const [loading, setLoading] = useState(false);

  function splitSentenceFingersBySpace(sentenceFingers: number[]) {
    return sentenceFingers.reduce(
      (acc, f) => {
        if (f === space) {
          acc.push([]);
        } else {
          acc[acc.length - 1].push(f);
        }

        return acc;
      },
      [[]] as number[][]
    );
  }

  async function onKeyPress(e: KeyboardEvent) {
    if (e.key === "Backspace") {
      if (prefixComplete.current) {
        setCurrentSentence((p) => ({
          ...p,
          sentence: p.sentence.slice(0, -1),
          sentenceFingers: p.sentenceFingers.slice(0, -1),
        }));
      } else {
        setCurrentSentence((p) => ({
          ...p,
          prefix: p.prefix.slice(0, -1),
        }));
      }
    } else if (e.key === "Enter") {
      setLoading(true);

      const sentenceWords = splitSentenceFingersBySpace(
        currentSentence.sentenceFingers
      );
      let wordLists: string[][] = [];

      for (let i = 0; i < sentenceWords.length; i++) {
        const fingersForWord = sentenceWords[i];

        let possibleWords: Set<string> | undefined = undefined;

        for (let j = 0; j < fingersForWord.length; j++) {
          const finger = fingersForWord[j];

          possibleWords = fingersToPossibleWords(
            finger,
            trie,
            possibleWords,
            j === 0
          );
        }

        wordLists.push([...(possibleWords ?? [])]);
      }

      const { predicted_sentence } = (await predictSentence(
        currentSentence.prefix,
        wordLists,
        "internal"
      )) as APISentencePrediction;

      setPastSentences((p) => [
        ...p,
        {
          prefix: currentSentence.prefix,
          sentence: currentSentence.sentence,
          sentenceFingers: currentSentence.sentenceFingers,
          prediction: predicted_sentence.split(" ").slice(1),
        },
      ]);
      setCurrentSentence({
        prefix: "",
        sentence: "",
        sentenceFingers: [],
        prediction: [],
      });
      prefixComplete.current = false;

      setLoading(false);
    } else {
      const finger = letterToFinger(e.key as Letter);

      setCurrentSentence((p) => {
        if (finger === space && !prefixComplete.current) {
          prefixComplete.current = true;
          return p;
        } else if (!prefixComplete.current) {
          return {
            ...p,
            prefix: p.prefix + e.key,
          };
        } else {
          return {
            ...p,
            sentence: p.sentence + e.key,
            sentenceFingers: [...p.sentenceFingers, finger],
          };
        }
      });
    }
  }

  useEffect(() => {
    document.addEventListener("keydown", onKeyPress);

    return () => document.removeEventListener("keydown", onKeyPress);
  }, [onKeyPress]);

  const { sentenceFingers, prefix } = currentSentence;

  return (
    <>
      {pastSentences.map(
        ({ prefix, sentenceFingers, sentence, prediction }, i) => (
          <div key={i} className="sentence">
            <div className="word static">{prefix}</div>
            {splitSentenceFingersBySpace(sentenceFingers).map((word, i) => (
              <Word
                key={i}
                locked
                predictions={[]}
                prediction={prediction[i]}
                predictionCorrect={prediction[i] === sentence.split(" ")[i]}
              >
                {word.join("")}
              </Word>
            ))}
          </div>
        )
      )}
      <div className="sentence">
        <div className="word static">{prefix}</div>
        {splitSentenceFingersBySpace(sentenceFingers).map((word, i) => (
          <Word key={i} locked predictions={[]}>
            {word.join("")}
          </Word>
        ))}
      </div>
    </>
  );
}
