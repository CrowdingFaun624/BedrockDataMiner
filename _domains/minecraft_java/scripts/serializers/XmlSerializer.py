from typing import TYPE_CHECKING, Any, NotRequired, TypedDict

import defusedxml.ElementTree as defusedxml

import Serializer.Serializer as Serializer

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

__all__ = ("XmlSerializer",)

class ElementTypedDict(TypedDict):
    tag: str
    attrib: NotRequired[dict[str, Any]]
    text: NotRequired[str]
    children: NotRequired[list["ElementTypedDict"]]
    tail: NotRequired[str]

class XmlSerializer(Serializer.Serializer):

    def encode_xml_element(self, data:"Element") -> ElementTypedDict:
        output:ElementTypedDict = {
            "tag": data.tag,
        }
        if len(data.attrib) > 0:
            output["attrib"] = data.attrib
        if data.text is not None and len(data.text.strip()) > 0:
            output["text"] = data.text
        if data.tail is not None and len(data.tail.strip()) > 0:
            output["tail"] = data.tail
        if len(children := [self.encode_xml_element(child) for child in data]) > 0:
            output["children"] = children
        return output

    def deserialize(self, data: bytes) -> ElementTypedDict:
        root = defusedxml.fromstring(data)
        return self.encode_xml_element(root)
