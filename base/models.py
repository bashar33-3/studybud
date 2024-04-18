from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# The topic Model is a Parent of the Room model so it is created above it 
class Topic(models.Model):
    name = models.CharField(max_length = 200)

    # for every model we need to create the str format of it :
    def __str__(self) -> str:
        return self.name

# let us create the room table 
class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # if topic was defined below Room in the code we can reference it with 'Topic' inside quotations
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length = 200)
    description = models.TextField(null = True, blank=True)
    # many to many relationship
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True) #auto_now takes a snapshot of the time everytime we update the instance
    created = models.DateTimeField(auto_now_add=True) #auto_now_add takes the time only when the instance is created 


    # this is how we order in descending order 
    class Meta:
        ordering = ['-updated', '-created']
    # create a string representation of the instance
    def __str__(self) -> str:
        return self.name
    
# message is a child of Room because it is activated inside the room so we create the model below the Room model
class Message(models.Model):
    # user is imported from django.contrib.auth.models import User built in django check django user model for more info about the attrbs of a user 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) #related to Room Model, when the Room is deleted we need to delete the children so we do models.Cascade, if we need to keep the comments but the room is deleted we can do models.SET_NULL
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)


    # this is how we order in descending order 
    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self) -> str:
        return self.body[0:50]
    