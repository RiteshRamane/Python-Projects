import streamlit as st
import pandas as pd
import re
import pickle
import os

# ======================================
# STREAMLIT CONFIG
# ======================================
st.set_page_config(
    page_title="Vehicle Insurance Claim Prediction",
    layout="wide"
)
st.title("Vehicle Insurance Claim Prediction")


# ======================================
# HELPER FUNCTION
# ======================================
def extract_number(text):
    try:
        return float(re.findall(r"\d+\.?\d*", str(text))[0])
    except:
        return 0.0


TEXT_NUMERIC_COLS = ["max_torque", "max_power"]


# ======================================
# LOAD MODEL
# ======================================
@st.cache_resource
def load_model():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "best_model.pkl")

    if not os.path.exists(MODEL_PATH):
        st.error(f"❌ Model file not found:\n{MODEL_PATH}")
        st.stop()

    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    return model


model = load_model()
st.success("✅ Model loaded successfully")


# ======================================
# LOAD DATASET
# ======================================
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "CleanedDataset.csv")

    if not os.path.exists(DATA_PATH):
        st.error(f"❌ Dataset not found:\n{DATA_PATH}")
        st.stop()

    df = pd.read_csv(DATA_PATH)

    if "policy_id" in df.columns:
        df.drop("policy_id", axis=1, inplace=True)

    df.replace({"Yes": 1, "No": 0}, inplace=True)
    return df


raw_df = load_data()


# ======================================
# USER INPUT FORM
# ======================================
st.divider()
st.subheader("Enter Vehicle & Policy Details")

user_input = {}
cols = st.columns(3)
idx = 0

for col in raw_df.columns:
    if col == "is_claim":
        continue

    with cols[idx % 3]:

        if col in TEXT_NUMERIC_COLS:
            user_input[col] = st.text_input(
                col, value=str(raw_df[col].mode()[0])
            )

        elif raw_df[col].dtype == "object":
            user_input[col] = st.selectbox(
                col, sorted(raw_df[col].dropna().unique())
            )

        else:
            user_input[col] = st.number_input(
                col, value=float(raw_df[col].mean())
            )

    idx += 1


# ======================================
# INPUT PREPROCESSING
# ======================================
input_df = pd.DataFrame([user_input])

# Torque / Power extraction
if "max_torque" in input_df.columns:
    input_df["torque"] = input_df["max_torque"].apply(extract_number)
    input_df.drop("max_torque", axis=1, inplace=True)

if "max_power" in input_df.columns:
    input_df["power"] = input_df["max_power"].apply(extract_number)
    input_df.drop("max_power", axis=1, inplace=True)

# One-hot encoding
cat_cols = input_df.select_dtypes(include="object").columns
input_encoded = pd.get_dummies(input_df, columns=cat_cols, drop_first=True)


# ======================================
# FEATURE ALIGNMENT (CRITICAL FIX)
# ======================================
trained_features = model.feature_names_in_

input_encoded = input_encoded.reindex(
    columns=trained_features,
    fill_value=0
)


# ======================================
# PREDICTION
# ======================================
if st.button("Predict Claim", use_container_width=True):

    prediction = model.predict(input_encoded)[0]

    if hasattr(model, "predict_proba"):
        probability = model.predict_proba(input_encoded)[0][1]
    else:
        probability = None

    st.divider()

    if prediction == 1:
        st.error(
            f" CLAIM LIKELY"
            + (f"\n\nProbability: {probability:.2f}" if probability else "")
        )
    else:
        st.success(
            f" NO CLAIM"
            + (f"\n\nProbability: {probability:.2f}" if probability else "")
        )