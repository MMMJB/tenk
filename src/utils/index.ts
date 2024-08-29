import * as _ from "lodash";

import fingermap from "../static/fingermap.json";

export type Letter = keyof typeof fingermap;
export type Finger = (typeof fingermap)[Letter];

// Group letters by finger
export const groupedFingerMap = _.groupBy(
  Object.keys(fingermap),
  (key) => fingermap[key as Letter]
);

// Get finger for letter
export function letterToFinger(letter: Letter): Finger {
  return fingermap[letter];
}

// Get possible letters for finger
export function fingerToPossibleLetters(finger: Finger): Letter[] {
  return groupedFingerMap[finger] as Letter[];
}
