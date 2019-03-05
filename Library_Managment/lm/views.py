from django.views import generic
from .models import *
from django.shortcuts import reverse ,render , get_object_or_404
from . import libSetting
from django.http import HttpResponse , HttpResponseRedirect
from django.http.response import Http404
import datetime
from django.core.files.storage import FileSystemStorage


sett = LibrarySettings.load()


class information():
    def __init__(self, issuee, dayLeft):
        self.issue = issuee
        self.dayLeft = dayLeft


def issueThis(request,userpk,bookpk):
    try :
        user = get_object_or_404(Student,pk = userpk)
        book = get_object_or_404(Book, pk=bookpk)
        if book.currently_issued:
            return HttpResponseRedirect(reverse('lm:book',kwargs={'pk':book.pk}))
        if user.bookCount >= (sett.maxBookForStudent if user.is_student else sett.maxBookForFaculty):
            return StudentDetail(request,user.pk,context={'error':'Already Have Books'})
        if not user.exist :
            return StudentDetail(request, user.pk, context={'error': 'User left Colledge'})
        if not book.active:
            return StudentDetail(request, user.pk, context={'error': 'Book is not active'})
    except Http404:
        return HttpResponse(render(request,'lm/error.html',context={'error':"can't issue book problem occured "}))
    else :
        iss = Issue(user = user,book = book ,day = event_day.load() ,is_returned = False )
        days = sett.maxDelayDayStudent if user.is_student else sett.maxDelayDayFaculty
        book.currently_issued = True
        iss.issue_time = datetime.datetime.now()
        iss.return_time = iss.issue_time.date() + datetime.timedelta(days=days)
        user.bookCount += 1
        user.save()
        book.save()
        iss.save()

        sett.total_issued += 1
        sett.save()
        return HttpResponseRedirect(reverse('lm:user',kwargs={'userid':user.pk}))


def issuee(request):
    print(request.POST)
    dic = request.POST
    userpk = -1
    bookpk = -1
    try :
        userpk = dic.get('userpk') if 'userpk' in dic else get_object_or_404(Student,roll=dic.get('userroll')).pk if 'userroll' in dic else -1
        bookpk = dic.get('bookpk') if 'bookpk' in dic else get_object_or_404(Book,barcode=dic.get('barcode')).pk if 'barcode' in dic else get_object_or_404(Book,barcode=dic.get('barcode')).pk if 'barcode' in dic else -1
    except Http404:
        if userpk == -1:
            return HttpResponse(
                render(request, 'lm/error.html', context={'error': 'user does not exist', 'createUser': True}))
        if bookpk == -1:
            return HttpResponse(render(request, 'lm/error.html', context={'error': 'book does not exist', 'createBook': True}))
    else :
        if userpk == -1:
            return HttpResponse(
                render(request, 'lm/error.html', context={'error': 'user does not exist', 'createUser': True}))
        if bookpk == -1:
            return HttpResponse(
                render(request, 'lm/error.html', context={'error': 'book does not exist', 'createBook': True}))
        return issueThis(request, userpk, bookpk)


def returnbook(request,issue_id):
    info = Issue.objects.get(pk = issue_id)
    book = info.book
    user = info.user
    if not info.is_returned:
        context = {'issue': info}
        delayedby = libSetting.daysLeft(info) - libSetting.getday(info.user.is_student)
        if delayedby > 0:
            context['showDate'] = True
            user.payable_amount += delayedby * libSetting.getcost(info.user.is_student)
            user.save()
        info.is_returned = True
        info.return_time = datetime.datetime.now()
        book.currently_issued = False
        user.bookCount -= 1
        if user.bookCount < 0:
            user.bookCount = 0
        user.save()
        info.save()
        book.save()
        sett.total_issued -= 1
        sett.save()
    return HttpResponseRedirect(reverse('lm:user',kwargs={'userid':user.pk}))


def searchBook(request):
    id = request.POST.get('book')
    try :
        book = get_object_or_404(Book,barcode = id)
    except Http404:
        return HttpResponse(render(request,'lm/error.html', context={'error':"book does not exist"}))
    else :
        return HttpResponseRedirect(reverse('lm:book', kwargs={'pk': book.pk}))


def searchUser(request):
    id = request.POST.get('user')
    try :
        user = get_object_or_404(Student,roll = id)
    except Http404:
        return HttpResponse(render(request,'lm/error.html', context={'error': "User does not exist"}))
    else :
        return HttpResponseRedirect(reverse('lm:user', kwargs={'userid': user.pk}))


def StudentDetail(request,userid,context={}):
    try :
        stud = get_object_or_404(Student,pk = userid)
    except Http404:
        #404 error
        pass
    else:

            books = [information(b, libSetting.daysLeft(b)) for b in stud.issue_set.all().filter(is_returned=False)]
            context['books'] = books
            context['student'] = stud
            return render(request,'lm/userDetail.html',context)


def payable(request,userid):
    student = Student.objects.get(pk=userid)
    all=[information(a,libSetting.daysLeft(a)) for a in student.issue_set.all() if a.is_returned and libSetting.daysLeft(a)>libSetting.getday(a.user.is_student) ]
    return HttpResponse(render(request,'lm/payable.html',context={'issuesday':all,'name':student.name,'roll':student.roll}))


def Index(request):
    return HttpResponse(render(request,'lm/index.html',context={'user':False}))


def userForm(request):
    return HttpResponse(render(request,'lm/userForm.html'))


