import cv2
import numpy as np
import mediapipe as mp
from pythonosc import udp_client
import sys
import math

# Initialize OSC client
osc_client = udp_client.SimpleUDPClient("127.0.0.1", 4567)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# Start webcam capture
cap = cv2.VideoCapture(6)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    sys.exit(1)

# Try to get a frame from the webcam
for _ in range(10):  # Try up to 10 times
    ret, frame = cap.read()
    if ret:
        break
    else:
        print("Warning: Failed to grab frame. Retrying...")

if not ret:
    print("Error: Could not read frame from webcam after multiple attempts.")
    cap.release()
    sys.exit(1)

# Get the frame dimensions
frame_height, frame_width, _ = frame.shape

def remap_distance(distance):
    # Adjust these values based on your observations
    min_distance = 0.5
    max_distance = 1.0
    
    # Remap the distance
    remapped = (distance - min_distance) / (max_distance - min_distance)
    
    # Clamp the value between 0 and 1
    return max(0, min(remapped, 1))

while True:
    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    max_relative_distance1 = 0
    max_normalized_angle1 = 0
    max_relative_distance2 = 0
    max_normalized_angle2 = 0
    max_hand = None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get coordinates of thumb, index finger, pinky finger, and wrist
            thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            pinky = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

            # Calculate hand length (wrist to index finger tip)
            hand_length = np.hypot(index.x - wrist.x, index.y - wrist.y)

            # Calculate distances
            distance1 = np.hypot(index.x - thumb.x, index.y - thumb.y)
            distance2 = np.hypot(pinky.x - thumb.x, pinky.y - thumb.y)

            # Calculate relative distances
            relative_distance1 = distance1 / hand_length
            relative_distance2 = distance2 / hand_length

            # Calculate angles
            dx1 = index.x - thumb.x
            dy1 = index.y - thumb.y
            dx2 = pinky.x - thumb.x
            dy2 = pinky.y - thumb.y
            angle1 = math.degrees(math.atan2(abs(dy1), abs(dx1)))
            angle2 = math.degrees(math.atan2(abs(dy2), abs(dx2)))
            normalized_angle1 = angle1 / 90  # This will be 0 for horizontal, 1 for vertical
            normalized_angle2 = angle2 / 90  # This will be 0 for horizontal, 1 for vertical

            # Update max values if this hand has a greater distance
            if relative_distance1 > max_relative_distance1:
                max_relative_distance1 = relative_distance1
                max_normalized_angle1 = normalized_angle1
                max_relative_distance2 = relative_distance2
                max_normalized_angle2 = normalized_angle2
                max_hand = ((thumb.x, thumb.y), (index.x, index.y), (pinky.x, pinky.y))

    if max_hand:
        # Remap the distances
        remapped_distance1 = remap_distance(max_relative_distance1)
        remapped_distance2 = remap_distance(max_relative_distance2)
        
        # Send OSC messages for the hand with maximum distance
        osc_client.send_message("/hand/distance1", remapped_distance1)
        osc_client.send_message("/hand/rotation1", max_normalized_angle1)
        osc_client.send_message("/hand/distance2", remapped_distance2)
        osc_client.send_message("/hand/rotation2", max_normalized_angle2)

        # Draw lines
        thumb_point = (int(max_hand[0][0] * frame_width), int(max_hand[0][1] * frame_height))
        index_point = (int(max_hand[1][0] * frame_width), int(max_hand[1][1] * frame_height))
        pinky_point = (int(max_hand[2][0] * frame_width), int(max_hand[2][1] * frame_height))
        cv2.line(img, thumb_point, index_point, (0, 255, 0), 2)
        cv2.line(img, thumb_point, pinky_point, (255, 0, 0), 2)

        # Display the remapped distances and normalized angles
        cv2.putText(img, f'Dist1: {remapped_distance1:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f'Angle1: {max_normalized_angle1:.2f}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f'Dist2: {remapped_distance2:.2f}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(img, f'Angle2: {max_normalized_angle2:.2f}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Hand Tracking", img)

    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()
