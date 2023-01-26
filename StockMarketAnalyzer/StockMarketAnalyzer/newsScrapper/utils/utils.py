"""Utils functions file for stock news and data fetching."""
import json
import requests


GET_STOCK_ID_URL = "https://www.moneycontrol.com/mccode/common/autosuggestion_solr.php"


def get_stock_id(name):
    """
    Function to extract stock id for moneycontrol.
    """
    res = requests.get(
        url=GET_STOCK_ID_URL,
        params={
            "classic": "true",
            "query": name,
            "type": 1,
            "format": "json"
        },
        timeout=5,
    )
    return json.loads(res.text)[0]["sc_id"]
