from django.db import models
from django.shortcuts import reverse
import datetime


class event_year(models.Model):
    year = models.IntegerField(primary_key=True)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(year=datetime.date.today().year)
        return obj


class event_month(models.Model):
    month = models.IntegerField(primary_key=True)
    year = models.ForeignKey(event_year, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.month)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(month=datetime.date.today().month,year = event_year.load())
        return obj


class event_day(models.Model):
    day = models.IntegerField(primary_key=True)
    month = models.ForeignKey(event_month, on_delete=models.CASCADE)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(day=datetime.date.today().day,month=event_month.load())
        return obj


class LibrarySettings(models.Model):
    maxDelayDayStudent = models.IntegerField(default=14)
    maxDelayDayFaculty = models.IntegerField(default=182)
    revenuePerDayStudent = models.IntegerField(default=10)
    revenuePerDayFaculty = models.IntegerField(default=10)
    total_Books = models.IntegerField(default=0,editable=True)
    total_student = models.IntegerField(default=000,editable=True)
    total_staff = models.IntegerField(default=000,editable=True)
    maxBookForStudent = models.IntegerField(default=2)
    maxBookForFaculty = models.IntegerField(default=3)
    total_issued = models.IntegerField(default=0,editable=True)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Student(models.Model):
    name = models.CharField(max_length=30,default=' ',editable=True)
    roll = models.IntegerField(editable=True,primary_key=True)
    image_path = models.ImageField(default='../static/lm/anon.png',editable=True)
    email = models.EmailField(blank=True,editable=True)
    payable_amount = models.IntegerField(default=0,editable=True)
    is_student = models.BooleanField(default=True,editable=True)
    is_active = models.BooleanField(default=True,null=False,editable=True)
    exist = models.BooleanField(default=True)
    bookCount = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse('lm:user', kwargs={'userid': self.pk})


class Book(models.Model):
    barcode = models.IntegerField(default=0,primary_key=True,editable=True,)
    classification_number = models.IntegerField(default=0,null=True,blank=True,editable=True)
    currently_issued = models.BooleanField(default=False,editable=True,null=False,blank=False)
    active = models.BooleanField(default=True,editable=True)

    def get_absolute_url(self):
        return reverse('lm:book', kwargs={'pk': self.pk})


class Issue(models.Model):
    user = models.ForeignKey(Student,on_delete=models.CASCADE,null=True)
    book = models.ForeignKey(Book,on_delete=models.CASCADE,null=True,)
    day = models.ForeignKey(event_day,on_delete=models.CASCADE,null=True)
    issue_time = models.DateTimeField(auto_now_add=True,blank=True,editable=True)
    is_returned = models.BooleanField(default=False,editable=True)
    return_time = models.DateTimeField(auto_now_add=False,blank=True,editable=True,null=True)
    paid = models.BooleanField(default=False,editable=True)
    is_late = models.BooleanField(default=False,editable=True)
    mailSend = models.BooleanField(default=False)


