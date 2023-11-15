import io
import os
import time
from picamera2 import Picamera2
from google.cloud import vision_v1p3beta1 as vision
import RPi.GPIO as GPIO
from PIL import Image
import numpy as np
import json 

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

output_directory = "detected_faces"
os.makedirs(output_directory, exist_ok=True) 

# Configuration for buzzer
BUZZER_PIN = 7  # Buzzer pin number
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

notes = {  # Dict that contains the first scale notes frequencies
    'C': 0.002109, 'D': 0.001879, 'E': 0.001674, 'F': 0.001580, 'G': 0.001408,
    'A': 0.001254, 'B': 0.001117, 'C1': 0.001054,
}

def play_sound(duration, frequency):  # Play different frequencies
    for i in range(duration):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(frequency)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(frequency)

# Configuration for PIR sensor
PIR_PIN = 12
GPIO.setup(PIR_PIN, GPIO.IN)

print("PIR-Sensor activated!")

# Set up Google Cloud Vision API client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/alex10/my_virtual_env/savvy-aileron-404621-c23d34c08331.json"
client = vision.ImageAnnotatorClient()

try:
    while True:
        if GPIO.input(PIR_PIN) == 0:  # No movement
            print("No movements...")
            time.sleep(0.5)
        elif GPIO.input(PIR_PIN) == 1:  # Movement detected
            print("Movements recognized!")

            # Capture image with the camera
            im = picam2.capture_array()
            
            # Convert NumPY array to Pillow Image 
            pil_image = Image.fromarray(im) 
            
            # Convert image to RGB mode
            pil_image = pil_image.convert('RGB')

            # Convert image to bytes
            image_bytes = io.BytesIO()
            pil_image.save(image_bytes, format='JPEG')
            image_bytes = image_bytes.getvalue()

            # Detect faces using Google Cloud Vision API
            image = vision.Image(content=image_bytes)
            response = client.face_detection(image=image)
            faces = response.face_annotations

            if faces:  # Check if faces are detected
                print("Face detected!")
                
                # Print or log the raw JSON API response
                response_json = {
                    "face_annotations": [
                        {
                            "bounding_box": [(vertex.x, vertex.y) for vertex in face.bounding_poly.vertices],
                            "joy_likelihood": face.joy_likelihood,
                            "sorrow_likelihood": face.sorrow_likelihood,
                            "anger_likelihood": face.anger_likelihood,
                            "surprise_likelihood": face.surprise_likelihood,
                        }
                        for face in faces
                    ]
                }
                print("API Response:", json.dumps(response_json, indent=2))

                for i, face in enumerate(faces):
                    bbox = [(vertex.x, vertex.y) for vertex in face.bounding_poly.vertices]
                    x, y, w, h = bbox[0][0], bbox[0][1], bbox[2][0] - bbox[0][0], bbox[2][1] - bbox[0][1]
                    
                    # Extract the region of interest (ROI) containing the face
                    face_region = pil_image.crop((x, y, x + w, y + h))

                    # Save the face region to the output directory
                    timestamp = int(time.time())
                    filename = os.path.join(output_directory, f"face_{i}_{timestamp}.jpg")
                    face_region.save(filename)

                    # Trigger the buzzer when a face is detected
                    for n in ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C1']:
                        play_sound(100, notes[n])

                    # Print relevant face information
                    print(f"Face {i + 1}:")
                    print()

                time.sleep(0.5)  # wait for a short time before checking for motion again

except KeyboardInterrupt:
    GPIO.cleanup()  # Clear GPIO
    picam2.stop()