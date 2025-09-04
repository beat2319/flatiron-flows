import datetime as dt
from dateutil import tz
import pytz 
import time

date_str = '250822033804'
date_format = '%y%m%d%H%M%S'

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/Denver')

# utc =  datetime.strptime(date_str, date_format)

# utc = utc.replace(tzinfo=from_zone)

# mountain = utc.astimezone(to_zone)

# mountain_2 = utc.dt.tz_localize('UTC').dt.tz_convert('America/Denver')
print(dt.datetime.now())
# print(mountain_2)



