
class Dialect(object):
   
    def __init__(self, code):
        self.code = code

    def has_seq(self):
        return False

    def has_if(self):
        return False

    def has_ifelse(self):
        return False
    
    def has_for(self):
        return False
    
    def has_while(self):
        return False

