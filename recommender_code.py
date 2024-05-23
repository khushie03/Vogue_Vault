from flask import Flask, render_template, request
import os
import cv2
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.applications.resnet50 import preprocess_input

app = Flask(__name__)

def extract_features(image_path, model):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.expand_dims(img, axis=0)  
    img = preprocess_input(img)  
    features = model.predict(img)
    return features.flatten() 

@app.route('/')
def upload_page():
    return render_template('image_context.html')

@app.route('/image_similarity', methods=['POST'])
def image_similarity():
    folder_path = "static/Images/"
    image_files = os.listdir(folder_path)[:30]  
    model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False, pooling='avg')
    folder_features = {}
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        features = extract_features(image_path, model)
        folder_features[image_file] = features
    provided_image_file = request.files['image']
    provided_image_file.save('provided_image.jpg')
    provided_image_path = 'provided_image.jpg'
    provided_image_features = extract_features(provided_image_path, model)
    similarities = []
    for image_file, features in folder_features.items():
        similarity = cosine_similarity([provided_image_features], [features])[0][0]
        similarities.append({"id": image_file, "similarity_score": similarity})
    similar_images = sorted(similarities, key=lambda x: x['similarity_score'], reverse=True)[:10]

    products_df = pd.read_csv('price.csv')
    product_info = {}
    for index, row in products_df.iterrows():
        product_info[row['id']] = {"description": row['description'], "price": row['price']}

    for image in similar_images:
        image_id = image['id']
        if image_id in product_info:
            image['description'] = product_info[image_id]['description']
            image['price'] = product_info[image_id]['price']
    
    return render_template('image_similarity.html', similar_images=similar_images)

if __name__ == '__main__':
    app.run(debug=True)
