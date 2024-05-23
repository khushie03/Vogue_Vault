from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from recommender_code import image_similarity
import db_helper
import generic_helper
from flask import Flask, render_template, request, jsonify
import os
import cv2

import tensorflow as tf
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.applications.resnet50 import preprocess_input
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)
inprogress_orders = {}

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(2000), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Task %r>" % self.id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    dob = db.Column(db.Date)
    country = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"User('{self.name}', '{self.age}', '{self.country}')"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/sign_up.html')
def sign_up():
    return render_template("sign_up.html")

@app.route('/recommender.html')
def recommender():
    return render_template("recommender.html")

@app.route('/image_context.html')
def image_finder():
    return render_template("image_context.html")


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        dob_str = request.form['dob']
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        country = request.form['country']
        phone_number = request.form['phone_number']
        password = request.form['password']
        new_user = User(name=name, age=age, dob=dob, country=country, phone_number=phone_number, password=password)
        db.session.add(new_user)
        db.session.commit()


        return render_template("recommender.html")

data = pd.read_csv("price.csv")
product_data = data[['id', 'price', 'description', 'category', 'code', 'href']]

tfidf_vectorizer = TfidfVectorizer(stop_words='english')
product_descriptions = product_data['description'].fillna('')
tfidf_matrix = tfidf_vectorizer.fit_transform(product_descriptions)

def define_cloth_category(description):
    if pd.isna(description):
        return None

    keywords = ["heels", "dress", "scarf", "pants", "skirt", "shirt", "jacket","kaftaan","kafta", 
                "pant","suit","sari", "shorts", "purse", "kurti", "vest", "hoodie", "sneakers",
                "jumpsuit", "top", "sweater", "sunglasses", "sling", "shawl",
                "suit", "sash", "leli", "blouse", "tee", "lepa", "kurt", "cardigan",
                "sari", "sandals", "bag", "motifs", "lehen", "shaw", "rom", "pati",
                "stoler", "clutch", "rug", "dupa", "t-shirt", "saree", ""
                "anklet", "bangle", "bodysuit", "boots", "bra", "shoes", "coats", "t shirt",
                "sweater", "sweatshirt", "shirt", "jeans", "kurta", "dupatta", "coats", "coat",
                "scarf", "socks", "jacket", "blouse", "dress", "skirt", "pants", "leggings", "lera", "leaph",
                "gow", "rom", "kimono", "hoodie", ""
                "shorts", "suit", "tie", "gloves", "hat", "cap", "hoodie", "tunic", "tank top",
                "cardigan", "blazer", "vest", "poncho", "kimono", "sari", "jumpsuit", "romper",
                "overalls", "pajamas", "robe", "swimwear", "lingerie", "underwear", "nightwear",
                "sportswear", "activewear", "formalwear", "casualwear", "outerwear", "ethnicwear",
                "westernwear", "workwear", "uniform", "traditional", "vintage", "modern", "contemporary"]

    for keyword in keywords:
        if keyword in description.lower():
            return keyword
    return None


@app.route('/context_text', methods=['POST'])
def recommend_products_handler():
    user_choice = request.form['typed_text']
    text_category = define_cloth_category(user_choice)
    category_products = product_data[product_data['category'] == text_category]
    first_20_products = category_products.head(50)
    product_descriptions = first_20_products['description'].fillna('')
    user_vector = tfidf_vectorizer.transform([user_choice])
    product_vectors = tfidf_vectorizer.transform(product_descriptions)
    similarity_scores = np.dot(user_vector, product_vectors.T).toarray().flatten()
    top_indices = similarity_scores.argsort()[-50:][::-1]
    recommended_products = first_20_products.iloc[top_indices].to_dict(orient='records')
    return render_template('context_text.html', recommended_products=recommended_products)


@app.route("/", methods=['POST'])
def handle_request():
    payload = request.json
    print(payload)  
    intent = payload["queryResult"]["intent"]["displayName"]
    parameters = payload["queryResult"]["parameters"]
    output_contexts = payload["queryResult"]["outputContexts"]

    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])
    intent_handler_dict = {
        "order_add-context:ongoing_order": add_to_order,
        "order_remove - context : ongoing order": remove_from_order,
        "order_complete:context-ongoing order": complete_order,
        "track_order:context-ongoing_order": track_order
    }
    if intent in intent_handler_dict:
        return intent_handler_dict[intent](parameters, session_id)

def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return jsonify(content={
            "fulfillmentText": "I couldn't find your current order. Please start a new order."
        })
    
    items = parameters["id"]
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        fulfillment_text = f'I have removed {",".join(removed_items)} from your order.'

    if len(no_such_items) > 0:
        fulfillment_text = f'I could not find {",".join(no_such_items)} in your current order.'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is now empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Your updated order: {order_str}"

    return jsonify(
         fulfillmentText = fulfillment_text
    )


def add_to_order(parameters: dict , session_id:str):
    product = parameters["item_id"]
    size = parameters["size_chart"]
    product = [item.lstrip('#') for item in product]
    if len(product) != len(size):
        fulfillment_text = "Sorry I am not able to understand what you are trying to convey please write product item and size clearly"
    else:
        new_product_dict = dict(zip(product , size))
        if session_id in inprogress_orders:
            current_product_dict = inprogress_orders[session_id]
            current_product_dict.update(new_product_dict)
            inprogress_orders[session_id] = current_product_dict
        else :
            inprogress_orders[session_id] = new_product_dict
        print("@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(inprogress_orders)
        order_str = generic_helper.get_str_from_product_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far recieved order from your side : {order_str}. Do you need anything else "
    return jsonify(fulfillmentText=fulfillment_text)

def complete_order(parameters:dict, session_id :str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I am having trouble finding the order . Can you please place a new order"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

        if order_id == -1 :
            fulfillment_text = "Sorry I cannot complete your order due to some order in the backend! "
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = f"Awesome your order has been placed "\
            f"here is your {order_id} : "\
            f"Your total amount of the order is {order_total} which you can pay at the delivery"
        del inprogress_orders[session_id]
    return jsonify(fulfillmentText = fulfillment_text)

def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()
    if next_order_id == -1:
        return -1
    
    for id, size in order.items():
        rcode = db_helper.insert_order_item(id, size, next_order_id)
        if rcode == -1:
            return -1

    db_helper.insert_order_tracking(next_order_id, "in_progress")
    return next_order_id

def track_order(parameters: dict , session_id :str):
    order_id = parameters["number"][0] 
    status = db_helper.get_order_status(order_id)

    if status:
        fulfillment_text = f"The order status for the order id: {order_id} is: {status}"
    else:
        fulfillment_text = f"No order found with the order id: {order_id}"

    return jsonify(fulfillmentText=fulfillment_text)

def extract_features(image_path, model):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.expand_dims(img, axis=0)  
    img = preprocess_input(img)  
    features = model.predict(img)
    return features.flatten() 

@app.route('/image_similarity', methods=['POST'])
def image_similarity():
    folder_path = "static/Images"
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
    return render_template('image_similarity.html', similar_images=similar_images)

if __name__ == '__main__':
    app.run(debug=True)
