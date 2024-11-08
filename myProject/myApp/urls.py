from . import views
from django.urls import path
from .views import event_detail_view,book_event, booking_confirmation, download_ticket

from userapp import views as userapp_views

urlpatterns = [
    path("", views.home, name="home"),
    path("reg", views.reg, name="reg"),
    path("login", userapp_views.login, name="login"),
    path("about/", views.about, name="about"),
    path("events/", views.events, name="events"),
    path("booking/", views.booking, name="booking"),
    path('myBooking/', views.myBooking, name='myBooking'),
    path("contact/", views.contact, name="contact"),
    path('events/<int:id>/', event_detail_view, name='event_detail'),
    path("submitevent/", views.submitevent, name="submitevent"),
    path("manageevent/", views.manageevent, name="manageevent"),
    path("create_event/", views.create_event, name="create_event"),
    path('event-success/', views.event_success, name='event_success'),
    path('book/<int:event_id>/', book_event, name='book_event'),
    path("organizer_dashboard/", views.organizer_dashboard, name="organizer_dashboard"),
    path('event/<int:event_id>/download_ticket/<int:ticket_number>/', views.download_ticket, name='download_ticket'),
    # Booking confirmation URL with the option to download tickets
    path('booking-confirmation/<int:event_id>/<int:number_of_tickets>/', booking_confirmation, name='booking_confirmation'),
    
    # Separate ticket download path after booking confirmation
    path('booking-confirmation/download_ticket/<int:event_id><int:number_of_tickets>/', download_ticket, name='download_ticket'),
    
    # Keep the download ticket URL separate
    # path('download-ticket/<int:event_id>/<int:ticket_number>/', views.download_ticket, name='download_ticket'),
    # path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('events/<int:event_id>/view/', views.view_event, name='view_event'),
    path('events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('attendees/', views.attendees_view, name='attendees'),
    path('event-performance/', views.event_performance_view, name='event_performance'),
]