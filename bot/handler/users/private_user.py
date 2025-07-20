import asyncio
import logging
import re
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async

from set_main.models import User, Order, Car, Route, BotSettings
from bot.states.user_state import Form, AdminStates
from bot.keyboards.inline import (
    get_direction_kb, get_trip_type_kb, get_car_kb, 
    get_confirm_kb, get_admin_kb, get_no_comment_kb,
    get_year_kb, get_month_kb, get_day_kb
)
from bot.keyboards.reply import get_main_menu, get_cancel_kb

router = Router()

# --- VALIDATORS ---
def is_valid_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def is_valid_phone(phone):
    return re.match(r"^(\+998|998)?\d{9}$", phone)

# --- COMMANDS ---
@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    logging.info(f"/start from user_id={message.from_user.id}")
    await state.clear()
    
    # Add user to database
    user, created = await sync_to_async(User.objects.get_or_create)(
        user_id=message.from_user.id,
        defaults={'full_name': message.from_user.full_name}
    )
    
    if created:
        logging.info(f"User registered: {message.from_user.id} {message.from_user.full_name}")
    
    # Set commands based on user role
    settings = await sync_to_async(BotSettings.objects.first)()
    admin_id = settings.admin_id if settings else None
    if message.from_user.id == admin_id:
        commands = [
            BotCommand(command="start", description="Buyurtma berishni boshlash"),
            BotCommand(command="help", description="Yordam"),
            BotCommand(command="cancel", description="Jarayonni bekor qilish"),
            BotCommand(command="admin", description="Admin panel (faqat admin uchun)"),
            BotCommand(command="stats", description="Statistika (faqat admin uchun)"),
            BotCommand(command="users", description="Foydalanuvchilar soni (faqat admin uchun)")
        ]
    else:
        commands = [
            BotCommand(command="start", description="Buyurtma berishni boshlash"),
            BotCommand(command="help", description="Yordam"),
            BotCommand(command="cancel", description="Jarayonni bekor qilish")
        ]
    await message.bot.set_my_commands(commands, scope={"type": "chat", "chat_id": message.chat.id})

    await message.answer(
        "Assalomu alaykum!\n\nBuyurtma berish uchun yo'nalishni tanlang ",
        reply_markup=await get_direction_kb()
    )
    await state.set_state(Form.direction)

@router.message(Command("help"))
async def help_cmd(message: Message, state: FSMContext):
    logging.info(f"/help from user_id={message.from_user.id}")
    await message.answer(
        "Bot yordamchisi:\n\n"
        "/start — Buyurtma berishni boshlash\n"
        "/cancel — Jarayonni bekor qilish\n"
        "/help — Yordam\n\n"
        "Buyurtma bosqichlarida tugmalardan foydalaning va ma'lumotlarni to'g'ri kiriting."
    )

@router.message(Command("cancel"))
async def cancel_cmd(message: Message, state: FSMContext):
    logging.info(f"/cancel from user_id={message.from_user.id}")
    await state.clear()
    await message.answer("Buyurtma bekor qilindi. /start orqali yangidan boshlang.")

@router.message(Command("stats"))
async def stats_cmd(message: Message):
    logging.info(f"/stats from user_id={message.from_user.id}")
    
    # Get admin ID from settings
    try:
        settings = await sync_to_async(BotSettings.objects.first)()
        admin_id = settings.admin_id if settings else None
    except:
        admin_id = None
    
    if message.from_user.id == admin_id:
        orders_count = await sync_to_async(Order.objects.count)()
        await message.answer(f"Jami buyurtmalar: {orders_count}")
    else:
        await message.answer("Bu buyruq faqat admin uchun.")

@router.message(Command("adminhelp"))
async def admin_help(message: Message):
    logging.info(f"/adminhelp from user_id={message.from_user.id}")
    
    # Get admin ID from settings
    try:
        settings = await sync_to_async(BotSettings.objects.first)()
        admin_id = settings.admin_id if settings else None
    except:
        admin_id = None
    
    if message.from_user.id == admin_id:
        await message.answer(
            "Admin uchun buyruqlar:\n"
            "/admin — Admin panel\n"
            "/adminhelp — Admin uchun yordam\n"
            "/stats — Buyurtmalar statistikasi\n"
            "/users — Foydalanuvchilar soni\n\n"
            "Panelda: Mashina va marshrutlarni qo'shish/o'chirish/ko'rish."
        )
    else:
        await message.answer("Bu buyruq faqat admin uchun.")

