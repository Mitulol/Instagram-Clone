"""
Insta485 index (main) view.

URLs include:
/
"""
import uuid
import os
import pathlib
import hashlib
import flask
import arrow
import insta485


@insta485.app.route('/')
def show_index():
    """Display / route."""
    username = flask.session.get('username')

    if username is None:
        return flask.redirect(flask.url_for('show_login_account'))

    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    logname = username
    cur = connection.execute(
        "SELECT username, fullname "
        "FROM users "
        "WHERE username != ?",
        (logname, )
    )

    cur = connection.execute(
        """
        SELECT posts.postid AS postid,
            posts.owner AS owner,
            (SELECT users.filename
                FROM users
                WHERE users.username = posts.owner) AS owner_img_url,
            TRIM(posts.filename) AS img_url,
            posts.created AS timestamp,
            (SELECT COUNT(*)
                FROM likes
                WHERE likes.postid = posts.postid) AS likes
            FROM posts
            WHERE posts.owner = ?
        UNION
        SELECT posts.postid AS postid,
            posts.owner AS owner,
            (SELECT users.filename
                FROM users
                WHERE users.username = posts.owner) AS owner_img_url,
            TRIM(posts.filename) AS img_url,
            posts.created AS timestamp,
            (SELECT COUNT(*)
                FROM likes
                WHERE likes.postid = posts.postid) AS likes
            FROM posts JOIN following
            ON posts.owner = following.username2
            WHERE following.username1 = ?
        ORDER BY posts.postid DESC;
        """, (logname, logname)
    )

    # No comments in posts rn.
    posts = cur.fetchall()
    print(posts)

    # Adding comments into posts.
    for post in posts:
        cur = connection.execute(
            """
            SELECT owner, text
            FROM comments
            WHERE postid = ?
            ORDER BY commentid ASC;
            """, (post['postid'],)
        )
        temp_time = arrow.get(post['timestamp'])
        post['timestamp'] = temp_time.humanize()
        post['comments'] = cur.fetchall()

        cur = connection.execute(
            """
            SELECT COUNT(*)
            FROM likes
            WHERE likes.owner = ? AND likes.postid = ?;
            """,
            (logname, post['postid'])
        )

        has_liked = cur.fetchone()['COUNT(*)'] > 0

        post['logname_has_liked'] = has_liked

    # Add database info to context
    context = {"logname": logname,
               "posts": posts,
               }
    return flask.render_template("index.html", **context)


# @insta485.app.route('/uploads/<filename>')
# def show_image(filename, uploads_url):
#     if uploads_url != "yes":
#         return flask.send_from_directory
#         (flask.current_app.config['UPLOAD_FOLDER'],
#         filename, as_attachment = False)
#         # return flask.send_from_directory
#               ('../var/uploads/', filename, as_attachment = True)
#     else:
#         context = {"img_url": filename}
#         print(f"Accessing file: {filename}")
#         print(f"Value of uploads_url: {uploads_url}")
#         return flask.render_template("uploads.html", **context)


@insta485.app.route('/uploads/<filename>')
def show_image(filename):
    """Show the image."""
    username = flask.session.get('username')
    if username is None:
        flask.abort(403)
    # If user is authenticated, attempt to serve the file
    try:
        return flask.send_from_directory(
                flask.current_app.config['UPLOAD_FOLDER'],
                filename, as_attachment=True)
    except FileNotFoundError:
        # If the file does not exist, return 404 Not Found
        flask.abort(404)

# @insta485.app.route('/uploads2/<filename>')
# def show_uploads(filename):
#     context = {"img_url": filename}
#     return flask.render_template("uploads.html", **context)


