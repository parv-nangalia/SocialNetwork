from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email','username','password1','password2')

        # Adjust fields as per your CustomUser model or use default User model