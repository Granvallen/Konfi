
from konfi import Exportor

def main():
    table_dir = "./design"
    data_dir = "./data"
    writer_ext = "yaml"
    enum_tables = { "枚举" }
    
    exportor = Exportor(
        table_dir = table_dir, 
        data_dir = data_dir, 
        writer_ext = writer_ext,
        enum_tables = enum_tables,
        is_inc = False,
    )
    
    exportor.run()



if __name__ == "__main__":
    main()

