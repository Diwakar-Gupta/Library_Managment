from django.db import models
from django.shortcuts import reverse


class LibrarySettings(models.Model):
    maxDelayDayStudent = models.IntegerField(default=14)
    maxDelayDayFaculty = models.IntegerField(default=182)
    revenuePerDayStudent = models.IntegerField(default=10)
    revenuePerDayFaculty = models.IntegerField(default=10)
    total_Books = models.IntegerField(default=1000,editable=True)
    total_student = models.IntegerField(default=1000,editable=True)
    total_staff = models.IntegerField(default=1000,editable=True)
    maxBookForStudent = models.IntegerField(default=2)
    maxBookForFaculty = models.IntegerField(default=3)


class Student(models.Model):
    name = models.CharField(max_length=30,default=' ',editable=True)
    roll = models.IntegerField(editable=False,primary_key=True)
    image_path = models.ImageField(default='../static/lm/anon.png',editable=True)
    mobile_number = models.IntegerField(default=0000000000,editable=True)
    payable_amount = models.IntegerField(default=0,editable=True)
    is_student = models.BooleanField(default=True,editable=True)
    is_active = models.BooleanField(default=True,null=False,editable=True)
    exist = models.BooleanField(default=True)
    bookCount = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse('lm:user', kwargs={'userid': self.pk})


class Book(models.Model):
    identity = models.IntegerField(primary_key=True,editable=False)
    barcode = models.IntegerField(default=0,blank=True,null=True,editable=True)
    classification_number = models.IntegerField(default=0,null=True,blank=True,editable=True)
    currently_issued = models.BooleanField(default=False,editable=True,null=False,blank=False)
    active = models.BooleanField(default=True,editable=True)

    def get_absolute_url(self):
        return reverse('lm:book', kwargs={'pk': self.id})



class Issue(models.Model):
    user = models.ForeignKey(Student,on_delete=models.DO_NOTHING)
    book = models.ForeignKey(Book,on_delete=models.DO_NOTHING)
    issue_time = models.DateTimeField(auto_now_add=True,blank=True,editable=True)
    is_returned = models.BooleanField(default=False,editable=True)
    return_time = models.DateTimeField(auto_now_add=False,blank=True,editable=True,null=True)
    mailSend = models.BooleanField(default=False)
