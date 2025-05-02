from datetime import datetime

class EntityProperties(object):
    def default(self, o):
        return o.__dict__
    
    id:int = None
    entityid:int = None
    name:str = None
    sourcename:str = None
    destname:str = None
    datatype:str = None
    length:str = None
    isidentifier:bool = None
    defaultvalue:str = None
    createondate:str = datetime.now()
    modifyondate:str = datetime.now()