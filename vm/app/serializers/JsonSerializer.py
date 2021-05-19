import json
from serializers.Serializer import Serializer

class JsonSerializer(Serializer):
    """
    Json serializer
    """
    def __init__(self):
        super().__init__()

    def serialize(self, data):
        return json.dumps(data)

    def deserialize(self, data):
        return json.loads(data)
