# Insta485 - Full-Stack Instagram Clone

A fully functional Instagram-like web application built as part of the EECS 485 course at the University of Michigan. This project was implemented in three phases: static site generation, server-side dynamic pages, and client-side dynamic pages with a REST API.

---

## 🚀 Project Overview
Insta485 is a web application that replicates core Instagram features, including user authentication, posting images, liking and commenting on posts, following/unfollowing users, and infinite scrolling.

The project was developed in three parts:
1. **Static Site Generation** (P1) - Generates HTML pages from templates using Python and Jinja.
2. **Server-Side Dynamic Pages** (P2) - Implements an interactive database-backed web app using Flask and SQLite.
3. **Client-Side Dynamic Pages & REST API** (P3) - Converts the UI to be dynamic using React and AJAX while exposing REST API endpoints.

---

## 🛠️ Technologies Used
### Backend:
- Python 🐍
- Flask 🌐
- SQLite 🗄️
- SQLAlchemy (optional ORM) 🗄️
- Werkzeug (for authentication) 🔐

### Frontend:
- HTML, CSS 🎨
- JavaScript (ES6+) ⚡
- React ⚛️
- Webpack 📦
- Axios / Fetch API 🌐

### Deployment & Testing:
- AWS EC2 (Deployment) ☁️
- Cypress (End-to-End Testing) 🧪
- Pytest (Unit Testing) 🐍
- ESLint & Prettier (Code Formatting) ✅
- PEP8, Pydocstyle, Pylint (Python Code Quality) 🧐

---

## 📸 Project Features
### ✅ Implemented Functionalities:
- **User Authentication:** Login, Logout, Account Creation
- **Post Management:** Upload, Delete, View Posts
- **Likes & Comments:** Like/Unlike posts, Add/Delete comments dynamically
- **Follow System:** Follow/Unfollow users
- **Infinite Scrolling:** Auto-fetch new posts as the user scrolls
- **REST API:** Exposes structured JSON data for posts, likes, and comments
- **Double-click to Like:** Users can double-tap posts to like them

### 📌 Key Enhancements in Each Phase
| Phase | Features Added |
|-------|---------------|
| **P1** | Static pages with Jinja2 templates |
| **P2** | Server-side dynamic rendering, user sessions, authentication |
| **P3** | React frontend, REST API, AJAX interactions, infinite scroll |

---

## ⚙️ Installation & Setup
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/yourusername/Insta485.git
cd Insta485
```

### 2️⃣ Setup Python Virtual Environment
```sh
python3 -m venv env
source env/bin/activate  # On macOS/Linux
env\Scripts\activate     # On Windows
```

### 3️⃣ Install Backend Dependencies
```sh
pip install -r requirements.txt
pip install -e .
```

### 4️⃣ Setup the Database
```sh
./bin/insta485db reset
```

### 5️⃣ Install Frontend Dependencies
```sh
npm ci
```

### 6️⃣ Start the Development Server
```sh
./bin/insta485run
```
Navigate to **`http://localhost:8000/`** in your browser.

---

## 📁 Project Structure
```
Insta485/
│── bin/                    # Scripts for running & testing the app
│── insta485/                # Main application package
│   ├── __init__.py          # App initialization
│   ├── config.py            # Flask configuration
│   ├── model.py             # Database models
│   ├── views/               # Backend view functions
│   ├── static/              # CSS & images
│   ├── templates/           # Jinja2 templates
│── sql/                     # Database schema & sample data
│── tests/                   # Unit & integration tests
│── package.json             # Frontend dependencies
│── webpack.config.js        # Webpack configuration
│── requirements.txt         # Backend dependencies
│── README.md                # Project documentation (this file)
```

---

## 🔍 Testing
### Run Backend Tests (Pytest)
```sh
pytest -v tests/
```

### Run Frontend Tests (Cypress)
```sh
npx cypress run
```

### Check Code Style
```sh
pycodestyle insta485
pydocstyle insta485
pylint insta485
npx eslint --ext jsx insta485/js/
npx prettier --check insta485/js/
```

---

## 🚀 Deployment
### 1️⃣ Deploy to AWS
1. Launch an AWS EC2 instance (Ubuntu).
2. Clone the project to the instance.
3. Install required dependencies.
4. Run `./bin/insta485install` to set up the environment.
5. Configure Nginx and run `./bin/insta485run`.

### 2️⃣ Verify Deployment
Run:
```sh
curl -v "http://<your-aws-public-ip>/"
```
Check `deployed_index.html` for successful deployment.

---

## 🏆 Achievements & Learnings
This project was a great hands-on experience in full-stack web development. Through implementing Insta485, I gained experience with:
- Building **server-side** and **client-side** dynamic web apps
- Implementing **REST APIs** with Flask
- Using **React** for a seamless user experience
- Working with **SQLite** for relational data storage
- Deploying web apps on **AWS EC2**
- Writing and running **unit tests** and **end-to-end tests**
- Following best practices for **code organization and style**

---

## 📜 License
This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 License**. You’re free to use and modify the code for educational purposes.

---

## ✨ Future Improvements
- Implement Direct Messaging 📩
- Add Notifications for Likes & Comments 🔔
- Improve Mobile Responsiveness 📱
- Optimize Database Queries for Faster Performance ⚡

---

## 👨‍💻 Author
- **Mitul Goel**  
- LinkedIn: [your-linkedin](https://linkedin.com/in/yourprofile)  
- GitHub: [your-github](https://github.com/yourusername)  

---

