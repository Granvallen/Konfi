
from __future__ import annotations
from typing import Callable
from openpyxl.worksheet.worksheet import Worksheet
from enum import Enum, auto, StrEnum


class SheetType(Enum):
    COMMON = auto()
    ENUM   = auto()
    KV     = auto()
    OTHERS = auto()
    
class SheetConfig(StrEnum):
    """ 用 ! 标记配置行开始
    """
    VAR   = "!var"   # 字段名行
    TYPE  = "!type"  # 类型行
    LABEL = "!label" # 标签行
    PARAM = "!param" # 参数行, 参数列表

class ParserMeta(type):
    """ 解析器元类, 注册派生解析器到基类 _reg_parsers_cls
    """
    
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

        if "_reg_parsers_cls" in namespace:
            return

        for base in bases:
            if hasattr(base, "_reg_parsers_cls"):
                base._reg_parsers_cls[name] = cls
                break


class Parser(metaclass=ParserMeta):
    """ sheet 解析类
    """
    
    _reg_parsers_cls: dict[str, type[Parser]] = {}
    _parsers: dict[str, Parser] = {} # 单例
    
    matcher: set[str] = set() # 列出的 sheet 将使用该解析器
    
    
    def _clean_row_data(self, row: tuple) -> tuple:
        """ 清理行数据
            1. 纯空格的单元视为 None
        """
        return tuple(None if (isinstance(c, str) and not c.strip()) else c for c in row)

    
    # --------------------------------------------------------------------------------
    
    @classmethod
    def get_parser(cls, name):
        """ 获取注册的解析器
        """
        if cls is not Parser:
            raise TypeError(f"{cls.__name__} 不能调用 get_parser")
        
        if name in cls._parsers:
            return cls._parsers[name]
        
        parser_cls = cls._reg_parsers_cls.get(name, None)
        if parser_cls:
            parser = parser_cls()
            cls._parsers[name] = parser
            return parser
        
        else:
            raise ValueError(f"解析器 {name} 未注册")
    
    
    @classmethod
    def get_reg_parsers(cls) -> dict[str, type[Parser]]:
        """ 获取所有注册的解析器
        """
        if cls is not Parser:
            raise TypeError(f"{cls.__name__} 不能调用 get_reg_parsers")
        
        for name, _ in Parser._reg_parsers_cls.items():
            Parser.get_parser(name)
        
        return Parser._parsers
    
    # --------------------------------------------------------------------------------

    @property
    def sheet_type(self) -> SheetType:
        return SheetType.OTHERS
    
    @classmethod
    def filter(cls, ws: Worksheet) -> bool:
        """ 判断 sheet 是否匹配解析器, 子类可选择实现
        """
        return True

    def parse(self, ws: Worksheet, data: dict) -> None:
        """ 解析 sheet
        """
        raise NotImplementedError("子类必须实现 parse 方法")
        
        
        