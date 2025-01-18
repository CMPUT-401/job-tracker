from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import JobApplication, Notification
from django.utils.dateparse import parse_date
#import spacy
from collections import Counter
from django.http import JsonResponse

#nlp = spacy.load("en_core_web_sm") #load spacy language model

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
    status_filter = request.GET.get('status', None)  # Get the filter from the query parameters
    if status_filter:  # If a filter is applied
        applications = JobApplication.objects.filter(status=status_filter)
    else:
        applications = JobApplication.objects.all()  # Otherwise, show all applications

    statuses = ['Yet to Apply', 'Applied', 'Interview Offer', 'Interview Completed', 'Offered', 'Rejected']
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    # Pass both `applications`, `statuses`, and `notifications` to the template
    return render(request, 'dashboard.html', {
        'applications': applications,
        'statuses': statuses,
        'notifications': notifications,
    })

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

def add_or_edit_application(request):
    if request.method == "POST":
        app_id = request.POST.get("id", None)
        if app_id:  # Edit existing application
            application = get_object_or_404(JobApplication, id=app_id)
        else:  # Add new application
            application = JobApplication()

        # Retrieve fields and allow them to be empty
        application.company = request.POST.get("company", None) or None
        application.position = request.POST.get("position", None) or None
        application.status = request.POST.get("status", None) or None
        application.deadline = parse_date(request.POST.get("deadline", None)) or None
        application.date_applied = parse_date(request.POST.get("date_applied", None)) or None
        application.notes = request.POST.get("notes", None) or None

        application.save()
        messages.success(request, "Application saved successfully!")
        return redirect("dashboard")

    return redirect("dashboard")