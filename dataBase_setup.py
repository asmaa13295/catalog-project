import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, func, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)


class Cat(Base):
    __tablename__ = "Categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship(User)
    # add a decorator property to serialize data from the database
    @property
    def serialize(self):
        return{
        'id': self.id,
        'name': self.name,
        'user_id': self.user_id
        }



class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(String(8), nullable=False)
    time = Column(
                DateTime(timezone=True), nullable=False,
                server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship(User)
    cat_id = Column(Integer, ForeignKey("Categories.id"))
    cat = relationship(Cat)
    # add a decorator property to serialize data from the database
    @property
    def serialize(self):
        return{
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'time': self.time
        }

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