@router.message(Command("users"))
async def users_count(message: Message):
    logging.info(f"/users from user_id={message.from_user.id}")
    
    # Get admin ID from settings
    try:
        settings = await sync_to_async(BotSettings.objects.first)()
        admin_id = settings.admin_id if settings else None
    except:
        admin_id = None
    
    if message.from_user.id == admin_id:
        count = await sync_to_async(User.objects.count)()
        await message.answer(f"Jami foydalanuvchilar: {count}")
    else:
        await message.answer("Bu buyruq faqat admin uchun.")

# --- ADMIN PANEL ---
@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    logging.info(f"/admin from user_id={message.from_user.id}")
    
    # Get admin ID from settings
    try:
        settings = await sync_to_async(BotSettings.objects.first)()
        admin_id = settings.admin_id if settings else None
    except:
        admin_id = None
    
    if message.from_user.id != admin_id:
        await message.answer("Bu bo'lim faqat admin uchun.")
        return
    
    await message.answer("Admin paneliga xush kelibsiz!", reply_markup=get_admin_kb())

@router.callback_query(F.data.startswith("admin_"))
async def admin_actions(callback: CallbackQuery, state: FSMContext):
    logging.info(f"Admin action: {callback.data} from user_id={callback.from_user.id}")
    
    # Get admin ID from settings
    try:
        settings = await sync_to_async(BotSettings.objects.first)()
        admin_id = settings.admin_id if settings else None
    except:
        admin_id = None
    
    if callback.from_user.id != admin_id:
        await callback.answer("Faqat admin uchun!", show_alert=True)
        return
    
    async def safe_answer(text, reply_markup=None):
        if callback.message:
            return await callback.message.answer(text, reply_markup=reply_markup)
        else:
            return await callback.bot.send_message(callback.from_user.id, text, reply_markup=reply_markup)
    
    if callback.data == "admin_add_car":
        await safe_answer("Yangi mashina nomini kiriting:")
        await state.set_state(AdminStates.add_car)
    elif callback.data == "admin_del_car":
        cars = await sync_to_async(list)(Car.objects.all())
        if not cars:
            await safe_answer("Mashinalar ro'yxati bo'sh.")
            return
        text = "O'chirmoqchi bo'lgan mashina nomini kiriting (aniq nom):\n" + ", ".join([car.name for car in cars])
        await safe_answer(text)
        await state.set_state(AdminStates.del_car)
    elif callback.data == "admin_list_car":
        cars = await sync_to_async(list)(Car.objects.all())
        if not cars:
            await safe_answer("Mashinalar ro'yxati bo'sh.")
        else:
            await safe_answer("Mashinalar ro'yxati:\n" + ", ".join([car.name for car in cars]))
    elif callback.data == "admin_add_route":
        await safe_answer("Yangi marshrut nomini kiriting:")
        await state.set_state(AdminStates.add_route)
    elif callback.data == "admin_del_route":
        routes = await sync_to_async(list)(Route.objects.all())
        if not routes:
            await safe_answer("Marshrutlar ro'yxati bo'sh.")
            return
        text = "O'chirmoqchi bo'lgan marshrut nomini kiriting (aniq nom):\n" + ", ".join([route.name for route in routes])
        await safe_answer(text)
        await state.set_state(AdminStates.del_route)
    elif callback.data == "admin_list_route":
        routes = await sync_to_async(list)(Route.objects.all())
        if not routes:
            await safe_answer("Marshrutlar ro'yxati bo'sh.")
        else:
            await safe_answer("Marshrutlar ro'yxati:\n" + ", ".join([route.name for route in routes]))

@router.message(AdminStates.add_car)
async def admin_add_car(message: Message, state: FSMContext):
    car_name = message.text.strip()
    if not car_name:
        await message.answer("Mashina nomi bo'sh bo'lishi mumkin emas.")
        return
    
    car, created = await sync_to_async(Car.objects.get_or_create)(name=car_name)
    if created:
        await message.answer(f"Mashina '{car_name}' qo'shildi!")
    else:
        await message.answer(f"Mashina '{car_name}' allaqachon mavjud.")
    
    await state.clear()

@router.message(AdminStates.del_car)
async def admin_del_car(message: Message, state: FSMContext):
    car_name = message.text.strip()
    try:
        car = await sync_to_async(Car.objects.get)(name=car_name)
        await sync_to_async(car.delete)()
        await message.answer(f"Mashina '{car_name}' o'chirildi!")
    except Car.DoesNotExist:
        await message.answer(f"Mashina '{car_name}' topilmadi.")
    
    await state.clear()

@router.message(AdminStates.add_route)
async def admin_add_route(message: Message, state: FSMContext):
    route_name = message.text.strip()
    if not route_name:
        await message.answer("Marshrut nomi bo'sh bo'lishi mumkin emas.")
        return
    
    route, created = await sync_to_async(Route.objects.get_or_create)(name=route_name)
    if created:
        await message.answer(f"Marshrut '{route_name}' qo'shildi!")
    else:
        await message.answer(f"Marshrut '{route_name}' allaqachon mavjud.")
    
    await state.clear()

