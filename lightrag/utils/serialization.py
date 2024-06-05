import json
import logging
import os
import pickle
from typing import Mapping, Any, Optional, List, Dict, Union


log = logging.getLogger(__name__)


def default(o: Any) -> Union[Dict[str, Any], str]:
    seralized_obj = {}
    # (1) For most objects within lightRAG, to_dict() is the method to serialize the object
    if hasattr(o, "to_dict") and callable(getattr(o, "to_dict")):
        try:
            seralized_obj = o.to_dict()
            return seralized_obj
        except Exception as e:
            pass

    # (2) Fallback to serializing attributes who come from external libraries
    try:

        return {"type": type(o).__name__, "data": str(o)}
    except Exception as e:
        raise TypeError(
            f"Object of type {o.__class__.__name__} is not JSON serializable: {str(e)}"
        )


def serialize(obj: Mapping[str, Any]) -> str:
    """Serialize the object to a json string.

    Args:
        obj (Mapping[str, Any]): The object to be serialized.

    Returns:
        str: The serialized object in json format.
    """

    return json.dumps(obj, indent=4, default=default)


# TODO: make this more clear
def save(obj: Mapping[str, Any], f: str = "task") -> None:
    __doc__ = """Save the object to a json file.

    We save two versions of the object:
    - task.json: the object itself with Parameter serialized to dict
    - task.pickle: the object itself with Parameter as is
    """

    # save the object to a json file
    json_f = f"{f}.json"

    os.makedirs(os.path.dirname(json_f) or ".", exist_ok=True)
    with open(json_f, "w") as file:
        # serialize the object with the default function
        # serialized_obj = serialize(obj)
        # file.write(serialized_obj, indent=4)
        json.dump(obj, file, indent=4, default=default)

    # save the object to a pickle file
    pickle_f = f"{f}.pickle"
    with open(pickle_f, "wb") as file:
        pickle.dump(obj, file)


def save_json(obj: Mapping[str, Any], f: str = "task.json") -> None:
    __doc__ = """Save the object to a json file.

    Args:
        obj (Mapping[str, Any]): The object to be saved.
        f (str, optional): The file name. Defaults to "task".
    """
    os.makedirs(os.path.dirname(f) or ".", exist_ok=True)
    try:
        with open(f, "w") as file:
            json.dump(obj, file, indent=4, default=default)
    except IOError as e:
        raise IOError(f"Error saving object to JSON file {f}: {e}")


def save_pickle(obj: Mapping[str, Any], f: str = "task.pickle") -> None:
    __doc__ = """Save the object to a pickle file.

    Args:
        obj (Mapping[str, Any]): The object to be saved.
        f (str, optional): The file name. Defaults to "task".
    """
    os.makedirs(os.path.dirname(f) or ".", exist_ok=True)
    try:
        with open(f, "wb") as file:
            pickle.dump(obj, file)
    except Exception as e:
        raise Exception(f"Error saving object to pickle file {f}: {e}")


def save(obj: Mapping[str, Any], f: str = "task") -> None:
    __doc__ = r"""Save the object to both a json and a pickle file.

    We save two versions of the object:
    - task.json: the object itself with Parameter serialized to dict
    - task.pickle: the object itself with Parameter as is
    """

    try:
        save_json(obj, f=f"{f}.json")
        save_pickle(obj, f=f"{f}.pickle")
    except Exception as e:
        raise Exception(f"Error saving object to json and pickle files: {e}")


def load_json(f: str = "task.json") -> Optional[Mapping[str, Any]]:
    __doc__ = r"""Load the object from a json file.

    Args:
        f (str, optional): The file name. Defaults to "task".
    """
    if not os.path.exists(f):
        log.warning(f"File {f} does not exist.")
        return None
    try:
        with open(f, "r") as file:
            return json.load(file)
    except Exception as e:
        raise Exception(f"Error loading object from JSON file {f}: {e}")


def load_pickle(f: str = "task.pickle") -> Optional[Mapping[str, Any]]:
    __doc__ = r"""Load the object from a pickle file.

    Args:
        f (str, optional): The file name. Defaults to "task".
    """
    if not os.path.exists(f):
        log.warning(f"File {f} does not exist.")
        return None
    try:
        with open(f, "rb") as file:
            return pickle.load(file)
    except Exception as e:
        raise Exception(f"Error loading object from pickle file {f}: {e}")


def load(f: str = "task") -> Optional[Mapping[str, Any]]:
    __doc__ = r"""Load both the json and pickle files and return the object from the json file

    Args:
        f (str, optional): The file name. Defaults to "task".
    """
    try:
        json_obj = load_json(f=f"{f}.json")
        obj = load_pickle(f=f"{f}.pickle")
        return json_obj, obj
    except Exception as e:
        raise Exception(f"Error loading object from json and pickle files: {e}")


def load_jsonl(f: str = None) -> List[Dict[str, Any]]:
    __doc__ = r"""Load a jsonl file and return a list of dictionaries.

    Args:
        f (str, optional): The file name. Defaults to None.
    """
    try:
        import jsonlines
    except ImportError:
        raise ImportError("Please install jsonlines to use this function.")
    if not os.path.exists(f):
        log.warning(f"File {f} does not exist.")
        return []

    try:
        with jsonlines.open(f) as reader:
            return list(reader)
    except Exception as e:
        log.error(f"Error loading jsonl file {f}: {e}")
        return []


def append_to_jsonl(f: str, data: Dict[str, Any]) -> None:
    __doc__ = r"""Append data to a jsonl file.

    Args:
        f (str): The file name.
        data (Dict[str, Any]): The data to be appended.
    """
    try:
        import jsonlines
    except ImportError:
        raise ImportError("Please install jsonlines to use this function.")
    os.makedirs(os.path.dirname(f) or ".", exist_ok=True)
    try:
        with jsonlines.open(f, mode="a") as writer:
            writer.write(data)
    except Exception as e:
        log.error(f"Error appending data to jsonl file {f}: {e}")


def write_list_to_jsonl(f: str, data: List[Dict[str, Any]]) -> None:
    __doc__ = r"""Write a list of dictionaries to a jsonl file.

    Args:
        f (str): The file name.
        data (List[Dict[str, Any]]): The data to be written.
    """
    try:
        import jsonlines
    except ImportError:
        raise ImportError("Please install jsonlines to use this function.")
    os.makedirs(os.path.dirname(f) or ".", exist_ok=True)
    try:
        with jsonlines.open(f, mode="w") as writer:
            for d in data:
                writer.write(d)
    except Exception as e:
        log.error(f"Error writing data to jsonl file {f}: {e}")
