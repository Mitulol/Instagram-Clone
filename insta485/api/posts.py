"""REST API for posts."""
# import os
# import pathlib
import hashlib
from urllib.parse import urlparse
from functools import wraps
import flask
import insta485


def access_control(username: str, password: str):
    """Check authentication and enforce access control."""
    # Define valid username and password (in reality, check the database)
    connection = insta485.model.get_db()

    cur = connection.execute(
      "SELECT password AS passworddd FROM users WHERE username = ?",
      (username,)
    )
    db_password = cur.fetchone()

    # Extract the salt and hash from the stored password
    stored_hash = db_password['passworddd']
    algorithm, salt, stored_hash_value = stored_hash.split('$')

    # Hash the provided password with the same salt
    hashed_password = hash_password_sha512(password, salt)
    if hashed_password != stored_hash_value:
        return error_response("Forbidden", 403)
    # If authentication passes, return None to indicate success
    print(f"Using algorithm: {algorithm}")
    return None


def hash_password_sha512(password, salt):
    """Hash a password with SHA-512 and a salt."""
    return hashlib.sha512((salt + password).encode('utf-8')).hexdigest()


def error_response(message, status_code):
    """Return error_response."""
    return flask.jsonify({
        "message": message,
        "status_code": status_code
    }), status_code


