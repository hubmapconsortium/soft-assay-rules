import json
import requests as http_r
import time

# Place your Globus token here
token = ''
base_url = 'https://ingest-api.dev.hubmapconsortium.org/'
endpoint = 'assaytype'

headers = {
  'Authorization': f'Bearer {token}',
  'X-Hubmap-Application': 'ingest-pipeline',
  'Content-Type': 'application/json'
}

metadata = {
  'metadata_schema_id': '',
  'dataset_type': ''
  # Include other metadata items to match the rules
}

# This is the call to reload the rules from GitHub
url = f'{base_url}reload-assaytypes'
response = http_r.put(url, headers=headers)

url = f'{base_url}{endpoint}'
response = http_r.post(url, headers=headers, json=metadata)
print(response.content)
