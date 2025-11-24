# models.py

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import event, text, func, ForeignKey, Numeric
from typing import Optional, List
from datetime import datetime
import secrets
import os

# Читання DATABASE_URL з змінних оточення
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("Помилка: Змінна оточення DATABASE_URL не встановлена.")

engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

# Асоціативна таблиця для зв'язку "багато-до-багатьох"
waiter_table_association = sa.Table(
    'waiter_table_association',
    Base.metadata,
    sa.Column('employee_id', sa.ForeignKey('employees.id'), primary_key=True),
    sa.Column('table_id', sa.ForeignKey('tables.id'), primary_key=True)
)


class MenuItem(Base):
    __tablename__ = 'menu_items'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(sa.String(100), nullable=False, unique=True)
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(sa.Integer, default=100)
    show_on_website: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    show_in_telegram: Mapped[bool] = mapped_column(sa.Boolean, default=True)


class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(50), nullable=False, unique=True)
    can_manage_orders: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    can_be_assigned: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    can_serve_tables: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    can_receive_kitchen_orders: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    can_receive_bar_orders: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=text("false"))
    
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="role")

class Employee(Base):
    __tablename__ = 'employees'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[Optional[int]] = mapped_column(sa.BigInteger, nullable=True, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(sa.String(20), nullable=True, unique=True)
    
    # --- НОВЕ ПОЛЕ ДЛЯ PWA АВТОРИЗАЦІЇ ---
    password_hash: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    # -------------------------------------

    role_id: Mapped[int] = mapped_column(sa.ForeignKey('roles.id'), nullable=False)
    role: Mapped["Role"] = relationship("Role", back_populates="employees", lazy='selectin')
    is_on_shift: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=text("false"), nullable=False)
    
    # Баланс готівки "на руках" у співробітника
    cash_balance: Mapped[float] = mapped_column(sa.Numeric(10, 2), default=0.00, server_default=text("0.00"), comment="Гроші, які співробітник винен касі")

    current_order_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('orders.id', ondelete="SET NULL"), nullable=True)
    current_order: Mapped[Optional["Order"]] = relationship("Order", foreign_keys="Employee.current_order_id")
    
    assigned_tables: Mapped[List["Table"]] = relationship("Table", secondary=waiter_table_association, back_populates="assigned_waiters")
    accepted_orders: Mapped[List["Order"]] = relationship("Order", back_populates="accepted_by_waiter", foreign_keys="Order.accepted_by_waiter_id")


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(100))
    sort_order: Mapped[int] = mapped_column(sa.Integer, default=100, server_default=text("100"))
    show_on_delivery_site: Mapped[bool] = mapped_column(sa.Boolean, default=True, server_default=text("true"), nullable=False)
    show_in_restaurant: Mapped[bool] = mapped_column(sa.Boolean, default=True, server_default=text("true"), nullable=False)
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(100))
    description: Mapped[str] = mapped_column(sa.String(500), nullable=True)
    image_url: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    price: Mapped[float] = mapped_column(sa.Numeric(10, 2), nullable=False) 
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True, server_default=text("true"))
    category_id: Mapped[int] = mapped_column(sa.ForeignKey('categories.id'))
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="product")
    preparation_area: Mapped[str] = mapped_column(sa.String(20), default='kitchen', server_default=text("'kitchen'"), nullable=False)


class OrderStatus(Base):
    __tablename__ = 'order_statuses'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    notify_customer: Mapped[bool] = mapped_column(sa.Boolean, default=True, server_default=text("true"), nullable=False)
    visible_to_operator: Mapped[bool] = mapped_column(sa.Boolean, default=True, server_default=text("true"), nullable=False)
    visible_to_courier: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=text("false"), nullable=False)
    visible_to_waiter: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=text("false"), nullable=False)
    visible_to_chef: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=text("false"), nullable=False)
    visible_to_bartender: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=text("false"), nullable=False)
    requires_kitchen_notify: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=text("false"), nullable=False)
    is_completed_status: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=text("false"), nullable=False)
    is_cancelled_status: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=text("false"), nullable=False)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="status")
    history_entries: Mapped[list["OrderStatusHistory"]] = relationship("OrderStatusHistory", back_populates="status")

# --- КАСОВІ ЗМІНИ ---

class CashShift(Base):
    """Касова зміна"""
    __tablename__ = 'cash_shifts'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(sa.ForeignKey('employees.id'), nullable=False)
    
    start_time: Mapped[datetime] = mapped_column(sa.DateTime, default=func.now())
    end_time: Mapped[Optional[datetime]] = mapped_column(sa.DateTime, nullable=True)
    
    start_cash: Mapped[float] = mapped_column(sa.Numeric(10, 2), default=0.0, comment="Залишок на початок зміни")
    end_cash_actual: Mapped[Optional[float]] = mapped_column(sa.Numeric(10, 2), nullable=True, comment="Фактичний залишок при закритті")
    
    total_sales_cash: Mapped[float] = mapped_column(sa.Numeric(10, 2), default=0.0, comment="Продажі готівкою")
    total_sales_card: Mapped[float] = mapped_column(sa.Numeric(10, 2), default=0.0, comment="Продажі карткою")
    service_in: Mapped[float] = mapped_column(sa.Numeric(10, 2), default=0.0, comment="Службове внесення")
    service_out: Mapped[float] = mapped_column(sa.Numeric(10, 2), default=0.0, comment="Службове вилучення/Інкасація")
    
    is_closed: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    
    employee: Mapped["Employee"] = relationship("Employee")
    transactions: Mapped[list["CashTransaction"]] = relationship("CashTransaction", back_populates="shift")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="cash_shift")

