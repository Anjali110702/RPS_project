# gesture_game/views.py

import cv2 as cv
import mediapipe as mp
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import random
import string

# Initialize MediaPipe Hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
def index(request): 
    return render(request, 'index.html')

game_sessions = {}
def generate_game_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def player1(request):
    game_id = generate_game_id()
    game_sessions[game_id] = {'p1_ready': False, 'p1_move': None, 'p2_ready': False, 'p2_move': None}
    
    game_url = request.build_absolute_uri('/') + game_id + '/'
    
    return render(request, 'player1.html', {'game_id': game_id, 'game_url': game_url})
def player2(request, game_id):
    if game_id in game_sessions:
        return render(request, 'player2.html', {'game_id': game_id})
    else:
        return render(request, 'index.html')
@csrf_exempt
def start_game(request):
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        if game_id in game_sessions:
            game_sessions[game_id]['p1_ready'] = True
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Game ID not found'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def gesture_capture(request, game_id, player):
    if request.method == 'POST':
        # Initialize video capture
        vid = cv.VideoCapture(0)

        # Initialize MediaPipe Hands
        with mp_hands.Hands(model_complexity=0,
                            min_detection_confidence=0.5,
                            min_tracking_confidence=0.5) as hands:
            while True:
                ret, frame = vid.read()
                if not ret or frame is None: 
                    break
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

                results = hands.process(frame)

                frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(frame,
                                                hand_landmarks,
                                                mp_hands.HAND_CONNECTIONS,
                                                mp_drawing_styles.get_default_hand_landmarks_style(),
                                                mp_drawing_styles.get_default_hand_connections_style())

                frame = cv.flip(frame, 1)
                cv.imshow('frame', frame)

                if cv.waitKey(1) & 0xFF == ord('q'):
                    break

                # Implement gesture recognition logic here
                # Example: getHandMove(hand_landmarks)

                # Store player gesture in game_sessions
                # game_sessions[game_id][f'p{player}_move'] = getHandMove(hand_landmarks)

            vid.release()
            cv.destroyAllWindows()

            return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
