import { Trie } from "../lib/trie";
import fingermap from "../static/fingermap.json";

const start = performance.now();

// Load all words into a set
const words = new Set(
  // Load words from words.txt
  (await fetch("/words.txt").then((res) => res.text()))
    // Split words by new line
    .toLowerCase()
    .replace(/\s+/g, "\n")
    .split("\n")
    // Filter out words that contain characters not in the fingermap
    .filter((word) => word.split("").every((letter) => letter in fingermap))
);

const trie = Trie.buildTrie([...words]);

console.log(`Ready in ${performance.now() - start}ms`);

export default trie;
