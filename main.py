
import cv2
import time
import threading
from flask import Response, Flask

global video_frame
video_frame = None

# Usamos thread-safe para ver en varios buscadores
global thread_lock 
thread_lock = threading.Lock()

# Objeto Flask
app = Flask(__name__)

def captureFrames():
    global video_frame, thread_lock

    video_capture = cv2.VideoCapture(0, cv2.CAP_GSTREAMER)

    while True and video_capture.isOpened():
        return_key, frame = video_capture.read()
        if not return_key:
            break

        with thread_lock:
            video_frame = frame.copy()
        
        key = cv2.waitKey(30) & 0xff
        if key == 27:
            break

    video_capture.release()
        
def encodeFrame():
    global thread_lock
    while True:

        with thread_lock:
            global video_frame
            if video_frame is None:
                continue
            return_key, encoded_image = cv2.imencode(".jpg", video_frame)
            if not return_key:
                continue

        # Onvertimos la imagen en bytes
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encoded_image) + b'\r\n')

@app.route("/")
def streamFrames():
    return Response(encodeFrame(), mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':

    # Creación del hilo 
    process_thread = threading.Thread(target=captureFrames)
    process_thread.daemon = True

    # Iniciamos el hilo
    process_thread.start()

    # Iniciamos la API con la IP de la tarjeta 
    app.run(host='10.42.0.1')
