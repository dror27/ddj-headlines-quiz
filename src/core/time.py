# time stuff


import datetime

def midnight():
	return datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())