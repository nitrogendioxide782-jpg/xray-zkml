import json
from datetime import datetime


def build_fhir_report(ai_output, patient_id="P001"):

    diagnosis = ai_output.get("diagnosis", "")
    risk = ai_output.get("risk", "")
    confidence = ai_output.get("confidence", 0.0)

    # 🔒 強制 type safety（避免 Streamlit / API crash）
    try:
        confidence = float(confidence)
    except:
        confidence = 0.0

    fhir_resource = {
        "resourceType": "DiagnosticReport",
        "status": "final",

        "code": {
            "text": "Chest X-Ray AI Diagnosis"
        },

        "subject": {
            "reference": f"Patient/{patient_id}"
        },

        "effectiveDateTime": datetime.utcnow().isoformat(),

        "conclusion": str(diagnosis),

        "conclusionCode": [
            {
                "text": str(diagnosis)
            }
        ],

        "extension": [
            {
                "url": "http://example.org/fhir/StructureDefinition/risk-level",
                "valueString": str(risk)
            },
            {
                "url": "http://example.org/fhir/StructureDefinition/ai-confidence",
                "valueDecimal": confidence
            }
        ]
    }

    return fhir_resource


def to_fhir_json(fhir_resource):
    # ✔ 保證是合法 JSON（不是 Python dict）
    return json.dumps(
        fhir_resource,
        indent=2,
        ensure_ascii=False
    )