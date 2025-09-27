from __future__ import annotations

from pathlib import Path

class WriterMeta(type):
    """ 写入器元类
    """
    
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

        if "_reg_writers_cls" in namespace:
            return

        for base in bases:
            if hasattr(base, "_reg_writers_cls"):
                base._reg_writers_cls[cls.ext] = cls
                break





class Writer(metaclass=WriterMeta):
    """ 写入器
    """
    ext = "" # 文件扩展名
    
    _reg_writers_cls: dict[str, type[Writer]] = {}
    _writers: dict[str, type[Writer]] = {} # 单例
    

    @classmethod
    def get_writer(cls, ext: str) -> type[Writer]:
        if ext in cls._writers:
            return cls._writers[ext]
        
        writer_cls = cls._reg_writers_cls.get(ext, None)
        if writer_cls:
            writer = writer_cls()
            cls._writers[ext] = writer
            return writer
            
        else:
            raise ValueError(f"Writer {ext} 未找到")
 

    def write(
        self, 
        data: dict, 
        data_path: Path,
    ) -> None:
        """ 写入数据
        """
        raise NotImplementedError("子类必须实现 write 方法")




