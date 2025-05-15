import requests
import json
import base64
from datetime import datetime


def get_config():
    return {
        "BASE_URL": "https://sandbox.safaricom.co.ke",
        "ACCESS_TOKEN_URL": "/oauth/v1/generate?grant_type=client_credentials",
        "STK_PUSH_URL": "/mpesa/stkpush/v1/processrequest",
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


if __name__ == "__main__":
    # Example usage
    result = initiate_stk_push(amount=1, phone_number="254712345678")
    print(result)
