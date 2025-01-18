from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            # Check if the username already exists
            if not User.objects.filter(username=username).exists():
                # Create the user
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Log in the user after signup
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('dashboard')  # Redirect to the dashboard
                else:
                    messages.error(request, "Something went wrong during login.")
            else:
                messages.error(request, "Username already exists.")
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'signup.html')

def login_user(request):
    if request.method == 'POST':
        # Get the username and password from the form
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in and redirect to a protected page
            login(request, user)
            return redirect('dashboard')  # Replace 'dashboard' with your desired page
        else:
            # Invalid credentials
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')  # Render the login page

def home(request):
    return render(request, 'home.html')

def dashboard(request):
    return render(request, 'dashboard.html', {'username': request.user.username})

def logout_user(request):
    logout(request)
    return redirect('login')


