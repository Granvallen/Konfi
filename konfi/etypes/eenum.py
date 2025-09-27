from __future__ import annotations

from dataclasses import dataclass
from .etype import EType

@dataclass(slots=True)
class EnumPack:
    name : str = None
    alias: str = None
    val  : int = None


class EEnumVal(EType):
    """ 枚举值
    """
    etype_tag = "enumval"
    
    def __init__(self, val: str, nullable, eenum: EEnum):
        super().__init__(val, nullable)
        
        self.eenum = eenum
        self.enum_val = None
        
        self._convert()
        
    def __repr__(self):
        return self.py_val if self.py_val else repr(self.py_val)
        
    def _convert(self):
        if self.val is None:
            if self.nullable:
                self.py_val = None
            else:
                raise ValueError(f"{self.eenum.enum_cls} 枚举值不能为空") from None
            
            return

        if pack := self.eenum.enum_dict_name.get(self.val, None):
            self.py_val = f"{self.eenum.enum_cls}.{self.val}"
            self.enum_val = pack.val

        elif pack := self.eenum.enum_dict_alias.get(self.val, None):
            self.py_val = f"{self.eenum.enum_cls}.{pack.name}"
            self.enum_val = pack.val
            
        else:
            raise ValueError(f"无法将值 {self.val} 转换为 {type(self).__name__}") from None
    
        self.enums = { self.eenum.enum_cls }

class EEnum(EType):
    """ 枚举
    """
    etype_tag = "enum"
    

    def __init__(self, val: dict, nullable=False):
        super().__init__(val, nullable)

        self.enum_cls: str = None
        self.enum_cls_alias: str = None # 可空
        self.enum_dict_name: dict[str, EnumPack] = {} # { enum_name: enum_val }
        self.enum_dict_alias: dict[str, EnumPack] = {} # { enum_name_alias: enum_val }
        
        self._convert()
        
    def __repr__(self):
        s = [f"class {self.enum_cls}(Enum):\n"]
        
        if self.enum_cls_alias:
            s.append(f'    """ {self.enum_cls_alias}\n    """\n')
            
        max_name_len = max(len(n) for n in self.enum_dict_name)
        max_val_len = max(len(str(p.val)) for p in self.enum_dict_name.values())
        for pack in self.enum_dict_name.values():
            alias = pack.alias and f"# {pack.alias}" or ""
            s.append(f"    {pack.name:{max_name_len}} = {pack.val:<{max_val_len}} {alias}\n")

        return "".join(s)

    def _convert(self):
        if self.val is None:
            raise ValueError(f"EEnum val 不能为 None") from None

        try:
            self.py_val = self.val
            self.enum_cls = self.val["enum_cls"]
            self.enum_cls_alias = self.val.get("enum_cls_alias", None)
            self.enum_dict_name = self.val["enum_dict_name"]
            self.enum_dict_alias = self.val["enum_dict_alias"]
            
            # 处理 auto
            count = 0
            for pack in self.enum_dict_name.values():
                if pack.val == "auto":
                    pack.val = count
                    count += 1
            
        except ValueError:
            raise ValueError(f"无法将值 {self.val} 转换为 {type(self).__name__}") from None


