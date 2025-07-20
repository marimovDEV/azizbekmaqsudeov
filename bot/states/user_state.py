from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    add_car = State()
    del_car = State()
    add_route = State()
    del_route = State()

class Form(StatesGroup):
    direction = State()
    year = State()
    month = State()
    day = State()
    date = State()
    phone = State()
    trip_type = State()
    car = State()
    address = State()
    comment = State()
    confirm = State()