@router.message(AdminStates.del_route)
async def admin_del_route(message: Message, state: FSMContext):
    route_name = message.text.strip()
    try:
        route = await sync_to_async(Route.objects.get)(name=route_name)
        await sync_to_async(route.delete)()
        await message.answer(f"Marshrut '{route_name}' o'chirildi!")
    except Route.DoesNotExist:
        await message.answer(f"Marshrut '{route_name}' topilmadi.")
    
    await state.clear()

# --- FORM HANDLERS ---
@router.callback_query(Form.direction)
async def choose_direction(callback: CallbackQuery, state: FSMContext):
    direction = callback.data
    await state.update_data(direction=direction)
    await callback.message.edit_text(
        f"Sana tanlang:\n\n<code>YYYY-MM-DD</code>\n\nYilni tanlang:",
        reply_markup=get_year_kb(),
        parse_mode="HTML"
    )
    await state.set_state(Form.year)
    await callback.answer()

@router.callback_query(Form.year)
async def choose_year(callback: CallbackQuery, state: FSMContext):
    year = int(callback.data.split('_')[1])
    await state.update_data(year=year)
    text = f"Sana tanlang:\n\n<code>{year}-MM-DD</code>\n\nOy tanlang:"
    await callback.message.edit_text(
        text,
        reply_markup=get_month_kb(year),
        parse_mode="HTML"
    )
    await state.set_state(Form.month)
    await callback.answer()

@router.callback_query(Form.month)
async def choose_month(callback: CallbackQuery, state: FSMContext):
    month = int(callback.data.split('_')[1])
    data = await state.get_data()
    year = data.get('year')
    months = [
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
    ]
    await state.update_data(month=month)
    text = f"Sana tanlang:\n\n<code>{year}-{month:02d}-DD</code>\n\nKun tanlang:"
    await callback.message.edit_text(
        text,
        reply_markup=get_day_kb(year, month),
        parse_mode="HTML"
    )
    await state.set_state(Form.day)
    await callback.answer()

@router.callback_query(Form.day)
async def choose_day(callback: CallbackQuery, state: FSMContext):
    day = int(callback.data.split('_')[1])
    data = await state.get_data()
    year = data.get('year')
    month = data.get('month')
    await state.update_data(day=day)
    date_str = f"{year}-{month:02d}-{day:02d}"
    await state.update_data(date=date_str)
    await callback.message.edit_text(
        f"✅ Tanlangan sana: <b>{date_str}</b>",
        parse_mode="HTML"
    )
    await callback.message.answer("Telefon raqamingizni kiriting (+998XXXXXXXXX):")
    await state.set_state(Form.phone)
    await callback.answer()

@router.message(Form.direction)
async def block_text(message: Message):
    await message.answer("Iltimos, tugmalardan foydalaning!")

@router.message(Form.date)
async def enter_date(message: Message, state: FSMContext):
    date_text = message.text.strip()
    if not is_valid_date(date_text):
        await message.answer("Noto'g'ri sana format. Iltimos, YYYY-MM-DD formatida kiriting.")
        return
    
    await state.update_data(date=date_text)
    await message.answer("Telefon raqamingizni kiriting (+998XXXXXXXXX):")
    await state.set_state(Form.phone)

@router.message(Form.phone)
async def enter_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not is_valid_phone(phone):
        await message.answer("Noto'g'ri telefon raqam. Iltimos, +998XXXXXXXXX formatida kiriting.")
        return
    
    await state.update_data(phone=phone)
    await message.answer("Sayohat turini tanlang:", reply_markup=get_trip_type_kb())
    await state.set_state(Form.trip_type)

@router.callback_query(Form.trip_type)
async def choose_type(callback: CallbackQuery, state: FSMContext):
    trip_type = callback.data
    await state.update_data(trip_type=trip_type)
    # Edit the message to show the selected trip type
    trip_type_text = "Odam" if trip_type == 'person' else "Pochta"
    await callback.message.edit_text(f"✅ Tanlangan tur: {trip_type_text}")
    # Send next step
    await callback.message.answer("Mashinani tanlang:", reply_markup=await get_car_kb())
    await state.set_state(Form.car)
    await callback.answer()

@router.message(Form.trip_type)
async def block_trip_type(message: Message):
    await message.answer("Iltimos, tugmalardan foydalaning!")

