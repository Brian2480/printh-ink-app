
from datetime import datetime
from decimal import Decimal
from typing import List
import pytz

from dataclasses import dataclass
from flask_login import UserMixin
from sqlalchemy import String , Integer, DateTime , Boolean , Computed , ForeignKey , func , Numeric
from sqlalchemy.orm import Mapped , mapped_column , relationship
from werkzeug.security import generate_password_hash, check_password_hash

from src.app.database.db_base import Base



def get_time_cdmx():
    zona_horaria = pytz.timezone('America/Mexico_City')
    return datetime.now(zona_horaria).replace(tzinfo=None)


class User(Base, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), unique=False, nullable=False)
    custom_price: Mapped[Decimal] = mapped_column(Numeric(5,2), default=200.00, init=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relacion User
    orders:Mapped[List['Order']] = relationship( 'Order', back_populates='user', cascade='all, delete-orphan', init=False )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

class Order(Base):
    __tablename__ = 'order'

    id: Mapped[int] = mapped_column(Integer() , primary_key = True, init=False )
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False )
    meters: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False) # type: ignore
    cost: Mapped[Decimal] = mapped_column(Numeric(7, 2), Computed(price * meters), init=False)

    advance: Mapped[Decimal] = mapped_column( Numeric(7, 2), nullable=False, default=Decimal('0.00'))
    a_belong: Mapped[str] = mapped_column(String(15), nullable=False, default='S/A', init=False)

    total: Mapped[Decimal] = mapped_column(Numeric(7 , 2), Computed((price * meters) - advance), init=False)
    t_belong: Mapped[str] = mapped_column(String(15) , nullable=False, default='S/A', init=False)

    paid: Mapped[bool] = mapped_column(Boolean(), default=False )

    created_at: Mapped[datetime] = mapped_column( 
        DateTime,
        nullable = False,
        default = get_time_cdmx,
        init=False
    )
    
    # Relacion User
    user: Mapped['User'] = relationship('User' , back_populates='orders', init=False )

    #Relacion Upload
    uploads: Mapped['Upload'] = relationship( 'Upload' , back_populates='order' , cascade='all, delete-orphan', init=False)


class Upload(Base):
    __tablename__ = 'upload'

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, init=False)
    order_id: Mapped[int] = mapped_column( ForeignKey('order.id'), nullable=False)

    pdf_url: Mapped[str] = mapped_column(String(500), nullable=False, default=None)
    pdf_public_id: Mapped[str] = mapped_column(String(255), nullable=False, default=None , unique=True)

    # Campos para el adelanto
    jpg_advance_url: Mapped[str] = mapped_column(String(500), nullable=True ,default=None,)
    jpg_advance_public_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None, unique=True)

    # Campos para el pago Final
    jpg_pay_url: Mapped[str] = mapped_column(String(500), nullable=True ,default=None,)
    jpg_pay_public_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None, unique=True)

    #Relacion Upload
    order:Mapped['Order'] = relationship('Order' , back_populates='uploads', init=False)
