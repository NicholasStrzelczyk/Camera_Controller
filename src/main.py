import atexit
import logging
import logging.handlers
import os
import smtplib
import sys
from datetime import datetime, timedelta, date

import cv2
import numpy as np
import schedule


def get_email_recipient_list(path):
	with open(path, "r") as file:
		emails = file.readlines()
	emails = [e.strip("\n") for e in emails]
	print(emails)  # debugging
	return emails


def get_email_credentials(path):
	with open(path, "r") as file:
		creds = file.readlines()
	creds = [c.strip("\n") for c in creds]
	print(creds)  # debugging
	return creds[0], creds[1]


def log(msg, level=logging.INFO):
	logging.log(level, msg)


def get_current_hour_str():
	current_hour = datetime.today().hour
	if current_hour == 12:
		result = "{}pm".format(current_hour)
	elif current_hour > 12:
		result = "{}pm".format(current_hour - 12)
	else:
		result = "{}am".format(current_hour)
	return result


def setup_directories():
	global data_dir, current_dir

	# Determine the date and construct path string
	today = date.today()
	new_path = "{}/{}/{}/{}".format(data_dir, today.year, today.month, today.day)

	# Check if the constructed path exists and create it if false
	if not os.path.exists(new_path):
		log("creating new directory for {}".format(today))
		os.makedirs(new_path)
	else:
		log("directory already exists for {}".format(today))

	# Set global variable and log changes
	current_dir = new_path
	log("current file directory set as \"{}\"".format(current_dir))


def capture_routine():
	global use_webcam, show_window, camera_url, current_dir, live_duration, photo_interval
	log("starting capture routine")

	# Check if directories have been made
	setup_directories()

	# Initialize connection
	cam = cv2.VideoCapture(0)
	if not use_webcam:
		cam = cv2.VideoCapture(camera_url)
		log("initializing rtsp camera device")
	else:
		log("initializing default camera (webcam) device")

	# Check if camera is operational
	if not cam.isOpened():
		log("camera not open, cannot extract feed, exiting routine", logging.ERROR)
		return

	# Initialize naming variables
	cam_window_name = "rtsp camera feed"
	current_date_str = str(date.today()).replace("-", "_")
	current_hour_str = get_current_hour_str()
	base_filename = "{}/{}_{}_snapshot".format(current_dir, current_date_str, current_hour_str)

	# Set up stop condition & timing variables
	img_counter = 0
	fail_counter = 0
	max_failures = 10
	max_images = np.floor((live_duration * 60) / photo_interval)
	end_time = datetime.now() + timedelta(minutes=live_duration)
	next_photo_time = datetime.now() + timedelta(seconds=photo_interval)

	while True:
		# Grab frame from camera
		success, frame = cam.read()
		if not success:
			log("failed to grab frame from camera feed", logging.WARNING)
			fail_counter += 1

		# End routine if too many failures
		if fail_counter >= max_failures:
			log("exceeded maximum number of failures to grab frame, exiting capture routine", logging.ERROR)
			break

		# Show current feed if show_window is True
		if show_window:
			cv2.imshow(cam_window_name, frame)

		# Save snapshot of current frame
		if datetime.now() >= next_photo_time:
			img_name = "{}_{}.png".format(base_filename, img_counter + 1)
			cv2.imwrite(img_name, frame)
			log("snapshot taken, saved as \"{}\"".format(img_name))
			next_photo_time = datetime.now() + timedelta(seconds=photo_interval)
			img_counter += 1

		# Stop conditions
		if img_counter == max_images or datetime.now() >= end_time:
			log("stop condition met, concluding capture routine")
			break

		# Wait interval until loop is repeated (100ms = ~ 10fps)
		cv2.waitKey(100)

	# Summarize Results
	log("captured {} images during {} block".format(img_counter, current_hour_str))

	# Garbage collection
	log("closing connection to camera")
	cam.release()
	cv2.waitKey(1000)
	cv2.destroyAllWindows()
	cv2.waitKey(5000)
	log("capture routine has concluded")


def exit_handler():
	log("ending script...\n##################################################", logging.FATAL)
	return


