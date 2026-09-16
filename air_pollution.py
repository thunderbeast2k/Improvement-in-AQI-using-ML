import pandas as pd
import numpy as np
import requests
import cv2
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# -----------------------------------------------
# LOAD & PREPARE DATASET (once at startup)
# -----------------------------------------------
_df_cache = None

def _load_data():
    global _df_cache
    if _df_cache is None:
        df = pd.read_csv("data.csv", encoding='cp1252', low_memory=False)
        # Only fill numeric columns with 0, leave strings as-is
        num_cols = df.select_dtypes(include=[np.number]).columns
        df[num_cols] = df[num_cols].fillna(0)
        # Convert pollutant columns to numeric (coerce non-numeric to NaN then 0)
        for col in ['so2', 'no2', 'rspm', 'spm', 'pm2_5']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        _df_cache = df
    return _df_cache


# -----------------------------------------------
# TRAIN GLOBAL MODEL (Random Forest) for live AQI
# -----------------------------------------------
_global_model = None

def _get_global_model():
    global _global_model
    if _global_model is None:
        df = _load_data()
        X = df[['so2', 'no2', 'rspm', 'spm']]
        y = df['pm2_5']
        _global_model = RandomForestRegressor(n_estimators=50, random_state=42)
        _global_model.fit(X, y)
    return _global_model


# -----------------------------------------------
# API FUNCTION — Fetch live AQI for a city
# -----------------------------------------------
def fetch_live_aqi(city):
    API_KEY = "1e102e5042dda0116a70b2fc1105de4e43967b95"
    url = f"https://api.waqi.info/feed/{city}/?token={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("status") == "ok":
            iaqi = data["data"].get("iaqi", {})
            return {
                "aqi":   data["data"].get("aqi", 0),
                "city":  data["data"].get("city", {}).get("name", city),
                "pm25":  iaqi.get("pm25", {}).get("v", 0),
                "pm10":  iaqi.get("pm10", {}).get("v", 0),
                "so2":   iaqi.get("so2",  {}).get("v", 0),
                "no2":   iaqi.get("no2",  {}).get("v", 0),
                "co":    iaqi.get("co",   {}).get("v", 0),
                "o3":    iaqi.get("o3",   {}).get("v", 0),
            }
    except Exception:
        pass
    return None


# -----------------------------------------------
# SINGLE ML PREDICTION using live city values
# -----------------------------------------------
def predict_aqi(pm25, pm10):
    mdl = _get_global_model()
    inp = pd.DataFrame(
        [[pm25 or 0, pm10 or 0, pm10 or 0, pm25 or 0]],
        columns=['so2', 'no2', 'rspm', 'spm']
    )
    return round(float(mdl.predict(inp)[0]), 2)


# -----------------------------------------------
# CITY AQI — predict with ALL 3 algorithms
# -----------------------------------------------
def predict_city_aqi_all_algorithms(city):
    """
    Fetch live AQI for city, then run SO2/NO2/RSPM/SPM values
    through all 3 ML models.  Returns a dict with live data +
    per-algorithm predictions.
    """
    live = fetch_live_aqi(city)
    if not live:
        return None

    so2  = live.get("so2",  0) or 0
    no2  = live.get("no2",  0) or 0
    pm25 = live.get("pm25", 0) or 0
    pm10 = live.get("pm10", 0) or 0

    inp = pd.DataFrame(
        [[so2, no2, pm10, pm25]],
        columns=['so2', 'no2', 'rspm', 'spm']
    )

    df = _load_data()
    X = df[['so2', 'no2', 'rspm', 'spm']]
    y = df['pm2_5']
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

    rf  = RandomForestRegressor(n_estimators=50, random_state=42)
    lr  = LinearRegression()
    dt  = DecisionTreeRegressor(max_depth=6, random_state=42)

    rf.fit(X_train, y_train)
    lr.fit(X_train, y_train)
    dt.fit(X_train, y_train)

    rf_pred  = round(float(rf.predict(inp)[0]),  2)
    lr_pred  = round(float(lr.predict(inp)[0]),  2)
    dt_pred  = round(float(dt.predict(inp)[0]),  2)

    def classify(val):
        if val <= 50:   return "Good"
        if val <= 100:  return "Moderate"
        if val <= 150:  return "Unhealthy for Sensitive Groups"
        if val <= 200:  return "Unhealthy"
        if val <= 300:  return "Very Unhealthy"
        return "Hazardous"

    return {
        "live":      live,
        "rf_pred":   rf_pred,  "rf_category":  classify(rf_pred),
        "lr_pred":   lr_pred,  "lr_category":  classify(lr_pred),
        "dt_pred":   dt_pred,  "dt_category":  classify(dt_pred),
        "avg_pred":  round((rf_pred + lr_pred + dt_pred) / 3, 2),
    }


