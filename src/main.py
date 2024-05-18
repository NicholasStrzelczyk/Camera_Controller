import os
import time
import cv2
import schedule
import logging
import numpy as np
from datetime import datetime, timedelta, date


def log_print(msg, level=logging.INFO):
    global print_logs_msgs

    if print_logs_msgs:
        print("{}: {}".format(datetime.now(), msg))

    if level == logging.WARNING:
        logging.warning(msg)
    elif level == logging.ERROR:
        logging.error(msg)
    elif level == logging.CRITICAL:
        logging.critical(msg)
    else:
        logging.info(msg)


def get_current_hour_str():
    current_hour = datetime.today().hour
    if current_hour == 12:
        result = "{}pm".format(current_hour)
    elif current_hour > 12:
        result = "{}pm".format(current_hour-12)
    else:
        result = "{}am".format(current_hour)
    return result


def setup_directories():
    global data_dir, current_dir

    today = date.today()
    new_path = "{}/{}/{}/{}".format(data_dir, today.year, today.month, today.day)

    if not os.path.exists(new_path):
        log_print("creating new directory for {}".format(today))
        os.makedirs(new_path)
    else:
        log_print("directory already exists for {}".format(today))

    current_dir = new_path
    log_print("current file directory set as \"{}\"".format(current_dir))


def capture_routine():
    global use_webcam, show_window, camera_url, current_dir, live_duration, photo_interval

    # Check if directories have been made
    setup_directories()

    # Initialize connection
    cam = cv2.VideoCapture(0)
    if not use_webcam:
        cam = cv2.VideoCapture(camera_url)
        log_print("initializing rtsp camera device")
    else:
        log_print("initializing default camera (webcam) device")

    # Check if camera is operational
    if not cam.isOpened():
        log_print("camera not open, cannot extract feed, exiting routine", logging.ERROR)
        return

    # Initialize naming variables
    cam_window_name = "rtsp camera feed"
    current_date_str = str(date.today()).replace("-", "_")
    current_hour_str = get_current_hour_str()
    base_filename = "{}/{}_{}_snapshot".format(current_dir, current_date_str, current_hour_str)

    # Set up stop condition & timing variables
    img_counter = 0
    max_images = np.floor((live_duration * 60) / photo_interval)
    end_time = datetime.now() + timedelta(minutes=live_duration)
    next_photo_time = datetime.now() + timedelta(seconds=photo_interval)

    while True:
        # Grab frame from camera
        success, frame = cam.read()
        if not success:
            log_print("failed to grab frame from camera feed, ending capture routine", logging.ERROR)
            break

        # Show current feed if show_window is True
        if show_window:
            cv2.imshow(cam_window_name, frame)

        # Save snapshot of current frame
        if datetime.now() >= next_photo_time:
            img_name = "{}_{}.png".format(base_filename, img_counter+1)
            cv2.imwrite(img_name, frame)
            log_print("snapshot taken, saved as \"{}\"".format(img_name))
            next_photo_time = datetime.now() + timedelta(seconds=photo_interval)
            img_counter += 1

        # Stop conditions
        if img_counter == max_images or datetime.now() >= end_time:
            log_print("concluding capture routine for current live block, captured {} images".format(img_counter))
            break

        # Wait interval until loop is repeated (100ms = ~ 10fps)
        cv2.waitKey(100)

    # Garbage collection
    log_print("closing connection to camera")
    cam.release()
    cv2.waitKey(1000)
    cv2.destroyAllWindows()
    cv2.waitKey(5000)


if __name__ == '__main__':

    # Script Configuration
    use_webcam = False          # controls whether webcam is used instead of 5G camera (debugging)
    show_window = False         # controls whether live stream is shown during capture routine (debugging)
    print_logs_msgs = True      # controls whether log msgs are printed to console (debugging)
    data_dir = "./data"         # base img file location
    current_dir = ""            # global variable for where img files are currently being saved
    live_duration = 5           # minutes during which the camera is live (5 minutes)
    photo_interval = 90         # seconds between each photograph during a live block (90 seconds)

    # Camera Connection Configuration
    ip_address = "174.90.198.126"
    rtsp_port = "554"
    camera_url = "rtsp://{}:{}/main".format(ip_address, rtsp_port)

    # Schedule Configuration
    schedule.every().day.at("06:00").do(capture_routine)      # 6am
    schedule.every().day.at("07:00").do(capture_routine)      # 7am
    schedule.every().day.at("08:00").do(capture_routine)      # 8am
    schedule.every().day.at("09:00").do(capture_routine)      # 9am
    schedule.every().day.at("10:00").do(capture_routine)      # 10am
    schedule.every().day.at("11:00").do(capture_routine)      # 11am
    schedule.every().day.at("12:00").do(capture_routine)      # 12pm
    schedule.every().day.at("13:00").do(capture_routine)      # 1pm
    schedule.every().day.at("14:00").do(capture_routine)      # 2pm
    schedule.every().day.at("15:00").do(capture_routine)      # 3pm
    schedule.every().day.at("16:00").do(capture_routine)      # 4pm
    schedule.every().day.at("17:00").do(capture_routine)      # 5pm
    schedule.every().day.at("18:00").do(capture_routine)      # 6pm
    # schedule.every(90).seconds.do(capture_routine)  # debugging

    # Log initialization
    log_file = "./capture_log.log"
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    log_date_fmt = '%d-%b-%y %H:%M:%S'
    logging.basicConfig(filename=log_file, format=log_format, datefmt=log_date_fmt, level=logging.INFO)

    log_print("starting capture script...")
    log_print("rtsp camera url set to \"{}\"".format(camera_url))
    jobs_str = "{} scheduled jobs:".format(len(schedule.jobs))
    for job in schedule.jobs:
        jobs_str = jobs_str + ("\n\t{}".format(job))
    log_print(jobs_str)

    while True:
        schedule.run_pending()
        time.sleep(1)
