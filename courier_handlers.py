# courier_handlers.py

import logging
import html as html_module
from aiogram import Dispatcher, F, html, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload, selectinload
from typing import Dict, Any, Optional, List
from urllib.parse import quote_plus
import re 
import os
from decimal import Decimal

from models import Employee, Order, OrderStatus, Settings, OrderStatusHistory, Table, Category, Product, OrderItem
# Додано notify_station_completion
from notification_manager import notify_new_order_to_staff, notify_all_parties_on_status_change, notify_station_completion
# --- КАСА: Імпорт сервісів ---
from cash_service import link_order_to_shift, register_employee_debt

logger = logging.getLogger(__name__)

class StaffAuthStates(StatesGroup):
    waiting_for_phone = State()

class WaiterCreateOrderStates(StatesGroup):
    managing_cart = State()
    choosing_category = State()
    choosing_product = State()


def get_staff_login_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🔐 Вхід оператора"))
    builder.row(KeyboardButton(text="🚚 Вхід кур'єра"))
    builder.row(KeyboardButton(text="🤵 Вхід офіціанта"))
    builder.row(KeyboardButton(text="🧑‍🍳 Вхід повара"), KeyboardButton(text="🍹 Вхід бармена"))
    return builder.as_markup(resize_keyboard=True)

def get_staff_keyboard(employee: Employee):
    builder = ReplyKeyboardBuilder()
    role = employee.role
    
    if employee.is_on_shift:
        builder.row(KeyboardButton(text="🔴 Завершити зміну"))
    else:
        builder.row(KeyboardButton(text="🟢 Почати зміну"))

    role_buttons = []
    if employee.is_on_shift:
        if role.can_be_assigned:
            role_buttons.append(KeyboardButton(text="📦 Мої замовлення"))
        if role.can_serve_tables:
            role_buttons.append(KeyboardButton(text="🍽 Мої столики"))
        if role.can_receive_kitchen_orders:
             role_buttons.append(KeyboardButton(text="🔪 Кухня"))
        if role.can_receive_bar_orders:
             role_buttons.append(KeyboardButton(text="🍹 Бар"))
            
    if role_buttons:
        builder.row(*role_buttons)

    builder.row(KeyboardButton(text="🚪 Вийти"))
    return builder.as_markup(resize_keyboard=True)

def get_courier_keyboard(employee: Employee): return get_staff_keyboard(employee)
def get_operator_keyboard(employee: Employee): return get_staff_keyboard(employee)
def get_waiter_keyboard(employee: Employee): return get_staff_keyboard(employee)


# --- ДОПОМІЖНА ФУНКЦІЯ: Отримання відфільтрованого тексту чека ---
async def _get_filtered_order_text(session: AsyncSession, order: Order, area: str) -> str:
    """
    Повертає текст складу замовлення, залишаючи ТІЛЬКИ товари для вказаного цеху.
    Використовує OrderItem.
    """
    # Завантажуємо items якщо вони ще не завантажені
    if 'items' not in order.__dict__:
        await session.refresh(order, ['items'])
        
    if not order.items:
        return ""

    filtered_lines = []
    for item in order.items:
        # Перевіряємо цех
        is_target = False
        if area == 'bar' and item.preparation_area == 'bar':
            is_target = True
        elif area == 'kitchen' and item.preparation_area != 'bar':
            # Все, що не бар, йде на кухню (за замовчуванням)
            is_target = True

        if is_target:
            filtered_lines.append(f"- {html_module.escape(item.product_name)} x {item.quantity}")

    if not filtered_lines:
        return ""
        
    return "\n".join(filtered_lines)


# --- ЕКРАН ПОВАРА (Тільки 'kitchen') ---
async def show_chef_orders(message_or_callback: Message | CallbackQuery, session: AsyncSession, **kwargs: Dict[str, Any]):
    user_id = message_or_callback.from_user.id
    message = message_or_callback.message if isinstance(message_or_callback, CallbackQuery) else message_or_callback

    employee = await session.scalar(select(Employee).where(Employee.telegram_user_id == user_id).options(joinedload(Employee.role)))
    
    if not employee or not employee.role.can_receive_kitchen_orders:
         return await message.answer("❌ У вас немає прав повара.")
    if not employee.is_on_shift:
         return await message.answer("🔴 Ви не на зміні.")

    kitchen_statuses_res = await session.execute(select(OrderStatus.id).where(OrderStatus.visible_to_chef == True))
    kitchen_status_ids = kitchen_statuses_res.scalars().all()

    # Завантажуємо items для фільтрації
    orders_res = await session.execute(
        select(Order)
        .options(joinedload(Order.status), joinedload(Order.table), selectinload(Order.items))
        .where(Order.status_id.in_(kitchen_status_ids))
        .order_by(Order.id.asc())
    )
    all_orders = orders_res.scalars().all()

    text = "🔪 <b>Замовлення на кухні:</b>\n\n"
    count = 0
    
    kb = InlineKeyboardBuilder()
    for order in all_orders:
        # Якщо кухня вже виконала свою частину, не показуємо
        if order.kitchen_done:
            continue

        products_text = await _get_filtered_order_text(session, order, 'kitchen')
        if not products_text:
            continue
            
        count += 1
        table_info = order.table.name if order.table else ('Доставка' if order.is_delivery else 'Самовивіз')
        
        text += (f"═════════════════\n"
                 f"<b>№{order.id}</b> ({table_info})\n"
                 f"Час: {order.created_at.strftime('%H:%M')}\n"
                 f"{products_text}\n\n")
        
        kb.row(InlineKeyboardButton(text=f"✅ Видача #{order.id}", callback_data=f"chef_ready_{order.id}_kitchen"))
    
    if count == 0:
        text += "Наразі активних замовлень немає."
        
    kb.adjust(1)
    
    try:
        if isinstance(message_or_callback, CallbackQuery):
            await message.edit_text(text, reply_markup=kb.as_markup())
            await message_or_callback.answer()
        else:
            await message.answer(text, reply_markup=kb.as_markup())
    except TelegramBadRequest: pass


