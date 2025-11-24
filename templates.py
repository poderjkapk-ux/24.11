# templates.py

# Головний шаблон адмінки з меню
ADMIN_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Адмін-панель</title>
    
    <link rel="apple-touch-icon" sizes="180x180" href="/static/favicons/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/static/favicons/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/favicons/favicon-16x16.png">
    <link rel="manifest" href="/static/favicons/site.webmanifest">
    <link rel="shortcut icon" href="/static/favicons/favicon.ico">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --primary-color: #4a4a4a;
            --primary-hover-color: #333333;
            --text-color-light: #111827;
            --text-color-dark: #f9fafb;
            --bg-light: #f9fafb;
            --bg-dark: #111827;
            --sidebar-bg-light: #ffffff;
            --sidebar-bg-dark: #1f2937;
            --card-bg-light: #ffffff;
            --card-bg-dark: #1f2937;
            --border-light: #e5e7eb;
            --border-dark: #374151;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
            --font-sans: 'Inter', sans-serif;
            --status-green: #10b981;
            --status-yellow: #f59e0b;
            --status-red: #ef4444;
            --status-blue: #3b82f6;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: var(--font-sans);
            background-color: var(--bg-light);
            color: var(--text-color-light);
            display: flex;
            min-height: 100vh;
            transition: background-color 0.3s, color 0.3s;
        }}
        body.dark-mode {{
            --bg-light: var(--bg-dark);
            --text-color-light: var(--text-color-dark);
            --sidebar-bg-light: var(--sidebar-bg-dark);
            --card-bg-light: var(--card-bg-dark);
            --border-light: var(--border-dark);
        }}
        
        /* --- Sidebar Styles --- */
        .sidebar {{
            width: 260px;
            background-color: var(--sidebar-bg-light);
            border-right: 1px solid var(--border-light);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            position: fixed;
            height: 100%;
            transition: background-color 0.3s, border-color 0.3s, transform 0.3s ease-in-out;
            z-index: 1000;
        }}
        .sidebar-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            margin-bottom: 2.5rem;
        }}
        .sidebar-header .logo {{ display: flex; align-items: center; gap: 0.75rem; }}
        .sidebar-header .logo h2 {{ font-size: 1.5rem; font-weight: 700; color: var(--primary-color); }}
        .sidebar nav a {{
            display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem;
            color: #6b7280; text-decoration: none; font-weight: 500;
            border-radius: 0.5rem; transition: all 0.2s ease; margin-bottom: 0.5rem;
        }}
        body.dark-mode .sidebar nav a {{ color: #9ca3af; }}
        .sidebar nav a:hover {{ background-color: #f3f4f6; color: var(--primary-color); }}
        body.dark-mode .sidebar nav a:hover {{ background-color: #374151; }}
        .sidebar nav a.active {{ background-color: var(--primary-color); color: white; box-shadow: var(--shadow); }}
        .sidebar nav a i {{ width: 20px; text-align: center; }}
        .sidebar-footer {{ margin-top: auto; }}
        .sidebar-close {{
            display: none; background: none; border: none; font-size: 2rem;
            color: #6b7280; cursor: pointer;
        }}

        /* --- Main Content & Header --- */
        main {{
            flex-grow: 1;
            padding: 2rem;
            transition: margin-left 0.3s ease-in-out;
            margin-left: 260px;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }}
        .header-left {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        header h1 {{ font-size: 2rem; font-weight: 700; }}
        .menu-toggle {{
            display: none; background: none; border: 1px solid var(--border-light);
            width: 40px; height: 40px; border-radius: 0.5rem;
            align-items: center; justify-content: center;
            font-size: 1.25rem; color: #6b7280; cursor: pointer;
        }}
        .theme-toggle {{ cursor: pointer; font-size: 1.25rem; color: #6b7280; }}

        /* --- Overlay for Mobile Menu --- */
        .content-overlay {{
            display: none; position: fixed; top: 0; left: 0;
            width: 100%; height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 999;
        }}
        .content-overlay.active {{ display: block; }}

        /* --- Responsive Styles (Mobile) --- */
        @media (max-width: 992px) {{
            .sidebar {{
                transform: translateX(-100%);
                box-shadow: var(--shadow);
            }}
            .sidebar.open {{
                transform: translateX(0);
            }}
            .sidebar-close {{
                display: block;
            }}
            main {{
                margin-left: 0;
            }}
            .menu-toggle {{
                display: inline-flex;
            }}
            header h1 {{ font-size: 1.5rem; }}
        }}

        /* --- General Component Styles (Cards, Tables, etc.) --- */
        .card {{
            background-color: var(--card-bg-light); border-radius: 0.75rem;
            padding: 1.5rem; box-shadow: var(--shadow);
            border: 1px solid var(--border-light); margin-bottom: 2rem;
        }}
        .card h2 {{ font-size: 1.25rem; font-weight: 600; margin-bottom: 1.5rem; }}
        .card h3 {{
             font-size: 1.1rem; font-weight: 600; margin-top: 1.5rem;
             margin-bottom: 1rem; padding-bottom: 0.5rem;
             border-bottom: 1px solid var(--border-light);
        }}
        .button, button[type="submit"] {{
            padding: 0.6rem 1.2rem; background-color: var(--primary-color);
            color: white !important; border: none; border-radius: 0.5rem;
            cursor: pointer; font-size: 0.9rem; font-weight: 600;
            transition: background-color 0.2s ease; text-decoration: none;
            display: inline-flex; align-items: center; gap: 0.5rem;
        }}
        button:hover, .button:hover {{ background-color: var(--primary-hover-color); }}
        .button.secondary {{ background-color: #6b7280; }}
        .button.secondary:hover {{ background-color: #4b5563; }}
        .button.danger {{ background-color: #ef4444; }}
        .button.danger:hover {{ background-color: #dc2626; }}
        .button-sm {{
            display: inline-block; padding: 0.4rem 0.6rem; 
            border-radius: 0.3rem; text-decoration: none; color: white !important;
            background-color: #6b7280;
        }}
        .button-sm.danger {{ background-color: var(--status-red); }}
        .button-sm:hover {{ opacity: 0.8; }}
        .table-wrapper {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 1rem; text-align: left; border-bottom: 1px solid var(--border-light); vertical-align: middle; }}
        th {{ font-weight: 600; font-size: 0.85rem; text-transform: uppercase; color: #6b7280; }}
        body.dark-mode th {{ color: #9ca3af; }}
        td .table-img {{ width: 40px; height: 40px; border-radius: 0.5rem; object-fit: cover; vertical-align: middle; margin-right: 10px; }}
        .status {{
            padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 600;
            background-color: #e5e7eb; color: #374151;
        }}
        .actions {{ text-align: right; }}
        .actions a {{ color: #6b7280; margin-left: 0.75rem; font-size: 1.1rem; text-decoration: none; }}
        .actions a:hover {{ color: var(--primary-color); }}
        label {{ font-weight: 600; display: block; margin-bottom: 0.5rem; font-size: 0.9rem; }}
        input, textarea, select {{
            width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border-light);
            border-radius: 0.5rem; font-family: var(--font-sans); font-size: 1rem;
            background-color: var(--bg-light); color: var(--text-color-light);
            margin-bottom: 1rem;
        }}
        input:focus, textarea:focus, select:focus {{
            outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 2px #bfdbfe;
        }}
        input[type="color"] {{
            padding: 0.25rem; height: 40px;
        }}
        .checkbox-group {{ display: flex; align-items: center; gap: 10px; margin-bottom: 1rem;}}
        .checkbox-group input[type="checkbox"] {{ width: auto; margin-bottom: 0; }}
        .checkbox-group label {{ margin-bottom: 0; }}
        .search-form, .inline-form {{ display: flex; gap: 10px; margin-bottom: 1rem; align-items: center; }}
        .inline-form input {{ margin-bottom: 0; }}
        .pagination {{ margin-top: 1rem; display: flex; gap: 5px; }}
        .pagination a {{ padding: 5px 10px; border: 1px solid var(--border-light); text-decoration: none; color: var(--text-color-light); border-radius: 5px; }}
        .pagination a.active {{ background-color: var(--primary-color); color: white; border-color: var(--primary-color);}}
        
        .nav-tabs {{ display: flex; gap: 10px; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border-light); padding-bottom: 5px; }}
        .nav-tabs a {{ padding: 8px 15px; border-radius: 5px 5px 0 0; text-decoration: none; color: #6b7280; transition: color 0.2s; }}
        .nav-tabs a:hover {{ color: var(--primary-color); }}
        .nav-tabs a.active {{ background-color: var(--primary-color); color: white !important; }}
        
        /* --- Modal Styles --- */
        .modal-overlay {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.6); z-index: 2000;
            display: none; justify-content: center; align-items: center;
        }}
        .modal-overlay.active {{ display: flex; }}
        .modal {{
            background: var(--card-bg-light); border-radius: 0.75rem; padding: 2rem;
            width: 90%; max-width: 700px; max-height: 80vh;
            display: flex; flex-direction: column;
        }}
        .modal-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }}
        .modal-header h4 {{ font-size: 1.25rem; }}
        .modal-header .close-button {{ background: none; border: none; font-size: 2rem; cursor: pointer; }}
        .modal-body {{ flex-grow: 1; overflow-y: auto; }}
    </style>
</head>
<body class="">
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <div class="logo">
                <i class="fa-solid fa-utensils"></i>
                <h2>{site_title}</h2>
            </div>
            <button class="sidebar-close" id="sidebar-close">&times;</button>
        </div>
        <nav>
            <a href="/admin" class="{main_active}"><i class="fa-solid fa-chart-line"></i> Головна</a>
            <a href="/admin/orders" class="{orders_active}"><i class="fa-solid fa-box-archive"></i> Замовлення</a>
            <a href="/admin/clients" class="{clients_active}"><i class="fa-solid fa-users-line"></i> Клієнти</a>
            <a href="/admin/tables" class="{tables_active}"><i class="fa-solid fa-chair"></i> Столики</a>
            
            <a href="/admin/cash" class="{reports_active}"><i class="fa-solid fa-cash-register"></i> 💰 Каса</a>
            
            <a href="/admin/products" class="{products_active}"><i class="fa-solid fa-burger"></i> Страви</a>
            
            <a href="/admin/categories" class="{categories_active}"><i class="fa-solid fa-folder-open"></i> Категорії</a>
            <a href="/admin/menu" class="{menu_active}"><i class="fa-solid fa-file-lines"></i> Сторінки меню</a>
            <a href="/admin/employees" class="{employees_active}"><i class="fa-solid fa-users"></i> Співробітники</a>
            <a href="/admin/statuses" class="{statuses_active}"><i class="fa-solid fa-clipboard-list"></i> Статуси</a>
            <a href="/admin/reports" class="{reports_active}"><i class="fa-solid fa-chart-pie"></i> Звіти</a>
            <a href="/admin/design_settings" class="{design_active}"><i class="fa-solid fa-palette"></i> Дизайн та SEO</a>
            <a href="/admin/settings" class="{settings_active}"><i class="fa-solid fa-gear"></i> Налаштування</a>
        </nav>
        <div class="sidebar-footer">
            <a href="#"><i class="fa-solid fa-right-from-bracket"></i> Вийти</a>
        </div>
    </div>

    <main>
        <header>
            <div class="header-left">
                <button class="menu-toggle" id="menu-toggle">
                    <i class="fa-solid fa-bars"></i>
                </button>
                <h1>{title}</h1>
            </div>
            <i id="theme-toggle" class="fa-solid fa-sun theme-toggle"></i>
        </header>
        {body}
    </main>

    <div class="content-overlay" id="content-overlay"></div>

    <script>
      // --- Theme Toggler ---
      const themeToggle = document.getElementById('theme-toggle');
      const body = document.body;

      if (localStorage.getItem('theme') === 'light') {{
        body.classList.remove('dark-mode');
        themeToggle.classList.add('fa-moon');
        themeToggle.classList.remove('fa-sun');
      }} else {{
        body.classList.add('dark-mode');
        themeToggle.classList.add('fa-sun');
        themeToggle.classList.remove('fa-moon');
      }}

      themeToggle.addEventListener('click', () => {{
        body.classList.toggle('dark-mode');
        themeToggle.classList.toggle('fa-sun');
        themeToggle.classList.toggle('fa-moon');
        if(body.classList.contains('dark-mode')){{
          localStorage.setItem('theme', 'dark');
        }} else {{
          localStorage.setItem('theme', 'light');
        }}
      }});

      // --- Mobile Sidebar Logic ---
      const sidebar = document.getElementById('sidebar');
      const menuToggle = document.getElementById('menu-toggle');
      const sidebarClose = document.getElementById('sidebar-close');
      const contentOverlay = document.getElementById('content-overlay');

      const openSidebar = () => {{
        sidebar.classList.add('open');
        contentOverlay.classList.add('active');
      }};

      const closeSidebar = () => {{
        sidebar.classList.remove('open');
        contentOverlay.classList.remove('active');
      }};

      menuToggle.addEventListener('click', openSidebar);
      sidebarClose.addEventListener('click', closeSidebar);
      contentOverlay.addEventListener('click', closeSidebar);

    </script>
</body>
</html>
"""

ADMIN_TABLES_BODY = """
<style>
    .qr-code-img {{
        width: 100px;
        height: 100px;
        border: 1px solid var(--border-light);
        padding: 5px;
        background: white;
    }}
    /* Стиль для селекта з множинним вибором */
    #waiter_ids_select {{
        height: 250px;
        width: 100%;
    }}
</style>
<div class="card">
    <h2><i class="fa-solid fa-plus"></i> Додати новий столик</h2>
    <form action="/admin/tables/add" method="post" class="search-form">
        <input type="text" id="name" name="name" placeholder="Назва або номер столика" required>
        <button type="submit">Додати столик</button>
    </form>
</div>
<div class="card">
    <h2><i class="fa-solid fa-chair"></i> Список столиків</h2>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Назва</th>
                    <th>QR-код</th>
                    <th>Закріплені офіціанти</th>
                    <th>Дії</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
</div>
<div class="modal-overlay" id="assign-waiter-modal">
    <div class="modal">
        <div class="modal-header">
            <h4 id="modal-title">Призначити офіціантів для столика</h4>
            <button type="button" class="close-button" onclick="closeModal()">&times;</button>
        </div>
        <div class="modal-body">
            <form id="assign-waiter-form" method="post">
                <label for="waiter_ids_select">Виберіть офіціантів (на зміні):</label>
                <p style="font-size: 0.8rem; margin-bottom: 10px;">(Утримуйте Ctrl/Cmd для вибору кількох)</p>
                <select id="waiter_ids_select" name="waiter_ids" multiple>
                    </select>
                <br><br>
                <button type="submit">Призначити</button>
            </form>
        </div>
    </div>
</div>
<script>
function openAssignWaiterModal(tableId, tableName, waiters, assignedWaiterIds) {{
    const modal = document.getElementById('assign-waiter-modal');
    const form = document.getElementById('assign-waiter-form');
    const select = document.getElementById('waiter_ids_select');
    const title = document.getElementById('modal-title');
    
    title.innerText = `Призначити офіціантів для столика "${{tableName}}"`;
    form.action = `/admin/tables/assign_waiter/${{tableId}}`;
    select.innerHTML = ''; // Очищуємо список
    
    waiters.forEach(waiter => {{
        const option = document.createElement('option');
        option.value = waiter.id;
        option.textContent = waiter.full_name;
        // Перевіряємо, чи цей офіціант вже призначений
        if (assignedWaiterIds.includes(waiter.id)) {{
            option.selected = true;
        }}
        select.appendChild(option);
    }});
    
    modal.classList.add('active');
}}

function closeModal() {{
    document.getElementById('assign-waiter-modal').classList.remove('active');
}}

// Закриття модального вікна по кліку поза ним
window.onclick = function(event) {{
    const modal = document.getElementById('assign-waiter-modal');
    if (event.target == modal) {{
        closeModal();
    }}
}}
</script>
"""

ADMIN_ORDER_FORM_BODY = """
<style>
    .form-grid {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }}
    @media (min-width: 768px) {{
        .form-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    .order-items-table .quantity-input {{
        width: 70px;
        text-align: center;
        padding: 0.5rem;
    }}
    .order-items-table .actions button {{
        background: none; border: none; color: var(--status-red);
        cursor: pointer; font-size: 1.2rem;
    }}
    .totals-summary {{
        text-align: right;
        font-size: 1.1rem;
        font-weight: 600;
    }}
    .totals-summary div {{ margin-bottom: 0.5rem; }}
    .totals-summary .total {{ font-size: 1.4rem; color: var(--primary-color); }}
    
    #product-list {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1rem;
    }}
    .product-list-item {{
        border: 1px solid var(--border-light);
        border-radius: 0.5rem;
        padding: 1rem;
        cursor: pointer;
        transition: border-color 0.2s, box-shadow 0.2s;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .product-list-item:hover {{
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px #bfdbfe;
    }}
    .product-list-item h5 {{ font-size: 1rem; font-weight: 600; margin-bottom: 0.25rem;}}
    .product-list-item p {{ font-size: 0.9rem; color: #6b7280; }}
    body.dark-mode .product-list-item p {{ color: #9ca3af; }}
</style>

<div class="card">
    <form id="order-form" method="POST">
        <h3>Інформація про клієнта</h3>
        <div class="form-grid">
            <div class="form-group">
                <label for="phone_number">Номер телефону</label>
                <input type="tel" id="phone_number" placeholder="+380 (XX) XXX-XX-XX" required>
            </div>
            <div class="form-group">
                <label for="customer_name">Ім'я клієнта</label>
                <input type="text" id="customer_name" required>
            </div>
        </div>
        <div class="form-group">
            <label>Тип замовлення</label>
            <select id="delivery_type">
                <option value="delivery">Доставка</option>
                <option value="pickup">Самовивіз</option>
            </select>
        </div>
        <div class="form-group" id="address-group">
            <label for="address">Адреса доставки</label>
            <textarea id="address" rows="2"></textarea>
        </div>

        <h3>Склад замовлення</h3>
        <div class="table-wrapper">
            <table class="order-items-table">
                <thead>
                    <tr>
                        <th>Страва</th>
                        <th>Ціна</th>
                        <th>Кількість</th>
                        <th>Сума</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody id="order-items-body">
                </tbody>
            </table>
        </div>
        <div style="margin-top: 1.5rem; display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 1rem;">
            <button type="button" class="button" id="add-product-btn">
                <i class="fa-solid fa-plus"></i> Додати страву
            </button>
            <div class="totals-summary">
                <div class="total">До сплати: <span id="grand-total">0.00</span> грн</div>
            </div>
        </div>

        <div style="border-top: 1px solid var(--border-light); margin-top: 2rem; padding-top: 1.5rem; display: flex; justify-content: flex-end; gap: 1rem;">
             <a href="/admin/orders" class="button secondary">Скасувати</a>
             <button type="submit" class="button">Зберегти замовлення</button>
        </div>
    </form>
</div>

<div class="modal-overlay" id="product-modal">
    <div class="modal">
        <div class="modal-header">
            <h4>Вибір страви</h4>
            <button type="button" class="close-button" id="close-modal-btn">&times;</button>
        </div>
        <div class="modal-body">
            <div class="form-group">
                <input type="text" id="product-search-input" placeholder="Пошук страви за назвою...">
            </div>
            <div id="product-list">
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', () => {
    // State
    let orderItems = {};
    let allProducts = [];

    // Element References
    const orderForm = document.getElementById('order-form');
    const orderItemsBody = document.getElementById('order-items-body');
    const grandTotalEl = document.getElementById('grand-total');
    const deliveryTypeSelect = document.getElementById('delivery_type');
    const addressGroup = document.getElementById('address-group');
    const addProductBtn = document.getElementById('add-product-btn');
    const productModal = document.getElementById('product-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const productListContainer = document.getElementById('product-list');
    const productSearchInput = document.getElementById('product-search-input');

    // API Function
    const fetchAllProducts = async () => {
        try {
            const response = await fetch('/api/admin/products');
            if (!response.ok) throw new Error('Failed to fetch products');
            return await response.json();
        } catch (error) {
            console.error("Fetch products error:", error);
            alert('Помилка мережі при завантаженні страв.');
            return [];
        }
    };

    // Core Logic
    const calculateTotals = () => {
        let currentTotal = 0;
        for (const id in orderItems) {
            currentTotal += orderItems[id].price * orderItems[id].quantity;
        }
        grandTotalEl.textContent = currentTotal.toFixed(2);
    };

    const renderOrderItems = () => {
        orderItemsBody.innerHTML = '';
        if (Object.keys(orderItems).length === 0) {
            orderItemsBody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Додайте страви до замовлення</td></tr>';
        } else {
            for (const id in orderItems) {
                const item = orderItems[id];
                const row = document.createElement('tr');
                row.dataset.id = id;
                row.innerHTML = `
                    <td>${item.name}</td>
                    <td>${item.price.toFixed(2)} грн</td>
                    <td><input type="number" class="quantity-input" value="${item.quantity}" min="1" data-id="${id}"></td>
                    <td>${(item.price * item.quantity).toFixed(2)} грн</td>
                    <td class="actions"><button type="button" class="remove-item-btn" data-id="${id}">&times;</button></td>
                `;
                orderItemsBody.appendChild(row);
            }
        }
        calculateTotals();
    };

    const addProductToOrder = (product) => {
        if (orderItems[product.id]) {
            orderItems[product.id].quantity++;
        } else {
            orderItems[product.id] = { name: product.name, price: product.price, quantity: 1 };
        }
        renderOrderItems();
    };

    // Modal Logic
    const renderProductsInModal = (products) => {
        productListContainer.innerHTML = '';
        products.forEach(p => {
            const itemEl = document.createElement('div');
            itemEl.className = 'product-list-item';
            itemEl.dataset.id = p.id;
            itemEl.innerHTML = `
                <div><h5>${p.name}</h5><p>${p.category}</p></div>
                <p><strong>${p.price.toFixed(2)} грн</strong></p>`;
            productListContainer.appendChild(itemEl);
        });
    };

    const openProductModal = async () => {
        productListContainer.innerHTML = '<p>Завантаження страв...</p>';
        productModal.classList.add('active');
        if (allProducts.length === 0) {
             allProducts = await fetchAllProducts();
        }
        renderProductsInModal(allProducts);
    };

    const closeProductModal = () => {
        productModal.classList.remove('active');
        productSearchInput.value = '';
    };

    window.initializeForm = (data) => {
        if (!data) {
            console.error("Initial order data is not provided!");
            orderForm.action = '/api/admin/order/new';
            orderForm.querySelector('button[type="submit"]').textContent = 'Створити замовлення';
            orderItems = {};
            renderOrderItems();
            return;
        }

        orderForm.action = data.action;
        orderForm.querySelector('button[type="submit"]').textContent = data.submit_text;

        if (data.form_values) {
            document.getElementById('phone_number').value = data.form_values.phone_number || '';
            document.getElementById('customer_name').value = data.form_values.customer_name || '';
            document.getElementById('delivery_type').value = data.form_values.is_delivery ? "delivery" : "pickup";
            document.getElementById('address').value = data.form_values.address || '';
            deliveryTypeSelect.dispatchEvent(new Event('change'));
        }

        orderItems = data.items || {};
        renderOrderItems();
    };

    // Event Listeners
    deliveryTypeSelect.addEventListener('change', (e) => {
        addressGroup.style.display = e.target.value === 'delivery' ? 'block' : 'none';
    });

    addProductBtn.addEventListener('click', openProductModal);
    closeModalBtn.addEventListener('click', closeProductModal);
    productModal.addEventListener('click', (e) => { if (e.target === productModal) closeProductModal(); });

    productSearchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const filteredProducts = allProducts.filter(p => p.name.toLowerCase().includes(searchTerm));
        renderProductsInModal(filteredProducts);
    });

    productListContainer.addEventListener('click', (e) => {
        const productEl = e.target.closest('.product-list-item');
        if (productEl) {
            const product = allProducts.find(p => p.id == productEl.dataset.id);
            if (product) addProductToOrder(product);
            closeProductModal();
        }
    });

    orderItemsBody.addEventListener('change', (e) => {
        if (e.target.classList.contains('quantity-input')) {
            const id = e.target.dataset.id;
            const newQuantity = parseInt(e.target.value, 10);
            if (newQuantity > 0) {
                if (orderItems[id]) orderItems[id].quantity = newQuantity;
            } else {
                 delete orderItems[id];
            }
            renderOrderItems();
        }
    });

    orderItemsBody.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-item-btn')) {
            delete orderItems[e.target.dataset.id];
            renderOrderItems();
        }
    });

    orderForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const saveButton = orderForm.querySelector('button[type="submit"]');
        const originalButtonText = saveButton.textContent;
        saveButton.textContent = 'Збереження...';
        saveButton.disabled = true;

        const payload = {
            customer_name: document.getElementById('customer_name').value,
            phone_number: document.getElementById('phone_number').value,
            delivery_type: document.getElementById('delivery_type').value,
            address: document.getElementById('address').value,
            items: orderItems
        };

        try {
            const response = await fetch(orderForm.action, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                window.location.href = result.redirect_url || '/admin/orders';
            } else {
                alert(`Помилка: ${result.detail || 'Невідома помилка'}`);
                saveButton.textContent = originalButtonText;
                saveButton.disabled = false;
            }
        } catch (error) {
            console.error("Submit error:", error);
            alert('Помилка мережі. Не вдалося зберегти замовлення.');
            saveButton.textContent = originalButtonText;
            saveButton.disabled = false;
        }
    });

    if (typeof window.initializeForm === 'function' && !window.initializeForm.invoked) {
        const newOrderData = {
             items: {},
             action: '/api/admin/order/new',
             submit_text: 'Створити замовлення',
             form_values: null
        };
        window.initializeForm(newOrderData);
        window.initializeForm.invoked = true;
    }
});
</script>
"""

ADMIN_EMPLOYEE_BODY = """
<div class="card">
    <ul class="nav-tabs">
        <li class="nav-item"><a href="/admin/employees" class="active">Співробітники</a></li>
        <li class="nav-item"><a href="/admin/roles">Ролі</a></li>
    </ul>
    <h2>👤 Додати співробітника</h2>
    <form action="/admin/add_employee" method="post">
        <label for="full_name">Повне ім'я:</label><input type="text" id="full_name" name="full_name" required>
        <label for="phone_number">Номер телефону (для авторизації):</label><input type="text" id="phone_number" name="phone_number" placeholder="+380XX XXX XX XX" required>
        <label for="role_id">Роль:</label><select id="role_id" name="role_id" required>{role_options}</select>
        <button type="submit">Додати співробітника</button>
    </form>
</div>
<div class="card">
    <h2>👥 Список співробітників</h2>
    <p>🟢 - На зміні (авторизований)</p>
    <table><thead><tr><th>ID</th><th>Ім'я</th><th>Телефон</th><th>Роль</th><th>Статус</th><th>Telegram ID</th><th>Дії</th></tr></thead><tbody>
    {rows}
    </tbody></table>
</div>
"""
ADMIN_ROLES_BODY = """
<div class="card">
    <ul class="nav-tabs">
        <li class="nav-item"><a href="/admin/employees">Співробітники</a></li>
        <li class="nav-item"><a href="/admin/roles" class="active">Ролі</a></li>
    </ul>
    <h2>Додати нову роль</h2>
    <form action="/admin/add_role" method="post">
        <label for="name">Назва ролі:</label><input type="text" id="name" name="name" required>
        <div class="checkbox-group">
            <input type="checkbox" id="can_manage_orders" name="can_manage_orders" value="true">
            <label for="can_manage_orders">Може керувати замовленнями (Оператор)</label>
        </div>
        <div class="checkbox-group">
            <input type="checkbox" id="can_be_assigned" name="can_be_assigned" value="true">
            <label for="can_be_assigned">Може бути призначений на замовлення (Кур'єр)</label>
        </div>
        <div class="checkbox-group">
            <input type="checkbox" id="can_serve_tables" name="can_serve_tables" value="true">
            <label for="can_serve_tables">Може обслуговувати столики (Офіціант)</label>
        </div>
        <div class="checkbox-group">
            <input type="checkbox" id="can_receive_kitchen_orders" name="can_receive_kitchen_orders" value="true">
            <label for="can_receive_kitchen_orders">Отримує замовлення для приготування (Повар)</label>
        </div>
        <div class="checkbox-group">
            <input type="checkbox" id="can_receive_bar_orders" name="can_receive_bar_orders" value="true">
            <label for="can_receive_bar_orders">Отримує замовлення для бару (Бармен)</label> 
        </div>
        <button type="submit">Додати роль</button>
    </form>
</div>
<div class="card">
    <h2>Список ролей</h2>
    <table><thead><tr><th>ID</th><th>Назва</th><th>Керув. замовл.</th><th>Признач. доставку</th><th>Обслуг. столики</th><th>Кухня</th><th>Бар</th><th>Дії</th></tr></thead><tbody>
    {rows}
    </tbody></table>
</div>
"""
ADMIN_REPORTS_BODY = """
<div class="card">
    <h2>📊 Выбор отчета</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <a href="/admin/reports/cash_flow" class="report-link-card" style="display:block; padding:20px; background: #e3f2fd; border-radius:8px; text-decoration:none; color:#333; border:1px solid #90caf9;">
            <i class="fa-solid fa-money-bill-trend-up" style="font-size: 2em; color: #1976d2; margin-bottom:10px;"></i>
            <h3 style="margin:0;">Движение средств</h3>
            <p style="color:#666; font-size:0.9em;">Выручка, расходы, наличные и безнал.</p>
        </a>
        
        <a href="/admin/reports/workers" class="report-link-card" style="display:block; padding:20px; background: #fff3e0; border-radius:8px; text-decoration:none; color:#333; border:1px solid #ffcc80;">
            <i class="fa-solid fa-users-gear" style="font-size: 2em; color: #f57c00; margin-bottom:10px;"></i>
            <h3 style="margin:0;">Эффективность персонала</h3>
            <p style="color:#666; font-size:0.9em;">KPI сотрудников, количество заказов, продажи.</p>
        </a>

        <a href="/admin/reports/analytics" class="report-link-card" style="display:block; padding:20px; background: #e8f5e9; border-radius:8px; text-decoration:none; color:#333; border:1px solid #a5d6a7;">
            <i class="fa-solid fa-chart-column" style="font-size: 2em; color: #388e3c; margin-bottom:10px;"></i>
            <h3 style="margin:0;">Аналитика продаж</h3>
            <p style="color:#666; font-size:0.9em;">Топ блюд, категории.</p>
        </a>
        
        <a href="/admin/reports/couriers" class="report-link-card" style="display:block; padding:20px; background: #f3e5f5; border-radius:8px; text-decoration:none; color:#333; border:1px solid #ce93d8;">
            <i class="fa-solid fa-truck-fast" style="font-size: 2em; color: #8e24aa; margin-bottom:10px;"></i>
            <h3 style="margin:0;">Отчет по курьерам</h3>
            <p style="color:#666; font-size:0.9em;">Старый отчет по доставкам.</p>
        </a>
    </div>
</div>
"""
ADMIN_SETTINGS_BODY = """
<div class="card">
    <form action="/admin/settings" method="post" enctype="multipart/form-data">
        <h2>⚙️ Основні налаштування</h2>
        
        <h3>Зовнішній вигляд</h3>
        <label>Логотип (завантажте новий, щоб замінити):</label>
        <input type="file" name="logo_file" accept="image/*">
        {current_logo_html}

        <h3 style="margin-top: 2rem;">Налаштування Favicon</h3>
        <p>Завантажте необхідні файли favicon. Після завантаження оновіть сторінку (Ctrl+F5), щоб побачити зміни.</p>
        <h4>Поточні іконки</h4>
        <div style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap; margin-bottom: 2rem; background: #f0f0f0; padding: 1rem; border-radius: 8px;">
            <div><img src="/static/favicons/favicon-16x16.png?v={cache_buster}" alt="16x16" style="border: 1px solid #ccc;"><br><small>16x16</small></div>
            <div><img src="/static/favicons/favicon-32x32.png?v={cache_buster}" alt="32x32" style="border: 1px solid #ccc;"><br><small>32x32</small></div>
            <div><img src="/static/favicons/apple-touch-icon.png?v={cache_buster}" alt="Apple Touch Icon" style="width: 60px; height: 60px; border: 1px solid #ccc;"><br><small>Apple Icon</small></div>
        </div>

        <h4>Завантажити нові іконки</h4>
        <div class="form-grid" style="grid-template-columns: 1fr;">
            <div class="form-group"><label for="apple_touch_icon">apple-touch-icon.png (180x180)</label><input type="file" id="apple_touch_icon" name="apple_touch_icon" accept="image/png"></div>
            <div class="form-group"><label for="favicon_32x32">favicon-32x32.png</label><input type="file" id="favicon_32x32" name="favicon_32x32" accept="image/png"></div>
            <div class="form-group"><label for="favicon_16x16">favicon-16x16.png</label><input type="file" id="favicon_16x16" name="favicon_16x16" accept="image/png"></div>
            <div class="form-group"><label for="favicon_ico">favicon.ico (всі розміри)</label><input type="file" id="favicon_ico" name="favicon_ico" accept="image/x-icon"></div>
            <div class="form-group"><label for="site_webmanifest">site.webmanifest</label><input type="file" id="site_webmanifest" name="site_webmanifest" accept="application/manifest+json"></div>
        </div>
        
        <div style="margin-top: 2rem;">
            <button type="submit">Зберегти всі налаштування</button>
        </div>
    </form>
</div>
"""


ADMIN_MENU_BODY = """
<div class="card">
    <h2>{form_title}</h2>
    <form action="{form_action}" method="post">
        <label for="title">Заголовок (текст на кнопці):</label>
        <input type="text" id="title" name="title" value="{item_title}" required>
        
        <label for="content">Зміст сторінки (можна використовувати HTML-теги):</label>
        <textarea id="content" name="content" rows="10" required>{item_content}</textarea>
        
        <label for="sort_order">Порядок сортування (менше = вище):</label>
        <input type="number" id="sort_order" name="sort_order" value="{item_sort_order}" required>
        
        <div class="checkbox-group">
            <input type="checkbox" id="show_on_website" name="show_on_website" value="true" {item_show_on_website_checked}>
            <label for="show_on_website">Показувати на сайті</label>
        </div>
        <div class="checkbox-group">
            <input type="checkbox" id="show_in_telegram" name="show_in_telegram" value="true" {item_show_in_telegram_checked}>
            <label for="show_in_telegram">Показувати в Telegram-боті</label>
        </div>
        
        <button type="submit">{button_text}</button>
        <a href="/admin/menu" class="button secondary">Скасувати</a>
    </form>
</div>
<div class="card">
    <h2>📜 Список сторінок</h2>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Заголовок</th>
                    <th>Сортування</th>
                    <th>На сайті</th>
                    <th>В Telegram</th>
                    <th>Дії</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
</div>
"""

ADMIN_ORDER_MANAGE_BODY = """
<style>
    .manage-grid {{
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 2rem;
    }}
    .order-details-card .detail-item {{
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--border-light);
    }}
    .order-details-card .detail-item:last-child {{
        border-bottom: none;
    }}
    .order-details-card .detail-item strong {{
        color: #6b7280;
    }}
    body.dark-mode .order-details-card .detail-item strong {{
        color: #9ca3af;
    }}
    .status-history {{
        list-style-type: none;
        padding-left: 1rem;
        border-left: 2px solid var(--border-light);
    }}
    .status-history li {{
        margin-bottom: 0.75rem;
        position: relative;
        font-size: 0.9rem;
    }}
    .status-history li::before {{
        content: '✓';
        position: absolute;
        left: -1.1rem;
        top: 2px;
        color: var(--primary-color);
        font-weight: 900;
    }}
    @media (max-width: 992px) {{
        .manage-grid {{
            grid-template-columns: 1fr;
        }}
    }}
</style>
<div class="manage-grid">
    <div class="left-column">
        <div class="card order-details-card">
            <h2>Деталі замовлення #{order_id}</h2>
            <div class="detail-item">
                <strong>Клієнт:</strong>
                <span>{customer_name}</span>
            </div>
            <div class="detail-item">
                <strong>Телефон:</strong>
                <span>{phone_number}</span>
            </div>
            <div class="detail-item">
                <strong>Адреса:</strong>
                <span>{address}</span>
            </div>
             <div class="detail-item">
                <strong>Сума:</strong>
                <span>{total_price} грн</span>
            </div>
            <div class="detail-item">
                <strong>Оплата:</strong>
                <span>{payment_method_text}</span>
            </div>
            <div class="detail-item" style="flex-direction: column; align-items: start;">
                <strong style="margin-bottom: 0.5rem;">Склад замовлення:</strong>
                <div>{products_html}</div>
            </div>
        </div>
        <div class="card">
            <h2>Історія статусів</h2>
            {history_html}
        </div>
    </div>
    <div class="right-column">
        <div class="card">
            <h2>Керування статусом</h2>
            <form action="/admin/order/manage/{order_id}/set_status" method="post">
                <label for="status_id">Новий статус:</label>
                <select name="status_id" id="status_id" required>
                    {status_options}
                </select>
                
                <label for="payment_method" style="margin-top:10px;">Метод оплати (для каси):</label>
                <select name="payment_method" id="payment_method">
                    <option value="cash" {sel_cash}>💵 Готівка</option>
                    <option value="card" {sel_card}>💳 Картка / Термінал</option>
                </select>

                <button type="submit" style="margin-top:15px;">Зберегти зміни</button>
            </form>
        </div>
        <div class="card">
            <h2>Призначення кур'єра</h2>
            <form action="/admin/order/manage/{order_id}/assign_courier" method="post">
                <label for="courier_id">Кур'єр (на зміні):</label>
                <select name="courier_id" id="courier_id" required>
                    {courier_options}
                </select>
                <button type="submit">Призначити кур'єра</button>
            </form>
        </div>
    </div>
</div>
"""


ADMIN_CLIENTS_LIST_BODY = """
<div class="card">
    <h2><i class="fa-solid fa-users-line"></i> Список клієнтів</h2>
    <form action="/admin/clients" method="get" class="search-form">
        <input type="text" name="search" placeholder="Пошук за іменем або телефоном..." value="{search_query}">
        <button type="submit">🔍 Знайти</button>
    </form>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>Ім'я</th>
                    <th>Телефон</th>
                    <th>Всього замовлень</th>
                    <th>Загальна сума</th>
                    <th>Дії</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    {pagination}
</div>
"""

ADMIN_CLIENT_DETAIL_BODY = """
<style>
    .client-info-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }}
    .info-block {{
        background-color: var(--bg-light);
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid var(--border-light);
    }}
    .info-block h4 {{
        font-size: 0.9rem;
        color: #6b7280;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }}
    .info-block p {{
        font-size: 1.1rem;
        font-weight: 600;
    }}
    .order-summary-row {{
        cursor: pointer;
    }}
    .order-summary-row:hover {{
        background-color: #f3f4f6;
    }}
    body.dark-mode .order-summary-row:hover {{
        background-color: #374151;
    }}
    .order-details-row {{
        display: none;
    }}
    .details-content {{
        padding: 1.5rem;
        background-color: var(--bg-light);
    }}
    .status-history {{
        list-style-type: none;
        padding-left: 1rem;
        border-left: 2px solid var(--border-light);
    }}
    .status-history li {{
        margin-bottom: 0.5rem;
        position: relative;
    }}
    .status-history li::before {{
        content: '✓';
        position: absolute;
        left: -1.1rem;
        top: 2px;
        color: var(--primary-color);
        font-weight: 900;
    }}
</style>
<div class="card">
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;">
        <i class="fa-solid fa-user-circle" style="font-size: 3rem;"></i>
        <div>
            <h2 style="margin-bottom: 0;">{client_name}</h2>
            <a href="tel:{phone_number}">{phone_number}</a>
        </div>
    </div>
    <div class="client-info-grid">
        <div class="info-block">
            <h4>Остання адреса</h4>
            <p>{address}</p>
        </div>
        <div class="info-block">
            <h4>Всього замовлень</h4>
            <p>{total_orders}</p>
        </div>
        <div class="info-block">
            <h4>Загальна сума</h4>
            <p>{total_spent} грн</p>
        </div>
    </div>
</div>
<div class="card">
    <h3>Історія замовлень</h3>
    <div class="table-wrapper">
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Дата</th>
                    <th>Статус</th>
                    <th>Сума</th>
                    <th>Доставив</th>
                    <th>Деталі</th>
                </tr>
            </thead>
            <tbody>
                {order_rows}
            </tbody>
        </table>
    </div>
</div>
<script>
    function toggleDetails(row) {{
        const detailsRow = row.nextElementSibling;
        const icon = row.querySelector('i');
        if (detailsRow.style.display === 'table-row') {{
            detailsRow.style.display = 'none';
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
        }} else {{
            detailsRow.style.display = 'table-row';
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
        }}
    }}
</script>
"""

IN_HOUSE_MENU_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_title} - {table_name}</title>
    <meta name="description" content="{seo_description}">
    <meta name="keywords" content="{seo_keywords}">
    <meta name="robots" content="noindex, nofollow">
    <link rel="apple-touch-icon" sizes="180x180" href="/static/favicons/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/static/favicons/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/favicons/favicon-16x16.png">
    <link rel="manifest" href="/static/favicons/site.webmanifest">
    <link rel="shortcut icon" href="/static/favicons/favicon.ico">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family={font_family_serif_encoded}:wght@400;700&family={font_family_sans_encoded}:wght@400;600&display=swap" rel="stylesheet">
    
    <style>
      :root {{
        --primary-color: {primary_color_val};
        --secondary-color: {secondary_color_val};
        --background-color: {background_color_val};
        --text-color: {text_color_val};
        --footer-bg-color: {footer_bg_color_val};
        --footer-text-color: {footer_text_color_val};
        
        /* Navigation settings */
        --nav-bg-color: {category_nav_bg_color};
        --nav-text-color: {category_nav_text_color};
        
        --header-bg-image: url('/{header_image_url}');
        
        --primary-hover-color: color-mix(in srgb, {primary_color_val}, black 10%);
        --primary-glow-color: {primary_color_val}26;
      }}
      
      body, .category-nav a, .add-to-cart-btn, .action-btn, #checkout-form, .radio-group label {{
        font-family: '{font_family_sans_val}', sans-serif;
      }}
      header h1, .category-title, .product-name, .product-price, .cart-header h2, .modal-content h2 {{
        font-family: '{font_family_serif_val}', serif;
      }}
    </style>
    <style>
        :root {{
            --bg-color: var(--background-color, #f4f4f4);
            --card-bg: #ffffff;
            --border-color: var(--secondary-color, #dddddd);
            --dark-text-for-accent: #ffffff;
            --side-padding: 20px;
        }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes popIn {{ from {{ opacity: 0; transform: scale(0.95); }} to {{ opacity: 1; transform: scale(1); }} }}
        @keyframes cartPop {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.2); }} 100% {{ transform: scale(1); }} }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        html {{ scroll-behavior: smooth; overflow-y: scroll; }}
        body {{
            margin: 0;
            background-color: var(--bg-color);
            color: var(--text-color); 
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}
        .container {{ width: 100%; margin: 0 auto; padding: 0; }}
        
        /* --- HEADER with Image --- */
        header {{ 
            text-align: center; 
            padding: 60px var(--side-padding) 40px;
            position: relative;
            background-image: var(--header-bg-image);
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            color: white; /* Always white on image */
        }}
        header::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.5); /* Overlay */
            z-index: 0;
        }}
        .header-logo-container, header h1, header h2, header p, .table-name-header {{
            position: relative;
            z-index: 1;
        }}
        
        .header-logo-container {{ display: inline-block; margin-bottom: 25px; }}
        .header-logo {{ height: 100px; width: auto; }}
        header h1 {{
            font-size: clamp(2.5em, 5vw, 3.5em);
            margin: 0; font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }}
        header p {{
            font-size: clamp(1em, 2vw, 1.2em);
            margin-top: 10px; letter-spacing: 4px; text-transform: uppercase;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }}
        .table-name-header {{
            font-size: clamp(1.2em, 2.5vw, 1.5em);
            margin-top: 20px;
            color: rgba(255,255,255,0.9); /* Light for visibility */
        }}

        /* --- CATEGORY NAV --- */
        .category-nav {{
            display: flex; position: sticky; top: -1px;
            background-color: var(--nav-bg-color); 
            backdrop-filter: blur(12px);
            z-index: 100; animation: fadeIn 0.5s ease-out; overflow-x: auto;
            white-space: nowrap; -webkit-overflow-scrolling: touch; scrollbar-width: none;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
            width: 100%; padding: 15px 0;
        }}
        .category-nav::-webkit-scrollbar {{ display: none; }}
        .category-nav a {{
            color: var(--nav-text-color); text-decoration: none; padding: 10px 25px;
            border: 1px solid transparent; border-radius: 20px;
            transition: all 0.3s ease; font-weight: 500; flex-shrink: 0; margin: 0 10px;
            background: rgba(255,255,255,0.1); /* Slight background for better visibility */
        }}
        .category-nav a:first-child {{ margin-left: var(--side-padding); }}
        .category-nav a:last-child {{ margin-right: var(--side-padding); }}
        
        .category-nav a:hover, .category-nav a.active {{
            background-color: var(--primary-color); color: var(--dark-text-for-accent);
            border-color: var(--primary-color); transform: scale(1.05); font-weight: 600;
            box-shadow: 0 0 15px var(--primary-glow-color);
        }}
        
        #menu {{ display: grid; grid-template-columns: 1fr; gap: 40px; padding: 0 var(--side-padding); margin-bottom: 40px; }}
        .category-section {{ margin-bottom: 30px; padding-top: 90px; margin-top: -90px; }}
        .category-title {{
            font-size: clamp(2.2em, 4vw, 2.8em);
            color: var(--primary-color); padding-bottom: 15px; margin-bottom: 40px;
            text-align: center; border-bottom: 1px solid var(--border-color); position: relative;
        }}
        .category-title::after {{
            content: ''; position: absolute; bottom: -1px; left: 50%;
            transform: translateX(-50%); width: 100px; height: 2px;
            background-color: var(--primary-color); box-shadow: 0 0 10px var(--primary-glow-color);
        }}
        .products-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 30px; }}
        .product-card {{
            background-color: var(--card-bg); border: 1px solid var(--border-color);
            border-radius: 8px; overflow: hidden; display: flex; flex-direction: column;
            transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
            animation: fadeIn 0.5s ease-out forwards; opacity: 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        .product-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.1), 0 0 20px var(--primary-glow-color);
            border-color: var(--primary-color);
        }}
        .product-image-wrapper {{ width: 100%; height: 220px; position: relative; overflow: hidden; }}
        .product-image {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s ease; }}
        .product-card:hover .product-image {{ transform: scale(1.1); }}
        .product-info {{ padding: 25px; flex-grow: 1; display: flex; flex-direction: column; }}
        .product-name {{ font-size: 1.7em; margin: 0 0 10px; color: #333; }}
        .product-desc {{ font-size: 0.9em; color: #777; margin: 0 0 20px; flex-grow: 1; line-height: 1.6; }}
        .product-footer {{ display: flex; justify-content: space-between; align-items: center; }}
        .product-price {{ font-size: 1.8em; color: var(--primary-color); }}
        .add-to-cart-btn {{
            background: var(--primary-color); color: var(--dark-text-for-accent);
            border: none; padding: 12px 22px; border-radius: 5px; cursor: pointer;
            font-weight: 600; font-size: 0.9em; transition: all 0.3s ease;
        }}
        .add-to-cart-btn.added {{ background-color: #28a745; color: white; }}
        .add-to-cart-btn:hover {{
            background-color: var(--primary-hover-color); transform: scale(1.05);
            box-shadow: 0 0 15px var(--primary-glow-color);
        }}
        
        #cart-sidebar, #history-sidebar {{
            position: fixed; top: 0; right: -100%; width: 100%; max-width: 420px; height: 100%;
            background-color: rgba(255, 255, 255, 0.95); backdrop-filter: blur(15px);
            border-left: 1px solid var(--border-color); box-shadow: -5px 0 25px rgba(0,0,0,0.1);
            transition: all 0.4s ease-in-out; display: flex; flex-direction: column; z-index: 1000;
            color: #333;
        }}
        #history-sidebar {{ left: -100%; right: auto; border-left: none; border-right: 1px solid var(--border-color); box-shadow: 5px 0 25px rgba(0,0,0,0.1); }}

        #cart-sidebar.open {{ right: 0; }}
        #history-sidebar.open {{ left: 0; }}

        .cart-header {{ padding: 20px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }}
        .cart-header h2 {{ margin: 0; color: var(--primary-color); }}
        #close-cart-btn, #close-history-btn {{ background: none; border: none; color: #333; font-size: 2.5em; cursor: pointer; line-height: 1; transition: transform 0.2s ease, color 0.2s ease;}}
        #close-cart-btn:hover, #close-history-btn:hover {{ color: var(--primary-color); transform: rotate(90deg); }}
        
        .cart-items {{ flex-grow: 1; overflow-y: auto; padding: 20px; }}
        .cart-item {{ animation: popIn 0.3s ease-out; display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid var(--border-color); }}
        .cart-item-info {{ flex-grow: 1; }} .cart-item-name {{ font-weight: 600; }}
        .cart-item-price {{ color: #555; font-size: 0.9em; }}
        .cart-item-controls {{ display: flex; align-items: center; }}
        .cart-item-controls button {{ background: var(--secondary-color, #eee); border: 1px solid var(--border-color); color: #333; width: 28px; height: 28px; cursor: pointer; border-radius: 50%; }}
        .cart-item-controls span {{ margin: 0 10px; }}
        .cart-footer {{ padding: 20px; border-top: 1px solid var(--border-color); background-color: rgba(255, 255, 255, 0.8); }}
        .cart-total {{ display: flex; justify-content: space-between; font-size: 1.2em; font-weight: 700; margin-bottom: 20px; }}
        
        .action-buttons {{ padding: 0 20px 20px; display: flex; flex-direction: column; gap: 10px; }}
        .action-btn, #place-order-btn {{
            width: 100%; padding: 15px; font-size: 1.1em; cursor: pointer; border-radius: 5px;
            font-weight: 700; border: 1px solid var(--primary-color); display: flex;
            align-items: center; justify-content: center; gap: 10px;
            transition: all 0.3s ease;
        }}
        .action-btn svg, #place-order-btn svg {{ width: 20px; height: 20px; }}
        #place-order-btn {{ background-color: var(--primary-color); color: var(--dark-text-for-accent); border-color: var(--primary-color); }}
        #place-order-btn:hover:not(:disabled) {{ background-color: var(--primary-hover-color); box-shadow: 0 0 15px var(--primary-glow-color); }}
        #place-order-btn:disabled {{ background-color: #aaa; color: #eee; cursor: not-allowed; border-color: #aaa; }}
        .call-waiter-btn, .request-bill-btn {{ background-color: transparent; color: var(--primary-color); }}
        .call-waiter-btn:hover, .request-bill-btn:hover {{ background-color: var(--secondary-color, #f4f4f4); }}

        /* Floating Buttons */
        #cart-toggle {{
            position: fixed; bottom: 20px; right: 20px; background-color: var(--primary-color);
            color: var(--dark-text-for-accent); border: none; border-radius: 50%;
            width: 60px; height: 60px; cursor: pointer; z-index: 1001;
            display: flex; justify-content: center; align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: all 0.3s ease;
        }}
        #history-toggle {{
            position: fixed; bottom: 20px; left: 20px; background-color: #fff;
            color: var(--primary-color); border: 1px solid var(--primary-color); border-radius: 50%;
            width: 60px; height: 60px; cursor: pointer; z-index: 1001;
            display: flex; justify-content: center; align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: all 0.3s ease;
        }}
        
        #cart-toggle.popping {{ animation: cartPop 0.4s ease; }}
        #cart-toggle svg, #history-toggle svg {{ width: 28px; height: 28px; }}
        #cart-toggle:hover {{ transform: scale(1.1); background-color: var(--primary-hover-color); }}
        #history-toggle:hover {{ transform: scale(1.1); background-color: #f9f9f9; }}
        
        #cart-count {{
            position: absolute; top: -5px; right: -5px; background: var(--primary-color);
            color: var(--dark-text-for-accent); border-radius: 50%; width: 25px; height: 25px;
            font-size: 0.8em; display: flex; justify-content: center; align-items: center;
            font-weight: 700; border: 2px solid var(--card-bg);
        }}
        
        /* Styles for History Items */
        .history-item {{
            padding: 15px; border: 1px solid var(--border-color); border-radius: 8px;
            margin-bottom: 15px; background-color: rgba(0,0,0,0.02);
        }}
        .history-header {{ display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 0.9em; color: #777; }}
        .history-products {{ font-weight: 500; margin-bottom: 10px; line-height: 1.4; }}
        .history-footer {{ display: flex; justify-content: space-between; font-weight: 700; color: var(--primary-color); }}
        .grand-total-section {{
            margin-top: 20px; padding-top: 15px; border-top: 2px dashed var(--border-color);
            font-size: 1.1em;
        }}
        .total-row {{ display: flex; justify-content: space-between; margin-bottom: 5px; }}
        .total-row.final {{ font-size: 1.3em; font-weight: 800; color: var(--primary-color); margin-top: 10px; }}

        .toast {{
            position: fixed; bottom: 90px; left: 50%; transform: translateX(-50%);
            background-color: #333; color: #fff; padding: 15px 25px; border-radius: 8px;
            z-index: 3000; opacity: 0; transition: opacity 0.5s, transform 0.5s;
            pointer-events: none; border: 1px solid var(--primary-color);
            box-shadow: 0 0 20px var(--primary-glow-color);
        }}
        .toast.show {{ opacity: 1; transform: translateX(-50%) translateY(-20px); }}
        .btn-spinner {{
            display: none; border: 2px solid rgba(255,255,255,0.3);
            border-top: 2px solid var(--dark-text-for-accent);
            border-radius: 50%; width: 18px; height: 18px;
            animation: spin 0.8s linear infinite;
        }}
        button.working .btn-spinner {{ display: inline-block; }}
        button.working span {{ vertical-align: middle; }}
        #loader {{ display: flex; justify-content: center; align-items: center; height: 80vh; }}
        .spinner {{ border: 5px solid var(--border-color); border-top: 5px solid var(--primary-color); border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; }}
        
        /* --- Payment Modal Styles (Updated) --- */
        .modal-overlay {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0,0,0,0.6); z-index: 3000;
            display: none; justify-content: center; align-items: center;
            opacity: 0; transition: opacity 0.3s ease;
            backdrop-filter: blur(5px);
        }}
        .modal-overlay.active {{ display: flex; opacity: 1; }}
        
        .modal {{
            background-color: var(--card-bg); 
            padding: 2rem; 
            border-radius: 15px; 
            width: 90%; max-width: 400px;
            border: 1px solid var(--border-color);
            box-shadow: 0 20px 50px rgba(0,0,0,0.15);
            transform: scale(0.95); transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            position: relative;
            text-align: center;
        }}
        .modal-overlay.active .modal {{ transform: scale(1); }}
        
        .modal-header {{ display: flex; justify-content: center; margin-bottom: 1.5rem; }}
        .modal-header h3 {{ 
            margin: 0; color: var(--primary-color); 
            font-size: 1.5rem; font-weight: 700; 
        }}
        
        .close-button {{ 
            position: absolute; right: 1.5rem; top: 1.5rem; 
            background: none; border: none; font-size: 2rem; 
            color: #999; cursor: pointer; line-height: 1; 
            padding: 0; transition: color 0.2s;
        }}
        .close-button:hover {{ color: var(--primary-color); }}
        
        .payment-options {{
            display: grid; gap: 15px; margin-top: 10px;
        }}
        
        .payment-option-btn {{
            width: 100%; padding: 18px; border: none; border-radius: 12px;
            font-size: 1.1rem; font-weight: 600; cursor: pointer;
            display: flex; align-items: center; justify-content: center; gap: 12px;
            transition: transform 0.2s, box-shadow 0.2s;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            background: var(--primary-color); /* Use primary color for both */
        }}
        
        .payment-option-btn:hover {{
            transform: translateY(-2px);
            background: var(--primary-hover-color);
            box-shadow: 0 8px 15px rgba(0,0,0,0.15);
        }}
        
        /* Add subtle difference or border if needed, but kept same style as requested */
        .btn-card {{ opacity: 0.9; }}
        
        .payment-option-btn:active {{
            transform: translateY(0);
        }}
        
        .payment-option-btn i {{ font-size: 1.3rem; }}
        
        
        /* --- NEW Footer Styles --- */
        footer {{
            background-color: var(--footer-bg-color);
            color: var(--footer-text-color);
            padding: 50px var(--side-padding) 30px;
            margin-top: auto;
            border-top: 1px solid var(--border-color);
        }}
        .footer-content {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .footer-section h4 {{
            font-size: 1.3em;
            margin-bottom: 20px;
            font-weight: 700;
            position: relative;
            padding-bottom: 10px;
            color: var(--footer-text-color);
        }}
        .footer-section h4::after {{
            content: '';
            position: absolute;
            left: 0;
            bottom: 0;
            width: 50px;
            height: 2px;
            background-color: var(--primary-color);
        }}
        .footer-contact-item {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 15px;
            font-size: 0.95em;
            line-height: 1.5;
        }}
        .footer-contact-item i {{
            margin-right: 12px;
            color: var(--primary-color);
            margin-top: 4px;
            font-size: 1.1em;
        }}
        .footer-contact-item a {{
            color: var(--footer-text-color);
            text-decoration: none;
            transition: color 0.2s;
        }}
        .footer-contact-item a:hover {{
            color: var(--primary-color);
        }}
        .footer-social {{
            display: flex;
            gap: 15px;
            margin-top: 10px;
        }}
        .footer-social a {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            background-color: rgba(255,255,255,0.1);
            border-radius: 50%;
            color: var(--footer-text-color);
            font-size: 1.2em;
            transition: all 0.3s ease;
            text-decoration: none;
        }}
        .footer-social a:hover {{
            background-color: var(--primary-color);
            color: var(--dark-text-for-accent);
            transform: translateY(-3px);
        }}
        
        .wifi-card {{
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .wifi-card strong {{ color: var(--primary-color); }}
        
        .footer-bottom {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
            font-size: 0.85em;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-logo-container">
            {logo_html}
        </div>
        <h1>{site_title}</h1> <h2 class="table-name-header">{table_name}</h2>
    </header>
    <div class="container">
        <nav id="category-nav" class="category-nav"></nav>
        <main id="menu">
            <div id="loader"><div class="spinner"></div></div>
        </main>
    </div>
    <div style="height: 100px;"></div>
    
    <button id="history-toggle" title="Історія та Рахунок">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
        </svg>
    </button>

    <button id="cart-toggle">
        <svg fill="currentColor" viewBox="0 0 20 20"><path d="M3 1a1 1 0 000 2h1.22l.305 1.222a.997.997 0 00.01.042l1.358 5.43-.893.892C3.74 11.846 4.632 14 6.414 14H15a1 1 0 000-2H6.414l1-1H14a1 1 0 00.894-.553l3-6A1 1 0 0017 3H6.28l-.31-1.243A1 1 0 005 1H3zM16 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM6.5 18a1.5 1.5 0 11-3 0 1.5 1.5 0 003 0z"></path></svg>
        <span id="cart-count">0</span>
    </button>

    <aside id="history-sidebar">
        <div class="cart-header">
            <h2>Ваш рахунок</h2>
            <button id="close-history-btn">&times;</button>
        </div>
        <div class="cart-items">
            <div id="history-list"></div>
            
            <div class="grand-total-section">
                <div class="total-row">
                    <span>Замовлені страви:</span>
                    <span><b id="history-total">{grand_total}</b> грн</span>
                </div>
                <div class="total-row" style="color: #777;">
                    <span>Поточний кошик:</span>
                    <span id="cart-pending-total">0 грн</span>
                </div>
                <div class="total-row final">
                    <span>Разом до сплати:</span>
                    <span id="grand-total-display">{grand_total} грн</span>
                </div>
            </div>
        </div>
        <div class="action-buttons">
             <button class="action-btn request-bill-btn">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3.375m-3.375 2.25h10.5m4.5 0a4.5 4.5 0 00-4.5-4.5h-2.25a4.5 4.5 0 00-4.5 4.5v2.25a4.5 4.5 0 004.5 4.5h2.25a4.5 4.5 0 004.5-4.5v-2.25z" /></svg>
                <div class="btn-spinner"></div>
                <span>Попросити рахунок</span>
            </button>
        </div>
    </aside>

    <aside id="cart-sidebar">
        <div class="cart-header">
            <h2>Ваше замовлення</h2>
            <button id="close-cart-btn">&times;</button>
        </div>
        <div id="cart-items-container" class="cart-items"></div>
        <div class="cart-footer">
            <div class="cart-total">
                <span>Всього:</span>
                <span id="cart-total-price">0 грн</span>
            </div>
            <button id="place-order-btn" disabled>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <div class="btn-spinner"></div>
                <span>Замовити</span>
            </button>
        </div>
        <div class="action-buttons">
            <button class="action-btn call-waiter-btn">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" /></svg>
                <div class="btn-spinner"></div>
                <span>Викликати офіціанта</span>
            </button>
        </div>
    </aside>
    <div id="toast" class="toast"></div>
    
    <div id="payment-method-modal" class="modal-overlay">
        <div class="modal">
            <button id="close-payment-modal" class="close-button">&times;</button>
            <div class="modal-header">
                <h3>💳 Спосіб оплати</h3>
            </div>
            <div class="modal-body">
                <p style="margin-bottom: 25px; color: #666; font-size: 1.05rem;">Як ви бажаєте розрахуватись?</p>
                <div class="payment-options">
                    <button class="payment-option-btn btn-cash confirm-payment-btn" data-method="cash">
                        <i class="fa-solid fa-money-bill-wave"></i> Готівка
                    </button>
                    <button class="payment-option-btn btn-card confirm-payment-btn" data-method="card">
                        <i class="fa-regular fa-credit-card"></i> Картка / Термінал
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h4>Контакти</h4>
                <div class="footer-contact-item">
                    <i class="fa-solid fa-location-dot"></i>
                    <span>{footer_address}</span>
                </div>
                <div class="footer-contact-item">
                    <i class="fa-solid fa-phone"></i>
                    <a href="tel:{footer_phone}">{footer_phone}</a>
                </div>
                 <div class="footer-contact-item">
                    <i class="fa-solid fa-clock"></i>
                    <span>{working_hours}</span>
                </div>
            </div>
            <div class="footer-section">
                <h4>Інтернет</h4>
                <div class="wifi-card">
                    <div><i class="fa-solid fa-wifi"></i> <strong>Wi-Fi:</strong> {wifi_ssid}</div>
                    <div style="margin-top: 5px;"><i class="fa-solid fa-lock"></i> <strong>Pass:</strong> {wifi_password}</div>
                </div>
            </div>
            <div class="footer-section">
                <h4>Ми в соцмережах</h4>
                <div class="footer-social">
                    {social_links_html}
                </div>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2024 {site_title}. Всі права захищені.</p>
        </div>
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const TABLE_ID = {table_id};
            let cart = {{}};
            const menuData = {menu_data};
            
            // --- NEW: Data from backend ---
            const historyData = {history_data};
            const initialGrandTotal = {grand_total};

            const menuContainer = document.getElementById('menu');
            const categoryNav = document.getElementById('category-nav');
            const cartSidebar = document.getElementById('cart-sidebar');
            const historySidebar = document.getElementById('history-sidebar');
            const cartToggle = document.getElementById('cart-toggle');
            const historyToggle = document.getElementById('history-toggle');
            const closeCartBtn = document.getElementById('close-cart-btn');
            const closeHistoryBtn = document.getElementById('close-history-btn');
            const cartItemsContainer = document.getElementById('cart-items-container');
            const cartTotalPriceEl = document.getElementById('cart-total-price');
            const cartCountEl = document.getElementById('cart-count');
            const placeOrderBtn = document.getElementById('place-order-btn');
            const toastEl = document.getElementById('toast');
            const loader = document.getElementById('loader');
            
            // --- Elements for Bill Summary ---
            const historyListEl = document.getElementById('history-list');
            const cartPendingTotalEl = document.getElementById('cart-pending-total');
            const grandTotalDisplayEl = document.getElementById('grand-total-display');
            const historyTotalEl = document.getElementById('history-total');
            
            // --- Elements for Payment Modal ---
            const payModal = document.getElementById('payment-method-modal');
            const closePayModalBtn = document.getElementById('close-payment-modal');
            const requestBillBtn = document.querySelector('.request-bill-btn');
            
            const showToast = (message) => {{
                toastEl.textContent = message;
                toastEl.classList.add('show');
                setTimeout(() => {{
                    toastEl.classList.remove('show');
                }}, 4000);
            }};
            
            // --- Render History ---
            const renderHistory = (orders) => {{
                historyListEl.innerHTML = '';
                if (!orders || orders.length === 0) {{
                    historyListEl.innerHTML = '<p style="text-align:center; color:#888;">Історія замовлень порожня.</p>';
                    return;
                }}
                
                orders.forEach(order => {{
                    const item = document.createElement('div');
                    item.className = 'history-item';
                    const productsHtml = order.products.replace(/, /g, '<br>');
                    
                    item.innerHTML = `
                        <div class="history-header">
                            <span>#${{order.id}} • ${{order.time}}</span>
                            <span style="color:var(--primary-color); font-weight:600;">${{order.status}}</span>
                        </div>
                        <div class="history-products">${{productsHtml}}</div>
                        <div class="history-footer">
                            <span>Сума:</span>
                            <span>${{order.total_price}} грн</span>
                        </div>
                    `;
                    historyListEl.appendChild(item);
                }});
            }};

            // --- Автооновлення (Polling) ---
            const fetchUpdates = async () => {{
                try {{
                    const response = await fetch(`/api/menu/table/${{TABLE_ID}}/updates`);
                    if (!response.ok) return;
                    
                    const data = await response.json();
                    renderHistory(data.history_data);
                    
                    // Оновлення сум
                    if(historyTotalEl) historyTotalEl.textContent = data.grand_total;
                    
                    // Перерахунок загальної суми з урахуванням кошика
                    let currentCartTotal = 0;
                    Object.values(cart).forEach(item => currentCartTotal += item.price * item.quantity);
                    
                    if(grandTotalDisplayEl) {{
                        const finalTotal = data.grand_total + currentCartTotal;
                        grandTotalDisplayEl.textContent = `${{finalTotal}} грн`;
                    }}

                }} catch (error) {{
                    console.error("Update error:", error);
                }}
            }};
            
            // Запускаємо оновлення кожні 5 секунд
            setInterval(fetchUpdates, 5000);

            const updateCartView = () => {{
                cartItemsContainer.innerHTML = '';
                let totalPrice = 0;
                let totalCount = 0;
                const items = Object.values(cart);
                if (items.length > 0) {{
                    items.forEach(item => {{
                        totalPrice += item.price * item.quantity;
                        totalCount += item.quantity;
                        const cartItem = document.createElement('div');
                        cartItem.className = 'cart-item';
                        cartItem.innerHTML = `
                            <div class="cart-item-info">
                                <div class="cart-item-name">${{item.name}}</div>
                                <div class="cart-item-price">${{item.quantity}} x ${{item.price}} грн</div>
                            </div>
                            <div class="cart-item-controls">
                                <button data-id="${{item.id}}" class="change-quantity">-</button>
                                <span>${{item.quantity}}</span>
                                <button data-id="${{item.id}}" class="change-quantity">+</button>
                            </div>`;
                        cartItemsContainer.appendChild(cartItem);
                    }});
                    placeOrderBtn.disabled = false;
                }} else {{
                    cartItemsContainer.innerHTML = '<p style="text-align:center; color:#888;">Ваш кошик порожній</p>';
                    placeOrderBtn.disabled = true;
                }}
                
                // Update Cart Totals
                cartTotalPriceEl.textContent = `${{totalPrice.toFixed(2)}} грн`;
                cartCountEl.textContent = totalCount;
                cartCountEl.style.display = totalCount > 0 ? 'flex' : 'none';
                
                // Update Bill Summary
                if(cartPendingTotalEl) cartPendingTotalEl.textContent = `${{totalPrice}} грн`;
                
                // Force update grand total immediately
                fetchUpdates();
            }};

            const renderMenu = (data) => {{
                menuContainer.innerHTML = '';
                categoryNav.innerHTML = '';
                loader.style.display = 'none';
                data.categories.forEach((category, index) => {{
                    const navLink = document.createElement('a');
                    navLink.href = `#category-${{category.id}}`;
                    navLink.textContent = category.name;
                    if (index === 0) navLink.classList.add('active');
                    categoryNav.appendChild(navLink);

                    const categorySection = document.createElement('section');
                    categorySection.className = 'category-section';
                    categorySection.id = `category-${{category.id}}`;
                    categorySection.innerHTML = `<h2 class="category-title">${{category.name}}</h2>`;
                    
                    const productsGrid = document.createElement('div');
                    productsGrid.className = 'products-grid';
                    const products = data.products.filter(p => p.category_id === category.id);
                    products.forEach((product, pIndex) => {{
                        const productCard = document.createElement('div');
                        productCard.className = 'product-card';
                        productCard.style.animationDelay = `${{pIndex * 0.05}}s`;
                        productCard.innerHTML = `
                            <div class="product-image-wrapper">
                                <img src="/${{product.image_url || 'static/images/placeholder.jpg'}}" alt="${{product.name}}" class="product-image">
                            </div>
                            <div class="product-info">
                                <h3 class="product-name">${{product.name}}</h3>
                                <p class="product-desc">${{product.description || ''}}</p>
                                <div class="product-footer">
                                    <span class="product-price">${{product.price}} грн</span>
                                    <button class="add-to-cart-btn" data-id="${{product.id}}" data-name="${{product.name}}" data-price="${{product.price}}">Додати</button>
                                </div>
                            </div>`;
                        productsGrid.appendChild(productCard);
                    }});
                    categorySection.appendChild(productsGrid);
                    menuContainer.appendChild(categorySection);
                }});
                setupScrollspy();
            }};

            const setupScrollspy = () => {{
                const navLinks = categoryNav.querySelectorAll('a');
                const sections = document.querySelectorAll('.category-section');
                const observer = new IntersectionObserver((entries) => {{
                    entries.forEach(entry => {{
                        if (entry.isIntersecting) {{
                            const id = entry.target.getAttribute('id');
                            const activeLink = document.querySelector(`.category-nav a[href="#${{id}}"]`);
                            navLinks.forEach(link => link.classList.remove('active'));
                            activeLink.classList.add('active');
                            activeLink.scrollIntoView({{ behavior: 'smooth', block: 'nearest', inline: 'center' }});
                        }}
                    }});
                }}, {{ root: null, rootMargin: '-40% 0px -60% 0px', threshold: 0 }});
                sections.forEach(section => observer.observe(section));
            }};
            
            menuContainer.addEventListener('click', e => {{
                if (e.target.classList.contains('add-to-cart-btn')) {{
                    const button = e.target;
                    const id = button.dataset.id;
                    if (cart[id]) {{
                        cart[id].quantity++;
                    }} else {{
                        cart[id] = {{ id: id, name: button.dataset.name, price: parseInt(button.dataset.price), quantity: 1 }};
                    }}
                    updateCartView();
                    cartToggle.classList.add('popping');
                    setTimeout(() => cartToggle.classList.remove('popping'), 400);
                    button.textContent = '✓ Додано';
                    button.classList.add('added');
                    setTimeout(() => {{
                        button.textContent = 'Додати';
                        button.classList.remove('added');
                    }}, 1500);
                }}
            }});

            cartItemsContainer.addEventListener('click', e => {{
                const target = e.target;
                const id = target.dataset.id;
                if (!id || !target.classList.contains('change-quantity')) return;
                
                if (target.textContent === '+') {{
                    cart[id].quantity++;
                }} else {{
                    cart[id].quantity--;
                    if (cart[id].quantity === 0) delete cart[id];
                }}
                updateCartView();
            }});
            
            cartToggle.addEventListener('click', () => {{
                cartSidebar.classList.add('open');
                historySidebar.classList.remove('open');
            }});
            
            historyToggle.addEventListener('click', () => {{
                historySidebar.classList.add('open');
                cartSidebar.classList.remove('open');
                fetchUpdates(); // Refresh immediately when opening
            }});
            
            closeCartBtn.addEventListener('click', () => cartSidebar.classList.remove('open'));
            closeHistoryBtn.addEventListener('click', () => historySidebar.classList.remove('open'));

            const handleApiButtonClick = async (button, apiUrl) => {{
                button.disabled = true;
                button.classList.add('working');
                try {{
                    const response = await fetch(apiUrl, {{ method: 'POST' }});
                    const result = await response.json();
                    showToast(result.message);
                }} catch (error) {{
                    showToast('Сталася помилка. Спробуйте ще раз.');
                }} finally {{
                    button.disabled = false;
                    button.classList.remove('working');
                }}
            }};

            document.querySelector('.call-waiter-btn').addEventListener('click', (e) => {{
                handleApiButtonClick(e.currentTarget, `/api/menu/table/${{TABLE_ID}}/call_waiter`);
            }});
            
            // --- Payment Modal Logic ---
            if(requestBillBtn) {{
                requestBillBtn.addEventListener('click', (e) => {{
                    payModal.classList.add('active');
                }});
            }}
            
            if(closePayModalBtn) {{
                closePayModalBtn.addEventListener('click', () => payModal.classList.remove('active'));
            }}
            
            window.addEventListener('click', (e) => {{
                if (e.target === payModal) payModal.classList.remove('active');
            }});
            
            document.querySelectorAll('.confirm-payment-btn').forEach(btn => {{
                btn.addEventListener('click', async (e) => {{
                    const method = e.currentTarget.dataset.method;
                    const originalBtnContent = e.currentTarget.innerHTML;
                    
                    e.currentTarget.disabled = true;
                    e.currentTarget.innerHTML = '<div class="btn-spinner" style="display:inline-block; border-color:white; border-top-color:transparent;"></div>';

                    try {{
                        const response = await fetch(`/api/menu/table/${{TABLE_ID}}/request_bill?method=${{method}}`, {{ method: 'POST' }});
                        const result = await response.json();
                        payModal.classList.remove('active');
                        showToast(result.message);
                    }} catch (error) {{
                        showToast('Сталася помилка.');
                    }} finally {{
                        e.currentTarget.disabled = false;
                        e.currentTarget.innerHTML = originalBtnContent;
                    }}
                }});
            }});

            placeOrderBtn.addEventListener('click', async (e) => {{
                const button = e.currentTarget;
                const items = Object.values(cart);
                if (items.length === 0) return;
                
                button.disabled = true;
                button.classList.add('working');

                try {{
                    const response = await fetch(`/api/menu/table/${{TABLE_ID}}/place_order`, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(items)
                    }});
                    const result = await response.json();
                    showToast(result.message);
                    if (response.ok) {{
                        cart = {{}};
                        updateCartView();
                        cartSidebar.classList.remove('open');
                        historySidebar.classList.add('open'); // Show history immediately
                        fetchUpdates();
                    }}
                }} catch (error) {{
                    showToast('Помилка при відправці замовлення.');
                }} finally {{
                    button.disabled = false;
                    button.classList.remove('working');
                }}
            }});
            
            renderMenu(menuData);
            renderHistory(historyData); // Initial render
            updateCartView();
        }});
    </script>
</body>
</html>
"""

WEB_ORDER_HTML = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_title}</title>
    <meta name="description" content="{seo_description}">
    <meta name="keywords" content="{seo_keywords}">
    <link rel="apple-touch-icon" sizes="180x180" href="/static/favicons/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/static/favicons/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/favicons/favicon-16x16.png">
    <link rel="manifest" href="/static/favicons/site.webmanifest">
    <link rel="shortcut icon" href="/static/favicons/favicon.ico">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family={font_family_serif_encoded}:wght@400;700&family={font_family_sans_encoded}:wght@400;600&display=swap" rel="stylesheet">
    
    <style>
      :root {{
        --primary-color: {primary_color_val};
        --secondary-color: {secondary_color_val};
        --background-color: {background_color_val};
        --text-color: {text_color_val}; /* NEW */
        --footer-bg-color: {footer_bg_color_val}; /* NEW */
        --footer-text-color: {footer_text_color_val}; /* NEW */
        
        /* Navigation settings */
        --nav-bg-color: {category_nav_bg_color};
        --nav-text-color: {category_nav_text_color};
        
        --header-bg-image: url('/{header_image_url}');
        
        --primary-hover-color: color-mix(in srgb, {primary_color_val}, black 10%);
        --primary-glow-color: {primary_color_val}26; 
      }}
      
      body, .category-nav a, .add-to-cart-btn, .action-btn, #checkout-form, .radio-group label {{
        font-family: '{font_family_sans_val}', sans-serif;
      }}
      header h1, .category-title, .product-name, .product-price, .cart-header h2, .modal-content h2, #page-modal-title {{
        font-family: '{font_family_serif_val}', serif;
      }}
    </style>
    <style>
        :root {{
            --bg-color: var(--background-color, #f4f4f4);
            --card-bg: #ffffff;
            --border-color: var(--secondary-color, #dddddd);
            --success-color: #28a745;
            --dark-text-for-accent: #ffffff;
            --side-padding: 20px;
        }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes popIn {{ from {{ opacity: 0; transform: scale(0.95); }} to {{ opacity: 1; transform: scale(1); }} }}
        @keyframes cartPop {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.2); }} 100% {{ transform: scale(1); }} }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}

        html {{
            scroll-behavior: smooth;
            overflow-y: scroll;
        }}
        body {{
            margin: 0;
            background-color: var(--bg-color);
            color: var(--text-color); /* Updated */
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}
        .container {{ 
            width: 100%; 
            margin: 0 auto; 
            padding: 0; 
        }}
        
        /* --- HEADER with Image --- */
        header {{ 
            text-align: center; 
            padding: 60px var(--side-padding) 40px;
            position: relative;
            background-image: var(--header-bg-image);
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            color: white; /* Always white on image */
        }}
        header::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.5); /* Overlay */
            z-index: 0;
        }}
        .header-logo-container, header h1, .main-nav {{
            position: relative;
            z-index: 1;
        }}
        
        .header-logo-container {{
            display: inline-block;
            margin-bottom: 25px;
        }}
        .header-logo {{
            height: 100px;
            width: auto;
            color: var(--text-color);
        }}
        header h1 {{
            font-size: clamp(3em, 6vw, 4em);
            margin: 0;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }}

        .main-nav {{
            text-align: center;
            padding: 10px var(--side-padding);
            margin-bottom: 20px;
            position: relative;
        }}
        .main-nav::after {{
            content: '';
            position: absolute;
            bottom: -5px;
            left: 50%;
            transform: translateX(-50%);
            width: calc(100% - (var(--side-padding) * 2));
            height: 1px;
            background: linear-gradient(to right, transparent, var(--border-color), transparent);
        }}
        .main-nav a {{
            color: var(--text-color);
            text-decoration: none;
            margin: 0 15px;
            font-size: 1.1em;
            font-weight: 500;
            transition: color 0.3s, text-shadow 0.3s;
            cursor: pointer;
        }}
        .main-nav a:hover {{
            color: var(--primary-color);
            text-shadow: 0 0 10px var(--primary-glow-color);
        }}

        .category-nav {{
            display: flex; 
            position: sticky; 
            top: -1px;
            background-color: var(--nav-bg-color);
            backdrop-filter: blur(12px);
            z-index: 100; 
            animation: fadeIn 0.5s ease-out; 
            overflow-x: auto; 
            white-space: nowrap;
            -webkit-overflow-scrolling: touch; 
            scrollbar-width: none;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
            border-top: 1px solid var(--border-color); 
            border-bottom: 1px solid var(--border-color); 
            width: 100%;
            padding: 15px 0;
        }}
        .category-nav::-webkit-scrollbar {{ display: none; }}
        .category-nav a {{
            color: var(--nav-text-color); text-decoration: none; padding: 10px 25px;
            border: 1px solid transparent; border-radius: 20px;
            transition: all 0.3s ease; font-weight: 500; flex-shrink: 0; margin: 0 10px;
            background: rgba(255,255,255,0.1); /* Slight background for visibility */
        }}
         .category-nav a:first-child {{ margin-left: var(--side-padding); }}
         .category-nav a:last-child {{ margin-right: var(--side-padding); }}
        .category-nav a:hover {{
            background-color: var(--primary-color); color: var(--dark-text-for-accent);
            border-color: var(--primary-color); transform: scale(1.05); font-weight: 600;
            box-shadow: 0 0 15px var(--primary-glow-color);
        }}
        .category-nav a.active {{
            background-color: var(--primary-color);
            color: var(--dark-text-for-accent);
            border-color: var(--primary-hover-color);
            font-weight: 600;
            transform: scale(1.05);
            box-shadow: 0 0 20px var(--primary-glow-color);
        }}

        #menu {{ 
            display: grid; 
            grid-template-columns: 1fr; 
            gap: 40px; 
            padding: 0 var(--side-padding); 
            margin-bottom: 40px;
        }}
        .category-section {{ margin-bottom: 30px; padding-top: 90px; margin-top: -90px; }}
        .category-title {{
            font-size: clamp(2.2em, 4vw, 2.8em); color: var(--primary-color);
            padding-bottom: 15px; margin-bottom: 40px; text-align: center;
            border-bottom: 1px solid var(--border-color);
            position: relative;
        }}
        .category-title::after {{
            content: '';
            position: absolute;
            bottom: -1px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 2px;
            background-color: var(--primary-color);
            box-shadow: 0 0 10px var(--primary-glow-color);
        }}
        .products-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 30px; }}
        .product-card {{
            background-color: var(--card-bg); border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden; display: flex; flex-direction: column;
            transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
            animation: fadeIn 0.5s ease-out forwards; opacity: 0; position: relative;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
        }}
        .product-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.1), 0 0 20px var(--primary-glow-color); 
            border-color: var(--primary-color);
        }}
        .product-image-wrapper {{ width: 100%; height: 220px; position: relative; overflow: hidden; }}
        .product-image-wrapper::after {{ content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 50%; background: linear-gradient(to top, rgba(0,0,0,0.5), transparent); }}
        .product-image {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.4s ease; }}
        .product-card:hover .product-image {{ transform: scale(1.1); }}
        .product-info {{ padding: 25px; flex-grow: 1; display: flex; flex-direction: column; }}
        .product-name {{ font-size: 1.7em; font-weight: 700; margin: 0 0 10px; color: #333; }}
        .product-desc {{ font-size: 0.9em; font-weight: 400; color: #777; margin: 0 0 20px; flex-grow: 1; line-height: 1.6; }} 
        .product-footer {{ display: flex; justify-content: space-between; align-items: center; }}
        .product-price {{ font-size: 1.8em; font-weight: 700; color: var(--primary-color); }}
        .add-to-cart-btn {{
            background: var(--primary-color);
            color: var(--dark-text-for-accent);
            border: none;
            padding: 12px 22px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9em;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        .add-to-cart-btn.added {{ background-color: var(--success-color); color: white; }}
        .add-to-cart-btn:hover {{
            background-color: var(--primary-hover-color);
            transform: scale(1.05);
            box-shadow: 0 0 15px var(--primary-glow-color);
        }}

        #cart-sidebar {{
            position: fixed; top: 0; right: -100%; width: 400px; height: 100%;
            background-color: rgba(255, 255, 255, 0.85); 
            backdrop-filter: blur(15px);
            border-left: 1px solid var(--border-color); box-shadow: -5px 0 25px rgba(0,0,0,0.1); 
            transition: right 0.4s ease-in-out; display: flex; flex-direction: column; z-index: 1000;
            color: #333; 
        }}
        #cart-sidebar.open {{ right: 0; }}
        .cart-header {{ padding: 20px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }}
        .cart-header h2 {{ margin: 0; color: var(--primary-color); }}
        #close-cart-btn {{ background: none; border: none; color: #333; font-size: 2.5em; cursor: pointer; line-height: 1; padding: 0; transition: transform 0.2s ease, color 0.2s ease; }} 
        #close-cart-btn:hover {{ color: var(--primary-color); transform: rotate(90deg); }}
        .cart-items {{ flex-grow: 1; overflow-y: auto; padding: 20px; }}
        .cart-empty-msg {{ color: #888; text-align: center; margin-top: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; }}
        .cart-empty-msg svg {{ width: 60px; height: 60px; margin-bottom: 20px; opacity: 0.3; }}
        .cart-empty-msg .go-to-menu-btn {{ margin-top: 20px; padding: 10px 20px; background: var(--primary-color); color: var(--dark-text-for-accent); text-decoration: none; border-radius: 5px; transition: background-color 0.3s; font-weight: 600; }}
        .cart-empty-msg .go-to-menu-btn:hover {{ background-color: var(--primary-hover-color); }}
        .cart-item {{ animation: popIn 0.3s ease-out; display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid var(--border-color); }}
        .cart-item-info {{ flex-grow: 1; margin-right: 10px; }}
        .cart-item-name {{ font-weight: 600; }}
        .cart-item-price {{ color: #555; font-size: 0.9em; }} 
        .cart-item-controls {{ display: flex; align-items: center; }}
        .cart-item-controls button {{ background: #eee; border: 1px solid var(--border-color); color: #333; width: 28px; height: 28px; cursor: pointer; border-radius: 50%; font-size: 1.1em; transition: background-color 0.2s ease, transform 0.2s ease; }} 
        .cart-item-controls button:hover {{ background-color: #ddd; transform: scale(1.1); }} 
        .cart-item-controls span {{ margin: 0 10px; font-weight: 500; }}
        .cart-item-remove-btn {{ background: none; border: none; color: #999; font-size: 1.5em; line-height: 1; cursor: pointer; margin-left: 10px; transition: color 0.2s ease, transform 0.2s ease; }}
        .cart-item-remove-btn:hover {{ color: #ff6b6b; transform: scale(1.2); }}
        .cart-footer {{ padding: 20px; border-top: 1px solid var(--border-color); background-color: rgba(255, 255, 255, 0.8); }} 
        .cart-total {{ display: flex; justify-content: space-between; font-size: 1.2em; font-weight: 700; margin-bottom: 20px; }}
        #checkout-btn {{ width: 100%; padding: 15px; background-color: var(--primary-color); color: var(--dark-text-for-accent); border: none; font-size: 1.1em; cursor: pointer; border-radius: 5px; font-weight: 700; transition: all 0.3s ease; }}
        #checkout-btn:hover:not(:disabled) {{ background-color: var(--primary-hover-color); box-shadow: 0 0 15px var(--primary-glow-color); }}
        #checkout-btn:disabled {{ background-color: #aaa; cursor: not-allowed; color: #eee; }} 
        #cart-toggle {{
            position: fixed; bottom: 20px; right: 20px; background-color: var(--primary-color); color: var(--dark-text-for-accent);
            border: none; border-radius: 50%; width: 60px; height: 60px; cursor: pointer; z-index: 1001;
            display: flex; justify-content: center; align-items: center; transition: transform 0.3s ease, background-color 0.3s ease, box-shadow 0.3s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.2); 
        }}
        #cart-toggle.popping {{ animation: cartPop 0.4s ease; }}
        #cart-toggle svg {{ width: 28px; height: 28px; }}
        #cart-toggle:hover {{ transform: scale(1.1); background-color: var(--primary-hover-color); box-shadow: 0 6px 20px rgba(0,0,0,0.3); }} 
        #cart-count {{ position: absolute; top: -5px; right: -5px; background: var(--primary-color); color: var(--dark-text-for-accent); border-radius: 50%; width: 25px; height: 25px; font-size: 0.8em; display: flex; justify-content: center; align-items: center; font-weight: 700; border: 2px solid var(--card-bg);}}
        #checkout-modal {{ display: none; position: fixed; z-index: 2000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); justify-content: center; align-items: center; opacity: 0; transition: opacity 0.3s ease; }}
        #checkout-modal.visible {{ opacity: 1; }}
        .modal-content {{ background-color: var(--card-bg); backdrop-filter: blur(15px); padding: 30px; border-radius: 8px; width: 90%; max-width: 500px; border: 1px solid var(--border-color); transform: scale(0.95); transition: transform 0.3s ease; }}
        #checkout-modal.visible .modal-content {{ transform: scale(1); }}
        .modal-content h2 {{ color: var(--primary-color); margin-top: 0; text-align: center; }}
        .modal-content .form-group {{ margin-bottom: 15px; }}
        .modal-content .form-group label {{ display: block; margin-bottom: 8px; font-weight: 500; font-size: 0.9em; color: #555; }} 
        .modal-content input[type="text"], .modal-content input[type="tel"] {{ width: 100%; padding: 12px; background: var(--secondary-color, #eee); border: 1px solid var(--border-color); color: #333; border-radius: 5px; box-sizing: border-box; transition: border-color 0.3s ease, box-shadow 0.3s ease; }} 
        .modal-content input[type="text"]:focus, .modal-content input[type="tel"]:focus {{ border-color: var(--primary-color); box-shadow: 0 0 10px var(--primary-glow-color); outline: none; }}
        .modal-content input:invalid {{ border-color: #e53935; }}
        .radio-group {{ display: flex; gap: 15px; }}
        .radio-group input[type="radio"] {{ display: none; }}
        .radio-group label {{ flex: 1; text-align: center; padding: 10px; border: 1px solid var(--border-color); border-radius: 5px; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; gap: 8px; }}
        .radio-group label svg {{ width: 18px; height: 18px; opacity: 0.7; transition: opacity 0.3s ease; }}
        .radio-group input[type="radio"]:checked + label {{ background-color: var(--primary-color); border-color: var(--primary-color); color: var(--dark-text-for-accent); font-weight: 700; box-shadow: 0 0 10px rgba(0,0,0,0.1); }} 
        .radio-group input[type="radio"]:checked + label svg {{ opacity: 1; }}
        #place-order-btn {{ width: 100%; padding: 15px; margin-top: 10px; background-color: var(--primary-color); color: var(--dark-text-for-accent); border:none; border-radius: 5px; font-weight: 700; font-size: 1.1em; cursor: pointer; transition: all 0.3s ease;}}
        #place-order-btn:hover {{ background-color: var(--primary-hover-color); box-shadow: 0 0 15px var(--primary-glow-color); }}
        .close-modal {{ float: right; font-size: 1.8em; cursor: pointer; color: #888; transition: color 0.2s ease, transform 0.2s ease; }}
        .close-modal:hover {{ color: #333; transform: rotate(90deg); }} 
        #scroll-to-top {{ display: none; opacity: 0; position: fixed; bottom: 90px; right: 20px; width: 50px; height: 50px; border-radius: 50%; background: var(--primary-color); color: var(--dark-text-for-accent); border: none; cursor: pointer; z-index: 999; font-size: 1.5em; transition: opacity 0.3s ease, transform 0.3s ease, background-color 0.3s ease; }}
        #scroll-to-top.visible {{ display: block; opacity: 1; }}
        #scroll-to-top:hover {{ transform: scale(1.1); background-color: var(--primary-hover-color); box-shadow: 0 0 15px var(--primary-glow-color); }}
        #loader {{ display: flex; justify-content: center; align-items: center; height: 80vh; }}
        .spinner {{ border: 5px solid var(--border-color); border-top: 5px solid var(--primary-color); border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; }}
        
        /* --- NEW Footer Styles --- */
        footer {{
            background-color: var(--footer-bg-color);
            color: var(--footer-text-color);
            padding: 50px var(--side-padding) 30px;
            margin-top: auto;
            border-top: 1px solid var(--border-color);
        }}
        .footer-content {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .footer-section h4 {{
            font-size: 1.3em;
            margin-bottom: 20px;
            font-weight: 700;
            position: relative;
            padding-bottom: 10px;
            color: var(--footer-text-color);
        }}
        .footer-section h4::after {{
            content: '';
            position: absolute;
            left: 0;
            bottom: 0;
            width: 50px;
            height: 2px;
            background-color: var(--primary-color);
        }}
        .footer-contact-item {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 15px;
            font-size: 0.95em;
            line-height: 1.5;
        }}
        .footer-contact-item i {{
            margin-right: 12px;
            color: var(--primary-color);
            margin-top: 4px;
            font-size: 1.1em;
        }}
        .footer-contact-item a {{
            color: var(--footer-text-color);
            text-decoration: none;
            transition: color 0.2s;
        }}
        .footer-contact-item a:hover {{
            color: var(--primary-color);
        }}
        .footer-social {{
            display: flex;
            gap: 15px;
            margin-top: 10px;
        }}
        .footer-social a {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            background-color: rgba(255,255,255,0.1);
            border-radius: 50%;
            color: var(--footer-text-color);
            font-size: 1.2em;
            transition: all 0.3s ease;
            text-decoration: none;
        }}
        .footer-social a:hover {{
            background-color: var(--primary-color);
            color: var(--dark-text-for-accent);
            transform: translateY(-3px);
        }}
        
        .wifi-card {{
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .wifi-card strong {{ color: var(--primary-color); }}
        
        .footer-bottom {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
            font-size: 0.85em;
            opacity: 0.8;
        }}
        
        /* Styles for the Page Modal */
        .page-modal-overlay {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0, 0, 0, 0.8); backdrop-filter: blur(10px);
            z-index: 2000; display: none; justify-content: center; align-items: center;
            opacity: 0; transition: opacity 0.3s ease-in-out;
        }}
        .page-modal-overlay.visible {{ display: flex; opacity: 1; }}
        .page-modal-content {{
            background-color: var(--card-bg); padding: 2rem 3rem; border-radius: 8px;
            border: 1px solid var(--border-color); width: 90%; max-width: 800px; max-height: 85vh;
            overflow-y: auto; position: relative; transform: scale(0.95); transition: transform 0.3s ease-in-out;
            color: #333;
        }}
        .page-modal-overlay.visible .page-modal-content {{ transform: scale(1); }}
        .close-page-modal-btn {{
            position: absolute; top: 15px; right: 20px; background: none; border: none;
            color: #333; font-size: 2.5em; cursor: pointer; line-height: 1;
            transition: transform 0.2s ease, color 0.2s ease;
        }}
        .close-page-modal-btn:hover {{ color: var(--primary-color); transform: rotate(90deg); }}
        #page-modal-title {{
            color: var(--primary-color); margin-top: 0; margin-bottom: 1.5rem;
            padding-bottom: 1rem; border-bottom: 1px solid var(--border-color); line-height: 1.3;
        }}
        #page-modal-body {{ line-height: 1.8; }}
        #page-modal-body a {{ color: var(--primary-color); }}
        #page-modal-body .spinner {{ margin: 40px auto; }}

        @media (max-width: 768px) {{
            #cart-sidebar {{ width: 95%; }}
            .page-modal-content {{ padding: 2rem 1.5rem; }}
            .footer-content {{ grid-template-columns: 1fr; gap: 30px; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-logo-container">
            {logo_html}
        </div>
        <h1>{site_title}</h1>
    </header>
    <nav class="main-nav">
        {menu_links_html}
    </nav>
    <div class="container">
        <nav id="category-nav" class="category-nav" style="display: none;"></nav>
        <main id="menu">
            <div id="loader"><div class="spinner"></div></div>
        </main>
    </div>
    <button id="cart-toggle">
        <svg fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M3 1a1 1 0 000 2h1.22l.305 1.222a.997.997 0 00.01.042l1.358 5.43-.893.892C3.74 11.846 4.632 14 6.414 14H15a1 1 0 000-2H6.414l1-1H14a1 1 0 00.894-.553l3-6A1 1 0 0017 3H6.28l-.31-1.243A1 1 0 005 1H3zM16 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM6.5 18a1.5 1.5 0 11-3 0 1.5 1.5 0 003 0z"></path></svg>
        <span id="cart-count">0</span>
    </button>
    <button id="scroll-to-top">&#x2191;</button>
    <aside id="cart-sidebar">
        <div class="cart-header">
            <h2>Ваше замовлення</h2>
            <button id="close-cart-btn">&times;</button>
        </div>
        <div id="cart-items-container" class="cart-items"></div>
        <div class="cart-footer">
            <div class="cart-total">
                <span>Всього:</span>
                <span id="cart-total-price">0 грн</span>
            </div>
            <button id="checkout-btn" disabled>Оформити замовлення</button>
        </div>
    </aside>
    <div id="checkout-modal" style="display: none;">
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h2>Оформлення замовлення</h2>
            <form id="checkout-form">
                <div class="form-group">
                    <label>Тип отримання:</label>
                    <div class="radio-group">
                        <input type="radio" id="delivery" name="delivery_type" value="delivery" checked>
                        <label for="delivery"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.125-.504 1.125-1.125V14.25m-17.25 4.5v-1.875a3.375 3.375 0 003.375-3.375h1.5a1.125 1.125 0 011.125 1.125v-1.5a3.375 3.375 0 00-3.375-3.375H3.375m15.75 9V14.25A3.375 3.375 0 0015.75 10.5h-1.5a1.125 1.125 0 01-1.125-1.125v-1.5a3.375 3.375 0 00-3.375-3.375H4.5m11.25 9h-3.375a1.125 1.125 0 01-1.125-1.125V14.25m1.125 1.125a3.375 3.375 0 013.375 3.375" /></svg> Доставка</label>
                        <input type="radio" id="pickup" name="delivery_type" value="pickup">
                        <label for="pickup"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" /></svg> Самовивіз</label>
                    </div>
                </div>
                <div class="form-group"><input type="text" id="customer_name" placeholder="Ваше ім'я" required></div>
                <div class="form-group"><input type="tel" id="phone_number" placeholder="Номер телефону" required></div>
                <div id="address-group" class="form-group"><input type="text" id="address" placeholder="Адреса доставки" required></div>
                <div class="form-group">
                    <label>Час отримання:</label>
                    <div class="radio-group">
                        <input type="radio" id="asap" name="delivery_time" value="asap" checked>
                        <label for="asap"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> Якнайшвидше</label>
                        <input type="radio" id="specific_time" name="delivery_time" value="specific">
                        <label for="specific_time"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> На інший час</label>
                    </div>
                </div>
                <div id="specific-time-group" class="form-group" style="display: none;">
                    <input type="text" id="specific_time_input" placeholder="Введіть час (напр. 18:30)">
                </div>

                <div class="form-group">
                    <label>Спосіб оплати:</label>
                    <div class="radio-group">
                        <input type="radio" id="pay_cash" name="payment_method" value="cash" checked>
                        <label for="pay_cash"><i class="fa-solid fa-money-bill-wave"></i> Готівка</label>
                        
                        <input type="radio" id="pay_card" name="payment_method" value="card">
                        <label for="pay_card"><i class="fa-regular fa-credit-card"></i> Картка</label>
                    </div>
                </div>

                <button type="submit" id="place-order-btn">Замовити</button>
            </form>
        </div>
    </div>
    
    <div id="page-modal" class="page-modal-overlay">
        <div class="page-modal-content">
            <button id="close-page-modal-btn" class="close-page-modal-btn">&times;</button>
            <h2 id="page-modal-title"></h2>
            <div id="page-modal-body"></div>
        </div>
    </div>

    <footer>
        <div class="footer-content">
            <div class="footer-section">
                <h4>Контакти</h4>
                <div class="footer-contact-item">
                    <i class="fa-solid fa-location-dot"></i>
                    <span>{footer_address}</span>
                </div>
                <div class="footer-contact-item">
                    <i class="fa-solid fa-phone"></i>
                    <a href="tel:{footer_phone}">{footer_phone}</a>
                </div>
                 <div class="footer-contact-item">
                    <i class="fa-solid fa-clock"></i>
                    <span>{working_hours}</span>
                </div>
            </div>
            <div class="footer-section">
                <h4>Ми в соцмережах</h4>
                <div class="footer-social">
                    {social_links_html}
                </div>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2024 {site_title}. Всі права захищені.</p>
        </div>
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            let cart = {{}};
            const savedCart = localStorage.getItem('webCart');
            if (savedCart) {{
                try {{
                    cart = JSON.parse(savedCart) || {{}};
                }} catch(e) {{
                    console.error("Could not parse saved cart:", e);
                    cart = {{}};
                }}
            }}

            // --- Element References ---
            const mainNav = document.querySelector('.main-nav');
            const menuContainer = document.getElementById('menu');
            const categoryNav = document.getElementById('category-nav');
            const cartSidebar = document.getElementById('cart-sidebar');
            const cartToggle = document.getElementById('cart-toggle');
            const closeCartBtn = document.getElementById('close-cart-btn');
            const cartItemsContainer = document.getElementById('cart-items-container');
            const cartTotalPriceEl = document.getElementById('cart-total-price');
            const cartCountEl = document.getElementById('cart-count');
            const checkoutBtn = document.getElementById('checkout-btn');
            const checkoutModal = document.getElementById('checkout-modal');
            const closeModalBtn = document.querySelector('.close-modal');
            const checkoutForm = document.getElementById('checkout-form');
            const loader = document.getElementById('loader');
            const scrollToTopBtn = document.getElementById('scroll-to-top');
            const deliveryTypeRadios = document.querySelectorAll('input[name="delivery_type"]');
            const addressGroup = document.getElementById('address-group');
            const addressInput = document.getElementById('address');
            const timeTypeRadios = document.querySelectorAll('input[name="delivery_time"]');
            const specificTimeGroup = document.getElementById('specific-time-group');
            const phoneInput = document.getElementById('phone_number');

            const pageModal = document.getElementById('page-modal');
            const closePageModalBtn = document.getElementById('close-page-modal-btn');
            const pageModalTitle = document.getElementById('page-modal-title');
            const pageModalBody = document.getElementById('page-modal-body');
            
            const lockBodyScroll = () => {{
                document.body.style.overflow = 'hidden';
            }};

            const unlockBodyScroll = () => {{
                document.body.style.overflow = '';
            }};

            // --- Checkout Logic ---
            deliveryTypeRadios.forEach(radio => radio.addEventListener('change', (e) => {{
                if (e.target.value === 'delivery') {{
                    addressGroup.style.display = 'block';
                    addressInput.required = true;
                }} else {{
                    addressGroup.style.display = 'none';
                    addressInput.required = false;
                }}
            }}));
            timeTypeRadios.forEach(radio => radio.addEventListener('change', (e) => {{
                specificTimeGroup.style.display = (e.target.value === 'specific') ? 'block' : 'none';
            }}));

            phoneInput.addEventListener('blur', async (e) => {{
                const phone = e.target.value.trim();
                if (phone.length >= 10) {{
                    try {{
                        const response = await fetch(`/api/customer_info/${{encodeURIComponent(phone)}}`);
                        if (response.ok) {{
                            const data = await response.json();
                            document.getElementById('customer_name').value = data.customer_name || '';
                            if (document.getElementById('address')) {{
                                document.getElementById('address').value = data.address || '';
                            }}
                        }}
                    }} catch (error) {{
                        console.warn('Could not fetch customer info:', error);
                    }}
                }}
            }});

            // --- Menu Rendering Logic ---
            const fetchMenu = async () => {{
                try {{
                    const response = await fetch('/api/menu');
                    const data = await response.json();
                    renderMenu(data);
                    setupScrollspy();
                    loader.style.display = 'none';
                    categoryNav.style.display = 'flex';
                }} catch (error) {{
                    loader.innerHTML = '<p>Не вдалося завантажити меню. Спробуйте оновити сторінку.</p>';
                }}
            }};

            const renderMenu = (data) => {{
                menuContainer.innerHTML = '';
                categoryNav.innerHTML = '';
                data.categories.forEach((category, index) => {{
                    const navLink = document.createElement('a');
                    navLink.href = `#category-${{category.id}}`;
                    navLink.textContent = category.name;
                    if (index === 0) {{
                        navLink.classList.add('active');
                    }}
                    categoryNav.appendChild(navLink);
                    const categorySection = document.createElement('section');
                    categorySection.className = 'category-section';
                    categorySection.id = `category-${{category.id}}`;
                    const categoryTitle = document.createElement('h2');
                    categoryTitle.className = 'category-title';
                    categoryTitle.textContent = category.name;
                    categorySection.appendChild(categoryTitle);
                    const productsGrid = document.createElement('div');
                    productsGrid.className = 'products-grid';
                    const products = data.products.filter(p => p.category_id === category.id);
                    products.forEach((product, pIndex) => {{
                        const productCard = document.createElement('div');
                        productCard.className = 'product-card';
                        productCard.style.animationDelay = `${{pIndex * 0.05}}s`;
                        productCard.innerHTML = `
                            <div class="product-image-wrapper">
                                <img src="/${{product.image_url || 'static/images/placeholder.jpg'}}" alt="${{product.name}}" class="product-image">
                            </div>
                            <div class="product-info">
                                <h3 class="product-name">${{product.name}}</h3>
                                <p class="product-desc">${{product.description || ''}}</p>
                                <div class="product-footer">
                                    <span class="product-price">${{product.price}} грн</span>
                                    <button class="add-to-cart-btn" data-id="${{product.id}}" data-name="${{product.name}}" data-price="${{product.price}}">Додати</button>
                                </div>
                            </div>
                        `;
                        productsGrid.appendChild(productCard);
                    }});
                    categorySection.appendChild(productsGrid);
                    menuContainer.appendChild(categorySection);
                }});
            }};
            
            const setupScrollspy = () => {{
                const navContainer = document.getElementById('category-nav');
                const navLinks = navContainer.querySelectorAll('a');
                const sections = document.querySelectorAll('.category-section');

                const setActiveLink = (activeLink) => {{
                    if (!activeLink) return;
                    navLinks.forEach(link => link.classList.remove('active'));
                    activeLink.classList.add('active');
                    
                    activeLink.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'nearest',
                        inline: 'center'
                    }});
                }};

                const observerOptions = {{
                    root: null,
                    rootMargin: '-40% 0px -60% 0px',
                    threshold: 0
                }};

                const observer = new IntersectionObserver((entries) => {{
                    entries.forEach(entry => {{
                        if (entry.isIntersecting) {{
                            const id = entry.target.getAttribute('id');
                            const activeLink = document.querySelector(`.category-nav a[href="#${{id}}"]`);
                            setActiveLink(activeLink);
                        }}
                    }});
                }}, observerOptions);

                sections.forEach(section => observer.observe(section));

                navContainer.addEventListener('click', (e) => {{
                    if (e.target.tagName === 'A') {{
                        setActiveLink(e.target);
                    }}
                }});
            }};
            
            const updateCartView = () => {{
                cartItemsContainer.innerHTML = '';
                let totalPrice = 0;
                let totalCount = 0;
                const items = Object.values(cart);
                if (items.length === 0) {{
                    cartItemsContainer.innerHTML = `
                        <div class="cart-empty-msg">
                            <svg fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10 2a4 4 0 00-4 4v1H5a1 1 0 00-.994.89l-1 9A1 1 0 004 18h12a1 1 0 00.994-1.11l-1-9A1 1 0 0015 7h-1V6a4 4 0 00-4-4zm2 5V6a2 2 0 10-4 0v1h4zm-6 3a1 1 0 112 0 1 1 0 01-2 0zm7-1a1 1 0 100 2 1 1 0 000-2z" clip-rule="evenodd"></path></svg>
                            <p>Ваш кошик порожній</p>
                            <a href="#menu" class="go-to-menu-btn" onclick="document.getElementById('close-cart-btn').click()">Перейти до меню</a>
                        </div>`;
                    checkoutBtn.disabled = true;
                }} else {{
                    items.forEach((item, index) => {{
                        totalPrice += item.price * item.quantity;
                        totalCount += item.quantity;
                        const cartItem = document.createElement('div');
                        cartItem.className = 'cart-item';
                        cartItem.style.animationDelay = `${{index * 0.05}}s`;
                        cartItem.innerHTML = `
                            <div class="cart-item-info">
                                <div class="cart-item-name">${{item.name}}</div>
                                <div class="cart-item-price">${{item.quantity}} x ${{item.price}} грн</div>
                            </div>
                            <div class="cart-item-controls">
                                <button data-id="${{item.id}}" class="change-quantity">-</button>
                                <span>${{item.quantity}}</span>
                                <button data-id="${{item.id}}" class="change-quantity">+</button>
                            </div>
                            <button class="cart-item-remove-btn" data-id="${{item.id}}">&times;</button>
                        `;
                        cartItemsContainer.appendChild(cartItem);
                    }});
                    checkoutBtn.disabled = false;
                }}
                cartTotalPriceEl.textContent = `${{totalPrice.toFixed(2)}} грн`;
                cartCountEl.textContent = totalCount;
                cartCountEl.style.display = totalCount > 0 ? 'flex' : 'none';
                
                localStorage.setItem('webCart', JSON.stringify(cart));
            }};

            menuContainer.addEventListener('click', e => {{
                if (e.target.classList.contains('add-to-cart-btn')) {{
                    const button = e.target;
                    const id = button.dataset.id;
                    if (cart[id]) {{
                        cart[id].quantity++;
                    }} else {{
                        cart[id] = {{
                            id: id, name: button.dataset.name, price: parseInt(button.dataset.price), quantity: 1
                        }};
                    }}
                    updateCartView();
                    cartToggle.classList.add('popping');
                    setTimeout(() => cartToggle.classList.remove('popping'), 400);
                    button.textContent = '✓ Додано';
                    button.classList.add('added');
                    setTimeout(() => {{
                        button.textContent = 'Додати';
                        button.classList.remove('added');
                    }}, 1500);
                }}
            }});

            cartItemsContainer.addEventListener('click', e => {{
                const target = e.target;
                const id = target.dataset.id;
                if (!id) return;
                if (target.classList.contains('change-quantity')) {{
                    if (target.textContent === '+') {{
                        cart[id].quantity++;
                    }} else {{
                        cart[id].quantity--;
                        if (cart[id].quantity === 0) delete cart[id];
                    }}
                    updateCartView();
                }}
                if (target.classList.contains('cart-item-remove-btn')) {{
                    delete cart[id];
                    updateCartView();
                }}
            }});

            const openModal = () => {{
                lockBodyScroll();
                checkoutModal.style.display = 'flex';
                setTimeout(() => checkoutModal.classList.add('visible'), 10);
            }};

            const closeModal = () => {{
                unlockBodyScroll();
                checkoutModal.classList.remove('visible');
                setTimeout(() => checkoutModal.style.display = 'none', 300);
            }};

            const toggleCart = () => cartSidebar.classList.toggle('open');
            cartToggle.addEventListener('click', toggleCart);
            closeCartBtn.addEventListener('click', toggleCart);
            checkoutBtn.addEventListener('click', () => {{
                if (Object.keys(cart).length > 0) openModal();
            }});
            closeModalBtn.addEventListener('click', closeModal);

            checkoutForm.addEventListener('submit', async e => {{
                e.preventDefault();
                const deliveryType = document.querySelector('input[name="delivery_type"]:checked').value;
                const timeType = document.querySelector('input[name="delivery_time"]:checked').value;
                
                // ПОЛУЧЕНИЕ ВЫБРАННОГО МЕТОДА ОПЛАТЫ
                const paymentMethod = document.querySelector('input[name="payment_method"]:checked').value;

                let deliveryTime = "Якнайшвидше";
                if (timeType === 'specific') {{
                    deliveryTime = document.getElementById('specific_time_input').value || "Не вказано";
                }}
                const orderData = {{
                    customer_name: document.getElementById('customer_name').value,
                    phone_number: document.getElementById('phone_number').value,
                    address: deliveryType === 'delivery' ? addressInput.value : null,
                    is_delivery: deliveryType === 'delivery',
                    delivery_time: deliveryTime,
                    payment_method: paymentMethod, // Передаем метод оплаты
                    items: Object.values(cart)
                }};
                const response = await fetch('/api/place_order', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(orderData)
                }});
                if (response.ok) {{
                    alert('Дякуємо! Ваше замовлення прийнято.');
                    cart = {{}};
                    localStorage.removeItem('webCart');
                    updateCartView();
                    closeModal();
                    checkoutForm.reset();
                    document.getElementById('delivery').checked = true;
                    addressGroup.style.display = 'block';
                    addressInput.required = true;
                    specificTimeGroup.style.display = 'none';
                    cartSidebar.classList.remove('open');
                }} else {{
                    alert('Сталася помилка. Спробуйте ще раз.');
                }}
            }});
            
            const openPageModal = async (itemId) => {{
                lockBodyScroll();
                pageModal.classList.add('visible');
                pageModalTitle.textContent = '';
                pageModalBody.innerHTML = '<div class="spinner"></div>'; 

                try {{
                    const response = await fetch(`/api/page/${{itemId}}`);
                    if (!response.ok) throw new Error('Page not found');
                    const data = await response.json();
                    pageModalTitle.textContent = data.title;
                    pageModalBody.innerHTML = data.content;
                }} catch (error) {{
                    pageModalTitle.textContent = 'Помилка';
                    pageModalBody.textContent = 'Не вдалося завантажити сторінку. Спробуйте пізніше.';
                }}
            }};

            const closePageModal = () => {{
                unlockBodyScroll();
                pageModal.classList.remove('visible');
            }};
            
            if(mainNav) {{
                mainNav.addEventListener('click', (e) => {{
                    const trigger = e.target.closest('.menu-popup-trigger');
                    if (trigger) {{
                        e.preventDefault();
                        const itemId = trigger.dataset.itemId;
                        openPageModal(itemId);
                    }}
                }});
            }}
            
            closePageModalBtn.addEventListener('click', closePageModal);
            pageModal.addEventListener('click', (e) => {{
                if (e.target === pageModal) {{
                    closePageModal();
                }}
            }});

            window.addEventListener('scroll', () => {{
                scrollToTopBtn.classList.toggle('visible', window.scrollY > 300);
            }});

            scrollToTopBtn.addEventListener('click', () => {{
                window.scrollTo({{ top: 0, behavior: 'smooth' }});
            }});

            fetchMenu();
            updateCartView();
        }});
    </script>
</body>
</html>
"""

ADMIN_DESIGN_SETTINGS_BODY = """
<div class="card">
    <form action="/admin/design_settings" method="post" enctype="multipart/form-data">
        <h2><i class="fa-solid fa-file-signature"></i> Назви та SEO</h2>
        
        <label for="site_title">Назва сайту/закладу:</label>
        <input type="text" id="site_title" name="site_title" value="{site_title}" placeholder="Назва, що відображається на сайті та в адмін-панелі">
        
        <label for="seo_description">SEO Опис (Description):</label>
        <textarea id="seo_description" name="seo_description" rows="3" placeholder="Короткий опис для пошукових систем (до 160 символів)">{seo_description}</textarea>
        
        <label for="seo_keywords">SEO Ключові слова (Keywords):</label>
        <input type="text" id="seo_keywords" name="seo_keywords" value="{seo_keywords}" placeholder="Наприклад: доставка їжі, ресторан, назва">

        <h2 style="margin-top: 2rem;"><i class="fa-solid fa-palette"></i> Дизайн та Кольори</h2>
        
        <div class="form-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px;">
            <div>
                <label for="primary_color">Основний колір (Акцент):</label>
                <input type="color" id="primary_color" name="primary_color" value="{primary_color}" style="width: 100%; height: 40px;">
            </div>
            <div>
                <label for="secondary_color">Додатковий колір:</label>
                <input type="color" id="secondary_color" name="secondary_color" value="{secondary_color}" style="width: 100%; height: 40px;">
            </div>
            <div>
                <label for="background_color">Колір фону сторінки:</label>
                <input type="color" id="background_color" name="background_color" value="{background_color}" style="width: 100%; height: 40px;">
            </div>
            <div>
                <label for="text_color">Колір основного тексту:</label>
                <input type="color" id="text_color" name="text_color" value="{text_color}" style="width: 100%; height: 40px;">
            </div>
            <div>
                <label for="footer_bg_color">Фон підвалу (Footer):</label>
                <input type="color" id="footer_bg_color" name="footer_bg_color" value="{footer_bg_color}" style="width: 100%; height: 40px;">
            </div>
            <div>
                <label for="footer_text_color">Текст підвалу:</label>
                <input type="color" id="footer_text_color" name="footer_text_color" value="{footer_text_color}" style="width: 100%; height: 40px;">
            </div>
        </div>
        
        <h3 style="margin-top: 1rem;">Навігація по категоріям</h3>
        <div class="form-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px;">
            <div>
                <label for="category_nav_bg_color">Колір фону (можна прозорий):</label>
                <input type="color" id="category_nav_bg_color" name="category_nav_bg_color" value="{category_nav_bg_color}" style="width: 100%; height: 40px;">
            </div>
            <div>
                <label for="category_nav_text_color">Колір тексту посилань:</label>
                <input type="color" id="category_nav_text_color" name="category_nav_text_color" value="{category_nav_text_color}" style="width: 100%; height: 40px;">
            </div>
        </div>
        
        <h3 style="margin-top: 2rem;">Зображення Шапки (Header)</h3>
        <label>Завантажте фонове зображення для шапки (Overlay буде додано автоматично):</label>
        <input type="file" name="header_image_file" accept="image/*">
        
        <div style="margin-top: 1rem;">
            <label for="font_family_sans">Основний шрифт (Без засічок):</label>
            <select id="font_family_sans" name="font_family_sans">
                {font_options_sans}
            </select>
            
            <label for="font_family_serif">Шрифт заголовків (Із засічками):</label>
            <select id="font_family_serif" name="font_family_serif">
                {font_options_serif}
            </select>
        </div>

        <h2 style="margin-top: 2rem;"><i class="fa-solid fa-circle-info"></i> Підвал сайту (Контакти)</h2>
        <div class="form-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <label for="footer_address"><i class="fa-solid fa-location-dot"></i> Адреса:</label>
                <input type="text" id="footer_address" name="footer_address" value="{footer_address}" placeholder="вул. Прикладна, 10">
            </div>
            <div>
                <label for="footer_phone"><i class="fa-solid fa-phone"></i> Телефон:</label>
                <input type="text" id="footer_phone" name="footer_phone" value="{footer_phone}" placeholder="+380 XX XXX XX XX">
            </div>
            <div>
                <label for="working_hours"><i class="fa-solid fa-clock"></i> Час роботи:</label>
                <input type="text" id="working_hours" name="working_hours" value="{working_hours}" placeholder="Пн-Нд: 10:00 - 22:00">
            </div>
        </div>
        
        <h4 style="margin-top: 1rem;">Налаштування Wi-Fi (для QR меню)</h4>
        <div class="form-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <label for="wifi_ssid"><i class="fa-solid fa-wifi"></i> Назва мережі (SSID):</label>
                <input type="text" id="wifi_ssid" name="wifi_ssid" value="{wifi_ssid}" placeholder="Restaurant_WiFi">
            </div>
            <div>
                <label for="wifi_password"><i class="fa-solid fa-lock"></i> Пароль:</label>
                <input type="text" id="wifi_password" name="wifi_password" value="{wifi_password}" placeholder="securepass123">
            </div>
        </div>

        <div class="form-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 10px;">
            <div>
                <label for="instagram_url"><i class="fa-brands fa-instagram"></i> Instagram (посилання):</label>
                <input type="text" id="instagram_url" name="instagram_url" value="{instagram_url}" placeholder="https://instagram.com/...">
            </div>
            <div>
                <label for="facebook_url"><i class="fa-brands fa-facebook"></i> Facebook (посилання):</label>
                <input type="text" id="facebook_url" name="facebook_url" value="{facebook_url}" placeholder="https://facebook.com/...">
            </div>
        </div>
        
        <h2 style="margin-top: 2rem;"><i class="fa-brands fa-telegram"></i> Тексти Telegram-бота</h2>
        
        <label for="telegram_welcome_message">Привітальне повідомлення (Клієнт-бот):</label>
        <textarea id="telegram_welcome_message" name="telegram_welcome_message" rows="5" placeholder="Текст, який бачить користувач при старті бота.">{telegram_welcome_message}</textarea>
        <p style="font-size: 0.8rem; margin-top: -0.5rem; margin-bottom: 1rem;">Використовуйте <code>{{user_name}}</code>, щоб вставити ім'я користувача.</p>

        <div style="margin-top: 2rem;">
            <button type="submit">Зберегти налаштування</button>
        </div>
    </form>
</div>
"""
ADMIN_REPORT_CASH_FLOW_BODY = """
<div class="card">
    <h2>💰 Отчет о движении денежных средств</h2>
    <form action="/admin/reports/cash_flow" method="get" class="search-form" style="background: #f9f9f9; padding: 15px; border-radius: 8px;">
        <label>Период:</label>
        <input type="date" name="date_from" value="{date_from}" required>
        <span>—</span>
        <input type="date" name="date_to" value="{date_to}" required>
        <button type="submit">Показать</button>
    </form>
</div>

<div class="card">
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px;">
        <div style="background:#e8f5e9; padding:15px; border-radius:5px;">
            <small>Общая выручка</small>
            <div style="font-size:1.4em; font-weight:bold; color:#2e7d32;">{total_revenue} грн</div>
        </div>
        <div style="background:#fff3e0; padding:15px; border-radius:5px;">
            <small>Наличные</small>
            <div style="font-size:1.4em; font-weight:bold; color:#ef6c00;">{cash_revenue} грн</div>
        </div>
        <div style="background:#e3f2fd; padding:15px; border-radius:5px;">
            <small>Карта / Терминал</small>
            <div style="font-size:1.4em; font-weight:bold; color:#1565c0;">{card_revenue} грн</div>
        </div>
        <div style="background:#ffebee; padding:15px; border-radius:5px;">
            <small>Расходы (Изъятия)</small>
            <div style="font-size:1.4em; font-weight:bold; color:#c62828;">{total_expenses} грн</div>
        </div>
    </div>

    <h3>Детализация транзакций (Служебные)</h3>
    <table>
        <thead><tr><th>Дата</th><th>Тип</th><th>Сумма</th><th>Кассир</th><th>Комментарий</th></tr></thead>
        <tbody>{transaction_rows}</tbody>
    </table>
</div>
"""

ADMIN_REPORT_WORKERS_BODY = """
<div class="card">
    <h2>👥 Отчет по сотрудникам</h2>
    <form action="/admin/reports/workers" method="get" class="search-form" style="background: #f9f9f9; padding: 15px; border-radius: 8px;">
        <label>Период:</label>
        <input type="date" name="date_from" value="{date_from}" required>
        <span>—</span>
        <input type="date" name="date_to" value="{date_to}" required>
        <button type="submit">Показать</button>
    </form>
</div>

<div class="card">
    <table>
        <thead>
            <tr>
                <th>Сотрудник</th>
                <th>Роль</th>
                <th>Кол-во заказов</th>
                <th>Общая сумма продаж</th>
                <th>Средний чек</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</div>
"""

ADMIN_REPORT_ANALYTICS_BODY = """
<div class="card">
    <h2>📈 Аналитика продаж (Топ блюд)</h2>
    <form action="/admin/reports/analytics" method="get" class="search-form" style="background: #f9f9f9; padding: 15px; border-radius: 8px;">
        <label>Период:</label>
        <input type="date" name="date_from" value="{date_from}" required>
        <span>—</span>
        <input type="date" name="date_to" value="{date_to}" required>
        <button type="submit">Показать</button>
    </form>
</div>

<div class="card">
    <h3>Топ популярных позиций</h3>
    <table>
        <thead>
            <tr>
                <th>№</th>
                <th>Название блюда</th>
                <th>Продано (шт)</th>
                <th>Выручка (грн)</th>
                <th>Доля выручки</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</div>
"""

STAFF_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вхід для персоналу</title>
    <link rel="manifest" href="/staff/manifest.json">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f0f2f5; }
        .login-card { background: white; padding: 2.5rem; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); width: 90%; max-width: 380px; text-align: center; }
        h2 { margin-top: 0; color: #333; margin-bottom: 1.5rem; }
        input { width: 100%; padding: 14px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 16px; background: #fafafa; }
        input:focus { border-color: #333; outline: none; background: #fff; }
        button { width: 100%; padding: 14px; background: #333; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 15px; transition: background 0.2s; }
        button:hover { background: #000; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>🔐 Staff Access</h2>
        <form action="/staff/login" method="post">
            <input type="tel" name="phone" placeholder="Номер телефону" required autocomplete="username">
            <input type="password" name="password" placeholder="Пароль" required autocomplete="current-password">
            <button type="submit">Увійти</button>
        </form>
    </div>
    <script>
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
          navigator.serviceWorker.register('/sw.js');
        });
      }
    </script>
</body>
</html>
"""
# ... (предыдущие шаблоны остаются без изменений: ADMIN_HTML_TEMPLATE, ADMIN_TABLES_BODY, и т.д.)

# templates.py (только STAFF_DASHBOARD_HTML, остальное оставьте как было)

STAFF_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{site_title} - Staff</title>
    <link rel="manifest" href="/staff/manifest.json">
    <meta name="theme-color" content="#333">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <style>
        :root {{ --primary: #333; --accent: #f39c12; --bg: #f4f4f4; --white: #fff; --green: #27ae60; --red: #e74c3c; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: var(--bg); padding-bottom: 80px; -webkit-tap-highlight-color: transparent; }}
        
        /* HEADER */
        .dashboard-header {{ background: var(--white); padding: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 100; }}
        .user-info h3 {{ margin: 0; font-size: 1.1rem; }}
        .role-badge {{ font-size: 0.8rem; background: #eee; padding: 2px 6px; border-radius: 4px; color: #555; }}
        .shift-btn {{ border: none; padding: 8px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem; cursor: pointer; transition: all 0.2s; }}
        .shift-btn.on {{ background: #e8f5e9; color: var(--green); border: 1px solid var(--green); }}
        .shift-btn.off {{ background: #ffebee; color: var(--red); border: 1px solid var(--red); }}

        /* CONTENT AREA */
        #main-view {{ padding: 15px; }}
        .empty-state {{ text-align: center; color: #999; margin-top: 50px; font-size: 0.9rem; }}
        
        /* CARDS */
        .grid-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; }}
        .card {{ background: var(--white); border-radius: 10px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); cursor: pointer; transition: transform 0.1s; }}
        .card:active {{ transform: scale(0.98); }}
        .table-card {{ text-align: center; border: 2px solid transparent; }}
        .table-card .card-title {{ font-weight: bold; margin-bottom: 5px; font-size: 1.1rem; }}
        
        .order-card {{ margin-bottom: 15px; border-left: 4px solid var(--primary); background: var(--white); padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        .order-card .card-header {{ display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 0.9rem; color: #666; }}
        .order-card .card-body {{ font-size: 0.95rem; line-height: 1.4; }}
        .order-card .card-footer {{ margin-top: 15px; text-align: right; }}
        .info-row {{ display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }}
        
        /* BUTTONS & BADGES */
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }}
        .badge.success {{ background: #e8f5e9; color: var(--green); }}
        .badge.alert {{ background: #ffebee; color: var(--red); }}
        
        .action-btn {{ background: var(--primary); color: var(--white); border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.9rem; }}
        .action-btn.secondary {{ background: #eee; color: #333; }}
        
        /* BOTTOM NAV */
        .bottom-nav {{ position: fixed; bottom: 0; left: 0; width: 100%; background: var(--white); border-top: 1px solid #ddd; display: flex; justify-content: space-around; padding: 10px 0; z-index: 100; padding-bottom: max(10px, env(safe-area-inset-bottom)); }}
        .nav-item {{ background: none; border: none; color: #999; display: flex; flex-direction: column; align-items: center; font-size: 0.7rem; width: 100%; cursor: pointer; }}
        .nav-item.active {{ color: var(--primary); }}
        .nav-item i {{ font-size: 1.4rem; margin-bottom: 4px; }}

        /* MODAL */
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 2000; justify-content: center; align-items: flex-end; }}
        .modal.active {{ display: flex; animation: slideUp 0.3s; }}
        .modal-content {{ background: var(--white); width: 100%; max-height: 90vh; border-radius: 15px 15px 0 0; padding: 20px; overflow-y: auto; box-sizing: border-box; }}
        .close {{ float: right; font-size: 24px; cursor: pointer; }}
        @keyframes slideUp {{ from {{ transform: translateY(100%); }} to {{ transform: translateY(0); }} }}

        /* CART STYLES */
        .menu-item {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; align-items: center; }}
        .qty-ctrl {{ display: flex; align-items: center; gap: 10px; }}
        .qty-btn {{ width: 30px; height: 30px; border-radius: 50%; border: 1px solid #ddd; background: #fff; font-weight: bold; cursor: pointer; }}
        .cart-bar {{ display: flex; justify-content: space-between; align-items: center; margin-top: 15px; padding-top: 15px; border-top: 2px solid #eee; font-weight: bold; }}
        .big-btn {{ width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: bold; margin-top: 10px; cursor: pointer; }}
    </style>
</head>
<body>
    {content}
    
    <div id="staff-modal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <div id="modal-body"></div>
        </div>
    </div>

    <audio id="notification-sound" src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" preload="auto"></audio>

    <script>
        // --- GLOBAL STATE ---
        let currentView = 'orders'; // 'orders', 'tables', 'production', 'delivery'
        let currentTableId = null;
        let menuData = [];
        let cart = {{}}; // {{ productId: {{ qty: 1, price: 100, name: '...' }} }}

        // --- INITIALIZATION ---
        document.addEventListener('DOMContentLoaded', () => {{
            const activeBtn = document.querySelector('.nav-item.active');
            if (activeBtn) {{
                const onclick = activeBtn.getAttribute('onclick');
                const match = onclick.match(/switchTab\('(\w+)'\)/);
                if (match) currentView = match[1];
            }}
            fetchData();
            setInterval(fetchData, 8000); // Оновлення кожні 8с
        }});

        // --- NAVIGATION ---
        function switchTab(view) {{
            currentView = view;
            document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
            event.currentTarget.classList.add('active');
            
            document.getElementById('content-area').innerHTML = '<div id="loading-indicator" style="text-align:center;margin-top:20px;"><i class="fa-solid fa-spinner fa-spin"></i></div>';
            fetchData();
        }}

        // --- DATA FETCHING ---
        async function fetchData() {{
            const errEl = document.getElementById('error-message');
            try {{
                const response = await fetch(`/staff/api/data?view=${{currentView}}`);
                
                if (!response.ok) {{
                    throw new Error("Server error: " + response.status);
                }}
                
                const data = await response.json();
                if (data.error) throw new Error(data.error);
                
                document.getElementById('content-area').innerHTML = data.html;
                errEl.style.display = 'none';
            }} catch (e) {{ 
                console.error(e); 
                document.getElementById('loading-indicator').style.display = 'none';
                errEl.innerText = "Ошибка соединения. Проверьте интернет.";
                errEl.style.display = 'block';
            }}
        }}

        async function toggleShift() {{
            const btn = document.getElementById('shift-btn');
            btn.disabled = true;
            const res = await fetch('/staff/api/shift/toggle', {{ method: 'POST' }});
            const data = await res.json();
            if (data.status === 'ok') {{
                location.reload(); 
            }}
        }}

        // --- ACTIONS ---
        async function performAction(action, orderId, extra=null) {{
            if(!confirm("Подтвердить действие?")) return;
            
            try {{
                const res = await fetch('/staff/api/action', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ action, orderId, extra }})
                }});
                const data = await res.json();
                if (data.success) {{
                    fetchData();
                    closeModal();
                }} else {{
                    alert("Ошибка: " + (data.error || "Unknown"));
                }}
            }} catch (e) {{ alert("Network error"); }}
        }}

        // --- TABLE MODAL & ORDERS ---
        async function openTableModal(tableId, tableName) {{
            currentTableId = tableId;
            cart = {{}};
            const modal = document.getElementById('staff-modal');
            const body = document.getElementById('modal-body');
            
            body.innerHTML = `
                <h3>🪑 ${{tableName}}</h3>
                <div id="table-orders-list">Загрузка...</div>
                <hr>
                <button class="big-btn" onclick="openMenuForOrder()">➕ Новый заказ</button>
            `;
            modal.classList.add('active');
            loadTableOrders(tableId);
        }}

        async function loadTableOrders(tableId) {{
            const res = await fetch(`/staff/api/table/${{tableId}}/orders`);
            const orders = await res.json();
            const container = document.getElementById('table-orders-list');
            
            if (orders.length === 0) {{
                container.innerHTML = "<p>Активных заказов нет.</p>";
                return;
            }}
            
            let html = "";
            orders.forEach(o => {{
                html += `
                <div style="background:#f9f9f9; padding:10px; margin-bottom:10px; border-radius:8px;">
                    <div style="display:flex; justify-content:space-between;">
                        <b>#${{o.id}}</b> <span>${{o.status}}</span>
                    </div>
                    <div style="font-size:0.85rem; color:#666; margin:5px 0;">${{o.items}}</div>
                    <div style="text-align:right; font-weight:bold;">${{o.total}} грн</div>
                    <div style="text-align:right; margin-top:5px;">
                        <button class="action-btn secondary" onclick="openPaymentModal(${{o.id}}, ${{o.total}})">💰 Расчет</button>
                    </div>
                </div>`;
            }});
            container.innerHTML = html;
        }}

        // --- MENU & CART ---
        async function openMenuForOrder() {{
            const body = document.getElementById('modal-body');
            body.innerHTML = "Загрузка меню...";
            
            if (menuData.length === 0) {{
                const res = await fetch('/staff/api/menu/full');
                menuData = await res.json();
            }}
            
            renderMenu();
        }}

        function renderMenu() {{
            const body = document.getElementById('modal-body');
            let html = `
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3>Создать заказ</h3>
                    <button class="action-btn secondary" onclick="openTableModal(currentTableId, '')">Назад</button>
                </div>
                <div style="max-height:60vh; overflow-y:auto;">`;
            
            menuData.forEach(cat => {{
                html += `<h4 style="margin-bottom:5px; color:var(--primary);">${{cat.name}}</h4>`;
                cat.products.forEach(prod => {{
                    const qty = cart[prod.id] ? cart[prod.id].qty : 0;
                    html += `
                    <div class="menu-item">
                        <div>${{prod.name}}<br><small>${{prod.price}} грн</small></div>
                        <div class="qty-ctrl">
                            <button class="qty-btn" onclick="updateCart(${{prod.id}}, '${{prod.name}}', ${{prod.price}}, -1)">-</button>
                            <span>${{qty}}</span>
                            <button class="qty-btn" onclick="updateCart(${{prod.id}}, '${{prod.name}}', ${{prod.price}}, 1)">+</button>
                        </div>
                    </div>`;
                }});
            }});
            
            html += `</div>
            <div class="cart-bar">
                <span>Итого: <span id="cart-total">0</span> грн</span>
                <button class="action-btn" onclick="submitOrder()">✅ Отправить</button>
            </div>`;
            
            body.innerHTML = html;
            recalcCartTotal();
        }}

        function updateCart(id, name, price, delta) {{
            if (!cart[id]) cart[id] = {{ qty: 0, price: price, name: name }};
            cart[id].qty += delta;
            if (cart[id].qty <= 0) delete cart[id];
            renderMenu();
        }}

        function recalcCartTotal() {{
            let total = 0;
            Object.values(cart).forEach(item => total += item.qty * item.price);
            document.getElementById('cart-total').innerText = total.toFixed(2);
        }}

        async function submitOrder() {{
            const items = Object.entries(cart).map(([id, val]) => ({{ id: id, qty: val.qty }}));
            if (items.length === 0) return alert("Корзина пуста");
            
            try {{
                const res = await fetch('/staff/api/order/create', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ tableId: currentTableId, cart: items }})
                }});
                const data = await res.json();
                if (data.success) {{
                    alert("Заказ создан!");
                    openTableModal(currentTableId, ""); 
                }} else {{
                    alert("Ошибка: " + data.error);
                }}
            }} catch (e) {{ alert("Network error"); }}
        }}

        // --- PAYMENT ---
        function openPaymentModal(orderId, total) {{
            const body = document.getElementById('modal-body');
            body.innerHTML = `
                <h3>💰 Оплата заказа #${{orderId}}</h3>
                <p style="font-size:1.2rem;">Сумма: <b>${{total}} грн</b></p>
                <hr>
                <p>Выберите метод:</p>
                <button class="big-btn" onclick="performAction('pay_order', ${{orderId}}, 'cash')">💵 Наличные</button>
                <button class="big-btn" style="background:#2980b9;" onclick="performAction('pay_order', ${{orderId}}, 'card')">💳 Карта / Терминал</button>
            `;
            document.getElementById('staff-modal').classList.add('active');
        }}
        
        function changeStatus(orderId, statusId) {{
             performAction('change_status', orderId, statusId);
        }}

        function closeModal() {{
            document.getElementById('staff-modal').classList.remove('active');
        }}
        
        // --- Service Worker Registration ---
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
              navigator.serviceWorker.register('/sw.js')
                .then(registration => console.log('SW registered'))
                .catch(err => console.log('SW registration failed', err));
            }});
        }}
    </script>
</body>
</html>
"""