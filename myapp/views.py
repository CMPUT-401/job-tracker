from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import JobApplication, Notification
from django.utils.dateparse import parse_date

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
    if 'master_resume' not in request.session:
        request.session['master_resume'] = {
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
    if 'blank_resume' not in request.session:
        request.session['blank_resume'] = {}

    master_resume = request.session['master_resume']
    blank_resume = request.session['blank_resume']

    if request.method == "POST":
        action = request.POST.get('action')
        print(f"Action: {action}")  # Debugging to see what action was triggered

        if action == "add_to_blank":
            selected_items = request.POST.getlist('selected_items')
            print(f"Selected Items: {selected_items}")
            for item in selected_items:
                section, content = item.split('|', 1)
                # Add the item to blank_resume
                if section not in blank_resume:
                    blank_resume[section] = []
                if content not in blank_resume[section]:
                    blank_resume[section].append(content)
                # Do NOT remove from master_resume in this step
                # Uncomment the following lines ONLY if you want to remove after copying:
                # if section in master_resume and content in master_resume[section]:
                #     master_resume[section].remove(content)

        elif action.startswith("copy_section"):
            section = action.split('|')[1]
            if section in master_resume and section not in blank_resume:
                blank_resume[section] = master_resume[section][:]

        elif action == "remove_from_blank":
            section = request.POST.get('section')
            content = request.POST.get('content')
            if section in blank_resume and content in blank_resume[section]:
                blank_resume[section].remove(content)
                if not blank_resume[section]:
                    del blank_resume[section]

        elif action == "add_section_master":
            new_section = request.POST.get('new_section')
            if new_section:
                new_section = new_section.strip()
                if new_section and new_section not in master_resume:
                    master_resume[new_section] = []

        elif action == "remove_section_blank":
            section = request.POST.get('section')
            if section in blank_resume:
                del blank_resume[section]

        elif action == "remove_section_master":
            section = request.POST.get('section')
            if section in master_resume:
                del master_resume[section]

        elif action == "add_section_blank":
            new_section = request.POST.get('new_section').strip()
            if new_section and new_section not in blank_resume:
                blank_resume[new_section] = []

        elif action == "add_item_master":
            section = request.POST.get('section')
            new_item = request.POST.get('new_item').strip()
            if section in master_resume and new_item:
                master_resume[section].append(new_item)

        elif action == "add_item_blank":
            section = request.POST.get('section')
            new_item = request.POST.get('new_item')
            if section and new_item:
                section = section.strip()
                new_item = new_item.strip()
                if section not in blank_resume:
                    blank_resume[section] = []
                blank_resume[section].append(new_item)
                
        elif action == "remove_from_master":
            section = request.POST.get('section')
            content = request.POST.get('content')
            if section in master_resume and content in master_resume[section]:
                master_resume[section].remove(content)
                if not master_resume[section]:
                    del master_resume[section]

        # Save the updates to session
        request.session['master_resume'] = master_resume
        request.session['blank_resume'] = blank_resume

        print(f"Blank Resume After Update: {request.session['blank_resume']}")

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