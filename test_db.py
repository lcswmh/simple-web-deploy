from database_models import User,SessionLocal
from sqlalchemy.orm import Session
import string
import  random


def generate_short_code():
    """生成一个随机短码（例如6位）"""
    #string.ascii_letters：包含所有大小写英文字母，string.digits：包含数字字符串0-9，拼接区6位返回一个列表在用字符串拼接
    return  ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# 插入一条数据 （第二天内容）
def insert_url(db: Session ,url='',murl_record=''):
    """
    接收数据库会话、原始 URL 和短码，创建 User 对象并添加到会话，提交事务，刷新以获取自增 ID，打印成功信息
    :param db:数据库会话
    :param url:url地址
    :param murl_record:短码
    """
    new_url = User(
        original_url=url,
        short_code=murl_record,
    )
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    print(f"插入成功，ID: {new_url.id}, 短码: {new_url.short_code}")

    # 查询刚才插入的数据
    ##表示从数据库的urls表，发起一个查询会话，filter过滤条件，查数据库的short_code和刚才插入的数据new_url.short_code是否相等，有返回第一条数据
    query_url = db.query(User).filter(User.short_code == new_url.short_code).first()
    if query_url:
        print(f"查询成功：原链接 = {query_url.original_url}")
    else:
        print("未找到")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        insert_url(murl_record=generate_short_code(),db=db)
    finally:
        db.close()