import numpy as np
import os
import cv2
import rasterio
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Set directories for dataset
data_dir = 'path/to/training/images'
categories = ['urban', 'forest', 'water']  # Define your categories

# Parameters
img_size = 128  # Image size (128x128)
batch_size = 32
epochs = 20

# Load and preprocess data
def load_data(data_dir, categories, img_size):
    data = []
    for category in categories:
        path = os.path.join(data_dir, category)
        class_num = categories.index(category)
        for img in os.listdir(path):
            try:
                img_array = cv2.imread(os.path.join(path, img))
                resized_array = cv2.resize(img_array, (img_size, img_size))
                data.append([resized_array, class_num])
            except Exception as e:
                print(f"Error loading image {img}: {e}")
    return data

data = load_data(data_dir, categories, img_size)
print(f"Loaded {len(data)} images.")

# Split data into features and labels
X, y = zip(*data)
X = np.array(X).reshape(-1, img_size, img_size, 3) / 255.0
y = np.array(y)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Data augmentation
datagen = ImageDataGenerator(
    rotation_range=20,
    zoom_range=0.15,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.15,
    horizontal_flip=True,
    fill_mode="nearest"
)

# Build the CNN model
def build_model(input_shape, num_classes):
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

model = build_model((img_size, img_size, 3), len(categories))
model.summary()

# Train the model
history = model.fit(datagen.flow(X_train, y_train, batch_size=batch_size),
                    epochs=epochs,
                    validation_data=(X_test, y_test))

# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test accuracy: {accuracy * 100:.2f}%")

# Load GeoTIFF data
def load_geotiff(file_path):
    with rasterio.open(file_path) as src:
        return [src.read(i) for i in range(1, 6)]  # Read all bands

# Calculate vegetation indices
def calculate_indices(red, blue, nir, swir):
    ndvi = (nir - red) / (nir + red)
    ndmi = (nir - swir) / (nir + swir)
    msavi = (2 * nir + 1 - np.sqrt((2 * nir + 1) ** 2 - 8 * (nir - red))) / 2
    ndre = (nir - blue) / (nir + blue)
    return ndvi, ndmi, msavi, ndre

# Create dataset from indices
def create_dataset(red, green, nir, swir):
    ndvi, ndmi, ndre, msavi = calculate_indices(red, green, nir, swir)
    data = {
        'NDVI': ndvi.flatten(),
        'NDMI': ndmi.flatten(),
        'NDRE': ndre.flatten(),
        'MSAVI': msavi.flatten()
    }
    return pd.DataFrame(data)

# Train Random Forest model
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    return model

# Analyze indices for recommendations
def analyze_indices(ndvi, ndmi, msavi, ndre):
    recommendations = {
        'Crop Health': 'Healthy' if np.mean(ndvi) > 0.6 else 'Moderate' if np.mean(ndvi) > 0.3 else 'Poor',
        'Moisture Content': 'Adequate' if np.mean(ndmi) > 0.2 else 'Low',
        'Crop Stage': 'Mature' if np.mean(msavi) > 0.5 else 'Young',
        'Vegetation Cover': 'High' if np.mean(ndvi) > 0.4 else 'Low',
        'Irrigation': 'Required' if np.mean(ndmi) <= 0.2 else 'Not Required'
    }
    return recommendations

# Generate PDF report
def generate_pdf(recommendations, filename='agricultural_analysis.pdf'):
    with PdfPages(filename) as pdf:
        plt.figure(figsize=(8, 6))
        plt.title('Agricultural Analysis Recommendations')
        plt.axis('off')
        for i, (key, value) in enumerate(recommendations.items()):
            plt.text(0.1, 1 - 0.1 * i, f'{key}: {value}', fontsize=12)
        pdf.savefig()
        plt.close()

# Main function to analyze image
def main(image_path, labels):
    red, green, blue, nir, swir = load_geotiff(image_path)
    dataset = create_dataset(red, green, nir, swir)
    model = train_model(dataset, labels)  # Assuming labels are defined
    recommendations = analyze_indices(*calculate_indices(red, blue, nir, swir))
    generate_pdf(recommendations)

# Example usage
# main('path_to_your_satellite_image.tif', labels)
main('/path/to/image', 'Test')

# Plot training & validation accuracy values
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train')
plt.plot(history.history['val_accuracy'], label='Test')
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(loc='upper left')

# Plot training & validation loss values
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train')
plt.plot(history.history['val_loss'], label='Test')
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(loc='upper left')
plt.show()