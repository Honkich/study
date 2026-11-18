# -*- coding: utf-8 -*-
"""
Telegram-бот для группы ИКТО-2542 (СПбГУТ им. Бонч-Бруевича)
Расписание, сессия, отслеживание долгов и даты пересдач (ноябрь 2026).
"""

import os
import json
import time
import datetime
import threading
import telebot
from telebot import types
from lk_parser import lk_client, BASE_URL

TOKEN = "9235927933:AAFT1RNAeEdS1RHYNSGSE2EwRLOL-5B8Ei4"
WEBAPP_URL = "https://honkich.github.io/study/?v=3"

bot = telebot.TeleBot(TOKEN)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
SUBSCRIBERS_FILE = os.path.join(DATA_DIR, "subscribers.json")
DEBTS_FILE = os.path.join(DATA_DIR, "debts_state.json")

# ==================== ДАННЫЕ ====================

DAYS = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']

SCHEDULE = {
    # 1: Нечётная неделя
    1: {
        1: [
            {"num": 2, "type": "Лекция", "name": "Технологии программирования", "time": "10:45 - 12:20", "room": "Ауд. 110, Б22/1", "teacher": "Дагаев А.В."},
            {"num": 3, "type": "Лекция", "name": "Математические модели в сетях связи", "time": "13:00 - 14:35", "room": "Ауд. 106, Б22/1", "teacher": "Гришин И.В."},
            {"num": "ФЗ", "type": "Практика", "name": "Физ. культура и спорт", "time": "15:00 - 16:30", "room": "СК Динамит, Ч13В", "teacher": "Сапсаева Т.В."}
        ],
        2: [
            {"num": 1, "type": "Лаб. работа", "name": "Математические модели в сетях связи", "time": "09:00 - 10:35", "room": "Ауд. 417, Б22/2", "teacher": "Лобастова М.В."},
            {"num": 2, "type": "Лаб. работа", "name": "Основы защиты информации в ТКС", "time": "10:45 - 12:20", "room": "Ауд. 504, Б22/1", "teacher": "Шемякин С.Н."}
        ],
        3: [
            {"num": 1, "type": "Практика", "name": "Материалы электронной техники", "time": "09:00 - 10:35", "room": "Ауд. 413, Б22/1", "teacher": "Арсирий А.И.", "note": "13-я неделя"},
            {"num": 2, "type": "Лекция", "name": "Физика (спецглавы)", "time": "10:45 - 12:20", "room": "Ауд. 704, Б22/1", "teacher": "Урванцева Н.Л."},
            {"num": 3, "type": "Практика", "name": "Электропитание устройств и систем ТК", "time": "13:00 - 14:35", "room": "Ауд. 406, Б22/2", "teacher": "Виноградов П.Ю."},
            {"num": 4, "type": "Лаб. работа", "name": "Физика (спецглавы)", "time": "14:45 - 16:20", "room": "Ауд. 317, Б22/1", "teacher": "Урванцева Н.Л."},
            {"num": 5, "type": "Практика", "name": "Многоканальные ТК системы", "time": "16:30 - 18:05", "room": "Ауд. 447, Б22/2", "teacher": "Герасимов А.М."}
        ],
        4: [
            {"num": 1, "type": "Лаб. работа", "name": "Электроника", "time": "09:00 - 10:35", "room": "Ауд. 446, Б22/1", "teacher": "Ланда А.Э."},
            {"num": 2, "type": "Лекция", "name": "Электроника", "time": "10:45 - 12:20", "room": "Ауд. 112, Б22/1", "teacher": "Ланда А.Э."},
            {"num": 3, "type": "Лекция", "name": "Многоканальные ТК системы", "time": "13:00 - 14:35", "room": "Ауд. 112, Б22/1", "teacher": "Матюхин А.Ю."},
            {"num": "ФЗ", "type": "Практика", "name": "Физ. культура и спорт", "time": "15:00 - 16:30", "room": "СК Динамит, Ч13В", "teacher": "Сапсаева Т.В."}
        ],
        5: [],
        6: [
            {"num": 1, "type": "Лаб. работа", "name": "Технологии программирования", "time": "09:00 - 10:35", "room": "Ауд. 515, Б22/2", "teacher": "Дагаев А.В."},
            {"num": 2, "type": "Практика", "name": "Теория вероятностей и мат. статистика", "time": "10:45 - 12:20", "room": "Ауд. 511, Б22/2", "teacher": "Воронова М.В."},
            {"num": 3, "type": "Практика", "name": "Теория вероятностей и мат. статистика", "time": "13:00 - 14:35", "room": "Ауд. 511, Б22/2", "teacher": "Воронова М.В."}
        ]
    },
    # 2: Чётная неделя
    2: {
        1: [
            {"num": 1, "type": "Практика", "name": "Технологии программирования", "time": "09:00 - 10:35", "room": "Ауд. 233, Б22/2", "teacher": "Дагаев А.В."},
            {"num": 2, "type": "Лекция", "name": "Основы защиты информации в ТКС", "time": "10:45 - 12:20", "room": "Ауд. 110, Б22/1", "teacher": "Бабков И.Н."}
        ],
        2: [
            {"num": 1, "type": "Практика", "name": "Математические модели в сетях связи", "time": "09:00 - 10:35", "room": "Ауд. 417, Б22/2", "teacher": "Лобастова М.В."},
            {"num": 2, "type": "Практика", "name": "Основы защиты информации в ТКС", "time": "10:45 - 12:20", "room": "Ауд. 504, Б22/1", "teacher": "Шемякин С.Н."},
            {"num": 3, "type": "Практика", "name": "Электроника", "time": "13:00 - 14:35", "room": "Ауд. 446, Б22/1", "teacher": "Ланда А.Э."},
            {"num": 4, "type": "Лаб. работа", "name": "Материалы электронной техники", "time": "14:45 - 16:20", "room": "Ауд. 413, Б22/1", "teacher": "Арсирий А.И."}
        ],
        3: [
            {"num": 3, "type": "Лаб. работа", "name": "Электропитание устройств и систем ТК", "time": "13:00 - 14:35", "room": "Ауд. 406, Б22/2", "teacher": "Копылова И.В."},
            {"num": 4, "type": "Практика", "name": "Физика (спецглавы)", "time": "14:45 - 16:20", "room": "Ауд. 301, Б22/1", "teacher": "Урванцева Н.Л."},
            {"num": 5, "type": "Лаб. работа", "name": "Многоканальные ТК системы", "time": "16:30 - 18:05", "room": "Ауд. 447, Б22/2", "teacher": "Герасимов А.М."}
        ],
        4: [
            {"num": 1, "type": "Лекция", "name": "Электропитание устройств и систем ТК", "time": "09:00 - 10:35", "room": "Ауд. 106, Б22/1", "teacher": "Виноградов П.Ю."},
            {"num": 2, "type": "Лекция", "name": "Теория вероятностей и мат. статистика", "time": "10:45 - 12:20", "room": "Ауд. 106, Б22/1", "teacher": "Камартина Н.М."},
            {"num": 3, "type": "Лекция", "name": "Материалы электронной техники", "time": "13:00 - 14:35", "room": "Ауд. 106, Б22/1", "teacher": "Арсирий А.И."},
            {"num": "ФЗ", "type": "Практика", "name": "Физ. культура и спорт", "time": "15:00 - 16:30", "room": "СК Динамит, Ч13В", "teacher": "Сапсаева Т.В."}
        ],
        5: [],
        6: []
    }
}

