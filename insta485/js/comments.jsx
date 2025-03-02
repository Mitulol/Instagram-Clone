import React, { useState } from "react";
import PropTypes from "prop-types";

export default function Comments({ comments, postid, setComments }) {
  const [newComment, setNewComment] = useState(""); // State for new comment input
  const [loadingComment, setLoadingComment] = useState(false);

  const handleCommentChange = (event) => {
    setNewComment(event.target.value); // Update the new comment state
  };

  const handleCommentSubmit = (event) => {
    event.preventDefault(); // Prevent the page from reloading

    if (newComment.trim() === "") return; // Ignore empty comments
    // console.log(newComment);

    // const tempCommentObject = {
    //   commentid: 0,
    //   owner: curUser,
    //   text: newComment.trim(),
    //   lognameOwnsThis: true,
    // };
    // setComments([...comments, tempCommentObject]);

    setLoadingComment(true);

    // Make API call to add the comment
    fetch(`/api/v1/comments/?postid=${postid}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: newComment,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Assuming the response returns the new comment data with commentid
        const newCommentObject = {
          commentid: data.commentid,
          owner: data.owner,
          text: data.text,
          lognameOwnsThis: data.lognameOwnsThis,
        };

        // Update comments state with the newly added comment
        setComments([...comments, newCommentObject]);
        // setComments(comments.filter((com) => com.commentid !== 0));

        // Reset the input field
        setNewComment("");
      })
      .catch((error) => console.log(error))

      .finally(() => setLoadingComment(false)); // Reset loading state
  };

  const handleCommentDelete = (commentid) => {
    // Make API call to delete the comment
    fetch(`/api/v1/comments/${commentid}/`, {
      method: "DELETE",
    })
      .then((response) => {
        if (response.ok) {
          // Update comments state to remove the deleted comment
          setComments(comments.filter((com) => com.commentid !== commentid));
        } else {
          console.log("Failed to delete comment");
        }
      })
      .catch((error) => console.log(error));
  };

  return (
    <div className="comments">
      {/* Comment Form */}
      {loadingComment ? (
        "Loading..."
      ) : (
        <form data-testid="comment-form" onSubmit={handleCommentSubmit}>
          <input
            type="text"
            value={newComment}
            onChange={handleCommentChange}
            data-testid="comment-text"
            placeholder="Add a comment..."
            disabled={loadingComment}
          />
        </form>
      )}

      {/* Render comments */}
      {comments.map((com) => (
        <div key={com.commentid}>
          <span data-testid="comment-text">
            <a href={com.ownerShowUrl}>{com.owner}</a>: {com.text}
          </span>
          {com.lognameOwnsThis && ( // Show delete button if the logged-in user owns the comment
            <button
              type="button"
              data-testid="delete-comment-button"
              onClick={() => handleCommentDelete(com.commentid)}
            >
              Delete
            </button>
          )}
        </div>
      ))}
    </div>
  );
}

Comments.propTypes = {
  comments: PropTypes.arrayOf(
    PropTypes.shape({
      commentid: PropTypes.number.isRequired,
      owner: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      lognameOwnsThis: PropTypes.bool.isRequired,
    }),
  ).isRequired,
  postid: PropTypes.number.isRequired,
  setComments: PropTypes.func.isRequired,
};
