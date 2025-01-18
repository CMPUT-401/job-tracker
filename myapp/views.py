from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import JobApplication
import spacy
from collections import Counter
from django.http import JsonResponse

nlp = spacy.load("en_core_web_sm") #load spacy language model

def extract_keywords(text, top_n=10):
    """
    Extracts keywords from a given text using spaCy.
    """
    # Process the text with spaCy
    doc = nlp(text)

    # List to hold the keywords (filtered words)
    keywords = [
        token.text.lower() for token in doc
        if token.pos_ in ["NOUN", "PROPN", "ADJ", "VERB"] and not token.is_stop and not token.is_punct
    ]

    # Count the frequency of each keyword
    keyword_freq = Counter(keywords)

    # Return the most common keywords
    return keyword_freq.most_common(top_n)

def index(request):
    """
    Renders the main page where users can paste text.
    """
    return render(request, "keyword_extractor/index.html")

def extract_keywords_view(request):
    """
    View to handle the AJAX request for keyword extraction.
    """
    if request.method == "POST":
        text = request.POST.get("text")
        keywords = extract_keywords(text)
        return JsonResponse({"keywords": keywords})

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
    applications = JobApplication.objects.all()  # Fetch all job applications
    return render(request, 'dashboard.html', {'applications': applications})

def logout_user(request):
    logout(request)
    return redirect('login')

def resume_tailor(request):
    # Example data for Master Resume
    master_resume = {
        "Experiences": [
            "Software Engineer at XYZ Corp (2020 - Present)",
            "Intern at ABC Inc. (2018 - 2019)"
        ],
        "Projects": [
            "Developed a job tracking application using Django",
            "Created a weather forecasting app using React"
        ],
        "Skills": [
            "Python, Django, JavaScript",
            "SQL, PostgreSQL, MongoDB"
        ]
    }

    # Initialize or retrieve blank_resume from session
    if request.method == "POST":
        selected_items = request.POST.getlist('selected_items')
        # Retrieve blank_resume as a dictionary or initialize a new one
        blank_resume = request.session.get('blank_resume', {})
        if not isinstance(blank_resume, dict):
            blank_resume = {}  # Ensure blank_resume is a dictionary

        for item in selected_items:
            section, content = item.split('|', 1)  # Split section and content
            if section not in blank_resume:
                blank_resume[section] = []  # Initialize section if it doesn't exist
            if content not in blank_resume[section]:
                blank_resume[section].append(content)  # Append content to the section

        # Save the updated blank_resume back to the session
        request.session['blank_resume'] = blank_resume
    else:
        # Retrieve blank_resume from the session for GET requests
        blank_resume = request.session.get('blank_resume', {})
        if not isinstance(blank_resume, dict):
            blank_resume = {}

    return render(request, 'resume_tailor.html', {
        'master_resume': master_resume,
        'blank_resume': blank_resume,
    })

def add_application(request):
    if request.method == 'POST':
        company = request.POST['company']
        position = request.POST['position']
        status = request.POST['status']
        deadline = request.POST['deadline']
        date_applied = request.POST.get('date_applied', None)
        notes = request.POST.get('notes', '')

        JobApplication.objects.create(
            company=company,
            position=position,
            status=status,
            deadline=deadline,
            date_applied=date_applied,
            notes=notes
        )
        return redirect('dashboard')  # Redirect to the dashboard after adding
    return render(request, 'dashboard.html')
