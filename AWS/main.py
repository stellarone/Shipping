import json
from RS_Functions import RSFunctions

def lambda_handler(event, context):
	# You can get your RocketShipIt API key from: https://www.rocketship.it/account
	# Check Params
	token = event.get("token")
	action = event.get("action")
	orgName = event.get("org_name")
	orgAddr1 = event.get("org_addr1")
	orgAddr2 = event.get("org_addr2")
	orgCity = event.get("org_city")
	orgState = event.get("org_state")
	orgZip = event.get("org_code")
	orgPhone = event.get("org_phone")
	weight = event.get("weight")
	length = event.get("length")
	width = event.get("width")
	height = event.get("height")
	sigType = event.get("sig_type")
	toName = event.get("to_name")
	toAddr1 = event.get("to_addr1")
	toAddr2 = event.get("to_addr2")
	toCity = event.get("to_city")
	toState = event.get("to_state")
	toZip = event.get("to_code")
	toPhone = event.get("to_phone")
	service = event.get("service")
	if not service:
		service = ""
	if not sigType:
		sigType = "SERVICE_DEFAULT"
	############################################################
	#
	# Add config keys to RSFunctions(CarrierAccount, CarrierPass, CarrierAPIKey, CarrierMeterNumber)
	print("selecting action...")
	if action == "rateshop":
		oFunction = RSFunctions()
		oFunction.getCreds(token)
		aRates = oFunction.getRates(orgName, orgAddr1, orgAddr2, orgCity, orgState, orgZip, 
			weight, length, width, height, toName, toAddr1, toAddr2, toCity, toState, toZip, service)
			
		print(aRates)
		if aRates[0]['service_code'].find('Error', 0 , 10) > 0:
			errstr = aRates[0]['service_code']
			print(errstr)
			return {
				'statusCode': 301,
				'body': errstr
			}
		
		return {
			'statusCode': 200,
			'body': json.dumps(aRates)
		}
		
		
	elif action == "submitShipment": 
		if not service:
			service = ""
		oFunctions = RSFunctions()
		aRates = oFunctions.getRates(orgName, orgAddr1, orgAddr2, orgCity, orgState, orgZip, 
			weight, length, width, height, toName, toAddr1, toAddr2, toCity, toState, toZip, service)
		aShipment = oFunctions.sendLabel(str(orgName), str(orgAddr1), str(orgAddr2), str(orgCity), str(orgState), str(orgZip), str(orgPhone),
			float(weight), str(sigType), str(toName), str(toAddr1), str(toAddr2), str(toCity), str(toState), str(toZip), str(toPhone), str(service))
		
		if aRates[0]['service_code'].find('Error', 0 , 10) > 0:
			errstr = aRates[0]['service_code']
			print(errstr)
			return {
				'statusCode': 301,
				'body': errstr
			}
		
		return {
			'statusCode': 200,
			'rates': json.dumps(aRates),
			'body': json.dumps(aShipment)
		}