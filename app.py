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

def calculated_value(input_values):
    AR = input_values[0][0]
    CR = input_values[0][1]
    theta = input_values[0][2]  
    theta_radians = np.deg2rad(theta)

    drag_coefficient = -0.364 - 0.13 * np.log10(AR) - 0.308 * (CR ** 3) + 4.138 * np.cos(theta_radians) - 2.315 * np.cos(theta_radians) * np.cos(theta_radians)
    return drag_coefficient

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

    calculated_coefficient = round(calculated_value(final_features),2)

    output = round(prediction[0], 2)

    return render_template('index.html', prediction_text='Drag Coefficient of billboard is :{} \n Calculated Drag Coefficient is: {}'.format(output,calculated_coefficient))

if __name__ == "__main__":
    app.run(debug=True)
