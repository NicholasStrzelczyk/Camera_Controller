import os
import time
from datetime import datetime

import cv2


def extract_frames(video_file, images_dir, prev_count):
	cap = cv2.VideoCapture(video_file)
	count = prev_count
	while cap.isOpened():
		success, frame = cap.read()
		if not success:
			break
		count += 1
		cv2.imwrite("{}/vid_frame_{}.png".format(images_dir, count), frame)
	cap.release()
	return count


if __name__ == '__main__':

	partition = "train"  # change this depending on which partition you wish to convert

	videos_dir = "./../../../../Bell_5G_Data/{}/videos/".format(partition)
	images_dir = "./../../../../Bell_5G_Data/{}/images/".format(partition)
	num_of_videos = len(os.listdir(videos_dir))
	print("Number of videos in this directory: {}".format(num_of_videos))

	current_video_count = 0
	current_frame_count = 0
	start_time = time.time()

	for video_file in os.listdir(videos_dir):
		if video_file.endswith(".mp4"):
			current_video_path = os.path.join(videos_dir, video_file)
			current_frame_count = extract_frames(current_video_path, images_dir, current_frame_count)
			current_video_count += 1
			print("[{:.0f}] - Conversion took {:.2f} seconds".format(datetime.now(), time.time() - start_time))
			print("[{:.0f}] - {}/{} videos converted".format(datetime.now(), current_video_count, num_of_videos))
			print("[{:.0f}] - Current frame count: {}".format(datetime.now(), current_frame_count))
			quit()

	elapsed_time = time.time() - start_time

	print("--------------- Script Complete ---------------")
	print("Videos converted: {}".format(current_video_count))
	print("Total frames saved: {}".format(current_frame_count))
	print("Time elapsed: {}".format(elapsed_time))
