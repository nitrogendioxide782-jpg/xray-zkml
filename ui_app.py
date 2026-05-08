import streamlit as st
import hashlib
import uuid
from datetime import datetime

from zone1_ai_fhir import load_image
from zone2_ai_fhir import XRayModel
from zone3_ai_fhir import generate_report
from zone4_ai_fhir import build_fhir_report
from zone2_5_zkml import ZKMLVerifier


# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="EMR SYSTEM - Secure AI Demo",
    layout="wide"
)


# -------------------------
# USERS
# -------------------------
USERS = {
    "doctor": hashlib.sha256("1234".encode()).hexdigest(),
    "nurse": hashlib.sha256("1234".encode()).hexdigest(),
    "patient": hashlib.sha256("1234".encode()).hexdigest(),
}


# -------------------------
# INIT STATE
# -------------------------
def init_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "role" not in st.session_state:
        st.session_state.role = None

    if "result" not in st.session_state:
        st.session_state.result = None


init_state()


# -------------------------
# RESET SESSION
# -------------------------
def reset_session():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.result = None
    st.rerun()


# -------------------------
# LOGIN PAGE
# -------------------------
def login_page():
    st.title("🔐 EMR LOGIN SYSTEM")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login", key="login_btn"):
        if username in USERS:
            hashed = hashlib.sha256(password.encode()).hexdigest()

            if hashed == USERS[username]:
                st.session_state.logged_in = True
                st.session_state.role = username
                st.success(f"Logged in as {username}")
                st.rerun()
            else:
                st.error("Wrong password")
        else:
            st.error("User not found")


# -------------------------
# CACHE MODELS
# -------------------------
@st.cache_resource
def get_model():
    return XRayModel("ezkl.onnx")


@st.cache_resource
def get_verifier():
    return ZKMLVerifier()


# -------------------------
# PIPELINE
# -------------------------
def run_pipeline(image_path):
    image_tensor = load_image(image_path)

    model = get_model()
    ai_output = model.predict(image_tensor)

    report = generate_report(ai_output)

    # TEMP MOCK FOR COLAB
    zkml_result = True

    fhir = build_fhir_report(report, patient_id="P001")

    return {
        "ai": report,
        "zkml": zkml_result,
        "fhir": fhir,
        "timestamp": datetime.now().isoformat()
    }


# -------------------------
# ROLE VIEW
# -------------------------
def role_view(result, role):

    base = {
        "ai": result["ai"],
        "timestamp": result["timestamp"]
    }

    if role == "doctor":
        return {
            **base,
            "zkml": result["zkml"],
            "fhir": result["fhir"]
        }

    if role == "nurse":
        fhir = result["fhir"].copy()
        fhir.pop("extension", None)
        return {**base, "fhir": fhir}

    if role == "patient":
        return {
            "summary": {
                "diagnosis": result["ai"]["diagnosis"],
                "risk": result["ai"]["risk"]
            }
        }


# -------------------------
# SIDEBAR (ONLY ONCE)
# -------------------------
def sidebar():
    st.sidebar.title("🔐 Session Control")

    st.sidebar.write(f"Role: **{st.session_state.role}**")

    if st.sidebar.button("🔄 Logout / Switch Role", key="logout_btn"):
        reset_session()


# -------------------------
# LOGIN GATE
# -------------------------
if not st.session_state.logged_in:
    login_page()
    st.stop()

sidebar()


# -------------------------
# MAIN UI
# -------------------------
st.title(f"🏥 EMR SYSTEM ({st.session_state.role.upper()})")

uploaded_file = st.file_uploader(
    "📤 Upload Chest X-ray",
    type=["png", "jpg", "jpeg"],
    key="uploader"
)

# reset result when new file uploaded
if uploaded_file:
    st.session_state.result = None

    st.image(uploaded_file, width=300)

    if st.button("🚀 Run AI Pipeline", key="run_btn"):

        temp_path = f"temp_{uuid.uuid4().hex}.png"

        file_bytes = uploaded_file.getvalue()
        with open(temp_path, "wb") as f:
            f.write(file_bytes)

        with st.spinner("Processing AI + ZK verification..."):
            st.session_state.result = run_pipeline(temp_path)


# -------------------------
# OUTPUT
# -------------------------
if st.session_state.result:

    result = st.session_state.result

    if "error" in result:
        st.error(result["error"])

    else:
        view = role_view(result, st.session_state.role)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🧠 AI Result")
            st.json(view.get("ai", view.get("summary")))

        with col2:

            if st.session_state.role == "doctor":
                st.subheader("🔐 ZKML Verification")

                zkml = view.get("zkml")
                if isinstance(zkml, dict) and "error" in zkml:
                    st.error(zkml["error"])
                else:
                    st.write("VERIFIED" if zkml else "FAILED")

                st.subheader("🏥 FHIR Full Data")
                st.json(view["fhir"])

            elif st.session_state.role == "nurse":
                st.subheader("🏥 Clinical FHIR View")
                st.json(view["fhir"])

            elif st.session_state.role == "patient":
                st.subheader("📋 Patient Summary")
                st.json(view["summary"])


# -------------------------
# STATUS
# -------------------------
st.divider()

if st.session_state.result:
    st.success("Pipeline completed")
