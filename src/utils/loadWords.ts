import { Trie } from "../lib/trie";
import fingermap from "../static/fingermap.json";
import { letterToFinger } from ".";

import type { Letter } from ".";

const startWordlistLoad = performance.now();

// Load all words into a set
const words = new Set(
  // Load words from words.txt
  (await fetch("/words.txt").then((res) => res.text()))
    // Split words by new line
    .toLowerCase()
    .split(/\s+/g)
    // Filter out words that contain characters not in the fingermap
    .filter((word) => word.split("").every((letter) => letter in fingermap))
);

const fingerCombinations: Record<string, string[]> = {};
for (const word of words) {
  const fingerCombination = word
    .split("")
    .map((letter) => letterToFinger(letter as Letter))
    .join("");

  if (!(fingerCombination in fingerCombinations)) {
    fingerCombinations[fingerCombination] = [word];
  } else {
    fingerCombinations[fingerCombination].push(word);
  }
}

const fingerCombinationsWithOneWord = Object.values(fingerCombinations).filter(
  (words) => words.length === 1
);

console.log(fingerCombinationsWithOneWord.flat());

console.info(`Loaded word list (${performance.now() - startWordlistLoad}ms)`);

const startTrieBuild = performance.now();

const trie = Trie.buildTrie([...words]);

console.info(
  `Processed word list (${words.size} words in ${
    performance.now() - startTrieBuild
  }ms)`
);

export default trie;
export { words };
