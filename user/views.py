from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# ---------- REGISTER ----------
def user_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "All fields are required")
            return redirect('user_register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('user_register')

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Registration successful")
        return redirect('user_login')

    return render(request, 'user/user_register.html')


# ---------- LOGIN ----------
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('user_home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'user/user_login.html')


# ---------- HOME ----------
def user_home(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    return render(request, 'user/user_home.html')


# ---------- LOGOUT ----------
def user_logout(request):
    logout(request)
    return redirect('user_login')


# ---------- AIR QUALITY ----------
def air_quality_analysis(request):
    return render(request, 'user/air_quality_analysis.html')

# ---------- USER INDEX ----------
def user_index(request):
    return render(request, 'user/user_index.html')