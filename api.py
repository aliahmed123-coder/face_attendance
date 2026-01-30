from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import Optional, List
import json
import uvicorn
from contextlib import asynccontextmanager

from face_attendance_core import FaceAttendanceSystem, AttendanceRequest, AttendanceResult

# Initialize System
# In a real app, you might load models here
system = FaceAttendanceSystem()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load models if needed
    print("Face Attendance API Starting...")
    yield
    # Shutdown
    print("Face Attendance API Shutting down...")

app = FastAPI(title="Face Attendance API", lifespan=lifespan)

@app.post("/verify")
async def verify_attendance(
    image: UploadFile = File(...),
    timestamp: float = Form(...),
    user_history: str = Form(...), # JSON string
    ref_embedding: str = Form(...), # JSON string of list[float]
    gps_score: float = Form(1.0),
    behavior_history_score: float = Form(0.0),
    room_id: Optional[str] = Form(None),
    registered_gender: Optional[str] = Form(None)
):
    try:
        # Parse JSON fields
        history_dict = json.loads(user_history)
        embedding_list = json.loads(ref_embedding)
        
        # Read image bytes (In real app, convert to numpy/image format)
        image_bytes = await image.read()
        
        # Construct Request
        request = AttendanceRequest(
            image=image_bytes,
            timestamp=timestamp,
            user_history=history_dict,
            ref_embedding=embedding_list,
            gps_score=gps_score,
            behavior_history_score=behavior_history_score,
            room_id=room_id,
            registered_gender=registered_gender
        )
        
        # Process
        result = system.process_attendance(request)
        
        return {
            "is_valid": result.is_valid,
            "risk_score": result.risk_score,
            "face_score": result.face_score,
            "liveness_score": result.liveness_score,
            "details": result.details
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in form data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
