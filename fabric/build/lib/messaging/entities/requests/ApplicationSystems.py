from datetime import datetime

class ApplicationSystems(object):
    def default(self, o):
        return o.__dict__
    
    id:int = None
    name:str = None
    direction:str
    createondate:str = datetime.now()
    modifyondate:str = datetime.now()
    ispsims:bool = None
    iscardsystem:bool = None
    canaddareas:bool = None
    isenabled:bool = None