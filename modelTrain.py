# Import relevant libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
import pickle

# Load dataset
df = pd.read_csv('input.csv')
# Check for missing values
# Drop duplicate rows
df = df.drop_duplicates(keep='first')
df = df.drop('Unnamed: 4', axis=1)
X = df[['Aspect ratio ', 'Clearance ratio ', 'ø (angle in theta)']]
y = df['Drag Coeff. (Out put)']
# Split the data into training and testing sets (70% training, 30% testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=10)
model = DecisionTreeRegressor(max_depth=6, min_samples_leaf=2)
model.fit(X_train, y_train)

pickle.dump(model, open('model.pkl','wb'))