class CashTransaction(Base):
    """Службові операції з готівкою (внесення/вилучення)"""
    __tablename__ = 'cash_transactions'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shift_id: Mapped[int] = mapped_column(sa.ForeignKey('cash_shifts.id'), nullable=False)
    
    amount: Mapped[float] = mapped_column(sa.Numeric(10, 2), nullable=False)
    transaction_type: Mapped[str] = mapped_column(sa.String(20), nullable=False, comment="'in' - внесення, 'out' - вилучення, 'handover' - здача виручки")
    comment: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=func.now())
    
    shift: Mapped["CashShift"] = relationship("CashShift", back_populates="transactions")

# -----------------------------------

class OrderItem(Base):
    __tablename__ = 'order_items'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(sa.ForeignKey('orders.id', ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('products.id', ondelete="SET NULL"), nullable=True)
    
    product_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(sa.Integer, default=1, nullable=False)
    price_at_moment: Mapped[float] = mapped_column(sa.Numeric(10, 2), nullable=False)
    
    preparation_area: Mapped[str] = mapped_column(sa.String(20), default='kitchen', server_default=text("'kitchen'"))

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product")


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(sa.BigInteger, nullable=True)
    username: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy='selectin')
    
    total_price: Mapped[float] = mapped_column(sa.Numeric(10, 2), default=0.00)
    
    customer_name: Mapped[str] = mapped_column(sa.String(100), nullable=True)
    phone_number: Mapped[str] = mapped_column(sa.String(20), nullable=True, index=True)
    address: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    status_id: Mapped[int] = mapped_column(sa.ForeignKey('order_statuses.id'), default=1, nullable=False)
    status: Mapped["OrderStatus"] = relationship("OrderStatus", back_populates="orders", lazy='selectin')
    is_delivery: Mapped[bool] = mapped_column(default=True)
    delivery_time: Mapped[str] = mapped_column(sa.String(50), nullable=True, default="Якнайшвидше")
    courier_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('employees.id', ondelete="SET NULL"), nullable=True)
    courier: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys="Order.courier_id")
    
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=func.now(), server_default=func.now())
    closed_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime, nullable=True)
    
    completed_by_courier_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('employees.id'), nullable=True)
    completed_by_courier: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys="Order.completed_by_courier_id")
    history: Mapped[list["OrderStatusHistory"]] = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan", lazy='selectin')
    table_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('tables.id'), nullable=True)
    table: Mapped[Optional["Table"]] = relationship("Table", back_populates="orders")
    order_type: Mapped[str] = mapped_column(sa.String(20), default='delivery', server_default=text("'delivery'"), nullable=False)
    accepted_by_waiter_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('employees.id'), nullable=True)
    accepted_by_waiter: Mapped[Optional["Employee"]] = relationship("Employee", back_populates="accepted_orders", foreign_keys="Order.accepted_by_waiter_id")
    
    cancellation_reason: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    
    # --- КАСА ---
    payment_method: Mapped[str] = mapped_column(sa.String(20), default='cash', server_default=text("'cash'"), nullable=False, comment="'cash' або 'card'")
    cash_shift_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('cash_shifts.id'), nullable=True)
    cash_shift: Mapped[Optional["CashShift"]] = relationship("CashShift", back_populates="orders")
    
    is_cash_turned_in: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=text("false"), comment="Чи здана готівка касиру")

    kitchen_done: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=text("false"))
    bar_done: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=text("false"))

    @property
    def products_text(self) -> str:
        if not self.items:
            return ""
        return ", ".join([f"{item.product_name} x {item.quantity}" for item in self.items])


class OrderStatusHistory(Base):
    __tablename__ = 'order_status_history'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id', ondelete="CASCADE"), nullable=False, index=True)
    status_id: Mapped[int] = mapped_column(ForeignKey('order_statuses.id'), nullable=False)
    actor_info: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(sa.DateTime, default=func.now(), server_default=func.now(), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="history")
    status: Mapped["OrderStatus"] = relationship("OrderStatus", back_populates="history_entries", lazy='selectin')


class Customer(Base):
    __tablename__ = 'customers'
    user_id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=True)
    phone_number: Mapped[str] = mapped_column(sa.String(20), nullable=True)
    address: Mapped[str] = mapped_column(sa.String(255), nullable=True)

