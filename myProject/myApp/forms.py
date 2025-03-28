from django import forms
from . models import Booking, Event
class DateInput(forms.DateInput):
    input_type='date'

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'desc','img', 'date', 'time', 'location', 'ticket_template','number_of_tickets', 'ticket_price','is_free','latitude', 'longitude'] 
    
    date = forms.DateField(widget=DateInput())  
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

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