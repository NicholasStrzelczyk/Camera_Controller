import os
import time
from datetime import datetime

import cv2
from tqdm import tqdm


def extract_frames(video_file, images_dir, prev_count):
	cap = cv2.VideoCapture(video_file)
	count = prev_count
	while cap.isOpened():
		success, frame = cap.read()
		if not success:
			break
		count += 1
		cv2.imwrite("{}/frame_{}.png".format(images_dir, count), frame)
	cap.release()
	return count


if __name__ == '__main__':

	verbose = False  # change this depending on if you would like more print statements
	videos_dir = "./../../../../Bell_5G_AE_Data/videos/"  # path to directory where video files are stored
	images_dir = "./../../../../Bell_5G_AE_Data/images/"  # path to directory where images will be saved

	# ---------------------------------------- #

	num_of_videos = len(os.listdir(videos_dir))
	print("Number of video files in this directory: {}".format(num_of_videos))
	current_video_count = 0
	current_frame_count = 0
	start_time = time.time()

	for video_file in tqdm(os.listdir(videos_dir), desc="Extraction Progress"):
		if video_file.endswith(".mp4"):
			current_video_path = os.path.join(videos_dir, video_file)
			current_frame_count = extract_frames(current_video_path, images_dir, current_frame_count)
			current_video_count += 1
			if verbose:
				print("\n")
				print("[{}] - Conversion took {:.2f} seconds".format(datetime.now(), time.time() - start_time))
				print("[{}] - {}/{} videos converted".format(datetime.now(), current_video_count, num_of_videos))
				print("[{}] - Current frame count: {}".format(datetime.now(), current_frame_count))

	elapsed_time = time.time() - start_time

	print("--------------- Script Complete ---------------")
	print("Videos converted: {}".format(current_video_count))
	print("Total frames saved: {}".format(current_frame_count))
	print("Time elapsed: {}".format(elapsed_time))
