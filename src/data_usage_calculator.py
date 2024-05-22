#########################################################
#                                                       #
#   THIS CODE IS UNFINISHED AND UNTESTED FOR ACCURACY   #
#                                                       #
#########################################################

def calc_compressed_estimates(bitrate, intervals, interval_len):
	global kbps_to_MiBps

	live_seconds_per_day = float(intervals * interval_len * 60)
	bitrate_MiBps = float(bitrate / kbps_to_MiBps)

	daily_MiB_estimate = float(live_seconds_per_day * bitrate_MiBps)
	weekly_MiB_estimate = daily_MiB_estimate * 7.0
	monthly_MiB_estimate = weekly_MiB_estimate * 4.0

	estimates = {
		'd': daily_MiB_estimate,
		'w': weekly_MiB_estimate,
		'm': monthly_MiB_estimate
	}
	return estimates


def calc_uncompressed_estimates(img_size, fps, intervals, interval_len):
	global MB_to_MiB

	live_minutes_per_day = float(intervals * interval_len)
	frames_per_day = float(fps * live_minutes_per_day * 60)

	img_w, img_h = img_size
	total_pixels_per_frame = float(img_w * img_h)
	total_megaBYTES_per_frame = float((total_pixels_per_frame * 3) / 1_000_000)

	daily_MiB_estimate = float((total_megaBYTES_per_frame * frames_per_day) / MB_to_MiB)
	weekly_MiB_estimate = daily_MiB_estimate * 7.0
	monthly_MiB_estimate = weekly_MiB_estimate * 4.0

	estimates = {
		'd': daily_MiB_estimate,
		'w': weekly_MiB_estimate,
		'm': monthly_MiB_estimate
	}
	return estimates


def print_estimates(estimates, fps=None):
	if fps is None:
		print("Daily Estimate: {:,.2f} MiB".format(estimates['d']))
		print("Weekly Estimate: {:,.2f} MiB".format(estimates['w']))
		print("Monthly Estimate: {:,.2f} MiB".format(estimates['m']))
	else:
		print("{} fps Daily Estimate: {:,.2f} MiB".format(fps, estimates['d']))
		print("{} fps Weekly Estimate: {:,.2f} MiB".format(fps, estimates['w']))
		print("{} fps Monthly Estimate: {:,.2f} MiB".format(fps, estimates['m']))
		print("")


if __name__ == '__main__':
	MB_to_MiB = 1.048576  # 1 MiB = this many MB (global constant)
	kbps_to_MiBps = 1048.58  # 1 MiBps = this many kbps (global constant)

	# -- Variables for estimates --
	img_size = (704, 576)  # pixels (length, width)
	fps_list = [25, 15, 10]  # fps
	daily_intervals = 15  # live blocks scheduled per day
	length_of_intervals = 2  # minutes
	bit_rate_kbps = 2048  # kilo-bit per second

	# ------------------------- #

	print("------------------------------")
	print("--- Uncompressed Estimates ---")
	for fps in fps_list:
		print_estimates(calc_uncompressed_estimates(img_size, fps, daily_intervals, length_of_intervals), fps)

	print("------------------------------")
	print("---- Compressed Estimates ----")
	print_estimates(calc_compressed_estimates(bit_rate_kbps, daily_intervals, length_of_intervals))

# ------------------------- #
