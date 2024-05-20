
#########################################################
#                                                       #
#   THIS CODE IS UNFINISHED AND UNTESTED FOR ACCURACY   #
#                                                       #
#########################################################

def calc_estimates(pixels_w, pixels_h, fps, intervals, interval_len):
	global MiB_conv

	live_minutes_per_day = float(intervals * interval_len)
	frames_per_day = float(fps * live_minutes_per_day * 60)

	total_pixels_per_frame = float(pixels_w * pixels_h)
	total_megaBYTES_per_frame = float((total_pixels_per_frame * 3) / 1_000_000)

	daily_MiB_estimate = float(MiB_conv * total_megaBYTES_per_frame * frames_per_day)
	weekly_MiB_estimate = daily_MiB_estimate * 7.0
	monthly_MiB_estimate = weekly_MiB_estimate * 4.0

	estimates = {
		'd': daily_MiB_estimate,
		'w': weekly_MiB_estimate,
		'm': monthly_MiB_estimate
	}
	return estimates

def print_estimates(estimates, fps):
	print("{} fps Daily Estimate: {:,.2f} MiB".format(fps, estimates['d']))
	print("{} fps Weekly Estimate: {:,.2f} MiB".format(fps, estimates['w']))
	print("{} fps Monthly Estimate: {:,.2f} MiB".format(fps, estimates['m']))
	print("")


if __name__ == '__main__':
	MiB_conv = 1.048576 # 1 MiB = this many MB (global constant)

	# -- Variables for estimates --
	img_height = 576            # pixels
	img_width = 704             # pixels
	fps_list = [25, 15, 10]     # fps
	daily_intervals = 13        # live blocks scheduled per day
	length_of_intervals = 10    # minutes

	# ------------------------- #

	for fps in fps_list:
		print_estimates(calc_estimates(img_width, img_height, fps, daily_intervals, length_of_intervals), fps)

	# ------------------------- #
