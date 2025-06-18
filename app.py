import os
import requests, bcrypt, mysql.connector
from urllib.parse import quote
from bs4 import BeautifulSoup
import streamlit as st
import google.generativeai as gen
from mysql.connector import Error


# Configuration  (keep secrets OUT of your code)

DB_HOST     = st.secrets["db"]["host"]        # e.g. "localhost"
DB_USER     = st.secrets["db"]["user"]        # e.g. "root"
DB_PASS     = st.secrets["db"]["password"]    # e.g. "root"
DB_NAME     = st.secrets["db"]["database"]    # e.g. "smartshop_details"

GEMINI_KEY  = st.secrets["gemini"]["api_key"] # set this in .streamlit/secrets.toml

gen.configure(api_key=GEMINI_KEY)
gpt_model = gen.GenerativeModel("gemini-2.0-flash")

# Flipkart Scraper

def check_flipkart_availability(product_name: str) -> tuple[bool, str | None]:
    """
    Returns (True, url) if at least one product link is found,
    else (False, None)
    """
    search_url = f"https://www.flipkart.com/search?q={quote(product_name)}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        r = requests.get(search_url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.RequestException:
        return False, None

    soup = BeautifulSoup(r.text, "html.parser")

    # ① look for any anchor that points to a product page  (contains /p/)
    # ② ensure we catch result even if Flipkart changes class names
    for a in soup.select("a[href*='/p/']"):
        href = a.get("href", "")
        if href.startswith("/"):
            return True, "https://www.flipkart.com" + href.split("?")[0]

    return False, None

# Gemini helper  (backup when Flipkart fails)

def gemini_fallback(product_name: str) -> str:
    prompt = (
        f"You are an e‑commerce assistant. "
        f"Find at least three reputable Indian online stores "
        f"where someone could buy '{product_name}'. "
        f"For each, give the store name and a product URL if available. "
        f"If the product looks uncommon, suggest closest matches."
    )
    try:
        resp = gpt_model.generate_content(prompt, safety_settings={"HARASSMENT": "block_none"})
        return resp.text.strip()
    except Exception as e:
        return f"Gemini could not fetch alternatives ({e})."

# DB helpers

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
    )


def register_user(username: str, password: str) -> tuple[bool, str]:
    try:
        cnx = get_connection()
        cur = cnx.cursor()
        cur.execute("SELECT 1 FROM user_details WHERE username = %s", (username,))
        if cur.fetchone():
            return False, "Username already exists."

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cur.execute("INSERT INTO user_details(username, password) VALUES (%s, %s)", (username, hashed))
        cnx.commit()
        return True, "Registered successfully! You may log in."
    except Error as e:
        return False, f"DB error: {e}"
    finally:
        cur.close(), cnx.close()


def authenticate_user(username: str, password: str) -> bool:
    try:
        cnx = get_connection()
        cur = cnx.cursor()
        cur.execute("SELECT password FROM user_details WHERE username = %s", (username,))
        row = cur.fetchone()
        return bool(row and bcrypt.checkpw(password.encode(), row[0].encode()))
    except Error:
        return False
    finally:
        cur.close(), cnx.close()

# Streamlit pages

def register_page():
    st.subheader("Create a new account")
    u = st.text_input("Username / email")
    p1 = st.text_input("Password", type="password")
    p2 = st.text_input("Confirm password", type="password")
    if st.button("Register"):
        if not (u and p1 and p2):
            st.error("Please fill in every field.")
        elif p1 != p2:
            st.error("Passwords do not match.")
        else:
            ok, msg = register_user(u, p1)
            (st.success if ok else st.error)(msg)
            if ok:
                st.session_state.page = "login"
                st.rerun()


def login_page():
    st.subheader("Login")
    with st.form(key="login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        cols = st.columns(2)
        login_clicked = cols[0].form_submit_button("Login 🔐")
        register_clicked = cols[1].form_submit_button("Register ➕")

    if login_clicked:
        if authenticate_user(u, p):
            st.session_state.auth = True
            st.session_state.user = u
            st.session_state.page = "chat"
            st.success("Logged in!")
            st.rerun()
        else:
            st.error("Invalid credentials.")

    if register_clicked:
        st.session_state.page = "register"
        st.rerun()


def chatbot_page():
    st.title("Smart Shop 🛒")
    if st.button("Logout"):
        st.session_state.clear()
        st.session_state.page = "login"
        st.rerun()

    st.write(f"Hello, **{st.session_state.user}**!  \nType a product name to check its availability on Flipkart.")
    product = st.chat_input("Try: laptop, Apple iPhone 15, …")

    if product:
        with st.spinner("Searching Flipkart…"):
            ok, link = check_flipkart_availability(product)

        if ok:
            st.success(f"✅ **Product found!**  \n[➡️ Buy on Flipkart]({link})")
        else:
            st.warning("🔎 Not found on Flipkart.")
            with st.spinner("Checking other stores via Gemini…"):
                alt = gemini_fallback(product)
            st.info(alt)

# Page router

if "page" not in st.session_state:
    st.session_state.page = "login"
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = ""

page = st.session_state.page
if page == "login":
    login_page()
elif page == "register":
    register_page()
elif page == "chat":
    chatbot_page()
