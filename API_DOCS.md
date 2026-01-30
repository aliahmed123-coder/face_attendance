# Face Attendance API Documentation

## Base URL
`http://localhost:8000`

## Endpoints

### 1. Verify Attendance
**URL**: `/verify`
**Method**: `POST`
**Content-Type**: `multipart/form-data`

#### Description
Processes an attendance request by analyzing the uploaded face image and metadata against the reference data.

#### Request Parameters

| Field | Type | Description |
|---|---|---|
| `image` | File (Upload) | The image file containing the user's face (JPEG/PNG). |
| `timestamp` | Float | Unix timestamp of the request. |
| `user_history` | String (JSON) | JSON object containing user behavior history. |
| `ref_embedding` | String (JSON) | JSON array of floats representing the registered face embedding (128-d). |
| `gps_score` | Float | (Optional) Location trust score (0.0 - 1.0). Default: 1.0. |
| `behavior_history_score`| Float | (Optional) Risk score based on past behavior (0.0 good - 1.0 bad). Default 0.0. |
| `room_id` | String | (Optional) Room ID for geofencing check. |
| `registered_gender` | String | (Optional) Expected gender of the user (e.g., "Male", "Female"). |

#### Response Format (JSON)

```json
{
  "is_valid": boolean,          // True if Risk < Threshold
  "risk_score": float,          // Calculated Risk (0.0 - 1.0)
  "face_score": float,          // Similarity Score (0.0 - 1.0)
  "liveness_score": float,      // Liveness Confidence (0.0 - 1.0)
  "details": {
    "gps_score": float,
    "behavior_score": float,
    "detected_gender": string,
    "gender_match": boolean,
    "room_id": string,
    "threshold_used": float,
    "face_region": { "x": int, "y": int, "w": int, "h": int }
  }
}
```

#### Example Usage (Python Requests)

```python
import requests
import json
import time

url = "http://localhost:8000/verify"

files = { "image": open("face.jpg", "rb") }
data = {
    "timestamp": time.time(),
    "user_history": json.dumps({"frequent_locations": ["Room A"]}),
    "ref_embedding": json.dumps([0.1] * 128),
    "gps_score": 0.95,
    "room_id": "Room A",
    "registered_gender": "Male"
}

response = requests.post(url, files=files, data=data)
print(response.json())
```
