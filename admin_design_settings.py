# admin_design_settings.py

import html
import os
import secrets
import aiofiles
from fastapi import APIRouter, Depends, Form, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Settings
# Тепер імпортуємо і ADMIN_DESIGN_SETTINGS_BODY, оскільки ми перенесли його в templates.py
from templates import ADMIN_HTML_TEMPLATE, ADMIN_DESIGN_SETTINGS_BODY
from dependencies import get_db_session, check_credentials

router = APIRouter()

# --- Словники шрифтів для легкого керування ---
FONT_FAMILIES_SANS = [
    "Golos Text", "Inter", "Roboto", "Open Sans", "Montserrat", "Lato", "Nunito"
]
DEFAULT_FONT_SANS = "Golos Text"

FONT_FAMILIES_SERIF = [
    "Playfair Display", "Lora", "Merriweather", "EB Garamond", "PT Serif", "Cormorant"
]
DEFAULT_FONT_SERIF = "Playfair Display"
# -----------------------------------------------

@router.get("/admin/design_settings", response_class=HTMLResponse)
async def get_design_settings_page(
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    """Відображає сторінку налаштувань дизайну, SEO та текстів."""
    settings = await session.get(Settings, 1)
    if not settings:
        settings = Settings(id=1) # Створюємо тимчасовий об'єкт, якщо в БД пусто

    # --- Функція для генерації HTML <option> для <select> ---
    def get_font_options(font_list: list, selected_font: str, default_font: str) -> str:
        options_html = ""
        current_font = selected_font or default_font
        for font in font_list:
            is_default = "(За замовчуванням)" if font == default_font else ""
            is_selected = "selected" if font == current_font else ""
            options_html += f'<option value="{html.escape(font)}" {is_selected}>{html.escape(font)} {is_default}</option>\n'
        return options_html
    # -----------------------------------------------------

    font_options_sans = get_font_options(FONT_FAMILIES_SANS, settings.font_family_sans, DEFAULT_FONT_SANS)
    font_options_serif = get_font_options(FONT_FAMILIES_SERIF, settings.font_family_serif, DEFAULT_FONT_SERIF)

    # Отримуємо поточний логотип для відображення (якщо є)
    current_logo_html = f'<img src="/{settings.logo_url}" alt="Поточний логотип" style="height: 50px; margin-top: 10px;">' if settings.logo_url else ''
    
    # Cache buster для фавіконок, щоб браузер оновлював їх
    cache_buster = secrets.token_hex(4)

    body = ADMIN_DESIGN_SETTINGS_BODY.format(
        site_title=html.escape(settings.site_title or "Назва"),
        seo_description=html.escape(settings.seo_description or ""),
        seo_keywords=html.escape(settings.seo_keywords or ""),
        
        # --- Кольори ---
        primary_color=settings.primary_color or "#5a5a5a",
        secondary_color=settings.secondary_color or "#eeeeee",
        background_color=settings.background_color or "#f4f4f4",
        text_color=settings.text_color or "#333333",
        footer_bg_color=settings.footer_bg_color or "#333333",
        footer_text_color=settings.footer_text_color or "#ffffff",
        
        # --- Навігація ---
        category_nav_bg_color=settings.category_nav_bg_color or "#ffffff",
        category_nav_text_color=settings.category_nav_text_color or "#333333",
        # ------------------

        current_logo_html=current_logo_html,
        cache_buster=cache_buster,

        # --- Шрифти ---
        font_options_sans=font_options_sans,
        font_options_serif=font_options_serif,
        
        # --- Контакти (Підвал) та Wi-Fi ---
        footer_address=html.escape(settings.footer_address or ""),
        footer_phone=html.escape(settings.footer_phone or ""),
        working_hours=html.escape(settings.working_hours or ""),
        instagram_url=html.escape(settings.instagram_url or ""),
        facebook_url=html.escape(settings.facebook_url or ""),
        wifi_ssid=html.escape(settings.wifi_ssid or ""),
        wifi_password=html.escape(settings.wifi_password or ""),
        # ----------------------------------

        telegram_welcome_message=html.escape(settings.telegram_welcome_message or "Шановний {user_name}, ласкаво просимо! 👋\n\nМи раді вас бачити. Оберіть опцію:"),
    )

    active_classes = {key: "" for key in ["main_active", "orders_active", "clients_active", "tables_active", "products_active", "categories_active", "menu_active", "employees_active", "statuses_active", "reports_active", "settings_active"]}
    active_classes["design_active"] = "active"
    
    return HTMLResponse(ADMIN_HTML_TEMPLATE.format(
        title="Дизайн та SEO", 
        body=body, 
        site_title=settings.site_title or "Назва",
        **active_classes
    ))

@router.post("/admin/design_settings")
async def save_design_settings(
    site_title: str = Form(...),
    seo_description: str = Form(""),
    seo_keywords: str = Form(""),
    
    # --- Кольори ---
    primary_color: str = Form(...),
    secondary_color: str = Form(...),
    background_color: str = Form(...),
    text_color: str = Form("#333333"),
    footer_bg_color: str = Form("#333333"),
    footer_text_color: str = Form("#ffffff"),
    
    # --- Навігація ---
    category_nav_bg_color: str = Form("#ffffff"),
    category_nav_text_color: str = Form("#333333"),
    # -----------------

    # --- Зображення шапки ---
    header_image_file: UploadFile = File(None),
    
    # --- Підвал та контакти ---
    footer_address: str = Form(""),
    footer_phone: str = Form(""),
    working_hours: str = Form(""),
    instagram_url: str = Form(""),
    facebook_url: str = Form(""),
    wifi_ssid: str = Form(""),
    wifi_password: str = Form(""),
    # --------------------------

    font_family_sans: str = Form(...),
    font_family_serif: str = Form(...),
    telegram_welcome_message: str = Form(...),
    session: AsyncSession = Depends(get_db_session),
    username: str = Depends(check_credentials)
):
    """Зберігає налаштування дизайну, SEO, контактів та текстів."""
    settings = await session.get(Settings, 1)
    if not settings:
        settings = Settings(id=1)
        session.add(settings)

    settings.site_title = site_title
    settings.seo_description = seo_description
    settings.seo_keywords = seo_keywords
    
    # --- Збереження кольорів ---
    settings.primary_color = primary_color
    settings.secondary_color = secondary_color
    settings.background_color = background_color
    settings.text_color = text_color
    settings.footer_bg_color = footer_bg_color
    settings.footer_text_color = footer_text_color
    settings.category_nav_bg_color = category_nav_bg_color
    settings.category_nav_text_color = category_nav_text_color
    # --------------------------------

    # --- Обробка зображення шапки ---
    if header_image_file and header_image_file.filename:
        # Видаляємо старе зображення, якщо воно є
        if settings.header_image_url and os.path.exists(settings.header_image_url):
            try:
                os.remove(settings.header_image_url)
            except OSError:
                pass
        
        # Зберігаємо нове
        ext = header_image_file.filename.split('.')[-1] if '.' in header_image_file.filename else 'jpg'
        filename = f"header_bg_{secrets.token_hex(8)}.{ext}"
        path = os.path.join("static/images", filename)
        
        try:
            async with aiofiles.open(path, 'wb') as f:
                await f.write(await header_image_file.read())
            settings.header_image_url = path
        except Exception as e:
            print(f"Error saving header image: {e}")
    # --------------------------------

    # --- Збереження контактів та Wi-Fi ---
    settings.footer_address = footer_address
    settings.footer_phone = footer_phone
    settings.working_hours = working_hours
    settings.instagram_url = instagram_url
    settings.facebook_url = facebook_url
    settings.wifi_ssid = wifi_ssid
    settings.wifi_password = wifi_password
    # -------------------------------------

    settings.font_family_sans = font_family_sans
    settings.font_family_serif = font_family_serif
    settings.telegram_welcome_message = telegram_welcome_message

    await session.commit()
    
    return RedirectResponse(url="/admin/design_settings?saved=true", status_code=303)