# Please ensure that you have set up your django app appropriately and set up
# the urls too. This file does not cater for that.

import base64
import requests
from datetime import datetime
from django.http import JsonResponse


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


def get_access_token(request):
    """
    Sends a HTTP GET Request to retrieve a temporary access token.

    :return: JsonResponse with access token or error
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
        return JsonResponse({"access_token": result["access_token"]})

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)


def initiate_stk_push(request):
    """
    Initiates an STK push

    Expected POST data:
    {
        "amount": 1,
        "phone_number": "254XXXXXXXXX"
    }

    :return: JsonResponse with STK push result or error
    """
    import json

    # Parse request body
    try:
        data = json.loads(request.body)
        amount = data.get("amount", 1)
        phone_number = data.get("phone_number", "254463744444")
    except json.JSONDecodeError:
        # Fallback to default values if JSON parsing fails
        amount = 1
        phone_number = "254463744444"

    config = get_config()

    # Get access token directly
    token_url = config["BASE_URL"] + config["ACCESS_TOKEN_URL"]
    headers = {"Content-Type": "application/json"}

    try:
        token_response = requests.get(
            token_url,
            headers=headers,
            auth=(config["CONSUMER_KEY"], config["CONSUMER_SECRET"]),
        )
        token_response.raise_for_status()
        token_result = token_response.json()
        access_token = token_result["access_token"]

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            (
                config["BUSINESS_SHORT_CODE"] + config["PASSKEY"] + timestamp
            ).encode()
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

        response = requests.post(
            query_url, headers=stk_push_headers, json=stk_push_payload
        )
        return JsonResponse(response.json())

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)


def query_stk_status(request):
    """
    Queries the status of an STK push transaction

    Expected POST data:
    {
        "checkout_request_id": "ws_CO_DMZ_12345678901234567"
    }

    :return: JsonResponse with STK query result or error
    """
    import json

    # Parse request body
    try:
        data = json.loads(request.body)
        checkout_request_id = data.get("checkout_request_id")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    if not checkout_request_id:
        return JsonResponse(
            {"error": "Checkout Request ID not provided"}, status=400
        )

    config = get_config()

    # Get access token directly
    token_url = config["BASE_URL"] + config["ACCESS_TOKEN_URL"]
    headers = {"Content-Type": "application/json"}

    try:
        token_response = requests.get(
            token_url,
            headers=headers,
            auth=(config["CONSUMER_KEY"], config["CONSUMER_SECRET"]),
        )
        token_response.raise_for_status()
        token_result = token_response.json()
        access_token = token_result["access_token"]

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            (
                config["BUSINESS_SHORT_CODE"] + config["PASSKEY"] + timestamp
            ).encode()
        ).decode()

        query_url = config["BASE_URL"] + config["STK_QUERY_URL"]

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

        response = requests.post(
            query_url, headers=query_headers, json=query_payload
        )
        return JsonResponse(response.json())
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)
