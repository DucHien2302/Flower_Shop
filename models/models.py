from sqlalchemy import Date, DateTime, Column, Text, DECIMAL, func, Boolean
# from sqlalchemy.types import Integer,String
from config.db import meta
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class Flower(Base):
    __tablename__ = 'flowers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    # image_url sẽ lưu đường dẫn tương đối tới file trên server, ví dụ: /media/flower_images/abc.jpg
    image_url = Column(String(255), nullable=True)
    flower_type = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
class FlowerTypes(Base):
    __tablename__ = 'FlowerTypes'
    id = Column(Integer, primary_key=True, index = True)
    Name = Column(String(255), nullable = False)
    Description  = Column(String(255), nullable = False)

class Categories(Base):
    __tablename__ = 'Categories'
    id = Column(Integer, primary_key=True, index = True)
    Name = Column(String(255), nullable = False)
    Description  = Column(String(255), nullable = False)

class Products(Base):
    __tablename__ = 'Products'
    id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(255), nullable=False)
    Description = Column(Text, nullable=False)
    Price = Column(Integer, nullable=False)
    DiscountedPrice = Column(Integer, nullable=False)
    StockQuantity = Column(Integer, default=0)
    CategoryID = Column(Integer, nullable=False)
    ImageURL = Column(String(255), nullable=False)
    IsFreeship = Column(Boolean, default=False)
    FlowerTypeID = Column(Integer, nullable=False)

class Informations(Base):
    __tablename__ = 'Informations'
    id = Column(Integer, primary_key=True, index=True)
    FirstName = Column(String(128), nullable=False)
    LastName = Column(String(128), nullable=False)
    FullName = Column(String(256), nullable=False)
    DateOfBirth = Column(Date, nullable=False)
    Gender = Column(String(32), nullable=False)
    Address = Column(String(512), nullable=False)
    UserId = Column(Integer, nullable=False)

class SysUser(Base):
    __tablename__ = 'SysUser'
    id = Column(Integer, primary_key=True, index=True)
    Email = Column(String(128), nullable=False)
    Password = Column(String(1024), nullable=False)

class SysRole(Base):
    __tablename__ = "SysRole"
    id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(128), nullable=False)
    CreateAt = Column(Date, nullable=False)
    UpdateAt = Column(Date, nullable=False)

class SysUserRole(Base):
    __tablename__ = "SysUserRole"
    id = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, nullable=False)
    RoleId = Column(Integer, nullable=False)

class Carts(Base):
    __tablename__ = 'Carts'
    id = Column(Integer, primary_key=True, index=True)
    ProductId = Column(Integer, nullable=False)
    Quantity = Column(Integer, nullable=False)
    IsChecked = Column(Integer, nullable=False)

class Invoices(Base):
    __tablename__ = 'Invoices'
    id = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, nullable=False)
    CreateAt = Column(DateTime, nullable=False)
    Price = Column(DECIMAL(10,2), nullable=False)
    Discount = Column(DECIMAL(10,2), nullable=False)
    Amount = Column(DECIMAL(10,2), nullable=False)
    Status = Column(Integer, nullable=False)

class InvoiceDetails(Base):
    __tablename__ = 'InvoiceDetails'
    id = Column(Integer, primary_key=True, index=True)
    ProductId = Column(Integer, nullable=False)
    InvoiceId = Column(Integer, nullable=False)
    Quantity = Column(Integer, nullable=False)
    Price = Column(DECIMAL(10, 2), nullable=False)

class VnPayment(Base):
    __tablename__ = 'VnPayment'
    TmnCode = Column(String(128), primary_key=True, index=True)
    Amount = Column(DECIMAL(10, 2), nullable=False)
    BankCode = Column(String(128), nullable=False)
    BankTranNo = Column(String(128), nullable=False)
    CardType = Column(String(128), nullable=False)
    OrderInfo = Column(String(128), nullable=False)
    PayDate = Column(String(128), nullable=False)
    ResponseCode = Column(String(128), nullable=False)
    TransactionNo = Column(String(128), nullable=False)
    TransactionStatus = Column(String(128), nullable=False)
    TxnRef = Column(String(128), nullable=False)