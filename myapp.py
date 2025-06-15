import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import mysql.connector
import bcrypt
from mysql.connector import Error 
user_db={"admin":{"password":"admin123"}}
product=["laptop","phone","Headphones","Camera","smartwatch"]
def check_flipkart_availability(product_name):
    search_url = f"https://www.flipkart.com/search?q={quote(product_name)}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        return False, None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Flipkart item selector (simplified, may need updating)
    products = soup.find_all("a", {"class": "_1fQZEK"})

    if not products:
        products = soup.find_all("a", {"class": "_2rpwqI"})

    if products:
        product_link = "https://www.flipkart.com" + products[0].get("href")
        return True, product_link

    return False, None


# DB connection function
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="smartshopbot",
        password="smartshop1419",
        database="smartshop_details"
    )

# Register user
def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT * FROM user_details WHERE username = %s", (username,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return False, "Username already exists!"

    # Hash password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO user_details(username, password) VALUES (%s, %s)",
        (username, hashed.decode())
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True, "User registered successfully!"

# Authenticate user
def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM user_details WHERE username = %s", (username,))
    record = cursor.fetchone()
    cursor.close()
    conn.close()

    if record:
        stored_password = record[0].encode()
        if bcrypt.checkpw(password.encode(), stored_password):
            return True
    return False


#Registration page
def register_page():
    st.title("Register")
    new_username=st.text_input(label="Create Username",placeholder="Enter username or email id")
    new_password=st.text_input(label="Create Password",placeholder="Enter password",type="password")
    confirm_password=st.text_input(label="Confirm Password",placeholder="Enter pasword",type="password")
    if st.button("Register"):
            if not new_username or not new_password or not confirm_password:
                st.error("Please fill all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, msg = register_user(new_username, new_password)
                if success:
                    st.success(msg)
                    st.session_state["page"]="Login"
                    st.rerun()
                else:
                    st.error(msg)

def login_page():
    with st.form("Login"):
        st.title(" Login")
        username=st.text_input("Username",placeholder="Enter username")
        password=st.text_input("Password",placeholder="Enter Password",type="password")
        if st.form_submit_button("Login"):
            if authenticate_user(username, password):
                st.success(f"Welcome back,{username}!")
                st.session_state["authenticated"]=True
                st.session_state["username"]=username
                st.session_state["page"]="chatbot"
                st.rerun()

            else:
                st.error("Invalid username or password")
        if st.form_submit_button("Go to Registration"):
            st.session_state["page"]="Register"
            st.rerun()

def chatbot():
    st.title("Smart Shop")
    if st.button("Logout"):
            st.session_state["authenticated"]=False
            st.session_state["page"]="Login"
            st.rerun()
    st.write(f"Hello,{st.session_state['username']}!Type the name of a product to check its availability.")
    product_name = st.chat_input("Enter the product name")
    if product_name:
        status,url = check_flipkart_availability(product_name)
        if status:
            st.success(f"✅ Product found: [Buy Now]({url})")
        else:
            st.warning("❌ Product not available or not found.")
    else:
        st.error("Please enter a product name.")

        
#main app



if "authenticated" not in st.session_state:
    st.session_state["authenticated"]=False
if "page" not in st.session_state:
    st.session_state["page"]="Login"


if st.session_state["page"]=="Login":
    login_page()
elif st.session_state["page"]=="Register":
    register_page()
elif st.session_state["page"]=="chatbot":
    chatbot()
