from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('team/', views.team, name='team'),
    path('gallery/', views.gallery, name='gallery'),
    path('news/', views.news, name='news'),
    path('news/<slug:slug>/', views.news_detail,
         name='news_detail'),  # New URL pattern
    path('sponsors/', views.sponsors, name='sponsors'),
    path('contact/', views.contact, name='contact'),
    path('calendar/', views.calendar, name='calendar'),
]
