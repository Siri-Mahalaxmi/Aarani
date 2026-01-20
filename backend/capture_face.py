import cv2
import os

# 1. Setup - Name of the person to enroll
name = "mahalaxmi" 
folder = f'database/{name}'

if not os.path.exists(folder):
    os.makedirs(folder)

# 2. Start Camera
cam = cv2.VideoCapture(0)
count = 0

print(f"--- Enrolling {name}. Look at the camera and move your head slowly ---")

while count < 30:
    ret, frame = cam.read()
    if not ret:
        break

    # Save the frame
    file_path = f"{folder}/{name}_{count}.jpg"
    cv2.imwrite(file_path, frame)
    
    # Show the capture live
    cv2.imshow("Enrolling...", frame)
    count += 1
    
    # Wait a bit so it doesn't take 30 photos in 1 second
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

print(f"--- Successfully saved {count} images to {folder} ---")
cam.release()
cv2.destroyAllWindows()