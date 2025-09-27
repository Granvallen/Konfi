
from typing import Any
from .etype import EType

class EBool(EType):
    """ 布尔
    """
    etype_tag = "bool"
    default = False
    
    def __init__(self, val: Any, nullable: bool = False):
        super().__init__(val, nullable)

        self._convert()

    def _convert(self):
        if self.val is None:
            if self.nullable:
                self.py_val = None
            else:
                self.py_val = self.__class__.default

            return

        if self.val in ("否", "N", "0"):
            self.py_val = False
            
        elif self.val in ("是", "Y", "1"):
            self.py_val = True
        
        else:
            raise ValueError(f"无法将值 {self.val} 转换为 {type(self).__name__}") from None


