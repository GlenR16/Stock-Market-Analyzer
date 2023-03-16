"""Utils functions file for stock news and data fetching."""
import json
import requests
from bs4 import BeautifulSoup
import re

GET_STOCK_ID_URL = "https://www.moneycontrol.com/mccode/common/autosuggestion_solr.php"
GET_ET_CODE_URL = "https://economictimes.indiatimes.com/stocksearch.cms"


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

# Economic times stock code to stock id
def get_et_code(name):
    """
    Function to extract Economic Times id for stock name.
    """
    res = requests.get(
        url=GET_ET_CODE_URL,
        params={
            "ticker": name
        },
        timeout=5,     
    )
    soup = BeautifulSoup(res.content, "html.parser")
    try:
        response = soup.li.a.get("data-compid")
    except:
        response = None
    return response