TREATMENTS = {
    "Tomato___Late_blight": "Use copper-based fungicide. Avoid overhead watering.",
    "Tomato___Early_blight": "Remove infected leaves. Apply mancozeb or chlorothalonil.",
    "Tomato___Leaf_Mold": "Spray fungicide and remove infected plants immediately.",
    "Potato___Late_blight": "Apply appropriate fungicide and practice crop rotation.",
    "Potato___Bacterial_spot": "Use disease-free seeds and copper sprays.",
    "Healthy": "No treatment needed. Maintain proper irrigation and nutrition.",
    
    # Newly added treatments for diseases identified by the model
    "Pepper__bell___Bacterial_spot": "Apply copper-based bactericides. Remove severely infected plants. Ensure good air circulation.",
    "Pepper__bell___healthy": "No specific treatment needed. Maintain optimal growing conditions.",
    "Potato___Early_blight": "Apply fungicides containing chlorothalonil or mancozeb. Rotate crops.",
    "Potato___healthy": "No specific treatment needed. Maintain optimal growing conditions.",
    "Tomato_Bacterial_spot": "Apply copper-based bactericides and fungicides. Remove infected plant parts.",
    "Tomato_Septoria_leaf_spot": "Apply fungicides containing chlorothalonil or mancozeb. Remove infected leaves.",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Use insecticidal soaps or neem oil. Introduce predatory mites.",
    "Tomato__Target_Spot": "Apply fungicides such as azoxystrobin or chlorothalonil. Improve air circulation.",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Manage whiteflies, which transmit the virus. Use resistant varieties. Remove infected plants.",
    "Tomato__Tomato_mosaic_virus": "Remove and destroy infected plants. Use disease-free seeds. Disinfect tools.",
}

def get_treatment(disease_name):
    return TREATMENTS.get(
        disease_name,
        "No specific treatment found. Consult an agricultural expert."
    )