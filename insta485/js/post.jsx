import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import Likes from "./likes"; // Import the Likes component
import Comments from "./comments"; // Import the Comments component

dayjs.extend(relativeTime);
dayjs.extend(utc);

export default function Post({ url }) {
  const [comments, setComments] = useState([]);
  const [created, setCreated] = useState("");
  const [imgUrl, setImgUrl] = useState("");
  const [likes, setLikes] = useState({
    numLikes: 0,
    lognameLikesThis: false,
    url: "", // Store the URL for likes API
  });
  const [owner, setOwner] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [postid, setPostId] = useState("");
  const [ownerShowUrl, setOwnerShowUrl] = useState("");
  const [postShowUrl, setPostShowUrl] = useState("");
  const [loadingLike, setLoadingLike] = useState(false);
  //  "url": "/api/v1/posts/3/"

  useEffect(() => {
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        if (!ignoreStaleRequest) {
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setComments(data.comments);
          setCreated(data.created);
          setLikes({
            numLikes: data.likes.numLikes,
            lognameLikesThis: data.likes.lognameLikesThis,
            url: data.likes.url, // Set the correct URL for likes
          });
          setOwnerImgUrl(data.ownerImgUrl);
          setPostId(data.postid);
          setOwnerShowUrl(data.ownerShowUrl);
          setPostShowUrl(data.postShowUrl);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      ignoreStaleRequest = true;
    };
  }, [url]);

  const handleLikeToggle = () => {
    setLoadingLike(true);
    console.log(loadingLike);
    if (likes.lognameLikesThis) {
      // If already liked, make DELETE request to remove the like
      setLikes((prev) => ({
        ...prev,
        numLikes: likes.numLikes - 1,
        lognameLikesThis: false,
      }));
    } else {
      // If not liked, make POST request to create a new like
      setLikes((prev) => ({
        ...prev,
        numLikes: likes.numLikes + 1,
        lognameLikesThis: true,
      }));
    }
    if (likes.lognameLikesThis) {
      fetch(likes.url, {
        method: "DELETE",
      })
        .then((response) => {
          if (response.ok) {
            setLikes({
              numLikes: likes.numLikes - 1,
              lognameLikesThis: false,
              url: "", // Clear the like URL after deletion
            });
          }
        })
        .catch((error) => console.log(error))
        .finally(() => setLoadingLike(false));
      console.log(loadingLike);
    } else {
      fetch(`/api/v1/likes/?postid=${postid}`, {
        method: "POST",
      })
        .then((response) => response.json())
        .then((data) => {
          setLikes({
            numLikes: likes.numLikes + 1,
            lognameLikesThis: true,
            url: data.url, // Set the new like URL after creation
          });
        })
        .catch((error) => console.log(error))
        .finally(() => setLoadingLike(false));
      console.log(loadingLike);
    }
  };

  // Double-click to like functionality
  const handleDoubleClickLike = () => {
    if (!likes.lognameLikesThis) {
      handleLikeToggle();
    }
  };

  const humanReadableCreated = dayjs.utc(created).local().fromNow();

  return (
    <div className="post">
      <a href={ownerShowUrl}>
        <img
          src={ownerImgUrl}
          alt="post owner pfp"
          width="30"
          height="30"
          style={{ verticalAlign: "middle" }}
        />
        <b>{owner}</b>
      </a>
      <a
        href={postShowUrl}
        className="graylink"
        style={{ float: "right", verticalAlign: "text-top" }}
      >
        {humanReadableCreated}
      </a>
      <p>
        <img
          src={imgUrl}
          alt={`post ${postid}`}
          onDoubleClick={handleDoubleClickLike} // Handle double-click
        />
      </p>

      {/* Render the Likes component */}
      <Likes
        numLikes={likes.numLikes}
        onLikeToggle={handleLikeToggle} // Pass handleLikeToggle function to Likes component
        liked={likes.lognameLikesThis}
        loadingLike={loadingLike}
      />

      {/* Render the Comments component and pass necessary props */}
      <Comments
        comments={comments}
        postid={Number(postid)}
        setComments={setComments}
        // curUser={'awdeorio'}
      />
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
