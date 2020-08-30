from typing import Dict, List, Union


FieldList = List['irbis.field.Field']
SubField = 'irbis.subfield.SubField'
SubFieldList = List[SubField]
SubFieldsDict = Dict[str, str]
FieldValue = Union[
    SubField,
    SubFieldList,
    SubFieldsDict,
    str,
    None
]
