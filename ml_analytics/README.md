# Satellite Image Classification and Analysis Using CNN and Random Forest

## Introduction

This document provides a comprehensive overview of a Python script designed for satellite image classification and analysis. The code utilizes **_Convolutional Neural Networks (CNN)_** for image classification and **_Random Forest_** for analyzing vegetation indices derived from satellite imagery. The primary goal is to classify images into categories such as urban, forest, and water, while also generating recommendations based on vegetation health and moisture content.

### Key Concepts

- Convolutional Neural Networks (CNN): A deep learning model particularly effective for image classification tasks.
- Random Forest Classifier: An ensemble learning method used for classification that operates by constructing multiple decision trees.
- Vegetation Indices: Metrics calculated from satellite imagery that provide insights into vegetation health and moisture content, such as NDVI (Normalized Difference Vegetation Index) and NDMI (Normalized Difference Moisture Index).
- Data Augmentation: Techniques used to artificially expand the size of a training dataset by creating modified versions of images.

## Code Structure

The code is structured into several key sections:

- Imports: Necessary libraries for image processing, machine learning, and data manipulation.
- Data Loading and Preprocessing: Functions to load satellite images and preprocess them for model training.
- Model Building: A function to construct the CNN architecture.
- Training and Evaluation: Code to train the model and evaluate its performance.
- Vegetation Index Calculation: Functions to compute various vegetation indices from satellite data.
- Random Forest Training: A function to train a Random Forest model on the calculated indices.
- Recommendations Generation: Analyzing indices to provide actionable insights.
- PDF Report Generation: Creating a PDF report of the analysis results.

## Satellite Image Classification and Analysis

### Overview

This project implements a machine learning pipeline for classifying satellite images into categories such as urban, forest, and water. It also analyzes vegetation indices to provide insights into crop health and moisture content.

### Requirements

- Python 3.x Libraries: numpy, pandas, tensorflow, opencv-python, rasterio, scikit-learn, matplotlib

### Installation

To install the required libraries, run:

```bash
uv add numpy pandas tensorflow opencv-python rasterio scikit-learn matplotlib
```

### Usage

1. Set the data_dir variable to the path of your satellite images.
2. Define the categories of images you want to classify.
3. Run the script to load the data, train the model, and generate recommendations based on the analysis of vegetation indices.

#### Functions

- load_data(data_dir, categories, img_size): Loads and preprocesses images.
- build_model(input_shape, num_classes): Constructs the CNN model.
- train_model(X, y): Trains a Random Forest model on vegetation indices.
- analyze_indices(ndvi, ndmi, msavi, ndre): Generates recommendations based on calculate
- generate_pdf(recommendations, filename): Creates a PDF report of the analysis.

#### Example

To run the analysis on a specific satellite image, use:

```python
main('path_to_your_satellite_image.tif', labels)
```
