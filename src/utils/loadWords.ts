import { Trie } from "../lib/trie";
import fingermap from "../static/fingermap.json";

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

console.info(`Loaded word list (${performance.now() - startWordlistLoad}ms)`);

const startTrieBuild = performance.now();

const trie = Trie.buildTrie([...words]);

console.info(
  `Processed word list (${words.size} words in ${
    performance.now() - startTrieBuild
  }ms)`
);

export default trie;
