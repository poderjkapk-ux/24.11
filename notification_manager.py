# notification_manager.py
import logging
import os
from aiogram import Bot, html
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from models import Order, OrderStatus, Employee, Role, OrderItem

logger = logging.getLogger(__name__)

async def notify_new_order_to_staff(admin_bot: Bot, order: Order, session: AsyncSession):
    """
    Надсилає сповіщення про НОВЕ замовлення в загальний чат, операторам.
    """
    admin_chat_id_str = os.environ.get('ADMIN_CHAT_ID')
    
    # Завантажуємо зв'язки для відображення
    # Використовуємо selectinload для колекцій (items) та joinedload для одиничних зв'язків
    query = select(Order).where(Order.id == order.id).options(
        selectinload(Order.items),
        joinedload(Order.status),
        joinedload(Order.table)
    )
    result = await session.execute(query)
    # Оновлюємо об'єкт order актуальними даними
    order = result.scalar_one()

    is_delivery = order.is_delivery 

    if order.order_type == 'in_house':
        delivery_info = f"📍 <b>В закладі</b> (Стіл: {html.quote(order.table.name if order.table else 'Невідомий')})"
        source = "Джерело: 🤵 Офіціант / QR"
    elif is_delivery:
        delivery_info = f"🚚 <b>Доставка</b>: {html.quote(order.address or 'Не вказана')}"
        source = f"Джерело: {'🌐 Веб-сайт' if order.user_id is None else '🤖 Telegram-бот'}"
    else:
        delivery_info = "🏃 <b>Самовивіз</b>"
        source = f"Джерело: {'🌐 Веб-сайт' if order.user_id is None else '🤖 Telegram-бот'}"

    status_name = order.status.name if order.status else 'Невідомий'
    time_info = f"Час: {html.quote(order.delivery_time)}"
    
    # Формуємо список товарів з об'єктів OrderItem
    products_formatted = ""
    if order.items:
        products_formatted = "\n".join([f"- {html.quote(item.product_name)} x {item.quantity}" for item in order.items])
    else:
        products_formatted = "- <i>Немає товарів</i>"
    
    admin_text = (f"<b>Замовлення #{order.id}</b>\n{source}\n\n"
                  f"<b>Клієнт:</b> {html.quote(order.customer_name or 'Не вказано')}\n<b>Телефон:</b> {html.quote(order.phone_number or 'Не вказано')}\n"
                  f"{delivery_info}\n<b>{time_info}</b>\n\n"
                  f"<b>Страви:</b>\n{products_formatted}\n\n"
                  f"<b>Сума:</b> {order.total_price} грн\n\n"
                  f"<b>Статус:</b> {status_name}")

    # --- КЛАВІАТУРА ДЛЯ ОПЕРАТОРА ---
    kb_admin = InlineKeyboardBuilder()
    statuses_res = await session.execute(
        select(OrderStatus).where(OrderStatus.visible_to_operator == True).order_by(OrderStatus.id)
    )
    status_buttons = [
        InlineKeyboardButton(text=s.name, callback_data=f"change_order_status_{order.id}_{s.id}")
        for s in statuses_res.scalars().all()
    ]
    for i in range(0, len(status_buttons), 2):
        kb_admin.row(*status_buttons[i:i+2])
    kb_admin.row(InlineKeyboardButton(text="👤 Призначити кур'єра", callback_data=f"select_courier_{order.id}"))
    kb_admin.row(InlineKeyboardButton(text="✏️ Редагувати замовлення", callback_data=f"edit_order_{order.id}"))
    # --------------------------------------------------------

    # 1. Відправка в загальний адмін-чат та операторам
    target_chat_ids = set()
    if admin_chat_id_str:
        try:
            target_chat_ids.add(int(admin_chat_id_str))
        except ValueError:
            logger.warning(f"Некоректний ADMIN_CHAT_ID: {admin_chat_id_str}")

    operator_roles_res = await session.execute(select(Role.id).where(Role.can_manage_orders == True))
    operator_role_ids = operator_roles_res.scalars().all()

    operators_on_shift_res = await session.execute(
        select(Employee).where(
            Employee.role_id.in_(operator_role_ids),
            Employee.is_on_shift == True,
            Employee.telegram_user_id.is_not(None)
        )
    )
    for operator in operators_on_shift_res.scalars().all():
        if operator.telegram_user_id not in target_chat_ids:
            target_chat_ids.add(operator.telegram_user_id)
            
    for chat_id in target_chat_ids:
        try:
            await admin_bot.send_message(chat_id, admin_text, reply_markup=kb_admin.as_markup())
        except Exception as e:
            logger.error(f"Не вдалося відправити нове замовлення оператору/адміну {chat_id}: {e}")

    # 2. РОЗПОДІЛ НА ВИРОБНИЦТВО (Кухня/Бар)
    # Якщо статус нового замовлення одразу вимагає приготування
    if order.status and order.status.requires_kitchen_notify:
        await distribute_order_to_production(admin_bot, order, session)
    else:
        logger.info(f"Замовлення #{order.id} створено, очікує підтвердження.")


