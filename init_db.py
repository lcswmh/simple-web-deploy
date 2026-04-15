from database_models import engine,Base

## 据定义的模型，在数据库中创建所有不存在的表；如果表已经存在，则跳过，不会重复创建，
#也不会修改已有的表结构（比如不会自动添加新增的列）。
Base.metadata.create_all(bind=engine)
print("数据库表创建成功！")
