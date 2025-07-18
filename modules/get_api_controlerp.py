from dotenv import load_dotenv
import os
import requests

load_dotenv(verbose=True,override=True)

api_key = os.getenv("API_KEY_SISTEMA")
url = os.getenv("URL_SISTEMA")+'api/document/search-items'

def get_api_controlerp():
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',  # Adjust the content type as needed
    }

    response = requests.get(url, headers=headers)
    try:
        if response.status_code == 200:
            data_final = response.json()
            return data_final
        else:
            print(f'Error in the request. Status code: {response.status_code}')
            print('Error message:', response.text)
            return None
        
    except Exception as e:
        print(f'An error occurred: {e}')
        return None


# get_api_controlerp()