# -----------------------------------------------
# DATASET FUNCTION — first 50 rows
# -----------------------------------------------
def get_dataset():
    df = _load_data()
    return df.head(50)


# -----------------------------------------------
# DATASET STATS — for home page cards & charts
# -----------------------------------------------
def get_dataset_stats():
    df = _load_data()

    # Summary stats
    stats = {}
    for col in ['so2', 'no2', 'rspm', 'spm', 'pm2_5']:
        stats[col] = {
            "mean":   round(df[col].mean(), 2),
            "median": round(df[col].median(), 2),
            "max":    round(df[col].max(), 2),
            "std":    round(df[col].std(), 2),
        }

    # Top 10 polluted states by avg RSPM
    top_states = (
        df.groupby('state')['rspm']
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    # Pollution category distribution by rspm
    def cat(v):
        if v <= 60:  return "Good"
        if v <= 90:  return "Moderate"
        if v <= 120: return "Poor"
        return "Hazardous"

    df['category'] = df['rspm'].apply(cat)
    cat_counts = df['category'].value_counts().to_dict()

    # Feature importance from RF on this dataset
    X = df[['so2', 'no2', 'rspm', 'spm']]
    y = df['pm2_5']
    rf = RandomForestRegressor(n_estimators=50, random_state=42)
    rf.fit(X, y)
    importance = dict(zip(['so2', 'no2', 'rspm', 'spm'],
                          [round(v, 4) for v in rf.feature_importances_]))

    return {
        "stats":      stats,
        "top_states": {"labels": top_states.index.tolist(),
                       "values": [round(v, 2) for v in top_states.values]},
        "categories": cat_counts,
        "importance": importance,
        "total_rows": len(df),
        "total_states": df['state'].nunique(),
    }


# -----------------------------------------------
# MULTI-ALGORITHM ANALYSIS — 3 algorithms compared
# -----------------------------------------------
def multi_algorithm_analysis():
    df = _load_data()
    X = df[['so2', 'no2', 'rspm', 'spm']]
    y = df['pm2_5']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    algorithms = {
        "Random Forest":   RandomForestRegressor(n_estimators=50, random_state=42),
        "Linear Regression": LinearRegression(),
        "Decision Tree":   DecisionTreeRegressor(max_depth=6, random_state=42),
    }

    results = {}
    predictions_50 = {}
    actual_50 = y_test.tolist()[:50]

    for name, mdl in algorithms.items():
        mdl.fit(X_train, y_train)
        preds = mdl.predict(X_test)
        results[name] = {
            "mae":  round(mean_absolute_error(y_test, preds), 3),
            "mse":  round(mean_squared_error(y_test, preds),  3),
            "r2":   round(r2_score(y_test, preds),            4),
        }
        predictions_50[name] = [round(p, 2) for p in preds[:50]]

    return {
        "metrics":    results,
        "actual":     actual_50,
        "predicted":  predictions_50,
    }


# -----------------------------------------------
# IMAGE-BASED POLLUTION ANALYSIS using OpenCV
# -----------------------------------------------
def analyze_pollution_image(image_bytes):
    """
    Analyze an uploaded image for pollution indicators.
    Uses OpenCV to extract color/haze features and classify air quality.
    """
    try:
        import numpy as np
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {"error": "Could not read image. Please upload a valid image file."}

        # Convert to different color spaces
        img_rgb   = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_hsv   = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        h, w = img.shape[:2]

        # --- Feature extraction ---
        # 1. Brightness (higher = clearer sky)
        brightness = round(float(np.mean(img_gray)), 2)

        # 2. Blue channel intensity (clear sky = high blue)
        blue_intensity = round(float(np.mean(img_rgb[:, :, 2])), 2)

        # 3. Contrast (hazy images have lower contrast)
        contrast = round(float(img_gray.std()), 2)

        # 4. Saturation from HSV (pollution reduces saturation)
        saturation = round(float(np.mean(img_hsv[:, :, 1])), 2)

        # 5. Haze Factor — ratio of low-contrast pixels
        laplacian_var = cv2.Laplacian(img_gray, cv2.CV_64F).var()
        haze_factor   = round(max(0, 100 - min(laplacian_var / 5, 100)), 2)

        # 6. Gray dominance (pollution makes images grayer)
        r_mean = float(np.mean(img_rgb[:, :, 0]))
        g_mean = float(np.mean(img_rgb[:, :, 1]))
        b_mean = float(np.mean(img_rgb[:, :, 2]))
        gray_dominance = round(1 - (max(r_mean, g_mean, b_mean) -
                                    min(r_mean, g_mean, b_mean)) / 255, 4)

        # --- Pollution Score (0=clean, 500=very polluted) ---
        # High haze, low blue, low contrast, high gray = more pollution
        pollution_score = (
            haze_factor * 2.0
            + (255 - blue_intensity) * 0.8
            + (100 - min(contrast, 100)) * 0.5
            + gray_dominance * 80
        )
        pollution_score = round(min(pollution_score, 500), 1)

        # --- Classification ---
        if pollution_score < 80:
            level = "Good"
            color = "#27ae60"
            description = "Air quality appears clean and clear. Excellent visibility."
            recommendations = [
                "Enjoy outdoor activities freely.",
                "Air quality is excellent — no precautions needed.",
                "Great day for exercise and outdoor sports."
            ]
        elif pollution_score < 180:
            level = "Moderate"
            color = "#f39c12"
            description = "Moderate haze detected. Air quality is acceptable."
            recommendations = [
                "Unusually sensitive people should consider reducing prolonged outdoor exertion.",
                "Keep windows open for ventilation.",
                "Monitor air quality updates."
            ]
        elif pollution_score < 300:
            level = "Poor"
            color = "#e74c3c"
            description = "Significant haze/pollution detected. Reduced visibility."
            recommendations = [
                "People with respiratory conditions should limit outdoor exposure.",
                "Wear a mask (N95) if going outside.",
                "Avoid strenuous outdoor activity.",
                "Keep windows closed and use air purifiers indoors."
            ]
        else:
            level = "Hazardous"
            color = "#8e44ad"
            description = "Severe pollution/haze detected. Very poor visibility."
            recommendations = [
                "Avoid all outdoor activities if possible.",
                "Wear N95 mask if you must go outside.",
                "Keep all windows and doors sealed.",
                "Use air purifiers indoors.",
                "Seek medical advice if experiencing breathing difficulties."
            ]

        # Encode image for display in browser
        _, buffer   = cv2.imencode('.jpg', img)
        import base64
        img_b64 = base64.b64encode(buffer).decode('utf-8')

        return {
            "pollution_score":  pollution_score,
            "pollution_level":  level,
            "level_color":      color,
            "description":      description,
            "recommendations":  recommendations,
            "brightness":       brightness,
            "blue_intensity":   blue_intensity,
            "contrast":         contrast,
            "saturation":       saturation,
            "haze_factor":      haze_factor,
            "gray_dominance":   round(gray_dominance * 100, 2),
            "image_b64":        img_b64,
            "image_size":       f"{w} x {h} px",
        }

    except Exception as e:
        return {"error": f"Image analysis failed: {str(e)}"}


# -----------------------------------------------
# LEGACY COMPAT — kept for any old references
# -----------------------------------------------
def dataset_analysis():
    result = multi_algorithm_analysis()
    return result["actual"], result["predicted"]["Random Forest"]