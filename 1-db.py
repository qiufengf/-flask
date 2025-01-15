from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String,Boolean,Numeric,Text
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    url="mysql://root:123@127.0.0.1:3306/student?charset=utf8mb4",
    echo=True,
    pool_size=8,
    pool_recycle=60*30
)

DbSession = sessionmaker(bind=engine)
session = DbSession()
Model = declarative_base()
