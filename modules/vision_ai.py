import cv2
import mediapipe as mp
import numpy as np
import tempfile

def calcola_angolo(a, b, c):
    """Calcola l'angolo tra tre punti (x,y)"""
    a = np.array(a); b = np.array(b); c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0: angle = 360 - angle
    return angle

def processa_video(video_path):
    # Inizializza MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    cap = cv2.VideoCapture(video_path)
    
    # Parametri video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Output Video
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    out = cv2.VideoWriter(tfile.name, cv2.VideoWriter_fourcc(*'avc1'), fps, (width, height))
    
    # Liste per statistiche
    angoli_ginocchio = []
    angoli_anca = []
    angoli_gomito = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        # Conversione colore per AI
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        
        # Riconversione per disegno
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            
            # --- ESTRAZIONE PUNTI CHIAVE (LATO SINISTRO STANDARD) ---
            # 11=Spalla, 13=Gomito, 15=Polso
            # 23=Anca, 25=Ginocchio, 27=Caviglia
            
            shoulder = [lm[11].x * width, lm[11].y * height]
            elbow = [lm[13].x * width, lm[13].y * height]
            wrist = [lm[15].x * width, lm[15].y * height]
            hip = [lm[23].x * width, lm[23].y * height]
            knee = [lm[25].x * width, lm[25].y * height]
            ankle = [lm[27].x * width, lm[27].y * height]
            
            # --- CALCOLO ANGOLI BIOMECCANICI ---
            # 1. Ginocchio (Estensione)
            knee_angle = calcola_angolo(hip, knee, ankle)
            angoli_ginocchio.append(knee_angle)
            
            # 2. Anca (Busto - Flessione Anca)
            hip_angle = calcola_angolo(shoulder, hip, knee)
            angoli_anca.append(hip_angle)
            
            # 3. Gomito (Reach/Piega)
            elbow_angle = calcola_angolo(shoulder, elbow, wrist)
            angoli_gomito.append(elbow_angle)
            
            # --- DISEGNO SUL VIDEO (HUD) ---
            
            # Disegna tutto lo scheletro
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            
            # Stampa valori a schermo (HUD)
            # Ginocchio
            cv2.putText(image, f"KNEE: {int(knee_angle)}", tuple(np.multiply(knee, [1,1]).astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            # Anca
            cv2.putText(image, f"HIP: {int(hip_angle)}", tuple(np.multiply(hip, [1,1]).astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
            # Gomito
            cv2.putText(image, f"ARM: {int(elbow_angle)}", tuple(np.multiply(elbow, [1,1]).astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
            
        out.write(image)
        
    cap.release()
    out.release()
    
    # Calcolo medie e picchi
    dati_completi = {
        'max_knee': max(angoli_ginocchio) if angoli_ginocchio else 0,
        'min_knee': min(angoli_ginocchio) if angoli_ginocchio else 0,
        'avg_hip': np.mean(angoli_anca) if angoli_anca else 0,
        'avg_arm': np.mean(angoli_gomito) if angoli_gomito else 0
    }
    
    return tfile.name, dati_completi
