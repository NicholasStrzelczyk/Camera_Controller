from datetime import datetime

import cv2

debug_schedule_weekdays = [
	"05:56", "06:30", "07:01", "10:33", "11:56", "12:30",
	"13:01", "16:03", "17:56", "18:30", "19:01"
]
debug_schedule_weekends = [
	"05:56", "06:30", "07:01", "11:56", "12:30",
	"13:01", "17:56", "18:30", "19:01"
]


def get_email_recipient_list(path):
	with open(path, "r") as file:
		emails = file.readlines()
	emails = [e.strip("\n") for e in emails]
	return emails


def get_smtp_api_key(path):
	with open(path, "r") as file:
		key = file.readline()
	return key


def get_current_hour_str():
	current_hour = datetime.today().hour
	if current_hour == 12:
		result = "{}pm".format(current_hour)
	elif current_hour > 12:
		result = "{}pm".format(current_hour - 12)
	else:
		result = "{}am".format(current_hour)
	return result


def get_recording_details(filename):
	video = cv2.VideoCapture(filename)
	duration = video.get(cv2.CAP_PROP_POS_MSEC)
	frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
	video.release()
	return duration, frame_count
