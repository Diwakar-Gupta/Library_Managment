from django.views import generic
from .models import Student , Book , Issue , LibrarySettings
from django.shortcuts import reverse ,render , get_object_or_404
from . import libSetting
from django.http import HttpResponse , HttpResponseRedirect
from django.http.response import Http404
import datetime


sett = LibrarySettings.objects.all()[0]


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
        if user.bookCount >= sett.maxBookForStudent if user.is_student else sett.maxBookForFaculty:
            return StudentDetail(request,user.pk,context={'error':'Already Have Books'})
        if not user.exist :
            return StudentDetail(request, user.pk, context={'error': 'User left Colledge'})
    except Http404:
        return HttpResponse(render(request,'lm/error.html',context={'error':"can't issue book problem occured "}))
    else :
        iss = Issue(user = user,book = book ,is_returned = False ,issue_time=datetime.datetime.now())
        days = sett.maxDelayDayStudent if user.is_student else sett.maxDelayDayFaculty
        iss.return_time = iss.issue_time.date()+datetime.timedelta(days = days)
        book.currently_issued = True
        user.bookCount += 1
        user.save()
        book.save()
        iss.save()
        return HttpResponseRedirect(reverse('lm:user',kwargs={'userid':user.pk}))


def issuee(request):
    print(request.POST)
    dic = request.POST
    userpk = -1
    bookpk = -1
    try :
        userpk = dic.get('userpk') if 'userpk' in dic else get_object_or_404(Student,roll=dic.get('userroll')).pk if 'userroll' in dic else -1
        bookpk = dic.get('bookpk') if 'bookpk' in dic else get_object_or_404(Book,identity=dic.get('identity')).pk if 'identity' in dic else get_object_or_404(Book,barcode=dic.get('barcode')).pk if 'barcode' in dic else -1
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
    context = {'issue':info}
    delayedby = libSetting.daysLeft(info) - libSetting.getday(info.user.is_student)
    if delayedby > 0:
        context['showDate'] = True
        user.payable_amount += delayedby*libSetting.getcost(info.user.is_student)
        user.save()
    info.is_returned = True
    info.return_time = datetime.datetime.now()
    book.currently_issued = False
    user.bookCount -= 1
    if user.bookCount <0:
        user.bookCount = 0
    user.save()
    info.save()
    book.save()
    return HttpResponseRedirect(reverse('lm:user',kwargs={'userid':user.pk}))


def searchBook(request):
    id = request.POST.get('book')
    try :
        book = get_object_or_404(Book,identity = id)
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
    all=[information(a,libSetting.daysLeft(a)) for a in student.Issue_set.all() if a.is_returned and libSetting.daysLeft(a)>libSetting.getday(a.user.is_student) ]
    return render(request,'lm/payable.html',context={'issuesday':all,'name':student.name,'roll':student.roll})


def Index(request):
    return HttpResponse(render(request,'lm/Form.html',context={'user':True}))


def profileForm(request,who):
    user = True if who else False

    return HttpResponse(render(request,'lm/Form.html',context={'user':user}))


def addUser(request):
    try :
        dic = request.POST
        name = dic.get('name') if 'name' in dic else ''
        roll = dic.get('roll')
        email = dic.get('email')
        image = dic.get('image') if 'image' in dic else '../static/lm/anon.png'
        student = False if 'isstudent'in dic and 'off'== dic.get('isstudent')  else True
        active = False if 'inactive'in dic and 'off'== dic.get('inactive')  else True
        exist = False if 'exist'in dic and 'off'== dic.get('exist')  else True

        s=get_object_or_404(Student,roll=roll)
        return StudentDetail(request,userid=s.pk,context={'error':'user already exists'})
    except Http404:
        s = Student(name=name, roll=roll, image_path=image,email=email, is_student=student, is_active=active, exist=exist,
                    bookCount=0, payable_amount=0)
        s.save()
        return HttpResponseRedirect(reverse('lm:user',kwargs={'userid':s.pk}))
    except :
        return HttpResponse(render(request,'lm/error.html',context={'error':'Cant create Profile'}))



def addBook(request):
    try :
        dic = request.POST

        identity = dic.get('identity')
        barcode = dic.get('barcode') if 'barcode' in dic else 0
        classification_number = dic.get('classification_number') if 'classification_number' in dic else 0
        active = dic.get('isactive') if 'isactive' in dic else True

        s=get_object_or_404(Book,identity=identity)
        return HttpResponseRedirect(reverse('lm:book',kwargs={'pk':s.pk}))
    except Http404:
        s = Student(identity=identity,barcode=barcode,classification_number=classification_number, is_active=active)
        s.save()
        return HttpResponseRedirect(reverse('lm:book',kwargs={'pk':s.pk}))
    except :
        return HttpResponse(render(request,'lm/error.html',context={'error':'Cant create Book Profile'}))


class PendingBooks(generic.ListView):
    context_object_name = 'pendingIssue'

    def get_queryset(self):
        return Issue.objects.all().filter(is_returned = False)


class PendingFines(generic.ListView):
    template_name = 'lm/pendingFines.html'
    context_object_name = 'pendingIssue'

    def get_queryset(self):
        return [information(b,libSetting.daysLeft(b)) for b in Issue.objects.all().filter(is_returned = True) if libSetting.daysLeft(b) > libSetting.getday(b.user.is_student) ]


class BookDetail(generic.DetailView):
    model = Book
    template_name = 'lm/bookDetail.html'


def updateStudent(request):
    return HttpResponseRedirect(reverse('lm:user',kwargs={'userid':request.POST.get('roll')}))


def updateBook(request):
    return HttpResponseRedirect(reverse('lm:book',kwargs={'pk':request.POST.get('pk')}))

class updateBook(generic.UpdateView):
    model = Book
    fields = ['barcode','classification_number']

