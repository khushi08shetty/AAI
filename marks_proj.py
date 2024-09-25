import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px

# Helper functions
def load_users():
    """Load user data from a JSON file."""
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    else:
        return {}

def save_users(users):
    """Save user data to a JSON file."""
    with open('users.json', 'w') as f:
        json.dump(users, f)

def create_user_folder(username):
    """Create a folder for the user if it doesn't exist."""
    user_folder = os.path.join(os.getcwd(), username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

def load_user_marks(username):
    """Load the user's marks from their CSV file."""
    user_folder = os.path.join(os.getcwd(), username)
    file_path = os.path.join(user_folder, 'marks.csv')
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=['Subject', 'Marks'])

def save_user_marks(username, marks_df):
    """Save the user's marks to their CSV file."""
    user_folder = os.path.join(os.getcwd(), username)
    file_path = os.path.join(user_folder, 'marks.csv')
    marks_df.to_csv(file_path, index=False)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# Sign-up page
def signup_page():
    st.title("Welcome to the Sign Up Page")
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    dob = st.date_input("Date of Birth")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign Up", key="signup_btn"):
        users = load_users()
        
        # Check if the email already exists
        if email in users:
            st.error("User with this email already exists!")
        else:
            # Add new user
            users[email] = {
                'name': name,
                'phone': phone,
                'dob': str(dob),
                'password': password
            }
            save_users(users)
            create_user_folder(email)
            st.success("Sign up successful! Please log in.")
            st.session_state['page'] = 'login'

# Login page
def login_page():
    st.title("Welcome to the Login Page")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login", key="login_btn"):
        users = load_users()
        
        # Check if the email exists and password matches
        if email in users and users[email]['password'] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = email
            st.session_state['page'] = 'marks'
            st.success(f"Welcome {users[email]['name']}!")
        else:
            st.error("Invalid email or password!")

# Marks submission page
def marks_page():
    st.title(f"Welcome, {load_users()[st.session_state['username']]['name']}")
    
    subjects = ['Maths', 'Physics', 'Chemistry', 'Biology', 'English', 'ICT', 'History']
    marks = {}
    
    for subject in subjects:
        marks[subject] = st.slider(f"Enter your marks for {subject}", 0, 100, key=subject)

    if st.button("Submit Marks", key="submit_marks_btn"):
        # Save marks to a CSV file in user's folder
        marks_df = pd.DataFrame({
            'Subject': subjects,
            'Marks': [marks[sub] for sub in subjects]
        })
        save_user_marks(st.session_state['username'], marks_df)
        st.success("Marks submitted successfully!")
        st.session_state['page'] = 'report'

# Report page (Graphs)
def report_page():
    st.title("Your Reports are Ready!")
    
    marks_df = load_user_marks(st.session_state['username'])

    if not marks_df.empty:
        # Bar chart for average marks
        fig1 = px.bar(marks_df, x='Subject', y='Marks', title="Marks per Subject")
        st.plotly_chart(fig1)

        # Line chart for marks distribution
        fig2 = px.line(marks_df, x='Subject', y='Marks', title="Marks Distribution")
        st.plotly_chart(fig2)

        # Pie chart for marks distribution
        fig3 = px.pie(marks_df, names='Subject', values='Marks', title="Marks Share by Subject")
        st.plotly_chart(fig3)
    else:
        st.warning("No marks found!")

    if st.sidebar.button("Sign out", key="signout_btn"):
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'login'

# App flow
if st.session_state['logged_in']:
    if st.session_state['page'] == 'marks':
        marks_page()
    elif st.session_state['page'] == 'report':
        report_page()
else:
    if st.session_state['page'] == 'login':
        login_page()
    elif st.session_state['page'] == 'signup':
        signup_page()

# Sidebar navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Login", key="sidebar_login_btn"):
    st.session_state['page'] = 'login'
if st.sidebar.button("Signup", key="sidebar_signup_btn"):
    st.session_state['page'] = 'signup'