@insta485.app.route('/users/<user_url_slug>/')
def show_user(user_url_slug):
    """Show the user."""
    username = flask.session.get('username')
    logname = username

    if username is None:
        return flask.redirect(flask.url_for('show_login_account'))

    # Connect to database
    connection = insta485.model.get_db()

    cur = connection.execute(" SELECT * FROM users WHERE username = ?",
                             (user_url_slug,))

    user = cur.fetchone()

    # Check for if the user exists in the database. Not if user is None
    if user is None:
        # Abort with 404 if the user does not exist
        flask.abort(404)

    # Query database
    user = user_url_slug
    cur = connection.execute(
        "SELECT username, fullname "
        "FROM users "
        "WHERE username = ?",
        (user, ))
    userdata = cur.fetchall()

    cur = connection.execute(
        "SELECT COUNT(*) FROM following WHERE username1 = ? AND username2 = ?",
        (logname, user))
    # (logname, username)
    result = cur.fetchone()
    print(result)
    logname_follows_username = result['COUNT(*)'] > 0

    cur = connection.execute(
        "SELECT COUNT(*) FROM following WHERE username1 = ?",
        (user,))
    # Number of users 'username' is following
    following_count = cur.fetchone()['COUNT(*)']

    cur = connection.execute(
        "SELECT COUNT(*) FROM following WHERE username2 = ?",
        (user,))
    # Number of users following 'username'
    followers_count = cur.fetchone()['COUNT(*)']

    cur = connection.execute(
        "SELECT COUNT(*) FROM posts WHERE owner = ?",
        (user,))
    total_posts = cur.fetchone()['COUNT(*)']

    cur = connection.execute(
        "SELECT postid, filename AS img_url FROM posts WHERE owner = ?",
        (user,))
    posts_data = cur.fetchall()

    # Prepare the post data with image URLs
    # posts = [
    #     {"postid": post["postid"],
    #     "img_url": f"/uploads/{post['filename']}"
    # } for post in posts_data]
    print(userdata)
    context = {
        "logname": logname,
        "username": user,
        "logname_follows_username": logname_follows_username,
        "fullname": userdata[0]['fullname'],
        "following": following_count,
        "followers": followers_count,
        "total_posts": total_posts,
        "posts": posts_data
    }
    return flask.render_template("user.html", **context)


@insta485.app.route('/users/<user_url_slug>/followers/')
def show_user_followers(user_url_slug):
    """Show user followers, takes url slug as argument."""
    username = flask.session.get('username')

    if username is None:
        return flask.redirect(flask.url_for('show_login_account'))

    # Connect to database
    connection = insta485.model.get_db()

    cur = connection.execute(" SELECT * FROM users WHERE username = ?",
                             (user_url_slug,))

    user = cur.fetchone()

    # Check for if the user exists in the database. Not if user is None
    if user is None:
        # Abort with 404 if the user does not exist
        flask.abort(404)

    # Get logged-in username
    logname = username

    cur = connection.execute(
        "SELECT username1 FROM following WHERE username2 = ?",
        (user_url_slug,)
    )
    followers = cur.fetchall()

    # Initialize lists to hold data for each follower
    followers_data = []

    # Loop through each follower and fetch additional information
    for follower in followers:
        follower_username = follower['username1']

        # Fetch the profile image of the follower
        cur = connection.execute(
            "SELECT users.filename FROM users WHERE username = ?",
            (follower_username,)
        )
        follower_img = cur.fetchone()['filename']

        # Check if logname is following the follower
        cur = connection.execute(
            """
             SELECT COUNT(*)
             FROM following
             WHERE username1 = ? AND username2 = ?
            """,
            (logname, follower_username)
        )
        is_following = cur.fetchone()['COUNT(*)'] > 0  # True if count > 0

        # Build the follower's data dictionary
        followers_data.append({
            "username": follower_username,
            "user_img_url": follower_img,
            "logname_follows_username": is_following
        })
    # Create context with logname, username, and the followers' data
    context = {
        "logname": logname,
        # "username": user_url_slug,
        "followers": followers_data
    }
    return flask.render_template("followers.html", **context)


#############################################################

