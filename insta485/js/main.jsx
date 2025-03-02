// import React, { StrictMode } from "react";
// import { createRoot } from "react-dom/client";
// import Post from "./post";

// // Create a root
// const root = createRoot(document.getElementById("reactEntry"));

// // This method is only called once
// // Insert the post component into the DOM
// root.render(
//   <StrictMode>
//     <Post url="/api/v1/posts/3/" />
//   </StrictMode>,
// );

import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import PostList from "./postList"; // Import the PostList component

// Create a root
const root = createRoot(document.getElementById("reactEntry"));

// This method is only called once
// Insert the PostList component into the DOM
root.render(
  <StrictMode>
    <PostList url="/api/v1/posts/" /> {/* Render the PostList component here */}
  </StrictMode>,
);
