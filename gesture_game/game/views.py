from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2 as cv
import mediapipe as mp
import threading
import random

# Initialize MediaPipe Hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def getHandMove(hand_landmarks):
    landmarks = hand_landmarks.landmark
    # Check for "rock"
    if all([landmarks[i].y < landmarks[i+3].y for i in range(9, 20, 4)]):
        return "rock"
    # Check for "scissors"
    elif landmarks[13].y < landmarks[16].y and landmarks[17].y < landmarks[20].y:
        return "scissors"
    # Default to "paper"
    else:
        return "paper"

class VideoCamera(object):
    def __init__(self):
        self.video = cv.VideoCapture(0)
        self.clock = 0
        self.p1_move = self.p2_move = None
        self.gameText = ""
        self.success = True
        self.hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

    def get_frame(self):
        frame = self.frame
        if not self.grabbed or frame is None:
            return None

        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = self.hands.process(frame)
        frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame,
                                          hand_landmarks,
                                          mp_hands.HAND_CONNECTIONS,
                                          mp_drawing_styles.get_default_hand_landmarks_style(),
                                          mp_drawing_styles.get_default_hand_connections_style())

        frame = cv.flip(frame, 1)
        height, width, _ = frame.shape

        if 0 <= self.clock < 20:
            self.success = True
            self.gameText = "Ready?"
        elif self.clock < 30:
            self.gameText = "3..."
        elif self.clock < 40:
            self.gameText = "2..."
        elif self.clock < 50:
            self.gameText = "1..."
        elif self.clock < 60:
            self.gameText = "GO!..."
        elif self.clock == 60:
            hls = results.multi_hand_landmarks
            if hls and len(hls) == 2:
                self.p1_move = getHandMove(hls[0])
                self.p2_move = getHandMove(hls[1])
            else:
                self.success = False
        elif self.clock < 100:
            if self.success:
                self.gameText = f'''Player 1 played {self.p1_move}. Player 2 played {self.p2_move}.'''
                if self.p1_move == self.p2_move:
                    self.gameText += " Game is tied."
                elif self.p1_move == "paper" and self.p2_move == "rock":
                    self.gameText += " Player 1 wins."
                elif self.p1_move == "rock" and self.p2_move == "scissors":
                    self.gameText += " Player 1 wins."
                elif self.p1_move == "scissors" and self.p2_move == "paper":
                    self.gameText += " Player 1 wins."
                else:
                    self.gameText += " Player 2 wins!"
            else:
                self.gameText = "Didn't play properly!"

        # Adjust the position and styling of the rectangle and text
        padding = 5
        rectangle_height = int(0.15 * height)
        rectangle_start_point = (0, 0)
        rectangle_end_point = (width, rectangle_height)
        text1_position = (padding, int(0.05 * height))
        text2_position = (padding, int(0.1 * height))

        # Create a semi-transparent background for the text
        overlay = frame.copy()
        cv.rectangle(overlay, rectangle_start_point, rectangle_end_point, (0, 0, 0), -1)
        cv.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        # Display the clock and game text
        cv.putText(frame, f"Clock: {self.clock}", text1_position, cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2,
                   cv.LINE_AA)
        cv.putText(frame, self.gameText, text2_position, cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2, cv.LINE_AA)

        self.clock = (self.clock + 1) % 100

        ret, jpeg = cv.imencode('.jpg', frame)
        return jpeg.tobytes()

class ComputerCamera(object):
    def __init__(self):
        self.video = cv.VideoCapture(0)
        self.clock = 0
        self.player_move = self.computer_move = None
        self.gameText = ""
        self.success = True
        self.hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

    def get_frame(self):
        frame = self.frame
        if not self.grabbed or frame is None:
            return None

        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = self.hands.process(frame)
        frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame,
                                          hand_landmarks,
                                          mp_hands.HAND_CONNECTIONS,
                                          mp_drawing_styles.get_default_hand_landmarks_style(),
                                          mp_drawing_styles.get_default_hand_connections_style())

        frame = cv.flip(frame, 1)
        height, width, _ = frame.shape

        if 0 <= self.clock < 20:
            self.success = True
            self.gameText = "Ready?"
        elif self.clock < 30:
            self.gameText = "3..."
        elif self.clock < 40:
            self.gameText = "2..."
        elif self.clock < 50:
            self.gameText = "1..."
        elif self.clock < 60:
            self.gameText = "GO!..."
        elif self.clock == 60:
            hls = results.multi_hand_landmarks
            if hls and len(hls) == 1:
                self.player_move = getHandMove(hls[0])
                self.computer_move = random.choice(["rock", "paper", "scissors"])
            else:
                self.success = False
        elif self.clock < 100:
            if self.success:
                self.gameText = f'''Player played {self.player_move}. Computer played {self.computer_move}.'''
                if self.player_move == self.computer_move:
                    self.gameText += " Game is tied."
                elif self.player_move == "paper" and self.computer_move == "rock":
                    self.gameText += " Player wins."
                elif self.player_move == "rock" and self.computer_move == "scissors":
                    self.gameText += " Player wins."
                elif self.player_move == "scissors" and self.computer_move == "paper":
                    self.gameText += " Player wins."
                else:
                    self.gameText += " Computer wins!"
            else:
                self.gameText = "Didn't play properly!"

        # Adjust the position and styling of the rectangle and text
        padding = 5
        rectangle_height = int(0.15 * height)
        rectangle_start_point = (0, 0)
        rectangle_end_point = (width, rectangle_height)
        text1_position = (padding, int(0.05 * height))
        text2_position = (padding, int(0.1 * height))

        # Create a semi-transparent background for the text
        overlay = frame.copy()
        cv.rectangle(overlay, rectangle_start_point, rectangle_end_point, (0, 0, 0), -1)
        cv.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        # Display the clock and game text
        cv.putText(frame, f"Clock: {self.clock}", text1_position, cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2,
                   cv.LINE_AA)
        cv.putText(frame, self.gameText, text2_position, cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2, cv.LINE_AA)

        self.clock = (self.clock + 1) % 100

        ret, jpeg = cv.imencode('.jpg', frame)
        return jpeg.tobytes()

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def index(request):
    return render(request, 'game/index.html')

def friend_game(request):
    return render(request, 'game/play.html', {'mode': 'friend'})

def computer_game(request):
    return render(request, 'game/play.html', {'mode': 'computer'})

def video_feed_friend(request):
    return StreamingHttpResponse(gen(VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def video_feed_computer(request):
    return StreamingHttpResponse(gen(ComputerCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def select_opponent(request):
    return render(request, 'game/buttons.html')

def about(request):
    return render(request, 'game/about.html')