@insta485.app.route('/users/<user_url_slug>/following/')
def show_user_following(user_url_slug):
    """Show who the user is following."""
    username = flask.session.get('username')

    if username is None:
        return flask.redirect(flask.url_for('show_login_account'))

    # Connect to database
    connection = insta485.model.get_db()

    cur = connection.execute("SELECT * FROM users WHERE username = ?",
                             (user_url_slug,))

    user = cur.fetchone()

    if user is None:
        # Abort with 404 if the user does not exist
        flask.abort(404)

    # Get logged-in username
    logname = username

    cur = connection.execute(
        "SELECT username2 FROM following WHERE username1 = ?",
        (user_url_slug,)
    )
    followings = cur.fetchall()

    # Initialize lists to hold data for each follower
    following_data = []

    # Loop through each follower and fetch additional information
    for following in followings:
        following_username = following['username2']

        # Fetch the profile image of the follower
        cur = connection.execute(
            "SELECT users.filename FROM users WHERE username = ?",
            (following_username,)
        )
        following_img = cur.fetchone()['filename']

        # Check if logname is following the follower
        cur = connection.execute(
            ("SELECT COUNT(*)"
             "FROM following WHERE username1 = ? AND username2 = ?"),
            (logname, following_username)
        )
        is_following = cur.fetchone()['COUNT(*)'] > 0  # True if count > 0

        # Build the follower's data dictionary
        following_data.append({
            "username": following_username,
            "user_img_url": following_img,
            "logname_follows_username": is_following
        })
    # Create context with logname, username, and the followers' data
    context = {
        "logname": logname,
        "username": user_url_slug,
        "following": following_data
    }
    return flask.render_template("following.html", **context)


@insta485.app.route('/posts/<postid_url_slug>/')
def show_post(postid_url_slug):
    """Show a post."""
    username = flask.session.get('username')

    if username is None:
        return flask.redirect(flask.url_for('show_login_account'))

    # Connect to database
    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT owner, filename, created FROM posts WHERE postid = ?;",
        (postid_url_slug,))

    post = cur.fetchone()

    temp_time = arrow.get(post['created'])
    post['created'] = temp_time.humanize()
    owner = post['owner']
    cur = connection.execute("SELECT filename FROM users WHERE username = ?;",
                             (owner,))

    owner_img_url = cur.fetchone()['filename']

    cur = connection.execute("SELECT COUNT(*) FROM likes WHERE postid = ?;",
                             (postid_url_slug),)
    likes = cur.fetchone()['COUNT(*)']

    cur = connection.execute(
        """
            SELECT COUNT(*)
            FROM likes WHERE likes.owner = ?
            AND likes.postid = ?
        """,
        (username, postid_url_slug),
    )

    has_liked = cur.fetchone()['COUNT(*)'] > 0

    cur = connection.execute(
        """
        SELECT commentid, owner, text
        FROM comments
        WHERE postid = ?
        ORDER BY commentid ASC;
        """, (postid_url_slug,)
    )
    # used top one to get commentid
    # cur = connection.execute(
    #         """
    #         SELECT owner, text
    #         FROM comments
    #         WHERE postid = ?
    #         ORDER BY commentid ASC;
    #         """, (postid_url_slug,)
    #     )

    comments = cur.fetchall()

    context = {
        "logname": username,
        "postid": postid_url_slug,
        "owner": owner,
        "owner_img_url": owner_img_url,
        "img_url": post['filename'],
        "timestamp": post['created'],
        "likes": likes,
        "logname_has_liked": has_liked,
        "comments": comments
    }

    return flask.render_template("post.html", **context)


@insta485.app.route('/explore/')
def show_explore():
    """Show explore."""
    username = flask.session.get('username')

    if username is None:
        return flask.redirect(flask.url_for('show_login_account'))

    # Connect to database
    connection = insta485.model.get_db()

    # Get logged-in username
    logname = username

    # Get all users that the logged-in user is NOT following
    cur = connection.execute(
        """
        SELECT username, filename
        FROM users WHERE username != ?
        AND username NOT IN (
            SELECT username2 FROM following
            WHERE username1 = ?
        )
        """, (logname, logname)
    )

    # Fetch the result
    not_following = cur.fetchall()

    context = {
        "logname": logname,
        "not_following": [
            {
                "username": user['username'],
                "user_img_url": user['filename']
            }
            for user in not_following
        ]
    }

    return flask.render_template("explore.html", **context)


@insta485.app.route('/accounts/login/')
def show_login_account():
    """Show login."""
    # If the user is logged in, redirect to the home page
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))

    # Otherwise, show the login page
    return flask.render_template("login.html")


@insta485.app.route('/accounts/create/')
def show_create_account():
    """Show the create account."""
    # If the user is logged in, redirect to the account edit page
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_edit_account'))

    # Otherwise, render the account creation page
    return flask.render_template("create_account.html")


