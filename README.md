# Vogue_Vault

Vogue_Vault is a comprehensive platform providing a wholesome experience to users through three key components: Chatbot, Virtual Try-on, and Style Preferences. Each component is designed to enhance user interaction and satisfaction by leveraging advanced technologies.

## Features

### 1. Chatbot
- **Overview**: The chatbot is built on Dialogflow, allowing seamless conversation and interaction.
- **Integration**: Integrated with Telegram to ensure user data security by not sharing sensitive information.
- **Capabilities**: Users can interact with the chatbot for various services, such as placing orders, tracking orders, and getting recommendations.

### 2. Virtual Try-on
- **Overview**: A feature that allows users to virtually try on clothes.
- **Technology**: Utilizes advanced image processing and augmented reality techniques to provide a realistic try-on experience.
- **User Experience**: Users can see how different clothes look on them without physically trying them on, enhancing online shopping convenience.

### 3. Style Preferences
- **Overview**: Users can search for similar products by providing input in the form of text or images.
- **Text-Based Search**: Users can describe what they are looking for, and the system will recommend products based on text descriptions.
- **Image-Based Search**: Users can upload an image to find products that are visually similar to the uploaded image.
- **Dataset**: The image dataset used is sourced from Kaggle, ensuring a diverse and comprehensive collection of fashion items.

## Technologies Used
- **Flask**: Web framework for building the application.
- **SQLAlchemy**: ORM for database management.
- **Pandas**: Data manipulation and analysis.
- **TensorFlow**: Image feature extraction using pre-trained models.
- **TF-IDF Vectorizer**: For text-based product recommendations.
- **OpenCV**: Image preprocessing.
- **Scikit-Learn**: Cosine similarity calculations.


## Setup and Installation

### Prerequisites
- Python 3.6+
- Virtual environment (optional but recommended)

### Installation Steps
1. **Clone the repository**:
    ```sh
    git clone https://github.com/khushie03/Vogue_Vault
    cd Vogue_Vault
    ```

2. **Create a virtual environment** (optional but recommended):
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up the database**:
    ```sh
    flask shell
    >>> from app import db
    >>> db.create_all()
    >>> exit()
    ```

5. **Run the application**:
    ```sh
    flask run
    ```
    The application will be accessible at `http://127.0.0.1:5000/`.

## Usage
### User Registration
Navigate to `http://127.0.0.1:5000/sign_up.html` and fill out the registration form.

### Text-Based Product Recommendation
Navigate to `http://127.0.0.1:5000/recommender.html`, input a description, and get product recommendations based on the entered text.

### Image Similarity Search
Navigate to `http://127.0.0.1:5000/image_context.html`, upload an image, and find similar images from the predefined set.

## API Endpoints
- `GET /`: Renders the home page.
- `GET /sign_up.html`: Renders the sign-up page.
- `GET /recommender.html`: Renders the text-based recommender page.
- `GET /image_context.html`: Renders the image similarity search page.
- `POST /register`: Handles user registration.
- `POST /context_text`: Handles text-based product recommendation requests.
- `POST /image_similarity`: Handles image similarity search requests.
- `POST /`: Handles various order-related requests via intent detection.

## Helper Functions
- **extract_features(image_path, model)**: Extracts features from an image using the given model.
- **define_cloth_category(description)**: Defines the cloth category based on the given description.
- **add_to_order(parameters, session_id)**: Adds items to the current order.
- **remove_from_order(parameters, session_id)**: Removes items from the current order.
- **complete_order(parameters, session_id)**: Completes the current order.
- **track_order(parameters, session_id)**: Tracks the status of an order.
- **save_to_db(order)**: Saves the current order to the database.

## Database Models
- **Todo**: Model for a simple to-do item.
- **User**: Model for user details.

