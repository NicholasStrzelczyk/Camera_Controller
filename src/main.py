import atexit
import logging
import logging.handlers
import os
import sys
import time
from datetime import datetime, timedelta, date

import cv2
import numpy as np
import schedule

from src import helper


def log(msg, level=logging.INFO):
	logging.log(level, msg)


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
	global camera_url, current_dir, video_duration, photos_per_block, video_fps
	log("starting capture routine")
	setup_directories()

	# Initialize variables
	img_counter = 0
	fail_counter = 0
	max_failures = 10
	current_date_str = str(date.today()).replace("-", "_")
	current_hour_str = helper.get_current_hour_str()
	video_fourcc = cv2.VideoWriter.fourcc(*'mp4v')
	base_img_filename = "{}/{}_{}_snapshot".format(current_dir, current_date_str, current_hour_str)
	vid_filename = "{}/{}_{}_video.mp4".format(current_dir, current_date_str, current_hour_str)
	photo_interval = np.floor((video_duration * 60) / (photos_per_block + 1)) + (video_duration * photos_per_block)
	end_time = datetime.now() + timedelta(minutes=video_duration)
	next_photo_time = datetime.now() + timedelta(seconds=photo_interval)

	# Initialize connection to camera
	log("initializing rtsp camera device")
	cam = cv2.VideoCapture(camera_url)
	video_dims = (int(cam.get(3)), int(cam.get(4)))
	video_out = cv2.VideoWriter(vid_filename, video_fourcc, video_fps, video_dims)

	# Check if camera is operational
	if not cam.isOpened():
		log("camera not open, cannot extract feed, exiting routine", logging.ERROR)
		return

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
		# Stop conditions
		if img_counter == photos_per_block or datetime.now() >= end_time:
			log("stop condition met, concluding capture routine")
			break

		# Write the frame to video file
		video_out.write(frame)
		# Save snapshot of current frame
		if datetime.now() >= next_photo_time:
			img_name = "{}_{}.png".format(base_img_filename, img_counter + 1)
			cv2.imwrite(img_name, frame)
			log("snapshot taken, saved as \"{}\"".format(img_name))
			next_photo_time = datetime.now() + timedelta(seconds=photo_interval)
			img_counter += 1

	# Release resources
	log("closing connection to camera")
	cam.release()
	video_out.release()
	log("capture routine has concluded")


def exit_handler():
	log("ending script...\n##################################################", logging.FATAL)
	return


if __name__ == '__main__':

	# Script Configuration
	verbose = True  # controls whether log msgs are printed to console (debugging)
	send_emails = False  # controls whether notification emails are sent in specific situations
	video_duration = 1  # minutes during which the video is being recorded (1 minute)
	photos_per_block = 3  # number of photos taken during capture routine (3 photos)
	video_fps = 25  # fps of saved video recording (matches fps of camera feed)
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
	schedule_times = [  # ranges from 6am to 8pm
		"06:00", "07:00", "08:00", "09:00", "10:00",
		"11:00", "12:00", "13:00", "14:00", "15:00",
		"16:00", "17:00", "18:00", "19:00", "20:00"
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
		email_credentials = helper.get_email_credentials(email_creds_path)
		email_handler = logging.handlers.SMTPHandler(
			mailhost=("smtp.mail.yahoo.com", 587),
			fromaddr=email_credentials[0],
			toaddrs=helper.get_email_recipient_list(email_list_path)[0],
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
	summary_str = summary_str + "\n\tverbose = {}".format(verbose)
	summary_str = summary_str + "\n\tsend_emails = {}".format(send_emails)
	summary_str = summary_str + "\n\tlive_duration = {} min".format(video_duration)
	summary_str = summary_str + "\n\tphotos_per_block = {}".format(photos_per_block)
	summary_str = summary_str + "\n\tvideo_fps = {}".format(video_fps)
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
	# creds = get_email_credentials(email_creds_path)
	# recipient = get_email_recipient_list(email_list_path)[0]
	# with smtplib.SMTP_SSL("smtp.mail.yahoo.com", port=465) as connection:
	# 	connection.set_debuglevel(1)
	# 	connection.login(
	# 		user=creds[0],
	# 		password=creds[1]
	# 	)
	# 	connection.sendmail(
	# 		from_addr=creds[0],
	# 		to_addrs=recipient,
	# 		msg=f"Subject:Text\n\n"
	# 		    f"Body of the text"
	# 	)
	##########################################################################
	##########################################################################
	##########################################################################

	while True:
		schedule.run_pending()
		time.sleep(1)
