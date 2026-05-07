import streamlit as st
import threading
st.write("UI OK")
st.stop()
from zone1_ai_fhir import load_image
from zone2_ai_fhir import XRayModel
from zone3_ai_fhir import generate_report
from zone4_ai_fhir import build_fhir_report
from zone2_5_zkml import ZKMLVerifier

st.set_page_config(page_title="EMR SYSTEM - LOGIN MODE", layout="wide")

# -------------------------
# 🔐 LOGIN SYSTEM
# -------------------------
USERS = {
    "doctor": {"password": "1234", "role": "doctor"},
    "nurse": {"password": "1234", "role": "nurse"},
    "patient": {"password": "1234", "role": "patient"},
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None


def login():
    st.title("🔐 EMR LOGIN SYSTEM")

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
# PIPELINE
# -------------------------
if "result" not in st.session_state:
    st.session_state.result = None

if "running" not in st.session_state:
    st.session_state.running = False


def pipeline(image_path):
    try:
        image_tensor = load_image(image_path)

        model = XRayModel("ezkl.onnx")
        model_output = model.predict(image_tensor)

        report = generate_report(model_output)

        zkml = ZKMLVerifier()
        zkml_result = zkml.run()

        fhir = build_fhir_report(report, patient_id="P001")

        st.session_state.result = {
            "ai": report,
            "zkml": zkml_result,
            "fhir": fhir
        }

    except Exception as e:
        st.session_state.result = {"error": str(e)}

    st.session_state.running = False


# -------------------------
# IF NOT LOGIN → STOP HERE
# -------------------------
if not st.session_state.logged_in:
    login()
    st.stop()


# -------------------------
# MAIN UI
# -------------------------
st.title(f"🏥 EMR SYSTEM ({st.session_state.role.upper()})")

uploaded_file = st.file_uploader("📤 Upload Chest X-ray", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Input Image", width=300)

    if st.button("🚀 Run Verifiable AI Pipeline"):

        with open("temp.png", "wb") as f:
            f.write(uploaded_file.read())

        st.session_state.running = True
        st.session_state.result = None

        t = threading.Thread(target=pipeline, args=("temp.png",))
        t.start()

        st.info("🟢 Running pipeline...")

# -------------------------
# ROLE-BASED DISPLAY
# -------------------------
if st.session_state.result:

    result = st.session_state.result

    if "error" in result:
        st.error(result["error"])

    else:

        role = st.session_state.role

        st.subheader("🧠 AI RESULT")
        st.json(result["ai"])

        # 👨‍⚕️ DOCTOR
        if role == "doctor":
            st.subheader("🔐 ZKML VERIFICATION")
            st.write("VERIFIED" if result["zkml"] else "FAILED")

            st.subheader("🏥 FULL FHIR")
            st.json(result["fhir"])

        # 👩‍⚕️ NURSE
        elif role == "nurse":
            st.subheader("🏥 FHIR (CLINICAL VIEW)")
            fhir = result["fhir"].copy()
            fhir.pop("extension", None)
            st.json(fhir)

        # 🧑 PATIENT
        elif role == "patient":
            st.subheader("📋 Patient Summary")
            st.write("Diagnosis:", result["ai"]["diagnosis"])
            st.write("Risk:", result["ai"]["risk"])

if st.session_state.running:
    st.warning("⏳ Processing...")
