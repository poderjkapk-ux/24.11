# admin_cash.py

import html
from datetime import datetime
from decimal import Decimal  # <--- ЗМІНЕНО: Додано імпорт
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_
from sqlalchemy.orm import joinedload

from models import Employee, CashShift, Settings, Order
from templates import ADMIN_HTML_TEMPLATE
from dependencies import get_db_session, check_credentials
from cash_service import (
    open_new_shift, get_shift_statistics, close_active_shift, 
    add_shift_transaction, process_handover
)

router = APIRouter()

@router.get("/admin/cash", response_class=HTMLResponse)
async def cash_dashboard(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    settings = await session.get(Settings, 1) or Settings()
    
    # Шукаємо будь-яку відкриту зміну
    active_shift_res = await session.execute(
        select(CashShift).where(CashShift.is_closed == False).options(joinedload(CashShift.employee))
    )
    active_shift = active_shift_res.scalars().first()
    
    # Кнопка історії
    history_btn = """
    <div style="text-align: right; margin-bottom: 20px;">
        <a href="/admin/cash/history" class="button secondary">📜 Історія змін (Z-звіти)</a>
    </div>
    """
    
    debtors_html = ""
    
    if active_shift:
        # --- БЛОК БОРЖНИКІВ (Хто не здав касу) ---
        debtors_res = await session.execute(
            select(Employee).where(Employee.cash_balance > 0).order_by(desc(Employee.cash_balance))
        )
        debtors = debtors_res.scalars().all()
        
        if debtors:
            debtors_rows = ""
            for d in debtors:
                debtors_rows += f"""
                <tr>
                    <td>{html.escape(d.full_name)}</td>
                    <td>{d.role.name}</td>
                    <td style="color: #d32f2f; font-weight: bold;">{d.cash_balance:.2f} грн</td>
                    <td class="actions">
                        <a href="/admin/cash/handover/{d.id}" class="button-sm">💸 Прийняти гроші</a>
                    </td>
                </tr>
                """
            
            debtors_html = f"""
            <div class="card" style="border-left: 5px solid #f57c00;">
                <h3>💸 Очікують здачі виручки</h3>
                <div class="table-wrapper">
                    <table>
                        <thead><tr><th>Співробітник</th><th>Роль</th><th>Сума на руках</th><th>Дії</th></tr></thead>
                        <tbody>{debtors_rows}</tbody>
                    </table>
                </div>
            </div>
            """
        else:
            debtors_html = """
            <div class="card" style="border-left: 5px solid #4caf50;">
                <h3>✅ Всі співробітники здали виручку</h3>
            </div>
            """
        # ------------------------------------------

        # Статистика зміни
        stats = await get_shift_statistics(session, active_shift.id)
        
        x_report_html = f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px;">
                <h3>💰 Готівка в касі (Теорія)</h3>
                <div style="font-size: 2em; font-weight: bold; color: #0d47a1;">{stats['theoretical_cash']:.2f} грн</div>
                <small>Початок ({stats['start_cash']:.2f}) + Виручка ({stats['total_sales_cash']:.2f}) + Внесення ({stats['service_in']:.2f}) - Вилучення ({stats['service_out']:.2f})</small>
            </div>
            <div style="background: #f3e5f5; padding: 15px; border-radius: 8px;">
                <h3>💳 Термінал (Картка)</h3>
                <div style="font-size: 2em; font-weight: bold; color: #4a148c;">{stats['total_sales_card']:.2f} грн</div>
            </div>
        </div>
        
        <table style="width: 100%; margin-bottom: 20px;">
            <tr><td><b>Початок зміни:</b></td><td>{stats['start_time'].strftime('%d.%m.%Y %H:%M')}</td></tr>
            <tr><td><b>Касир:</b></td><td>{html.escape(active_shift.employee.full_name)}</td></tr>
            <tr><td><b>Загальні продажі:</b></td><td>{stats['total_sales']:.2f} грн</td></tr>
        </table>
        """
        
        actions_html = f"""
        <div class="card">
            <h3>Службові операції</h3>
            <form action="/admin/cash/transaction" method="post" class="inline-form">
                <input type="hidden" name="shift_id" value="{active_shift.id}">
                <select name="transaction_type" style="width: 150px;">
                    <option value="in">📥 Внесення</option>
                    <option value="out">📤 Вилучення</option>
                </select>
                <input type="number" step="0.01" name="amount" placeholder="Сума" required style="width: 120px;">
                <input type="text" name="comment" placeholder="Коментар (напр. Розмін)" required>
                <button type="submit">Виконати</button>
            </form>
        </div>

        <div class="card" style="border-color: #f44336;">
            <h3 style="color: #d32f2f;">🛑 Закриття зміни (Z-звіт)</h3>
            <p>Перерахуйте фактичну готівку в касі перед закриттям.</p>
            <form action="/admin/cash/close" method="post" onsubmit="return confirm('Ви впевнені, що хочете закрити зміну?');">
                <input type="hidden" name="shift_id" value="{active_shift.id}">
                <label>Фактичний залишок готівки:</label>
                <input type="number" step="0.01" name="end_cash_actual" required placeholder="Скільки грошей по факту?">
                <button type="submit" class="button danger">🖨️ Закрити зміну (Зберегти Z-звіт)</button>
            </form>
        </div>
        """
        
        body = f"""
        {history_btn}
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2>🟢 Зміна відкрита #{active_shift.id}</h2>
                <span style="color:gray;">{active_shift.start_time.strftime('%H:%M')}</span>
            </div>
            {x_report_html}
        </div>
        {debtors_html}
        {actions_html}
        """
    else:
        # Зміна закрита. Форма відкриття.
        employees = (await session.execute(select(Employee).where(Employee.is_on_shift == True))).scalars().all()
        emp_options = "".join([f'<option value="{e.id}">{html.escape(e.full_name)}</option>' for e in employees])
        
        body = f"""
        {history_btn}
        <div class="card">
            <h2>🔴 Каса закрита</h2>
            <p>Щоб почати роботу, відкрийте нову касову зміну.</p>
            <form action="/admin/cash/open" method="post" style="max_width: 400px;">
                <label>Касир (хто відкриває):</label>
                <select name="employee_id" required>
                    {emp_options or '<option value="" disabled>Немає працівників на зміні</option>'}
                </select>
                
                <label>Залишок в касі (грн):</label>
                <input type="number" step="0.01" name="start_cash" value="0.00" required>
                
                <button type="submit" class="button">🟢 Відкрити зміну</button>
            </form>
        </div>
        """

    active_classes = {key: "" for key in ["orders_active", "clients_active", "tables_active", "products_active", "categories_active", "menu_active", "employees_active", "statuses_active", "reports_active", "settings_active", "design_active"]}
    active_classes["reports_active"] = "active"

    return HTMLResponse(ADMIN_HTML_TEMPLATE.format(
        title="Каса", 
        body=body, 
        site_title=settings.site_title or "Назва", 
        main_active="",
        **active_classes
    ))

# --- СТОРІНКА ПРИЙОМУ ГРОШЕЙ (Handover) ---
@router.get("/admin/cash/handover/{employee_id}", response_class=HTMLResponse)
async def handover_form(
    employee_id: int,
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    settings = await session.get(Settings, 1) or Settings()
    employee = await session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Співробітника не знайдено")

    # Отримуємо відкриту зміну касира (для прив'язки)
    active_shift_res = await session.execute(select(CashShift).where(CashShift.is_closed == False))
    active_shift = active_shift_res.scalars().first()
    
    if not active_shift:
        return HTMLResponse("<h1>Спочатку відкрийте касову зміну!</h1><a href='/admin/cash'>Назад</a>")

    # Знаходимо замовлення, за які співробітник винен гроші
    orders_res = await session.execute(
        select(Order).where(
            Order.payment_method == 'cash',
            Order.is_cash_turned_in == False,
            or_(
                Order.courier_id == employee.id,
                Order.accepted_by_waiter_id == employee.id,
                Order.completed_by_courier_id == employee.id
            )
        ).order_by(Order.id.desc())
    )
    orders = orders_res.scalars().all()
    
    rows = ""
    total_sum = Decimal('0.00')
    for o in orders:
        total_sum += o.total_price
        rows += f"""
        <tr>
            <td><input type="checkbox" name="order_ids" value="{o.id}" checked onchange="recalcTotal()"></td>
            <td>#{o.id}</td>
            <td>{o.created_at.strftime('%d.%m %H:%M')}</td>
            <td>{html.escape(o.address or 'В закладі')}</td>
            <td class="amount">{o.total_price:.2f}</td>
        </tr>
        """
    
    js_script = """
    <script>
        function recalcTotal() {
            let total = 0;
            document.querySelectorAll('input[name="order_ids"]:checked').forEach(cb => {
                const row = cb.closest('tr');
                const amount = parseFloat(row.querySelector('.amount').innerText);
                total += amount;
            });
            document.getElementById('selected-total').innerText = total.toFixed(2);
        }
    </script>
    """

    body = f"""
    {js_script}
    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h2>💸 Прийом виручки від: {html.escape(employee.full_name)}</h2>
            <a href="/admin/cash" class="button secondary">⬅️ Назад</a>
        </div>
        
        <p>Поточний баланс співробітника: <b>{employee.cash_balance:.2f} грн</b></p>
        
        <form action="/admin/cash/process_handover" method="post">
            <input type="hidden" name="employee_id" value="{employee.id}">
            <input type="hidden" name="shift_id" value="{active_shift.id}">
            
            <div class="table-wrapper">
                <table>
                    <thead><tr><th><input type="checkbox" checked onclick="toggleAll(this)"></th><th>ID</th><th>Дата</th><th>Адреса</th><th>Сума (грн)</th></tr></thead>
                    <tbody>
                        {rows or "<tr><td colspan='5'>Немає неоплачених замовлень</td></tr>"}
                    </tbody>
                </table>
            </div>
            
            <div style="margin-top: 20px; text-align: right;">
                <h3>До отримання: <span id="selected-total">{total_sum:.2f}</span> грн</h3>
                <button type="submit" class="button">💰 Підтвердити отримання грошей</button>
            </div>
        </form>
    </div>
    <script>
        function toggleAll(source) {{
            checkboxes = document.getElementsByName('order_ids');
            for(var i=0, n=checkboxes.length;i<n;i++) {{
                checkboxes[i].checked = source.checked;
            }}
            recalcTotal();
        }}
    </script>
    """
    
    active_classes = {key: "" for key in ["orders_active", "clients_active", "tables_active", "products_active", "categories_active", "menu_active", "employees_active", "statuses_active", "reports_active", "settings_active", "design_active"]}
    active_classes["reports_active"] = "active"
    
    return HTMLResponse(ADMIN_HTML_TEMPLATE.format(
        title="Прийом виручки", 
        body=body, 
        site_title=settings.site_title or "Назва", 
        main_active="",
        **active_classes
    ))

@router.post("/admin/cash/process_handover")
async def process_handover_route(
    request: Request,
    employee_id: int = Form(...),
    shift_id: int = Form(...),
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    form_data = await request.form()
    order_ids = [int(x) for x in form_data.getlist("order_ids")]
    
    if not order_ids:
        raise HTTPException(status_code=400, detail="Не вибрано жодного замовлення")
    
    try:
        await process_handover(session, shift_id, employee_id, order_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return RedirectResponse("/admin/cash", status_code=303)

# --- ІСТОРІЯ ЗМІН ---
@router.get("/admin/cash/history", response_class=HTMLResponse)
async def cash_history(session: AsyncSession = Depends(get_db_session), username: str = Depends(check_credentials)):
    settings = await session.get(Settings, 1) or Settings()
    
    shifts_res = await session.execute(
        select(CashShift)
        .where(CashShift.is_closed == True)
        .options(joinedload(CashShift.employee))
        .order_by(desc(CashShift.end_time))
        .limit(20)
    )
    shifts = shifts_res.scalars().all()
    
    rows = ""
    for s in shifts:
        theoretical = s.start_cash + s.total_sales_cash + s.service_in - s.service_out
        diff = s.end_cash_actual - theoretical
        
        diff_color = "green" if abs(diff) < 1 else ("red" if diff < 0 else "blue")
        diff_str = f"{diff:+.2f}"
        
        rows += f"""
        <tr>
            <td>#{s.id}</td>
            <td>{s.start_time.strftime('%d.%m %H:%M')} <br> {s.end_time.strftime('%d.%m %H:%M')}</td>
            <td>{html.escape(s.employee.full_name)}</td>
            <td>{s.total_sales_cash + s.total_sales_card:.2f} грн</td>
            <td>{s.end_cash_actual:.2f} грн</td>
            <td style="color:{diff_color}; font-weight:bold;">{diff_str}</td>
            <td>
                <a href="/admin/cash/z_report/{s.id}" target="_blank" class="button-sm">🖨️ Чек</a>
            </td>
        </tr>
        """
        
    body = f"""
    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h2>📜 Історія касових змін (Останні 20)</h2>
            <a href="/admin/cash" class="button secondary">⬅️ Поточна зміна</a>
        </div>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Час (Відкр/Закр)</th>
                        <th>Касир</th>
                        <th>Виручка (Гот+Карт)</th>
                        <th>Готівка (факт)</th>
                        <th>Різниця</th>
                        <th>Дії</th>
                    </tr>
                </thead>
                <tbody>
                    {rows or "<tr><td colspan='7'>Історія порожня</td></tr>"}
                </tbody>
            </table>
        </div>
    </div>
    """
    
    active_classes = {key: "" for key in ["orders_active", "clients_active", "tables_active", "products_active", "categories_active", "menu_active", "employees_active", "statuses_active", "reports_active", "settings_active", "design_active"]}
    active_classes["reports_active"] = "active"
    
    return HTMLResponse(ADMIN_HTML_TEMPLATE.format(title="Історія змін", body=body, site_title=settings.site_title, main_active="", **active_classes))

# --- ДРУК Z-ЗВІТУ ---
@router.get("/admin/cash/z_report/{shift_id}", response_class=HTMLResponse)
async def print_z_report(shift_id: int, session: AsyncSession = Depends(get_db_session)):
    shift = await session.get(CashShift, shift_id, options=[joinedload(CashShift.employee)])
    if not shift: return HTMLResponse("Зміну не знайдено", status_code=404)
    
    settings = await session.get(Settings, 1) or Settings()
    
    theoretical = shift.start_cash + shift.total_sales_cash + shift.service_in - shift.service_out
    diff = shift.end_cash_actual - theoretical
    
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Z-звіт #{shift.id}</title>
        <style>
            body {{ font-family: 'Courier New', monospace; width: 300px; margin: 0 auto; padding: 10px; }}
            .header {{ text-align: center; margin-bottom: 10px; border-bottom: 1px dashed #000; padding-bottom: 5px; }}
            .row {{ display: flex; justify-content: space-between; margin-bottom: 3px; }}
            .total {{ font-weight: bold; border-top: 1px dashed #000; margin-top: 5px; padding-top: 5px; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 0.8em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h3>{settings.site_title}</h3>
            <div>Z-ЗВІТ (Зміна #{shift.id})</div>
            <div>{shift.end_time.strftime('%d.%m.%Y %H:%M:%S')}</div>
            <div>Касир: {shift.employee.full_name}</div>
        </div>
        
        <div class="row"><span>Початок зміни:</span><span>{shift.start_time.strftime('%H:%M')}</span></div>
        <div class="row"><span>Початковий залишок:</span><span>{shift.start_cash:.2f}</span></div>
        <br>
        <div class="row"><span>Продажі (Готівка):</span><span>+{shift.total_sales_cash:.2f}</span></div>
        <div class="row"><span>Продажі (Картка):</span><span>+{shift.total_sales_card:.2f}</span></div>
        <div class="row total"><span>ВСЬОГО ПРОДАЖІВ:</span><span>{(shift.total_sales_cash + shift.total_sales_card):.2f}</span></div>
        <br>
        <div class="row"><span>Службове внесення:</span><span>+{shift.service_in:.2f}</span></div>
        <div class="row"><span>Службове вилучення:</span><span>-{shift.service_out:.2f}</span></div>
        <br>
        <div class="row" style="font-weight:bold;"><span>Готівка в касі (факт):</span><span>{shift.end_cash_actual:.2f}</span></div>
        <div class="row"><span>Різниця:</span><span>{diff:+.2f}</span></div>
        
        <div class="footer">
            <p>Зміна закрита.</p>
            <p>--- ФІСКАЛЬНИЙ ЧЕК (ТЕСТ) ---</p>
        </div>
        
        <script>window.print();</script>
    </body>
    </html>
    """
    return HTMLResponse(html_report)


@router.post("/admin/cash/open")
async def web_open_shift(
    employee_id: int = Form(...),
    start_cash: Decimal = Form(...),  # <--- ЗМІНЕНО: Decimal
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    try:
        await open_new_shift(session, employee_id, start_cash)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return RedirectResponse("/admin/cash", status_code=303)

@router.post("/admin/cash/transaction")
async def web_cash_transaction(
    shift_id: int = Form(...),
    transaction_type: str = Form(...),
    amount: Decimal = Form(...), # <--- ЗМІНЕНО: Decimal
    comment: str = Form(...),
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    await add_shift_transaction(session, shift_id, amount, transaction_type, comment)
    return RedirectResponse("/admin/cash", status_code=303)

@router.post("/admin/cash/close")
async def web_close_shift(
    shift_id: int = Form(...),
    end_cash_actual: Decimal = Form(...), # <--- ЗМІНЕНО: Decimal
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    try:
        await close_active_shift(session, shift_id, end_cash_actual)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return RedirectResponse("/admin/cash/history", status_code=303)