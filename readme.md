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

4. The script will open a window showing the webcam feed with hand tracking overlay.

5. Press 'Esc' to exit the program.

## OSC Messages

The script sends two OSC messages:

- `/hand/distance`: A float value between 0 and 1 representing how open the hand is.
- `/hand/rotation`: A float value between 0 and 1 representing the angle of the hand (0 is horizontal, 1 is vertical).

## Troubleshooting

- If the script can't access your webcam, try changing the camera index in the line `cap = cv2.VideoCapture(4)` to a different number (usually 0 or 1).
- Make sure you have the necessary permissions to access your webcam.

