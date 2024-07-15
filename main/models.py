from django.db import models
from django.contrib.auth.models import User 
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
# Create your models here.

class FriendRequest(models.Model):

    CHOICES = (
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Pending', 'Pending'),
    )
    
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=CHOICES, default='pending')

    class Meta:
        unique_together = ('from_user', 'to_user')

