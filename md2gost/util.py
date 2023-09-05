from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml.etree import _Element


def create_element(name: str, *args: dict[str, str] | list[_Element] | str)\
        -> _Element:
    """Creates an OxmlElement

    Variable arguments:
    * dict -- element's attributes
    * list -- element's children
    * string -- element's text
    """
    attrs = {}
    children = []
    text = None

    for arg in args:
        if isinstance(arg, dict):
            attrs.update(arg)
        elif isinstance(arg, list):
            children.extend(arg)
        elif isinstance(arg, str):
            text = arg

    element = OxmlElement(name, {
        (qn(name) if ":" in name else name): value for name, value in attrs.items()
    })
    for child in children:
        element.append(child)
    if text:
        element.text = text
    return element


def merge_objects(*objects):
    from inspect import getmembers, ismethod
    """
    Returns the new object containing attributes from objects, where the latest
    one has the highest priority.
    """

    class MergedObject:
        pass

    merged_object = MergedObject()
    for name, value in getmembers(objects[0]):
        if name.startswith("_") or ismethod(value):
            continue
        merged_object.__setattr__(name, value)

    for object_ in objects[1:]:
        for name, value in getmembers(object_):
            if name.startswith("_") or ismethod(value):
                continue
            if value is not None:
                merged_object.__setattr__(name, value)

    return merged_object
