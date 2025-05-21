from json import JSONEncoder


class NebulaSerializer(JSONEncoder):
    def default(self, obj):
        if(hasattr(obj,'__dict__')):
            return obj.__dict__
