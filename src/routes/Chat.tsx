import "../chat.css";

import { useState } from "react";

import { Fragment } from "react";

import type { APISentencePrediction } from "../utils/prediction";
import type { Finger, Letter } from "../utils";

import { letterToFinger } from "../utils";
import { fingersToPossibleWords, predictSentence } from "../utils/prediction";
import { trie } from "../main";

type Message = {
  text: string[][];
  fingers: Finger[][];
};

const space = letterToFinger(" ") as Finger;

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

export default function Page() {
  const [fingers, setFingers] = useState<Finger[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);

  async function sendMessage(fingersByWord: Finger[][], messageIndex: number) {
    let wordLists: string[][] = [];

    for (let i = 0; i < fingersByWord.length; i++) {
      const fingersForWord = fingersByWord[i];

      let possibleWords: Set<string> | undefined = undefined;

      for (let j = 0; j < fingersForWord.length; j++) {
        const finger = fingersForWord[j];

        possibleWords = fingersToPossibleWords(
          finger,
          trie,
          possibleWords,
          j === 0,
          j === fingersForWord.length - 1
        );
      }

      wordLists.push([...(possibleWords ?? [])]);
    }

    const { predicted_sentence } = (await predictSentence(
      wordLists,
      "internal"
    )) as APISentencePrediction;

    const text = predicted_sentence.split(" ").map((w) => w.split(""));

    setMessages((p) =>
      p.map((m, i) => (i === messageIndex ? { ...m, text } : m))
    );
  }

  function onKeyPress(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;

    if (e.key === "Enter" && fingers.length) {
      const fingersByWord = splitSentenceFingersBySpace(fingers);

      sendMessage(fingersByWord, messages.length);

      setFingers([]);
      setMessages((p) => [...p, { text: [], fingers: fingersByWord }]);
    } else if (e.key === "Backspace") {
      setFingers((p) => p.slice(0, -1));
    } else {
      const letter = e.key.toLowerCase() as Letter;
      const finger = letterToFinger(letter);

      if (finger !== undefined) {
        setFingers((p) => [...p, finger]);
      }
    }
  }

  return (
    <main id="chat">
      <ul id="messages">
        {messages.map(({ text, fingers }, i) => (
          <li className="message" key={i}>
            {fingers.map((word, wordIndex) => (
              <Fragment key={wordIndex}>
                <span className="word">
                  {word.map((letter, letterIndex) => (
                    <Fragment key={letterIndex}>
                      {!!text.length && (
                        <span
                          className="letter"
                          style={{
                            animationDelay: `${letterIndex * 0.025}s`,
                          }}
                        >
                          {text[wordIndex][letterIndex]}
                        </span>
                      )}
                      <span className="finger" aria-hidden>
                        {letter}
                      </span>
                    </Fragment>
                  ))}
                </span>
                {wordIndex < fingers.length - 1 && <span> </span>}
              </Fragment>
            ))}
          </li>
        ))}
      </ul>
      <input
        id="input"
        type="text"
        value={fingers.join("")}
        onKeyDown={onKeyPress}
        autoFocus
        readOnly
        autoComplete="off"
      />
    </main>
  );
}
