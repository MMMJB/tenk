import { useState, useEffect, useCallback } from "react";

import Display from "./Display";

// TODO: Switch with control key on arduino.py
const CTRL_KEY = "Tab";

export default function Controller() {
  const [mode, setMode] = useState<"typing" | "waiting">("waiting");
  const [keys, setKeys] = useState<number[]>([]);

  // TODO: Switch with output from arduino.py
  const onKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === CTRL_KEY) {
        setMode((p) => (p === "typing" ? "waiting" : "typing"));
        setKeys([]);
      } else if (mode === "waiting") return;

      if (isNaN(parseInt(e.key))) return;

      setKeys((p) => [...p, parseInt(e.key)]);
    },
    [mode]
  );

  useEffect(() => {
    window.addEventListener("keydown", onKeyDown);

    return () => {
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [mode]);

  return <Display mode={mode} keys={keys} />;
}
