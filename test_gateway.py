import requests
from requests_ip_rotator import ApiGateway
import os
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables
load_dotenv()

# Initialize the API Gateway for IP rotation
url = 'https://store.steampowered.com/api/appdetails/?appids=162206'
url2 = 'https://store.steampowered.com/api/appdetails/'
ip_url = 'http://checkip.amazonaws.com'
regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
gateway = ApiGateway(url2, regions=regions, access_key_id=os.getenv('AWS_ACCESS_KEY'), access_key_secret=os.getenv('AWS_SECRET_KEY'))
gateway.start()

# Debug: Print the endpoints to verify
print("API Gateway endpoints:")
pprint(gateway.endpoints)

# Create a session and mount the API Gateway
session = requests.Session()
session.mount(url2, gateway)

# Make a request to check the IP address
for i in range(5):  # Make multiple requests to check IP rotation
    response = session.get(url)
    print(f"Request {i+1} from IP address: {response.text.strip()}")

# Optionally, print out the session adapters to verify correct mounting
print("Session adapters:")
pprint(session.adapters)
