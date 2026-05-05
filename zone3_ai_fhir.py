def generate_report(model_output, threshold=0.506):

    prob = model_output["probability"]

    if prob < threshold:
        diagnosis = "PNEUMONIA"
        risk = "HIGH"
    else:
        diagnosis = "NORMAL"
        risk = "LOW"

    return {
        "diagnosis": diagnosis,
        "risk": risk,
        "confidence": round(prob, 4)
    }