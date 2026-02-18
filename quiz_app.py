import streamlit as st
import hashlib
import json
import os

# ── Session State ─────────────────────────────────────────────────────────────
for key, default in [
    ("page", "home"),
    ("name", ""),
    ("subject", ""),
    ("score", 0),
    ("answers", {}),
    ("logged_in", False),
    ("username", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Quizify", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;600;700;800&family=Nunito:wght@400;600;700&display=swap');

    * { font-family: 'Nunito', sans-serif; }

    .stApp { background: #f5f1e8; }

    .logo {
        font-size: 3rem; font-weight: 800; text-align: center; margin: 20px 0;
        font-family: 'Baloo 2', cursive;
        background: linear-gradient(135deg,#ff9a9e 0%,#fad0c4 40%,#ffd1a0 60%,#a8e6cf 80%,#87ceeb 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }

    .title {
        font-size: 2.8rem; font-weight: 800; color: #2c3e50; text-align: center;
        margin: 30px 0 15px; font-family: 'Baloo 2', cursive;
    }

    .subtitle {
        font-size: 1.4rem; color: #5a6c7d; text-align: center;
        margin-bottom: 40px; font-weight: 600; font-family: 'Baloo 2', cursive;
    }

    .card {
        background: #2d5a5a; border-radius: 25px; padding: 50px;
        margin: 30px auto; max-width: 600px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15); text-align: center;
    }

    .card-title { font-size: 2.5rem; color: white; font-weight: 800; margin-bottom: 20px; font-family: 'Baloo 2', cursive; }
    .card-text  { font-size: 1.3rem; color: white; margin-bottom: 10px; font-weight: 600; font-family: 'Baloo 2', cursive; }

    .auth-card {
        background: white; border-radius: 25px; padding: 50px;
        margin: 20px auto; max-width: 480px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.12);
    }

    .auth-title {
        font-size: 2rem; font-weight: 800; color: #2c3e50; text-align: center;
        margin-bottom: 30px; font-family: 'Baloo 2', cursive;
    }

    .question-text {
        font-size: 1.5rem; color: #2c3e50; font-weight: 700;
        margin: 30px 0 25px; line-height: 1.5; font-family: 'Baloo 2', cursive;
    }

    .q-number {
        background: #ffb347; color: white; padding: 8px 18px;
        border-radius: 12px; font-weight: 800; margin-right: 12px;
        font-family: 'Baloo 2', cursive; display: inline-block;
    }

    .stButton > button {
        background: #26d07c; color: white; font-size: 1.2rem; font-weight: 800;
        padding: 16px 40px; border-radius: 50px; border: none;
        transition: all 0.3s; box-shadow: 0 4px 15px rgba(38,208,124,0.3);
        font-family: 'Baloo 2', cursive;
    }

    .stButton > button:hover {
        background: #20b569; transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(38,208,124,0.4);
    }

    .stTextInput input {
        background: white !important; border: 3px solid #e0e0e0 !important;
        border-radius: 15px !important; font-size: 1.1rem !important;
        padding: 14px 18px !important; color: #2c3e50 !important; font-weight: 600 !important;
    }

    .stTextInput input:focus {
        border-color: #26d07c !important; box-shadow: 0 0 0 3px rgba(38,208,124,0.1) !important;
    }

    div.row-widget.stRadio label {
        background: transparent !important; border-radius: 0 !important;
        padding: 16px 0 !important; font-size: 1.1rem !important;
        color: #2c3e50 !important; border: none !important;
        border-bottom: 2px solid #e0e0e0 !important; transition: all 0.3s !important;
        cursor: pointer !important; font-weight: 600 !important;
    }

    div.row-widget.stRadio label:hover {
        border-bottom-color: #26d07c !important; padding-left: 10px !important;
    }

    .result-card {
        background: white; border-radius: 25px; padding: 60px;
        margin: 30px auto; max-width: 700px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center;
    }

    .result-title  { font-size: 3.5rem; font-weight: 800; color: #2c3e50; margin-bottom: 20px; font-family: 'Baloo 2', cursive; }
    .result-score  { font-size: 5rem; font-weight: 800; margin: 30px 0; font-family: 'Baloo 2', cursive; }

    h3 { font-family: 'Baloo 2', cursive !important; color: #2c3e50 !important; font-weight: 700 !important; }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Simple File-Based User Store ───────────────────────────────────────────────
USERS_FILE = "quizify_users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ── Questions ──────────────────────────────────────────────────────────────────
questions = {
    "Java": [
        ("What is the default value of an int in Java?", ["null", "0", "1", "-1"], "0"),
        ("Which keyword is used to inherit a class?", ["implements", "extends", "inherits", "super"], "extends"),
        ("What does JVM stand for?", ["Java Virtual Machine", "Java Variable Method", "Java Verified Module", "Java Version Manager"], "Java Virtual Machine"),
        ("Which method is the entry point of a Java program?", ["start()", "run()", "main()", "init()"], "main()"),
        ("Which of these is NOT a Java primitive type?", ["int", "boolean", "String", "char"], "String"),
        ("What is the size of an int in Java?", ["2 bytes", "4 bytes", "8 bytes", "16 bytes"], "4 bytes"),
        ("Which keyword prevents a method from being overridden?", ["static", "final", "abstract", "private"], "final"),
        ("What does 'OOP' stand for?", ["Object Oriented Programming", "Out Of Place", "Open Online Platform", "Optional Object Parameter"], "Object Oriented Programming"),
        ("Which collection allows duplicate elements?", ["Set", "Map", "List", "HashSet"], "List"),
        ("What is the parent class of all classes in Java?", ["Base", "Root", "Object", "Super"], "Object"),
    ],
    "C++": [
        ("What does 'cout' do in C++?", ["Reads input", "Prints output", "Declares variable", "Loops"], "Prints output"),
        ("Which operator is used to access members via a pointer?", [".", "::", "->", "*"], "->"),
        ("What is the extension of a C++ file?", [".c", ".java", ".cpp", ".py"], ".cpp"),
        ("Which concept is NOT part of OOP?", ["Encapsulation", "Polymorphism", "Compilation", "Inheritance"], "Compilation"),
        ("What is a destructor?", ["Allocates memory", "Deletes a class", "Cleans up when object is destroyed", "Creates a copy"], "Cleans up when object is destroyed"),
        ("Which keyword allocates dynamic memory?", ["malloc", "new", "alloc", "create"], "new"),
        ("What does 'cin' stand for?", ["Console In", "Character Input", "Code In", "Class Input"], "Console In"),
        ("Which of these is a C++ reference declaration?", ["int* x", "int& x", "int[] x", "int@ x"], "int& x"),
        ("What is a template in C++?", ["A design pattern", "A class blueprint", "Generic programming feature", "Header file"], "Generic programming feature"),
        ("What is 'std' in 'std::cout'?", ["Standard library namespace", "String data", "Static declaration", "Structured type"], "Standard library namespace"),
    ],
    "Python": [
        ("What is the output of print(2 ** 3)?", ["6", "8", "9", "5"], "8"),
        ("Which keyword defines a function in Python?", ["func", "define", "def", "fun"], "def"),
        ("What data type is []?", ["tuple", "dict", "set", "list"], "list"),
        ("What does len('hello') return?", ["4", "5", "6", "hello"], "5"),
        ("Which symbol is used for single-line comments?", ["//", "#", "--", "/*"], "#"),
        ("What is the output of type(3.14)?", ["<class 'int'>", "<class 'str'>", "<class 'float'>", "<class 'num'>"], "<class 'float'>"),
        ("Which keyword is used for loops?", ["repeat", "loop", "for", "iterate"], "for"),
        ("How do you create a dictionary in Python?", ["[]", "()", "{}", "<>"], "{}"),
        ("What does 'None' represent in Python?", ["0", "False", "Empty string", "Null/no value"], "Null/no value"),
        ("What is a lambda in Python?", ["A loop", "An anonymous function", "A class", "A module"], "An anonymous function"),
    ],
    "JavaScript": [
        ("Which keyword declares a constant in JS?", ["var", "let", "const", "static"], "const"),
        ("What does DOM stand for?", ["Document Object Model", "Data Object Method", "Dynamic Output Mode", "Display Object Map"], "Document Object Model"),
        ("What is the output of typeof null?", ["'null'", "'undefined'", "'object'", "'boolean'"], "'object'"),
        ("Which method adds an element to the END of an array?", ["push()", "pop()", "shift()", "unshift()"], "push()"),
        ("What does '===' check?", ["Value only", "Type only", "Value and type", "Reference"], "Value and type"),
        ("Which company created JavaScript?", ["Microsoft", "Google", "Netscape", "Apple"], "Netscape"),
        ("What is a closure in JS?", ["A loop construct", "A way to close browser", "A function with access to outer scope", "An error handler"], "A function with access to outer scope"),
        ("How do you write a comment in JS?", ["# comment", "<!-- comment -->", "// comment", "** comment"], "// comment"),
        ("What does JSON stand for?", ["Java Syntax Object Notation", "JavaScript Object Notation", "Java Standard Output Name", "JSON Script Object Node"], "JavaScript Object Notation"),
        ("Which method removes the LAST element of an array?", ["shift()", "pop()", "splice()", "remove()"], "pop()"),
    ],
    "CSS": [
        ("What does CSS stand for?", ["Creative Style Sheets", "Cascading Style Sheets", "Computer Style System", "Colorful Style Syntax"], "Cascading Style Sheets"),
        ("Which property changes text color?", ["font-color", "text-color", "color", "foreground"], "color"),
        ("How do you select an element with id='box'?", [".box", "#box", "*box", "box"], "#box"),
        ("Which value makes an element invisible but still in flow?", ["display:none", "visibility:hidden", "opacity:1", "hidden:true"], "visibility:hidden"),
        ("What does 'flexbox' help with?", ["Animations", "Responsive layout", "Colors", "Typography"], "Responsive layout"),
        ("Which property controls spacing INSIDE an element?", ["margin", "border", "padding", "spacing"], "padding"),
        ("How do you apply a style to ALL paragraphs?", ["#p", ".p", "p", "*p"], "p"),
        ("What is the correct CSS syntax?", ["p {color; red}", "p: color=red", "p {color: red;}", "{p color: red}"], "p {color: red;}"),
        ("Which property sets background color?", ["bg-color", "background-color", "bgcolor", "color-bg"], "background-color"),
        ("What does z-index control?", ["Zoom level", "Stacking order", "Font size", "Border width"], "Stacking order"),
    ],
    "HTML": [
        ("What does HTML stand for?", ["Hyper Text Makeup Language", "Hyper Text Markup Language", "High Text Modern Language", "Home Tool Markup Language"], "Hyper Text Markup Language"),
        ("Which tag creates a hyperlink?", ["<link>", "<a>", "<href>", "<url>"], "<a>"),
        ("Which tag is used for the largest heading?", ["<h6>", "<head>", "<h1>", "<title>"], "<h1>"),
        ("Which tag creates an ordered list?", ["<ul>", "<li>", "<ol>", "<list>"], "<ol>"),
        ("What is the correct HTML for a line break?", ["<break>", "<lb>", "<newline>", "<br>"], "<br>"),
        ("Which attribute specifies an image path?", ["href", "src", "url", "link"], "src"),
        ("Which tag defines the body of a webpage?", ["<main>", "<section>", "<body>", "<content>"], "<body>"),
        ("Which tag is used for a paragraph?", ["<para>", "<txt>", "<p>", "<text>"], "<p>"),
        ("What tag embeds a JavaScript file?", ["<js>", "<javascript>", "<script>", "<code>"], "<script>"),
        ("Which tag links an external CSS file?", ["<style>", "<css>", "<link>", "<stylesheet>"], "<link>"),
    ],
    "Next.js": [
        ("What is Next.js built on top of?", ["Angular", "Vue", "React", "Svelte"], "React"),
        ("Which folder contains pages in Next.js (Pages Router)?", ["/src", "/components", "/pages", "/views"], "/pages"),
        ("What does SSR stand for?", ["Static Site Rendering", "Server Side Rendering", "Simple Script Runner", "Style Sheet Rendering"], "Server Side Rendering"),
        ("Which file configures Next.js?", ["package.json", "next.config.js", "app.config.js", "server.js"], "next.config.js"),
        ("What is 'getStaticProps' used for?", ["Client-side data fetching", "Fetch data at build time", "API routing", "Middleware"], "Fetch data at build time"),
        ("What does ISR stand for in Next.js?", ["Instant Script Refresh", "Incremental Static Regeneration", "Internal Server Response", "Initial State Render"], "Incremental Static Regeneration"),
        ("Which Next.js router is newer?", ["Pages Router", "App Router", "File Router", "Link Router"], "App Router"),
        ("What is the purpose of _app.js?", ["API route handler", "Global layout wrapper", "Static config", "Middleware"], "Global layout wrapper"),
        ("How do you create an API route in Next.js?", ["In /services folder", "In /pages/api folder", "In /routes folder", "In /controllers folder"], "In /pages/api folder"),
        ("What company created Next.js?", ["Meta", "Google", "Microsoft", "Vercel"], "Vercel"),
    ],
}

# ── Pages ──────────────────────────────────────────────────────────────────────

# HOME
if st.session_state.page == "home":
    st.markdown('<div class="logo">Quizify</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="card">
            <div class="card-title">BrainBlast Quiz</div>
            <div class="card-text">Jump in and test your super brain!</div>
            <div class="card-text">Ready, set, go! Your quiz adventure starts now! 🏅</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sign Up", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()

# SIGNUP
elif st.session_state.page == "signup":
    st.markdown('<div class="logo">Quizify</div>', unsafe_allow_html=True)
    st.markdown('<div class="title">Create Account</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown('<div class="auth-title">👋 Join Quizify</div>', unsafe_allow_html=True)

        new_name     = st.text_input("Full Name",     placeholder="Your full name",     key="su_name")
        new_username = st.text_input("Username",      placeholder="Choose a username",  key="su_user")
        new_pw       = st.text_input("Password",      placeholder="Create a password",  type="password", key="su_pw")
        confirm_pw   = st.text_input("Confirm Password", placeholder="Repeat password", type="password", key="su_cpw")
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Back", use_container_width=True, key="su_back"):
                st.session_state.page = "home"
                st.rerun()
        with c2:
            if st.button("Register", use_container_width=True, key="su_reg"):
                users = load_users()
                if not new_name or not new_username or not new_pw:
                    st.warning("Please fill in all fields!")
                elif new_pw != confirm_pw:
                    st.warning("Passwords do not match!")
                elif new_username in users:
                    st.warning("Username already taken. Try another!")
                else:
                    users[new_username] = {"name": new_name, "password": hash_pw(new_pw)}
                    save_users(users)
                    st.success("Account created! Please login.")
                    st.session_state.page = "login"
                    st.rerun()

# LOGIN
elif st.session_state.page == "login":
    st.markdown('<div class="logo">Quizify</div>', unsafe_allow_html=True)
    st.markdown('<div class="title">Welcome Back!</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown('<div class="auth-title">🔐 Login</div>', unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter your username", key="li_user")
        password = st.text_input("Password", placeholder="Enter your password", type="password", key="li_pw")
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Back", use_container_width=True, key="li_back"):
                st.session_state.page = "home"
                st.rerun()
        with c2:
            if st.button("Login", use_container_width=True, key="li_btn"):
                users = load_users()
                if username in users and users[username]["password"] == hash_pw(password):
                    st.session_state.logged_in = True
                    st.session_state.username  = username
                    st.session_state.name      = users[username]["name"]
                    st.session_state.page      = "info"
                    st.rerun()
                else:
                    st.warning("Invalid username or password!")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<center>Don't have an account?</center>", unsafe_allow_html=True)
        if st.button("Create Account", use_container_width=True, key="li_signup"):
            st.session_state.page = "signup"
            st.rerun()

# INFO (subject selection)
elif st.session_state.page == "info":
    if not st.session_state.logged_in:
        st.session_state.page = "home"
        st.rerun()

    st.markdown('<div class="logo">Quizify</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="title">Hello, {st.session_state.name}! </div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Pick a subject and start your quiz adventure!</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🎯 Choose your subject")
        subject = st.selectbox(
            "",
            ["Java", "C++", "Python", "JavaScript", "CSS", "HTML", "Next.js"],
            index=0,
            key="subject_select"
        )
        st.session_state.subject = subject

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Logout", use_container_width=True):
                for k in ["logged_in", "username", "name", "subject", "score", "answers"]:
                    st.session_state[k] = "" if k in ["username", "name", "subject"] else (False if k == "logged_in" else (0 if k == "score" else {}))
                st.session_state.page = "home"
                st.rerun()
        with c2:
            if st.button("Start Quiz ▶", use_container_width=True):
                st.session_state.page  = "quiz"
                st.session_state.score = 0
                st.session_state.answers = {}
                st.rerun()

# QUIZ
elif st.session_state.page == "quiz":
    if not st.session_state.logged_in:
        st.session_state.page = "home"
        st.rerun()

    st.markdown('<div class="logo">Quizify</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="title">{st.session_state.subject} Quiz</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">Go {st.session_state.name}! You Got This! 😎</div>', unsafe_allow_html=True)

    current_questions = questions[st.session_state.subject]

    for i, (q, options, correct) in enumerate(current_questions):
        st.markdown(f'<div class="question-text"><span class="q-number">Q{i+1}</span>{q}</div>', unsafe_allow_html=True)
        saved_index = options.index(st.session_state.answers[f"q_{i}"]) if f"q_{i}" in st.session_state.answers else None
        answer = st.radio("", options, key=f"q_{i}", index=saved_index)
        if answer:
            st.session_state.answers[f"q_{i}"] = answer

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("Back", use_container_width=True):
            st.session_state.page = "info"
            st.rerun()
    with c2:
        if st.button("Submit Answers", use_container_width=True):
            score = sum(
                1 for i in range(len(current_questions))
                if f"q_{i}" in st.session_state.answers
                and st.session_state.answers[f"q_{i}"] == current_questions[i][2]
            )
            st.session_state.score = score
            st.session_state.page  = "result"
            st.rerun()

# RESULT
elif st.session_state.page == "result":
    st.markdown('<div class="logo">Quizify</div>', unsafe_allow_html=True)

    score = st.session_state.score
    total = len(questions[st.session_state.subject])

    if score >= 9:
        msg, color = "SUPERSTAR! ⭐", "#26d07c"
    elif score >= 7:
        msg, color = "AWESOME! 🎉", "#5eb3f6"
    elif score >= 5:
        msg, color = "GOOD JOB! 👍", "#ffb347"
    else:
        msg, color = "KEEP TRYING! 🔥", "#ff6b9d"

    st.markdown(f"""
        <div class="result-card">
            <div class="result-title">{msg}</div>
            <div class="result-score" style="color:{color};">{score} / {total}</div>
            <div style="font-size:1.4rem;color:#5a6c7d;font-weight:600;">
                Great work, {st.session_state.name}! — {st.session_state.subject} Quiz
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Try Another Subject", use_container_width=True):
            st.session_state.page    = "info"
            st.session_state.score   = 0
            st.session_state.answers = {}
            st.rerun()