if __name__ == '__main__':

	# Script Configuration
	use_webcam = False  # controls whether webcam is used instead of 5G camera (debugging)
	show_window = False  # controls whether live stream is shown during capture routine (debugging)
	verbose = True  # controls whether log msgs are printed to console (debugging)
	send_emails = False  # controls whether notification emails are sent in specific situations
	live_duration = 3  # minutes during which the camera is live (5 minutes)
	photo_interval = 50  # seconds between each photograph during a live block (90 seconds)
	data_dir = "./data"  # base img file location
	current_dir = ""  # global variable for where img files are currently being saved
	log_path = "./capture_log.log"  # log file name and location
	email_creds_path = "./../email_creds.txt"  # location of file containing email credentials
	email_list_path = "./../email_list.txt"  # location of file containing recipient emails for notifications
	atexit.register(exit_handler)  # runs a routine to notify us if the script exits

	# Camera Connection Configuration
	ip_address = "174.90.198.126"
	rtsp_port = "554"
	camera_url = "rtsp://{}:{}/main".format(ip_address, rtsp_port)

	# Schedule Configuration
	schedule_times = [
		"06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
		"12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"
	]
	schedule_times_debug = [  # for testing the script
		"05:56", "06:30", "07:01", "10:33", "11:56", "12:30",
		"13:01", "16:03", "17:56", "18:30", "19:01"
	]
	for t in schedule_times_debug:
		schedule.every().day.at(t).do(capture_routine)
	# schedule.every(90).seconds.do(capture_routine)  # for local debugging

	# Log initialization
	logging.getLogger().setLevel(logging.INFO)
	logging.captureWarnings(True)
	log_formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] - %(message)s", datefmt="%d-%b-%y %H:%M:%S")

	# Log file handler initialization
	file_handler = logging.FileHandler(log_path)
	file_handler.setFormatter(log_formatter)
	logging.getLogger().addHandler(file_handler)

	# Optional log console handler initialization
	if verbose:
		console_handler = logging.StreamHandler(sys.stdout)
		console_handler.setFormatter(log_formatter)
		logging.getLogger().addHandler(console_handler)

	# Optional log email handler initialization
	if send_emails:
		email_credentials = get_email_credentials(email_creds_path)
		email_handler = logging.handlers.SMTPHandler(
			mailhost=("smtp.mail.yahoo.com", 587),
			fromaddr=email_credentials[0],
			toaddrs=get_email_recipient_list(email_list_path)[0],
			subject="Cooling Tower Capture Script Alert",
			credentials=email_credentials,
			secure=()
		)
		email_handler.setFormatter(log_formatter)
		email_handler.setLevel(logging.ERROR)
		logging.getLogger().addHandler(email_handler)

	# Begin script
	log("starting script...", logging.CRITICAL)
	summary_str = "script variables:"
	summary_str = summary_str + "\n\tuse_webcam = {}".format(use_webcam)
	summary_str = summary_str + "\n\tshow_window = {}".format(show_window)
	summary_str = summary_str + "\n\tverbose = {}".format(verbose)
	summary_str = summary_str + "\n\tsend_emails = {}".format(send_emails)
	summary_str = summary_str + "\n\tlive_duration = {} minutes".format(live_duration)
	summary_str = summary_str + "\n\tphoto_interval = {} seconds".format(photo_interval)
	summary_str = summary_str + "\n\tdata_directory = \"{}\"".format(data_dir)
	summary_str = summary_str + "\n\tlog_path = \"{}\"".format(log_path)
	summary_str = summary_str + "\n\temail_creds_path = \"{}\"".format(email_creds_path)
	summary_str = summary_str + "\n\temail_list_path = \"{}\"".format(email_list_path)
	summary_str = summary_str + "\n\tcamera_url = \"{}\"".format(camera_url)
	summary_str = summary_str + "\n\tnum_of_scheduled_jobs = {}".format(len(schedule.jobs))
	log(summary_str)

	##########################################################################
	##########################################################################
	##########################################################################
	creds = get_email_credentials(email_creds_path)
	recipient = get_email_recipient_list(email_list_path)[0]
	with smtplib.SMTP_SSL("smtp.mail.yahoo.com", port=465) as connection:
		connection.set_debuglevel(1)
		connection.login(
			user=creds[0],
			password=creds[1]
		)
		connection.sendmail(
			from_addr=creds[0],
			to_addrs=recipient,
			msg=f"Subject:Text\n\n"
			    f"Body of the text"
		)
##########################################################################
##########################################################################
##########################################################################

# while True:
# 	schedule.run_pending()
# 	time.sleep(1)
