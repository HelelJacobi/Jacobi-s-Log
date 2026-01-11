import rasterio
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def load_geotiff(file_path):
    with rasterio.open(file_path) as src:
        red = src.read(3)
        green = src.read(2)
        blue = src.read(1)
        nir = src.read(4)
        swir = src.read(5)
    return red, green, nir, swir

def calculate_indices(image):
    red = image.read(3)
    green = image.read(2)
    blue = image.read(1)
    nir = image.read(4)
    swir = image.read(5)

    ndvi = (nir - red) / (nir + red)
    ndmi = (nir - swir) / (nir + swir)
    msavi = (2 * nir + 1 - np.sqrt((2 * nir + 1) ** 2 - 8 * (nir - red))) / 2
    ndre = (nir - blue) / (nir + blue)

    return ndvi, ndmi, msavi, ndre

def create_dataset(red, green, nir, swir):
    ndvi, ndmi, ndre, msavi = calculate_indices(red, nir, swir, green)
    data = {
        'NDVI': ndvi.flatten(),
        'NDMI': ndmi.flatten(),
        'NDRE': ndre.flatten(),
        'MSAVI': msavi.flatten()
    }
    return pd.DataFrame(data)

def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    return model

# def main(file_path, labels):
#     red, green, nir, swir = load_geotiff(file_path)
#     dataset = create_dataset(red, green, nir, swir)
#     model = train_model(dataset, labels)
#     return model

def analyze_indices(ndvi, ndmi, msavi, ndre):
    recommendations = {}
    
    # Crop health
    if np.mean(ndvi) > 0.6:
        recommendations['Crop Health'] = 'Healthy'
    elif np.mean(ndvi) > 0.3:
        recommendations['Crop Health'] = 'Moderate'
    else:
        recommendations['Crop Health'] = 'Poor'
    
    # Moisture content
    if np.mean(ndmi) > 0.2:
        recommendations['Moisture Content'] = 'Adequate'
    else:
        recommendations['Moisture Content'] = 'Low'
    
    # Crop stage
    if np.mean(msavi) > 0.5:
        recommendations['Crop Stage'] = 'Mature'
    else:
        recommendations['Crop Stage'] = 'Young'
    
    # Vegetation cover
    recommendations['Vegetation Cover'] = 'High' if np.mean(ndvi) > 0.4 else 'Low'
    
    # Irrigation
    recommendations['Irrigation'] = 'Required' if recommendations['Moisture Content'] == 'Low' else 'Not Required'
    
    return recommendations

def generate_pdf(recommendations, filename='agricultural_analysis.pdf'):
    with PdfPages(filename) as pdf:
        plt.figure(figsize=(8, 6))
        plt.title('Agricultural Analysis Recommendations')
        plt.axis('off')
        for key, value in recommendations.items():
            plt.text(0.1, 1 - 0.1 * list(recommendations.keys()).index(key), f'{key}: {value}', fontsize=12)
        pdf.savefig()
        plt.close()

def main(image_path):
    with rasterio.open(image_path) as image:
        ndvi, ndmi, msavi, ndre = calculate_indices(image)
        recommendations = analyze_indices(ndvi, ndmi, msavi, ndre)
        generate_pdf(recommendations)

# Example usage
# main('path_to_your_satellite_image.tif')
main('C:/Users/jacob/Documents/GitHub/Jacob-s-Log/test.tif')
