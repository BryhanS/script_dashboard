import requests
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv  
import os

load_dotenv(verbose=True,override=True)
# url = 'https://staging-583a-catapu8.wpcomstaging.com'
url = os.getenv("URL")
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")

headers = {
    "Content-Type": "application/json"
}



def put_tracking_woocommerce(order_id, tracking_number):
    path_url = f'{url}/wp-json/wc-shipment-tracking/v3/orders/{order_id}/shipment-trackings/'
    year, track = tracking_number.split("-")

    data = {
        "custom_tracking_provider": 'Olva Courier',
        "custom_tracking_link": f'https://tracking.olvaexpress.pe/?emision={year}&tracking={track}',
        "tracking_number": tracking_number
    }

    try:
        response = requests.post(
            path_url,
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            headers=headers,
            json=data
            )
        return(f"Order {order_id} - Status Code: {response.status_code}")

    except Exception as e:
        return(f"Order {order_id} - Error: {e}")
