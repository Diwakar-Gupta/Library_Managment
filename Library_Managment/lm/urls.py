from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name='lm'
urlpatterns = [
    path('',views.Index,name ='index'),

    path('user/<int:userid>', views.StudentDetail, name='user'),
    path('book/<int:pk>', views.BookDetail, name='book'),

    path('payable/<int:userid>', views.payable, name='payable'),
    path('pendingBooks/',views.PendingBooks.as_view(),name='pendingbooks'),
    path('pendingFines/',views.PendingFines.as_view(),name='pendingfines'),

    path('searchBook', views.searchBook, name='searchbook'),
    path('searchUser', views.searchUser, name='searchuser'),

    path('issuebook/', views.issuee, name='issue'),
    path('return/<int:issue_id>', views.returnbook, name='return'),

    path('Bookform',views.addUserform,name='bookform'),
    path('Userform',views.addBookform,name='userform'),

    path('addUser',views.addUser,name='adduser'),
    path('addBook',views.addBook,name='addbook'),

    path('Create/user',views.userForm,name='createuser'),
    path('Create/book',views.bookForm,name='createbook'),

    path('update/user/',views.updateStudent,name='updateuser'),
    path('update/book/',views.updateBook,name='updatebook'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

