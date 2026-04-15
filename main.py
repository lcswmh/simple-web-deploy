from  fastapi import  FastAPI,Depends,HTTPException #导入 FastAPI 核心组件：FastAPI 类、依赖注入 Depends、异常 HTTPException。
from fastapi.responses import RedirectResponse #RedirectResponse：用于返回 HTTP 重定向响应
from sqlalchemy.orm import Session  #从 SQLAlchemy 导入 Session 类型，用于类型注解
from  database_models import  get_db,User  #从自定义模块导入 get_db（数据库会话依赖）和 User（ORM 模型）
from  test_db import  generate_short_code,insert_url #从 test_db 导入生成短码的函数和插入记录的函数
from pydantic import BaseModel,HttpUrl #Pydantic 的 BaseModel：用于定义请求体的数据结构，HttpUrl校验url格式
from fastapi.staticfiles import StaticFiles #从FastAPI库中导入一个专门用来处理静态文件的工具类，
import  uvicorn #导入 ASGI 服务器，用于直接运行脚本时启动服务


import os   # 如果已经有这一行就不用重复加

# 从环境变量中读取基础网址，如果没有设置就默认使用本地地址
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

class Url(BaseModel):
    """
    定义一个 Pydantic 模型 Url,包含一个字段 original_url，类型为 HttpUrl。FastAPI 会自动校验请求体是否符合这个格式
    """
    original_url: HttpUrl

app = FastAPI() #创建 FastAPI 应用实例
#挂载静态文件：访问 /static 路径时，会从项目根目录下的 static 文件夹中读取文件。name 参数用于命名
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")


def create_short_url(original_url,db):
    """
    定义一个辅助函数，负责生成唯一的短码并保存到数据库
    :param original_url:
    :param db:
    :return: 返回 JSON 对象，包含生成的完整短链接地址。注意这里地址写死了 127.0.0.1:8000，部署到公网时需要改为真实域名
    """
    max_retries = 10
    for i in range(max_retries):
        gsc = generate_short_code()  #获取短码
        if not  db.query(User).filter(User.short_code == gsc).first(): #判断数据库有没有短码有就结束本次循环
            break
    else:
        raise HTTPException(status_code=500, detail="短码生成失败，请重试") #都有则抛出 500 错误
    insert_url(db,original_url,gsc) #调用 insert_url 将长链接和短码存入数据库
    return {"short_url": f"{BASE_URL}/{gsc}"}

@app.post("/shorten") #定义 POST 接口 /shorten
async def shorten_url(original_url:Url,db: Session = Depends(get_db)):
    """
    :param original_url:FastAPI 会自动从请求体中读取 JSON 并解析为 Url 对象
    :param db:db: Session = Depends(get_db)：依赖注入，获取数据库会话
    :return:调用 create_short_url 并返回结果
    """
    return  create_short_url(original_url.original_url,db)

@app.get("/{short_url}") #定义 GET 接口，路径参数 short_url（即短码）
async def redirect(short_url:str,db: Session = Depends(get_db)):
    #查询数据库，根据短码查找对应的记录。.first() 返回第一条结果，如果没有则返回 None
    url_record =  db.query(User).filter(User.short_code == short_url).first()
    if not url_record:
        raise HTTPException(status_code=404,detail="URL not found") #如果未找到，抛出 404 异常
    # 增加访问计数
    url_record.clicks += 1
    db.commit() #将查到的记录的 clicks 字段加 1，并提交到数据库
    return RedirectResponse(url=url_record.original_url) #返回重定向响应，浏览器会自动跳转到原始链接

if __name__ == '__main__':
    uvicorn.run('main:app',reload=True)















