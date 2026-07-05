def text_diagnosis(symptoms: str) -> str:
    text = symptoms.lower()

    if "yellow" in text and "spots" in text:
        return "Leaf Spot Disease"
    elif "brown" in text and "circle" in text:
        return "Early Blight"
    elif "wilting" in text:
        return "Wilt Disease"
    elif "rotten" in text or "water stress" in text:
        return "Possible Root or Water Stress"
    elif "holes" in text:
        return "Pest Attack"
    else:
        return "Unknown Disease"
