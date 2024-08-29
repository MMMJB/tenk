import { fingerToPossibleLetters, letterToFinger } from ".";

import type { Finger } from ".";
import type { Trie } from "../lib/trie";

// Get possible words for fingers
export function fingersToPossibleWords(
  finger: Finger,
  trie: Trie,
  wordList?: Set<string>,
  isFirstLetter = false
) {
  const possibleLetters = fingerToPossibleLetters(finger);

  if (isFirstLetter) return new Set(possibleLetters);
  else if (!wordList) throw new Error("wordList is required");

  const possibleWords = new Set<string>();

  for (const word of wordList) {
    for (const possibleLetter of possibleLetters) {
      const newWord = word + possibleLetter;

      if (trie.searchTrie(newWord)) {
        possibleWords.add(newWord);
      }
    }
  }

  return possibleWords;
}

// Get possible sentence from fingers
export function predictSentence(fingers: Finger[], trie: Trie) {
  const spaceFinger = letterToFinger(" ");

  const words = fingers.reduce(
    (acc, finger) => {
      if (finger === spaceFinger) {
        acc.push([]);
      } else {
        acc[acc.length - 1].push(finger);
      }

      return acc;
    },
    [[]] as Finger[][]
  );

  let sentenceWords: string[][] = [];

  for (let i = 0; i < words.length; i++) {
    const fingersForWord = words[i];
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

    sentenceWords.push([...(possibleWords ?? [])]);
  }

  return sentenceWords;
}
