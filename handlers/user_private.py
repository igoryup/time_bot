from aiogram import F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import (
    as_list,
    as_marked_section,
    Bold,
)  # Italic, as_numbered_list и тд

import asyncio

from filters.chat_types import ChatTypeFilter

from kbds.reply import get_keyboard

from datetime import datetime, timedelta, timezone

from string import Template


msk_offset = timedelta(hours=3)
msk_tz = timezone(msk_offset)

class DeltaTemplate(Template):
    delimiter = "%"

def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = '{:02d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

start_times = {}

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))

USER_KB = get_keyboard(
    "Начать день",
    placeholder="Выберите действие",
    sizes=(1, 0)
)

USER_EXT_KB = get_keyboard(
    "Проверить время",
    "Закончить день",
    placeholder="Выберите действие",
    sizes=(1, 1)
)

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Привет, я виртуальный помощник",
        reply_markup=USER_KB
    )

@user_private_router.message(or_f(Command("Начать день"), (F.text.lower() == "начать день")))
async def begin_cmd(message: types.Message):
    user_id = message.from_user.id    
    if user_id in start_times:
        await message.reply(f"Вы уже отметились!")
    else:
        start_times[user_id] = datetime.now(msk_tz)
        work_time = (start_times[user_id]).strftime("%H:%M:%S")
        work_status = True
        await message.reply(f"Время начала работы зафиксировано:\n\n<b>{work_time}</b>", reply_markup=USER_EXT_KB)

        # Задержка на несколько часов (например, 3 часа)
        delay_hours = 3
        delay_seconds = delay_hours * 3600
        await asyncio.sleep(10)
        if user_id in start_times:
            await message.reply(f"Время прошло, пора бы домой!", reply_markup=USER_EXT_KB)

        
@user_private_router.message(or_f(Command("Проверить время"), (F.text.lower() == "проверить время")))
async def check_cmd(message: types.Message):
    user_id = message.from_user.id    
    if user_id in start_times:
        start_time = start_times[user_id]
        end_time = datetime.now(msk_tz)
        duration = end_time - start_time
        work_time = strfdelta(duration, '%H:%M:%S')
        # await message.reply("Вы закончили работать.")
        await message.reply(f"На текущий момент Вы проработали:\n\n<b>{work_time}</b>.")
    else:
        await message.reply("Вы еще не отметились!")

@user_private_router.message(or_f(Command("Закончить день"), (F.text.lower() == "закончить день")))
async def end_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id in start_times:
        start_time = start_times.pop(user_id)
        end_time = datetime.now(msk_tz)
        duration = end_time - start_time
        end_time = end_time.strftime("%H:%M:%S")
        work_time = strfdelta(duration, '%H:%M:%S')
        # await message.reply("Вы закончили работать.")
        work_status = False
        await message.reply(f"Рабочее время завершено.\n\nВремя окончания работы зафиксировано:\n\n<b>{end_time}</b>.\n\nВы проработали:\n\n<b>{work_time}</b>.", reply_markup=USER_KB)
    else:
        await message.reply("Время начала работы не было зафиксировано.")