DEFAULT_DEBTS = [
    {
        "id": "d1",
        "subject": "Физические основы электроники (ФОЭ)",
        "dept": "Кафедра электроники",
        "dates": ["12.11 (прошла)", "17.11 (прошла)", "19.11 10:45–14:00 (ауд. 306/1)", "26.11 10:45–14:00 (ауд. 306/1)"],
        "next_date": "2026-11-19",
        "next_time": "10:45 - 14:00",
        "next_room": "Ауд. 306/1",
        "pdf": "https://www.sut.ru/doci/umu/peresdacha/2/84.pdf"
    },
    {
        "id": "d2",
        "subject": "Физическая культура",
        "dept": "Кафедра физической культуры",
        "dates": ["12.11 (прошла)", "16.11 (прошла)", "27.11 09:00–15:00 (СК «Динамит»)"],
        "next_date": "2026-11-27",
        "next_time": "09:00 - 15:00",
        "next_room": "СК «Динамит»",
        "pdf": "https://www.sut.ru/doci/umu/peresdacha/2/75.pdf"
    },
    {
        "id": "d3",
        "subject": "Физика",
        "dept": "Кафедра физики",
        "dates": ["16.11 (прошла)", "23.11 12:30–14:45 (ауд. 311/1)", "30.11 12:30–14:45 (ауд. 311/1)"],
        "next_date": "2026-11-23",
        "next_time": "12:30 - 14:45",
        "next_room": "Ауд. 311/1",
        "pdf": "https://www.sut.ru/doci/umu/peresdacha/2/82.pdf"
    },
    {
        "id": "d4",
        "subject": "Иностранный язык",
        "dept": "Кафедра иностранных языков (тех. секция)",
        "dates": ["10.11 (прошла)", "17.11 (прошла)", "24.11 16:30–19:00 (ауд. 317/2)"],
        "next_date": "2026-11-24",
        "next_time": "16:30 - 19:00",
        "next_room": "Ауд. 317/2",
        "pdf": "https://www.sut.ru/doci/umu/peresdacha/2/42.pdf"
    },
    {
        "id": "d5",
        "subject": "Организация и управление предприятиями",
        "dept": "Кафедра экономики данных",
        "dates": ["10.11 (прошла)", "17.11 (прошла)", "24.11 14:45–18:05 (ауд. 338/1)"],
        "next_date": "2026-11-24",
        "next_time": "14:45 - 18:05",
        "next_room": "Ауд. 338/1",
        "pdf": "https://www.sut.ru/doci/umu/peresdacha/2/67.pdf"
    },
    {
        "id": "d6",
        "subject": "Компоненты электронной техники (КЭТ)",
        "dept": "Кафедра КПРЭС",
        "dates": ["10.11 (прошла)", "16.11 (прошла)", "23.11 12:30–16:30 (ауд. 425/1)", "30.11 12:30–16:30 (ауд. 425/1)"],
        "next_date": "2026-11-23",
        "next_time": "12:30 - 16:30",
        "next_room": "Ауд. 425/1",
        "pdf": "https://www.sut.ru/doci/umu/peresdacha/2/72.pdf"
    },
    {
        "id": "d7",
        "subject": "Дискретная математика",
        "dept": "Кафедра высшей математики",
        "dates": ["18.11 09:00–12:30 (ауд. 112/1, РСР) — СЕГОДНЯ!", "27.11 09:00–12:30 (ауд. 707/1, ИКСС)"],
        "next_date": "2026-11-18",
        "next_time": "09:00 - 12:30",
        "next_room": "Ауд. 112/1 (РСР) / 27.11 ауд. 707/1 (ИКСС)",
        "pdf": "https://www.sut.ru/doci/umu/peresdacha/2/79.pdf"
    }
]

