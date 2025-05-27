from datetime import datetime

import cv2

# was used for testing initial implementation of script
debug_schedule_weekdays = [
	"05:56", "06:30", "07:01", "10:33", "11:56", "12:30",
	"13:01", "16:03", "17:56", "18:30", "19:01"
]
debug_schedule_weekends = [
	"05:56", "06:30", "07:01", "11:56", "12:30",
	"13:01", "17:56", "18:30", "19:01"
]


# Gets the list of email notification recipients from .txt file
def get_email_recipient_list(path):
	with open(path, "r") as file:
		emails = file.readlines()
	emails = [e.strip("\n") for e in emails]
	return emails


# Gets the email server API key from .txt file
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


# This doesn't work correctly, see comments:
def get_recording_details(filename):
	video = cv2.VideoCapture(filename)
	duration = video.get(cv2.CAP_PROP_POS_MSEC)  # returns 0.0
	frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)  # gets the total number of frames saved
	video.release()
	return duration, frame_count
