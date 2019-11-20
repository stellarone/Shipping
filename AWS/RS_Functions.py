from rocketshipit import RocketShipIt
import boto3
from boto3.dynamodb.conditions import Key, Attr

class RSFunctions: 
	
	def __init__(self):
		self.RS_API_KEY = 'sFuEf0TF1M5bVrIg3gnjs4vYJTOD6VVH3JAIVcAH' 
		self.FedEx_Account = '' # Test Account Number = '510087100'
		self.FedEx_Password = '' # Test Account Password = 'xyQpxVDe1zv7OtH4yfeSX67Ax' 
		self.FedEx_Api_Key = '' # Test API Key =  'jYnruZAs4Ts3eMih'
		self.FedEx_Meter = '' # Test Meter = '119126783'
		
	def getCreds(self, token):
		dynamodb = boto3.resource('dynamodb')	
		tbl_Connection = dynamodb.Table('Integrations_Tenant')
		queryResponse = tbl_Connection.query(KeyConditionExpression=Key('Integration').eq('Shipping') & Key('Tenant').eq(token))
		if not queryResponse.get("Items"):
			print('Token not found')
			return {code: -100, message: "Error: Token Not Found"}
		Carriers = queryResponse['Items'][0]['Carriers']
		if not Carriers['FedEx']: 
			print('Unable to find Carrier')
			return {code: -101, message: "Error: Unable to find Carrier"}
		#FedEx_Account = queryResponse['Items'][0]['Car_Account']
		#FedEx_Password=  queryResponse['Items'][0]['Car_Password'] 
		#FedEx_Api_Key = queryResponse['Items'][0]['Car_Api_Key'] 
		#FedEx_Meter = queryResponse['Items'][0]['Car_Meter']
		FedEx_Account = Carriers['FedEx']['Car_Account']
		FedEx_Password = Carriers['FedEx']['Car_Password']
		FedEx_Api_Key = Carriers['FedEx']['Car_Api_Key']
		FedEx_Meter = Carriers['FedEx']['Car_Meter']
		if not FedEx_Account:
			print("Error Parsing DynamoDB")
			return {code: -200, message: "Error: Unable to Parse DynamoDB Credentials"}
		return {code: 0, message: ""}
	
	def getRates(self, orgName, orgAddr1, orgAddr2, orgCity, orgState, orgZip, weight, length, width, height, toName, toAddr1, toAddr2, toCity, toState, toZip, service):
		rs = RocketShipIt(self.RS_API_KEY, 'https://api.rocketship.it/v1/')
		print(orgName, orgAddr1, orgAddr2, orgCity, orgState, orgZip, weight, length, width, height, toName, toAddr1, toAddr2, toCity, toState, toZip, service)
		resp = rs.request(
			'FedEx',
			'GetAllRates',
			{'account_number': str(self.FedEx_Account),
			'key': str(self.FedEx_Api_Key),
			'meter_number': str(self.FedEx_Meter),
			'weight_unit': "LB",
			'packages': [{'weight': float(weight),
				'length': float(length),
				'width': float(width),
				'height': float(height)}],
			'password': str(self.FedEx_Password),
			'shipper': str(orgName),
			'ship_addr1': str(orgAddr1),
			'ship_addr2': str(orgAddr2),
			'ship_city' : str(orgCity),
			'ship_state' : str(orgState),
			'ship_code': str(orgZip),
			'ship_country': 'US',
			'ship_phone': '9495445280',
			'to_name': str(toName),
			'to_addr1': str(toAddr1),
			'to_city': str(toCity),
			'to_state': str(toState),
			'to_code': str(toZip),
			'to_country': 'US',
			'service': service,
			'test': True}
			)   
		#'service': service, #Limits Shipping type
		# 
		
		eCode = resp['meta']
		if int(eCode['code']) != 200:
			return [{'service_code' : "_Error: " + eCode['error_message']}]
		data = resp['data']
		errors = data['errors']
		
		if errors:
			error = errors[0]
			return [{'service_code' : "_Error: " + error['description']}]
		rates = data['rates']
		respCount = len(rates)
		
		####################################
		# Initialize array[respCount][5] = 0 for all items
		# aRates = [[0 for y in range(5)] for z in range(respCount)]
		aRates = []
		keys = ['service_code', 'desc', 'rate', 'negotiated_rate', 'est_delivery_time']
		x = 0
		for x in range(0, respCount):
			ele_rates = rates[x]
			#######################################
			# Get members from ele_rates object
			servCode = ele_rates['service_code']
			desc = ele_rates['desc']	
			rate = ele_rates['rate'] #[2] - publishedRate
			negRate = ele_rates['negotiated_rate']
			time = ele_rates['est_delivery_time']
			values = [servCode, desc, rate, negRate, time]
			aRates.append(dict(zip(keys, values)))
		return aRates
	# End def getRates()
	#
	#
	def sendLabel(self, orgName, orgAddr1, orgAddr2, orgCity, orgState, orgZip, orgPhone, weight, sigType, toName, toAddr1, toAddr2, toCity, toState, toZip, toPhone, service):
		rs = RocketShipIt(self.RS_API_KEY, 'https://api.rocketship.it/v1/')
		resp = rs.request(
			'FedEx',
			'SubmitShipment',
			{'account_number': str(self.FedEx_Account),
			'key': str(self.FedEx_Api_Key),
			'meter_number': str(self.FedEx_Meter),
			'packages': [{'weight': float(weight), 'signature_type': str(sigType)}],
			'password': str(self.FedEx_Password),
			'shipper': str(orgName),
			'ship_addr1': str(orgAddr1),
			'ship_addr2': str(orgAddr2),
			'ship_city' : str(orgCity),
			'ship_state' : str(orgState),
			'ship_code': str(orgZip),
			'ship_country': 'US',
			'ship_phone': str(orgPhone),
			'to_name': str(toName),
			'to_addr1': str(toAddr1),
			'to_city': str(toCity),
			'to_state': str(toState),
			'to_code': str(toZip),
			'to_phone': str(toPhone),
			'to_country': 'US',
			'image_type': 'PDF',
			'test': True}
			)
		eCode = resp['meta']
		if int(eCode['code']) != 200:
			return [{'service_code' : "_Error: " + eCode['error_message']}]
		data = resp['data']
		errors = data['errors']
		
		if errors:
			error = errors[0]
			return [{'service_code' : "_Error: " + error['description']}]
		packages = data['packages']
		respCount = len(packages)
		##################################
		# Initialize array[respCount][5] = 0 for all items
		aRates = [[0 for y in range(5)] for z in range(respCount)]
		aRates = [{'charges': data['charges']}]
		labels = []
		keys = ['label', 'tracking_number']
		x = 0
		for x in range(0, respCount):
			ele_rates = packages[x]
			#######################################
			# Get members from ele_rates object
			label = packages[0]['label']
			tracking_number = packages[0]['tracking_number']
			values = [label, tracking_number]
			labels.append(dict(zip(keys, values)))
		aRates.append(dict(zip({'packages'}, labels)))
		return aRates