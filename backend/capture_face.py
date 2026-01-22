import cv2
import os
import sys
import time

# Get name from command line argument (sent by app.py)
if len(sys.argv) > 1:
    name = sys.argv[1]
else:
    name = "mahalaxmi"

# Create folder for the specific person
folder = f"database/{name}"
if not os.path.exists(folder):
    os.makedirs(folder)

cap = cv2.VideoCapture(0)
count = 0

print(f"--- Enrolling {name}. Look at the camera ---")

while count < 30:
    ret, frame = cap.read()
    if not ret:
        break

    # Save image
    img_path = os.path.join(folder, f"{name}_{count}.jpg")
    cv2.imwrite(img_path, frame)
    
    # Visual feedback on the enrollment window
    cv2.putText(frame, f"Capturing {name}: {count}/30", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 133), 2)
    cv2.imshow("Enrollment", frame)
    
    count += 1
    time.sleep(0.1) # Brief pause to get different angles

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"--- Successfully saved 30 images to {folder} ---")