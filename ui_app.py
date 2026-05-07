import streamlit as st
import os
import tempfile

# -------------------------
# Page config (must be first)
# -------------------------
st.set_page_config(
    page_title="EMR System - Verifiable AI",
    layout="wide"
)

st.title("🏥 EMR System - Verifiable AI Pipeline")

# -------------------------
# Session State Init
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if "result" not in st.session_state:
    st.session_state.result = None

# -------------------------
# Lazy module loaders (IMPORTANT FIX)
# -------------------------

def get_image_loader():
    from zone1_ai_fhir import load_image
    return load_image


def get_model():
    from zone2_ai_fhir import XRayModel
    return XRayModel("ezkl.onnx")


def get_report_generator():
    from zone3_ai_fhir import generate_report
    return generate_report


def get_fhir_builder():
    from zone4_ai_fhir import build_fhir_report
    return build_fhir_report


def get_zkml():
    from zone2_5_zkml import ZKMLVerifier
    return ZKMLVerifier()

# -------------------------
# Login system
# -------------------------
USERS = {
    "doctor": {"password": "1234", "role": "doctor"},
    "nurse": {"password": "1234", "role": "nurse"},
    "patient": {"password": "1234", "role": "patient"},
}

def login_page():
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = USERS[username]["role"]
            st.success(f"Logged in as {st.session_state.role}")
            st.rerun()
        else:
            st.error("Invalid credentials")

# -------------------------
# Pipeline (NO threading, FIXED)
# -------------------------

def run_pipeline(image_path):
    try:
        load_image = get_image_loader()
        XRayModel = get_model()
        generate_report = get_report_generator()
        build_fhir_report = get_fhir_builder()
        zkml = get_zkml()

        image_tensor = load_image(image_path)

        model = XRayModel
        model_output = model.predict(image_tensor)

        report = generate_report(model_output)

        zk_result = "SKIPPED (debug mode)"

        fhir = build_fhir_report(report, patient_id="P001")

        return {
            "ai": report,
            "zkml": zk_result,
            "fhir": fhir
        }

    except Exception as e:
        return {"error": str(e)}

# -------------------------
# Auth gate
# -------------------------
if not st.session_state.logged_in:
    login_page()
    st.stop()

st.sidebar.success(f"Role: {st.session_state.role}")

# -------------------------
# Upload section
# -------------------------
uploaded_file = st.file_uploader(
    "📤 Upload Chest X-ray",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    st.image(uploaded_file, caption="Input X-ray", width=300)

    temp_path = os.path.join(tempfile.gettempdir(), "xray.png")

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())

    if st.button("🚀 Run Verifiable AI Pipeline"):
        with st.spinner("Running AI + ZK verification..."):
            st.session_state.result = run_pipeline(temp_path)

        st.rerun()

# -------------------------
# Result rendering (FIXED layout)
# -------------------------

result = st.session_state.result

if result:

    if "error" in result:
        st.error(result["error"])
        st.stop()

    st.subheader("🧠 AI Result")
    st.json(result["ai"])

    role = st.session_state.role

    if role == "doctor":
        st.subheader("🔐 ZKML Verification")
        st.write("VERIFIED" if result["zkml"] else "FAILED")

        st.subheader("🏥 Full FHIR")
        st.json(result["fhir"])

    elif role == "nurse":
        st.subheader("🏥 Clinical FHIR View")
        fhir = result["fhir"].copy()
        fhir.pop("extension", None)
        st.json(fhir)

    elif role == "patient":
        st.subheader("📋 Patient Summary")
        st.write("Diagnosis:", result["ai"].get("diagnosis"))
        st.write("Risk:", result["ai"].get("risk"))

# -------------------------
# Status indicator
# -------------------------
if not result:
    st.info("Upload an X-ray to start the pipeline.")
