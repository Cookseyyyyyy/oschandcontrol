import cv2
import numpy as np
import mediapipe as mp
from pythonosc import udp_client
import sys
import math
import itertools

# Initialize OSC client
osc_client = udp_client.SimpleUDPClient("192.168.1.22", 4567)

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
cap = cv2.VideoCapture(4)

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

# Landmarks to track (including wrist)
landmarks_to_track = [mp_hands.HandLandmark.WRIST,
                      mp_hands.HandLandmark.THUMB_TIP,
                      mp_hands.HandLandmark.INDEX_FINGER_TIP,
                      mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                      mp_hands.HandLandmark.RING_FINGER_TIP,
                      mp_hands.HandLandmark.PINKY_TIP]

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

    max_relative_distance = 0
    max_normalized_angle = 0
    max_hand = None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get coordinates of tracked landmarks
            coords = []
            for lm in landmarks_to_track:
                x = hand_landmarks.landmark[lm].x
                y = hand_landmarks.landmark[lm].y
                coords.append((x, y))

            # Calculate hand length (wrist to middle finger tip)
            wrist = coords[0]
            middle_tip = coords[3]  # Index 3 corresponds to the middle finger tip
            hand_length = np.hypot(middle_tip[0] - wrist[0], middle_tip[1] - wrist[1])

            # Find the two fingers that are furthest apart
            max_distance = 0
            furthest_fingers = None
            for (x1, y1), (x2, y2) in itertools.combinations(coords[1:], 2):  # Exclude wrist
                distance = np.hypot(x2 - x1, y2 - y1)
                if distance > max_distance:
                    max_distance = distance
                    furthest_fingers = ((x1, y1), (x2, y2))

            # Calculate relative distance and angle
            relative_distance = max_distance / hand_length
            dx = furthest_fingers[1][0] - furthest_fingers[0][0]
            dy = furthest_fingers[1][1] - furthest_fingers[0][1]
            angle = math.degrees(math.atan2(abs(dy), abs(dx)))
            normalized_angle = angle / 90  # This will be 0 for horizontal, 1 for vertical

            # Update max values if this hand has a greater distance
            if relative_distance > max_relative_distance:
                max_relative_distance = relative_distance
                max_normalized_angle = normalized_angle
                max_hand = furthest_fingers

    if max_hand:
        # Remap the distance
        remapped_distance = remap_distance(max_relative_distance)
        
        # Send OSC messages for the hand with maximum distance
        osc_client.send_message("/hand/distance", remapped_distance)
        osc_client.send_message("/hand/rotation", max_normalized_angle)

        # Draw a line between the furthest fingers
        start_point = (int(max_hand[0][0] * frame_width), int(max_hand[0][1] * frame_height))
        end_point = (int(max_hand[1][0] * frame_width), int(max_hand[1][1] * frame_height))
        cv2.line(img, start_point, end_point, (0, 255, 0), 2)

        # Display the remapped distance and normalized angle
        cv2.putText(img, f'Distance: {remapped_distance:.2f}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(img, f'Normalized Angle: {max_normalized_angle:.2f}', (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Hand Tracking", img)

    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()
