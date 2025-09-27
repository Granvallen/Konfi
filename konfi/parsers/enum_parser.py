
from openpyxl.worksheet.worksheet import Worksheet

from .parser import Parser, SheetType, SheetConfig
from ..etypes import EType, EEnum, EnumPack


class EnumParser(Parser):
    """ 枚举表解析器
    """

    def __init__(self):
        super().__init__()
        
        self._ws = None # 当前处理工作表
        self._data = None
        self._enum_data = None
        self._col_config = None # 记录各列的配置, key 列数, val 配置 { 1: { "!var": "enum_cls" }, ... }
        self._info = None
        
        self._cfg_names = [
            SheetConfig.VAR,
        ]

    def _clear(self):
        """ 清理缓存
        """
        self._ws = None
        self._data = None
        self._enum_data = None
        self._col_config = None
        self._info = None

    # ---------------------- 解析配置 ---------------------------------
    
    def _parse_config(self, r: int, row: tuple):
        """ 解析配置
        """
        row_0 = row[0]
        for c, val in enumerate(row): # 遍历列
            if c == 0 or val is None:
                continue
            
            
            if row_0 == SheetConfig.VAR: # 变量名行
                if val.startswith("#"): # 注释列
                    continue

                self._col_config.setdefault(c, {})

            elif c not in self._col_config:
                continue
            

            cfg = self._col_config[c]
            cfg[row_0] = val


    def _parse_config_rows(self, ws: Worksheet):
        """ 解析配置行
        """
        for r, row in enumerate(ws.iter_rows(values_only=True)):
            row = self._clean_row_data(row)
            if not any(row) or row[0] == "#": # 跳过空行 与 注释行
                continue
            
            if row[0] not in self._cfg_names: # 非配置行结束解析
                break

            self._parse_config(r, row)
    
    # -------------------------- 解析数据 -------------------------------

    def _parse_data(self, r: int, row: tuple):
        """ 解析数据
        """
        row_data: dict[str, EType] = {}
        for c, val in enumerate(row): # 遍历列
            if c == 0 or (c not in self._col_config): # 跳过第一列 与 未配置的列
                continue 
            
            cfg = self._col_config[c]
            var = cfg[SheetConfig.VAR]
            row_data[var] = val
        
        data = self._data
        val = row_data["enum_cls"]
        if val in data:
            data = data[val]
        else:
            data = data.setdefault(val, {
                "enum_cls"       : val,
                "enum_cls_alias" : row_data.get("enum_cls_alias", None),
                "enum_dict_name" : {},
                "enum_dict_alias": {},
            })
        
        enum_name = row_data["enum_name"]
        enum_alias = row_data.get("enum_alias", None)
        enum_val = row_data["enum_val"]

        pack = EnumPack(enum_name, enum_alias, enum_val)
        data["enum_dict_name"][enum_name] = pack
        
        if enum_alias:
            data["enum_dict_alias"][enum_alias] = pack
    

    def _parse_data_rows(self, ws: Worksheet):
        """ 解析数据行
        """
        for r, row in enumerate(ws.iter_rows(values_only=True)):
            row = self._clean_row_data(row)
            if not any(row) or (row[0] and row[0].startswith(("#", "!"))):  # 跳过空行 配置行 注释行
                continue
            
            self._parse_data(r, row)
        
        # 注册解析出的枚举类型
        for enum_cls, val in self._data.items():
            eenum = EEnum(val)
            self._data[enum_cls] = eenum
            self._enum_data[enum_cls] = eenum

    # -----------------------------------------------------------------

    @property
    def sheet_type(self) -> SheetType:
        return SheetType.ENUM

    @classmethod
    def filter(cls, ws: Worksheet) -> bool:
        return ws.title.endswith("_enum")

    def parse(self, ws: Worksheet, data: dict, enum_data: dict):
        self._ws = ws
        self._data = data
        self._enum_data = enum_data
        self._col_config = {}
        self._info = {
            "title": ws.title,
        }
        
        # 1. 解析配置行
        self._parse_config_rows(ws)
        
        # 2. 解析数据行
        self._parse_data_rows(ws)
        
        # 
        # self._data["_config"] = self._col_config
        data["_info"] = self._info
        
        # 3. 清理状态
        self._clear()



