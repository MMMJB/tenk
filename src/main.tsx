import "./index.css";

// import { StrictMode } from 'react'
import App from "./App.tsx";

import { createRoot } from "react-dom/client";
import trie from "./utils/loadWords";

createRoot(document.getElementById("root")!).render(
  // <StrictMode>
  <App />
  //</StrictMode>,
);

export { trie };
