import datetime
from .models import *

sett = LibrarySettings.objects.get(id=1)

def getcost(b):
    if b:
        return sett.revenuePerDayStudent
    else :
        return sett.revenuePerDayFaculty

def getday(b):
    if b:
        return sett.maxDelayDayStudent
    else :
        return sett.maxDelayDayFaculty


def daysLeft(r):
    if r.is_returned:
        d = r.return_time.date() - r.issue_time.date()
        return d.days
    else:
        d = datetime.date.today() - r.issue_time.date()
        return sett.maxDelayDayStudent if r.user.is_student else sett.maxDelayDayFaculty - d.days