@insta485.app.route('/accounts/delete/')
def show_delete_account():
    """Show the account deletion page."""
    username = flask.session.get('username')

    if username is None:
        return flask.redirect(flask.url_for('show_login_account'))
    context = {'logname': username}
    return flask.render_template("delete_account.html", **context)


@insta485.app.route('/accounts/edit/')
def show_edit_account():
    """Show the edit account page."""
    # Assuming user is logged in, get their username
    username = flask.session.get('username')

    # If the user is not logged in, redirect to the login page
    if username is None:
        return flask.redirect(flask.url_for('show_login_account'))

    # Connect to the database
    connection = insta485.model.get_db()

    # Query the database for the current user's details
    cur = connection.execute(
        "SELECT fullname, email, filename FROM users WHERE username = ?",
        (username,)
    )
    user_info = cur.fetchone()

    # Set up the context with user details
    context = {
        "username": username,
        "fullname": user_info["fullname"],
        "email": user_info["email"],
        # Assuming the filename is the image path
        "user_img": user_info["filename"],
    }

    # Render the edit account template with user information
    return flask.render_template("edit_account.html", **context)


@insta485.app.route('/accounts/password/')
def show_password_account():
    """Show the password account."""
    username = flask.session.get('username')

    if username is None:
        return flask.redirect(flask.url_for('show_login_account'))

    context = {'logname': username}

    return flask.render_template("password_account.html", **context)


@insta485.app.route('/accounts/auth/')
def accounts_auth():
    """Make sure username is valid."""
    username = flask.session.get('username')

    if username is None:
        flask.abort(403)

    return flask.make_response('', 200)


LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route("/likes/", methods=["POST"])
def update_likes():
    """Update number of likes on a post."""
    LOGGER.debug("operation = %s", flask.request.form["operation"])
    LOGGER.debug("postid = %s", flask.request.form["postid"])
    # PITFALL: Do not call render_template()
    operation = flask.request.form["operation"]
    postid = flask.request.form["postid"]
    username = flask.session.get('username')  # Get the logged-in username

    connection = insta485.model.get_db()  # Connect to the database

    cur = connection.execute(
        "SELECT 1 FROM likes WHERE owner = ? AND postid = ?",
        (username, postid)
    )
    liked = cur.fetchone()

    if operation == "like":
        if liked:  # User has already liked the post
            flask.abort(409)  # Conflict
        # Insert like into the table
        connection.execute(
            "INSERT INTO likes (owner, postid) VALUES (?, ?)",
            (username, postid)
        )

    elif operation == "unlike":
        if not liked:  # User hasn't liked the post yet
            flask.abort(409)  # Conflict
        # Delete the like from the table
        connection.execute(
            "DELETE FROM likes WHERE owner = ? AND postid = ?",
            (username, postid)
        )

    # Redirect to the target URL, or '/' if no target is provided
    target = flask.request.args.get('target', flask.url_for('show_index'))
    return flask.redirect(target)


@insta485.app.route("/comments/", methods=["POST"])
def update_comments():
    """Update comments on a post."""
    # Extract the form data
    operation = flask.request.form.get("operation")
    postid = flask.request.form.get("postid")
    commentid = flask.request.form.get("commentid")
    # Ensure text is not None or whitespace
    text = flask.request.form.get("text", "").strip()
    username = flask.session['username']
    # Connect to the database
    connection = insta485.model.get_db()

    # Handle comment creation
    if operation == "create":
        if not text:  # If text is empty or only whitespace
            flask.abort(400)

        # Insert the new comment into the database
        connection.execute(
            """
            INSERT INTO comments (owner, postid, text)
            VALUES (?, ?, ?)
            """,
            (username, postid, text)
        )

    # Handle comment deletion
    elif operation == "delete":
        # Fetch the comment and check if it belongs to the logged-in user
        cur = connection.execute(
            "SELECT owner FROM comments WHERE commentid = ?",
            (commentid,)
        )
        comment = cur.fetchone()
        print(comment)
        if comment['owner'] != username:
            flask.abort(403)

        # Delete the comment from the database
        connection.execute(
            "DELETE FROM comments WHERE commentid = ?",
            (commentid,)
        )

    # Get the target URL, or default to '/' if not provided
    target = flask.request.args.get('target', flask.url_for('show_index'))
    return flask.redirect(target)


