import cv2
import numpy as np
import tensorflow as tf

model = tf.keras.models.load_model('model.h5')

def predict(frame):
    frame = cv2.resize(frame, (50, 50))
    frame = np.array(frame)
    frame = frame.reshape((1, 50, 50, 1))
    frame = frame.astype('float32') / 255
    prediction = model.predict(frame)
    
    val = 0
    i = 1
    for n in prediction[0]:
        if n > 0.8:
            val = i
        i = i + 1
    
    return val, prediction
    