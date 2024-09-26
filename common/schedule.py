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

def getCurTime():
    return datetime.now(msk_tz)

def getCurTimeFormat():
    return datetime.now(msk_tz).strftime("%H:%M:%S")

class WeeklySchedule:
    def __init__(self):
        # Инициализируем расписание текущим временем для всех дней недели
        current_time = getCurTime()
        self.schedule = {
            "Monday": (current_time, current_time),
            "Tuesday": (current_time, current_time),
            "Wednesday": (current_time, current_time),
            "Thursday": (current_time, current_time),
            "Friday": (current_time, current_time),
            "Saturday": (current_time, current_time),
            "Sunday": (current_time, current_time)
        }

    def get_today(self):
        # Получаем текущий день недели на английском
        return datetime.today().strftime('%A')

    def get_schedule_for_day(self, day) -> datetime:
        # Получаем расписание для конкретного дня недели
        return self.schedule.get(day, (getCurTime(), getCurTime()))

    def get_today_schedule(self):
        # Получаем расписание для текущего дня недели
        today = self.get_today()
        return self.get_schedule_for_day(today)

    def set_start_time_for_today(self, start_time):
        # Устанавливаем время начала работы для текущего дня
        today = self.get_today()
        end_time = self.schedule[today][1]  # Сохраняем текущее время окончания
        self.schedule[today] = (start_time, end_time)

    def set_end_time_for_today(self, end_time):
        # Устанавливаем время окончания работы для текущего дня
        today = self.get_today()
        start_time = self.schedule[today][0]  # Сохраняем текущее время начала
        self.schedule[today] = (start_time, end_time)