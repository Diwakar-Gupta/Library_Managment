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
            return HttpResponse(render('lm/error.html',context={'error':'book is already issued'}))
    except Http404:
        #404 book not found
        pass
    else :
        iss = Issue(user = user,book = book ,is_returned = False ,issue_time=datetime.datetime.now())
        days = sett.maxDelayDayStudent if user.is_student else sett.maxDelayDayFaculty
        iss.return_time = iss.issue_time.date()+datetime.timedelta(days = days)
        book.currently_issued = True
        book.user = user
        book.save()
        iss.save()
        return HttpResponseRedirect(reverse('lm:user',kwargs={'userid':user.pk}))



def issuee(request):
    print(request.POST)
    userpk = request.POST.get('userpk') if 'userpk' in request.POST else  request.POST.get('userroll').pk
    bookpk= request.POST.get('bookpk') if 'bookpk' in request.POST else  request.POST.get('identity') if 'identity' in request.POST else Book.objects.get(barcode = request.POST.get('barcode')).pk
    return issueThis(request,userpk,bookpk)



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
    book.user = None
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


def StudentDetail(request,userid):
    try :
        stud = get_object_or_404(Student,pk = userid)
    except Http404:
        #404 error
        pass
    else:
        try:
            books = [information(b, libSetting.daysLeft(b)) for b in stud.Issue_set.all().filter(is_returned=False)]
        except AttributeError:
            return render(request, 'lm/userDetail.html', context={'student': stud, 'books': []})
        else :
            return render(request,'lm/userDetail.html',context={'student':stud,'books':books})


def payable(request,userid):
    student = Student.objects.get(pk=userid)
    all=[information(a,libSetting.daysLeft(a)) for a in student.Issue_set.all() if a.is_returned and libSetting.daysLeft(a)>libSetting.getday(a.user.is_student) ]
    return render(request,'lm/payable.html',context={'issuesday':all,'name':student.name,'roll':student.roll})



class IndexView(generic.ListView):
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

class updateBook(generic.UpdateView):
    model = Book
    fields = ['barcode','classification_number']

