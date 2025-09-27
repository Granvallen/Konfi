
from pathlib import Path
from datetime import datetime

from .writer import Writer
from ..etypes import *
from ..parsers import SheetType, SheetConfig


class PyWriter(Writer):
    """ python 写入器
        data/
          |- config/
          |- enum/
    """
    ext = "py" # 文件扩展名
    
    def write(
        self, 
        data: dict[str, dict],
        data_path: Path,
    ) -> None:
        
        import black
        mode = black.Mode(line_length=30)
        
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
            info = sheet_data.pop("_info")
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
                # 写入注释
                f.write(f"# {table_sheet}\n")
                # f.write(f"# {datetime.now().isoformat(sep=' ', timespec='seconds')}\n")
                f.write(f"# export by konfi\n\n")
                
                # 写入配置
                if config:
                    max_len = max(len(c[SheetConfig.VAR]) for c in config.values())
                    for col in config.values():
                        var = col[SheetConfig.VAR]
                        etype = col[SheetConfig.TYPE]
                        label = col.get(SheetConfig.LABEL, '')
                        f.write(f"# {var:{max_len}}: {etype} {label}\n")

                    f.write("\n")
                
                # 写入数据
                if is_enum_sheet: # 1. 枚举表
                    f.write("from enum import Enum\n\n")
                    for eenum in sheet_data.values():
                        f.write(f"{repr(eenum)}\n\n")

                    enum_sheets.append(sheet_name)
                
                elif is_kv_sheet: # 2. 键值表
                    if enums := info.get("enums", None): # 导入所需枚举
                        f.write(f"from {module and '...' or '..'}enum import {', '.join(enums)}\n")
                    
                    if refs := info.get("refs", None):
                        f.write(f"from {module and '...' or '..'}type import {', '.join(refs)}\n")
                    
                    f.write("\n\n")
                    if sheet_data:
                        max_len = max(len(repr(k)) for k in sheet_data)
                        f.write(f"{sheet_name} = {{\n")
                        for k, v in sheet_data.items():
                            f.write(f'    {repr(k):{max_len}}: {repr(v)},\n')
                        f.write("}\n")
                    
                    else:
                        f.write(f"{sheet_name} = {{}}")

                else: # 3. 其他表
                    if enums := info.get("enums", None): # 导入所需枚举
                        f.write(f"from {module and '...' or '..'}enum import {', '.join(enums)}\n")
                    
                    if refs := info.get("refs", None):
                        f.write(f"from {module and '...' or '..'}type import {', '.join(refs)}\n")
                        
                    f.write("\n\n")
                    formatted = repr(sheet_data)
                    formatted = black.format_str(f"{sheet_name} = {formatted}", mode=mode)
                    f.write(formatted)

                print(f"[konfi] 导出 {table_sheet}")


        
        # 后处理
        # 写入 enum init
        enum_init_path = enum_path / "__init__.py"        
        with enum_init_path.open("w", encoding="utf-8") as f:
            for path in enum_path.glob("*_enum.py"):
                f.write(f"from .{path.stem} import *\n")

        # 写入 module init
        for module in modules:
            module_path = config_path / module
            module_init_path = module_path / "__init__.py"
            with module_init_path.open("w", encoding="utf-8") as f:
                for path in module_path.glob("[!_]*.py"):
                    f.write(f"from .{path.stem} import *\n")
            
            
            