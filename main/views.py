from django.shortcuts import render
# from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework import permissions
from django.db.models import Q
from rest_framework.throttling import SimpleRateThrottle, ScopedRateThrottle
from rest_framework import generics
from rest_framework.response import Response
# from django.http import JsonResponse
from rest_framework.decorators import action, throttle_classes
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UserSerializer, FriendRequestSerializer
from rest_framework import viewsets, filters
from .models import FriendRequest
# from rest_framework.throttling import UserRateThrottle
import logging

from django.conf import settings
print("Throttles",settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'])

logger = logging.getLogger(__name__)

# class SendFriendRequestRateThrottle(ScopedRateThrottle):
#     scope = 'send_friend_request'
#     print(scope)
    
#     def allow_request(self, request, view):
#         print("Checking throttle for:", request.user)
#         # if view.action == 'send':
#         return super().allow_request(request, view)
        # else:
        #     return True

    # def allow_request(self, request, view):
    #     allowed = super().allow_request(request, view)
    #     # logger.debug(f"Throttle applied: {self.scope}, Allowed: {allowed}")
    #     print(f"Throttle applied: {self.scope}, Allowed: {allowed}")
    #     return allowed
    

# Create your views here.
# class UserViewSet()
# class UserPage(APIView):
#     permission_classes = [IsAuthenticated]

    # def get(self, request, *args, **kwargs):
    #     to_user_id = request.data.get('to_user_id')
    #     try:
    #         to_user = User.objects.get(id=to_user_id)
    #     except User.DoesNotExist:
    #         return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
    #     if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
    #         return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
        
    #     friend_request = FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    #     return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

# class SendFriendRequestView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         to_user_id = request.data.get('to_user_id')
#         try:
#             to_user = User.objects.get(id=to_user_id)
#         except User.DoesNotExist:
#             return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
#         if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
#             return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
        
#         friend_request = FriendRequest.objects.create(from_user=request.user, to_user=to_user)
#         return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)
    

class ListUsers(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']

    def get_throttles(self):
        if self.action in ['send']:
            self.throttle_scope = 'send_friend_request'
        return super().get_throttles()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        print(page)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def get_queryset(self):
        search_query = self.request.query_params.get('search', None)
        queryset = super().get_queryset()

        if search_query:
            if '@' in search_query:
                queryset = queryset.filter(email__iexact=search_query)
            else:
                queryset = queryset.filter(username__icontains=search_query)
                
        return queryset
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        to_user = User.objects.get(pk=pk)
        from_user = request.user
        if from_user == to_user:
            return Response({"error": "You cannot send a friend request to yourself."}, status=status.HTTP_400_BAD_REQUEST)
        
        friend_request, created = FriendRequest.objects.get_or_create(from_user=from_user, to_user=to_user)
        if not created:
            return Response({"error": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        from_user = User.objects.get(pk=pk)
        to_user = request.user
        try:
            friend_request = FriendRequest.objects.get(from_user=from_user, to_user=to_user)
            friend_request.status = 'accepted'
            friend_request.save()
            return Response(FriendRequestSerializer(friend_request).data)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request does not exist."}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        from_user = User.objects.get(pk=pk)
        to_user = request.user
        try:
            friend_request = FriendRequest.objects.get(from_user=from_user, to_user=to_user)
            friend_request.status = 'rejected'
            friend_request.save()
            return Response(FriendRequestSerializer(friend_request).data)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request does not exist."}, status=status.HTTP_400_BAD_REQUEST)



    @action(detail=False, methods=['get'])
    def accepted_friends(self, request):
        user = request.user
        friends = FriendRequest.objects.filter(
            Q(from_user=user, status="accepted")
        )
        friend_users = User.objects.filter(
            Q(id__in=friends.values('to_user'))
        ).exclude(id=user.id)
        serializer = self.get_serializer(friend_users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_requests(self, request):
        user = request.user
        pending_requests = FriendRequest.objects.filter(
            Q(to_user=user, status="pending")
        )
        requests = User.objects.filter(
            Q(id__in=pending_requests.values('from_user'))
        ).exclude(id=user.id)
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)

        
# class FriendListView(generics.ListAPIView):

#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = UserSerializer

#     def get_queryset(self):
#         user = self.request.user
#         friends = FriendRequest.objects.filter(
#                     Q(from_user=user),
#                     status="accepted"
#                 ).values('to_user')
#         print(friends)
#         User.objects.filter()
    
# class PendingFriendRequest(generics.ListAPIView):

#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = FriendRequestSerializer

#     def get_queryset(self):
#         user = self.request.user
#         return FriendRequest.objects.filter(
#                     Q(to_user=user),
#                     status="pending"
#                 )

        
        


    

