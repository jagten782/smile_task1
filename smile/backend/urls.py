from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns=[
    path("",views.home,name='login_screen'),
    path("register/",views.register,name='register'),
    path("search_trains",views.search,name='search_trains'),
    path("bookings",views.bookings,name='bookings'),
    path('select_class/<int:t_id>/',views.select_class,name='select_class'),
    path('book_ticket/<str:query>/',views.book_ticket,name='book_ticket'),
    path('book/<int:num>/<str:query>/',views.book,name='book'),
    path('add_money/',views.add_money,name='add_money'),
    path('dasboard/',views.dasboard,name='dashboard'),
    path('cancel/',views.cancel,name='cancel')
]