@router.callback_query(Form.car)
async def choose_car(callback: CallbackQuery, state: FSMContext):
    car = callback.data
    await state.update_data(car=car)
    # Edit the message to show the selected car
    await callback.message.edit_text(f"✅ Tanlangan mashina: {car}")
    # Send next step
    await callback.message.answer("Qayerdan olib ketish kerak? Manzilingizni aniq yozing.")
    await state.set_state(Form.address)
    await callback.answer()

@router.message(Form.car)
async def block_car_text(message: Message):
    await message.answer("Iltimos, tugmalardan foydalaning!")

@router.message(Form.address)
async def enter_address(message: Message, state: FSMContext):
    address = message.text.strip()
    await state.update_data(address=address)
    await message.answer(
        "Izoh kiriting (ixtiyoriy): yoki qo‘shimcha fikringiz bo‘lsa kiriting.",
        reply_markup=get_no_comment_kb()
    )
    await state.set_state(Form.comment)

@router.callback_query(Form.comment, F.data == "no_comment")
async def no_comment_callback(callback: CallbackQuery, state: FSMContext):
    await state.update_data(comment="")
    data = await state.get_data()
    trip_type_text = "Odam" if data['trip_type'] == 'person' else "Pochta"
    summary = f"""
📋 Buyurtma ma'lumotlari:

🚗 Yo'nalish: {data['direction']}
📅 Sana: {data['date']}
📞 Telefon: {data['phone']}
👥 Tur: {trip_type_text}
🚙 Mashina: {data['car']}
📍 Manzil: {data['address']}
💬 Izoh: Yo'q

Tasdiqlaysizmi?
"""
    await callback.message.edit_text(summary, reply_markup=get_confirm_kb())
    await state.set_state(Form.confirm)
    await callback.answer()

@router.message(Form.comment)
async def enter_comment(message: Message, state: FSMContext):
    comment = message.text.strip()
    await state.update_data(comment=comment)
    
    data = await state.get_data()
    
    # Format order summary
    trip_type_text = "Odam" if data['trip_type'] == 'person' else "Pochta"
    
    summary = f"""
📋 Buyurtma ma'lumotlari:

🚗 Yo'nalish: {data['direction']}
📅 Sana: {data['date']}
📞 Telefon: {data['phone']}
👥 Tur: {trip_type_text}
🚙 Mashina: {data['car']}
📍 Manzil: {data['address']}
💬 Izoh: {data['comment'] if data['comment'] else 'Yo\'q'}

Tasdiqlaysizmi?
"""
    
    await message.answer(summary, reply_markup=get_confirm_kb())
    await state.set_state(Form.confirm)

@router.callback_query(Form.confirm, F.data == "confirm")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Remove inline keyboard from the confirmation message
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    # Get user
    user = await sync_to_async(User.objects.get)(user_id=callback.from_user.id)
    
    # Create order
    order = await sync_to_async(Order.objects.create)(
        user=user,
        direction=data['direction'],
        date=data['date'],
        phone=data['phone'],
        trip_type=data['trip_type'],
        car=data['car'],
        address=data['address'],
        comment=data['comment'] if data['comment'] else ''
    )
    
    # Send confirmation to user (without order number)
    await callback.message.answer(
        f"✅ Buyurtma tasdiqlandi!\n\nTez orada siz bilan bog'lanishadi."
    )
    
    # Send notification to admin (with order number)
    try:
        settings = await sync_to_async(BotSettings.objects.first)()
        admin_id = settings.admin_id if settings else None
        if admin_id:
            trip_type_text = "Odam" if data['trip_type'] == 'person' else "Pochta"
            tg_username = getattr(callback.from_user, 'username', None)
            if tg_username:
                user_link = f"<a href='https://t.me/{tg_username}'>{user.full_name}</a>"
            else:
                user_link = f"<a href='tg://user?id={user.user_id}'>{user.full_name}</a>"
            admin_message = f"""
🆕 Yangi buyurtma!

👤 Foydalanuvchi: {user_link}
📞 Telefon: {data['phone']}
🚗 Yo'nalish: {data['direction']}
📅 Sana: {data['date']}
👥 Tur: {trip_type_text}
🚙 Mashina: {data['car']}
📍 Manzil: {data['address']}
💬 Izoh: {data['comment'] if data['comment'] else 'Yo\'q'}

Buyurtma raqami: #{order.id}
"""
            await callback.bot.send_message(admin_id, admin_message, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Error sending admin notification: {e}")
    
    await state.clear()
    await callback.answer()

@router.callback_query(Form.confirm, F.data == "cancel")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Buyurtma bekor qilindi. /start orqali yangidan boshlang.")
    await state.clear()
    await callback.answer()

@router.message(Form.confirm)
async def block_confirm(message: Message):
    await message.answer("Iltimos, tugmalardan foydalaning!")
