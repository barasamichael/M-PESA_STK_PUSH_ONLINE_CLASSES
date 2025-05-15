### Python Version (Plain Python)

import requests
import json
import base64
import logging
from datetime import datetime


def get_config():
    return {
        "BASE_URL": "https://sandbox.safaricom.co.ke",
        "ACCESS_TOKEN_URL": "/oauth/v1/generate?grant_type=client_credentials",
        "STK_PUSH_URL": "/mpesa/stkpush/v1/processrequest",
        "STK_QUERY_URL": "/mpesa/stkpushquery/v1/query",
        "BUSINESS_SHORT_CODE": "174379",
        "PASSKEY": "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",
        "TILL_NUMBER": "174379",
        "CALLBACK_URL": "https://mydomain.com/path",
        "CONSUMER_KEY": "E7RkuNKKVFG3p2nWjEM78RcbFOwH2qb5UHpGvpOhzodFGbHV",
        "CONSUMER_SECRET": "tQw44mUODFBqUk25oS5NweJBMrlvdWwkYdap6P3895kekW2LmLFcHT4Lvjr4figm",
    }


def get_access_token():
    """
    Sends a HTTP GET Request to retrieve a temporary access token.

    :return: Access token string or None if unsuccessful
    """
    config = get_config()
    url = config["BASE_URL"] + config["ACCESS_TOKEN_URL"]
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(
            url,
            headers=headers,
            auth=(config["CONSUMER_KEY"], config["CONSUMER_SECRET"]),
        )
        response.raise_for_status()
        result = response.json()
        return result["access_token"]

    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": str(e)}, indent=2))
        return None


def initiate_stk_push(amount=1, phone_number="254463744444"):
    """
    Initiates an STK push using M-PESA API

    :param amount: Transaction amount
    :param phone_number: Customer phone number (format: 254XXXXXXXXX)
    :return: JSON response from the STK push request
    """
    config = get_config()
    access_token = get_access_token()

    if not access_token:
        return {"error": "Failed to get access token"}

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        (config["BUSINESS_SHORT_CODE"] + config["PASSKEY"] + timestamp).encode()
    ).decode()

    query_url = config["BASE_URL"] + config["STK_PUSH_URL"]

    stk_push_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    stk_push_payload = {
        "BusinessShortCode": config["BUSINESS_SHORT_CODE"],
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerBuyGoodsOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": config["TILL_NUMBER"],
        "PhoneNumber": phone_number,
        "CallBackURL": config["CALLBACK_URL"],
        "AccountReference": "DaSKF Raffle",
        "TransactionDesc": "STK/IN Push",
    }

    try:
        response = requests.post(
            query_url, headers=stk_push_headers, json=stk_push_payload
        )
        result = response.json()
        print(json.dumps(result, indent=2))
        return result
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def query_stk_status(checkout_request_id):
    """
    Queries the status of an STK push transaction

    :param checkout_request_id: The CheckoutRequestID from the STK push response
    :return: JSON response with transaction status
    """
    config = get_config()
    access_token = get_access_token()

    if not access_token:
        logging.error("Access token not obtained")
        return {"error": "Transaction failed. Try again later."}

    if not checkout_request_id:
        logging.error("Checkout Request ID not provided")
        return {"error": "Transaction failed. Try again later."}

    query_url = config["BASE_URL"] + config["STK_QUERY_URL"]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        (config["BUSINESS_SHORT_CODE"] + config["PASSKEY"] + timestamp).encode()
    ).decode()

    query_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    query_payload = {
        "BusinessShortCode": config["BUSINESS_SHORT_CODE"],
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id,
    }

    try:
        response = requests.post(
            query_url, headers=query_headers, json=query_payload
        )
        result = response.json()
        print(json.dumps(result, indent=2))
        return result
    except requests.exceptions.RequestException as e:
        return {"errorMessage": str(e)}


import time

if __name__ == "__main__":
    print("Testing STK Push:")
    push_result = initiate_stk_push(amount=1, phone_number="254114742348")

    if "CheckoutRequestID" in push_result:
        checkout_request_id = push_result["CheckoutRequestID"]
        print("\nTesting STK Query:")
        print(f"Using CheckoutRequestID: {checkout_request_id}")

        print(
            "\nPolling for status updates every 5 seconds (for up to 1 minute 30 seconds)..."
        )

        for attempt in range(18):  # 90 seconds / 5 seconds = 18
            query_result = query_stk_status(checkout_request_id)
            print(f"Attempt {attempt + 1}: {query_result}")

            # Break early if successful (assuming you check status field)
            if (
                query_result.get("ResultCode") == "0"
            ):  # or other success criteria
                print("Transaction successful.")
                break

            time.sleep(5)
        else:
            print("Transaction not completed within expected time.")

    else:
        print("Failed to get CheckoutRequestID for query")
