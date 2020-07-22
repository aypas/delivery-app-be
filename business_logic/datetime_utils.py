from datetime import datetime, timezone, timedelta
from django.utils.timezone import make_aware

def make_datetime_object(convert):
	return make_aware(datetime.strptime(convert.replace('T', ' ')[:-1], "%Y-%m-%d %H:%M:%S.%f"))
