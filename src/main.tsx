import "./index.css";

// import { StrictMode } from 'react'
import Visualization from "./routes/Visualization";
import Testing from "./routes/Testing";
import Chat from "./routes/Chat";
import { RouterProvider } from "react-router-dom";

import { createRoot } from "react-dom/client";
import { createBrowserRouter } from "react-router-dom";
import trie, { words } from "./utils/loadWords";

const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <>
        <a href="/visualization">Sentence visualization</a>
        <a href="/testing">Live sentence testing</a>
        <a href="/chat">Chat</a>
      </>
    ),
  },
  {
    path: "/visualization",
    element: <Visualization />,
  },
  {
    path: "/testing",
    element: <Testing />,
  },
  {
    path: "/chat",
    element: <Chat />,
  },
]);

createRoot(document.getElementById("root")!).render(
  // <StrictMode>
  <RouterProvider router={router} />
  //</StrictMode>,
);

export { trie, words };
