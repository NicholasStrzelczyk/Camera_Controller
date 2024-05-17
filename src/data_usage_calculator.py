
if __name__ == '__main__':

	img_height = 576            # pixels
	img_width = 704             # pixels
	bit_rate = 2048             # kbps
	fps = 25                    # fps
	daily_rec_intervals = 6     # live blocks scheduled per day
	length_of_intervals = 10    # minutes

	# ------------------------- #

	MiB_conv = 1.048576         # 1 MiB = this many MB
	live_minutes_per_day = float(daily_rec_intervals * length_of_intervals)
	frames_per_day = float(fps * live_minutes_per_day * 60)

	total_pixels = float(img_height * img_width)
	total_megaBYTES = float((total_pixels * 3) / 1_000_000)
	uncompressed_daily_MiB_estimate = float(MiB_conv * total_megaBYTES * frames_per_day)
	uncompressed_weekly_MiB_estimate = uncompressed_daily_MiB_estimate * 7.0
	uncompressed_monthly_MiB_estimate = uncompressed_weekly_MiB_estimate * 4.0

	kiloBITS_per_day = float(bit_rate * live_minutes_per_day * 60)
	megaBYTES_per_day = float(kiloBITS_per_day / 8_000_000)
	compressed_daily_MiB_estimate = float(MiB_conv * megaBYTES_per_day)
	compressed_weekly_MiB_estimate = compressed_daily_MiB_estimate * 7.0
	compressed_monthly_MiB_estimate = compressed_weekly_MiB_estimate * 4.0

	# ------------------------- #

	print("Daily (uncompressed): {} MiB".format(uncompressed_daily_MiB_estimate))
	print("Weekly (uncompressed): {} MiB".format(uncompressed_weekly_MiB_estimate))
	print("Monthly (uncompressed): {} MiB".format(uncompressed_monthly_MiB_estimate))
	print("")
	print("Daily (compressed): {} MiB".format(compressed_daily_MiB_estimate))
	print("Weekly (compressed): {} MiB".format(compressed_weekly_MiB_estimate))
	print("Monthly (compressed): {} MiB".format(compressed_monthly_MiB_estimate))