class CartItem(Base):
    __tablename__ = 'cart_items'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(sa.BigInteger, index=True)
    product_id: Mapped[int] = mapped_column(sa.ForeignKey('products.id'))
    quantity: Mapped[int] = mapped_column(default=1)
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items", lazy='selectin')

class Table(Base):
    __tablename__ = 'tables'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False, unique=True)
    access_token: Mapped[str] = mapped_column(sa.String(32), default=lambda: secrets.token_urlsafe(16), nullable=False, unique=True, index=True)
    qr_code_url: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    assigned_waiters: Mapped[List["Employee"]] = relationship("Employee", secondary=waiter_table_association, back_populates="assigned_tables")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="table")


class Settings(Base):
    __tablename__ = 'settings'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    logo_url: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    site_title: Mapped[Optional[str]] = mapped_column(sa.String(100), default="Назва")
    seo_description: Mapped[Optional[str]] = mapped_column(sa.String(255))
    seo_keywords: Mapped[Optional[str]] = mapped_column(sa.String(255))
    primary_color: Mapped[Optional[str]] = mapped_column(sa.String(7), default="#5a5a5a")
    secondary_color: Mapped[Optional[str]] = mapped_column(sa.String(7), default="#eeeeee")
    background_color: Mapped[Optional[str]] = mapped_column(sa.String(7), default="#f4f4f4")
    text_color: Mapped[Optional[str]] = mapped_column(sa.String(7), default="#333333")
    footer_bg_color: Mapped[Optional[str]] = mapped_column(sa.String(7), default="#333333")
    footer_text_color: Mapped[Optional[str]] = mapped_column(sa.String(7), default="#ffffff")
    font_family_sans: Mapped[Optional[str]] = mapped_column(sa.String(100), default="Golos Text")
    font_family_serif: Mapped[Optional[str]] = mapped_column(sa.String(100), default="Playfair Display")
    telegram_welcome_message: Mapped[Optional[str]] = mapped_column(sa.Text)
    footer_address: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    footer_phone: Mapped[Optional[str]] = mapped_column(sa.String(50), nullable=True)
    working_hours: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    instagram_url: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    facebook_url: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    
    # --- НОВІ ПОЛЯ ---
    header_image_url: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    wifi_ssid: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    wifi_password: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    category_nav_bg_color: Mapped[Optional[str]] = mapped_column(sa.String(7), default="#ffffff")
    category_nav_text_color: Mapped[Optional[str]] = mapped_column(sa.String(7), default="#333333")


async def create_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        result_status = await session.execute(sa.select(OrderStatus).limit(1))
        if not result_status.scalars().first():
            default_statuses = {
                "Новий": {"visible_to_operator": True, "visible_to_courier": False, "visible_to_waiter": True, "visible_to_chef": True, "visible_to_bartender": True, "requires_kitchen_notify": False},
                "В обробці": {"visible_to_operator": True, "visible_to_courier": False, "visible_to_waiter": True, "visible_to_chef": True, "visible_to_bartender": True, "requires_kitchen_notify": True},
                "Готовий до видачі": {"visible_to_operator": True, "visible_to_courier": True, "visible_to_waiter": True, "visible_to_chef": False, "visible_to_bartender": False, "notify_customer": True, "requires_kitchen_notify": False},
                "Доставлений": {"visible_to_operator": True, "visible_to_courier": True, "is_completed_status": True},
                "Скасований": {"visible_to_operator": True, "visible_to_courier": False, "is_cancelled_status": True, "visible_to_waiter": True, "visible_to_chef": False, "visible_to_bartender": False},
                "Оплачено": {"visible_to_operator": True, "is_completed_status": True, "visible_to_waiter": True, "visible_to_chef": False, "visible_to_bartender": False, "notify_customer": False}
            }
            for name, props in default_statuses.items():
                session.add(OrderStatus(name=name, **props))

        result_roles = await session.execute(sa.select(Role).limit(1))
        if not result_roles.scalars().first():
            session.add(Role(name="Адміністратор", can_manage_orders=True, can_be_assigned=True, can_serve_tables=True, can_receive_kitchen_orders=True, can_receive_bar_orders=True))
            session.add(Role(name="Оператор", can_manage_orders=True, can_be_assigned=False, can_serve_tables=True, can_receive_kitchen_orders=True, can_receive_bar_orders=True))
            session.add(Role(name="Кур'єр", can_manage_orders=False, can_be_assigned=True, can_serve_tables=False, can_receive_kitchen_orders=False, can_receive_bar_orders=False))
            session.add(Role(name="Офіціант", can_manage_orders=False, can_be_assigned=False, can_serve_tables=True, can_receive_kitchen_orders=False, can_receive_bar_orders=False))
            session.add(Role(name="Повар", can_manage_orders=False, can_be_assigned=False, can_serve_tables=False, can_receive_kitchen_orders=True, can_receive_bar_orders=False))
            session.add(Role(name="Бармен", can_manage_orders=False, can_be_assigned=False, can_serve_tables=False, can_receive_kitchen_orders=False, can_receive_bar_orders=True))

        await session.commit()