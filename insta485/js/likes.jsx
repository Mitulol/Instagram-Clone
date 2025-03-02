import React from "react";
import PropTypes from "prop-types";

function Likes({ numLikes, onLikeToggle, liked, loadingLike }) {
  return (
    <div>
      <p>{numLikes === 1 ? "1 like" : `${numLikes} likes`}</p>
      {loadingLike ? (
        "Loading..."
      ) : (
        <button
          type="button"
          data-testid="like-unlike-button"
          onClick={onLikeToggle}
        >
          {liked ? "Unlike" : "Like"}
        </button>
      )}
    </div>
  );
}

Likes.propTypes = {
  numLikes: PropTypes.number.isRequired,
  onLikeToggle: PropTypes.func.isRequired,
  liked: PropTypes.bool.isRequired,
  loadingLike: PropTypes.bool.isRequired,
};

export default Likes;

// import React from "react";

// function Likes({ numLikes, onLikeToggle, liked }) {
//   return (
//     <div>
//       <p>{numLikes === 1 ? "1 like" : `${numLikes} likes`}</p>
//       <button data-testid="like-unlike-button" onClick={onLikeToggle}>
//         {liked ? "Unlike" : "Like"}
//       </button>
//     </div>
//   );
// }

// export default Likes;
