import streamlit as st # type: ignore
import sqlite3
import bcrypt # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import re
import time
import matplotlib.pyplot as plt # type: ignore

# ---------------- THEME ----------------
st.set_page_config(page_title="Smart Spend AI", layout="wide")

st.markdown("""
<style>
body {background-color:#f5f0e6;}
.stButton>button {background-color:#8b6f47;color:white;border-radius:10px;}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS users(
username TEXT,
password BLOB
)""")
conn.commit()

# ---------------- VALIDATION ----------------
def valid_username(u):
    return bool(re.match(r"^[A-Za-z0-9_]{4,20}$", u))

def password_strength(p):
    score=0
    if re.search(r"[A-Z]",p): score+=1
    if re.search(r"[a-z]",p): score+=1
    if re.search(r"\d",p): score+=1
    if re.search(r"[^\w]",p): score+=1
    return ["Weak","Medium","Strong","Very Strong"][score-1] if score>0 else "Weak"

def valid_password(p):
    return len(p)>=8 and \
        re.search(r"[A-Z]",p) and \
        re.search(r"[a-z]",p) and \
        re.search(r"\d",p) and \
        re.search(r"[^\w]",p)

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user=None

# ---------------- AUTH PAGES ----------------
def register():
    st.title("Register")

    u=st.text_input("Username")
    p=st.text_input("Password",type="password")
    cp=st.text_input("Confirm Password",type="password")

    if u:
        if not valid_username(u):
            st.error("Invalid username format")

    if p:
        st.write("Strength:",password_strength(p))

    if st.button("Create Account"):

        if not valid_username(u):
            st.error("Invalid username")
            return

        if not valid_password(p):
            st.error("Weak password")
            return

        if p!=cp:
            st.error("Passwords do not match")
            return

        c.execute("SELECT * FROM users WHERE username=?",(u,))
        if c.fetchone():
            st.error("Username exists")
            return

        hashed=bcrypt.hashpw(p.encode(),bcrypt.gensalt())
        c.execute("INSERT INTO users VALUES(?,?)",(u,hashed))
        conn.commit()

        st.success("Account created")

def login():
    st.title("Login")
    u=st.text_input("Username")
    p=st.text_input("Password",type="password")

    if st.button("Login"):

        c.execute("SELECT password FROM users WHERE username=?",(u,))
        result=c.fetchone()

        time.sleep(1)

        if result and bcrypt.checkpw(p.encode(),result[0]):
            st.session_state.user=u
            st.success("Logged in")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------------- MAIN APP ----------------
def dashboard():

    st.title("Smart Spend AI")

    categories = {
        "Individual":["Food","Transport","Rent","Subscription","Entertainment","Investments"],
        "Business":["Operational","Salaries","Utilities","Vendors","Tax","Inventory"],
        "Trip":["Transport","Accommodation","Food","Local","Activities","Shopping"],
        "Family":["Groceries","Fees","Healthcare","Insurance","Utilities","Maintenance"]
    }

    mode=st.selectbox("Select Mode", list(categories.keys()))
    sub=st.selectbox("Subcategory", categories[mode])
    amt=st.number_input("Amount",step=1.0)

    if "data" not in st.session_state:
        st.session_state.data=[]

    if st.button("Add"):
        st.session_state.data.append([mode,sub,amt])

    if st.session_state.data:

        df=pd.DataFrame(st.session_state.data,
                        columns=["Mode","Subcategory","Amount"])

        st.subheader("Transactions")
        st.dataframe(df)

        # pie
        st.subheader("Spending Distribution")
        fig1,ax1=plt.subplots()
        df.groupby("Subcategory")["Amount"].sum().plot.pie(autopct="%1.1f%%",ax=ax1)
        st.pyplot(fig1)

        # trend
        st.subheader("Trend")
        fig2,ax2=plt.subplots()
        df["Amount"].plot(ax=ax2)
        st.pyplot(fig2)

        # anomaly
        mean=df.Amount.mean()
        std=df.Amount.std()

        df["Anomaly"]=df.Amount.apply(
            lambda x:"⚠️" if abs(x-mean)>2*std else "Normal")

        st.subheader("Anomaly Detection")
        st.dataframe(df)

        # score
        score=100
        if df.Amount.sum()>50000:
            score-=25

        st.metric("Financial Health Score",score)

        # summary
        st.subheader("Summary")
        st.write(f"""
Total spending ₹{df.Amount.sum():.2f}

Highest category:
{df.groupby("Subcategory")["Amount"].sum().idxmax()}

Suggestion:
Reduce unnecessary spending and monitor anomalies.
""")

    if st.button("Logout"):
        st.session_state.user=None
        st.rerun()

# ---------------- ROUTING ----------------
if st.session_state.user is None:

    tab1,tab2=st.tabs(["Login","Register"])
    with tab1: login()
    with tab2: register()

else:
    dashboard()
