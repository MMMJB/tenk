import { fingerToPossibleLetters, letterToFinger } from ".";

import type { Finger } from ".";
import type { Trie } from "../lib/trie";

// Get possible words for fingers
export function fingersToPossibleWords(
  finger: Finger,
  trie: Trie,
  wordList?: Set<string>,
  isFirstLetter = false
): Set<string> {
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
export function fingersToPossibleSentences(
  fingers: Finger[],
  trie: Trie
): string[][] {
  const startSentenceTime = performance.now();

  const spaceFinger = letterToFinger(" ");

  // Split fingers into words by space
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

    // Narrow down list of possible words as each finger is added
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

  console.info(
    `Finished sentence prediction (${performance.now() - startSentenceTime}ms)`
  );

  return sentenceWords;
}

type APIResponse = {
  input_text: string;
  word_probabilities: [string, number][];
};

export async function rankNextWords(
  context: string,
  options: string[]
): Promise<Record<string, number>> {
  // If there's only one option, return it
  if (options.length === 1) {
    return { [options[0]]: 1 };
  }

  const startPredictionTime = performance.now();

  // Returns a promise that resolves to the next word probabilities
  const response = await fetch(`${import.meta.env.VITE_API_ENDPOINT}/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text: context, options }),
  });
  const data = (await response.json()) as APIResponse;

  const wordProbabilities = Object.fromEntries(data.word_probabilities);

  console.info(
    `Finished word prediction (${performance.now() - startPredictionTime}ms)`
  );

  return wordProbabilities;
}

type SentencePrediction = {
  sentence: string;
  probabilities: Record<string, number>[];
};

export async function predictSentence(
  anchor: string,
  words: string[][]
): Promise<SentencePrediction> {
  const startPredictionTime = performance.now();

  let context = anchor;
  const predictions: Record<string, number>[] = [];

  for (const wordList of words) {
    const sortedWordProbabilities = await rankNextWords(context, wordList);

    predictions.push(sortedWordProbabilities);

    const nextWord = Object.entries(sortedWordProbabilities)[0][0];
    context += ` ${nextWord}`;
  }

  console.info(
    `Finished sentence prediction (${
      performance.now() - startPredictionTime
    }ms)`
  );

  return {
    sentence: context,
    probabilities: predictions,
  };
}
