import os, re
from twilio.rest import Client
from dotenv import load_dotenv
from wtforms.validators import ValidationError


account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_phone = os.environ['TWILIO_PHONE_NR']


def validate_phone_number(field):
	if re.match(r'^\+[0-9]{7,}$', field):
		return True
	return False

def send_sms(phone, message):
	if not validate_phone_number(phone):
		return False, "phone number is not valid"

	client = Client(account_sid, auth_token)

	try:
		message = client.messages.create(
			body=message,
			from_=twilio_phone,
			to=phone,
		)
		return True, None
	except Exception as error:
		return False, error.msg