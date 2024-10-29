from pyexpat.errors import messages
import random
import time
from django.conf import settings
from xml.dom import ValidationErr
from django.shortcuts import render,redirect,get_object_or_404
from .models import Event,Booking
from .forms import BookingForm
from django.views.generic import ListView
from django.contrib import messages
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
import io

def download_ticket(request, event_id, ticket_number):
    event = get_object_or_404(Event, id=event_id)
    if event.ticket_template:
        # Open the ticket template image
        image = Image.open(event.ticket_template.path)
        draw = ImageDraw.Draw(image)

        # Define the text for the ticket number and its position
        ticket_text = f"Ticket No: {ticket_number}"
        font = ImageFont.load_default()
        text_position = (100, 100)  # Adjust this position as needed
        draw.text(text_position, ticket_text, font=font, fill=(0, 0, 0))

        # Save the image to an in-memory file
        img_io = io.BytesIO()
        image.save(img_io, format='PNG')
        img_io.seek(0)

        # Serve the image as a downloadable file
        response = HttpResponse(img_io, content_type="image/png")
        response['Content-Disposition'] = f'attachment; filename="ticket_{ticket_number}.png"'
        return response
    else:
        return HttpResponse("Ticket template not available for this event.", status=404)
def events_view(request):
    events = Event.objects.all()
    for event in events:
        # Set a default ticket number if it's missing or empty
        if not hasattr(event, 'ticket_number') or not event.ticket_number:
            event.ticket_number = 12345  # Replace with your default logic
    return render(request, 'myApp/events.html', {'eve': events})
    
def home(request):
    return render(request, "myApp/home.html")

def reg(request):
    return render(request, "myApp/reg.html")

def login(request):
    return render(request, "myApp/login.html")


def about(request):
    return render(request,"myApp/about.html")

def events(request):
    search_query = request.GET.get('q', '')  # Get the search query from the URL

    if search_query:
        # Filter events that contain the search query in their name or description
        events = Event.objects.filter(name__icontains=search_query) | Event.objects.filter(desc__icontains=search_query)
    else:
        events = Event.objects.all()  # Get all events if no search query is provided

    dict_eve = {
        'eve': events,  # Pass the filtered events to the template
        'search_query': search_query  # Pass the search query to the template
    }

    return render(request, "myApp/events.html", dict_eve)
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
            event = form.save(commit=False)  # Don't save to the database yet
            event.organizer = request.user  # Set the current user as the organizer
            try:
                event.full_clean()  # Validate the event instance (includes the new logic)
                event.save()  # Save the event to the database
                return redirect('event_success')  # Redirect after successful submission
            except ValidationErr as e:
                form.add_error(None, e)  # Add validation errors to the form
                
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

def view_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    return render(request, 'events/view_event.html', {'event': event})

def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('manageevent')
    else:
        form = EventForm(instance=event)
    
    return render(request, 'events/edit_event.html', {'form': form, 'event': event})

def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('manageevent')
    
    return render(request, 'events/delete_event.html', {'event': event})
      
def book_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        # Get user details from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')  # Added phone number
        number_of_tickets = int(request.POST.get('number_of_tickets', 1))  # Added ticket count
        
        # Check ticket limit
        if number_of_tickets > 10:
            messages.error(request, "You cannot book more than 10 tickets.")
            return render(request, 'booking.html', {'event': event})

        # Save the booking information
        Booking.objects.create(
            event=event,
            name=name,
            email=email,
            phone=phone,
            number_of_tickets=number_of_tickets,
            ticket_price=event.ticket_price,  # Adding ticket price from the event
        )
        
        return redirect('booking_confirmation', event_id=event_id, number_of_tickets=number_of_tickets)  # Redirect to a confirmation page after booking

    return render(request, 'booking.html', {'event': event})
def booking_confirmation(request, event_id, number_of_tickets):
    # Retrieve the event based on the event_id
    event = get_object_or_404(Event, id=event_id)

    # Generate a unique ticket number (e.g., using a timestamp and random number)
    ticket_number = f"{int(time.time())}_{random.randint(1000, 9999)}"  # Example ticket number logic
    ticket_template_url = f"{settings.MEDIA_URL}{event.ticket_template.name}" if event.ticket_template else None

    # Prepare the context data to pass to the template
    context = {
        'ticket_number': ticket_number,
        'ticket_template_url': ticket_template_url,
        'event': event,  # Pass the event object
        'number_of_tickets': number_of_tickets,  # Pass number of tickets to template
    }

    return render(request, 'booking_confirmation.html', context)

def myBooking(request):
    if request.user.is_authenticated:
        bookings = Booking.objects.filter(email=request.user.email)  
    else:
        bookings = []

    return render(request, 'myBooking.html', {'bookings': bookings})

def attendees_view(request):
    bookings = Booking.objects.select_related('event').all()
    context = {
        'bookings': bookings,
    }
    return render(request, 'attendees.html', context)