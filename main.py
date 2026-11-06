from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import cv2
import base64
from insightface.app import FaceAnalysis

app = FastAPI()

# ✅ MAS MAGAAN: Gumamit ng 'buffalo_sc' (maliit na bersyon) at CPU lang
# Tinanggal din natin ang malaking detection size
face_app = FaceAnalysis(name='buffalo_sc', providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=-1, det_size=(320, 320)) # -1 means CPU, 320x320 is lighter

class ImagePair(BaseModel):
    image1: str
    image2: str

def decode_base64_image(base64_string):
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def get_embedding(img):
    faces = face_app.get(img)
    if len(faces) == 0:
        return None
    return faces[0].embedding

@app.post("/compare")
async def compare_faces(pair: ImagePair):
    try:
        img1 = decode_base64_image(pair.image1)
        img2 = decode_base64_image(pair.image2)

        if img1 is None or img2 is None:
            return {"success": False, "message": "Invalid image data"}

        emb1 = get_embedding(img1)
        emb2 = get_embedding(img2)

        if emb1 is None or emb2 is None:
            return {"success": False, "message": "No face detected"}

        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        is_same = bool(similarity > 0.5)

        return {"success": True, "is_same_person": is_same, "similarity": float(similarity)}
    except Exception as e:
        return {"success": False, "message": str(e)}