def bookForm(request):
    return HttpResponse(render(request, 'lm/bookForm.html'))

def addUserform(request):
    return HttpResponse(render(request,'lm/userForm.html'))


def addBookform(request):
    return HttpResponse(render(request,'lm/bookForm.html'))


def addUser(request):
    try :
        dic = request.POST
        print(dic)
        name = dic.get('name') if 'name' in dic else ''
        roll = dic.get('roll')
        email = dic.get('email')
        student = False if 'isstudent'in dic and 'off'== dic.get('isstudent')  else True
        active = False if 'isactive'in dic and 'off'== dic.get('isactive')  else True
        exist = False if 'exist'in dic and 'off'== dic.get('exist')  else True

        s=get_object_or_404(Student,roll=roll)
        return StudentDetail(request,userid=s.pk,context={'error':'user already exists'})
    except Http404:
        s = Student(name=name, roll=roll, email=email, is_student=student, is_active=active, exist=exist,bookCount=0, payable_amount=0)
        if request.FILES and request.FILES['image']:
            image = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(str(s.roll), image)
            uploaded_file_url = fs.url(filename)
            s.image_path = uploaded_file_url
        s.save()
        if student:
            sett.total_student += 1
        else:
            sett.total_staff += 1
        return HttpResponseRedirect(reverse('lm:user',kwargs={'userid':s.pk}))
    except :
        return HttpResponse(render(request,'lm/error.html',context={'error':'Cant create Profile'}))



def addBook(request):
    try :
        dic = request.POST
        print(dic)
        barcode = int(dic.get('barcode'))

        classification_number = dic.get('classification_number') if 'classification_number' in dic else 0
        if not classification_number:
            classification_number=0
        active = False if 'isactive'in dic and 'off'== dic.get('isactive')  else True

        s=get_object_or_404(Book,barcode=barcode)
        return HttpResponseRedirect(reverse('lm:book',kwargs={'pk':s.pk}))
    except :
        s = Book(barcode=barcode,classification_number=classification_number)
        s.save()
        sett.total_Books += 1
        sett.save()
        return HttpResponseRedirect(reverse('lm:book',kwargs={'pk':s.pk}))


class PendingBooks(generic.ListView):
    template_name = 'lm/pendingIssue.html'

    def get_queryset(self):
        return Issue.objects.all().filter(is_returned = False)


class PendingFines(generic.ListView):
    template_name = 'lm/pendingFines.html'
    context_object_name = 'pendingIssue'

    def get_queryset(self):
        return [information(b,libSetting.daysLeft(b)) for b in Issue.objects.all().filter(is_returned = True) if libSetting.daysLeft(b) > libSetting.getday(b.user.is_student) ]


def BookDetail(request,pk,context={}):
    try:
        b=get_object_or_404(Book,pk=pk)
    except Http404:
        return HttpResponse(render(request, 'lm/error.html', context={'error': 'Book does not exist'}))
    else:
        context['book'] = b
        return HttpResponse(render(request,'lm/bookDetail.html',context))


def status(request):
    return render(request,'lm/status.html',context={'sett':sett})



def updateStudent(request):
    dic = request.POST
    try :
        print(dic)
        roll = dic.get('roll')
        s=get_object_or_404(Student,pk=roll)
        stud = s.is_student
        name = dic.get('name') if 'name' in dic else ''
        if name:
            s.name = name

        if request.FILES and request.FILES['image']:
            image = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(str(s.roll), image)
            uploaded_file_url = fs.url(filename)
            s.image_path = uploaded_file_url

        email = dic.get('email') if 'email' in dic else ''
        if email:
            s.email = email
        is_student = True if 'isstudent' in dic and 'on'==dic.get('isstudent') else False

        s.is_student = is_student
        is_active = True if 'isactive' in dic and 'on'==dic.get('isactive') else False

        s.is_active = is_active
        s.save()
        if stud and not s.is_student:
            sett.total_student -= 1
            sett.total_staff += 1
            sett.save()
        if not stud and s.is_student:
            sett.total_student += 1
            sett.total_staff -= 1
            sett.save()
        return HttpResponseRedirect(reverse('lm:user', kwargs={'userid': s.pk}))
    except Http404:
        print('exception')
        return HttpResponse(render(request,'lm/error.html',context={'error':'user does not exist'}))

    else :
        return HttpResponse(render(request, 'lm/error.html', context={'error':'Cant update'}))


def updateBook(request):
    dic = request.POST
    try :
        print(dic)
        barcode = dic.get('barcode')
        s=get_object_or_404(Book,pk=barcode)

        if not barcode:
            s.barcode = 0
        classification_number = dic.get('classification_number') if 'classification_number' in dic else 0
        if not classification_number:
            s.classification_number = classification_number
        is_active = True if 'isactive' in dic and 'on'==dic.get('isactive') else False
        s.barcode=barcode
        s.classification_number=classification_number
        s.active = is_active
        s.save()
        return HttpResponseRedirect(reverse('lm:book', kwargs={'pk': s.pk}))
    except Http404:
        print('exception')
        return HttpResponse(render(request,'lm/error.html',context={'error':'book does not exist'}))

    else :
        return HttpResponse(render(request, 'lm/error.html', context={'error':'Cant update'}))


class Users(generic.ListView):
    template_name = 'lm/allUsers.html'

    def get_queryset(self):
        return Student.objects.all()


class Books(generic.ListView):
    template_name = 'lm/allBooks.html'

    def get_queryset(self):
        return Book.objects.all()

