from django.contrib import admin
from django.urls import path,include
from .import views
urlpatterns = [
   path('makeotp',views.MakeOTPView.as_view()),
   path('createroom',views.CreateRoomView.as_view()),
   path('createuser',views.CreateUser.as_view()),
   path('makebid',views.MakeBidView.as_view()),
   path('getroom',views.GetRoomView.as_view()),
   path('top10',views.Top10.as_view()),
   path('userrooms',views.UserRooms.as_view()),
   path('userbids',views.UserBids.as_view()),
]
