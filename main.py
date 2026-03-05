import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import time
import math

# loads the trained ML model file (TensorFlow Lite) and contains network to detect hands
# pass in and configure model to detect up to 2 hands
hand_model = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=hand_model,
    num_hands=1
)
detector = vision.HandLandmarker.create_from_options(options)

# mapping hand coordinates for screen control
    # ex. Example: If your camera sees your hand at the far right, 
    # you want your mouse to go to the far right of the screen.
screen_w, screen_h = pyautogui.size()
print(f"\n hand mouse control .")

# store previos cursor position to allow smooth movement
prev_screen_x, prev_screen_y = 0, 0

# gesture time control
click_start_time = None
click_times = []
click_cooldown = 0.5
scroll_mode = False
freeze_cursor = False
scroll_time = 0

# message display time
status_text = ""
status_time = 0

camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("can't open camera")
    exit()

while True:
    now = time.time()
    success, frame = camera.read()
    if not success:
        print("can't recieve frame")
        break
    camera_frame = cv2.flip(frame, 1)

    # convert color format | cv: BGR - mp: RGB
    # prepare image for the mp model and run the model on that specific image and pass it in to result
    rgb_frame = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image (
        image_format = mp.ImageFormat.SRGB,
        data = rgb_frame
    )
    result = detector.detect(mp_image)

    if result.hand_landmarks:
        # get image dimensions
        h, w, _ = camera_frame.shape

        for hand_landmarks in result.hand_landmarks:
            for landmark in hand_landmarks:
                # convert coordinates to pixel coordinates
                px = int(landmark.x * w)
                py = int(landmark.y * h)

                # draws dot at each landmaerk
                # image, (x,y), radius, color, thickness
                cv2.circle(camera_frame, (px, py), 5, (0, 255, 0), -1)
                # print(landmark.x, landmark.y)

            # =========set finger tip landmarks=================
            thumb_tip = hand_landmarks[4]
            index_tip = hand_landmarks[8]
            middle_tip = hand_landmarks[12]
            ring_tip = hand_landmarks[16]
            pinky_tip = hand_landmarks[20]
            # ==================================================

                # list comprehension that outputs 1s (finger up) and 0s (finger down)
                #   tip -> is the fingertip landmark
                #   tip - 2 -> the landmark two joints below the tip (near knuckle)
                #       hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y 
                #           -> if the tip is above the knuckle, the finger is considered "up"
            gesture_determination = [
                1 if hand_landmarks[tip].y < hand_landmarks[tip - 2].y else 0
                for tip in [8,12,16,20]
            ]

            # distance between thumb and index
            distance = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)

            if distance < 0.06:
                if not freeze_cursor:
                    freeze_cursor = True
                    click_times.append(now)

                    if len(click_times) > 2:
                        click_times.pop(0)

                    # double click check
                    if len(click_times) >= 2 and click_times[-1] - click_times[-2] < 0.7:
                        pyautogui.doubleClick()
                        status_text = "double click"
                        status_time = now
                        click_times = []
                    else:
                        pyautogui.click()
                        status_text = "single click"
                        status_time = now
            else:
                freeze_cursor = False  

            # move cursor with index_finger
            smooth = 0.2
            if not freeze_cursor:
                # calculate screen pixel location
                #   ex. screen_x = 0.5 * 1920 = 960
                screen_x = int(index_tip.x * screen_w)
                screen_y = int(index_tip.y * screen_h)

                # linear interpolation (LERP)
                #   this is the process of a CURRENT target *gradually* reaching its
                #   next destination | ex. 500 + (500 * 0.2) -> 500 + 100 = 600
                #                                                         -> 600 - 680
                #                                                         -> 680 -> 744
                screen_x = int(prev_screen_x + (screen_x - prev_screen_x) * smooth)
                screen_y = int(prev_screen_y + (screen_y - prev_screen_y) * smooth)

                pyautogui.moveTo(screen_x, screen_y)
                prev_screen_x, prev_screen_y = screen_x, screen_y

            # scrolling mode
            if sum(gesture_determination) == 4:
                scroll_mode = True
            else:
                scroll_mode = False

            # scroll actions
            if scroll_mode and now - scroll_time > 0.2:
                if index_tip.y < 0.4:
                    pyautogui.scroll(60)
                    status_text = "scrolling up"
                    status_time = now
                    scroll_time = now
                elif index_tip.y > 0.6:
                    pyautogui.scroll(-60)
                    status_text = "scrolling down"
                    status_time = now
                    scroll_time = now

    # display single|double|scrolling_up|scrolling_down click based on hand genstures
    if now - status_time < 1:
            cv2.putText(camera_frame, status_text, (10,50),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

    cv2.imshow("live video", camera_frame)
    if(cv2.waitKey(1)==ord('q')):
        break
camera.release()
cv2.destroyAllWindows()

