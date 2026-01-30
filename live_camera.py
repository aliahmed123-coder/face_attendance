import cv2
import requests
import json
import time

# API Configuration
API_URL = "http://localhost:8000/verify"

def main():
    print("Starting Live Face Attendance Client...")
    print("Press 'q' to quit.")

    # dummy data
    user_history = {"last_seen": "today"}
    # Using same ref embedding as mock in core to get Match
    ref_embedding = [0.1] * 128 
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    frame_count = 0
    last_result = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        frame_count += 1
        
        # Send every 30th frame (approx 1 per second) to avoid overloading API/Network
        if frame_count % 30 == 0:
            try:
                # Encode image
                _, img_encoded = cv2.imencode('.jpg', frame)
                
                # Prepare payload
                files = {
                    "image": ("cam.jpg", img_encoded.tobytes(), "image/jpeg")
                }
                data = {
                    "timestamp": time.time(),
                    "user_history": json.dumps(user_history),
                    "ref_embedding": json.dumps(ref_embedding),
                    "gps_score": 1.0,
                    "behavior_history_score": 0.0,
                    "room_id": "ROOM_A",
                    "registered_gender": "Male"
                }
                
                # Send Request
                # Use a short timeout so UI doesn't freeze too much (threaded is better but keeping simple)
                response = requests.post(API_URL, data=data, files=files, timeout=2)
                
                if response.status_code == 200:
                    last_result = response.json()
                    # print(f"API Result: {last_result['is_valid']}")
                else:
                    print(f"API Error: {response.status_code}")
                    
            except Exception as e:
                print(f"Request Error: {e}")

        # Draw UI
        if last_result:
            valid = last_result.get("is_valid", False)
            details = last_result.get("details", {})
            region = details.get("face_region", {})
            risk = last_result.get("risk_score", 0.0)
            
            # Status Text
            color = (0, 255, 0) if valid else (0, 0, 255) # Green / Red
            status_text = f"VALID (Risk: {risk:.2f})" if valid else f"FRAUD (Risk: {risk:.2f})"
            
            cv2.putText(frame, status_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # Draw Face Box if provided (and if it matches current frame somewhat?)
            # The box is from 1 sec ago, so might lag. 
            # But shows detection happened.
            if region:
                x, y, w, h = region.get("x",0), region.get("y",0), region.get("w",0), region.get("h",0)
                if w > 0:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

        cv2.imshow('Face Attendance Live', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
