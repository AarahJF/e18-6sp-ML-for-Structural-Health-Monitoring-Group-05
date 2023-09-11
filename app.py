import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import os
import subprocess

# Initialize the flask App
app = Flask(__name__)

# Function to check if the model.pkl file exists
def check_model_file():
    return os.path.isfile('model.pkl')

# Load the model if it exists, otherwise, call modelTrain.py to generate it
if check_model_file():
    model = pickle.load(open('model.pkl', 'rb'))
else:
    # Run modelTrain.py as a subprocess and wait for it to complete
    subprocess.run(["python", "modelTrain.py"], check=True)
    
    # Check if the model.pkl file exists after the subprocess completes
    if check_model_file():
        model = pickle.load(open('model.pkl', 'rb'))
    else:
        print("Error generating the model.pkl")

# Default page of our web-app
@app.route('/')
def home():
    return render_template('index.html')

# To use the predict button in our web-app
@app.route('/predict', methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    int_features = [float(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)

    output = round(prediction[0], 2)

    return render_template('index.html', prediction_text='Drag Coefficient of billboard is :{}'.format(output))

if __name__ == "__main__":
    app.run(debug=True)
