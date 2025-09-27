
from typing import Any
from .etype import EType

class EDict(EType):
    """ 单格字典, 泛型类型
    """
    etype_tag = "dict"
    default = {}
    
    def __init__(
        self, 
        val: Any, 
        nullable: bool, 
        enum_data: dict[str, EType], 
        etype_args: list[Any], 
        param: list[Any]=None
    ):
        super().__init__(val, nullable)

        self.etype_args = etype_args
        self.sep1 = param[0] if param else ":" # 分隔键与值
        self.sep2 = param[1] if param else "," # 分隔键值对

        self._convert(enum_data)

    def _convert(self, enum_data):
        if self.val is None:
            if self.nullable:
                self.py_val = None
            else:
                self.py_val = self.__class__.default

            return

        try:
            key_etype: str = self.etype_args[0]
            val_etype: str = self.etype_args[1]
            
            # 枚举引用
            self.enums = set()
            key_tag = key_etype[:-1] if key_etype.endswith("?") else key_etype
            val_tag = val_etype[:-1] if val_etype.endswith("?") else val_etype
            
            if key_tag in enum_data:
                self.enums.add(key_tag)
                
            if val_tag in enum_data:
                self.enums.add(val_tag)
            
            self.py_val = {}
            for item in self.val.split(self.sep2):
                item: list[str] = item.split(self.sep1)
                
                key = EType.create(key_etype, [item[0].strip() or None], enum_data)
                val = EType.create(val_etype, [item[1].strip() or None], enum_data)

                self.py_val[key] = val

        except ValueError:
            raise ValueError(f"无法将值 {self.val} 转换为 {type(self).etype_tag}")







class EDictM(EType):
    """ 多格字典, 泛型类型
        元素类型必须是单格的
    """
    etype_tag = "dict_m"
    single_cell = False

    def __init__(
        self, 
        val: Any, 
        nullable: bool, 
        enum_data: dict[str, EType], 
        etype_args: list[Any], 
        param: list[Any]=None
    ):
        super().__init__(val, nullable)

        self.etype_args = etype_args
        self.param = param
        self.default = {}

        self._convert(enum_data)

    def _convert(self, enum_data):
        if self.val is None:
            if self.nullable:
                self.py_val = None
            else:
                self.py_val = self.default

            return

        try:
            key_etype: str = self.etype_args[0]
            val_etype: str = self.etype_args[1]
            
            # 枚举引用
            self.enums = set()
            key_tag = key_etype[:-1] if key_etype.endswith("?") else key_etype
            val_tag = val_etype[:-1] if val_etype.endswith("?") else val_etype
            
            if key_tag in enum_data:
                self.enums.add(key_tag)
                
            if val_tag in enum_data:
                self.enums.add(val_tag)
            
            
            self.py_val = {}
            if self.param: # key 固定
                for i, k in enumerate(self.param):
                    key = EType.create(key_etype, [k], enum_data)
                    val = EType.create(val_etype, [self.val[i]], enum_data)
                    self.py_val[key] = val
            
            else: # key 非固定
                val_len = len(self.val)
                if val_len % 2 != 0: # 非偶数格
                    raise ValueError(f"dict 类型要求键值对偶数列输入")
                
                for item in [self.val[i:i+2] for i in range(0, val_len, 2)]:
                    key = EType.create(key_etype, [item[0]], enum_data)
                    val = EType.create(val_etype, [item[1]], enum_data)
                    self.py_val[key] = val

        except ValueError:
            raise ValueError(f"无法将值 {self.val} 转换为 {type(self).etype_tag}")