async def distribute_order_to_production(bot: Bot, order: Order, session: AsyncSession):
    """
    Розподіляє товари замовлення між Кухнею та Баром і надсилає відповідним працівникам.
    """
    # Завантажуємо items разом з product, щоб знати preparation_area
    query = select(Order).where(Order.id == order.id).options(
        selectinload(Order.items).joinedload(OrderItem.product)
    )
    result = await session.execute(query)
    loaded_order = result.scalar_one()

    kitchen_items = []
    bar_items = []

    for item in loaded_order.items:
        item_str = f"- {html.quote(item.product_name)} x {item.quantity}"
        
        # Визначаємо цех
        area = 'kitchen' # За замовчуванням
        if item.product:
            area = item.product.preparation_area
        
        if area == 'bar':
            bar_items.append(item_str)
        else:
            kitchen_items.append(item_str)

    # 3. Відправляємо на Кухню
    if kitchen_items:
        await send_group_notification(
            bot=bot,
            order=loaded_order,
            items=kitchen_items,
            role_filter=Role.can_receive_kitchen_orders == True,
            title="🧑‍🍳 ЗАМОВЛЕННЯ НА КУХНЮ",
            session=session,
            area="kitchen"
        )

    # 4. Відправляємо на Бар
    if bar_items:
        await send_group_notification(
            bot=bot,
            order=loaded_order,
            items=bar_items,
            role_filter=Role.can_receive_bar_orders == True,
            title="🍹 ЗАМОВЛЕННЯ НА БАР",
            session=session,
            area="bar"
        )


async def send_group_notification(bot: Bot, order: Order, items: list, role_filter, title: str, session: AsyncSession, area: str = "kitchen"):
    """
    Універсальна функція для відправки чека групі співробітників.
    """
    # Шукаємо ролі
    roles_res = await session.execute(select(Role.id).where(role_filter))
    role_ids = roles_res.scalars().all()

    if not role_ids:
        return

    # Шукаємо працівників на зміні
    employees_res = await session.execute(
        select(Employee).where(
            Employee.role_id.in_(role_ids),
            Employee.is_on_shift == True,
            Employee.telegram_user_id.is_not(None)
        )
    )
    employees = employees_res.scalars().all()

    if employees:
        is_delivery = order.is_delivery
        items_formatted = "\n".join(items)
        
        table_info = ""
        if order.order_type == 'in_house' and order.table:
             table_info = f" (Стіл: {html.quote(order.table.name)})"
        
        text = (f"{title}: <b>#{order.id}</b>{table_info}\n"
                f"<b>Тип:</b> {'Доставка' if is_delivery else 'В закладі / Самовивіз'}\n"
                f"<b>Час:</b> {html.quote(order.delivery_time)}\n\n"
                f"<b>СКЛАД:</b>\n{items_formatted}\n\n"
                f"<i>Натисніть 'Видача', коли буде готове.</i>")
        
        kb = InlineKeyboardBuilder()
        # Важливо: callback data містить area, щоб розрізняти кухню і бар
        kb.row(InlineKeyboardButton(text=f"✅ Видача #{order.id}", callback_data=f"chef_ready_{order.id}_{area}"))
        
        for emp in employees:
            try:
                await bot.send_message(emp.telegram_user_id, text, reply_markup=kb.as_markup())
            except Exception as e:
                logger.error(f"Не вдалося відправити замовлення працівнику {emp.id}: {e}")


