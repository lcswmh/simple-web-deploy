## 导入SQLAlchemy核心组件：# create_engine（数据库引擎）、Column（表字段）、数据类型（Integer整数、
## String字符串、DateTime时间）
from sqlalchemy import create_engine, Column, Integer, String, DateTime
## 修改后（SQLAlchemy 2.0+ 推荐写法） 导入ORM基类生成器（用于定义数据模型） （返回一个基类）
from sqlalchemy.orm import declarative_base
## 导入会话相关工具：# sessionmaker（会话工厂）、Session（会话类型）
from sqlalchemy.orm import sessionmaker
from datetime import datetime  # 用于记录注册时间
import  os


# 定义MySQL数据库连接字符串（格式：数据库类型+驱动://用户名:密码@主机:端口/数据库名）
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:root@192.168.190.102:3306/shorturl?charset=utf8mb4"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL) # 创建数据库引擎对象（负责与MySQL建立连接，管理连接池）
## sessionmaker创建会话工厂（用于生成数据库会话，会话是操作数据库的"通道"）每次调用SessionLocal（）会得到一个数据库会话,
# autocommit=False：关闭自动提交（需手动调用commit()提交事务）
# autoflush=False：关闭自动刷新（避免未提交的修改被意外同步到数据库）
SessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)
Base = declarative_base() #创建一个基类 Base。所有 ORM 模型都将继承这个类

def get_db():
    """
    这是一个依赖项函数，用于 FastAPI 的 Depends。它负责创建会话，使用完毕后自动关闭
    yield db：将会话对象交给 FastAPI 的路径函数使用。yield 之前的代码在请求开始时执行，
    yield 之后的代码在请求结束后执行（finally 确保会话关闭）。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base): #定义一个 ORM 类 User，继承自 Base
    __tablename__ = 'urls' #指定该类对应的数据库表名
    id = Column(Integer, primary_key=True,index=True,autoincrement=True)  #id
    original_url = Column(String(2048), nullable=False)         #字符串链接
    short_code = Column(String(50),unique=True, nullable=False,index=True)  #短码
    created_at = Column(DateTime,default=datetime.now)     #日期时间

    #新增字段
    clicks  = Column(Integer,default=0)  #记录短链接被访问的次数











    