# ==================== ХРАНИЛИЩЕ ====================

def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        try:
            with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_subscriber(chat_id):
    subs = load_subscribers()
    if chat_id not in subs:
        subs.add(chat_id)
        with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(subs), f, ensure_ascii=False)

def load_debts_state():
    if os.path.exists(DEBTS_FILE):
        try:
            with open(DEBTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    state = {d["id"]: False for d in DEFAULT_DEBTS}
    save_debts_state(state)
    return state

def save_debts_state(state):
    with open(DEBTS_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_current_week_type():
    now = datetime.datetime.now()
    start = datetime.datetime(now.year, 1, 1)
    week_num = int((now - start).days / 7) + 1
    return 1 if (week_num % 2 == 1) else 2

# ==================== КЛАВИАТУРЫ ====================

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_app = types.KeyboardButton("📱 Открыть Mini App", web_app=types.WebAppInfo(url=WEBAPP_URL))
    btn_today = types.KeyboardButton("📅 Пары сегодня")
    btn_debts = types.KeyboardButton("🎓 Долги и сессия")
    btn_retakes = types.KeyboardButton("🔄 Пересдачи")
    btn_messages = types.KeyboardButton("📬 Сообщения ЛК")
    btn_files = types.KeyboardButton("📁 Файлы группы")
    markup.row(btn_app)
    markup.row(btn_today, btn_debts)
    markup.row(btn_messages, btn_files)
    markup.row(btn_retakes)
    return markup

def get_debts_inline():
    state = load_debts_state()
    markup = types.InlineKeyboardMarkup()
    for d in DEFAULT_DEBTS:
        is_passed = state.get(d["id"], False)
        status_icon = "✅" if is_passed else "❌"
        btn_text = f"{status_icon} {d['subject'][:28]}..."
        callback = f"toggle_debt_{d['id']}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=callback))
    markup.add(types.InlineKeyboardButton("📱 Открыть в Mini App", web_app=types.WebAppInfo(url=WEBAPP_URL)))
    return markup

# ==================== ОБРАБОТЧИКИ ====================

@bot.message_handler(commands=['start'])
def handle_start(message):
    save_subscriber(message.chat.id)
    text = (
        "👋 **Привет! Я твой помощник по учёбе**\n"
        "🏛 **СПбГУТ им. проф. М.А. Бонч-Бруевича**\n"
        "👥 Группа: **ИКТО-2542**\n\n"
        "Я умею:\n"
        "• Показывать актуальное расписание пар\n"
        "• Напоминать о комиссиях и пересдачах (10–30 ноября)\n"
        "• Отслеживать долги и сессию\n"
        "• Запускать Telegram Mini App с полным функционалом\n\n"
        "Нажми кнопку ниже, чтобы открыть приложение 👇"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def handle_help(message):
    text = (
        "ℹ️ **Доступные команды:**\n\n"
        "/start — Главное меню и запуск приложения\n"
        "/today — Расписание занятий на сегодня\n"
        "/debts — Список долгов с отметками сдачи\n"
        "/retakes — Календарь пересдач комиссиям (ноябрь 2026)\n"
        "/messages — Сообщения и объявления из ЛК СПбГУТ\n"
        "/files — Файлы группы и методические указания из ЛК\n"
        "/sync — Принудительно обновить данные из ЛК прямо сейчас\n"
        "/lk_login — Привязать логин и пароль от lk.sut.ru\n"
        "/lk — Статус привязки Личного кабинета\n\n"
        "💡 **Офлайн-режим:** Когда серверы lk.sut.ru выключают на ночь, бот выдаёт все сохранённые файлы и сообщения из кэша!"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.message_handler(commands=['lk'])
def handle_lk_status(message):
    chat_id = message.chat.id
    creds = lk_client.load_creds(chat_id)
    cache = lk_client.load_cache(chat_id)
    last_sync = cache.get("last_sync_time", "Никогда")

    if creds:
        login_masked = creds['login'][:3] + "***" if len(creds['login']) > 3 else "***"
        text = (
            f"🏛 **Личный кабинет студента (lk.sut.ru)**\n\n"
            f"• Статус: ✅ **Привязан** (логин: `{login_masked}`)\n"
            f"• Последняя синхронизация: `{last_sync}`\n"
            f"• Сообщений в кэше: {len(cache.get('messages', []))}\n"
            f"• Файлов группы: {len(cache.get('files', []))}\n\n"
            f"Используйте /sync для обновления или /messages для просмотра."
        )
    else:
        text = (
            "🏛 **Личный кабинет студента (lk.sut.ru)**\n\n"
            "• Статус: ⚠️ **Не привязан**\n\n"
            "Чтобы бот автоматически забирал ДЗ, объявления и файлы группы:\n"
            "Отправьте команду:\n"
            "`/lk_login логин пароль`\n\n"
            "*(Данные хранятся на твоем компьютере. Днём бот автоматически скачивает всё в кэш, а ночью выдаёт файлы даже при выключенных серверах СПбГУТ!)*"
        )
    bot.send_message(chat_id, text, parse_mode="Markdown")

@bot.message_handler(commands=['lk_login'])
def handle_lk_login(message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(
            message.chat.id,
            "⚠️ Формат команды:\n`/lk_login твой_логин твой_пароль`\n\n"
            "Пример:\n`/lk_login ivanov_ii pass12345`\n\n"
            "*(После сохранения сообщение с паролем рекомендуется удалить ради безопасности)*",
            parse_mode="Markdown"
        )
        return

    login = parts[1].strip()
    password = parts[2].strip()
    lk_client.save_creds(message.chat.id, login, password)

    # Пробуем сразу сделать синхронизацию
    sync_res = lk_client.try_sync(message.chat.id)

    reply = (
        "✅ **Учётные данные lk.sut.ru сохранены!**\n\n"
        f"Статус проверки: {sync_res['msg']}\n\n"
        "Теперь ты можешь смотреть сообщения через /messages и файлы через /files."
    )
    bot.send_message(message.chat.id, reply, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.message_handler(commands=['messages'])
def handle_messages(message):
    res = lk_client.try_sync(message.chat.id)
    cache = res['data']
    messages = cache.get("messages", [])

    header = "📬 **Сообщения и объявления из ЛК СПбГУТ:**\n\n"
    if not res.get("server_online", False):
        header += "*(Офлайн-кэш: сервер ЛК сейчас недоступен/спит, показаны сохранённые данные)*\n\n"

    if not messages:
        header += "Новых сообщений нет."
    else:
        items = []
        for m in messages:
            item = (
                f"📌 **{m['title']}**\n"
                f"👤 {m['sender']} · 🕒 {m['date']}\n"
                f"{m['text']}"
            )
            items.append(item)
        header += "\n\n──────────────────\n\n".join(items)

    bot.send_message(message.chat.id, header, parse_mode="Markdown")

@bot.message_handler(commands=['files'])
def handle_files(message):
    res = lk_client.try_sync(message.chat.id)
    cache = res['data']
    files = cache.get("files", [])

    header = "📁 **Учебные материалы и файлы группы (lk.sut.ru):**\n\n"
    if not res.get("server_online", False):
        header += "*(Офлайн-кэш: сохранённые файлы доступны даже ночью)*\n\n"

    if not files:
        header += "Файлов не найдено."
    else:
        items = []
        for f in files:
            item = (
                f"📄 **{f['name']}**\n"
                f"• Преподаватель: {f.get('author', 'Кафедра')}\n"
                f"• Размер: {f.get('size', '—')} · Дата: {f.get('date', '—')}\n"
                f"• [Скачать из ЛК]({f.get('url', BASE_URL)})"
            )
            items.append(item)
        header += "\n\n".join(items)

    bot.send_message(message.chat.id, header, parse_mode="Markdown", disable_web_page_preview=True)

@bot.message_handler(commands=['sync'])
def handle_sync(message):
    res = lk_client.try_sync(message.chat.id)
    text = (
        f"🔄 **Результат синхронизации с lk.sut.ru:**\n\n"
        f"• {res['msg']}\n"
        f"• Время: {datetime.datetime.now().strftime('%H:%M:%S')}"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['week'])
def handle_week(message):
    w = get_current_week_type()
    w_name = "НЕЧЁТНАЯ (нижняя)" if w == 1 else "ЧЁТНАЯ (верхняя)"
    text = f"📌 Сейчас идёт **{w_name}** неделя."
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['today'])
def handle_today(message):
    now = datetime.datetime.now()
    dow = now.isoweekday()  # 1..7 (1=Mon)
    w = get_current_week_type()
    day_name = DAYS[now.weekday() + 1 if now.weekday() < 6 else 0]

    lessons = SCHEDULE.get(w, {}).get(dow, [])
    w_label = "нечётная" if w == 1 else "чётная"

    header = f"📅 **Пары на сегодня** ({day_name}, {w_label} неделя):\n\n"

    if dow == 5:
        text = header + "📖 **Пятница — день самостоятельной работы!** Пар нет."
    elif not lessons:
        text = header + "🎉 Сегодня пар нет, можно отдохнуть!"
    else:
        items = []
        for l in lessons:
            item = (
                f"**{l['num']} пара** ({l['time']})\n"
                f"• {l['type']}: **{l['name']}**\n"
                f"• 📍 {l['room']}\n"
                f"• 👤 {l.get('teacher', '')}"
            )
            items.append(item)
        text = header + "\n\n".join(items)

    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['debts'])
def handle_debts(message):
    state = load_debts_state()
    now_date = datetime.date.today()

    lines = ["🎓 **Мои академические задолженности (сессия):**\n"]
    for d in DEFAULT_DEBTS:
        is_passed = state.get(d["id"], False)
        status = "✅ **СДАНО**" if is_passed else "❌ **НЕ СДАНО**"

        dt = datetime.datetime.strptime(d["next_date"], "%Y-%m-%d").date()
        diff = (dt - now_date).days
        if diff < 0:
            diff_str = "Прошла (см. другие даты)"
        elif diff == 0:
            diff_str = "🚨 **СЕГОДНЯ!**"
        elif diff == 1:
            diff_str = "⚠️ **ЗАВТРА!**"
        else:
            diff_str = f"через {diff} дн."

        lines.append(
            f"**{d['subject']}** — {status}\n"
            f"• Ближайшая комиссия: **{dt.strftime('%d.%m')}** ({diff_str})\n"
            f"• Время/Ауд: {d['next_time']}, {d['next_room']}\n"
            f"• [📄 Официальное расписание PDF]({d['pdf']})\n"
        )

    lines.append("Нажмите на предмет ниже, чтобы переключить статус (сдано/не сдано):")
    bot.send_message(message.chat.id, "\n".join(lines), reply_markup=get_debts_inline(), parse_mode="Markdown", disable_web_page_preview=True)

@bot.message_handler(commands=['retakes'])
def handle_retakes(message):
    text = (
        "🔄 **Расписание комиссионных пересдач (10–30 ноября 2026):**\n\n"
        "🔴 **18.11 (СЕГОДНЯ!)**\n"
        "• Дискретная математика: 09:00–12:30, ауд. 112/1 (РСР)\n\n"
        "🟡 **19.11 (ЗАВТРА!)**\n"
        "• ФОЭ: 10:45–14:00, ауд. 306/1\n\n"
        "📅 **23.11**\n"
        "• Физика: 12:30–14:45, ауд. 311/1\n"
        "• КЭТ: 12:30–16:30, ауд. 425/1\n\n"
        "📅 **24.11**\n"
        "• Орг. и управление предприятиями: 14:45–18:05, ауд. 338/1\n"
        "• Иностранный язык (тех. секция): 16:30–19:00, ауд. 317/2\n\n"
        "📅 **26.11**\n"
        "• ФОЭ (повтор): 10:45–14:00, ауд. 306/1\n\n"
        "📅 **27.11**\n"
        "• Физкультура: 09:00–15:00, СК «Динамит»\n"
        "• Дискретная математика (ИКСС): 09:00–12:30, ауд. 707/1\n\n"
        "📅 **30.11**\n"
        "• Физика (повтор): 12:30–14:45, ауд. 311/1\n"
        "• КЭТ (повтор): 12:30–16:30, ауд. 425/1\n\n"
        "💡 Для подробностей и ссылок на PDF введите /debts или откройте Mini App!"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_debt_"))
def handle_toggle_debt(call):
    debt_id = call.data.replace("toggle_debt_", "")
    state = load_debts_state()
    state[debt_id] = not state.get(debt_id, False)
    save_debts_state(state)

    found = next((d for d in DEFAULT_DEBTS if d["id"] == debt_id), None)
    status_text = "Сдано! 🎉" if state[debt_id] else "Отмечено как не сдано"
    name = found["subject"] if found else ""

    bot.answer_callback_query(call.id, f"{name}: {status_text}")
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_debts_inline())
    except:
        pass

@bot.message_handler(func=lambda msg: True)
def handle_text_buttons(message):
    text = (message.text or "").strip().lower()

    if text in ["старт", "start", "/start", "меню", "привет", "главная"]:
        handle_start(message)
    elif "пара" in text or "пары" in text or "расписание" in text or "today" in text or text == "📅 пары сегодня":
        handle_today(message)
    elif "долг" in text or "сесси" in text or "debts" in text or text == "🎓 долги и сессия":
        handle_debts(message)
    elif "пересдач" in text or "комисси" in text or "retakes" in text or "🔄 пересдачи" in text or "🔄 ближайшие пересдачи" in text:
        handle_retakes(message)
    elif "сообщен" in text or "месседж" in text or "message" in text or text == "📬 сообщения лк":
        handle_messages(message)
    elif "файл" in text or "file" in text or "материал" in text or "методич" in text or text == "📁 файлы группы":
        handle_files(message)
    elif "недел" in text or "week" in text or text == "📌 какая неделя?":
        handle_week(message)
    elif "лх" in text or "лк" in text or "кабинет" in text or "аккаунт" in text:
        handle_lk_status(message)
    else:
        bot.send_message(
            message.chat.id,
            "👋 Выберите нужный раздел кнопками ниже или отправьте:\n"
            "• **старт** — главное меню и Mini App\n"
            "• **пары** — расписание на сегодня\n"
            "• **долги** — статус по сессии\n"
            "• **пересдачи** — даты комиссий\n"
            "• **сообщения** — объявления из ЛК\n"
            "• **файлы** — методички и файлы группы",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )

# ==================== ФОНОВЫЙ ПОТОК УВЕДОМЛЕНИЙ ====================

def reminder_worker():
    last_sent_day = None
    while True:
        try:
            now = datetime.datetime.now()
            today_str = now.strftime("%Y-%m-%d")

            # В 08:30 утра отправляем напоминание о расписании
            if now.hour == 8 and now.minute == 30 and last_sent_day != today_str:
                last_sent_day = today_str
                subs = load_subscribers()
                if subs:
                    w = get_current_week_type()
                    dow = now.isoweekday()
                    lessons = SCHEDULE.get(w, {}).get(dow, [])
                    if lessons:
                        msg = f"☀️ **Доброе утро! Расписание на сегодня ({len(lessons)} пар):**\n\n"
                        for l in lessons:
                            msg += f"• {l['num']} пара ({l['time']}): {l['name']} ({l['room']})\n"
                        for chat_id in subs:
                            try:
                                bot.send_message(chat_id, msg, parse_mode="Markdown")
                            except:
                                pass

            # Предупреждение о пересдачах на завтра (в 19:00)
            if now.hour == 19 and now.minute == 0:
                tomorrow = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                state = load_debts_state()
                alert_debts = [d for d in DEFAULT_DEBTS if d["next_date"] == tomorrow and not state.get(d["id"], False)]
                if alert_debts:
                    msg = "⚠️ **НАПОМИНАНИЕ: Завтра пересдача!**\n\n"
                    for ad in alert_debts:
                        msg += f"• **{ad['subject']}**\n  Время: {ad['next_time']}\n  Ауд: {ad['next_room']}\n\n"
                    msg += "Подготовься и не опаздывай! Удачи!"
                    for chat_id in load_subscribers():
                        try:
                            bot.send_message(chat_id, msg, parse_mode="Markdown")
                        except:
                            pass

            time.sleep(45)
        except Exception as e:
            time.sleep(60)

import http.server
import socketserver

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    class HealthHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"Bot is online and running 24/7!")
        def log_message(self, format, *args):
            pass # отключаем спам в консоль
    try:
        with socketserver.TCPServer(("", port), HealthHandler) as httpd:
            print(f"Health server listening on port {port}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Health server error: {e}")

if __name__ == "__main__":
    t1 = threading.Thread(target=reminder_worker, daemon=True)
    t1.start()
    t2 = threading.Thread(target=run_health_server, daemon=True)
    t2.start()
    print("Бот запущен и слушает Telegram...")
    bot.infinity_polling(skip_pending=False, timeout=20)
