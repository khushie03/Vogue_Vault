import pandas as pd
import random
from transformers import pipeline
import os

def define_cloth_category(description):
    if pd.isna(description):
        return None

    keywords = ["heels", "dress", "scarf", "pants", "skirt", "shirt", "jacket",
                "sari", "shorts", "purse", "kurti", "vest", "hoodie", "sneakers",
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

def captioner(img_path):
    captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
    text_caption = captioner(img_path)
    text = text_caption[0]["generated_text"]
    return text

price_values = [random.randint(500, 5000) for _ in range(1000)]

image_directory = "Images/Images"

# Ensure the CSV file is created with headers
with open('price_1.csv', 'w') as f:
    f.write('id,price,description,category\n')

# Process and save data row by row
for id_val in range(1, 10019):  # Ensure to cover IDs 1 to 10018
    img_path = os.path.join(image_directory, f"{id_val}.jpg")
    if os.path.exists(img_path):
        description = captioner(img_path)
        category = define_cloth_category(description)
    else:
        description = None
        category = None

    # Append data row to the CSV file
    with open('price_1.csv', 'a') as f:
        f.write(f'{id_val},{price_values[id_val-1] if id_val <= len(price_values) else random.randint(500, 5000)},{description},{category}\n')
