from django.urls import path
from accounts.views import LoginPage,LogoutView

urlpatterns = [
    path('login/',LoginPage.as_view(),name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]