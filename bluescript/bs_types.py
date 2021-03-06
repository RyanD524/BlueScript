
## important constants / most keywords or char pairs used in blue script
COMMENT_CHAR = "//" ## comments
TO_CHAR      = "->" ## goes to
null         = None ## just for null

## this is called in builtin.blue_logicalIf() 
## used for logical operations (goif, and if)
LOGIC_EQUALS  = "=="
LOGIC_GREATER = ">"
LOGIC_LESSER  = "<"
LOGIC_GEQL    = ">="
LOGIC_LEQL    = "<="
LOGICAL_NOT   = "!=" 

## moved LOGIC_GREATER and LOGIC_LESSer
## caused issue with matching later
LOGIC_ARRAY = [LOGIC_EQUALS,LOGIC_GEQL,LOGIC_LEQL,LOGIC_GREATER,LOGIC_LESSER,LOGICAL_NOT]

## used in math operations and string manipulation
## used mostly in set might get used in other places
MATH_ADD     = "+"
MATH_SUB     = "-"
MATH_MUL     = "*"
MATH_DIV     = "/"
MATH_POW     = "^"

MATH_ARRAY = [MATH_ADD,MATH_SUB,MATH_MUL,MATH_DIV,MATH_POW]

class BLUE_ARRAY:
    def __init__(self, data, size):
        self.data = data ## list
        self.size = size

    def array_get(self, index):
        if index == -1:
            return self.data
        
        if index <= len(self.data):
            return self.data[index]
        
        raise Exception(f"Index : {index} is out of range.")
    
    def append(self, value):
        self.data.append(value)


## may do later rework might not be needed as of yet
## rework types
class BLUE_INT:
    def __init__(self, data):
        self.data = data
        
    def data_get(self):
        return self.data
    
class BLUE_FLOAT:
    def __init__(self, data):
        pass
    
class BLUE_STRING:
    def __init__(self, data):
        pass
    
class BLUE_BOOL:
    def __init__(self, data):
        pass