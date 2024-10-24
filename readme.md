# Hand Tracking OSC Controller

This project uses computer vision to track hand movements and send the data via OSC (Open Sound Control).

## Requirements

- Python 3.7 or higher
- Webcam

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/hand-tracking-osc.git
   cd hand-tracking-osc
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Make sure your webcam is connected and working.

2. Open the `oschandcontrol.py` file and modify the following line to set your desired IP address and port:
   ```python
   osc_client = udp_client.SimpleUDPClient("127.0.0.1", 4567)
   ```
   Replace "127.0.0.1" with your target IP address (use "127.0.0.1" for localhost) and 4567 with your desired port number.

3. Run the script:
   ```
   python oschandcontrol.py
   ```

4. A window titled "Camera Selection" will open.

5. Select your desired camera from the dropdown menu.

6. Click the "Start" button to begin hand tracking.

7. A new window showing the webcam feed with hand tracking overlay will open.

8. To switch cameras, select a different camera from the dropdown and click "Start" again.

9. Press 'Esc' in the hand tracking window to stop the current tracking session.

## OSC Messages

The script sends four OSC messages:

- `/hand/distance1`: A float value between 0 and 1 representing how open the hand is (thumb to index finger).
- `/hand/rotation1`: A float value between 0 and 1 representing the angle of the hand (thumb to index finger).
- `/hand/distance2`: A float value between 0 and 1 representing how open the hand is (thumb to pinky finger).
- `/hand/rotation2`: A float value between 0 and 1 representing the angle of the hand (thumb to pinky finger).

## Troubleshooting

- The script can be temperamental depending on the video device. If you encounter issues, don't be afraid to restart the entire script.
- If a camera doesn't work, try selecting a different one from the dropdown menu.
- Make sure you have the necessary permissions to access your webcam.
- If the hand tracking window doesn't appear, check if it's hidden behind other windows.
- Ensure proper lighting conditions for better hand detection.

## Note on Video Devices

The behavior of video devices can vary depending on your system and the specific cameras you're using. If you experience any issues:

1. Try restarting the script.
2. Experiment with different cameras if you have multiple options.
3. Ensure no other applications are currently using the camera you're trying to access.
4. If problems persist, try rebooting your computer to reset all camera connections.

Remember, patience may be required when working with video inputs, as they can sometimes be finicky.