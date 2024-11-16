import math
from pyexpat.errors import messages
import random
import time
from django.conf import settings
from xml.dom import ValidationErr
from django.shortcuts import render,redirect,get_object_or_404
from .models import Event,Booking, Notification
from .forms import BookingForm
from django.views.generic import ListView
from django.contrib import messages
from datetime import datetime, timezone
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
import io
from django.db.models import Q
from geopy.distance import geodesic
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.utils.timezone import now
from django.db.models import Count

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

        response['Location'] = reverse('myBooking')  # Adjust if 'myBooking' is named differently in urls.py
        response.status_code = 303  # HTTP 303 See Other for immediate redirect after download
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
    # Annotate each event with total attendees and order by the most attended
    featured_events = (
        Event.objects
        .annotate(total_attendees=Count('bookings'))  
        .order_by('-total_attendees')[:3]  # Get top 3 events based on total attendees
    )

    return render(request, "myApp/home.html", {
        'featured_events': featured_events,
    })
def reg(request):
    return render(request, "myApp/reg.html")

def login(request):
    return render(request, "myApp/login.html")


def about(request):
    return render(request,"myApp/about.html")

# Function to calculate the distance using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def events(request):
    search_query = request.GET.get('q', '')  # Get the search query from the URL
    user_lat = request.GET.get('user_lat')   # Get user latitude
    user_lon = request.GET.get('user_lon')   # Get user longitude
    nearby = request.GET.get('nearby', False) 

    events = Event.objects.all()  # Default to all events

    current_time = now()
    if search_query:
        # Filter events that contain the search query in their name or description
        events = Event.objects.filter(name__icontains=search_query) | Event.objects.filter(desc__icontains=search_query)
    else:
        events = Event.objects.all()  # Get all events if no search query is provided

    event_distances = []

    if nearby and user_lat and user_lon:
        user_location = (float(user_lat), float(user_lon))
        
        for event in events:
            event_location = (event.latitude, event.longitude)  # Ensure events have lat/lon fields
            distance = haversine(user_location[0], user_location[1], event_location[0], event_location[1]) 
            event_distances.append((event, distance))  # Store event and its distance
    
    # If event_distances is populated, proceed to sort
        if event_distances:
            event_distances.sort(key=lambda x: x[1])  # Sort by the second element in the tuple (distance)

            # Select the top K nearest events (K = 7)
            K = 7
            nearest_events = [event for event, _ in event_distances[:K]]
            events = Event.objects.filter(id__in=[event.id for event in nearest_events])
    # Separate upcoming and past events
    upcoming_events = events.filter(date__gte=current_time).order_by('date')  # Events in the future or today
    past_events = events.filter(date__lt=current_time).order_by('-date')      # Events in the past

    dict_eve = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        # 'eve': events,  # Pass the filtered events to the template
        'search_query': search_query,  # Pass the search query to the template
        'user_lat': user_lat,
        'user_lon': user_lon,
        'nearby': nearby,
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
            event.latitude = form.cleaned_data.get('latitude')
            event.longitude = form.cleaned_data.get('longitude')
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


@login_required
def organizer_dashboard(request):
    # Get the current logged-in user as the organizer
    organizer = request.user

    # Fetch all events created by this organizer
    events = Event.objects.filter(organizer=organizer)

    # Categorize events into future and past
    current_date = timezone.now().date()
    future_events = []
    past_events = []

    for event in events:
        if event.date < current_date:
            past_events.append(event)
        else:
            future_events.append(event)

    context = {
        'future_events': future_events,
        'past_events': past_events,
    }

    return render(request, 'organizer_dashboard.html', context)

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
    
    # Convert timezone.now() to a date to match event.date if event.date is a date
    is_event_in_future = event.date >= timezone.now().date()

    if request.method == 'POST'and is_event_in_future:
        # Get user details from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')  # Added phone number
        number_of_tickets = int(request.POST.get('number_of_tickets', 1))  # Added ticket count
        
        # Check ticket limit
        if number_of_tickets > 10:
            messages.error(request, "You cannot book more than 10 tickets.")
            return render(request, 'booking.html', {'event': event})

        ticket_number = f"{int(time.time())}_{random.randint(1000, 9999)}"

        # Save the booking information
        booking = Booking.objects.create(
            event=event,
            name=name,
            email=email,
            phone=phone,
            number_of_tickets=number_of_tickets,
            ticket_price=event.ticket_price,  # Adding ticket price from the event
            ticket_number=ticket_number,
        )
        message = f"You have successfully booked the event: {event.name} on {event.date}."
        Notification.objects.create(user=request.user, message=message)
    
        return redirect('booking_confirmation', event_id=event_id, booking_id=booking.id)  # Redirect to a confirmation page after booking

    return render(request, 'booking.html', {'event': event, 'is_event_in_future': is_event_in_future,})
    
def booking_confirmation(request, event_id, booking_id):
    # Retrieve the event based on the event_id
    event = get_object_or_404(Event, id=event_id)
    booking = get_object_or_404(Booking, id=booking_id, event=event)

    # Generate a unique ticket number (e.g., using a timestamp and random number)
    # ticket_number = f"{int(time.time())}_{random.randint(1000, 9999)}"  # Example ticket number logic
    ticket_number = booking.ticket_number
    ticket_template_url = f"{settings.MEDIA_URL}{event.ticket_template.name}" if event.ticket_template else None

    
    # Prepare the context data to pass to the template
    context = {
        'ticket_number': booking.ticket_number,
        'ticket_template_url': ticket_template_url,
        'event': event,  # Pass the event object
        'number_of_tickets': booking.number_of_tickets,  # Pass number of tickets to template
    }

    return render(request, 'booking_confirmation.html', context)

def myBooking(request):
    if request.user.is_authenticated:
        # Get current date and time
        current_date = timezone.now()

        # Filter bookings for upcoming and past events
        upcoming_bookings = Booking.objects.filter(email=request.user.email, event__date__gte=current_date).order_by('event__date')
        past_bookings = Booking.objects.filter(email=request.user.email, event__date__lt=current_date).order_by('-event__date')
    else:
        upcoming_bookings = []
        past_bookings = []

    return render(request, 'myBooking.html', {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings
    })
    
@login_required
def attendees_view(request):
    # Get the current logged-in user as the organizer
    organizer = request.user
    
    # Get all events for this organizer
    events = Event.objects.filter(organizer=organizer)
    
    # Get the selected event ID from the query parameters, if any
    event_id = request.GET.get('event_id')
    if event_id:
        # Filter bookings by the selected event only if it's owned by the organizer
        bookings = Booking.objects.filter(event_id=event_id, event__organizer=organizer)
        selected_event_id = int(event_id)
    else:
        # Show all bookings for all events owned by the organizer
        bookings = Booking.objects.filter(event__organizer=organizer)
        selected_event_id = None

    context = {
        'bookings': bookings,
        'events': events,
        'selected_event_id': selected_event_id,
    }

    return render(request, 'attendees.html', context)

@login_required
def event_performance_view(request):
    # Get the current logged-in user as the organizer
    organizer = request.user

    # Fetch all events created by this organizer
    events = Event.objects.filter(organizer=organizer)

    # Prepare performance data for each event
    performance_data = []
    for event in events:
        # Calculate total attendees for the event (1 ticket per booking)
        total_attendees = Booking.objects.filter(event=event).count()
        current_date = datetime.now(timezone.utc).date()
        performance_data.append({
            'event': event,
            'total_attendees': total_attendees,
            'is_past': event.date < current_date 
        })

    context = {
        'performance_data': performance_data,
    }

    return render(request, 'event_performance.html', context)