def require_login(func):
    """Return require_login."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if the user is logged in via session
        if 'username' in flask.session:
            username = flask.session['username']
            password = None  # You can set password to None as it's not needed
        elif 'authorization' in flask.request.headers:
            auth = flask.request.authorization
            if auth:
                username = auth["username"]
                password = auth["password"]
        # Perform access control to check if the username/password is valid
                auth_response = access_control(username, password)
                if auth_response:
                    return auth_response
            else:
                return error_response("Forbidden", 403)
        else:
            return error_response("Forbidden", 403)

        # Store username in kwargs to pass it to the route function
        kwargs['username'] = username
        return func(*args, **kwargs)
    return wrapper


@insta485.app.route('/api/v1/')
def get_services():
    """Return available services."""
    services = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**services)


@insta485.app.route('/api/v1/posts/')
@require_login
def get_posts_10(username):
    """Return the 10 newest posts."""
    connection = insta485.model.get_db()

    # Get query parameters
    postid_lte = flask.request.args.get("postid_lte", type=int)
    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)

    # Validate size and page
    if size <= 0 or page < 0:
        return flask.jsonify({"error": "Invalid size or page parameter"}), 400

    # Determine the offset for pagination
    offset = page * size

    # Fetch postid_lte if not provided
    if postid_lte is None:
        postid_lte = get_latest_postid(connection, username)

    # Fetch posts
    posts = fetch_posts(connection, username, postid_lte, size, offset)

    # Prepare the results and next URL
    results = prepare_results(posts)
    next_url = calculate_next_url(posts, size, postid_lte, page)

    # Get the current URL
    full_path = get_full_path()

    # Create the response
    response = {
        "next": next_url,
        "results": results,
        "url": full_path,
    }

    return flask.jsonify(**response)


def get_latest_postid(connection, username):
    """Fetch the latest post ID for the given username."""
    query = """
        SELECT postid
        FROM posts
        WHERE (owner = ? OR owner IN (
            SELECT username2 FROM following WHERE username1 = ?
        ))
        ORDER BY postid DESC LIMIT 1
    """
    params = [username, username]
    cur = connection.execute(query, params)
    post = cur.fetchone()
    return post['postid'] if post else None


def fetch_posts(connection, username, postid_lte, size, offset):
    """Fetch posts with pagination and filtering."""
    query = """
        SELECT postid, owner
        FROM posts
        WHERE (owner = ? OR owner IN (
            SELECT username2 FROM following WHERE username1 = ?
        ))
        AND postid <= ?
        ORDER BY postid DESC LIMIT ? OFFSET ?
    """
    params = [username, username, postid_lte, size, offset]
    cur = connection.execute(query, params)
    return cur.fetchall()


def prepare_results(posts):
    """Prepare the results for the response."""
    return [
        {"postid": post["postid"], "url": f"/api/v1/posts/{post['postid']}/"}
        for post in posts
    ]


def calculate_next_url(posts, size, postid_lte, page):
    """Calculate the next URL for pagination."""
    if len(posts) == size:
        next_url = (
            f"/api/v1/posts/?size={size}&page={page+1}"
            f"&postid_lte={postid_lte}"
        )
        return next_url
    return ""


def get_full_path():
    """Get the full request path."""
    parsed_url = urlparse(flask.request.url)
    full_path = parsed_url.path
    if parsed_url.query:
        full_path += "?" + parsed_url.query
    return full_path


@insta485.app.route('/api/v1/posts/<int:postid>/')
@require_login
def get_post(postid, username):
    """Return details for a specific post by postid."""
    connection = insta485.model.get_db()

    # Fetch the post with the given postid
    cur = connection.execute(
        """
        SELECT posts.filename, posts.owner, users.filename
        AS owner_img, posts.created AS timestamp
        FROM posts
        JOIN users ON posts.owner = users.username
        WHERE posts.postid = ?;
        """,
        (postid,)
    )

    post = cur.fetchone()

    # Return 404 if the post doesn't exist
    if post is None:
        return flask.jsonify({
            "message": "Not Found",
            "status_code": 404
        }), 404

    # Fetch comments for the post
    cur = connection.execute(
        """
        SELECT commentid, owner, text
        FROM comments
        WHERE postid = ?
        ORDER BY commentid
        """,
        (postid,)
    )

    comments = cur.fetchall()

    comments_list = [
        {
            "commentid": comment["commentid"],
            "lognameOwnsThis": (comment["owner"] == username),
            "owner": comment["owner"],
            "ownerShowUrl": f"/users/{comment['owner']}/",
            "text": comment["text"],
            "url": f"/api/v1/comments/{comment['commentid']}/"
        } for comment in comments
    ]

    # Fetch likes for the post
    cur = connection.execute(
        """
        SELECT COUNT(*) AS numLikes
        FROM likes
        WHERE postid = ?
        """,
        (postid,)
    )

    likes = cur.fetchone()

    cur = connection.execute(
        """
        SELECT likeid
        FROM likes
        WHERE postid = ?
        AND owner = ?
        """,
        (postid, username)
    )

    user_like = cur.fetchone()

    # Prepare the likes object
    if user_like:
        likes_url = f"/api/v1/likes/{user_like['likeid']}/"
        logname_likes_this = True
    else:
        likes_url = None
        logname_likes_this = False

    # Prepare the response context
    context = {
        "comments": comments_list,
        "comments_url": f"/api/v1/comments/?postid={postid}",
        "created": post["timestamp"],
        "imgUrl": f"/uploads/{post['filename']}",
        "likes": {
            "lognameLikesThis": logname_likes_this,
            "numLikes": likes["numLikes"],
            "url": likes_url
        },
        "owner": post["owner"],
        "ownerImgUrl": f"/uploads/{post['owner_img']}",
        "ownerShowUrl": f"/users/{post['owner']}/",
        "postShowUrl": f"/posts/{postid}/",
        "postid": postid,
        "url": flask.request.path,
    }
    # Return the JSON response
    return flask.jsonify(context), 200


@insta485.app.route('/api/v1/likes/', methods=['POST'])
@require_login
def create_like(username):
    """Create a like for a post."""
    connection = insta485.model.get_db()

    # Get the post ID from query params
    postid = flask.request.args.get("postid")

    # Check if the post exists
    post = connection.execute(
        "SELECT * FROM posts WHERE postid = ?",
        (postid,)
    ).fetchone()

    if post is None:
        return flask.jsonify({
            "message": "Not Found",
            "status_code": 404
        }), 404

    # Check if the like already exists
    like = connection.execute(
        "SELECT likeid FROM likes WHERE postid = ? AND owner = ?",
        (postid, username)
    ).fetchone()

    if like:
        # If the like already exists, return it with a 200 response
        return flask.jsonify({
            "likeid": like["likeid"],
            "url": f"/api/v1/likes/{like['likeid']}/"
        }), 200

    # Otherwise, create a new like
    cursor = connection.execute(
        "INSERT INTO likes (postid, owner) VALUES (?, ?)",
        (postid, username)
    )
    likeid = cursor.lastrowid

    # Return the new like with a 201 response
    return flask.jsonify({
        "likeid": likeid,
        "url": f"/api/v1/likes/{likeid}/"
    }), 201


@insta485.app.route('/api/v1/likes/<int:likeid>/', methods=['DELETE'])
@require_login
def delete_like(likeid, username):
    """Delete a like."""
    connection = insta485.model.get_db()
    # Check if the like exists
    like = connection.execute(
        "SELECT * FROM likes WHERE likeid = ?",
        (likeid,)
    ).fetchone()

    if like is None:
        return flask.jsonify({
            "message": "Not Found",
            "status_code": 404
        }), 404

    # Check if the user owns the like
    if like["owner"] != username:
        return flask.jsonify({
            "message": "Forbidden: You don't own this like",
            "status_code": 403
        }), 403

    # Delete the like
    connection.execute(
        "DELETE FROM likes WHERE likeid = ?",
        (likeid,)
    )

    # Return 204 No Content
    return "", 204


@insta485.app.route('/api/v1/comments/', methods=['POST'])
@require_login
def create_comment(username):
    """Add a new comment to a post."""
    connection = insta485.model.get_db()

    # Get postid from the query string
    postid = flask.request.args.get('postid')
    if postid is None:
        return flask.jsonify({
            "message": "Missing postid parameter",
            "status_code": 400
        }), 400

    # Get the comment text from the request JSON
    request_json = flask.request.get_json(force=True)
    text = request_json.get("text", "")
    if not text:
        return flask.jsonify({
            "message": "Missing comment text",
            "status_code": 400
        }), 400

    # Ensure the post exists
    post = connection.execute(
        "SELECT * FROM posts WHERE postid = ?",
        (postid,)
    ).fetchone()

    if post is None:
        return flask.jsonify({
            "message": "Post not found",
            "status_code": 404
        }), 404

    # Insert the comment into the database
    connection.execute(
        "INSERT INTO comments (owner, postid, text) VALUES (?, ?, ?)",
        (username, postid, text)
    )

    # Retrieve the commentid of the most recent insert
    commentid = connection.execute(
        "SELECT last_insert_rowid()"
    ).fetchone()['last_insert_rowid()']

    # Build the response data
    response_data = {
        "commentid": commentid,
        "lognameOwnsThis": True,
        "owner": username,
        "ownerShowUrl": f"/users/{username}/",
        "text": text,
        "url": f"/api/v1/comments/{commentid}/"
    }

    # Return 201 Created with the new comment data
    return flask.jsonify(response_data), 201


@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
@require_login
def delete_comment(commentid, username):
    """Delete a comment by its ID."""
    connection = insta485.model.get_db()

    # Ensure the comment exists
    comment = connection.execute(
        "SELECT * FROM comments WHERE commentid = ?",
        (commentid,)
    ).fetchone()

    if comment is None:
        return flask.jsonify({
            "message": "Comment not found",
            "status_code": 404
        }), 404

    # Ensure the user owns the comment
    if comment['owner'] != username:
        return flask.jsonify({
            "message": "Forbidden: You do not own this comment",
            "status_code": 403
        }), 403

    # Delete the comment from the database
    connection.execute(
        "DELETE FROM comments WHERE commentid = ?",
        (commentid,)
    )

    # Return 204 No Content
    return '', 204
