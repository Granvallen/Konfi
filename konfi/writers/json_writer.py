
from pathlib import Path
import json

from .writer import Writer
from ..etypes import *
from ..parsers import SheetType

class JsonWriter(Writer):
    """ json 写入器
    """
    ext = "json"
    
    def _serializer(self, obj, is_key=False):
        match obj:
            case EEnumVal():
                obj = obj.enum_val
            case EnumPack():
                obj = obj.val
            case EDictM() | EDict():
                obj = { self._serializer(k, True): self._serializer(v) for k, v in obj.py_val.items() }
            case EListM() | EList():
                obj = [ self._serializer(v) for v in obj.py_val ]
            case ESetM() | ESet():
                obj = { self._serializer(v): True for v in obj.py_val }
            case EEnum():
                obj = obj.enum_dict_name
            case EType():
                obj = obj.py_val

        return str(obj) if is_key else obj

    
    def write(
        self, 
        data: dict[str, dict],
        data_path: Path,
    ) -> None:

        config_path = data_path / "config"
        enum_path = data_path / "enum"
        
        config_path.mkdir(parents=True, exist_ok=True)
        enum_path.mkdir(parents=True, exist_ok=True)
        
        # 辅助
        enum_sheets = []
        modules: list[str] = []
        
        for sheet_name, sheet_data in data.items():
            config = sheet_data.pop("_config", None)
            primary = sheet_data.pop("_primary", None)
            info = sheet_data.pop("_info", None)
            table_sheet = f"{info['table_path'].name}/{info['title']}"
            
            sheet_type = info["sheet_type"]
            is_enum_sheet = sheet_type == SheetType.ENUM
            is_kv_sheet = sheet_type == SheetType.KV
            path = is_enum_sheet and enum_path or config_path

            # 模块
            module = info.get("module", None)
            if module:
                path = path / module
                path.mkdir(parents=True, exist_ok=True)
                
                modules.append(module)
            
            # 处理 etype key 
            for k in list(sheet_data.keys()):
                sheet_data[self._serializer(k, True)] = sheet_data.pop(k)
            
            file_path = path / f"{sheet_name}.{self.ext}"
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(
                    sheet_data,
                    f,
                    ensure_ascii=False, 
                    indent=4, 
                    default=self._serializer
                )
        
        
        
        