from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async
from set_main.models import Car, Route
import datetime

async def get_direction_kb():
    routes = await sync_to_async(list)(Route.objects.all())
    if not routes:
        # Default routes if db is empty
        default_routes = ["Xorazmdan Buxoroga", "Buxorodan Xorazmga"]
        for route_name in default_routes:
            await sync_to_async(Route.objects.get_or_create)(name=route_name)
        routes = await sync_to_async(list)(Route.objects.all())
    
    buttons = [InlineKeyboardButton(text=route.name, callback_data=route.name) for route in routes]
    return InlineKeyboardMarkup(inline_keyboard=[[b] for b in buttons])

def get_trip_type_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Odam", callback_data="person"),
             InlineKeyboardButton(text="Pochta", callback_data="cargo")]
        ]
    )

async def get_car_kb():
    cars = await sync_to_async(list)(Car.objects.all())
    if not cars:
        # Default cars if db is empty
        default_cars = ["Kaptiva", "Malibu", "Cobalt", "Gentra", "Largus", "Lasetti"]
        for car_name in default_cars:
            await sync_to_async(Car.objects.get_or_create)(name=car_name)
        cars = await sync_to_async(list)(Car.objects.all())
    
    rows = []
    for i in range(0, len(cars), 2):
        row = []
        for j in range(2):
            if i + j < len(cars):
                row.append(InlineKeyboardButton(text=cars[i + j].name, callback_data=cars[i + j].name))
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)

def get_confirm_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
        ]
    )

def get_admin_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Mashina qo'shish", callback_data="admin_add_car")],
            [InlineKeyboardButton(text="➖ Mashina o'chirish", callback_data="admin_del_car")],
            [InlineKeyboardButton(text="🚗 Mashinalar ro'yxati", callback_data="admin_list_car")],
            [InlineKeyboardButton(text="➕ Marshrut qo'shish", callback_data="admin_add_route")],
            [InlineKeyboardButton(text="➖ Marshrut o'chirish", callback_data="admin_del_route")],
            [InlineKeyboardButton(text="🛣 Marshrutlar ro'yxati", callback_data="admin_list_route")]
        ]
    )

def get_no_comment_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Izoh yo‘q", callback_data="no_comment")]
        ]
    )

def get_year_kb():
    now = datetime.datetime.now()
    year1 = now.year
    year2 = now.year + 1
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=str(year1), callback_data=f"year_{year1}")],
            [InlineKeyboardButton(text=str(year2), callback_data=f"year_{year2}")]
        ]
    )

def get_month_kb(selected_year):
    now = datetime.datetime.now()
    months = [
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
    ]
    if selected_year == now.year:
        start_month = now.month
    else:
        start_month = 1
    buttons = []
    for i in range(start_month, 13):
        buttons.append([
            InlineKeyboardButton(text=f"{months[i-1]}", callback_data=f"month_{i:02d}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_day_kb(selected_year, selected_month):
    now = datetime.datetime.now()
    import calendar
    days_in_month = calendar.monthrange(selected_year, selected_month)[1]
    if selected_year == now.year and selected_month == now.month:
        start_day = now.day
    else:
        start_day = 1
    buttons = []
    row = []
    for day in range(start_day, days_in_month + 1):
        row.append(InlineKeyboardButton(text=f"{day:02d}", callback_data=f"day_{day:02d}"))
        if len(row) == 7:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)