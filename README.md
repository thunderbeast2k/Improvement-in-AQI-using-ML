# Improvement in Air Quality Index (AQI) Prediction Using Machine Learning & Deep Learning

An end-to-end machine learning and deep learning project focused on analyzing environmental sensor data, tracking historical air quality metrics, and predicting Air Quality Index (AQI) levels to aid in proactive pollution mitigation.

---

## Overview

Air pollution is a critical public health and environmental challenge. This project leverages predictive modeling techniques to forecast AQI trends using historical multi-pollutant datasets. By identifying patterns across meteorological factors and pollutant concentrations (such as $PM_{2.5}$, $PM_{10}$, $NO_2$, $SO_2$, and $CO$), the models provide early warning indicators to support data-driven decision-making.

---

## Features

* **Data Preprocessing & Cleaning:** Handles missing data, outliers, and time-series feature alignment across monitoring stations.
* **Exploratory Data Analysis (EDA):** Statistical summaries, correlation matrices, and spatial/temporal pollutant distributions.
* **Feature Engineering:** Rolling averages, lag features, and seasonal trend indicators.
* **Model Training & Evaluation:** Benchmarking classical regression models (Random Forest, XGBoost) and sequence-based Deep Learning models (LSTM/GRU/ANN) using $R^2$, RMSE, and MAE metrics.
* **Large Dataset Handling:** Integrated with Git LFS (Large File Storage) for tracking historical dataset files.

---

## Project Structure

```text
Improvement-in-AQI-using-ML/
│
├── data.csv                 # Raw/processed historical air quality dataset (managed via Git LFS)
├── notebooks/               # Jupyter notebooks for EDA, preprocessing, and model experiments
├── src/                     # Core application and model training source code
│   ├── preprocess.py        # Data cleaning and feature engineering pipelines
│   ├── models.py            # Model architecture definitions
│   └── train.py             # Model training and validation scripts
│
├── .gitattributes           # Git LFS tracking rules
├── .gitignore               # Ignored binaries, caches, and environment artifacts
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation