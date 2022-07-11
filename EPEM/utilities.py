import json

def singleton(self, *args, **kw):
    """
    The decorator is used to make sure that only one instance of the class is created in the program.
    """
    instances = {}

    def _singleton(*args, **kw):
        if self not in instances:
            instances[self] = self(*args, **kw)
        return instances[self]
    return _singleton

def read_json_file(file_name: str) -> dict:
    """
    This method is used to read a json file.

    Parameters
    ----------
    file_path : str
        The path to the json file.

    Returns
    -------
    dict
        The json file as a dictionary.
    """
    with open("json_data/" + file_name, 'r') as f:
        return json.load(f)