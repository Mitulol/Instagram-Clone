import React, { useState, useEffect } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post"; // Import the Post component

export default function PostList() {
  const [posts, setPosts] = useState([]); // Store all posts
  const [nextUrl, setNextUrl] = useState("/api/v1/posts/"); // URL to fetch the next set of posts
  const [hasMore, setHasMore] = useState(true); // Track if there are more posts to load

  const fetchInitialPosts = () => {
    fetch("/api/v1/posts/", { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setPosts(data.results); // Set initial posts
        setNextUrl(data.next); // Set the URL for the next set of posts
        setHasMore(data.next !== null); // Determine if more posts are available
      })
      .catch((error) => console.log(error));
  };

  // Fetch initial posts when the component mounts
  useEffect(() => {
    fetchInitialPosts();
  }, []);

  // Fetch more posts when the user scrolls to the bottom
  const fetchMorePosts = () => {
    if (!nextUrl) return; // If there are no more posts to load, stop

    fetch(nextUrl, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setPosts((prevPosts) => [...prevPosts, ...data.results]); // Append new posts to the list
        setNextUrl(data.next); // Update the next URL for more posts
        setHasMore(data.next !== null); // Check if there are more posts to load
      })
      .catch((error) => console.log(error));
  };

  return (
    <div>
      <InfiniteScroll
        dataLength={posts.length} // Current number of posts
        next={fetchMorePosts} // Function to call when scrolled to the bottom
        hasMore={hasMore} // Check if more posts are available
        loader={<h4>Loading more posts...</h4>} // Loader to display while fetching more posts
        endMessage={<p>No more posts to display</p>} // Message to display when no more posts
      >
        {/* Render each post */}
        {posts.map((post) => (
          <Post key={post.postid} url={`/api/v1/posts/${post.postid}`} />
        ))}
      </InfiniteScroll>
    </div>
  );
}
