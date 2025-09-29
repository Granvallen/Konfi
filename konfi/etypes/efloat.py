
from typing import Any
from .etype import EType

class EFloat(EType):
    """ 浮点数
    """
    etype_tag = "float"
    default = 0.0

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

        try:
            self.py_val = float(self.val)

        except ValueError:
            raise ValueError(f"无法将值 {self.val} 转换为 {type(self).__name__}") from None

