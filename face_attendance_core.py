import math
import time
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class AttendanceRequest:
    image: Any
    timestamp: float
    user_history: Dict[str, Any]
    ref_embedding: List[float]
    gps_score: float = 1.0
    behavior_history_score: float = 0.0
    room_id: Optional[str] = None
    registered_gender: Optional[str] = None

@dataclass
class AttendanceResult:
    is_valid: bool
    risk_score: float
    face_score: float
    liveness_score: float
    details: Dict[str, Any]

class FaceAttendanceSystem:
    def __init__(self, w1: float = 0.4, w2: float = 0.4, w3: float = 0.1, w4: float = 0.1, threshold: float = 0.3):
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        self.w4 = w4
        self.threshold = threshold

    def detect_face(self, image):
        """
        Detect face, return region and metadata (like detected gender).
        """
    def detect_face(self, image_data):
        """
        Detect face, return region and metadata (like detected gender).
        Uses OpenCV for real detection if available.
        """
        if image_data is None:
            raise ValueError("No image provided")
        
        region = {"x": 0, "y": 0, "w": 100, "h": 100}
        detected_gender = "Male" # Default/Mock

        try:
            import cv2
            import numpy as np
            
            # Decode image bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                print("Warning: Could not decode image")
                return {"region": region, "gender": detected_gender}

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Load Haar Cascade (using cv2.data for path)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                # Take the largest face or first one
                # faces returns (x, y, w, h)
                (x, y, w, h) = faces[0]
                region = {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
                # Mock gender logic: Randomize or stick to default? 
                # Let's keep it simple: "Male" default, or maybe hash of coordinates to flip it for fun?
                # For demo stability, keep "Male" unless we add a gender model.
            else:
                print("No face detected by OpenCV")
                # We could raise error or return default region. 
                # For a smoother demo if slightly off-frame, maybe return empty or error?
                # Let's return default region but maybe flag it? 
                # Actually, if no face, we can't really extract embedding effectively in real life.
                # But for this stubbed system, we'll just fall back to valid region 0,0,100,100 so it doesn't crash.
                pass

        except ImportError:
            print("OpenCV not installed, using mock detection")
        except Exception as e:
            print(f"Face detection error: {e}")

        return {"region": region, "gender": detected_gender}

    def extract_embedding(self, face_region):
        return [0.1] * 128

    def check_liveness(self, face_region) -> float:
        return 0.95

    def compute_similarity(self, embedding_a: List[float], embedding_b: List[float]) -> float:
        if not embedding_a or not embedding_b:
            return 0.0
        if embedding_a == embedding_b:
            return 1.0
        return 0.0

    def calculate_risk(self, face_score: float, liveness_score: float, gps_score: float, behavior_history_score: float) -> float:
        risk = (self.w1 * (1 - face_score)) + \
               (self.w2 * (1 - liveness_score)) + \
               (self.w3 * (1 - gps_score)) + \
               (self.w4 * behavior_history_score)
        return risk

    def process_attendance(self, request: AttendanceRequest) -> AttendanceResult:
        try:
            # 1. Detect face and attributes
            # Note: request.image is bytes
            face_data = self.detect_face(request.image)
            face_region = face_data["region"]
            detected_gender = face_data.get("gender")
            
            # 2. Extract embedding
            embedding = self.extract_embedding(face_region)
            
            # 3. Liveness
            liveness_score = self.check_liveness(face_region)
            
            # 4. Similarity
            face_score = self.compute_similarity(embedding, request.ref_embedding)
            
            # Gender Check Enforcement
            gender_match = True
            if request.registered_gender and detected_gender:
                if request.registered_gender.lower() != detected_gender.lower():
                    gender_match = False
                    # Penalize Face Score for formula consistency
                    face_score = max(0.0, face_score - 0.5) 
            
            # Room Check / GPS
            # If room_id is wrong (mock check), penalize GPS
            if request.room_id == "FORBIDDEN_ROOM": 
                 request.gps_score = 0.0

            # 5. Risk
            risk = self.calculate_risk(
                face_score=face_score,
                liveness_score=liveness_score,
                gps_score=request.gps_score,
                behavior_history_score=request.behavior_history_score
            )
            
            # 6. Final Decision
            is_valid = risk < self.threshold
            
            return AttendanceResult(
                is_valid=is_valid,
                risk_score=risk,
                face_score=face_score,
                liveness_score=liveness_score,
                details={
                    "gps_score": request.gps_score,
                    "behavior_score": request.behavior_history_score,
                    "detected_gender": detected_gender,
                    "gender_match": gender_match,
                    "room_id": request.room_id,
                    "threshold_used": self.threshold,
                    "face_region": face_region # Return region for UI drawing
                }
            )
            
        except Exception as e:
            print(f"Error processing attendance: {e}")
            return AttendanceResult(
                is_valid=False,
                risk_score=1.0,
                face_score=0.0,
                liveness_score=0.0,
                details={"error": str(e)}
            )
