import pandas as pd
from json import JSONDecoder
import json
from bs4 import BeautifulSoup


def extract_json_objects(text, decoder=JSONDecoder()):
    """Find JSON objects in text, and yield the decoded JSON data

    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object.

    """
    pos = 0
    while True:
        match = text.find("{", pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            yield result
            pos = match + index
        except ValueError:
            pos = match + 1

def merge_jsons(list_of_dict):
    d = {}
    for dic in list_of_dict:
        for key, value in dic.items():
            if key not in d:
                d[key] = value
            elif isinstance(d[key], list):
                d[key].append(value)
            else:
                d[key] = [d[key], value]
    return d

def json_fromprops(text):
    soup = BeautifulSoup(text, "lxml")
    json_objects = set()  # Use a set to avoid duplicates

    def extract_json_from_string(string):
        try:
            json_obj = json.loads(string)
            if isinstance(json_obj, (dict, list)):
                json_objects.add(json.dumps(json_obj))  # Convert to string for comparison
        except:
            pass

    # Find all elements with attributes or properties that contain JSON
    for tag in soup.find_all():
        for attr in tag.attrs:
            extract_json_from_string(tag[attr])

        for prop in dir(tag):
            if prop.startswith("__"):
                continue
            prop_value = getattr(tag, prop)
            if isinstance(prop_value, str):
                extract_json_from_string(prop_value)

    return [json.loads(obj) for obj in json_objects]  # Convert back to JSON objects



def remove_duplicates(obj):
    """
    Recursively remove duplicates from a nested dictionary or list
    """
    if isinstance(obj, dict):
        deduped_obj = {}
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                deduped_obj[key] = remove_duplicates(value)
            else:
                deduped_obj[key] = value
        return deduped_obj
    elif isinstance(obj, list):
        deduped_list = []
        for item in obj:
            if item not in deduped_list:
                deduped_list.append(remove_duplicates(item))
        return deduped_list
    else:
        return obj


class JsonExten:
    def __init__(self, json_content) -> None:
         self.json_content = json_content
         self._path_table = self.path_table(json_content)


    def __str__(self):
        if isinstance(self.json_content,dict):
            return json.dumps(self.json_content)
        return self.json_content

    def to_dict(self):
        return self.json_content
    
    def to_jsonstr(self):
        if isinstance(self.json_content,dict):
            return json.dumps(self.json_content)
        return self.json_content


    def get_paths(self,json_object):
        """Get all paths in a JSON object including list"""
        def get_paths_helper(json_object, path):
            if isinstance(json_object, dict):
                for key, value in json_object.items():
                    yield from get_paths_helper(value, path + [key])
            elif isinstance(json_object, list):
                for index, value in enumerate(json_object):
                    yield from get_paths_helper(value, path + [str(index)])
            else:
                yield path

        yield from get_paths_helper(json_object, [])


    def convert_to_dict_path(self,lst):
        """Convert a list of keys to a dictionary path"""
        result = ''
        for key in lst:
            if key.isdigit():
                result += f'[{key}]'
            else:
                result += f'["{key}"]'
        return result

    @property
    def paths(self):
        """Get all paths in a JSON object including list"""
        return self._path_table
    

    def path_table(self,json_content):
        """Get all paths in a JSON object including list and return a dataframe with the path, key and value of each path in the JSON object

        Args:
            json_content (dict):  JSON object

        Returns:
            (Dataframe):  Dataframe
        """    
    
        list_paths = self.get_paths(json_content)
        list_paths = [self.convert_to_dict_path(path) for path in list_paths]
        lst_dict = []
        for path in list_paths:
            try:
                value = eval(f'{json_content}{path}')
                lst_dict.append({'key':path.split('"')[-2],'value':value,'path':path})
            except:
                pass
        
        return pd.DataFrame(lst_dict)
    

    def search(self,key_contains=None,value_contains=None):
        """Search for a string in the JSON object

        Args:
            search_string (str):  String to search for

        Returns:
            (Dataframe):  Dataframe
        """
        if key_contains is not None:
            return self._path_table[self._path_table['key'].astype(str).str.contains(key_contains)]
        elif value_contains is not None:
            return self._path_table[self._path_table['value'].astype(str).str.contains(value_contains)]
        else:
            return self._path_table
        

  

