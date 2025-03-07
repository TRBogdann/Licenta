
def Logger():
    
    def __init__(self, filename):
        self.filename = filename
    
    def __print(self,key:str,value:str):
        
        if not isinstance(str, key):
            raise TypeError("Key should be of type string")
        
        if not isinstance(str, value):
            raise TypeError("Value should be of type string")
        
        open(text,"a").write(f'[{key}]:{value}')
        
    def print(self,text:str):
            self.__print('INFO',text)
        
    def warn(self,text:str):
            self.__print('WARN',text)
            
    def error(self,text:str):
            self.__print('ERROR',text)
        
            