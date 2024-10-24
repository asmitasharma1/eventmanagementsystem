from django.shortcuts import render,redirect,get_object_or_404
from .models import Event
from .forms import BookingForm
from django.views.generic import ListView


def home(request):
    return render(request, "myApp/home.html")

def reg(request):
    return render(request, "myApp/reg.html")

def login(request):
    return render(request, "myApp/login.html")


def about(request):
    return render(request,"myApp/about.html")
def events(request):
    dict_eve={
        'eve':Event.objects.all()
    }
    return render(request,"myApp/events.html",dict_eve)
def booking(request):
    if request.method == 'POST':
        form=BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')


    form=BookingForm()
    dict_form={
        'form':form
    }
    return render(request,"myApp/booking.html",dict_form)
def contact(request):
    return render(request,"myApp/contact.html")

def event_detail_view(request, id):
    event = get_object_or_404(Event, id=id)  # Fetch the event or return 404 if not found
    return render(request, 'event_detail.html', {'event': event})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EventForm

def submitevent(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user  # Set the current user as the organizer
            event.save()  # Save event with approved=False by default
            return redirect('event_success')  # Redirect after submission
    else:
        form = EventForm()
    return render(request, 'submitevent.html', {'form': form})


def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user  # Set the current user as the organizer
            event.save()  # Save event with approved=False by default
            return redirect('event_success')  # Redirect after submission
    else:
        form = EventForm()
    return render(request, 'create_event.html', {'form': form})

def event_success(request):
    return render(request, 'event_success.html')  # Render success page


def organizer_dashboard(request):
    return render(request, 'organizer_dashboard.html')


def manageevent(request):
    # Fetch the events for the logged-in organizer
    events = Event.objects.filter(organizer=request.user)
    return render(request, 'manageevent.html', {'events': events})  