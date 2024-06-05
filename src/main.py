import atexit
import logging
import logging.handlers
import os
import sys
import time
import traceback
from datetime import datetime, timedelta, date

import cv2
import numpy as np
import schedule

import helper


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

	# Initialize routine variables
	img_counter = 0
	fail_counter = 0
	current_date_str = str(date.today()).replace("-", "_")
	current_hour_str = helper.get_current_hour_str()
	video_fourcc = cv2.VideoWriter.fourcc(*'mp4v')
	base_img_filename = "{}/{}_{}_snapshot".format(current_dir, current_date_str, current_hour_str)
	vid_filename = "{}/{}_{}_video.mp4".format(current_dir, current_date_str, current_hour_str)
	photo_interval = np.floor((video_duration / (photos_per_block + 1)) + photos_per_block)

	# Initialize connection to camera and video writer
	cam = cv2.VideoCapture(camera_url)
	video_dims = (int(cam.get(3)), int(cam.get(4)))
	video_out = cv2.VideoWriter(vid_filename, video_fourcc, video_fps, video_dims)

	# Check if camera is operational
	if not cam.isOpened():
		log("camera not open, cannot extract feed, exiting routine", logging.ERROR)
		return

	log("starting recording")

	# Set up video and photo timing
	next_photo_time = datetime.now() + timedelta(seconds=photo_interval)
	end_time = datetime.now() + timedelta(seconds=video_duration)

	while datetime.now() < end_time:
		# Grab frame from camera
		success, frame = cam.read()
		if not success:
			log("failed to grab frame from camera feed", logging.WARNING)
			fail_counter += 1
		# Write the frame to video file
		video_out.write(frame)
		# Save snapshot of current frame
		if datetime.now() >= next_photo_time:
			img_name = "{}_{}.png".format(base_img_filename, img_counter + 1)
			cv2.imwrite(img_name, frame)
			log("snapshot taken, saved as \"{}\"".format(img_name))
			next_photo_time = datetime.now() + timedelta(seconds=photo_interval)
			img_counter += 1

	log("recording complete")

	# Check if any errors occurred and notify if necessary
	if img_counter == 0:
		log("failed to capture any images during this block", logging.ERROR)
	if fail_counter > 0:
		log("failed to grab frame {} times during routine".format(fail_counter), logging.ERROR)

	# Release resources
	cam.release()
	video_out.release()
	log("capture routine has concluded")


def exit_handler():  # Can only be called via a SystemExit
	log("exiting script...\n##################################################")


# TODO:
#   - implement rotating log files (or just a way to keep logs from getting too long)
#   - determine camera startup and shutdown time for more accurate scheduling
#   - find more error scenarios

if __name__ == '__main__':

	# Script Configuration
	verbose = True  # controls whether log msgs are printed to console (debugging)
	send_emails = True  # controls whether notification emails are sent in specific situations
	video_duration = 62  # seconds during which the video is being recorded (default is 60 sec)
	photos_per_block = 3  # number of photos taken during capture routine (default is 3 photos)
	video_fps = 25  # fps of saved video recording (matches fps of camera feed)
	data_dir = "/mnt/storage_1/PdM5g"  # base data location
	current_dir = ""  # global variable for where img files are currently being saved
	log_path = "./capture_log.log"  # log file name and location
	api_key_path = "./../email_api_key.txt"  # location of file containing email server api key
	email_list_path = "./../email_list.txt"  # location of file containing recipient emails for notifications

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
	for t in schedule_times:
		schedule.every().day.at(t).do(capture_routine)

	# Set up exit handler
	atexit.register(exit_handler)

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
		api_key = helper.get_smtp_api_key(api_key_path)
		recipients = helper.get_email_recipient_list(email_list_path)
		email_handler = logging.handlers.SMTPHandler(
			mailhost=("smtp.sendgrid.net", 587),
			fromaddr=recipients[0],
			toaddrs=recipients,
			subject="[ALERT] 5G Camera Capture Script",
			credentials=("apikey", api_key),
			secure=()
		)
		email_handler.setFormatter(log_formatter)
		email_handler.setLevel(logging.ERROR)
		logging.getLogger().addHandler(email_handler)

	# Begin script
	log("starting script...")
	summary_str = "script variables:"
	summary_str = summary_str + "\n\tverbose = {}".format(verbose)
	summary_str = summary_str + "\n\tsend_emails = {}".format(send_emails)
	summary_str = summary_str + "\n\tvideo_duration = {} sec".format(video_duration)
	summary_str = summary_str + "\n\tphotos_per_block = {}".format(photos_per_block)
	summary_str = summary_str + "\n\tvideo_fps = {}".format(video_fps)
	summary_str = summary_str + "\n\tdata_directory = \"{}\"".format(data_dir)
	summary_str = summary_str + "\n\tlog_path = \"{}\"".format(log_path)
	summary_str = summary_str + "\n\tapi_key_path = \"{}\"".format(api_key_path)
	summary_str = summary_str + "\n\temail_list_path = \"{}\"".format(email_list_path)
	summary_str = summary_str + "\n\tcamera_url = \"{}\"".format(camera_url)
	summary_str = summary_str + "\n\tnum_of_scheduled_jobs = {}".format(len(schedule.jobs))
	log(summary_str)

	while True:
		try:
			schedule.run_pending()
			time.sleep(1)
		except KeyboardInterrupt:  # avoids notification if script is manually terminated
			log("user shut down script with \"ctrl + c\" command")
			sys.exit(0)
		except BaseException as e:  # sends notification if script terminated due to any other exception
			log("script failure due to exception:\n{}".format(traceback.format_exc()), logging.CRITICAL)
			sys.exit(1)
