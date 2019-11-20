import json
import os
import requests
import subprocess

# Sends requests to RocketShipIt
class RocketShipIt:
	def __init__(self, api_key='', endpoint=''):
		self.api_key = api_key
		self.endpoint = endpoint
		self.bin_name = 'RocketShipIt'

		# Directory that holds the RocketShipIt binary
		current_dir = os.path.dirname(os.path.realpath(__file__))
		self.bin_dir = current_dir + '/../../'

	# Make local request if RocketShipIt binary is available
	# else make HTTP API request.
	def request(self, carrier, action, params):
		self.carrier = carrier

		# Use RocketShipIt Cloud if API key provided
		if self.api_key != '':
			return self.http_request(params, action)

		if os.path.isfile(self.bin_dir + self.bin_name):
			return self.local_request(action, params)

	# Send JSON to local RocketShipIt binary app through
	# stdin/stdout
	def local_request(self, action, params):
		data = {
			'carrier': self.carrier,
			'action': action,
			'params': params
		}
		popen = subprocess.Popen('./'+self.bin_name,
								stdout=subprocess.PIPE,
								stdin=subprocess.PIPE,
								cwd=self.bin_dir)
		s = popen.communicate(json.dumps(data))

		return json.loads(s[0])
		
	# Send JSON over HTTP to RocketShipIt API
	def http_request(self, params, action):
		data = {
			'carrier': self.carrier,
			'action': action,
			'params': params
		}
		headers = {
			'x-api-key': self.api_key,
			'Content-Type': 'application/json',
		}
		resp = requests.post(self.endpoint, json=data, headers=headers)

		return resp.json()
