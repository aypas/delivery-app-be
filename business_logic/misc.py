from django.utils.timezone import now, make_aware, is_aware
import pytz
import datetime

class timezone:
    """
    Return the current date in the given timezone :param:`tz`.
    """
    def __init__(self, tz='US/Eastern'):
        self.tz = pytz.timezone(tz)
        #pytz.timezone

    def date_today(self):
       return now().astimezone(self.tz).date()

    def date_time_now(self):
   	    return now().astimezone(self.tz)   

    def date_today_delta(self, delta):
        return self.date_today()-datetime.timedelta(delta)

    def date_today_aware(self):
       #return make_aware(datetime.datetime.combine(now().date(),datetime.time(4))).astimezone(self.tz)
       return make_aware(datetime.datetime.combine(datetime.datetime.today().astimezone(self.tz),datetime.time(0)))