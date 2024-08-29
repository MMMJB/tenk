import { useState, useEffect } from "react";

import type { Letter } from "../utils";

import { letterToFinger } from "../utils";

function Key({ n }: { n: number }) {
  const [pressed, setPressed] = useState(false);

  function onKeyDown(e: KeyboardEvent) {
    if (e.ctrlKey || e.metaKey) return;

    const finger = letterToFinger(e.key as Letter);
    if (finger !== n) return;

    setPressed(true);
  }

  function onKeyUp() {
    setPressed(false);
  }

  useEffect(() => {
    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("keyup", onKeyUp);

    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("keyup", onKeyUp);
    };
  }, [onKeyDown, onKeyUp]);

  return <div className={`key ${pressed && "pressed"}`} />;
}

export default function Keyboard() {
  return (
    <div className="keyboard">
      {Array.from({ length: 10 }).map((_, i) => (
        <Key key={String(i)} n={i} />
      ))}
    </div>
  );
}
