from django.forms import ModelForm
from .models import Room


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__' # this will create all field forms from Room\
        exclude = ['host', 'participants']