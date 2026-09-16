from django.shortcuts import render, redirect
import pandas as pd
import json
from django.contrib import messages
from .models import user_reg

from air_pollution import (
    fetch_live_aqi,
    predict_aqi,
    get_dataset,
    get_dataset_stats,
    multi_algorithm_analysis,
    predict_city_aqi_all_algorithms,
    analyze_pollution_image,
    dataset_analysis,
)

# -------------------------------
# LOGIN PAGE
# -------------------------------
def user_login(request):
    if request.method == "POST":
        uname    = request.POST.get("uname")
        password = request.POST.get("password")

        user = user_reg.objects.filter(uname=uname, password=password).first()
        if user:
            request.session['user_id']   = user.id
            request.session['user_name'] = user.fullname
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return render(request, "user/user_login.html")

    return render(request, "user/user_login.html")


# -------------------------------
# REGISTER PAGE
# -------------------------------
def user_register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email     = request.POST.get("email")
        mobile    = request.POST.get("mobile")
        uname     = request.POST.get("uname")
        password  = request.POST.get("password")

        user_reg.objects.create(
            fullname=full_name,
            email=email,
            mobile=mobile,
            uname=uname,
            password=password,
        )
        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, "user/user_register.html")


# -------------------------------
# HOME PAGE — Dataset + Stats
# -------------------------------
def user_home(request):
    result     = None
    prediction = None

    if request.method == "POST":
        city = request.POST.get("city")
        data = fetch_live_aqi(city)
        if data:
            pm25       = data.get("pm25") or 0
            pm10       = data.get("pm10") or 0
            prediction = predict_aqi(pm25, pm10)
            result     = data

    dataset = get_dataset()
    stats   = get_dataset_stats()

    context = {
        "result":        result,
        "prediction":    prediction,
        "dataset_html":  dataset.to_html(classes='table table-striped', index=False),
        "stats":         stats,
        # JSON-safe for Chart.js
        "top_states_labels":  json.dumps(stats["top_states"]["labels"]),
        "top_states_values":  json.dumps(stats["top_states"]["values"]),
        "cat_labels":         json.dumps(list(stats["categories"].keys())),
        "cat_values":         json.dumps(list(stats["categories"].values())),
        "imp_labels":         json.dumps(list(stats["importance"].keys())),
        "imp_values":         json.dumps(list(stats["importance"].values())),
        "total_rows":         stats["total_rows"],
        "total_states":       stats["total_states"],
    }
    return render(request, "user/user_home.html", context)


# -------------------------------
# AIR QUALITY ANALYSIS — City AQI + 3 algorithms
# -------------------------------
def air_quality_analysis(request):
    city_result  = None
    city_error   = None

    if request.method == "POST" and request.POST.get("city"):
        city        = request.POST.get("city")
        city_result = predict_city_aqi_all_algorithms(city)
        if not city_result:
            city_error = f"Could not fetch AQI data for '{city}'. Please check the city name."

    # Always load dataset-level ML analysis
    analysis     = multi_algorithm_analysis()
    metrics      = analysis["metrics"]
    actual_50    = analysis["actual"]
    predicted_50 = analysis["predicted"]   # dict: algo_name -> list

    context = {
        "city_result":  city_result,
        "city_error":   city_error,
        "metrics":      metrics,
        # JSON for Chart.js
        "actual_json":  json.dumps(actual_50),
        "rf_json":      json.dumps(predicted_50.get("Random Forest", [])),
        "lr_json":      json.dumps(predicted_50.get("Linear Regression", [])),
        "dt_json":      json.dumps(predicted_50.get("Decision Tree", [])),
        "algo_names":   json.dumps(list(metrics.keys())),
        "algo_r2":      json.dumps([metrics[k]["r2"]  for k in metrics]),
        "algo_mae":     json.dumps([metrics[k]["mae"] for k in metrics]),
    }
    return render(request, "user/air_quality_analysis.html", context)


# -------------------------------
# POLLUTION ANALYSIS — Image upload
# -------------------------------
def pollution_analysis(request):
    analysis_result = None

    if request.method == "POST" and request.FILES.get("image_file"):
        image_file     = request.FILES["image_file"]
        image_bytes    = image_file.read()
        analysis_result = analyze_pollution_image(image_bytes)

    return render(request, "user/pollution_analysis.html",
                  {"analysis_result": analysis_result})


# -------------------------------
# LOGOUT
# -------------------------------
def logout(request):
    request.session.flush()
    return redirect('login')