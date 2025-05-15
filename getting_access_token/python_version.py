import requests
import json


def get_access_token():
    """
    Sends a HTTP GET Request to retrieve a temporary access token.

    Notes:
        - When you move to production, change the `BASE_URL` to
          `https://api.safaricom.co.ke`.
        - Also change your `CONSUMER_KEY` AND `CONSUMER_SECRET` to match those
          provided to you by Safaricom.

    :return: None
    """
    config = {
        "BASE_URL": "https://sandbox.safaricom.co.ke",
        "ACCESS_TOKEN_URL": "/oauth/v1/generate?grant_type=client_credentials",
        "CONSUMER_KEY": "E7RkuNKKVFG3p2nWjEM78RcbFOwH2qb5UHpGvpOhzodFGbHV",
        "CONSUMER_SECRET": "tQw44mUODFBqUk25oS5NweJBMrlvdWwkYdap6P3895kekW2LmLFcHT4Lvjr4figm",
    }

    # Please take note that the Content-Type must always be JSON.
    url = config["BASE_URL"] + config["ACCESS_TOKEN_URL"]
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(
            url,
            headers=headers,
            auth=(config["CONSUMER_KEY"], config["CONSUMER_SECRET"]),
        )
        response.raise_for_status()

        # Comment this line if you are not interested in viewing the json
        # result.
        result = response.json()
        print(result)

        print(json.dumps({"access_token": result["access_token"]}, indent=2))

    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": str(e)}, indent=2))


if __name__ == "__main__":
    get_access_token()
