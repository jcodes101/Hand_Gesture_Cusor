# Hand Gesture Cursor

Control your mouse cursor using hand gestures and a webcam. Uses **MediaPipe** for hand tracking and **PyAutoGUI** for mouse control. No physical mouse required—navigate, click, double-click, and scroll with your hand in front of the camera.

---

## Features

- **Cursor movement** — Index finger position maps to screen position with smoothing and velocity prediction
- **Single click** — Thumb and index finger pinch (touch)
- **Double click** — Two quick pinches within ~0.7 seconds
- **Scroll** — All four fingers up: move index up to scroll up, down to scroll down
- **Live overlay** — Skeleton and fingertip landmarks drawn on the camera feed
- **Status feedback** — On-screen text for "single click", "double click", "scrolling up", "scrolling down"

---

## Requirements

- **Python** 3.8+
- **Webcam** (built-in or USB)
- **Windows** (PyAutoGUI is used for mouse control; behavior may differ on macOS/Linux)

### Dependencies

| Library     | Purpose                          |
|------------|-----------------------------------|
| OpenCV     | Webcam capture and frame display  |
| MediaPipe  | Hand landmark detection           |
| PyAutoGUI  | Mouse movement, clicks, scrolling |
| NumPy      | Optional utilities (see `numpy_util.py`) |

---

## Setup

### 1. Clone or download the project

```bash
cd hand_gesture_cursor
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Hand landmarker model

The app loads a MediaPipe hand landmarker model from `hand_landmarker.task` in the project root.

- If the file is **not** in the project folder, download it from the [MediaPipe Hand Landmarker task](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker#models) and place `hand_landmarker.task` in the same directory as `main.py`.

---

## How to Run

```bash
python main.py
```

- A window titled **"jcodes live hand cursor"** will show the camera feed with hand skeleton overlay.
- **Quit:** Press **`q`** in that window to exit.

---

## Gestures

| Gesture              | Action        | How to do it |
|----------------------|---------------|--------------|
| **Move cursor**      | Move mouse    | Move your index finger; cursor follows with smoothing. |
| **Single click**     | Left click    | Pinch thumb and index finger together (distance &lt; ~0.06 in normalized space). |
| **Double click**     | Double click  | Two pinches within ~0.7 seconds. |
| **Scroll up**        | Scroll up     | All four fingers up, index finger in **upper** part of frame. |
| **Scroll down**      | Scroll down   | All four fingers up, index finger in **lower** part of frame. |

---

## Project Structure

```
hand_gesture_cursor/
├── main.py              # Main application: camera, hand detection, cursor control
├── hand_landmarker.task # MediaPipe hand landmarker model (you may need to download)
├── numpy_util.py        # Optional helpers (angles, distances) for gesture logic
├── requirements.txt     # Python dependencies
├── main_notes.md        # Detailed notes on mapping, smoothing, deadzone, gestures
├── project_notes.md     # Library overview and high-level flow
└── README.md            # This file
```

---

## How It Works (High Level)

1. **Capture** — OpenCV reads frames from the webcam (640×480, mirrored).
2. **Detect** — MediaPipe Hand Landmarker finds 21 hand landmarks per frame.
3. **Map** — Index fingertip (landmark 8) is mapped to screen coordinates with an offset and scale so the hand area covers the screen.
4. **Smooth** — Cursor position is smoothed with dynamic alpha (exponential smoothing) and velocity prediction; a small deadzone reduces jitter.
5. **Gestures** — Pinch (thumb–index distance) triggers click/double-click; “all fingers up” enables scroll; index height controls scroll direction.

For a deeper dive into coordinate mapping, smoothing, deadzone, and gesture logic, see **`main_notes.md`**.

---

## Tips

- Use good, even lighting so the hand is clearly visible.
- Keep your hand within the camera frame; the index finger drives the cursor.
- For scroll, show all four fingers (index, middle, ring, pinky) up, then move the index up or down in the frame.

---

## License

Use and modify as you like. MediaPipe and OpenCV have their own licenses; ensure your use complies with them.
