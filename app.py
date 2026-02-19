import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Smart Spend Analyzer", layout="wide")

st.title(" Smart Spend Analyzer")



@st.cache_data
def load_data():
    df = pd.read_csv("Personal_Finance_Dataset.csv")
    return df

df = load_data()


df.columns = df.columns.str.strip()


rename_map = {}

if "transaction_amount" in df.columns:
    rename_map["transaction_amount"] = "Amount"
if "category" in df.columns:
    rename_map["category"] = "Category"
if "subcategory" in df.columns:
    rename_map["subcategory"] = "Subcategory"

df.rename(columns=rename_map, inplace=True)


required = ["Amount", "Category"]
for col in required:
    if col not in df.columns:
        st.error(f"Dataset must contain column: {col}")
        st.stop()


try:
    model = joblib.load("anomaly_model.pkl")
except:
    model = None

st.sidebar.header("Filter Transactions")

categories = st.sidebar.multiselect(
    "Select Category",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

filtered = df[df["Category"].isin(categories)]


st.subheader("📊 Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Spend", f"₹{filtered['Amount'].sum():,.2f}")
col2.metric("Transactions", len(filtered))
col3.metric("Average", f"₹{filtered['Amount'].mean():.2f}")


st.subheader("Category Breakdown")

cat_sum = filtered.groupby("Category")["Amount"].sum()
st.bar_chart(cat_sum)


if "Subcategory" in filtered.columns:
    st.subheader("Sub-Category Breakdown")
    sub_sum = filtered.groupby("Subcategory")["Amount"].sum()
    st.bar_chart(sub_sum)


st.subheader(" Unusual Transactions")

if model is not None:
    try:
        filtered["Anomaly"] = model.predict(filtered[["Amount"]])
        anomalies = filtered[filtered["Anomaly"] == -1]

        if anomalies.empty:
            st.success("No unusual transactions detected ✅")
        else:
            st.warning(f"{len(anomalies)} unusual transactions found")
            st.dataframe(anomalies)
    except:
        st.error("Model loaded but prediction failed. Check Amount column format.")
else:
    st.warning("No anomaly model found. Upload anomaly_model.pkl")


st.subheader(" Financial Health Summary")

total = filtered["Amount"].sum()
avg = filtered["Amount"].mean()
top = filtered.groupby("Category")["Amount"].sum().idxmax()

summary = f"""
You spent a total of ₹{total:.2f}.
Your highest spending category is {top}.
Your average transaction amount is ₹{avg:.2f}.

Tip: Consider reducing spending in your top category to improve savings.
"""

st.info(summary)


with st.expander("View Raw Data"):
    st.dataframe(filtered)
