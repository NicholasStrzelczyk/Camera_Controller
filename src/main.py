import os
import time
import cv2
import schedule
import numpy as np
from datetime import datetime, timedelta, date


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
        print("{}: creating new directory for {}".format(datetime.now(), today))
        os.makedirs(new_path)
    else:
        print("{}: directory already exists for {}".format(datetime.now(), today))
    current_dir = new_path
    print("{}: current file directory set as \"{}\"".format(datetime.now(), current_dir))


def capture_routine():
    global use_webcam, show_window, camera_url, current_dir, live_duration, photo_interval

    # Check if directories have been made
    setup_directories()

    # Initialize connection
    cam = cv2.VideoCapture(0)
    if not use_webcam:
        cam = cv2.VideoCapture(camera_url)
        print("{}: connecting to rtsp camera".format(datetime.now()))
    else:
        print("{}: connecting to default camera (webcam)".format(datetime.now()))

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
            print("{}: failed to grab frame".format(datetime.now()))
            break

        # Show current feed if show_window is True
        if show_window:
            cv2.imshow(cam_window_name, frame)

        # Save snapshot of current frame
        if datetime.now() >= next_photo_time:
            img_name = "{}_{}.png".format(base_filename, img_counter+1)
            cv2.imwrite(img_name, frame)
            print("{}: snapshot taken, saved as \"{}\"".format(datetime.now(), img_name))
            next_photo_time = datetime.now() + timedelta(seconds=photo_interval)
            img_counter += 1

        # Stop condition(s)
        if img_counter == max_images:
            print("{}: successfully captured 3 images during live block".format(datetime.now()))
            break

        if datetime.now() >= end_time:
            print("{}: camera live block has ended".format(datetime.now()))
            break

        # Wait interval until loop is repeated (100ms = ~ 10fps)
        cv2.waitKey(100)

    # Garbage collection
    print("{}: closing connection to camera".format(datetime.now()))
    cam.release()
    cv2.waitKey(1000)
    cv2.destroyAllWindows()
    cv2.waitKey(5000)


if __name__ == '__main__':

    print("{}: starting capture script".format(datetime.now()))

    # Script Configuration
    use_webcam = False          # for local debugging
    show_window = False         # for local debugging
    log_dir = "./../logs"       # log files location
    data_dir = "./../data"      # base img file location
    current_dir = ""            # global variable for where img files are currently being saved
    live_duration = 5           # minutes during which the camera is live (5 minutes)
    photo_interval = 90         # seconds between each photograph during a live block (90 seconds)

    # Camera Connection Configuration
    ip_address = "174.90.198.126"
    rtsp_port = "554"
    camera_url = "rtsp://{}:{}/main".format(ip_address, rtsp_port)
    print("{}: rtsp camera url set to \"{}\"".format(datetime.now(), camera_url))

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

    print("{}: scheduled jobs:".format(datetime.now()))
    for job in schedule.jobs:
        print("\t{}".format(job))

    while True:
        schedule.run_pending()
        time.sleep(1)
