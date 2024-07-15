from django.contrib import admin
from django.urls import path, include
from . import authenticate as auth
from . import views

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', views.ListUsers, basename='user' )



urlpatterns = [

    path('', auth.HomepageAPIView.as_view(), name='homepage'),

    path('signup/', auth.UserCreate.as_view(), name='signup'),

    path('login/', auth.UserLogin.as_view(), name='login'),

    path('logout/', auth.LogoutAPIView.as_view(), name='logout'),

    # path('users/', views.ListUsers.as_view({'get': 'list'}) , name='users'),

    path('users/', include(router.urls) , name='users'),

]
    # path('friends/', views.FriendListView.as_view() , name='friends'),

    # path('pending/', views.PendingFriendRequest.as_view(), name='pending'),
