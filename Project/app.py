# ======================================
# IMPORTS
# ======================================
import streamlit as st
import pandas as pd
import numpy as np
import re
import pickle
import os

# ======================================
# STREAMLIT CONFIG
# ======================================
st.set_page_config(
    page_title="Car Insurance Claim Risk Assessment",
    page_icon="🛡️",
    layout="wide"
)

# ======================================
# DARK THEME UI
# ======================================
st.markdown("""
<style>
body { background-color: #020617; color: #e5e7eb; }
.header { font-size: 36px; font-weight: 800; color: #f8fafc; }
.subheader { font-size: 18px; color: #94a3b8; margin-bottom: 20px; }
.card {
    background: #020617;
    padding: 28px;
    border-radius: 16px;
    border: 1px solid #1e293b;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    margin-bottom: 24px;
}
.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 15px;
    color: #e2e8f0;
}
.predict-btn button {
    background: linear-gradient(90deg, #38bdf8, #0ea5e9);
    color: #020617;
    font-size: 18px;
    font-weight: 800;
    border-radius: 14px;
    height: 60px;
}
.risk-high {
    background: linear-gradient(135deg, #7f1d1d, #991b1b);
    padding: 28px;
    border-radius: 14px;
    color: #fee2e2;
    font-size: 20px;
    font-weight: 800;
}
.risk-low {
    background: linear-gradient(135deg, #064e3b, #065f46);
    padding: 28px;
    border-radius: 14px;
    color: #dcfce7;
    font-size: 20px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# ======================================
# HEADER
# ======================================
st.markdown('<div class="header">🛡️ Car Insurance Claim Risk Assessment</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">AI-powered vehicle insurance claim prediction</div>', unsafe_allow_html=True)
st.divider()

# ======================================
# HELPER FUNCTIONS
# ======================================
def extract_number(text):
    try:
        return float(re.findall(r"\d+\.?\d*", str(text))[0])
    except:
        return 0.0

YES_NO_MAP = {"No": 0, "Yes": 1}
TEXT_NUMERIC_COLS = ["max_torque", "max_power"]

# ======================================
# LOAD MODEL
# ======================================
@st.cache_resource
def load_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "best_model.pkl")
    with open(path, "rb") as f:
        return pickle.load(f)

model = load_model()
st.success("✅ Model loaded")

# ======================================
# LOAD DATA
# ======================================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "CleanedDataset.csv")
    df = pd.read_csv(path)
    if "policy_id" in df.columns:
        df.drop("policy_id", axis=1, inplace=True)
    df.replace({"Yes": 1, "No": 0}, inplace=True)
    return df

raw_df = load_data()

# ======================================
# INPUT UI
# ======================================
# st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Vehicle & Policy Details</div>', unsafe_allow_html=True)

user_input = {}

# ---------- BASIC DETAILS ----------
st.markdown("### 🔹 Basic Details")

basic_cols = [
    "age_of_car",
    "vehicle_age",
    "policy_tenure",
    "segment",
    "fuel_type",
    "transmission_type",
    "engine_type",
    "steering_type",
    "ncap_rating",

    # ---- Binary safety / comfort features ----
    "is_commercial_vehicle",
    "is_power_steering",
    "is_day_night_rear_view_mirror",
    "is_speed_alert",
    "is_rear_window_wiper",
    "is_front_fog_lights",
    "is_brake_assist"
]

basic_cols = [c for c in basic_cols if c in raw_df.columns]

cols = st.columns(3)
idx = 0

for col in basic_cols:
    with cols[idx % 3]:
        label = col.replace("_", " ").title()

        # ALL is_* → Yes / No
        if col.startswith("is_"):
            user_input[col] = YES_NO_MAP[
                st.selectbox(label, ["No", "Yes"])
            ]
        elif raw_df[col].dtype == "object":
            user_input[col] = st.selectbox(
                label,
                sorted(raw_df[col].dropna().unique())
            )
        else:
            user_input[col] = st.number_input(
                label,
                value=float(raw_df[col].median())
            )
    idx += 1

# ---------- ADVANCED DETAILS ----------
with st.expander("⚙️ Advanced Vehicle Details (Optional)"):
    advanced_cols = [
        c for c in raw_df.columns
        if c not in basic_cols and c != "is_claim"
    ]

    cols = st.columns(3)
    idx = 0

    for col in advanced_cols:
        with cols[idx % 3]:
            label = col.replace("_", " ").title()

            if col.startswith("is_"):
                user_input[col] = YES_NO_MAP[
                    st.selectbox(label, ["No", "Yes"])
                ]
            elif col in TEXT_NUMERIC_COLS:
                user_input[col] = st.text_input(
                    label, value=str(raw_df[col].mode()[0])
                )
            elif raw_df[col].dtype == "object":
                user_input[col] = st.selectbox(
                    label,
                    sorted(raw_df[col].dropna().unique())
                )
            else:
                user_input[col] = st.number_input(
                    label,
                    value=float(raw_df[col].median())
                )
        idx += 1

st.markdown('</div>', unsafe_allow_html=True)

# ======================================
# PREPROCESSING
# ======================================
input_df = pd.DataFrame([user_input])

if "max_torque" in input_df.columns:
    input_df["torque"] = input_df["max_torque"].apply(extract_number)
    input_df.drop("max_torque", axis=1, inplace=True)

if "max_power" in input_df.columns:
    input_df["power"] = input_df["max_power"].apply(extract_number)
    input_df.drop("max_power", axis=1, inplace=True)

cat_cols = input_df.select_dtypes(include="object").columns
input_encoded = pd.get_dummies(input_df, columns=cat_cols, drop_first=True)

input_encoded = input_encoded.reindex(
    columns=model.feature_names_in_,
    fill_value=0
)

# ======================================
# PREDICTION
# ======================================
st.markdown('<div class="predict-btn">', unsafe_allow_html=True)
predict = st.button("Assess Claim Risk", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if predict:
    pred = model.predict(input_encoded)[0]
    prob = model.predict_proba(input_encoded)[0][1]

    st.divider()

    if pred == 1:
        st.markdown(
            f'<div class="risk-high">🚨 Likely Claim<br><br>Probability: {prob:.2%}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="risk-low">✅ No Claim Expected<br><br>Probability: {prob:.2%}</div>',
            unsafe_allow_html=True
        )
