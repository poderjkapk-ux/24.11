# admin_order_management.py

import html
import logging
import os
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from aiogram import Bot
from urllib.parse import quote_plus
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
import re

from models import Order, OrderStatus, Employee, Role, OrderStatusHistory, Settings, Product, OrderItem
from templates import ADMIN_HTML_TEMPLATE, ADMIN_ORDER_MANAGE_BODY
from dependencies import get_db_session, check_credentials
from notification_manager import notify_all_parties_on_status_change
# --- КАСА: Імпорт сервісів ---
from cash_service import link_order_to_shift, register_employee_debt

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/admin/order/manage/{order_id}", response_class=HTMLResponse)
async def get_manage_order_page(
    order_id: int,
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    """Відображає сторінку керування для конкретного замовлення."""
    settings = await session.get(Settings, 1) or Settings()
    
    order = await session.get(
        Order,
        order_id,
        options=[
            joinedload(Order.status),
            joinedload(Order.courier),
            joinedload(Order.history).joinedload(OrderStatusHistory.status),
            joinedload(Order.table),
            selectinload(Order.items) # Завантажуємо товари
        ]
    )
    if not order:
        raise HTTPException(status_code=404, detail="Замовлення не знайдено")

    # --- Формування списку товарів з іконками цехів ---
    products_html_list = []
    
    if order.items:
        for item in order.items:
            icon = "❓"
            # Визначаємо іконку на основі збереженого preparation_area
            if item.preparation_area == 'kitchen':
                icon = "🍳" 
            elif item.preparation_area == 'bar':
                icon = "🍹" 
            
            products_html_list.append(f"<li>{icon} {html.escape(item.product_name)} x {item.quantity} ({item.price_at_moment} грн)</li>")
    
    products_html = "<ul>" + "".join(products_html_list) + "</ul>" if products_html_list else "<i>Товарів немає</i>"
    # ---------------------------------------------------

    statuses_res = await session.execute(select(OrderStatus).order_by(OrderStatus.id))
    all_statuses = statuses_res.scalars().all()
    status_options = "".join([f'<option value="{s.id}" {"selected" if s.id == order.status_id else ""}>{html.escape(s.name)}</option>' for s in all_statuses])

    courier_role_res = await session.execute(select(Role.id).where(Role.can_be_assigned == True))
    courier_role_ids = courier_role_res.scalars().all()
    
    couriers_on_shift = []
    if courier_role_ids:
        couriers_res = await session.execute(
            select(Employee)
            .where(Employee.role_id.in_(courier_role_ids), Employee.is_on_shift == True)
            .order_by(Employee.full_name)
        )
        couriers_on_shift = couriers_res.scalars().all()
        
    courier_options = '<option value="0">Не призначено</option>'
    courier_options += "".join([f'<option value="{c.id}" {"selected" if c.id == order.courier_id else ""}>{html.escape(c.full_name)}</option>' for c in couriers_on_shift])

    history_html = "<ul class='status-history'>"
    sorted_history = sorted(order.history, key=lambda h: h.timestamp, reverse=True)
    for entry in sorted_history:
        timestamp = entry.timestamp.strftime('%d.%m.%Y %H:%M')
        history_html += f"<li><b>{entry.status.name}</b> (Ким: {html.escape(entry.actor_info)}) - {timestamp}</li>"
    history_html += "</ul>"
    
    # --- Payment Method & Cash Status ---
    sel_cash = "selected" if order.payment_method == 'cash' else ""
    sel_card = "selected" if order.payment_method == 'card' else ""
    
    payment_method_text = "Готівка" if order.payment_method == 'cash' else "Картка"
    
    # Додаємо інформацію про здачу виручки
    if order.payment_method == 'cash' and order.status.is_completed_status:
        if order.is_cash_turned_in:
            payment_method_text += " <span style='color:green; font-weight:bold;'>(В касі ✅)</span>"
        else:
            payment_method_text += " <span style='color:red; font-weight:bold;'>(Не здано ❌)</span>"

    # --- Адреса ---
    if order.order_type == 'in_house':
        table_name = order.table.name if order.table else '?'
        display_address = f"📍 В закладі (Стіл: {html.escape(table_name)})"
    elif order.is_delivery:
        display_address = html.escape(order.address or "Адреса не вказана")
    else:
        display_address = "🏃 Самовивіз"
    # --------------

    body = ADMIN_ORDER_MANAGE_BODY.format(
        order_id=order.id,
        customer_name=html.escape(order.customer_name or "Не вказано"),
        phone_number=html.escape(order.phone_number or "Не вказано"),
        address=display_address,
        total_price=order.total_price,
        products_html=products_html,
        status_options=status_options,
        courier_options=courier_options,
        history_html=history_html or "<p>Історія статусів порожня.</p>",
        sel_cash=sel_cash, 
        sel_card=sel_card, 
        payment_method_text=payment_method_text 
    )

    active_classes = {key: "" for key in ["clients_active", "main_active", "products_active", "categories_active", "statuses_active", "settings_active", "employees_active", "reports_active", "menu_active", "tables_active", "design_active"]}
    active_classes["orders_active"] = "active"
    return HTMLResponse(ADMIN_HTML_TEMPLATE.format(
        title=f"Керування замовленням #{order.id}", 
        body=body, 
        site_title=settings.site_title or "Назва", 
        **active_classes
    ))


@router.post("/admin/order/manage/{order_id}/set_status")
async def web_set_order_status(
    request: Request, 
    order_id: int,
    status_id: int = Form(...),
    payment_method: str = Form("cash"), 
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    """Обробляє зміну статусу замовлення з веб-панелі."""
    order = await session.get(Order, order_id, options=[joinedload(Order.status)])
    if not order:
        raise HTTPException(status_code=404, detail="Замовлення не знайдено")
    
    # Забороняємо змінювати метод оплати, якщо замовлення вже закрите (щоб не зламати касу)
    if not (order.status.is_completed_status or order.status.is_cancelled_status):
        order.payment_method = payment_method

    # Перевірка: якщо замовлення вже закрите
    if order.status.is_completed_status or order.status.is_cancelled_status:
        raise HTTPException(status_code=400, detail="Замовлення вже закрите. Зміна статусу заборонена.")

    if order.status_id == status_id:
        await session.commit()
        return RedirectResponse(url=f"/admin/order/manage/{order_id}", status_code=303)

    new_status = await session.get(OrderStatus, status_id)
    old_status_name = order.status.name if order.status else "Невідомий"
    
    order.status_id = status_id
    actor_info = "Адміністратор веб-панелі"
    
    history_entry = OrderStatusHistory(order_id=order.id, status_id=status_id, actor_info=actor_info)
    session.add(history_entry)
    
    # --- ЛОГІКА КАСИ ПРИ ЗАКРИТТІ ЧЕРЕЗ АДМІНКУ ---
    if new_status.is_completed_status:
        # 1. Прив'язуємо до зміни (адміна/касира або будь-якої відкритої)
        # Тут ми не знаємо ID співробітника-адміна з вебу, тому передаємо None, 
        # і функція знайде першу відкриту зміну.
        await link_order_to_shift(session, order, None) 
        
        # 2. Якщо це готівка, вирішуємо, де гроші
        if order.payment_method == 'cash':
            # Якщо є кур'єр, то гроші у нього (борг)
            if order.courier_id:
                await register_employee_debt(session, order, order.courier_id)
            # Якщо це офіціант (в закладі), то гроші у нього
            elif order.accepted_by_waiter_id:
                await register_employee_debt(session, order, order.accepted_by_waiter_id)
            else:
                # Якщо нікого немає (Самовивіз або адмін сам продав)
                # Вважаємо, що гроші відразу потрапили в касу (так як адмін зазвичай стоїть на касі)
                order.is_cash_turned_in = True
    # ----------------------------------------------

    await session.commit()

    # Сповіщення
    admin_bot = request.app.state.admin_bot
    client_bot = request.app.state.client_bot

    if admin_bot:
        await notify_all_parties_on_status_change(
            order=order,
            old_status_name=old_status_name,
            actor_info=actor_info,
            admin_bot=admin_bot,
            client_bot=client_bot,
            session=session
        )

    return RedirectResponse(url=f"/admin/order/manage/{order_id}", status_code=303)


@router.post("/admin/order/manage/{order_id}/assign_courier")
async def web_assign_courier(
    request: Request,
    order_id: int,
    courier_id: int = Form(...),
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    """Обробляє призначення кур'єра на замовлення з веб-панелі."""
    order = await session.get(Order, order_id, options=[joinedload(Order.status)])
    if not order:
        raise HTTPException(status_code=404, detail="Замовлення не знайдено")

    if order.status.is_completed_status or order.status.is_cancelled_status:
        raise HTTPException(status_code=400, detail="Замовлення вже закрите. Призначення кур'єра заборонено.")

    admin_bot = request.app.state.admin_bot
    # Не кидаємо помилку, якщо бот не налаштований, просто логуємо
    if not admin_bot:
         logger.warning("Admin bot not configured, notifications skipped.")
         
    admin_chat_id_str = os.environ.get('ADMIN_CHAT_ID')

    old_courier_id = order.courier_id
    new_courier_name = "Не призначено"

    if old_courier_id and old_courier_id != courier_id:
        old_courier = await session.get(Employee, old_courier_id)
        if old_courier and old_courier.telegram_user_id and admin_bot:
            try:
                await admin_bot.send_message(old_courier.telegram_user_id, f"❗️ Замовлення #{order.id} було знято з вас оператором.")
            except Exception as e:
                logger.error(f"Не вдалося сповістити колишнього кур'єра {old_courier.id}: {e}")

    if courier_id == 0:
        order.courier_id = None
    else:
        new_courier = await session.get(Employee, courier_id)
        if not new_courier:
            raise HTTPException(status_code=404, detail="Кур'єра не знайдено")
        
        order.courier_id = courier_id
        new_courier_name = new_courier.full_name
        
        if new_courier.telegram_user_id and admin_bot:
            try:
                kb_courier = InlineKeyboardBuilder()
                statuses_res = await session.execute(select(OrderStatus).where(OrderStatus.visible_to_courier == True).order_by(OrderStatus.id))
                statuses = statuses_res.scalars().all()
                kb_courier.row(*[InlineKeyboardButton(text=s.name, callback_data=f"courier_set_status_{order.id}_{s.id}") for s in statuses])
                
                if order.is_delivery and order.address:
                    encoded_address = quote_plus(order.address)
                    map_url = f"http://googleusercontent.com/maps/google.com/0{encoded_address}"
                    kb_courier.row(InlineKeyboardButton(text="🗺️ На карті", url=map_url))
                    
                await admin_bot.send_message(
                    new_courier.telegram_user_id,
                    f"🔔 Вам призначено нове замовлення!\n\n<b>Замовлення #{order.id}</b>\nАдреса: {html.escape(order.address or 'Самовивіз')}\nТелефон: {html.escape(order.phone_number or 'Не вказано')}\nСума: {order.total_price} грн.",
                    reply_markup=kb_courier.as_markup()
                )
            except Exception as e:
                logger.error(f"Не вдалося сповістити нового кур'єра {new_courier.telegram_user_id}: {e}")
    
    await session.commit()

    if admin_chat_id_str and admin_bot:
        try:
            await admin_bot.send_message(admin_chat_id_str, f"👤 Замовленню #{order.id} призначено кур'єра: <b>{html.escape(new_courier_name)}</b> (через веб-панель)")
        except Exception: pass
    
    return RedirectResponse(url=f"/admin/order/manage/{order_id}", status_code=303)