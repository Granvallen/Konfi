
from typing import Any
from .etype import EType

class EString(EType):
    """ 字符串
    """
    etype_tag = "string"
    default = ""

    def __init__(self, val: Any, nullable: bool=False):
        super().__init__(val, nullable)

        self._convert()

    def __repr__(self):
        if self.py_val is None:
            return repr(self.py_val)

        return f'"{self.py_val}"'

    def _convert(self):
        if self.val is None:
            if self.nullable:
                self.py_val = None
            else:
                self.py_val = self.__class__.default
                
            return

        try:
            self.py_val = str(self.val)
        except ValueError:
            raise ValueError(f"无法将值 {self.val} 转换为 {type(self).__name__}") from None


