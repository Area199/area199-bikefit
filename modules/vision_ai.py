import cv2
import mediapipe as mp
import numpy as np
import tempfile

def calcola_angolo(a, b, c):
    a = np.array(a); b = np.array(b); c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0: angle = 360 - angle
    return angle

def processa_video(video_path):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(video_path)
    
    # Setup video output
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    # Usa avc1 (H.264) che è compatibile con tutti i browser
    out = cv2.VideoWriter(tfile.name, cv2.VideoWriter_fourcc(*'avc1'), fps, (width, height))
    
    dati_angoli = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            # 23=Anca, 25=Ginocchio, 27=Caviglia
            hip = [lm[23].x * width, lm[23].y * height]
            knee = [lm[25].x * width, lm[25].y * height]
            ankle = [lm[27].x * width, lm[27].y * height]
            
            angolo = calcola_angolo(hip, knee, ankle)
            dati_angoli.append(angolo)
            
            # Disegna l'angolo
            cv2.putText(image, str(int(angolo)), tuple(np.multiply(knee,[1,1]).astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
        out.write(image)
        
    cap.release(); out.release()
    return tfile.name, (max(dati_angoli) if dati_angoli else 0), (min(dati_angoli) if dati_angoli else 0)