# --- ЕКРАН БАРМЕНА (Тільки 'bar') ---
async def show_bartender_orders(message_or_callback: Message | CallbackQuery, session: AsyncSession, **kwargs: Dict[str, Any]):
    user_id = message_or_callback.from_user.id
    message = message_or_callback.message if isinstance(message_or_callback, CallbackQuery) else message_or_callback

    employee = await session.scalar(select(Employee).where(Employee.telegram_user_id == user_id).options(joinedload(Employee.role)))
    
    if not employee or not employee.role.can_receive_bar_orders:
         return await message.answer("❌ У вас немає прав бармена.")
    if not employee.is_on_shift:
         return await message.answer("🔴 Ви не на зміні.")

    bar_statuses_res = await session.execute(select(OrderStatus.id).where(OrderStatus.visible_to_bartender == True))
    bar_status_ids = bar_statuses_res.scalars().all()

    orders_res = await session.execute(
        select(Order)
        .options(joinedload(Order.status), joinedload(Order.table), selectinload(Order.items))
        .where(Order.status_id.in_(bar_status_ids))
        .order_by(Order.id.asc())
    )
    all_orders = orders_res.scalars().all()

    text = "🍹 <b>Замовлення на барі:</b>\n\n"
    count = 0
    
    kb = InlineKeyboardBuilder()
    for order in all_orders:
        # Якщо бар вже виконав свою частину
        if order.bar_done:
            continue

        products_text = await _get_filtered_order_text(session, order, 'bar')
        if not products_text:
            continue
            
        count += 1
        table_info = order.table.name if order.table else ('Доставка' if order.is_delivery else 'Самовивіз')
        
        text += (f"═════════════════\n"
                 f"<b>№{order.id}</b> ({table_info})\n"
                 f"Час: {order.created_at.strftime('%H:%M')}\n"
                 f"{products_text}\n\n")
        
        kb.row(InlineKeyboardButton(text=f"✅ Готово #{order.id}", callback_data=f"chef_ready_{order.id}_bar"))
    
    if count == 0:
        text += "Наразі активних замовлень немає."

    kb.adjust(1)
    
    try:
        if isinstance(message_or_callback, CallbackQuery):
            await message.edit_text(text, reply_markup=kb.as_markup())
            await message_or_callback.answer()
        else:
            await message.answer(text, reply_markup=kb.as_markup())
    except TelegramBadRequest: pass


async def show_courier_orders(message_or_callback: Message | CallbackQuery, session: AsyncSession, **kwargs: Dict[str, Any]):
    user_id = message_or_callback.from_user.id
    message = message_or_callback.message if isinstance(message_or_callback, CallbackQuery) else message_or_callback

    employee = await session.scalar(select(Employee).where(Employee.telegram_user_id == user_id).options(joinedload(Employee.role)))
    
    if not employee or not employee.role.can_be_assigned:
         return await message.answer("❌ У вас немає прав кур'єра.")

    final_statuses_res = await session.execute(
        select(OrderStatus.id).where(or_(OrderStatus.is_completed_status == True, OrderStatus.is_cancelled_status == True))
    )
    final_status_ids = final_statuses_res.scalars().all()

    orders_res = await session.execute(
        select(Order).options(joinedload(Order.status)).where(
            Order.courier_id == employee.id,
            Order.status_id.not_in(final_status_ids)
        ).order_by(Order.id.desc())
    )
    orders = orders_res.scalars().all()

    text = "🚚 <b>Ваші активні замовлення:</b>\n\n"
    if not employee.is_on_shift:
         text += "🔴 Ви не на зміні. Натисніть '🟢 Почати зміну', щоб отримувати нові замовлення.\n\n"
    if not orders:
        text += "На даний момент немає активних замовлень, призначених вам."
    
    kb = InlineKeyboardBuilder()
    if orders:
        for order in orders:
            status_name = order.status.name if order.status else "Невідомий"
            address_info = order.address if order.is_delivery else 'Самовивіз'
            text += (f"<b>Замовлення #{order.id}</b> ({status_name})\n"
                     f"📍 Адреса: {html_module.escape(address_info)}\n"
                     f"💰 Сума: {order.total_price} грн\n\n")
            kb.row(InlineKeyboardButton(text=f"Дії по замовленню #{order.id}", callback_data=f"courier_view_order_{order.id}"))
        kb.adjust(1)
    
    try:
        if isinstance(message_or_callback, CallbackQuery):
            await message.edit_text(text, reply_markup=kb.as_markup())
            await message_or_callback.answer()
        else:
            await message.answer(text, reply_markup=kb.as_markup())
    except TelegramBadRequest: pass

