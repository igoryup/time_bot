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

import common.schedule

msk_offset = timedelta(hours=3)
msk_tz = timezone(msk_offset)

class DeltaTemplate(Template):
    delimiter = "%"

def strfdelta(tdelta, fmt):
    # Получаем общее количество дней
    d = {"D": tdelta.days}
    
    # Получаем общее количество часов, включая полные дни
    total_seconds = tdelta.total_seconds()
    hours = total_seconds // 3600  # Общее количество часов
    rem_seconds = total_seconds % 3600
    minutes = rem_seconds // 60
    seconds = rem_seconds % 60
    
    # Форматируем значения для словаря
    d["H"] = '{:d}'.format(int(hours))  # Часы без форматирования в 2 символа
    d["M"] = '{:02d}'.format(int(minutes))
    d["S"] = '{:02d}'.format(int(seconds))
    
    # Используем шаблон для замены
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

users_schedule = {}

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))

USER_KB = get_keyboard(
    "Начать день",
    "Отчет за неделю",
    placeholder="Выберите действие",
    sizes=(1, 1)
)

USER_EXT_KB = get_keyboard(
    "Проверить время",
    "Закончить день",
    "Отчет за неделю",
    placeholder="Выберите действие",
    sizes=(1, 2)
)

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id 
    sch = common.schedule.WeeklySchedule()
    sch.update_week()
    # key = {user_id, common.schedule.getCurWeek()}
    key = str(user_id) + str(common.schedule.getCurWeek())
    users_schedule[key] = sch
    await message.answer(
        "Привет, я виртуальный помощник",
        reply_markup=USER_KB
    )

@user_private_router.message(or_f(Command("Начать день"), (F.text.lower() == "начать день")))
async def begin_cmd(message: types.Message):
    user_id = message.from_user.id   
    # key = {user_id, common.schedule.getCurWeek()}
    key = str(user_id) + str(common.schedule.getCurWeek())
    sched = users_schedule[key]
    timestamp = common.schedule.getCurTime()
    sched.set_start_time_for_today(timestamp)
    work_time = timestamp.strftime("%H:%M:%S")
    await message.reply(f"Время начала работы зафиксировано:\n\n<b>{work_time}</b>", reply_markup=USER_EXT_KB)
    # Задержка на 8 часов
    delay_hours = 8
    delay_seconds = delay_hours * 3600
    await asyncio.sleep(delay_seconds)
    await message.reply(f"Время прошло, пора бы домой!", reply_markup=USER_EXT_KB)

        
@user_private_router.message(or_f(Command("Проверить время"), (F.text.lower() == "проверить время")))
async def check_cmd(message: types.Message):
    user_id = message.from_user.id    
    # key = {user_id, common.schedule.getCurWeek()}
    key = str(user_id) + str(common.schedule.getCurWeek())
    sched = users_schedule[key]
    start_time = sched.get_today_schedule()[0]
    end_time = common.schedule.getCurTime()
    duration = end_time - start_time
    work_time = common.schedule.strfdelta(duration, '%H:%M:%S')
    await message.reply(f"На текущий момент Вы проработали:\n\n<b>{work_time}</b>.")

@user_private_router.message(or_f(Command("Закончить день"), (F.text.lower() == "закончить день")))
async def end_cmd(message: types.Message):
    user_id = message.from_user.id
    # key = {user_id, common.schedule.getCurWeek()}
    key = str(user_id) + str(common.schedule.getCurWeek())
    sched = users_schedule[key]
    start_time = sched.get_today_schedule()[0]
    end_time = common.schedule.getCurTime()
    duration = end_time - start_time
    sched.set_end_time_for_today(end_time)
    work_time = strfdelta(duration, '%H:%M:%S')
    end_time = end_time.strftime("%H:%M:%S")
    # await message.reply("Вы закончили работать.")
    await message.reply(f"Рабочее время завершено.\n\nВремя окончания работы зафиксировано:\n\n<b>{end_time}</b>.\n\nВы проработали:\n\n<b>{work_time}</b>.", reply_markup=USER_KB)

@user_private_router.message(or_f(Command("Отчет за неделю"), (F.text.lower() == "отчет за неделю")))
async def check_cmd(message: types.Message):
    user_id = message.from_user.id
    # key = {user_id, common.schedule.getCurWeek()}
    key = str(user_id) + str(common.schedule.getCurWeek())
    sched = users_schedule[key]
    mon = sched.get_schedule_for_day("Monday")
    tue = sched.get_schedule_for_day("Tuesday")
    wed = sched.get_schedule_for_day("Wednesday")
    thu = sched.get_schedule_for_day("Thursday")
    fri = sched.get_schedule_for_day("Friday")
    sat = sched.get_schedule_for_day("Saturday")
    sun = sched.get_schedule_for_day("Sunday")
    mon_dur = mon[1] - mon[0] if mon[1] - mon[0] > timedelta(0) else timedelta(0)
    tue_dur = tue[1] - tue[0] if tue[1] - tue[0] > timedelta(0) else timedelta(0)
    wed_dur = wed[1] - wed[0] if wed[1] - wed[0] > timedelta(0) else timedelta(0)
    thu_dur = thu[1] - thu[0] if thu[1] - thu[0] > timedelta(0) else timedelta(0)
    fri_dur = fri[1] - fri[0] if fri[1] - fri[0] > timedelta(0) else timedelta(0)
    sat_dur = sat[1] - sat[0] if sat[1] - sat[0] > timedelta(0) else timedelta(0)
    sun_dur = sun[1] - sun[0] if sun[1] - sun[0] > timedelta(0) else timedelta(0)
    total = mon_dur + tue_dur + wed_dur + thu_dur + fri_dur + sat_dur + sun_dur
    total = strfdelta(total, '%H:%M:%S')
    text = f"За текущую неделю вы отработали {total}."
    mon_time = f"Понедельник: {strfdelta(mon_dur, '%H:%M:%S')}"
    tue_time = f"Вторник: {strfdelta(tue_dur, '%H:%M:%S')}"
    wed_time = f"Среда: {strfdelta(wed_dur, '%H:%M:%S')}"
    thu_time = f"Четверг: {strfdelta(thu_dur, '%H:%M:%S')}"
    fri_time = f"Пятница: {strfdelta(fri_dur, '%H:%M:%S')}"
    sat_time = f"Суббота: {strfdelta(sat_dur, '%H:%M:%S')}"
    sun_time = f"Воскресенье: {strfdelta(sun_dur, '%H:%M:%S')}"
    text += '\n' + '\n' + mon_time + '\n' + tue_time + '\n' + wed_time + '\n' + thu_time + '\n' + fri_time + '\n' + sat_time + '\n' + sun_time
    await message.reply(text)