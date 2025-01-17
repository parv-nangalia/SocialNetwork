from django.contrib.auth.models import User
from .models import FriendRequest
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        """
        Ensure the email ends with @example.com.
        """
        if not value.endswith('@example.com'):
            raise ValidationError("Email must end with @example.com")
        return value.lower()

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class SearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        if User.objects.filter(email = email).exists():
            username = list(User.objects.filter(email = email).values('username'))[0]
            username = username['username']
        else:
            raise serializers.ValidationError("Invalid credentials")
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise serializers.ValidationError("Invalid credentials")
        else:
            raise serializers.ValidationError("Must include both username and password")

        data["user"] = user
        return data
    


class FriendRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendRequest
        fields = ('from_user','to_user', 'status')