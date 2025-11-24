# cash_service.py

import logging
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import joinedload
from models import CashShift, CashTransaction, Order, Employee

logger = logging.getLogger(__name__)

async def get_open_shift(session: AsyncSession, employee_id: int) -> CashShift | None:
    """Повертає відкриту зміну співробітника або None."""
    result = await session.execute(
        select(CashShift).where(
            CashShift.employee_id == employee_id,
            CashShift.is_closed == False
        )
    )
    return result.scalars().first()

async def get_any_open_shift(session: AsyncSession) -> CashShift | None:
    """Повертає першу ліпшу відкриту зміну (для веб-адмінки)."""
    result = await session.execute(
        select(CashShift).where(CashShift.is_closed == False).limit(1)
    )
    return result.scalars().first()

async def open_new_shift(session: AsyncSession, employee_id: int, start_cash: Decimal) -> CashShift:
    """Відкриває нову касову зміну."""
    active_shift = await get_open_shift(session, employee_id)
    if active_shift:
        raise ValueError("У цього співробітника вже є відкрита зміна.")

    # Перевірка, чи немає іншої відкритої зміни (одна каса на всіх)
    any_shift = await get_any_open_shift(session)
    if any_shift:
         raise ValueError(f"Зміна вже відкрита співробітником {any_shift.employee_id}. Закрийте її спочатку.")

    new_shift = CashShift(
        employee_id=employee_id,
        start_time=datetime.now(),
        start_cash=start_cash,
        is_closed=False
    )
    session.add(new_shift)
    await session.commit()
    await session.refresh(new_shift)
    return new_shift

async def link_order_to_shift(session: AsyncSession, order: Order, employee_id: int | None):
    """
    Прив'язує замовлення до відкритої зміни.
    Це важливо для статистики продажів (Z-звіт).
    """
    if order.cash_shift_id:
        return 

    shift = None
    # Якщо це касир/оператор закриває замовлення, шукаємо його зміну
    if employee_id:
        shift = await get_open_shift(session, employee_id)
    
    if not shift:
        # Якщо не знайдено, беремо будь-яку активну зміну (загальна каса)
        shift = await get_any_open_shift(session)
    
    if shift:
        order.cash_shift_id = shift.id
        # session.commit() робитиме викликаючий код
        logger.info(f"Замовлення #{order.id} прив'язано до зміни #{shift.id} для статистики.")
    else:
        logger.warning(f"УВАГА: Замовлення #{order.id} не прив'язано до зміни (немає відкритих змін).")

async def register_employee_debt(session: AsyncSession, order: Order, employee_id: int):
    """
    Фіксує, що співробітник (кур'єр/офіціант) отримав готівку за замовлення.
    Збільшує його баланс (борг перед касою).
    """
    if order.payment_method != 'cash':
        return # Борг виникає тільки при готівці

    employee = await session.get(Employee, employee_id)
    if not employee:
        logger.error(f"Співробітника {employee_id} не знайдено при реєстрації боргу.")
        return

    # order.total_price це Decimal
    amount = order.total_price
    
    # Оновлюємо баланс співробітника
    employee.cash_balance += amount
    
    # Позначаємо, що гроші за це замовлення ще не в касі
    order.is_cash_turned_in = False
    
    logger.info(f"Співробітник {employee.full_name} отримав {amount} грн за замовлення #{order.id}. Поточний борг: {employee.cash_balance}")

async def process_handover(session: AsyncSession, cashier_shift_id: int, employee_id: int, order_ids: list[int]):
    """
    Касир приймає гроші від співробітника за конкретні замовлення.
    """
    shift = await session.get(CashShift, cashier_shift_id)
    if not shift or shift.is_closed:
        raise ValueError("Зміна касира не знайдена або закрита.")

    employee = await session.get(Employee, employee_id)
    if not employee:
        raise ValueError("Співробітника не знайдено.")

    orders_res = await session.execute(
        select(Order).where(Order.id.in_(order_ids), Order.is_cash_turned_in == False)
    )
    orders = orders_res.scalars().all()

    if not orders:
        raise ValueError("Немає доступних замовлень для здачі виручки.")

    total_amount = Decimal('0.00')
    
    for order in orders:
        amount = order.total_price
        total_amount += amount
        
        # Гроші потрапили в касу
        order.is_cash_turned_in = True
        
        # Якщо замовлення не було прив'язане до зміни (наприклад, стара зміна закрилась), прив'язуємо до поточної
        # Це гарантує, що гроші потраплять у Z-звіт цієї зміни
        if not order.cash_shift_id:
            order.cash_shift_id = shift.id

    # Зменшуємо борг співробітника
    employee.cash_balance -= total_amount
    if employee.cash_balance < Decimal('0.00'):
        employee.cash_balance = Decimal('0.00') # Захист від мінуса

    # Додаємо транзакцію в касу (просто як лог події, для балансу використовується is_cash_turned_in)
    tx = CashTransaction(
        shift_id=shift.id,
        amount=total_amount,
        transaction_type='handover',
        comment=f"Здача виручки: {employee.full_name} (Зам: {', '.join(map(str, order_ids))})"
    )
    session.add(tx)
    
    await session.commit()
    return total_amount

