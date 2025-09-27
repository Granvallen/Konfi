from __future__ import annotations
from typing import Any

import re

class ETypeMeta(type):
    """ 类型元类, 注册派生类型到基类 _reg_etypes_cls 列表中
    """
    
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

        if "_reg_etypes_cls" in namespace:
            return

        for base in bases:
            if hasattr(base, "_reg_etypes_cls"):
                base._reg_etypes_cls[cls.etype_tag] = cls
                break



class EType(metaclass=ETypeMeta):
    """ 配置类型
        TODO: 类型可以有自己的特定导出逻辑, 不一定需要改 writer 定制导出内容
    """
    
    _reg_etypes_cls: dict[str, type[EType]] = {}
    _etype_args_re = re.compile(r'\[([^\[\]]*)\]$')
    
    etype_tag: str = None
    single_cell: bool = True # 标记是否为单格类型
    default = None
    
    def __init__(self, val: Any, nullable: bool = False):
        self.val = val
        self.nullable = nullable
        
        self.py_val: Any = None
        self.enums: set[str] = None # 该类型引用的枚举
        self.refs: set[str] = None # 该类型引用的自定义类型
    
    def __eq__(self, other: EType) -> bool:
        return self.py_val == other.py_val
    
    def __hash__(self):
        return hash(self.py_val)
    
    def __repr__(self):
        return repr(self.py_val)
    
    def _convert(self):
        """ 转换为 Python 原生类型
        """
        raise NotImplementedError("子类必须实现 _convert 方法")
    
    
    @classmethod
    def create(
        cls, 
        etype: str, 
        data_list: list[Any], 
        enum_data: dict[str, EType], 
        *args, 
        **wargs,
    ) -> EType:
        """ 创建类型实例
            有两种分类: 
            1. 泛型 / 非泛型, 泛型需要有额外的类型参数 etype_args
            2. 单格 / 多格, 多格时 val 为提取自多格组成的列表
        """
        if cls is not EType:
            raise TypeError(f"{cls.__name__} 不能调用 create")
        
        nullable = etype.endswith("?")
        if nullable:
            etype = etype[:-1]
        
        if eenum := enum_data.get(etype, None): # 枚举类型
            etype_cls = cls._reg_etypes_cls.get("enumval", None)
            return etype_cls(data_list[0], nullable, eenum)
        
        
        idx = etype.find("[")
        if idx == -1: idx = len(etype)

        # etype_tag
        etype_tag = etype[:idx]
        etype_cls = cls._reg_etypes_cls.get(etype_tag, None)
        if etype_cls is None:
            raise ValueError(f"类型 {etype_tag} 未注册")

        # etype_args, 泛型额外类型参数
        if m := cls._etype_args_re.match(etype[idx:]):
            etype_args = [p.strip() for p in m.group(1).split(",")]
        else:
            etype_args = None
        
        # 创建类型实例
        val = data_list[0] if etype_cls.single_cell else data_list
        if etype_args is None: # 非泛型
            return etype_cls(val, nullable, *args, **wargs)
        else: # 泛型
            return etype_cls(val, nullable, enum_data, etype_args, *args, **wargs)
        
