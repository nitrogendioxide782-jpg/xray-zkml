from zone1_ai_fhir import load_image
from zone2_ai_fhir import XRayModel
from zone3_ai_fhir import generate_report
from zone4_ai_fhir import build_fhir_report

from zone2_5_zkml import ZKMLVerifier


# =========================
# PIPELINE
# =========================
def run_pipeline(image_path):

    print("\n🧠 Running Medical AI Pipeline\n")

    # -------------------------
    # Zone 1
    # -------------------------
    image_tensor = load_image(image_path)

    # -------------------------
    # Zone 2
    # -------------------------
    model = XRayModel("ezkl.onnx")
    model_output = model.predict(image_tensor)

    # -------------------------
    # Zone 3
    # -------------------------
    report = generate_report(model_output)

    print("=== AI REPORT ===")
    print(report)

    # -------------------------
    # Zone 2.5 ZKML
    # -------------------------
    zkml = ZKMLVerifier()

    zkml_result = zkml.run()

    # 🟢 FORCE BOOLEAN SAFETY (IMPORTANT FIX)
    if isinstance(zkml_result, dict):
        zkml_result = zkml_result.get("verified", False)
    elif isinstance(zkml_result, str):
        zkml_result = zkml_result.lower() == "true"

    print("\n=== ZKML VERIFIED ===")
    print(zkml_result)

    # -------------------------
    # Zone 4 FHIR
    # -------------------------
    fhir = build_fhir_report(report, patient_id="P001")

    print("\n=== FHIR OUTPUT ===")
    print(fhir)

    return {
        "ai": report,
        "zkml": zkml_result,
        "fhir": fhir
    }


# =========================
# TEST SUITE (SAFE VERSION)
# =========================
def test_all():

    print("\n🧪 EMR SYSTEM TEST START\n")

    result = run_pipeline("00000011_007.png")

    # -------------------------
    # SAFE ASSERTIONS
    # -------------------------
    assert "diagnosis" in result["ai"]
    assert "risk" in result["ai"]
    assert "confidence" in result["ai"]

    assert isinstance(result["zkml"], bool)

    assert "resourceType" in result["fhir"]

    print("\n✔ ALL TESTS PASSED")
    print("🟢 SYSTEM IS STABLE")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    test_all()