import streamlit as st
import flipkart as fk
user_db={"admin":{"password":"admin123"}}
product=["laptop","phone","Headphones","Camera","smartwatch"]
#Registration page
def register_page():
    st.title("Register")
    new_username=st.text_input(label="Create Username",placeholder="Enter username or email id")
    new_password=st.text_input(label="Create Password",placeholder="Enter password",type="password")
    confirm_password=st.text_input(label="Confirm Password",placeholder="Enter pasword",type="password")
    if st.button("Register"):
        if new_username in user_db:
            st.error("Username already exists.please choose a different username.")
        elif new_password!=confirm_password:
            st.error("Passwords do not match!")
        else:
            user_db[new_username]={"password":new_password}
            st.success("Regisstration Successful! you can now login")
            st.session_state["page"]="Login"
            st.rerun()

def login_page():
    with st.form("Login"):
        st.title(" Login")
        username=st.text_input("Username",placeholder="Enter username")
        password=st.text_input("Password",placeholder="Enter Password",type="password")
        if st.form_submit_button("Login"):
            if username in user_db and user_db[username]["password"]==password:
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
    st.write(f"Hello,{st.session_state['username']}!Type the name of a product to check its availability.")
    query=st.chat_input("Search for a product")
    if query:
        mproducts=fk.sflipkart(query)
        if mproducts:
            st.success(f"Product found:{','.join(mproducts)}")
        else:
            st.error("No matching product found")
        if st.navigation("Logout"):
            st.session_state["authenticated"]=False
            st.session_state["page"]="Login"
            st.rerun()
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