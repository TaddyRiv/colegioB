from django.urls import path
from .auth_views import LoginView,RegisterView
from .auth_views import TutorListView
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('tutores/', TutorListView.as_view(), name='tutor-list'),
    path('register/', RegisterView.as_view(), name='register'),
]
