
from typing import Any
from .etype import EType

class EList(EType):
    """ 单格列表, 泛型类型
        元素类型必须是单格的
    """
    etype_tag = "list"
    default = []

    def __init__(
        self, 
        val: Any, 
        nullable: bool, 
        enum_data: dict[str, EType], 
        etype_args: list[Any], 
        param: list[Any]=None
    ):
        val = val if val is None else str(val)
        super().__init__(val, nullable)

        self.etype_args = etype_args
        self.sep = param[0] if param else ","

        self._convert(enum_data)

    def _convert(self, enum_data):
        if self.val is None:
            if self.nullable:
                self.py_val = None
            else:
                self.py_val = self.__class__.default

            return

        try:
            etype: str = self.etype_args[0]
            
            # 枚举引用
            self.enums = set()
            etype_tag = etype[:-1] if etype.endswith("?") else etype
            
            if etype_tag in enum_data:
                self.enums.add(etype_tag)            
            
            self.py_val = []

            for item in [s.strip() for s in self.val.split(self.sep)]:
                val = EType.create(etype, [item or None], enum_data)
                self.py_val.append(val)

        except ValueError:
            raise ValueError(f"无法将值 {self.val} 转换为 {type(self).etype_tag}")



class EListM(EType):
    """ 多格列表, 泛型类型
    """
    etype_tag = "list_m"
    single_cell = False
    default = []

    def __init__(
        self, 
        val: Any, 
        nullable: bool, 
        enum_data: dict[str, EType], 
        etype_args: list[Any]
    ):
        super().__init__(val, nullable)

        self.etype_args = etype_args
        
        self._convert(enum_data)

    def _convert(self, enum_data):
        if self.val is None:
            if self.nullable:
                self.py_val = None
            else:
                self.py_val = self.__class__.default

            return

        try:
            etype: str = self.etype_args[0]
            
            # 枚举引用
            self.enums = set()
            etype_tag = etype[:-1] if etype.endswith("?") else etype
            
            if etype_tag in enum_data:
                self.enums.add(etype_tag)
            
            self.py_val = []
            for item in self.val:
                val = EType.create(etype, [item], enum_data)
                self.py_val.append(val)

        except ValueError:
            raise ValueError(f"无法将值 {self.val} 转换为 {type(self).etype_tag}")
