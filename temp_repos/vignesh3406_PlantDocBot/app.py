import streamlit as st
import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image

from backend.treatments import get_treatment
from backend.chatbot import text_diagnosis   # ✅ NEW IMPORT

# ---------------- CONFIG ----------------
MODEL_PATH = "models/resnet50_plantvillage_checkpoint.pth"
IMG_SIZE = 224

st.set_page_config(
    page_title="PlantDocBot",
    page_icon="🌿",
    layout="centered"
)

# ---------------- LOAD MODEL ----------------
def load_model():
    checkpoint = torch.load(MODEL_PATH, map_location="cpu")
    state_dict = checkpoint["model_state_dict"]

    num_classes = state_dict["fc.weight"].shape[0]
    
    # CORRECTED WAY TO EXTRACT CLASS NAMES
    idx_to_class = checkpoint.get("idx_to_class", {})
    class_names = [idx_to_class[i] for i in sorted(idx_to_class.keys())]

    model = models.resnet50(pretrained=False)
    model.fc = torch.nn.Linear(2048, num_classes)
    model.load_state_dict(state_dict, strict=True)
    model.eval()

    return model, class_names


model, class_names = load_model()

# ---------------- IMAGE TRANSFORM ----------------
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# ---------------- UI ----------------
st.title("🌿 PlantDocBot – AI Plant Disease Diagnosis")
st.write("Upload a leaf image or describe plant symptoms to get diagnosis and treatment.")

# ---------------- IMAGE INPUT ----------------
uploaded_file = st.file_uploader(
    "📷 Upload a plant leaf image",
    type=["jpg", "jpeg", "png"]
)

# ---------------- TEXT INPUT (CHATBOT) ----------------
st.markdown("---")
st.subheader("💬 Describe Plant Symptoms (Chatbot)")

user_text = st.text_area(
    "Example: yellow leaves with brown spots, wilting plant, holes in leaves"
)

# ---------------- IMAGE DIAGNOSIS ----------------
image_disease = None
image_confidence = None

if uploaded_file:
    if uploaded_file.size > 3 * 1024 * 1024:
        st.error("⚠️ Image too large. Upload image smaller than 3MB.")
        st.stop()

    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Leaf Image", width=350)

    img_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img_tensor)
        probs = F.softmax(outputs, dim=1)[0]

    top3 = torch.topk(probs, min(3, len(class_names)))

    st.subheader("🔍 Image-based Predictions")
    for i in range(len(top3.indices)):
        label = class_names[top3.indices[i].item()]
        conf = top3.values[i].item() * 100
        st.write(f"{i+1}. **{label}** — {conf:.2f}%")

    pred_idx = torch.argmax(probs).item()
    image_disease = class_names[pred_idx]
    image_confidence = probs[pred_idx].item()

    if image_confidence >= 0.25:
        st.success(f"🌿 Image Diagnosis: **{image_disease}**")
        st.info(f"Confidence: **{image_confidence * 100:.2f}%**")
    else:
        st.warning("⚠️ Image diagnosis confidence is low.")

# ---------------- TEXT DIAGNOSIS ----------------
text_disease = None

if user_text:
    text_disease = text_diagnosis(user_text)
    st.subheader("🧠 Text-based Diagnosis")
    st.success(f"Possible Disease: **{text_disease}**")

# ---------------- FINAL RECOMMENDATION ----------------
if image_disease or text_disease:
    st.markdown("### ✅ Final Recommendation")

    final_disease = image_disease if image_confidence and image_confidence >= 0.25 else text_disease
    treatment = get_treatment(final_disease)

    st.write(f"**Final Disease Decision:** {final_disease}")
    st.warning(f"💊 **Recommended Treatment:** {treatment}")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("PlantDocBot | Image + Chatbot based Plant Disease Diagnosis")