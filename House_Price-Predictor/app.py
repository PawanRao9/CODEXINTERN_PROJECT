import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

# Load dataset from URL (Mumbai House Prices)
url = "https://raw.githubusercontent.com/rupeshraundal/mumbai-house-prices/main/Mumbai1.csv"
data = pd.read_csv(url)

# Data Cleaning and Preparation
# Select relevant columns and rename for consistency
data = data[['area', 'Bedroom', 'bathroom', 'locality', 'parking', 'status', 'transaction', 'type', 'price']]
data = data.rename(columns={'Bedroom': 'bedrooms'})

# Remove rows with missing values
data = data.dropna()

# Convert area to float (handle comma separator)
data['area'] = data['area'].astype(str).str.replace(',', '').astype(float)

# Display dataset information
print("Dataset Shape:", data.shape)
print("\nFirst 5 Rows:")
print(data.head())
print("\nMissing Values:")
print(data.isnull().sum())

# Visualize distributions
plt.figure(figsize=(12, 8))
sns.histplot(data['price'], kde=True)
plt.title('House Price Distribution (Mumbai)')
plt.show()

# Prepare data for modeling
X = data.drop('price', axis=1)
y = data['price']

# Split data into train/test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Preprocessing pipeline
categorical_features = ['locality', 'status', 'transaction', 'type']
numerical_features = ['area', 'bedrooms', 'bathroom', 'parking']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# Create pipeline with preprocessing and model
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression())
])

# Train model
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("\nModel Performance:")
print(f"RMSE: {rmse:.2f}")
print(f"R² Score: {r2:.4f}")

# Visualize predictions vs actual
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
plt.xlabel('Actual Prices (₹)')
plt.ylabel('Predicted Prices (₹)')
plt.title('Actual vs Predicted House Prices (Mumbai)')
plt.show()

# Function to get user input and make prediction
def predict_house_price():
    print("\nEnter House Details for Price Prediction:")
    
    area = float(input("Area (sq. ft): "))
    bedrooms = int(input("Number of Bedrooms: "))
    bathroom = int(input("Number of Bathrooms: "))
    parking = int(input("Parking Spaces: "))
    locality = input("Locality: ")
    status = input("Status (Ready to Move/Under Construction): ")
    transaction = input("Transaction (New property/Resale): ")
    type_ = input("Type (Apartment/Builder_floor): ")
    
    input_data = pd.DataFrame({
        'area': [area],
        'bedrooms': [bedrooms],
        'bathroom': [bathroom],
        'parking': [parking],
        'locality': [locality],
        'status': [status],
        'transaction': [transaction],
        'type': [type_]
    })
    
    predicted_price = model.predict(input_data)[0]
    print(f"\nPredicted House Price: ₹{predicted_price:,.2f}")

# Run prediction function
predict_house_price()