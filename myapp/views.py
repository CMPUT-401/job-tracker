from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def resume_tailor(request):
    # Simulating a master resume for now
    master_resume = [
        "Developed REST APIs using Django and Flask.",
        "Optimized database queries, improving performance by 25%.",
        "Led a team of 5 to deliver high-quality software projects.",
        "Proficient in Python, JavaScript, and SQL.",
        "Collaborated with cross-functional teams to achieve project goals."
    ]
    blank_resume = []

    if request.method == 'POST':
        # Logic to handle copying items from master to blank resume
        selected_items = request.POST.getlist('selected_items')
        blank_resume.extend(selected_items)

    return render(request, 'resume_tailor.html', {
        'master_resume': master_resume,
        'blank_resume': blank_resume,
    })