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
	# Set global variable and log changes
	current_dir = new_path
	log("current file directory set as \"{}\"".format(current_dir))


def capture_routine():
	global camera_url, current_dir, capture_duration, photos_per_block
	log("starting capture routine")
	setup_directories()

	# Initialize routine variables
	img_counter = 0
	fail_counter = 0
	now = datetime.now()
	timestamp_str = now.strftime("%Y%m%d_%H") # Format the date and time into YYYYMMDD_HH
	base_img_filename = "{}/{}00_snapshot".format(current_dir, timestamp_str)
	photo_interval = np.floor((capture_duration / (photos_per_block + 1)) + photos_per_block)

	# Initialize connection to camera and set up photo timing
	cam = cv2.VideoCapture(camera_url)
	next_photo_time = datetime.now() + timedelta(seconds=photo_interval)
	end_time = datetime.now() + timedelta(seconds=capture_duration)

	# Main loop
	while datetime.now() < end_time:
		if datetime.now() >= next_photo_time:
			# Check if camera is operational
			if not cam.isOpened():
				log("camera not open, trying to reconnect", logging.ERROR)
				fail_counter += 1
				cam = cv2.VideoCapture(camera_url)
				continue

			# Grab frame from camera
			success, frame = cam.read()
			if not success:
				log("failed to grab frame from camera feed", logging.WARNING)
				fail_counter += 1
				continue

			# Save snapshot of current frame
			img_name = "{}{}.png".format(base_img_filename, img_counter + 1)
			cv2.imwrite(img_name, frame)
			log("snapshot taken, saved as \"{}\"".format(img_name))
			next_photo_time = datetime.now() + timedelta(seconds=photo_interval)
			img_counter += 1

	# Log a small summary of errors encountered during routine
	if img_counter == 0:
		log("no images captured during routine", logging.ERROR)
	else:
		log("captured {} image(s) during routine".format(img_counter))

	if fail_counter > 0:
		log("encountered {} failure(s) during routine".format(fail_counter), logging.ERROR)
	else:
		log("no failures encountered during routine")

	# Release resources
	cam.release()
	log("capture routine has concluded")


def exit_handler():  # Can only be called via a SystemExit
	log("exiting script...\n##################################################\n")


if __name__ == '__main__':
	# Script Configuration
	verbose = True  # controls whether log msgs are printed to console (debugging)
	capture_duration = 62  # seconds during which the camera is opened (default is 62 sec)
	photos_per_block = 5  # number of photos taken during capture routine (default is 5 photos)
	current_dir = ""  # global variable for where img files are currently being saved
	data_dir = "/mnt/storage_1/PdM5g"  # base data location
	log_path = "./capture_log.log"  # log file name and location

	# Camera Connection Configuration
	ip_address = "174.90.198.126"
	rtsp_port = "554"
	camera_url = "rtsp://{}:{}/main".format(ip_address, rtsp_port)

	# Schedule Configuration
	schedule_times = [  # ranges from 5am to 12am inclusively
		"05:00", "06:00", "07:00", "08:00", "09:00",
		"10:00", "11:00", "12:00", "13:00", "14:00", 
		"15:00", "16:00", "17:00", "18:00", "19:00", 
		"20:00", "21:00", "22:00", "23:00", "00:00"
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

	# Begin script
	log("starting script...")
	summary_str = "script variables:"
	summary_str = summary_str + "\n\tverbose = {}".format(verbose)
	summary_str = summary_str + "\n\tcapture_duration = {} sec".format(capture_duration)
	summary_str = summary_str + "\n\tphotos_per_block = {}".format(photos_per_block)
	summary_str = summary_str + "\n\tdata_directory = \"{}\"".format(data_dir)
	summary_str = summary_str + "\n\tlog_path = \"{}\"".format(log_path)
	summary_str = summary_str + "\n\tcamera_url = \"{}\"".format(camera_url)
	summary_str = summary_str + "\n\tnum_of_scheduled_jobs = {}".format(len(schedule.jobs))
	log(summary_str)

	while True:
		try:
			current_month = datetime.today().month
			if current_month > 3 and current_month < 10:
				schedule.run_pending()
			time.sleep(1)
		except KeyboardInterrupt:  # avoids notification if script is manually terminated
			log("user shut down script with \"ctrl + c\" command")
			sys.exit(0)
		except BaseException as e:  # sends notification if script terminated due to any other exception
			log("script failure due to exception:\n{}".format(traceback.format_exc()), logging.CRITICAL)
			sys.exit(1)
