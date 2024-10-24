from . import views
from django.urls import path
from .views import event_detail_view

from userapp import views as userapp_views

urlpatterns = [
    path("", views.home, name="home"),
    path("reg", views.reg, name="reg"),
    path("login", userapp_views.login, name="login"),
    path("about/", views.about, name="about"),
    path("events/", views.events, name="events"),
    path("booking/", views.booking, name="booking"),
    path("contact/", views.contact, name="contact"),
    path('events/<int:id>/', event_detail_view, name='event_detail'),
    path("submitevent/", views.submitevent, name="submitevent"),
    path("manageevent/", views.manageevent, name="manageevent"),
    path("create_event/", views.create_event, name="create_event"),
    path('event-success/', views.event_success, name='event_success'),

    path("organizer_dashboard/", views.organizer_dashboard, name="organizer_dashboard"),

    
    
]