async def show_waiter_tables(message_or_callback: Message | CallbackQuery, session: AsyncSession, state: FSMContext):
    is_callback = isinstance(message_or_callback, CallbackQuery)
    message = message_or_callback.message if is_callback else message_or_callback
    user_id = message_or_callback.from_user.id
    
    await state.clear()
    
    employee = await session.scalar(
        select(Employee).where(Employee.telegram_user_id == user_id).options(joinedload(Employee.role))
    )
    
    if not employee or not employee.role.can_serve_tables:
        return await message.answer("❌ У вас немає прав офіціанта.") if not is_callback else message_or_callback.answer("❌ Немає прав.", show_alert=True)

    if not employee.is_on_shift:
        text_off = "🔴 Ви не на зміні."
        return await message.answer(text_off) if not is_callback else message_or_callback.answer(text_off, show_alert=True)

    tables_res = await session.execute(
        select(Table).where(Table.assigned_waiters.any(Employee.id == employee.id)).order_by(Table.name)
    )
    tables = tables_res.scalars().all()

    text = "🍽 <b>Закріплені за вами столики:</b>\n\n"
    kb = InlineKeyboardBuilder()
    if not tables:
        text += "За вами не закріплено жодного столика."
    else:
        for table in tables:
            kb.add(InlineKeyboardButton(text=f"Столик: {html_module.escape(table.name)}", callback_data=f"waiter_view_table_{table.id}"))
    kb.adjust(1)
    
    try:
        if is_callback:
            await message.edit_text(text, reply_markup=kb.as_markup())
            await message_or_callback.answer()
        else:
            await message.answer(text, reply_markup=kb.as_markup())
    except TelegramBadRequest: pass


async def start_handler(message: Message, state: FSMContext, session: AsyncSession, **kwargs: Dict[str, Any]):
    await state.clear()
    employee = await session.scalar(
        select(Employee).where(Employee.telegram_user_id == message.from_user.id).options(joinedload(Employee.role))
    )
    if employee:
        keyboard = get_staff_keyboard(employee)
        await message.answer(f"🎉 Доброго дня, {employee.full_name}! Ви увійшли в режим {employee.role.name}.",
                             reply_markup=keyboard)
    else:
        await message.answer("👋 Ласкаво просимо! Використовуйте цей бот для управління замовленнями.",
                             reply_markup=get_staff_login_keyboard())

async def _generate_waiter_order_view(order: Order, session: AsyncSession):
    await session.refresh(order, ['status', 'accepted_by_waiter', 'table', 'items'])
    status_name = order.status.name if order.status else 'Невідомий'
    
    products_formatted = ""
    if order.items:
        products_formatted = "\n".join([f"- {html_module.escape(item.product_name)} x {item.quantity}" for item in order.items])
    else:
        products_formatted = "- <i>(Пусто)</i>"
    
    if order.accepted_by_waiter:
        accepted_by_text = f"<b>Прийнято:</b> {html_module.escape(order.accepted_by_waiter.full_name)}\n\n"
    else:
        accepted_by_text = "<b>Прийнято:</b> <i>Очікує...</i>\n\n"
    
    table_name = order.table.name if order.table else "N/A"
    
    payment_info = ""
    if order.status.is_completed_status:
         payment_info = f"\n<b>Оплата:</b> {'💳 Картка' if order.payment_method == 'card' else '💵 Готівка'}"
         if order.payment_method == 'cash':
             payment_info += " (В касі)" if order.is_cash_turned_in else " (У вас)"

    text = (f"<b>Керування замовленням #{order.id}</b> (Стіл: {table_name})\n\n"
            f"<b>Склад:</b>\n{products_formatted}\n\n<b>Сума:</b> {order.total_price} грн\n\n"
            f"{accepted_by_text}"
            f"<b>Поточний статус:</b> {status_name}{payment_info}")

    kb = InlineKeyboardBuilder()
    
    if not order.accepted_by_waiter_id:
        kb.row(InlineKeyboardButton(text="✅ Прийняти це замовлення", callback_data=f"waiter_accept_order_{order.id}"))

    statuses_res = await session.execute(
        select(OrderStatus).where(OrderStatus.visible_to_waiter == True).order_by(OrderStatus.id)
    )
    statuses = statuses_res.scalars().all()
    status_buttons = [
        InlineKeyboardButton(text=f"{'✅ ' if s.id == order.status_id else ''}{s.name}", callback_data=f"staff_set_status_{order.id}_{s.id}")
        for s in statuses
    ]
    for i in range(0, len(status_buttons), 2):
        kb.row(*status_buttons[i:i+2])

    kb.row(InlineKeyboardButton(text="✏️ Редагувати замовлення", callback_data=f"edit_order_{order.id}"))
    kb.row(InlineKeyboardButton(text="⬅️ Назад до столика", callback_data=f"waiter_view_table_{order.table_id}"))
    
    return text, kb.as_markup()