@insta485.app.route("/posts/", methods=["POST"])
def update_posts():
    """Create or delete a post."""
    # Get the logged-in user
    username = flask.session.get('username')
    operation = flask.request.form.get('operation')

    # Connect to the database
    connection = insta485.model.get_db()

    if operation == 'create':
        # Create a new post & check if the file is empty
        fileobj = flask.request.files.get('file')
        if fileobj is None or fileobj.filename == '':
            flask.abort(400)

        # Compute UUID filename for the uploaded file
        filename = fileobj.filename
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        # Insert the post information into the database
        connection.execute(
            "INSERT INTO posts (owner, filename) VALUES (?, ?);",
            (username, uuid_basename)
        )
    elif operation == 'delete':
        # Delete a post
        postid = flask.request.form.get('postid')

        # Check if the post exists and if the user owns the post
        cur = connection.execute(
            "SELECT filename, owner FROM posts WHERE postid = ?;",
            (postid,)
        )
        post = cur.fetchone()

        if post is None or post['owner'] != username:
            flask.abort(403)

        # Delete the post from the database
        connection.execute("DELETE FROM posts WHERE postid = ?;", (postid,))
        connection.execute("DELETE FROM comments WHERE postid = ?;", (postid,))
        connection.execute("DELETE FROM likes WHERE postid = ?;", (postid,))

        # # Remove the file from the filesystem
        file_path = pathlib.Path(
            insta485.app.config["UPLOAD_FOLDER"]) / post['filename']
        if file_path.exists():
            os.remove(file_path)
    # Redirect to the target URL
    target = flask.request.args.get(
        'target', flask.url_for('show_user', user_url_slug=username))
    return flask.redirect(target)


@insta485.app.route("/following/", methods=["POST"])
def update_following():
    """Update user's following list/status."""
    operation = flask.request.form.get('operation')
    follow_target = flask.request.form.get('username')
    username = flask.session.get('username')

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT 1 FROM following WHERE username1 = ? AND username2 = ?",
        (username, follow_target)
    )
    following = cur.fetchone()

    if operation == "follow":
        if following:  # User is already following the target
            flask.abort(409)
        connection.execute(
            "INSERT INTO following (username1, username2) VALUES (?, ?)",
            (username, follow_target)
        )
    elif operation == "unfollow":
        if not following:  # User is not following the target yet
            flask.abort(409)
        # Delete the follower from the database
        connection.execute(
            "DELETE FROM following WHERE username1 = ? AND username2 = ?",
            (username, follow_target)
        )

    # Get the target URL, or default to '/' if not provided
    target = flask.request.args.get('target', flask.url_for('show_index'))
    return flask.redirect(target)


@insta485.app.route('/accounts/logout/', methods=["POST"])
def update_logout():
    """Log out the user."""
    flask.session.clear()
    return flask.redirect(flask.url_for("show_login_account"))


@insta485.app.route('/accounts/', methods=["POST"])
def update_account():
    """Update account information."""
    operation = flask.request.form.get('operation')
    if operation == 'login':
        login()

    elif operation == 'create':
        create()

    elif operation == 'delete':
        delete()

    elif operation == 'edit_account':
        username = flask.session.get('username')
        # no user logged in
        if 'username' not in flask.session:
            flask.abort(403)

        fullname = flask.request.form.get('fullname')
        email = flask.request.form.get('email')
        fileobj = flask.request.files.get('file')

        # if fields are blank, abort
        if not fullname or not email:
            flask.abort(400)

        connection = insta485.model.get_db()
        # update fullname and email
        connection.execute(
            "UPDATE users SET fullname = ?, email = ? WHERE username = ?",
            (fullname, email, username)
        )

        # if a profile picture is given, update it
        if fileobj:
            filename = fileobj.filename
            stem = uuid.uuid4().hex
            suffix = pathlib.Path(filename).suffix.lower()
            uuid_basename = f"{stem}{suffix}"
            path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
            fileobj.save(path)

            cur = connection.execute(
                "SELECT filename FROM users WHERE username = ?",
                (username,)
            )

            post = cur.fetchone()
            file_path = pathlib.Path(
                insta485.app.config["UPLOAD_FOLDER"]) / post['filename']
            if file_path.exists():
                os.remove(file_path)
            connection.execute(
                "UPDATE users SET filename = ? WHERE username = ?",
                (uuid_basename, username)
            )
        # otherwise done

    elif operation == 'update_password':
        update_password()

    # at the end end of all operations, return to target or index as default
    target = flask.request.args.get('target', flask.url_for('show_index'))
    return flask.redirect(target)


