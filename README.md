# Face Attendance System

A comprehensive Face Attendance solution featuring API integration and live camera verification with liveness and fraud detection.

## Features
- **Core Logic**: Multi-factor risk scoring based on Face Similarity, Liveness, GPS, and User History.
- **Computer Vision**: Real-time face detection using OpenCV.
- **API**: FastAPI-based REST API for easy integration.
- **Live Demo**: Client script to demonstrate real-time attendance marking via webcam.
- **Enhanced Security**: Gender verification and Geofencing (Room ID) support.

## Installation

1.  **Clone/Download** the repository.
2.  **Install Dependencies**:
    ```bash
    pip install fastapi uvicorn python-multipart requests opencv-python numpyhttpx
    ```
    *Note: If using a virtual environment, ensure it is activated.*

## Project Structure
- `face_attendance_core.py`: Main logic class (`FaceAttendanceSystem`).
- `api.py`: FastAPI server application.
- `live_camera.py`: Client script for webcam demo.
- `verify_attendance.py`: Script to verify core logic formulas.
- `test_api.py`: Script to test API endpoints.

## Usage

### 1. Start the API Server
Run the following command to start the backend:
```bash
python -m uvicorn api:app --reload
```
The API will be available at `http://localhost:8000`.
- **Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Run the Live Camera Demo
With the API running, open a new terminal and run:
```bash
python live_camera.py
```
This will open a window showing your webcam feed. It sends frames to the API and displays `VALID` (Green) or `FRAUD` (Red) based on the risk analysis.
- Press `q` to quit the demo.

### 3. Run Tests
To verify the system logic:
```bash
python verify_attendance.py
python test_api.py
```

## Configuration
The system uses a weighted risk formula:
`Risk = w1*(1-FaceScore) + w2*(1-LivenessScore) + w3*(1-GPSScore) + w4*BehaviorHistory`

Default Weights in `face_attendance_core.py`:
- Face: 0.4
- Liveness: 0.4
- GPS: 0.1
- History: 0.1
- Threshold: 0.3

You can adjust these in the `FaceAttendanceSystem` `__init__` method.