async def notify_station_completion(bot: Bot, order: Order, area: str, session: AsyncSession):
    """
    Сповіщає офіціанта або кур'єра, що конкретний цех (Кухня або Бар) виконав свою частину.
    Це дозволяє забирати готові страви/напої, не чекаючи повної готовності замовлення.
    """
    # Завантажуємо необхідні дані про виконавців
    await session.refresh(order, ['table', 'accepted_by_waiter', 'courier'])
    
    source_label = "🍳 КУХНЯ" if area == 'kitchen' else "🍹 БАР"
    
    # Формуємо текст повідомлення
    table_info = f" (Стіл: {html.quote(order.table.name)})" if order.table else ""
    order_info = f"<b>Замовлення #{order.id}</b>{table_info}"
    
    message_text = f"✅ <b>{source_label} ГОТОВА!</b>\n{order_info}\n<i>Можна забирати частину замовлення.</i>"

    # Визначаємо отримувачів
    target_chat_ids = set()

    # 1. Якщо це замовлення в закладі - сповіщаємо офіціанта
    if order.order_type == 'in_house' and order.accepted_by_waiter and order.accepted_by_waiter.telegram_user_id:
        target_chat_ids.add(order.accepted_by_waiter.telegram_user_id)
    
    # 2. Якщо це доставка - сповіщаємо кур'єра
    if order.is_delivery and order.courier and order.courier.telegram_user_id:
        target_chat_ids.add(order.courier.telegram_user_id)

    # 3. Якщо ніхто не закріплений (або самовивіз без кур'єра), можна сповістити операторів
    if not target_chat_ids:
        admin_chat_id_str = os.environ.get('ADMIN_CHAT_ID')
        if admin_chat_id_str:
             # Додаємо позначку, що це для адміністратора
             message_text = f"⚠️ {message_text}\n(Виконавець не призначений)"
             try:
                 target_chat_ids.add(int(admin_chat_id_str))
             except ValueError: pass

    # Відправка повідомлень
    for chat_id in target_chat_ids:
        try:
            await bot.send_message(chat_id, message_text)
        except Exception as e:
            logger.error(f"Не вдалося надіслати сповіщення про готовність цеху {area} користувачу {chat_id}: {e}")


