import "./index.css";

// import { StrictMode } from 'react'
import App from "./App.tsx";
import Keyboard from "./components/Keyboard.tsx";

import { createRoot } from "react-dom/client";
import trie from "./utils/loadWords";

createRoot(document.getElementById("root")!).render(
  // <StrictMode>
  <>
    <Keyboard />
    <App />
  </>
  //</StrictMode>,
);

export { trie };
