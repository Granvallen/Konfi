
from openpyxl.worksheet.worksheet import Worksheet
from typing import Any

from .parser import Parser, SheetType, SheetConfig
from ..etypes import EType, EEnum, EnumPack, EEnumVal


class KVParser(Parser):
    """ 键值表解析器
    """

    def __init__(self):
        super().__init__()
        
        self._ws = None # 当前处理工作表
        self._data = None
        self._enum_data = None # 记录当前支持的枚举类型
        self._col_config = None # 记录各列的配置, key 列数, val 配置
        self._var_config = None # 记录 key 为 var 的配置
        self._info = None # 其他关于该 sheet 的信息
        
        self._cfg_names = [
            SheetConfig.VAR,
            SheetConfig.TYPE,
            SheetConfig.LABEL,
        ]

    def _clear(self):
        """ 清理缓存
        """
        self._ws = None
        self._data = None
        self._enum_data = None
        self._col_config = None
        self._var_config = None
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

                if val in self._var_config:
                    config = self._var_config[val]
                else:
                    config = {}
                    self._var_config[val] = config

                if c not in self._col_config:
                    self._col_config[c] = config

            elif c not in self._col_config: # 跳过没有变量名的列
                continue

            cfg = self._col_config[c]
            if row_0 == SheetConfig.PARAM:
                if row_0 in cfg:
                    cfg[row_0].append(val)
                else:
                    cfg[row_0] = [val]
            else:
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
        row_data: dict[str, list[Any]] = {}
        
        for c, val in enumerate(row): # 遍历列
            if c == 0 or (c not in self._col_config): # 跳过第一列 与 未配置的列
                continue 
            
            cfg = self._col_config[c]
            var = cfg[SheetConfig.VAR]
        
            if var not in row_data:
                row_data.setdefault(var, [])
            
            row_data[var].append(val)
        
        for var, data_list in row_data.items():
            cfg = self._var_config[var]
            etype = cfg[SheetConfig.TYPE]
            param = cfg.get(SheetConfig.PARAM, None)
        
            try:
                if param is None:
                    etype = EType.create(etype, data_list, self._enum_data)
                else:
                    etype = EType.create(etype, data_list, self._enum_data, param)
                
            except Exception:
                raise Exception(f"[konfi] KVParser {self._ws.title} 第 {r+1} 行解析数据出错")
            
            row_data[var] = etype
            
            if etype.enums: # 记录 sheet 用到的枚举类型
                self._info["enums"] |= etype.enums
        
            if etype.refs:
                self._info["refs"] |= etype.refs

        # 重构数据结构
        data = self._data
        key: EType = row_data["key"]
        if key in data:
            print(f"[konfi] 警告: {self._ws.title} 第 {r+1} 行 key {key} 已存在, 发生配置覆盖")
        
        data[key] = row_data["val"]
            

    def _parse_data_rows(self, ws: Worksheet):
        """ 解析数据行
        """
        for r, row in enumerate(ws.iter_rows(values_only=True)):
            row = self._clean_row_data(row)
            if not any(row) or (row[0] and row[0].startswith(("#", "!"))):  # 跳过空行 配置行 注释行
                continue
            
            self._parse_data(r, row)

    # -----------------------------------------------------------------

    @property
    def sheet_type(self) -> SheetType:
        return SheetType.KV

    @classmethod
    def filter(cls, ws: Worksheet) -> bool:
        return ws.title.endswith("_kv")

    def parse(self, ws: Worksheet, data: dict, enum_data: dict):
        self._ws = ws
        self._data = data
        self._enum_data = enum_data
        self._col_config = {}
        self._var_config = {}
        self._info = {
            "title": ws.title,
            "enums": set(),
            "refs": set(),
        }
        
        # 1. 解析配置行
        self._parse_config_rows(ws)
        
        # 2. 解析数据行
        self._parse_data_rows(ws)
        
        # 3. 填充额外信息
        data["_config"] = self._var_config
        data["_info"] = self._info
        
        # 4. 清理状态
        self._clear()


