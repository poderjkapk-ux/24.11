# staff_pwa.py

import html
import json
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Form, Request, Response, status, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import joinedload, selectinload

from models import Employee, Settings, Order, OrderStatus, Role, OrderItem, Table, Category, Product, OrderStatusHistory
from dependencies import get_db_session
from auth_utils import verify_password, create_access_token, get_current_staff, get_password_hash
from templates import STAFF_LOGIN_HTML, STAFF_DASHBOARD_HTML
from notification_manager import notify_all_parties_on_status_change, notify_new_order_to_staff, notify_station_completion
from cash_service import link_order_to_shift, register_employee_debt

router = APIRouter(prefix="/staff", tags=["staff_pwa"])

# --- ПЕРЕАДРЕСАЦІЯ ТА АВТОРИЗАЦІЯ ---

@router.get("/", include_in_schema=False)
async def staff_root_redirect():
    return RedirectResponse(url="/staff/dashboard")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Відображає сторінку входу."""
    token = request.cookies.get("staff_access_token")
    # Якщо є токен, пробуємо відправити на дашборд.
    # Якщо токен невалідний, дашборд поверне нас назад (див. логіку dashboard)
    if token:
        return RedirectResponse(url="/staff/dashboard")
    return STAFF_LOGIN_HTML

@router.post("/login")
async def login_action(
    response: Response,
    phone: str = Form(...), 
    password: str = Form(...), 
    session: AsyncSession = Depends(get_db_session)
):
    """Обробляє вхід."""
    clean_phone = ''.join(filter(str.isdigit, phone))
    result = await session.execute(select(Employee).where(Employee.phone_number.ilike(f"%{clean_phone}%")))
    employee = result.scalars().first()

    if not employee:
        return HTMLResponse("Користувача не знайдено", status_code=400)
    if not employee.password_hash:
        return HTMLResponse("Пароль ще не встановлено.", status_code=400)
    if not verify_password(password, employee.password_hash):
        return HTMLResponse("Невірний пароль", status_code=400)

    access_token = create_access_token(data={"sub": str(employee.id)})
    
    response = RedirectResponse(url="/staff/dashboard", status_code=303)
    # Встановлюємо HttpOnly cookie
    response.set_cookie(key="staff_access_token", value=access_token, httponly=True, max_age=60*60*12, samesite="lax")
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/staff/login", status_code=303)
    response.delete_cookie("staff_access_token")
    return response

# --- ГОЛОВНИЙ ІНТЕРФЕЙС (DASHBOARD) ---

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request, 
    # Ми прибираємо пряму залежність Depends(get_current_staff) тут, 
    # щоб обробити помилку авторизації вручну і зробити редірект
    session: AsyncSession = Depends(get_db_session)
):
    """Головна сторінка PWA."""
    try:
        # Спроба отримати співробітника
        employee = await get_current_staff(request, session)
    except HTTPException:
        # Якщо авторизація не пройшла (немає токена або він невірний) -> редірект на логін
        response = RedirectResponse(url="/staff/login", status_code=303)
        # Важливо: видаляємо куку, щоб не було нескінченного циклу
        response.delete_cookie("staff_access_token")
        return response

    settings = await session.get(Settings, 1) or Settings()
    if 'role' not in employee.__dict__:
        await session.refresh(employee, ['role'])

    # Перевірка статусу зміни для кнопки
    shift_status_btn = ""
    if employee.is_on_shift:
        shift_status_btn = '<button onclick="toggleShift()" class="shift-btn on">🟢 Ви на зміні</button>'
    else:
        shift_status_btn = '<button onclick="toggleShift()" class="shift-btn off">🔴 Почати зміну</button>'

    content = f"""
    <div class="dashboard-header">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h3>{html.escape(employee.full_name)}</h3>
            <div class="role-badge">{html.escape(employee.role.name)}</div>
        </div>
        <div style="margin-top: 10px;">{shift_status_btn}</div>
    </div>
    
    <div id="main-view">
        <div id="loading-indicator" style="text-align:center; margin-top: 20px; color:gray;">
            <i class="fa-solid fa-spinner fa-spin"></i> Завантаження...
        </div>
        <div id="content-area"></div>
    </div>
    
    <div id="staff-modal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <div id="modal-body"></div>
        </div>
    </div>
    """
    
    return STAFF_DASHBOARD_HTML.format(
        site_title=settings.site_title or "Staff App",
        employee_name=html.escape(employee.full_name),
        role_name=html.escape(employee.role.name),
        content=content
    )

@router.get("/manifest.json")
async def get_manifest(session: AsyncSession = Depends(get_db_session)):
    settings = await session.get(Settings, 1) or Settings()
    return JSONResponse({
        "name": f"{settings.site_title} Staff",
        "short_name": "StaffApp",
        "start_url": "/staff/dashboard",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": settings.primary_color or "#333333",
        "icons": [{"src": "/static/favicons/favicon-32x32.png", "sizes": "32x32", "type": "image/png"}]
    })

# --- API ДЛЯ ФУНКЦІОНАЛУ ---

@router.post("/api/shift/toggle")
async def toggle_shift_api(
    session: AsyncSession = Depends(get_db_session),
    employee: Employee = Depends(get_current_staff)
):
    employee.is_on_shift = not employee.is_on_shift
    await session.commit()
    state = "active" if employee.is_on_shift else "inactive"
    return JSONResponse({"status": "ok", "state": state, "message": f"Зміну {'розпочато' if employee.is_on_shift else 'завершено'}"})

@router.get("/api/data")
async def get_staff_data(
    view_mode: str = "orders",
    employee: Employee = Depends(get_current_staff),
    session: AsyncSession = Depends(get_db_session)
):
    """Універсальний ендпоінт для отримання даних."""
    if 'role' not in employee.__dict__: await session.refresh(employee, ['role'])
    
    response_data = {"html": ""}

    # 1. ОФІЦІАНТ: Режим Столики
    if view_mode == "tables" and employee.role.can_serve_tables:
        tables_res = await session.execute(
            select(Table).where(Table.assigned_waiters.any(Employee.id == employee.id)).order_by(Table.name)
        )
        tables = tables_res.scalars().all()
        
        if not tables:
            response_data["html"] = "<div class='empty-state'>За вами не закріплено жодного столика.</div>"
        else:
            html_content = "<div class='grid-container'>"
            for t in tables:
                active_orders_count = await session.scalar(
                    select(func.count(Order.id)).where(
                        Order.table_id == t.id,
                        Order.status_id.not_in(
                            select(OrderStatus.id).where(or_(OrderStatus.is_completed_status==True, OrderStatus.is_cancelled_status==True))
                        )
                    )
                )
                status_badge = f"<span class='badge alert'>{active_orders_count} зам.</span>" if active_orders_count > 0 else "<span class='badge success'>Вільний</span>"
                html_content += f"""<div class="card table-card" onclick="openTableDetails({t.id}, '{html.escape(t.name)}')"><div class="card-title">{html.escape(t.name)}</div><div>{status_badge}</div></div>"""
            html_content += "</div>"
            response_data["html"] = html_content
        return JSONResponse(response_data)

    # 2. ЗАМОВЛЕННЯ (Всі ролі)
    if view_mode == "orders":
        orders_data = await _get_orders_for_role(session, employee)
        if not orders_data:
            response_data["html"] = "<div class='empty-state'>Активних замовлень немає.</div>"
        else:
            response_data["html"] = "".join([o["html"] for o in orders_data])
        return JSONResponse(response_data)

    return JSONResponse(response_data)

async def _get_orders_for_role(session: AsyncSession, employee: Employee):
    orders_data = []
    
    # КУХНЯ
    if employee.role.can_receive_kitchen_orders:
        status_ids = (await session.execute(select(OrderStatus.id).where(OrderStatus.visible_to_chef == True))).scalars().all()
        q = select(Order).options(joinedload(Order.table), selectinload(Order.items))\
            .where(Order.status_id.in_(status_ids), Order.kitchen_done == False).order_by(Order.id.asc())
        orders = (await session.execute(q)).scalars().all()
        for o in orders:
            items_html = "".join([f"<li>{html.escape(i.product_name)} x{i.quantity}</li>" for i in o.items if i.preparation_area != 'bar'])
            if items_html:
                orders_data.append({"id": o.id, "html": _build_card(o, f"<ul>{items_html}</ul>", "✅ Готово", "chef_ready", "kitchen")})

    # БАР
    elif employee.role.can_receive_bar_orders:
        status_ids = (await session.execute(select(OrderStatus.id).where(OrderStatus.visible_to_bartender == True))).scalars().all()
        q = select(Order).options(joinedload(Order.table), selectinload(Order.items))\
            .where(Order.status_id.in_(status_ids), Order.bar_done == False).order_by(Order.id.asc())
        orders = (await session.execute(q)).scalars().all()
        for o in orders:
            items_html = "".join([f"<li>{html.escape(i.product_name)} x{i.quantity}</li>" for i in o.items if i.preparation_area == 'bar'])
            if items_html:
                orders_data.append({"id": o.id, "html": _build_card(o, f"<ul>{items_html}</ul>", "✅ Готово", "chef_ready", "bar")})

    # КУР'ЄР
    elif employee.role.can_be_assigned:
        completed_ids = (await session.execute(select(OrderStatus.id).where(or_(OrderStatus.is_completed_status==True, OrderStatus.is_cancelled_status==True)))).scalars().all()
        q = select(Order).options(joinedload(Order.status), selectinload(Order.items))\
            .where(Order.courier_id == employee.id, Order.status_id.not_in(completed_ids)).order_by(Order.id.desc())
        orders = (await session.execute(q)).scalars().all()
        for o in orders:
            info = f"📍 {html.escape(o.address or '')}<br>📞 {html.escape(o.phone_number or '')}<br>💰 {o.total_price} грн"
            orders_data.append({"id": o.id, "html": _build_card(o, info, "Деталі", "open_details")})

    # ОФІЦІАНТ / ІНШІ
    else:
        completed_ids = (await session.execute(select(OrderStatus.id).where(or_(OrderStatus.is_completed_status==True, OrderStatus.is_cancelled_status==True)))).scalars().all()
        q = select(Order).options(joinedload(Order.status), joinedload(Order.table))\
            .where(Order.status_id.not_in(completed_ids)).order_by(Order.id.desc()).limit(30)
        orders = (await session.execute(q)).scalars().all()
        for o in orders:
            target = o.table.name if o.table else ('Доставка' if o.is_delivery else 'Самовивіз')
            info = f"<b>{html.escape(target)}</b><br><span class='badge'>{o.status.name}</span><br>💰 {o.total_price} грн"
            btn = "Прийняти" if not o.accepted_by_waiter_id and o.order_type=='in_house' and employee.role.can_serve_tables else "Деталі"
            act = "accept_order" if btn == "Прийняти" else "open_details"
            orders_data.append({"id": o.id, "html": _build_card(o, info, btn, act)})

    return orders_data

def _build_card(order, content, btn_text, action, extra=""):
    return f"""
    <div class="order-card" id="order-{order.id}">
        <div class="card-header"><span>#{order.id}</span><span class="time">{order.created_at.strftime('%H:%M')}</span></div>
        <div class="card-body">{content}</div>
        <div class="card-footer"><button class="action-btn" onclick="performAction('{action}', {order.id}, '{extra}')">{btn_text}</button></div>
    </div>
    """

@router.post("/api/action")
async def handle_action_api(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    employee: Employee = Depends(get_current_staff)
):
    data = await request.json()
    action = data.get("action")
    order_id = int(data.get("orderId"))
    extra = data.get("extra")

    order = await session.get(Order, order_id, options=[joinedload(Order.status)])
    if not order: return JSONResponse({"error": "Not found"}, status_code=404)

    if action == "chef_ready":
        if extra == 'kitchen': order.kitchen_done = True
        elif extra == 'bar': order.bar_done = True
        await notify_station_completion(request.app.state.admin_bot, order, extra, session)
        await session.commit()
        return JSONResponse({"success": True})

    elif action == "accept_order":
        if order.accepted_by_waiter_id: return JSONResponse({"error": "Вже зайнято"}, status_code=400)
        order.accepted_by_waiter_id = employee.id
        proc_status = await session.scalar(select(OrderStatus).where(OrderStatus.name == "В обробці").limit(1))
        if proc_status:
            order.status_id = proc_status.id
            session.add(OrderStatusHistory(order_id=order.id, status_id=proc_status.id, actor_info=employee.full_name))
        await session.commit()
        await notify_all_parties_on_status_change(order, "Новий", f"{employee.full_name} (App)", request.app.state.admin_bot, request.app.state.client_bot, session)
        return JSONResponse({"success": True})

    return JSONResponse({"success": False})

# --- ДЕТАЛІ ТА ЗМІНА СТАТУСУ ---

@router.get("/api/order/{order_id}/details")
async def get_order_details(
    order_id: int,
    session: AsyncSession = Depends(get_db_session),
    employee: Employee = Depends(get_current_staff)
):
    order = await session.get(Order, order_id, options=[selectinload(Order.items), joinedload(Order.status), joinedload(Order.table)])
    items_html = "".join([f"<div style='display:flex;justify-content:space-between;margin-bottom:5px;'><span>{html.escape(i.product_name)}</span><span>x{i.quantity}</span></div>" for i in order.items])
    
    statuses = []
    if employee.role.can_be_assigned:
        statuses = (await session.execute(select(OrderStatus).where(OrderStatus.visible_to_courier == True))).scalars().all()
    elif employee.role.can_serve_tables:
        statuses = (await session.execute(select(OrderStatus).where(OrderStatus.visible_to_waiter == True))).scalars().all()
    
    status_btns = "".join([f"<button class='action-btn secondary' style='margin:5px;' onclick='changeStatus({order.id}, {s.id})'>{html.escape(s.name)}</button>" for s in statuses])

    html_content = f"""
    <div style="padding:15px;">
        <h3 style="margin-top:0;">Замовлення #{order.id}</h3>
        <p>Статус: <b>{html.escape(order.status.name)}</b></p>
        <p>Клієнт: {html.escape(order.customer_name or 'Гість')}</p>
        <p>Тел: {html.escape(order.phone_number or '-')}</p>
        <p><b>Сума: {order.total_price} грн</b></p>
        <hr>
        <div style="margin: 15px 0;">{items_html}</div>
        <hr>
        <h4>Змінити статус:</h4>
        <div>{status_btns}</div>
    </div>
    """
    return JSONResponse({"html": html_content})

@router.post("/api/order/status")
async def change_order_status_api(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    employee: Employee = Depends(get_current_staff)
):
    data = await request.json()
    order_id = int(data.get("orderId"))
    status_id = int(data.get("statusId"))
    order = await session.get(Order, order_id, options=[joinedload(Order.status)])
    new_status = await session.get(OrderStatus, status_id)
    if not order or not new_status: return JSONResponse({"error": "Error"}, status_code=400)

    old_status_name = order.status.name
    if new_status.is_completed_status:
        await link_order_to_shift(session, order, employee.id)
        if order.payment_method == 'cash': await register_employee_debt(session, order, employee.id)
    
    order.status_id = status_id
    session.add(OrderStatusHistory(order_id=order.id, status_id=status_id, actor_info=f"{employee.role.name}: {employee.full_name}"))
    await session.commit()
    await notify_all_parties_on_status_change(order, old_status_name, f"{employee.role.name} (App)", request.app.state.admin_bot, request.app.state.client_bot, session)
    return JSONResponse({"success": True})

# --- ЗАМОВЛЕННЯ ОФІЦІАНТА ---
@router.get("/api/menu/full")
async def get_full_menu(session: AsyncSession = Depends(get_db_session)):
    cats = (await session.execute(select(Category).where(Category.show_in_restaurant==True).order_by(Category.sort_order))).scalars().all()
    menu = []
    for c in cats:
        prods = (await session.execute(select(Product).where(Product.category_id==c.id, Product.is_active==True))).scalars().all()
        menu.append({"id": c.id, "name": c.name, "products": [{"id": p.id, "name": p.name, "price": float(p.price)} for p in prods]})
    return JSONResponse(menu)

@router.post("/api/order/create")
async def create_waiter_order(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    employee: Employee = Depends(get_current_staff)
):
    data = await request.json()
    table_id = int(data.get("tableId"))
    cart = data.get("cart")
    table = await session.get(Table, table_id)
    if not table or not cart: return JSONResponse({"error": "Error"}, status_code=400)
    
    total = Decimal(0)
    items_obj = []
    for item in cart:
        prod = await session.get(Product, int(item['id']))
        if prod:
            qty = int(item['qty'])
            total += prod.price * qty
            items_obj.append(OrderItem(product_id=prod.id, product_name=prod.name, quantity=qty, price_at_moment=prod.price, preparation_area=prod.preparation_area))
            
    new_status = await session.scalar(select(OrderStatus).where(OrderStatus.name == "Новий").limit(1))
    order = Order(
        table_id=table_id, customer_name=f"Стіл: {table.name}", phone_number=f"table_{table_id}",
        total_price=total, order_type="in_house", is_delivery=False, delivery_time="In House",
        accepted_by_waiter_id=employee.id, status_id=new_status.id if new_status else 1, items=items_obj
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    await notify_new_order_to_staff(request.app.state.admin_bot, order, session)
    return JSONResponse({"success": True, "orderId": order.id})

# --- API ДЛЯ AJAX ЗАПИТІВ ---
@router.get("/api/orders", response_class=JSONResponse)
async def get_staff_orders_api_endpoint(
    employee: Employee = Depends(get_current_staff),
    session: AsyncSession = Depends(get_db_session)
):
    # Обгортка для сумісності з JS
    orders_data = await _get_orders_for_role(session, employee)
    return JSONResponse({"orders": orders_data})

@router.post("/set_password")
async def set_password_temp(
    employee_id: int = Form(...), 
    password: str = Form(...),
    session: AsyncSession = Depends(get_db_session)
):
    emp = await session.get(Employee, employee_id)
    if emp:
        emp.password_hash = get_password_hash(password)
        await session.commit()
        return JSONResponse({"message": "OK"})
    return JSONResponse({"error": "Not found"}, status_code=404)