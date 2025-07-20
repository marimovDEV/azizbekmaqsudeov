import os
from set_main import models
from aiogram.filters import Filter
from asgiref.sync import sync_to_async
from aiogram.types import Message,FSInputFile
from aiogram.types import Message,FSInputFile,KeyboardButton,ReplyKeyboardMarkup,CallbackQuery

from ..states.user_state import UserStates
from ..keyboards.inline import CreateInline
from ..keyboards.inline import CreateInline,sub_check


class CheckSubChanelCall(Filter):
    async def __call__(self, call: CallbackQuery):
        # Получаем список всех каналов из базы данных
        channels = await sync_to_async(list)(models.ChanelGroup.objects.all())
        unsubscribed_channels = []

        # Проверяем статус подписки для каждого канала
        for channel in channels:
            user_status = await call.bot.get_chat_member(channel.group_id, call.from_user.id)  # Изменено на call.bot
            if user_status.status not in ['creator', 'administrator', "member"]:
                unsubscribed_channels.append((channel.group_name, channel.group_url))

        # Если есть неподписанные каналы, отправляем сообщение
        if unsubscribed_channels:
            await call.bot.send_message(  # Изменено на call.bot
                chat_id=call.from_user.id,
                text='❌ Kechirasiz botimizdan foydalanishdan oldin ushbu канналарга a\'zo bo\'lishingiz kerak.',
                reply_markup=sub_check(unsubscribed_channels)  # Отправляем клавиатуру с кнопками
            )
            return False  # Отклоняем запрос, так как пользователь не подписан на все каналы

        return True


class CheckSubChanel(Filter):
    async def __call__(self, message: Message):
        channels = await sync_to_async(list)(models.ChanelGroup.objects.all())
        unsubscribed_channels = []
        for channel in channels:
            user_status = await message.bot.get_chat_member(channel.group_id, message.from_user.id)
            if user_status.status not in ['creator', 'administrator', "member"]:
                unsubscribed_channels.append((channel.group_name, channel.group_url))
        if unsubscribed_channels:
            await message.bot.send_message(
                chat_id=message.from_user.id,
                text='❌ Kechirasiz botimizdan foydalanishdan oldin ushbu каннallarга a\'zo bo\'lishingiz kerak.',
                reply_markup=sub_check(unsubscribed_channels)
            )
            return False  # Отклоняем сообщение, так как пользователь не подписан на все каналы
        return True

def is_uzbek_number(phone_number):
        return phone_number.startswith('998') and int(phone_number)

class chat_type_filter(Filter):
    def __init__(self,chat_types:list[str]) -> None:
        self.chat_types = chat_types
    async def __call__(self,message:Message) -> bool:
        return message.chat.type in self.chat_types

def photo_filter(photo_field) -> Filter:
    if photo_field and hasattr(photo_field, 'path'):
            photo_path = photo_field.path
            if os.path.exists(photo_path):
                photo = FSInputFile(photo_path)
    return photo

async def send_bot_message(bot, chat_id, command, state_name=None, state=None,bot_text1=None):
    bot_message = await sync_to_async(models.BotMessage.objects.get)(command=command)
    if command == 'correct' and bot_text1:
        bot_text = bot_message.text.format(
            fullname=bot_text1.get('full_name', ''),
            contact=bot_text1.get('contact', ''),
        )
    else:
        bot_text = bot_message.text
    if command == 'contact':
        buttons_data = await sync_to_async(list)(bot_message.reply.all())
        if buttons_data:
            buttons = [[KeyboardButton(text=btn.text, request_contact=True) for btn in buttons_data]]
            keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
        else:
            keyboard = None
    else:
        buttons_data = await sync_to_async(list)(bot_message.inline.all())
        keyboard = CreateInline(buttons_data) if buttons_data else None
    if bot_message:
        if bot_message.photo:
            sent_message = await bot.send_photo(
                chat_id,
                photo=photo_filter(bot_message.photo),
                caption=bot_text,
                reply_markup=keyboard
            )
        else:
            sent_message = await bot.send_message(
                chat_id,
                bot_text,
                reply_markup=keyboard
            )
        if state_name and state:
            state_value = getattr(UserStates, state_name, None)  # Получаем состояние по имени
            if state_value:
                await state.set_state(state_value)  # Устанавливаем новое состояние
        return sent_message.message_id
    return None