async def notify_all_parties_on_status_change(
    order: Order,
    old_status_name: str,
    actor_info: str,
    admin_bot: Bot,
    client_bot: Bot | None,
    session: AsyncSession
):
    """
    Централізована функція для надсилання всіх сповіщень при зміні статусу.
    """
    # Завантажуємо необхідні зв'язки
    await session.refresh(order, ['status', 'courier', 'accepted_by_waiter', 'table'])
    admin_chat_id_str = os.environ.get('ADMIN_CHAT_ID')
    
    new_status = order.status
    
    # 1. Сповіщення в головний АДМІН-ЧАТ (Лог)
    if admin_chat_id_str:
        log_message = (
            f"🔄 <b>[Статус змінено]</b> Замовлення #{order.id}\n"
            f"<b>Ким:</b> {html.quote(actor_info)}\n"
            f"<b>Статус:</b> `{html.quote(old_status_name)}` → `{html.quote(new_status.name)}`"
        )
        try:
            await admin_bot.send_message(admin_chat_id_str, log_message)
        except Exception as e:
            logger.error(f"Не вдалося відправити лог в адмін-чат: {e}")

    # 2. ЛОГІКА ДЛЯ ВИРОБНИЦТВА (Кухня/Бар)
    # Якщо статус змінився на такий, що вимагає приготування (наприклад "В обробці")
    if new_status.requires_kitchen_notify:
        await distribute_order_to_production(admin_bot, order, session)

    # 3. СПОВІЩЕННЯ ПІД ЧАС ВИДАЧІ ("Готовий до видачі")
    if new_status.name == "Готовий до видачі":
        # --- ВИЗНАЧЕННЯ ДЖЕРЕЛА (Хто приготував?) ---
        source_label = ""
        if "Кухня" in actor_info:
            source_label = " (🍳 КУХНЯ)"
        elif "Бар" in actor_info:
            source_label = " (🍹 БАР)"
        
        ready_message = f"📢 <b>ГОТОВО ДО ВИДАЧІ{source_label}: #{order.id}</b>! \n"
        
        # Додаємо попередження, якщо це лише частина замовлення (наприклад, бар зробив, а кухня ще ні)
        # Це логіка перевірки прапорців, які ми встановимо в хендлерах
        if not (order.kitchen_done and order.bar_done) and (order.kitchen_done or order.bar_done):
             ready_message += "⚠️ <b>УВАГА: Це лише частина замовлення!</b> Перевірте інший цех.\n"

        target_employees = []
        # Якщо є офіціант (для замовлення в закладі)
        if order.order_type == 'in_house' and order.accepted_by_waiter and order.accepted_by_waiter.is_on_shift:
            target_employees.append(order.accepted_by_waiter)
            ready_message += f"Стіл: {html.quote(order.table.name if order.table else 'N/A')}. Прийняв: {html.quote(order.accepted_by_waiter.full_name)}"
        
        # Якщо є кур'єр (для доставки)
        if order.is_delivery and order.courier and order.courier.is_on_shift:
            target_employees.append(order.courier)
            ready_message += f"Призначений кур'єр: {html.quote(order.courier.full_name)}"

        # Якщо нікого немає, сповіщаємо операторів
        if not target_employees:
             operator_roles_res = await session.execute(select(Role.id).where(Role.can_manage_orders == True))
             operator_role_ids = operator_roles_res.scalars().all()
             operators_on_shift_res = await session.execute(
                 select(Employee).where(
                     Employee.role_id.in_(operator_role_ids),
                     Employee.is_on_shift == True,
                     Employee.telegram_user_id.is_not(None)
                 )
             )
             target_employees.extend(operators_on_shift_res.scalars().all())
             ready_message += f"Тип: {'Самовивіз' if order.order_type == 'pickup' else 'Доставка'}. Потрібна видача."
             
        for employee in target_employees:
            if employee.telegram_user_id:
                try:
                    await admin_bot.send_message(employee.telegram_user_id, ready_message)
                except Exception as e:
                    logger.error(f"Не вдалося сповістити {employee.telegram_user_id} про готовність: {e}")

    # 4. Сповіщення призначеному КУР'ЄРУ (про інші зміни статусу, окрім видачі)
    if order.courier and order.courier.telegram_user_id and "Кур'єр" not in actor_info and new_status.name != "Готовий до видачі":
        if new_status.visible_to_courier:
            courier_text = f"❗️ Статус вашого замовлення #{order.id} змінено на: <b>{new_status.name}</b>"
            try:
                await admin_bot.send_message(order.courier.telegram_user_id, courier_text)
            except Exception: pass

    # 5. Сповіщення призначеному ОФІЦІАНТУ (про інші зміни статусу)
    if order.order_type != 'delivery' and order.accepted_by_waiter and order.accepted_by_waiter.telegram_user_id and "Офіціант" not in actor_info and new_status.name != "Готовий до видачі":
        waiter_text = f"📢 Замовлення #{order.id} (Стіл: {html.quote(order.table.name if order.table else 'N/A')}) має новий статус: <b>{new_status.name}</b>"
        try:
            await admin_bot.send_message(order.accepted_by_waiter.telegram_user_id, waiter_text)
        except Exception: pass

    # 6. Сповіщення КЛІЄНТУ
    if new_status.notify_customer and order.user_id and client_bot:
        client_text = f"Статус вашого замовлення #{order.id} змінено на: <b>{new_status.name}</b>"
        try:
            await client_bot.send_message(order.user_id, client_text)
        except Exception as e:
            logger.error(f"Не вдалося сповістити клієнта {order.user_id}: {e}")