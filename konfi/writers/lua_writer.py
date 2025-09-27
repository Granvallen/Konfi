
from typing import Any
from pathlib import Path
import re

from .writer import Writer
from ..etypes import *
from ..parsers import *


class LuaWriter(Writer):
    """ lua 写入器
    """
    ext = "lua"

    def __init__(self):
        super().__init__()
        
        self._re = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    
    def _to_lua(self, data: Any, indent: int = 0) -> str:
        pad = "    " * indent

        match data:
            case dict():
                lines = []
                for k, v in data.items():
                    if isinstance(k, EType):
                        k = self._to_lua(k)
                    
                    if not bool(self._re.match(k)): # 非法键名加 []
                        k = f"[{k}]"
                    
                    v = self._to_lua(v, indent + 1)
                    lines.append(f"{pad}    {k} = {v},")
                    
                return f"{{\n" + "\n".join(lines) + f"\n{pad}}}"

            case bool():
                return "true" if data else "false"

            case EnumPack():
                return str(data.val)

            case EType():
                if data.py_val is None:
                    return "nil"
                
                match data:
                    case EString():
                        return f'"{data.py_val}"'

                    case EBool():
                        return "true" if data.py_val else "false"

                    case EEnum():
                        return self._to_lua(data.enum_dict_name, indent)
                    
                    case EEnumVal():
                        return str(data.enum_val)
                    
                    case EListM() | EList():
                        return f"{{ " + ", ".join(str(v) for v in data.py_val) + f" }}"

                    case ESetM() | ESet():
                        return self._to_lua({ v: True for v in data.py_val }, indent)

                    case EDictM() | EDict():
                        return self._to_lua(data.py_val, indent)

                    case _:
                        return str(data)
    
    
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
            
            
            file_path = path / f"{sheet_name}.{self.ext}"
            with file_path.open("w", encoding="utf-8") as f:
                f.write(f"-- {sheet_name}\n\n")
                res = self._to_lua(sheet_data)
                f.write(f"{sheet_name} = {res}")
                
                
                
        
        
















