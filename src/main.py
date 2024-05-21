import os
import sys
import time
import cv2
import schedule
import logging
import atexit
import smtplib
import numpy as np
from datetime import datetime, timedelta, date
from email.message import EmailMessage


def log(msg, level=logging.INFO):
    logging.log(level, msg)


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
    max_images = np.floor((live_duration * 60) / photo_interval)
    end_time = datetime.now() + timedelta(minutes=live_duration)
    next_photo_time = datetime.now() + timedelta(seconds=photo_interval)

    while True:
        # Grab frame from camera
        success, frame = cam.read()
        if not success:
            log("failed to grab frame from camera feed, ending capture routine", logging.ERROR)
            break

        # Show current feed if show_window is True
        if show_window:
            cv2.imshow(cam_window_name, frame)

        # Save snapshot of current frame
        if datetime.now() >= next_photo_time:
            img_name = "{}_{}.png".format(base_filename, img_counter+1)
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
    log("captured {} images during {} block".format(img_counter, max_images))

    # Garbage collection
    log("closing connection to camera")
    cam.release()
    cv2.waitKey(1000)
    cv2.destroyAllWindows()
    cv2.waitKey(5000)
    log("capture routine has concluded")


# SENDING EMAILS DOES NOT WORK - May 20th, 2024
# Perhaps turn this into another handler for the log
def send_email(msg_body, severity):
    recipients = ["nstrzel@uwo.ca", "sgomezro@uwo.ca"]
    default_preamble = (
        "Ignore this email if this was a test or on purpose.\n"
        "Check the logs for more information.\n"
        "Details:\n"
    )

    # Construct the msg
    msg = EmailMessage()
    msg["Subject"] = "{} Severity - Cooling Tower Capture Script Notification".format(severity)
    msg['From'] = "nstrzel@uwo.ca"
    msg['To'] = "nstrzel@uwo.ca"    # FOR TESTING
    # msg['To'] = ", ".join(recipients)
    msg.preamble = default_preamble + "\n\n" + msg_body + "\n\n"

    # Send the msg
    server = smtplib.SMTP('localhost')
    server.send_message(msg)
    server.quit()
    log("notification email was sent")


def exit_handler():
    log("ending script...\n##################################################", logging.CRITICAL)
    return


if __name__ == '__main__':

    # Script Configuration
    use_webcam = False              # controls whether webcam is used instead of 5G camera (debugging)
    show_window = False             # controls whether live stream is shown during capture routine (debugging)
    verbose = True                 # controls whether log msgs are printed to console (debugging)
    send_emails = False              # controls whether notification emails are sent in specific situations
    data_dir = "./data"             # base img file location
    current_dir = ""                # global variable for where img files are currently being saved
    live_duration = 3               # minutes during which the camera is live (5 minutes)
    photo_interval = 50             # seconds between each photograph during a live block (90 seconds)
    atexit.register(exit_handler)   # runs a routine to notify us if the script exits

    # Camera Connection Configuration
    ip_address = "174.90.198.126"
    rtsp_port = "554"
    camera_url = "rtsp://{}:{}/main".format(ip_address, rtsp_port)

    # Schedule Configuration
    # schedule.every().day.at("06:00").do(capture_routine)      # 6am
    # schedule.every().day.at("07:00").do(capture_routine)      # 7am
    # schedule.every().day.at("08:00").do(capture_routine)      # 8am
    # schedule.every().day.at("09:00").do(capture_routine)      # 9am
    # schedule.every().day.at("10:00").do(capture_routine)      # 10am
    # schedule.every().day.at("11:00").do(capture_routine)      # 11am
    # schedule.every().day.at("12:00").do(capture_routine)      # 12pm
    # schedule.every().day.at("13:00").do(capture_routine)      # 1pm
    # schedule.every().day.at("14:00").do(capture_routine)      # 2pm
    # schedule.every().day.at("15:00").do(capture_routine)      # 3pm
    # schedule.every().day.at("16:00").do(capture_routine)      # 4pm
    # schedule.every().day.at("17:00").do(capture_routine)      # 5pm
    # schedule.every().day.at("18:00").do(capture_routine)      # 6pm

    # schedule.every(90).seconds.do(capture_routine)  # debugging

    schedule.every().day.at("05:56").do(capture_routine)  # testing
    schedule.every().day.at("06:30").do(capture_routine)  # testing
    schedule.every().day.at("07:01").do(capture_routine)  # testing

    schedule.every().day.at("10:33").do(capture_routine)  # testing

    schedule.every().day.at("11:56").do(capture_routine)  # testing
    schedule.every().day.at("12:45").do(capture_routine)  # testing
    schedule.every().day.at("13:01").do(capture_routine)  # testing

    schedule.every().day.at("16:03").do(capture_routine)  # testing

    schedule.every().day.at("17:56").do(capture_routine)  # testing
    schedule.every().day.at("18:30").do(capture_routine)  # testing
    schedule.every().day.at("19:01").do(capture_routine)  # testing

    # Log initialization
    logging.getLogger().setLevel(logging.INFO)
    logging.captureWarnings(True)
    log_formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] - %(message)s", datefmt="%d-%b-%y %H:%M:%S")

    # Log file handler initialization
    file_handler = logging.FileHandler("./capture_log.log")
    file_handler.setFormatter(log_formatter)
    logging.getLogger().addHandler(file_handler)

    # Optional log console handler initialization
    if verbose:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_formatter)
        logging.getLogger().addHandler(console_handler)

    # Optional log email handler initialization
    # if send_emails:
    #     email_handler = logging.FileHandler()
    #     email_handler.setFormatter(log_formatter)
    #     email_handler.setLevel(logging.ERROR)
    #     logging.getLogger().addHandler(email_handler)

    # Begin script
    log("starting script...")
    summary_str = "script variables:"
    summary_str = summary_str + "\n\tuse_webcam = {}".format(use_webcam)
    summary_str = summary_str + "\n\tshow_window = {}".format(show_window)
    summary_str = summary_str + "\n\tverbose = {}".format(verbose)
    summary_str = summary_str + "\n\tsend_emails = {}".format(send_emails)
    summary_str = summary_str + "\n\tdata_directory = \"{}\"".format(data_dir)
    summary_str = summary_str + "\n\tlive_duration = {} minutes".format(live_duration)
    summary_str = summary_str + "\n\tphoto_interval = {} seconds".format(photo_interval)
    summary_str = summary_str + "\n\tcamera_url = \"{}\"".format(camera_url)
    summary_str = summary_str + "\n\tnum_of_scheduled_jobs = {}".format(len(schedule.jobs))
    log(summary_str)

    while True:
        schedule.run_pending()
        time.sleep(1)
