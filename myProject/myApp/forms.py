from django import forms
from . models import Booking, Event
class DateInput(forms.DateInput):
    input_type='date'

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'desc','img', 'date', 'time', 'location']  # Exclude 'approved'
    
    date = forms.DateField(widget=DateInput())  # Use the DateInput class
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

class BookingForm(forms.ModelForm):
    class Meta:
        model=Booking
        fields='__all__'

        widgets={
            'booking_date':DateInput(),
        }

        labels={
            'cus_name':"Customer Name:",
            'cus_ph':"Customer Phone:",
            'name':"Event Name:",
            'booking_date':"Booking Date:",
        }