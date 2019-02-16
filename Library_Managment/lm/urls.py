from django.urls import path
from . import views

app_name='lm'
urlpatterns = [
    path('',views.IndexView.as_view(),name ='index'),

    path('user/<int:userid>', views.StudentDetail, name='user'),
    path('book/<int:pk>', views.BookDetail.as_view(), name='book'),

    path('payable/<int:userid>', views.payable, name='payable'),
    path('pendingFines/',views.PendingFines.as_view(),name='pendingfines'),

    path('searchBook', views.searchBook, name='searchbook'),
    path('searchUser', views.searchUser, name='searchuser'),

    path('issuebook/', views.issuee, name='issue'),
    path('return/<int:issue_id>', views.returnbook, name='return'),

    path('update/user/',views.updateStudent,name='updateuser'),
    path('update/book/<int:pk>',views.updateBook.as_view(),name='updatebook'),
]
