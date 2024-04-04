from django.urls import path
from access_management.views import IndexPage, ConnectToDatabase,GivenAccess,ConfirmationLetter,CloseAccessManually,ClosedAccess,GiveTwoDBAccess
urlpatterns = [
    path('index_page/',IndexPage.as_view(),name='index_page'),
    path('Connect_to_db/',ConnectToDatabase.as_view(),name='Connect_to_db'),
    path('Given_access/',GivenAccess.as_view(),name='Given_access'),
    path('ConfirmationLetter/<str:pk>/',ConfirmationLetter.as_view(),name='ConfirmationLetter'),
    path('CloseManually/',CloseAccessManually.as_view(),name='CloseManually'),
    path('ClosedAccess/',ClosedAccess.as_view(),name='ClosedAccess'),
    path('GiveTwoDBAccess/',GiveTwoDBAccess.as_view(),name='GiveTwoDBAccess')
    
]