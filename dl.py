import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array

def predict_image(model, img_path, img_height=128, img_width=128):

    img = load_img(img_path, target_size=(img_height, img_width))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)[0][0]

    label = 'normal' if prediction >= 0.5 else 'collapsed'
    confidence = prediction if label == 'normal' else 1 - prediction

    print(f"Prediction: {label} ({confidence:.2f})")
    return label

    
# best_model = tf.keras.models.load_model('./best_model.h5')
# predict_image(best_model, "./image/col.png")
# predict_image(best_model, "./image/no.png")