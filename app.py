import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import os
import subprocess
import mysql.connector

# Initialize the flask App
app = Flask(__name__)

# import mysql.connector
import csv

# Define database configuration
db_config = {
    "host": 'localhost',
    "user": 'root',
    "password": "",
    "database": "6SP",
    'port': 3307, 
}

# Connect to the database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Execute a query to retrieve data (replace with your query)
query = "SELECT AspectRatio, ClearanceRatio, Angle, Predicted FROM datas"
cursor.execute(query)

# Fetch all rows of data
data = cursor.fetchall()

# Close the cursor and connection
cursor.close()
conn.close()

# Specify the CSV file path
csv_file_path = "data.csv"

# Write the data to the CSV file
with open(csv_file_path, "w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # Write the header row if needed
    csv_writer.writerow(["Aspect ratio" ,"Clearance ratio" ,"(angle in theta)","Drag Coeff. (Output)"])
    
    # Write the data rows
    for row in data:
        csv_writer.writerow(row)

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

db_config = {
    "host": 'localhost',
    "user": 'root',
    "password": "",
    "database": "6SP",
    'port': 3307, 
}


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

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        query = "INSERT INTO datas (AspectRatio, ClearanceRatio, Angle, Predicted, Calculated) VALUES (%s, %s, %s, %s, %s)"
        values = (final_features[0][0], final_features[0][1], final_features[0][2], output, calculated_coefficient)
        cursor.execute(query, values)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Error inserting data into MySQL:", str(e))
    finally:
        cursor.close()
        conn.close()

    return render_template('index.html', prediction_text='Drag Coefficient of billboard is :{} \n Calculated Drag Coefficient is: {}'.format(output,calculated_coefficient))

if __name__ == "__main__":
    app.run(debug=True)