async def get_shift_statistics(session: AsyncSession, shift_id: int):
    """Рахує статистику зміни (X-звіт)."""
    shift = await session.get(CashShift, shift_id)
    if not shift:
        return None

    # 1. Продажі (Всі замовлення, прив'язані до зміни)
    sales_query = select(
        Order.payment_method,
        func.sum(Order.total_price)
    ).where(
        Order.cash_shift_id == shift_id
    ).group_by(Order.payment_method)

    sales_res = await session.execute(sales_query)
    sales_data = sales_res.all()

    total_sales_cash_orders = Decimal('0.00') # Всього продажів готівкою (в т.ч. ті, що у кур'єрів)
    total_card_sales = Decimal('0.00')

    for method, amount in sales_data:
        amount_decimal = amount if amount is not None else Decimal('0.00')
        if method == 'cash':
            total_sales_cash_orders += amount_decimal
        elif method == 'card':
            total_card_sales += amount_decimal

    # 2. Службові операції
    trans_query = select(
        CashTransaction.transaction_type,
        func.sum(CashTransaction.amount)
    ).where(
        CashTransaction.shift_id == shift_id
    ).group_by(CashTransaction.transaction_type)

    trans_res = await session.execute(trans_query)
    trans_data = trans_res.all()

    service_in = Decimal('0.00')
    service_out = Decimal('0.00')
    handover_in = Decimal('0.00')

    for t_type, amount in trans_data:
        amount_decimal = amount if amount is not None else Decimal('0.00')
        if t_type == 'in':
            service_in += amount_decimal
        elif t_type == 'out':
            service_out += amount_decimal
        elif t_type == 'handover':
            handover_in += amount_decimal

    # 3. Готівка в касі (Cash Drawer)
    # Формула: Start + (Замовлення CASH, де turned_in=True) + Service In - Service Out
    # Handover транзакції ігноруємо в формулі, бо вони дублюються з turned_in=True.
    
    query_collected_cash = select(func.sum(Order.total_price)).where(
        Order.cash_shift_id == shift_id,
        Order.payment_method == 'cash',
        Order.is_cash_turned_in == True
    )
    collected_cash_res = await session.execute(query_collected_cash)
    collected_cash_scalar = collected_cash_res.scalar()
    total_collected_cash_orders = collected_cash_scalar if collected_cash_scalar is not None else Decimal('0.00')

    start_cash_decimal = shift.start_cash if shift.start_cash is not None else Decimal('0.00')
    
    theoretical_cash = start_cash_decimal + total_collected_cash_orders + service_in - service_out

    return {
        "shift_id": shift.id,
        "start_time": shift.start_time,
        "start_cash": start_cash_decimal,
        "total_sales_cash": total_sales_cash_orders, # Загальна сума чеків готівкою
        "total_sales_card": total_card_sales,
        "total_sales": total_sales_cash_orders + total_card_sales,
        "service_in": service_in,
        "service_out": service_out,
        "handover_in": handover_in, # Інформаційно
        "theoretical_cash": theoretical_cash
    }

async def close_active_shift(session: AsyncSession, shift_id: int, end_cash_actual: Decimal):
    """Закриває зміну (Z-звіт)."""
    shift = await session.get(CashShift, shift_id)
    if not shift or shift.is_closed:
        raise ValueError("Зміна не знайдена або вже закрита.")

    stats = await get_shift_statistics(session, shift_id)
    
    shift.end_time = datetime.now()
    shift.end_cash_actual = end_cash_actual
    
    shift.total_sales_cash = stats['total_sales_cash']
    shift.total_sales_card = stats['total_sales_card']
    shift.service_in = stats['service_in']
    shift.service_out = stats['service_out']
    shift.is_closed = True
    
    await session.commit()
    return shift

async def add_shift_transaction(session: AsyncSession, shift_id: int, amount: Decimal, t_type: str, comment: str):
    """Додає транзакцію."""
    tx = CashTransaction(
        shift_id=shift_id,
        amount=amount,
        transaction_type=t_type,
        comment=comment
    )
    session.add(tx)
    await session.commit()