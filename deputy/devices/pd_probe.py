

class PDProbe:

    def __init__(self):
        pass

    @classmethod
    def type(self):
        raise NotImplementedError
    
    @classmethod
    def find(self, **kwargs) -> list:
        return []
    
    def open(self):
        raise NotImplementedError
    
    def close(self):
        raise NotImplementedError
