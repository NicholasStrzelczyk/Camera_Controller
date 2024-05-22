from datetime import datetime


def get_email_recipient_list(path):
	with open(path, "r") as file:
		emails = file.readlines()
	emails = [e.strip("\n") for e in emails]
	print(emails)  # debugging
	return emails


def get_email_credentials(path):
	with open(path, "r") as file:
		creds = file.readlines()
	creds = [c.strip("\n") for c in creds]
	print(creds)  # debugging
	return creds[0], creds[1]


def get_current_hour_str():
	current_hour = datetime.today().hour
	if current_hour == 12:
		result = "{}pm".format(current_hour)
	elif current_hour > 12:
		result = "{}pm".format(current_hour - 12)
	else:
		result = "{}am".format(current_hour)
	return result
