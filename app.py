import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Smart Spend Analyzer", layout="wide")

st.title("💰 Smart Spend Analyzer")

# Load files
df = pd.read_csv("Personal_Finance_Dataset.csv")
model = joblib.load("anomaly_model.pkl")

# Sidebar Filters
st.sidebar.header("Filters")

category = st.sidebar.multiselect(
    "Select Category",
    df["Category"].unique(),
    default=df["Category"].unique()
)

filtered = df[df["Category"].isin(category)]

# Metrics
st.subheader("📊 Overview")
col1, col2, col3 = st.columns(3)

col1.metric("Total Spend", f"₹{filtered['Amount'].sum():,.2f}")
col2.metric("Transactions", len(filtered))
col3.metric("Average", f"₹{filtered['Amount'].mean():.2f}")

# Category chart
st.subheader("Category Breakdown")
cat_sum = filtered.groupby("Category")["Amount"].sum()
st.bar_chart(cat_sum)

# Subcategory
st.subheader("Sub-Category Breakdown")
sub_sum = filtered.groupby("Subcategory")["Amount"].sum()
st.bar_chart(sub_sum)

# Anomaly Detection
st.subheader("🚨 Unusual Transactions")

filtered["Anomaly"] = model.predict(filtered[["Amount"]])
anomaly_df = filtered[filtered["Anomaly"] == -1]

st.dataframe(anomaly_df)

# Summary
st.subheader("🧠 Financial Health Summary")

total = filtered["Amount"].sum()
highest = filtered.groupby("Category")["Amount"].sum().idxmax()
avg = filtered["Amount"].mean()

summary = f"""
You spent a total of ₹{total:.2f}.
Your highest spending category is {highest}.
Average transaction amount is ₹{avg:.2f}.
"""

st.info(summary)

