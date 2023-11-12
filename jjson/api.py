from .extension import *
import json
from bs4 import BeautifulSoup
import requests

def is_html(text):
    return bool(BeautifulSoup(text, "html.parser").find())
        
def is_json(text):
    """
    :param text: text to check
    :return: True if json, False if not
    """
    try:
        json.loads(json.dumps(text))
        return True
    except:
        return False

def is_valid_json(json_string):
    try:
        if isinstance(json_string, dict):
            return True
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False
    
def from_text(text):
    """
    :param text: text to parse
    :return: JJSONExten object
    """
    lst1 = extract_json_objects(text)
    lst2 = json_fromprops(text)
    list_of_dict1 = list(filter(None,lst1))
    list_of_dict2 = list(filter(None,lst2))
    list_of_dict = list_of_dict1 + list_of_dict2
    # remove list types from list
    list_of_dict = [x for x in list_of_dict if not isinstance(x, list)]
    # merge jsons
    mdict = merge_jsons(list_of_dict)
    remdups = remove_duplicates(mdict)
    return JsonExten(remdups)

def from_html(html):
    """
    :param html: html to parse
    :return: JJSONExten object
    """
    text = BeautifulSoup(html, 'html.parser')
    lst1 = extract_json_objects(str(text))
    lst2 = json_fromprops(str(text))
    list_of_dict1 = list(filter(None,lst1))
    list_of_dict2 = list(filter(None,lst2))
    list_of_dict = list_of_dict1 + list_of_dict2
    # remove list types from list
    list_of_dict = [x for x in list_of_dict if not isinstance(x, list)]
    # merge jsons
    mdict = merge_jsons(list_of_dict)
    remdups = remove_duplicates(mdict)
    return JsonExten(remdups)
 


def from_json(jsoncontent):
    """
    :param json: json to parse
    :return: JJSONExten object
    """
    if is_valid_json(jsoncontent):
        return JsonExten(jsoncontent)
    raise Exception("Not a valid json")
 

def from_url(url,method="GET",data=None,headers=None):
    """
    :param url: url to parse
    :param method: request method
    :param data: request data
    :param headers: request headers
    :return: JJSONExten object
    """
    text = requests.request(method, url, data=data, headers=headers).text
    strhtml = from_text(text)
    return strhtml



 
 




