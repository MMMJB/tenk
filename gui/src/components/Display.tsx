import { useRef, useEffect } from "react";

const modeText = {
  typing: "Typing...",
  waiting: "Waiting for input...",
};

export default function Display({
  keys,
  mode,
}: {
  keys: number[];
  mode: "typing" | "waiting";
}) {
  const containerRef = useRef<HTMLDivElement>(null);

  const displayMode = keys.length && mode === "typing" ? "typing" : "waiting";
  const displayClass =
    displayMode + (displayMode === "waiting" ? " glass" : "");

  useEffect(() => {
    if (!containerRef.current || !keys.length) return;

    containerRef.current.scrollTo({
      left: containerRef.current.scrollWidth,
      behavior: "smooth",
    });
  }, [keys]);

  return (
    <div ref={containerRef} id="display" className={displayClass}>
      <div id="display__keys">
        {keys.map((key, index) => (
          <span key={index} className="key glass">
            {key}
          </span>
        ))}
      </div>
      <div id="display__mode">{modeText[displayMode]}</div>
    </div>
  );
}