def verify_password(stored_hash: str, password: str) -> bool:
    """Verify given password against the database by."""
    algorithm, salt, db_hash = stored_hash.split("$")
    m = hashlib.new(algorithm)
    salted = salt + password
    m.update(salted.encode('utf-8'))
    m_result = m.hexdigest()

    return db_hash == m_result


def hash_password(password: str):
    """Hash a password using sha512 and a salt as per the spec."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    salted = salt + password
    hash_obj.update(salted.encode('utf-8'))
    return "$".join([algorithm, salt, hash_obj.hexdigest()])


def login():
    """Login."""
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    if not username:
        flask.abort(400)
    if not password:
        flask.abort(400)
    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    user = cur.fetchone()
    if user is not None:
        if verify_password(user['password'], password):
            flask.session['username'] = flask.request.form['username']
        else:
            flask.abort(403)
    else:
        flask.abort(403)


def create():
    """Create."""
    # pull fields
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    fullname = flask.request.form.get('fullname')
    email = flask.request.form.get('email')
    fileobj = flask.request.files.get('file')
    filename = fileobj.filename

    # if any are blanks, abort
    if not username or not password or not fullname:
        flask.abort(400)
    if not email or not fileobj:
        flask.abort(400)

    # uuid filename generation
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)
    connection = insta485.model.get_db()

    # confirm that the username is new
    cur = connection.execute(
        "SELECT 1 FROM users WHERE username = ?",
        (username,)
    )
    user_exists = cur.fetchone()

    if user_exists:
        flask.abort(409)

    flask.session['username'] = username

    # set password
    new_db_password = hash_password(password)
    connection.execute(
        """
        INSERT INTO users (username, fullname, email, filename, password)
        VALUES (?,?,?,?,?)
        """,
        (username, fullname, email, uuid_basename, new_db_password)
    )


def delete():
    """Delete."""
    username = flask.session.get('username')
    # no user logged in
    if 'username' not in flask.session:
        flask.abort(403)
    connection = insta485.model.get_db()
    # delete user, ON DELETE CASCADE should handle this
    cur = connection.execute(
        "SELECT filename FROM users WHERE username = ?",
        (username,)
    )
    user = cur.fetchone()
    print(user['filename'])
    file_path = pathlib.Path(
        insta485.app.config["UPLOAD_FOLDER"]) / user['filename']
    if file_path.exists():
        os.remove(file_path)

    cur = connection.execute(
        "SELECT filename FROM posts WHERE owner = ?",
        (username,)
    )
    post = cur.fetchone()
    while post is not None:
        file_path = pathlib.Path(
            insta485.app.config["UPLOAD_FOLDER"]) / post['filename']
        if file_path.exists():
            os.remove(file_path)
        post = cur.fetchone()

    connection.execute(
        "DELETE FROM users WHERE username = ?",
        (username,)
    )

    flask.session.clear()


def update_password():
    """Update password."""
    username = flask.session.get('username')
    # no user logged in
    if 'username' not in flask.session:
        flask.abort(403)
    password = flask.request.form.get('password')
    new_password1 = flask.request.form.get('new_password1')
    new_password2 = flask.request.form.get('new_password2')

    # abort if any fields are blank
    if not password or not new_password1 or not new_password2:
        flask.abort(400)

    connection = insta485.model.get_db()
    # identify the stored password
    cur = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    )

    db_password = cur.fetchone()

    # verify password is correct
    if not verify_password(db_password['password'], password):
        flask.abort(403)

    # passwords are not the same
    if new_password1 != new_password2:
        flask.abort(401)

    # hash and set the new password
    new_db_password = hash_password(new_password1)
    connection.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (new_db_password, username)
    )