def register_courier_handlers(dp_admin: Dispatcher):
    dp_admin.message.register(start_handler, CommandStart())

    @dp_admin.message(F.text.in_({"🚚 Вхід кур'єра", "🔐 Вхід оператора", "🤵 Вхід офіціанта", "🧑‍🍳 Вхід повара", "🍹 Вхід бармена"}))
    async def staff_login_start(message: Message, state: FSMContext, session: AsyncSession):
        user_id = message.from_user.id
        employee = await session.scalar(
            select(Employee).where(Employee.telegram_user_id == user_id).options(joinedload(Employee.role))
        )
        if employee:
            return await message.answer(f"✅ Ви вже авторизовані як {employee.role.name}. Спочатку вийдіть із системи.", 
                                        reply_markup=get_staff_login_keyboard())
        
        role_type = "unknown"
        if "кур'єра" in message.text: role_type = "courier"
        elif "оператора" in message.text: role_type = "operator"
        elif "офіціанта" in message.text: role_type = "waiter"
        elif "повара" in message.text: role_type = "chef"
        elif "бармена" in message.text: role_type = "bartender"
            
        await state.set_state(StaffAuthStates.waiting_for_phone)
        await state.update_data(role_type=role_type)
        kb = InlineKeyboardBuilder().add(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_auth")).as_markup()
        await message.answer(f"Будь ласка, введіть номер телефону для ролі **{role_type}**:", reply_markup=kb)

    @dp_admin.message(StaffAuthStates.waiting_for_phone)
    async def process_staff_phone(message: Message, state: FSMContext, session: AsyncSession):
        phone = message.text.strip()
        data = await state.get_data()
        role_type = data.get("role_type")
        
        employee = await session.scalar(select(Employee).options(joinedload(Employee.role)).where(Employee.phone_number == phone))
        
        role_checks = {
            "courier": lambda e: e and e.role.can_be_assigned,
            "operator": lambda e: e and e.role.can_manage_orders,
            "waiter": lambda e: e and e.role.can_serve_tables,
            "chef": lambda e: e and e.role.can_receive_kitchen_orders,
            "bartender": lambda e: e and e.role.can_receive_bar_orders,
        }
        
        if role_checks.get(role_type, lambda e: False)(employee):
            employee.telegram_user_id = message.from_user.id
            await session.commit()
            await state.clear()
            
            keyboard = get_staff_keyboard(employee)
            await message.answer(f"🎉 Доброго дня, {employee.full_name}! Ви успішно авторизовані як {employee.role.name}.", reply_markup=keyboard)
        else:
            await message.answer(f"❌ Співробітника з таким номером не знайдено або він не має прав для ролі '{role_type}'. Спробуйте ще раз.")

    @dp_admin.callback_query(F.data == "cancel_auth")
    async def cancel_auth(callback: CallbackQuery, state: FSMContext):
        await state.clear()
        try: await callback.message.edit_text("Авторизацію скасовано.")
        except Exception: await callback.message.delete()

    @dp_admin.message(F.text.in_({"🟢 Почати зміну", "🔴 Завершити зміну"}))
    async def toggle_shift(message: Message, session: AsyncSession):
        employee = await session.scalar(
            select(Employee).where(Employee.telegram_user_id == message.from_user.id).options(joinedload(Employee.role))
        )
        if not employee: return
        is_start = message.text.startswith("🟢")
        
        employee.is_on_shift = is_start
        await session.commit()
        
        action = "почали" if is_start else "завершили"
        
        debt_text = ""
        if not is_start and employee.cash_balance > 0:
            debt_text = f"\n\n⚠️ <b>Увага!</b> У вас на руках: <b>{employee.cash_balance:.2f} грн</b>.\nБудь ласка, здайте виручку касиру."
            
        await message.answer(f"✅ Ви успішно {action} зміну.{debt_text}", reply_markup=get_staff_keyboard(employee))


    @dp_admin.message(F.text == "🚪 Вийти")
    async def logout_handler(message: Message, session: AsyncSession):
        employee = await session.scalar(
            select(Employee).where(Employee.telegram_user_id == message.from_user.id)
            .options(joinedload(Employee.role))
        )
        if employee:
            if employee.cash_balance > 0:
                await message.answer(f"⚠️ У вас борг {employee.cash_balance} грн. Спочатку здайте касу, потім виходьте.")
                return
                
            employee.telegram_user_id = None
            employee.is_on_shift = False
            await session.commit()
            await message.answer("👋 Ви вийшли з системи.", reply_markup=get_staff_login_keyboard())
        else:
            await message.answer("❌ Ви не авторизовані.")

    @dp_admin.message(F.text.in_({"📦 Мої замовлення", "🍽 Мої столики", "🔪 Кухня", "🍹 Бар"}))
    async def handle_show_items_by_role(message: Message, session: AsyncSession, state: FSMContext, **kwargs: Dict[str, Any]):
        employee = await session.scalar(
            select(Employee).where(Employee.telegram_user_id == message.from_user.id).options(joinedload(Employee.role))
        )
        if not employee: return await message.answer("❌ Ви не авторизовані.")

        if message.text == "📦 Мої замовлення" and employee.role.can_be_assigned:
            await show_courier_orders(message, session)
        elif message.text == "🍽 Мої столики" and employee.role.can_serve_tables:
            await show_waiter_tables(message, session, state)
        elif message.text == "🔪 Кухня" and employee.role.can_receive_kitchen_orders:
            await show_chef_orders(message, session)
        elif message.text == "🍹 Бар" and employee.role.can_receive_bar_orders:
            await show_bartender_orders(message, session)
        else:
            await message.answer("❌ Ваша роль не дозволяє переглядати ці дані.")

    @dp_admin.callback_query(F.data.startswith("courier_view_order_"))
    async def courier_view_order_details(callback: CallbackQuery, session: AsyncSession, **kwargs: Dict[str, Any]):
        order_id = int(callback.data.split("_")[3])
        order = await session.get(Order, order_id, options=[selectinload(Order.items), joinedload(Order.status)])
        if not order: return await callback.answer("Замовлення не знайдено.")

        status_name = order.status.name if order.status else 'Невідомий'
        address_info = order.address if order.is_delivery else 'Самовивіз'
        
        pay_info = ""
        if order.status.is_completed_status:
            pay_info = f"\n<b>Оплата:</b> {'💳 Картка' if order.payment_method == 'card' else '💵 Готівка'}"
            
        products_text = ", ".join([f"{i.product_name} x {i.quantity}" for i in order.items])

        text = (f"<b>Деталі замовлення #{order.id}</b>\n\n"
                f"Статус: {status_name}\n"
                f"Адреса: {html_module.escape(address_info)}\n"
                f"Клієнт: {html_module.escape(order.customer_name or '')}\n"
                f"Телефон: {html_module.escape(order.phone_number or '')}\n" 
                f"Склад: {html_module.escape(products_text)}\n"
                f"Сума: {order.total_price} грн{pay_info}\n\n")
        
        kb = InlineKeyboardBuilder()
        statuses_res = await session.execute(select(OrderStatus).where(OrderStatus.visible_to_courier == True).order_by(OrderStatus.id))
        status_buttons = [InlineKeyboardButton(text=status.name, callback_data=f"staff_set_status_{order.id}_{status.id}") for status in statuses_res.scalars().all()]
        kb.row(*status_buttons)
        
        if order.is_delivery and order.address:
            encoded_address = quote_plus(order.address)
            map_query = f"https://maps.google.com/?q={encoded_address}"
            kb.row(InlineKeyboardButton(text="🗺️ Показати на карті", url=map_query))

        kb.row(InlineKeyboardButton(text="⬅️ До моїх замовлень", callback_data="show_courier_orders_list"))
        await callback.message.edit_text(text, reply_markup=kb.as_markup())
        await callback.answer()

    @dp_admin.callback_query(F.data == "show_courier_orders_list")
    async def back_to_list(callback: CallbackQuery, session: AsyncSession, **kwargs: Dict[str, Any]):
        await show_courier_orders(callback, session)

    # --- ЛОГІКА ВИДАЧІ (СПІЛЬНА ДЛЯ КУХНІ ТА БАРУ) ---
    @dp_admin.callback_query(F.data.startswith("chef_ready_"))
    async def chef_ready_for_issuance(callback: CallbackQuery, session: AsyncSession):
        client_bot = dp_admin.get("client_bot")
        employee = await session.scalar(select(Employee).where(Employee.telegram_user_id == callback.from_user.id).options(joinedload(Employee.role)))
        
        parts = callback.data.split("_")
        order_id = int(parts[2])
        area = parts[3] if len(parts) > 3 else 'kitchen'
        
        # Завантажуємо items для перевірки
        order = await session.get(Order, order_id, options=[
            joinedload(Order.status), 
            joinedload(Order.table), 
            joinedload(Order.accepted_by_waiter),
            joinedload(Order.courier), # Додаємо courier
            selectinload(Order.items)
        ])
        if not order: return await callback.answer("Замовлення не знайдено.")

        ready_status = await session.scalar(select(OrderStatus).where(OrderStatus.name == "Готовий до видачі").limit(1))
        if not ready_status: return await callback.answer("Статус 'Готовий до видачі' не налаштовано.", show_alert=True)
        
        # Встановлюємо флаги готовності цехів та перевіряємо чи не було натиснуто раніше
        already_done = False
        if area == 'kitchen':
            if order.kitchen_done: already_done = True
            order.kitchen_done = True
        elif area == 'bar':
            if order.bar_done: already_done = True
            order.bar_done = True
            
        # Перевіряємо, чи все замовлення готове
        has_kitchen_items = any(item.preparation_area != 'bar' for item in order.items)
        has_bar_items = any(item.preparation_area == 'bar' for item in order.items)
        
        is_fully_ready = True
        if has_kitchen_items and not order.kitchen_done:
            is_fully_ready = False
        if has_bar_items and not order.bar_done:
            is_fully_ready = False
            
        old_status_name = order.status.name
        actor_info = f"{employee.role.name if employee else 'Кухня/Бар'}: {employee.full_name if employee else 'Невідомий'}"
        
        if area == 'bar': actor_info += " (Бар)"
        else: actor_info += " (Кухня)"
        
        # Змінюємо статус тільки якщо все готово
        if is_fully_ready and order.status_id != ready_status.id:
            order.status_id = ready_status.id
            session.add(OrderStatusHistory(order_id=order.id, status_id=ready_status.id, actor_info=actor_info))
        
        await session.commit()
        
        # --- НОВА ЛОГІКА: Сповіщення про готовність цеху ---
        # Відправляємо, якщо цей цех ще не був позначений як готовий (щоб уникнути дублів)
        if not already_done:
            await notify_station_completion(callback.bot, order, area, session)
        # --------------------------------------------------
        
        # Якщо все повністю готове, спрацює стандартне сповіщення про зміну статусу
        if is_fully_ready and old_status_name != ready_status.name:
            await notify_all_parties_on_status_change(
                order=order, 
                old_status_name=old_status_name,
                actor_info=actor_info,
                admin_bot=callback.bot,
                client_bot=client_bot,
                session=session
            )

        products_formatted = await _get_filtered_order_text(session, order, area)
        
        done_text = f"✅ <b>ВИДАНО ({actor_info}): Замовлення #{order.id}</b>\n"
        if not is_fully_ready:
             done_text += "<i>(Чекаємо інший цех для повного завершення)</i>\n"
        done_text += f"Склад:\n{products_formatted}"
        
        try: await callback.message.edit_text(done_text, reply_markup=None)
        except TelegramBadRequest: pass
        
        await callback.answer(f"Сигнал видачі для #{order.id} відправлено!")

    # --- ЛОГІКА ПЕРЕХОПЛЕННЯ ОПЛАТИ ---
    @dp_admin.callback_query(F.data.startswith("staff_ask_payment_"))
    async def staff_ask_payment_method(callback: CallbackQuery, session: AsyncSession):
        parts = callback.data.split("_")
        order_id, status_id = int(parts[3]), int(parts[4])
        
        order = await session.get(Order, order_id)
        if not order: return await callback.answer("Замовлення не знайдено.")
        
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="💵 Готівка", callback_data=f"staff_set_status_{order_id}_{status_id}_cash"))
        kb.row(InlineKeyboardButton(text="💳 Картка / Термінал", callback_data=f"staff_set_status_{order_id}_{status_id}_card"))
        
        if order.order_type == "in_house":
             kb.row(InlineKeyboardButton(text="🔙 Скасувати", callback_data=f"waiter_manage_order_{order_id}"))
        else:
             kb.row(InlineKeyboardButton(text="🔙 Скасувати", callback_data=f"courier_view_order_{order_id}"))
        
        await callback.message.edit_text(
            f"💰 <b>Оплата замовлення #{order.id}</b>\nСума: {order.total_price} грн\n\nОберіть спосіб оплати:",
            reply_markup=kb.as_markup()
        )
        await callback.answer()

    @dp_admin.callback_query(F.data.startswith("staff_set_status_"))
    async def staff_set_status(callback: CallbackQuery, session: AsyncSession, **kwargs: Dict[str, Any]):
        client_bot = dp_admin.get("client_bot")
        employee = await session.scalar(select(Employee).where(Employee.telegram_user_id == callback.from_user.id).options(joinedload(Employee.role)))
        actor_info = f"{employee.role.name}: {employee.full_name}" if employee else f"Співробітник (ID: {callback.from_user.id})"
        
        parts = callback.data.split("_")
        order_id, new_status_id = int(parts[3]), int(parts[4])
        payment_method_override = parts[5] if len(parts) > 5 else None

        order = await session.get(Order, order_id, options=[joinedload(Order.table)])
        if not order: return await callback.answer("Замовлення не знайдено.")
        
        new_status = await session.get(OrderStatus, new_status_id)
        old_status_name = order.status.name if order.status else "Невідомий"
        
        if order.status.is_completed_status or order.status.is_cancelled_status:
             return await callback.answer("⛔️ Замовлення вже закрите. Зміна заборонена.", show_alert=True)

        # Запит методу оплати, якщо це фінальний статус
        if new_status.is_completed_status and not payment_method_override:
            kb = InlineKeyboardBuilder()
            kb.row(InlineKeyboardButton(text="💵 Готівка", callback_data=f"staff_set_status_{order_id}_{new_status_id}_cash"))
            kb.row(InlineKeyboardButton(text="💳 Картка", callback_data=f"staff_set_status_{order_id}_{new_status_id}_card"))
            
            await callback.message.edit_text(
                f"⚠️ <b>Уточніть оплату для замовлення #{order.id}:</b>", 
                reply_markup=kb.as_markup()
            )
            return

        if payment_method_override:
            order.payment_method = payment_method_override

        order.status_id = new_status.id
        session.add(OrderStatusHistory(order_id=order.id, status_id=new_status.id, actor_info=actor_info))
        
        debt_message = ""
        
        # --- КАСОВА ЛОГІКА ---
        if new_status.is_completed_status:
            # Прив'язуємо до поточної зміни
            await link_order_to_shift(session, order, employee.id)
            
            # Якщо готівка - вішаємо борг на співробітника
            if order.payment_method == 'cash':
                await register_employee_debt(session, order, employee.id)
                debt_message = f"\n\n💰 <b>Готівка: {order.total_price} грн</b> записана на ваш баланс. Здайте її касиру в кінці зміни."
        # ---------------------

        await session.commit()
        
        await notify_all_parties_on_status_change(
            order=order,
            old_status_name=old_status_name,
            actor_info=actor_info,
            admin_bot=callback.bot,
            client_bot=client_bot,
            session=session
        )

        pay_text = f" ({'Готівка' if order.payment_method == 'cash' else 'Картка'})" if new_status.is_completed_status else ""
        await callback.answer(f"Статус змінено: {new_status.name}{pay_text}")
        
        if order.order_type == "in_house":
            await manage_in_house_order_handler(callback, session, order_id=order.id)
        else:
            await courier_view_order_details(callback, session)
            
        if debt_message:
             await callback.message.answer(debt_message)

            
    # --- ОБРОБНИКИ ДЛЯ ОФІЦІАНТА ---
    
    @dp_admin.callback_query(F.data.startswith("waiter_view_table_"))
    async def show_waiter_table_orders(callback: CallbackQuery, session: AsyncSession, state: FSMContext, table_id: int = None):
        await state.clear()
        if table_id is None:
            try: table_id = int(callback.data.split("_")[-1])
            except ValueError: return await callback.answer("Помилка даних.", show_alert=True)
        
        table = await session.get(Table, table_id)
        if not table: return await callback.answer("Столик не знайдено!", show_alert=True)

        final_statuses_res = await session.execute(select(OrderStatus.id).where(or_(OrderStatus.is_completed_status == True, OrderStatus.is_cancelled_status == True)))
        final_statuses = final_statuses_res.scalars().all()
        
        active_orders_res = await session.execute(select(Order).where(Order.table_id == table_id, Order.status_id.not_in(final_statuses)).options(joinedload(Order.status)))
        active_orders = active_orders_res.scalars().all()

        text = f"<b>Столик: {html_module.escape(table.name)}</b>\n\nАктивні замовлення:\n"
        kb = InlineKeyboardBuilder()
        if not active_orders:
            text += "\n<i>Немає активних замовлень.</i>"
        else:
            for order in active_orders:
                kb.row(InlineKeyboardButton(
                    text=f"Замовлення #{order.id} ({order.status.name}) - {order.total_price} грн",
                    callback_data=f"waiter_manage_order_{order.id}"
                ))
        
        kb.row(InlineKeyboardButton(text="➕ Створити замовлення", callback_data=f"waiter_create_order_{table.id}"))
        kb.row(InlineKeyboardButton(text="⬅️ До списку столиків", callback_data="back_to_tables_list"))
        
        try: await callback.message.edit_text(text, reply_markup=kb.as_markup())
        except TelegramBadRequest: 
             await callback.message.delete()
             await callback.message.answer(text, reply_markup=kb.as_markup())
        await callback.answer()

    @dp_admin.callback_query(F.data == "back_to_tables_list")
    async def back_to_waiter_tables(callback: CallbackQuery, session: AsyncSession, state: FSMContext): 
        await show_waiter_tables(callback, session, state) 

    @dp_admin.callback_query(F.data.startswith("waiter_manage_order_"))
    async def manage_in_house_order_handler(callback: CallbackQuery, session: AsyncSession, order_id: int = None):
        if not order_id: order_id = int(callback.data.split("_")[-1])
        order = await session.get(Order, order_id, options=[joinedload(Order.table), joinedload(Order.status), joinedload(Order.accepted_by_waiter)])
        if not order: return await callback.answer("Замовлення не знайдено", show_alert=True)

        text, keyboard = await _generate_waiter_order_view(order, session) 
        try: await callback.message.edit_text(text, reply_markup=keyboard)
        except TelegramBadRequest: 
            await callback.message.delete()
            await callback.message.answer(text, reply_markup=keyboard)
        await callback.answer()

    @dp_admin.callback_query(F.data.startswith("waiter_accept_order_"))
    async def waiter_accept_order(callback: CallbackQuery, session: AsyncSession):
        order_id = int(callback.data.split("_")[-1])
        employee = await session.scalar(select(Employee).where(Employee.telegram_user_id == callback.from_user.id))
        
        order = await session.get(Order, order_id, options=[joinedload(Order.status)])
        if order.accepted_by_waiter_id:
            return await callback.answer("Вже прийнято іншим.", show_alert=True)

        order.accepted_by_waiter_id = employee.id
        # Спробуємо перевести в статус "В обробці"
        processing_status = await session.scalar(select(OrderStatus).where(OrderStatus.name == "В обробці").limit(1))
        if processing_status:
            order.status_id = processing_status.id
            session.add(OrderStatusHistory(order_id=order.id, status_id=processing_status.id, actor_info=f"Офіціант: {employee.full_name}"))

        await session.commit()
        await callback.answer(f"Замовлення #{order.id} прийнято!")
        await manage_in_house_order_handler(callback, session, order_id=order.id)

    # --- FSM СТВОРЕННЯ ЗАМОВЛЕННЯ (ОФІЦІАНТ) ---

    async def _display_waiter_cart(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
        data = await state.get_data()
        cart = data.get("cart", {})
        table_name = data.get("table_name", "N/A")
        table_id = data.get("table_id")

        text = f"📝 <b>Створення замовлення для: {html_module.escape(table_name)}</b>\n\n<b>Склад:</b>\n"
        kb = InlineKeyboardBuilder()
        total_price = 0

        if not cart:
            text += "<i>Кошик порожній</i>"
        else:
            for prod_id, item in cart.items():
                # Ціна тут float, тому множимо як float для відображення
                item_total = item['price'] * item['quantity']
                total_price += item_total
                text += f"- {html_module.escape(item['name'])} ({item['quantity']} шт.) = {item_total:.2f} грн\n"
                kb.row(
                    InlineKeyboardButton(text="➖", callback_data=f"waiter_cart_qnt_{prod_id}_-1"),
                    InlineKeyboardButton(text=f"{item['quantity']}x {html_module.escape(item['name'])}", callback_data="noop"),
                    InlineKeyboardButton(text="➕", callback_data=f"waiter_cart_qnt_{prod_id}_1")
                )
        
        text += f"\n\n<b>Загальна сума: {total_price:.2f} грн</b>"
    
        kb.row(InlineKeyboardButton(text="➕ Додати страву", callback_data="waiter_cart_add_item"))
        if cart:
            kb.row(InlineKeyboardButton(text="✅ Оформити замовлення", callback_data="waiter_cart_finalize"))
        kb.row(InlineKeyboardButton(text="⬅️ Скасувати", callback_data=f"waiter_view_table_{table_id}")) 
    
        try: await callback.message.edit_text(text, reply_markup=kb.as_markup())
        except TelegramBadRequest: pass
        await callback.answer()

    @dp_admin.callback_query(F.data.startswith("waiter_create_order_"))
    async def waiter_create_order_start(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
        table_id = int(callback.data.split("_")[-1])
        table = await session.get(Table, table_id)
        if not table: return await callback.answer("Столик не знайдено!", show_alert=True)
        
        await state.set_state(WaiterCreateOrderStates.managing_cart)
        await state.update_data(cart={}, table_id=table_id, table_name=table.name)
        await _display_waiter_cart(callback, state, session)

    @dp_admin.callback_query(WaiterCreateOrderStates.managing_cart, F.data == "waiter_cart_add_item")
    async def waiter_cart_add_item(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
        await state.set_state(WaiterCreateOrderStates.choosing_category)
        categories_res = await session.execute(select(Category).where(Category.show_in_restaurant == True).order_by(Category.sort_order, Category.name))
        
        kb = InlineKeyboardBuilder()
        for cat in categories_res.scalars().all():
            kb.add(InlineKeyboardButton(text=cat.name, callback_data=f"waiter_cart_cat_{cat.id}"))
        kb.adjust(2)
        kb.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="waiter_cart_back_to_cart"))
        
        await callback.message.edit_text("Виберіть категорію:", reply_markup=kb.as_markup())

    @dp_admin.callback_query(F.data == "waiter_cart_back_to_cart", WaiterCreateOrderStates.choosing_category)
    @dp_admin.callback_query(F.data == "waiter_cart_back_to_cart", WaiterCreateOrderStates.choosing_product)
    async def waiter_cart_back_to_cart(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
        await state.set_state(WaiterCreateOrderStates.managing_cart)
        await _display_waiter_cart(callback, state, session)

    @dp_admin.callback_query(WaiterCreateOrderStates.choosing_category, F.data.startswith("waiter_cart_cat_"))
    async def waiter_cart_show_category(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
        category_id = int(callback.data.split("_")[-1])
        await state.set_state(WaiterCreateOrderStates.choosing_product)
        
        products_res = await session.execute(select(Product).where(Product.category_id == category_id, Product.is_active == True).order_by(Product.name))
        
        kb = InlineKeyboardBuilder()
        for prod in products_res.scalars().all():
            kb.add(InlineKeyboardButton(text=f"{prod.name} - {prod.price} грн", callback_data=f"waiter_cart_prod_{prod.id}"))
        kb.adjust(1)
        kb.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="waiter_cart_back_to_categories"))
        
        await callback.message.edit_text("Виберіть страву:", reply_markup=kb.as_markup())

    @dp_admin.callback_query(F.data == "waiter_cart_back_to_categories", WaiterCreateOrderStates.choosing_product)
    async def waiter_cart_back_to_categories(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
        await waiter_cart_add_item(callback, state, session)

    @dp_admin.callback_query(WaiterCreateOrderStates.choosing_product, F.data.startswith("waiter_cart_prod_"))
    async def waiter_cart_add_product(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
        product_id = int(callback.data.split("_")[-1])
        product = await session.get(Product, product_id)
        
        data = await state.get_data()
        cart = data.get("cart", {})
        
        if str(product_id) in cart: cart[str(product_id)]["quantity"] += 1
        else: 
            # Зберігаємо preparation_area для подальшого створення OrderItem
            # Зберігаємо ціну як float для серіалізації в JSON (стан)
            cart[str(product_id)] = {
                "name": product.name, 
                "price": float(product.price), # Convert Decimal to float for JSON storage in FSM
                "quantity": 1,
                "area": product.preparation_area
            }
        
        await state.update_data(cart=cart)
        await state.set_state(WaiterCreateOrderStates.managing_cart)
        await _display_waiter_cart(callback, state, session)
        await callback.answer(f"{product.name} додано.")

    @dp_admin.callback_query(WaiterCreateOrderStates.managing_cart, F.data.startswith("waiter_cart_qnt_"))
    async def waiter_cart_change_quantity(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
        prod_id, change = callback.data.split("_")[3:]
        change = int(change)
        data = await state.get_data()
        cart = data.get("cart", {})
        
        if prod_id in cart:
            cart[prod_id]["quantity"] += change
            if cart[prod_id]["quantity"] <= 0: del cart[prod_id]
        
        await state.update_data(cart=cart)
        await _display_waiter_cart(callback, state, session)

    @dp_admin.callback_query(WaiterCreateOrderStates.managing_cart, F.data == "waiter_cart_finalize")
    async def waiter_cart_finalize(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
        data = await state.get_data()
        cart = data.get("cart", {})
        table_id = data.get("table_id")
        table_name = data.get("table_name")
        
        employee = await session.scalar(select(Employee).where(Employee.telegram_user_id == callback.from_user.id))
        
        # Розрахунок суми з використанням Decimal
        total_price = Decimal('0.00')
        
        # Створюємо тимчасовий список для OrderItems, щоб не ітерувати двічі
        items_to_create = []

        for prod_id, item in cart.items():
            # Конвертуємо ціну з float назад у Decimal через рядок для точності
            price_decimal = Decimal(str(item['price']))
            qty = item['quantity']
            
            total_price += price_decimal * qty
            
            items_to_create.append({
                "product_id": int(prod_id),
                "name": item['name'],
                "quantity": qty,
                "price": price_decimal,
                "area": item.get('area', 'kitchen')
            })
        
        new_status = await session.scalar(select(OrderStatus).where(OrderStatus.name == "Новий").limit(1))
        status_id = new_status.id if new_status else 1

        # Створюємо замовлення
        order = Order(
            customer_name=f"Стіл: {table_name}", phone_number=f"table_{table_id}",
            total_price=total_price, is_delivery=False,
            delivery_time="In House", order_type="in_house", table_id=table_id,
            status_id=status_id, accepted_by_waiter_id=employee.id
        )
        session.add(order)
        await session.flush() # Отримуємо ID замовлення

        # Створюємо OrderItems
        for item_data in items_to_create:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product_id"],
                product_name=item_data["name"],
                quantity=item_data["quantity"],
                price_at_moment=item_data["price"], # Decimal
                preparation_area=item_data["area"]
            )
            session.add(order_item)

        await session.commit()
        
        await session.refresh(order, ['status'])
        
        session.add(OrderStatusHistory(order_id=order.id, status_id=order.status_id, actor_info=f"Офіціант: {employee.full_name}"))
        await session.commit()
        
        await callback.answer(f"Замовлення #{order.id} створено!")
        
        admin_bot = dp_admin.get("bot_instance")
        if admin_bot:
            await notify_new_order_to_staff(admin_bot, order, session)

        await state.clear()
        await show_waiter_table_orders(callback, session, state, table_id=table_id)