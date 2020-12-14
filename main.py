import logging
import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN
import pymorphy2
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import json
import copy
import os
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

students = {}
cities = {}

weekday = {
    '0': 'понедельник',
    '1': 'вторник',
    '2': 'среду',
    '3': 'четверг',
    '4': 'пятницу',
    '5': 'субботу'
}

morph = pymorphy2.MorphAnalyzer()

city_kb = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton('Добавить или найти 🔍🌆',
                                                                     callback_data='add_city'))

school_kb = {}

grade_kb = InlineKeyboardMarkup(row_width=3)
grade_kb.add(
    InlineKeyboardButton('1', callback_data='grade_1'),
    InlineKeyboardButton('2', callback_data='grade_2'),
    InlineKeyboardButton('3', callback_data='grade_3'),
    InlineKeyboardButton('4', callback_data='grade_4'),
    InlineKeyboardButton('5', callback_data='grade_5'),
    InlineKeyboardButton('6', callback_data='grade_6'),
    InlineKeyboardButton('7', callback_data='grade_7'),
    InlineKeyboardButton('8', callback_data='grade_8'),
    InlineKeyboardButton('9', callback_data='grade_9'),
    InlineKeyboardButton('10', callback_data='grade_10'),
    InlineKeyboardButton('11', callback_data='grade_11'),
)

character_kb = InlineKeyboardMarkup(row_width=3)
character_kb.add(
    InlineKeyboardButton('А', callback_data='character_А'),
    InlineKeyboardButton('Б', callback_data='character_Б'),
    InlineKeyboardButton('В', callback_data='character_В'),
    InlineKeyboardButton('Г', callback_data='character_Г'),
    InlineKeyboardButton('Д', callback_data='character_Д'),
    InlineKeyboardButton('Е', callback_data='character_Е')
)

subjects_kb = InlineKeyboardMarkup(row_width=2)
subjects_kb.add(InlineKeyboardButton('Математика 🧮', callback_data='subject_Математика'),
                InlineKeyboardButton('Русский язык 👅', callback_data='subject_Русский язык'),
                InlineKeyboardButton('Литература 📚', callback_data='subject_Литература'),
                InlineKeyboardButton('Физика 🤷🏻‍♀️', callback_data='subject_Физика'),
                InlineKeyboardButton('Информатика 💻', callback_data='subject_Информатика'),
                InlineKeyboardButton('Обществознание ⚖', callback_data='subject_Обществознание'),
                InlineKeyboardButton('История ⚔', callback_data='subject_История'),
                InlineKeyboardButton('Биология 🌿', callback_data='subject_Биология'),
                InlineKeyboardButton('Химия 💥', callback_data='subject_Химия'),
                InlineKeyboardButton('Иностранный язык ㊙', callback_data='subject_Иностранный язык'),
                InlineKeyboardButton('Родной язык 👅', callback_data='subject_Родной язык'),
                InlineKeyboardButton('Родная литература 📚', callback_data='subject_Родная литература'),
                InlineKeyboardButton('Физкультура 🏋🏻‍♀️', callback_data='subject_Физкультура'),
                InlineKeyboardButton('География 🗺', callback_data='subject_География'))
subjects_kb.add(InlineKeyboardButton('Удалить последний добавленный предмет 🗑', callback_data='subject_del'))
subjects_kb.add(InlineKeyboardButton('Добавить предмет 🆕', callback_data='subject_add'))
subjects_kb.add(InlineKeyboardButton('Больше уроков в этот день нет 🆗', callback_data='subject_end'))

main_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Домашнее задание на завтра ➡'))
main_kb.add(KeyboardButton('Домашнее задание на неделю 📅'))
main_kb.add(KeyboardButton('Расписание 📃'))

main_kb_adm = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Изменить расписание 🔧'))
main_kb_adm.add(KeyboardButton('Домашнее задание на завтра ➡'))
main_kb_adm.add(KeyboardButton('Домашнее задание на неделю 📅'))
main_kb_adm.add(KeyboardButton('Расписание 📃'))

main_kb_sat = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Домашнее задание на послезавтра ➡'))
main_kb_sat.add(KeyboardButton('Домашнее задание на неделю 📅'))
main_kb_sat.add(KeyboardButton('Расписание 📃'))

main_kb_adm_sat = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Изменить расписание 🔧'))
main_kb_adm_sat.add(KeyboardButton('Домашнее задание на послезавтра ➡'))
main_kb_adm_sat.add(KeyboardButton('Домашнее задание на неделю 📅'))
main_kb_adm_sat.add(KeyboardButton('Расписание 📃'))

main_kb_add = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Добавить расписание на этот день 🆕'))
main_kb_add.add(KeyboardButton('Домашнее задание на завтра ➡'))
main_kb_add.add(KeyboardButton('Домашнее задание на неделю 📅'))
main_kb_add.add(KeyboardButton('Расписание 📃'))

main_kb_add_sat = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Добавить расписание на этот день 🆕'))
main_kb_add_sat.add(KeyboardButton('Домашнее задание на послезавтра ➡'))
main_kb_add_sat.add(KeyboardButton('Домашнее задание на неделю 📅'))
main_kb_add_sat.add(KeyboardButton('Расписание 📃'))

weekday_kb = InlineKeyboardMarkup(row_width=2)
weekday_kb.add(InlineKeyboardButton('Понедельник', callback_data='day_0'),
               InlineKeyboardButton('Вторник', callback_data='day_1'),
               InlineKeyboardButton('Среда', callback_data='day_2'),
               InlineKeyboardButton('Четверг', callback_data='day_3'),
               InlineKeyboardButton('Пятница', callback_data='day_4'),
               InlineKeyboardButton('Суббота', callback_data='day_5'))

cancel_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Отменить ❌', callback_data='cancel'))


async def save():
    global students, cities
    students_ = copy.deepcopy(students)
    for student in students_.values():
        student['start_messages'] = []
        student['last_messages'] = []
        if 'city' in student:
            del student['city']
        if 'school' in student:
            del student['school']
        if 'grade' in student:
            del student['grade']
    with open('students.json', 'w') as f:
        f.write(json.dumps(students_))
    with open('cities.json', 'w') as f:
        f.write(json.dumps(cities))


async def load():
    global students, cities, city_kb, school_kb
    with open('cities.json') as f:
        cities = json.load(f)
    for city in cities.keys():
        if city == list(cities.keys())[0]:
            city_kb.add(InlineKeyboardButton(city, callback_data=f'city_{city}'))
        else:
            city_kb.insert(InlineKeyboardButton(city, callback_data=f'city_{city}'))
        city_ = cities[city]
        school_kb[city] = InlineKeyboardMarkup(row_width=4).add(InlineKeyboardButton('Добавить или найти 🔍🏫',
                                                                                     callback_data='add_school'))
        for school in city_['schools'].keys():
            if school == list(city_['schools'].keys())[0]:
                school_kb[city].add(InlineKeyboardButton(school, callback_data=f'school_{school}'))
            else:
                school_kb[city].insert(InlineKeyboardButton(school, callback_data=f'school_{school}'))
    with open('students.json') as f:
        students_json = json.load(f)
    for student in students_json.items():
        user_id, parameters = student
        user_id = int(user_id)
        students[user_id] = parameters
        stud = students[user_id]
        if 'name_city' in stud:
            stud['city'] = cities[stud['name_city']]
        if 'number_school' in stud:
            stud['school'] = stud['city']['schools'][stud['number_school']]
        if 'number_grade' in stud:
            stud['grade'] = stud['school']['classes'][stud['number_grade']]


async def clear_homework():
    global cities
    today = str(datetime.datetime.today().weekday())
    if today != 6:
        for city in cities.values():
            for school in city['schools'].values():
                for grade in school['classes'].values():
                    for subject in grade['homework'][today].keys():
                        grade['homework'][today][subject] = ''
        for city in cities.keys():
            for school in cities[city]['schools'].keys():
                for grade in cities[city]['schools'][school]['classes'].keys():
                    directory = 'photos/{}/{}/{}/{}'.format(city, school, grade, today)
                    if os.listdir(directory):
                        for img in os.listdir(directory):
                            os.remove(f'{directory}/{img}')


def get_password():
    password = list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ-_')
    random.shuffle(password)
    return ''.join([random.choice(password) for _ in range(8)])


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('city'))
async def process_callback_choose_city(callback_query: types.CallbackQuery):
    global students, cities
    user_id = callback_query.from_user.id
    student = students[user_id]
    city = callback_query.data.split('_')[1]
    student['name_city'] = city
    student['city'] = cities[city]
    if 'number_school' in student:
        del student['number_school']
    if 'school' in student:
        del student['school']
    if 'number_grade' in student:
        del student['number_grade']
    if 'tmp_grade' in student:
        del student['tmp_grade']
    if 'grade' in student:
        del student['grade']
    await bot.answer_callback_query(callback_query.id)
    student['start_messages'] += [await bot.send_message(user_id, f'Выбран город {city}')]
    student['start_messages'] += [await bot.send_message(user_id, 'Из какой ты школы?',
                                                         reply_markup=school_kb[student['name_city']])]


@dp.callback_query_handler(lambda c: c.data and c.data == 'add_city')
async def process_callback_add_city(callback_query: types.CallbackQuery):
    global students
    user_id = callback_query.from_user.id
    student = students[user_id]
    student['flag_add_city'] = True
    student['flag_add_subject'] = False
    student['flag_add_school'] = False
    student['flag_add_name'] = False
    student['flag_add_homework'] = False
    student['enter_password'] = False
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, 'Напиши мне название города', reply_markup=cancel_kb)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('school'))
async def process_callback_choose_school(callback_query: types.CallbackQuery):
    global students, cities
    user_id = callback_query.from_user.id
    student = students[user_id]
    number_school = callback_query.data.split('_')[1]
    student['number_school'] = number_school
    student['school'] = student['city']['schools'][number_school]
    if 'number_grade' in student:
        del student['number_grade']
    if 'tmp_grade' in student:
        del student['tmp_grade']
    if 'grade' in student:
        del student['grade']
    await bot.answer_callback_query(callback_query.id)
    student['start_messages'] += [await bot.send_message(user_id, f'Выбрана {number_school} школа')]
    student['start_messages'] += [await bot.send_message(user_id, 'Из какого ты класса?', reply_markup=grade_kb)]


@dp.callback_query_handler(lambda c: c.data and c.data == 'add_school')
async def process_callback_add_school(callback_query: types.CallbackQuery):
    global students
    user_id = callback_query.from_user.id
    student = students[user_id]
    student['flag_add_school'] = True
    student['flag_add_city'] = False
    student['flag_add_subject'] = False
    student['flag_add_name'] = False
    student['flag_add_homework'] = False
    student['enter_password'] = False
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, 'Напиши мне номер школы 🏫', reply_markup=cancel_kb)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('grade'))
async def process_callback_choose_grade(callback_query: types.CallbackQuery):
    global students
    user_id = callback_query.from_user.id
    student = students[user_id]
    number_grade = callback_query.data.split('_')[1]
    student['grade'] = number_grade
    await bot.answer_callback_query(callback_query.id)
    student['start_messages'] += [await bot.send_message(user_id, f'Выбран {number_grade} класс')]
    student['start_messages'] += [await bot.send_message(user_id, 'Какая литера класса?', reply_markup=character_kb)]


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('character'))
async def process_callback_choose_character(callback_query: types.CallbackQuery):
    global students, cities
    user_id = callback_query.from_user.id
    student = students[user_id]
    character_grade = callback_query.data.split('_')[1]
    if student['grade'][-1].isalpha():
        student['grade'] = student['grade'][:-1] + character_grade
    else:
        student['grade'] += character_grade
    grade = student['grade']
    if grade in student['school']['classes']:
        student['tmp_grade'] = student['school']['classes'][grade]
        enter_password_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Ввести пароль',
                                                                            callback_data='enter_password'))
        student['start_messages'] += [await bot.send_message(user_id, f'Выбран {grade} класс',
                                                             reply_markup=enter_password_kb)]
    else:
        student['school']['classes'][grade] = {
            'number': grade,
            'students': [],
            'homework': {'0': {}, '1': {}, '2': {}, '3': {}, '4': {}, '5': {}, '6': {}},
            'schedule': {'0': [], '1': [], '2': [], '3': [], '4': [], '5': [], '6': []}
        }
        student['tmp_grade'] = student['school']['classes'][grade]
        create_grade_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Создать класс',
                                                                          callback_data='create_class'))
        student['start_messages'] += [await bot.send_message(user_id, f'Выбран {grade} класс',
                                                             reply_markup=create_grade_kb)]
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('create_class'))
async def process_callback_create_class(callback_query: types.CallbackQuery):
    global students
    user_id = callback_query.from_user.id
    student = students[user_id]
    gender = student['gender']
    if student['created_class']:
        create = morph.parse('создавал')[0]
        student['start_messages'] += [await bot.send_message(user_id, f'Ты уже {create.inflect({gender}).word} класс!')]
        student['start_messages'] += [await bot.send_message(user_id, 'Из какого ты класса?', reply_markup=grade_kb)]
    else:
        student['created_class'] = True
        student['grade'] = student['tmp_grade']
        student['number_grade'] = student['grade']['number']
        os.mkdir('photos/{}/{}/{}'.format(student['name_city'],
                                          student['number_school'],
                                          student['number_grade']))
        for i in range(6):
            os.mkdir('photos/{}/{}/{}/{}'.format(student['name_city'],
                                                 student['number_school'],
                                                 student['number_grade'], i))
        password = get_password()
        student['grade']['password'] = password
        student['grade']['students'] += [student['user_id']]
        student['grade']['admin'] = student['user_id']
        create = morph.parse('создал')[0]
        grade = student['grade']['number']
        if datetime.datetime.today().weekday() == 5:
            await bot.send_message(user_id, f'Ты успешно {create.inflect({gender}).word} '
                                            f'{grade} класс!', reply_markup=main_kb_sat)
        else:
            await bot.send_message(user_id, f'Ты успешно {create.inflect({gender}).word} '
                                            f'{grade} класс!', reply_markup=main_kb)
        await bot.send_message(user_id, f'Ваш пароль от класса:')
        await bot.send_message(user_id, password)
        await bot.send_message(user_id, 'Поделись им со своими одноклассниками, чтобы они тоже могли войти в Дневник')
        for msg in student['start_messages']:
            await msg.delete()
        student['start_messages'] = []
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('enter_password'))
async def process_callback_enter_password(callback_query: types.CallbackQuery):
    global students
    user_id = callback_query.from_user.id
    student = students[user_id]
    student['enter_password'] = True
    student['flag_add_school'] = False
    student['flag_add_city'] = False
    student['flag_add_subject'] = False
    student['flag_add_name'] = False
    student['flag_add_homework'] = False
    await bot.send_message(user_id, f'Введи пароль от класса', reply_markup=cancel_kb)
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('subject'))
async def process_callback_choose_subject(callback_query: types.CallbackQuery):
    global students
    user_id = callback_query.from_user.id
    student = students[user_id]
    subject = callback_query.data.split('_')[1]
    await bot.answer_callback_query(callback_query.id)
    if student['selected_day'] is not None:
        if subject == 'end':
            for msg in student['last_messages']:
                await msg.delete()
            student['last_messages'] = []
            day = student['selected_day']
            if datetime.datetime.today().weekday() == 5:
                await bot.send_message(user_id, 'Расписание добавлено! 🎉', reply_markup=main_kb_adm_sat
                                       if student['user_id'] == student['grade']['admin'] else main_kb_sat)
            else:
                await bot.send_message(user_id, 'Расписание добавлено! 🎉', reply_markup=main_kb_adm
                                       if student['user_id'] == student['grade']['admin'] else main_kb)
            custom_kb = InlineKeyboardMarkup(row_width=2)
            schedule = ''
            for i, subject in enumerate(student['grade']['schedule'][day]):
                schedule += f'*{i + 1}. {subject}*\n'
                custom_kb.add(InlineKeyboardButton(f'{subject}', callback_data=f'AddHomework_{subject}'))
            await bot.send_message(user_id, f'*Домашнее задание на {weekday[day]}*', parse_mode='Markdown')
            await bot.send_message(user_id, schedule, reply_markup=custom_kb, parse_mode='Markdown')
        elif subject == 'add':
            student['flag_add_subject'] = True
            student['flag_add_school'] = False
            student['flag_add_city'] = False
            student['flag_add_name'] = False
            student['flag_add_homework'] = False
            student['enter_password'] = False
            await bot.send_message(user_id, 'Введи название предмета', reply_markup=cancel_kb)
        elif subject == 'del':
            if student['grade']['schedule'][student['selected_day']]:
                subject_del = student['grade']['schedule'][student['selected_day']][-1]
                del student['grade']['schedule'][student['selected_day']][-1]
                if subject_del not in student['grade']['schedule'][student['selected_day']]:
                    del student['grade']['homework'][student['selected_day']][subject_del]
                await student['last_messages'][-1].delete()
                student['last_messages'] = student['last_messages'][:-1]
        else:
            student['grade']['homework'][student['selected_day']][subject] = ''
            student['grade']['schedule'][student['selected_day']] += [subject]
            n = len(student['grade']['schedule'][student['selected_day']])
            student['last_messages'] += [await callback_query.message.answer(f'{n}. {subject}')]
    else:
        await bot.send_message(user_id, 'Сначала выбери день!')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('day'))
async def process_callback_choose_day(callback_query: types.CallbackQuery):
    global students
    user_id = callback_query.from_user.id
    student = students[user_id]
    day = callback_query.data.split('_')[1]
    student['selected_day'] = day
    student['flag_add_homework'] = False
    await bot.answer_callback_query(callback_query.id)
    if student['grade']['schedule'][day]:
        custom_kb = InlineKeyboardMarkup(row_width=2)
        schedule = ''
        for i, subject in enumerate(student['grade']['schedule'][day]):
            if student['grade']['homework'][day][subject]:
                schedule += f'*{i + 1}. {subject}:*\n' + student['grade']['homework'][day][subject]
            else:
                schedule += f'*{i + 1}. {subject}*\n'
            custom_kb.add(InlineKeyboardButton(f'{subject}', callback_data=f'AddHomework_{subject}'))
        if student['user_id'] == student['grade']['admin']:
            if datetime.datetime.today().weekday() == 5:
                await bot.send_message(user_id, f'*Домашнее задание на {weekday[day]}*',
                                       reply_markup=main_kb_adm_sat, parse_mode='Markdown')
            else:
                await bot.send_message(user_id, f'*Домашнее задание на {weekday[day]}*', reply_markup=main_kb_adm,
                                       parse_mode='Markdown')
        else:
            await bot.send_message(user_id, f'*Домашнее задание на {weekday[day]}*', parse_mode='Markdown')
        await bot.send_message(user_id, schedule, reply_markup=custom_kb, parse_mode='Markdown')
        directory = 'photos/{}/{}/{}/{}'.format(student['name_city'],
                                                student['number_school'],
                                                student['number_grade'],
                                                student['selected_day'])
        if os.listdir(directory):
            for img in os.listdir(directory):
                with open(f'{directory}/{img}', 'rb') as photo:
                    await callback_query.message.answer_photo(photo)
    else:
        if datetime.datetime.today().weekday() == 5:
            await bot.send_message(user_id, 'Расписания на этот день ещё нет 😕', reply_markup=main_kb_add_sat)
        else:
            await bot.send_message(user_id, 'Расписания на этот день ещё нет 😕', reply_markup=main_kb_add)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('AddHomework'))
async def process_callback_add_homework(callback_query: types.CallbackQuery):
    global students
    user_id = callback_query.from_user.id
    student = students[user_id]
    subject = callback_query.data.split('_')[1]
    student['selected_subject'] = subject
    student['flag_add_homework'] = True
    student['flag_add_school'] = False
    student['flag_add_city'] = False
    student['flag_add_subject'] = False
    student['flag_add_name'] = False
    student['enter_password'] = False
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()
    await bot.send_message(user_id, f'Что задали по предмету "{subject}"?', reply_markup=cancel_kb)


@dp.callback_query_handler(lambda c: c.data and c.data == 'cancel')
async def cancel(callback_query: types.CallbackQuery):
    global students
    user_id = callback_query.from_user.id
    student = students[user_id]
    student['flag_add_city'] = False
    student['flag_add_school'] = False
    student['enter_password'] = False
    student['flag_add_subject'] = False
    if student['flag_add_homework']:
        student['flag_add_homework'] = False
        day = student['selected_day']
        custom_kb = InlineKeyboardMarkup(row_width=2)
        schedule = ''
        for i, subject in enumerate(student['grade']['schedule'][day]):
            if student['grade']['homework'][day][subject]:
                schedule += f'*{i + 1}. {subject}:*\n' + student['grade']['homework'][day][subject]
            else:
                schedule += f'*{i + 1}. {subject}*\n'
            custom_kb.add(InlineKeyboardButton(f'{subject}', callback_data=f'AddHomework_{subject}'))
        await bot.send_message(user_id, schedule, reply_markup=custom_kb, parse_mode='Markdown')
    await callback_query.message.delete()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    global students
    user_id = message.from_user.id
    if user_id not in students:
        students[user_id] = {
            'user_id': user_id,
            'flag_add_name': True,
            'flag_add_city': False,
            'flag_add_school': False,
            'flag_add_subject': False,
            'flag_add_homework': False,
            'created_class': False,
            'enter_password': False,
            'last_messages': [],
            'start_messages': []
        }
    else:
        student = students[user_id]
        try:
            student['grade']['students'].remove(student['user_id'])
        except:
            pass
        student['flag_add_name'] = True
        student['flag_add_city'] = False
        student['flag_add_school'] = False
        student['flag_add_subject'] = False
        student['flag_add_homework'] = False
        student['enter_password'] = False
    await bot.send_message(user_id, 'Привет! Я Леся, и я очень рада знакомству 🥰\nЕсли между нами возникнут какие-то '
                                    'недопонимания - пожалуйста, напиши @kudoff', reply_markup=ReplyKeyboardRemove())
    with open('data/logo.jpg', 'rb') as photo:
        await message.answer_photo(photo)
    await bot.send_message(user_id, 'Как тебя зовут?) 😜')


@dp.message_handler(commands=['load'])
async def cmd_load(message: types.Message):
    global students, cities, city_kb, school_kb
    with open('cities.json') as f:
        cities = json.load(f)
    for city in cities.keys():
        if city == list(cities.keys())[0]:
            city_kb.add(InlineKeyboardButton(city, callback_data=f'city_{city}'))
        else:
            city_kb.insert(InlineKeyboardButton(city, callback_data=f'city_{city}'))
        city_ = cities[city]
        school_kb[city] = InlineKeyboardMarkup(row_width=4).add(InlineKeyboardButton('Добавить или найти 🔍🏫',
                                                                                     callback_data='add_school'))
        for school in city_['schools'].keys():
            if school == list(city_['schools'].keys())[0]:
                school_kb[city].add(InlineKeyboardButton(school, callback_data=f'school_{school}'))
            else:
                school_kb[city].insert(InlineKeyboardButton(school, callback_data=f'school_{school}'))
    with open('students.json') as f:
        students_json = json.load(f)
    for student in students_json.items():
        user_id, parameters = student
        user_id = int(user_id)
        students[user_id] = parameters
        stud = students[user_id]
        if 'name_city' in stud:
            stud['city'] = cities[stud['name_city']]
        if 'number_school' in stud:
            stud['school'] = stud['city']['schools'][stud['number_school']]
        if 'number_grade' in stud:
            stud['grade'] = stud['school']['classes'][stud['number_grade']]


@dp.message_handler(commands=['save'])
async def cmd_save(message: types.Message):
    global cities, students
    students_ = copy.deepcopy(students)
    for student in students_.values():
        student['start_messages'] = []
        student['last_messages'] = []
        if 'city' in student:
            del student['city']
        if 'school' in student:
            del student['school']
        if 'grade' in student:
            del student['grade']
    with open('students.json', 'w') as f:
        f.write(json.dumps(students_))
    with open('cities.json', 'w') as f:
        f.write(json.dumps(cities))


@dp.message_handler(commands=['clearHomework'])
async def cmd_clear_homework(message: types.Message):
    global cities
    user_id = message.from_user.id
    if user_id == 562306231:
        today = str(datetime.datetime.today().weekday())
        if today != 6:
            for city in cities.values():
                for school in city['schools'].values():
                    for grade in school['classes'].values():
                        for subject in grade['homework'][today].keys():
                            grade['homework'][today][subject] = ''
            for city in cities.keys():
                for school in cities[city]['schools'].keys():
                    for grade in cities[city]['schools'][school]['classes'].keys():
                        directory = 'photos/{}/{}/{}/{}'.format(city, school, grade, today)
                        if os.listdir(directory):
                            for img in os.listdir(directory):
                                os.remove(f'{directory}/{img}')


@dp.message_handler(commands=['get_statistics'])
async def cmd_stat(message: types.Message):
    global students
    user_id = message.from_user.id
    await bot.send_message(user_id, f'Количество активных пользователей: {len(students)}')


@dp.message_handler(lambda message: message.text == 'Изменить расписание 🔧')
async def homework_change_schedule(message: types.Message):
    global students
    user_id = message.from_user.id
    student = students[user_id]
    if student['user_id'] == student['grade']['admin']:
        student['grade']['schedule'][student['selected_day']] = []
        student['grade']['homework'][student['selected_day']] = {}
        directory = 'photos/{}/{}/{}/{}'.format(student['name_city'],
                                                student['number_school'],
                                                student['number_grade'],
                                                student['selected_day'])
        if os.listdir(directory):
            for img in os.listdir(directory):
                os.remove(f'{directory}/{img}')
        student['last_messages'] += [await bot.send_message(user_id, 'Добавь уроки:', reply_markup=subjects_kb)]
        student['last_messages'] += [await bot.send_message(user_id, 'Нажми "Больше уроков в этот день нет", '
                                                                     'когда закончишь 😜',
                                                            reply_markup=ReplyKeyboardRemove())]


@dp.message_handler(lambda message: message.text == 'Домашнее задание на завтра ➡' or
                                    message.text == 'Домашнее задание на послезавтра ➡')
async def homework_tomorrow(message: types.Message):
    global students
    user_id = message.from_user.id
    student = students[user_id]
    if datetime.datetime.today().weekday() != 5 and datetime.datetime.today().weekday() != 6:
        tomorrow = str(datetime.datetime.today().weekday() + 1)
    else:
        tomorrow = '0'
    student['selected_day'] = tomorrow
    student['flag_add_homework'] = False
    if student['grade']['schedule'][tomorrow]:
        custom_kb = InlineKeyboardMarkup(row_width=2)
        schedule = ''
        for i, subject in enumerate(student['grade']['schedule'][tomorrow]):
            if student['grade']['homework'][tomorrow][subject]:
                schedule += f'*{i + 1}. {subject}:*\n' + student['grade']['homework'][tomorrow][subject]
            else:
                schedule += f'*{i + 1}. {subject}*\n'
            custom_kb.add(InlineKeyboardButton(f'{subject}', callback_data=f'AddHomework_{subject}'))
        if student['user_id'] == student['grade']['admin']:
            if datetime.datetime.today().weekday() == 5:
                await bot.send_message(user_id, f'*Домашнее задание на {weekday[tomorrow]}*',
                                       reply_markup=main_kb_adm_sat, parse_mode='Markdown')
            else:
                await bot.send_message(user_id, f'*Домашнее задание на {weekday[tomorrow]}*', reply_markup=main_kb_adm,
                                       parse_mode='Markdown')
        else:
            await bot.send_message(user_id, f'*Домашнее задание на {weekday[tomorrow]}*',
                                   parse_mode='Markdown')
        await bot.send_message(user_id, schedule, reply_markup=custom_kb, parse_mode='Markdown')
        directory = 'photos/{}/{}/{}/{}'.format(student['name_city'],
                                                student['number_school'],
                                                student['number_grade'],
                                                student['selected_day'])
        if os.listdir(directory):
            for img in os.listdir(directory):
                with open(f'{directory}/{img}', 'rb') as photo:
                    await message.answer_photo(photo)
    else:
        if datetime.datetime.today().weekday() == 5:
            await bot.send_message(user_id, 'Расписания на этот день ещё нет 😕', reply_markup=main_kb_add_sat)
        else:
            await bot.send_message(user_id, 'Расписания на этот день ещё нет 😕', reply_markup=main_kb_add)


@dp.message_handler(lambda message: message.text == 'Домашнее задание на неделю 📅')
async def homework_selected_day(message: types.Message):
    user_id = message.from_user.id
    await bot.send_message(user_id, 'Выбери день:', reply_markup=weekday_kb)


@dp.message_handler(lambda message: message.text == 'Добавить расписание на этот день 🆕')
async def add_homework(message: types.Message):
    global students
    user_id = message.from_user.id
    student = students[user_id]
    if not student['grade']['schedule'][student['selected_day']]:
        student['last_messages'] += [await bot.send_message(user_id, 'Добавь уроки:', reply_markup=subjects_kb)]
        student['last_messages'] += [await bot.send_message(user_id, 'Нажми "Больше уроков в этот день нет", '
                                                                     'когда закончишь 😜',
                                                            reply_markup=ReplyKeyboardRemove())]
    else:
        await bot.send_message(user_id, 'Расписание на этот день уже есть')


@dp.message_handler(lambda message: message.text.startswith('admin_send'))
async def admin_send(message: types.Message):
    global students
    user_id = message.from_user.id
    if user_id == 562306231:
        msg = message.text[11:]
        for student in students.keys():
            try:
                await bot.send_message(student, msg)
            except:
                pass


@dp.message_handler(lambda message: message.text.startswith('admin_answer'))
async def admin_answer(message: types.Message):
    global students
    user_id = message.from_user.id
    id_ = message.text[message.text.index('{') + 1:message.text.index('}')]
    if user_id == 562306231:
        msg = message.text[message.text.index('}') + 2:]
        try:
            await bot.send_message(int(id_), msg)
        except:
            pass


@dp.message_handler(lambda message: message.text == 'Расписание 📃')
async def cmd_schedule(message: types.Message):
    global students
    user_id = message.from_user.id
    student = students[user_id]
    font = ImageFont.FreeTypeFont('/home/ubuntu/sDiary/19572.TTF', 70)
    text_color = (150, 51, 72)
    img = Image.open('photo.jpg')
    draw = ImageDraw.Draw(img)

    for i in range(3):
        text_position_i = (280, 820 + i * 1080)
        for j in range(2):
            text_position_j = (text_position_i[0] + j * 1040, text_position_i[1])
            for z in range(7):
                text_position = (text_position_j[0], text_position_j[1] + z * 102)
                try:
                    text = student['grade']['schedule'][str(i + 3 * j)][z]
                    if len(text) > 12:
                        draw.text(text_position, text[:12] + '...', text_color, font)
                    else:
                        draw.text(text_position, text, text_color, font)
                except:
                    pass

    img.save('schedule_photo.jpg')

    with open('schedule_photo.jpg', 'rb') as photo:
        await message.answer_photo(photo)


@dp.message_handler()
async def echo_message(message: types.Message):
    global cities, students
    user_id = message.from_user.id
    student = students[user_id]
    if student['flag_add_name']:
        student['flag_add_name'] = False
        student['name'] = message.text.capitalize()
        student['gender'] = str(morph.parse(student['name'])[0].tag.gender) \
            if morph.parse(student['name'])[0].tag.gender else 'masc'
        student['start_messages'] += [await bot.send_message(user_id, 'Из какого ты города?', reply_markup=city_kb)]
    elif student['flag_add_city']:
        student['flag_add_city'] = False
        if 'number_school' in student:
            del student['number_school']
        if 'school' in student:
            del student['school']
        if 'number_grade' in student:
            del student['number_grade']
        if 'tmp_grade' in student:
            del student['tmp_grade']
        if 'grade' in student:
            del student['grade']
        if message.text not in cities:
            os.mkdir(f'photos/{message.text}')
            cities[message.text] = {'schools': {}}
            school_kb[message.text] = InlineKeyboardMarkup(row_width=4).add(InlineKeyboardButton('Добавить или '
                                                                                                 'найти 🔍🏫',
                                                                            callback_data='add_school'))
            if len(cities) == 1:
                city_kb.add(InlineKeyboardButton(message.text, callback_data=f'city_{message.text}'))
            else:
                city_kb.insert(InlineKeyboardButton(message.text, callback_data=f'city_{message.text}'))
        student['name_city'] = message.text
        student['city'] = cities[message.text]
        student['start_messages'] += [await bot.send_message(user_id, f'Выбран город {message.text}')]
        student['start_messages'] += [await bot.send_message(user_id, 'Из какой ты школы?',
                                                             reply_markup=school_kb[student['name_city']])]
    elif student['flag_add_school']:
        student['flag_add_school'] = False
        if 'number_grade' in student:
            del student['number_grade']
        if 'tmp_grade' in student:
            del student['tmp_grade']
        if 'grade' in student:
            del student['grade']
        if message.text.isdigit():
            if message.text not in student['city']['schools']:
                os.mkdir('photos/{}/{}'.format(student['name_city'], message.text))
                student['city']['schools'][message.text] = {'classes': {}}
                if len(student['city']['schools']) == 1:
                    school_kb[student['name_city']].add(InlineKeyboardButton(message.text,
                                                                             callback_data=f'school_{message.text}'))
                else:
                    school_kb[student['name_city']].insert(InlineKeyboardButton(message.text,
                                                                                callback_data=f'school_{message.text}'))
            student['number_school'] = message.text
            student['school'] = student['city']['schools'][message.text]
            student['start_messages'] += [await bot.send_message(user_id, f'Выбрана {message.text} школа')]
            student['start_messages'] += [await bot.send_message(user_id, 'Из какого ты класса?',
                                                                 reply_markup=grade_kb)]
        else:
            await bot.send_message(user_id, 'Что-то не так... Напиши мне номер школы')
            student['flag_add_school'] = True
    elif student['enter_password']:
        student['enter_password'] = False
        if message.text == student['tmp_grade']['password']:
            student['grade'] = student['tmp_grade']
            student['number_grade'] = student['grade']['number']
            student['grade']['students'] += [student['user_id']]
            enter = morph.parse('вошёл')[0]
            gender = student['gender']
            grade = student['grade']['number']
            if datetime.datetime.today().weekday() == 5:
                await bot.send_message(user_id, f'Ты успешно {enter.inflect({gender}).word} в '
                                                f'{grade} класс!', reply_markup=main_kb_sat)
            else:
                await bot.send_message(user_id, f'Ты успешно {enter.inflect({gender}).word} в '
                                                f'{grade} класс!', reply_markup=main_kb)
            for msg in student['start_messages']:
                await msg.delete()
            student['start_messages'] = []
        else:
            student['enter_password'] = True
            await bot.send_message(user_id, f'Неверный пароль! Попробуй снова)')
    elif student['flag_add_subject']:
        try:
            student['flag_add_subject'] = False
            subject = message.text.capitalize()
            student['grade']['homework'][student['selected_day']][subject] = ''
            student['grade']['schedule'][student['selected_day']] += [subject]
            n = len(student['grade']['schedule'][student['selected_day']])
            student['last_messages'] += [await bot.send_message(user_id, f'{n}. {subject}')]
        except:
            await bot.send_message(user_id, f'Упс... Что-то пошло не так. Попробуй снова')
            student['flag_add_subject'] = True
    elif student['flag_add_homework']:
        try:
            student['flag_add_homework'] = False
            s_day = student['selected_day']
            s_subject = student['selected_subject']
            from_name = morph.parse(student['name'])[0]
            from_name = from_name.inflect({'gent'}).word.capitalize()
            student['grade']['homework'][s_day][s_subject] += '      ' + message.text + f' _от {from_name}_\n'
            custom_kb = InlineKeyboardMarkup(row_width=2)
            schedule = ''
            for i, subject in enumerate(student['grade']['schedule'][s_day]):
                if student['grade']['homework'][s_day][subject]:
                    schedule += f'*{i + 1}. {subject}:*\n' + student['grade']['homework'][s_day][subject]
                else:
                    schedule += f'*{i + 1}. {subject}*\n'
                custom_kb.add(InlineKeyboardButton(f'{subject}', callback_data=f'AddHomework_{subject}'))
            if datetime.datetime.today().weekday() == 5:
                await bot.send_message(user_id, f'*Домашнее задание на {weekday[s_day]}*',
                                       reply_markup=main_kb_adm_sat if student['user_id'] == student['grade']['admin']
                                       else main_kb_sat,
                                       parse_mode='Markdown')
            else:
                await bot.send_message(user_id, f'*Домашнее задание на {weekday[s_day]}*',
                                       reply_markup=main_kb_adm if student['user_id'] == student['grade']['admin']
                                       else main_kb,
                                       parse_mode='Markdown')
            await bot.send_message(user_id, schedule, reply_markup=custom_kb, parse_mode='Markdown')
            directory = 'photos/{}/{}/{}/{}'.format(student['name_city'],
                                                    student['number_school'],
                                                    student['number_grade'],
                                                    student['selected_day'])
            if os.listdir(directory):
                for img in os.listdir(directory):
                    with open(f'{directory}/{img}', 'rb') as photo:
                        await message.answer_photo(photo)
            added = morph.parse('добавил')[0]
            name = student['name']
            gender = student['gender']
            for stud in student['grade']['students']:
                if stud != student['user_id']:
                    try:
                        await bot.send_message(stud, f'{name} {added.inflect({gender}).word} '
                                                     f'домашнее задание по предмету "{s_subject}" на {weekday[s_day]}')
                    except:
                        pass
        except:
            await bot.send_message(user_id, f'Упс... Что-то пошло не так. Попробуй снова')
            student['flag_add_homework'] = True
    else:
        await bot.send_message(562306231, f'{user_id} ' + student['name'] + ' ' + message.text)


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def get_photo(message):
    global cities, students
    user_id = message.from_user.id
    student = students[user_id]
    if student['flag_add_homework']:
        student['flag_add_homework'] = False
        directory = 'photos/{}/{}/{}/{}'.format(student['name_city'],
                                                student['number_school'],
                                                student['number_grade'],
                                                student['selected_day'])
        await message.photo[-1].download(f'{directory}/{len(os.listdir(directory))}.jpg')
        s_day = student['selected_day']
        s_subject = student['selected_subject']
        from_name = morph.parse(student['name'])[0]
        from_name = from_name.inflect({'gent'}).word.capitalize()
        if message.caption:
            student['grade']['homework'][s_day][s_subject] += '      ' + message.caption + f' _от {from_name}_\n'
        else:
            student['grade']['homework'][s_day][s_subject] += '      Фотография' + f' _от {from_name}_\n'
        custom_kb = InlineKeyboardMarkup(row_width=2)
        schedule = ''
        for i, subject in enumerate(student['grade']['schedule'][s_day]):
            if student['grade']['homework'][s_day][subject]:
                schedule += f'*{i + 1}. {subject}:*\n' + student['grade']['homework'][s_day][subject]
            else:
                schedule += f'*{i + 1}. {subject}*\n'
            custom_kb.add(InlineKeyboardButton(f'{subject}', callback_data=f'AddHomework_{subject}'))
        if datetime.datetime.today().weekday() == 5:
            await bot.send_message(user_id, f'*Домашнее задание на {weekday[s_day]}*',
                                   reply_markup=main_kb_adm_sat if student['user_id'] == student['grade']['admin']
                                   else main_kb_sat,
                                   parse_mode='Markdown')
        else:
            await bot.send_message(user_id, f'*Домашнее задание на {weekday[s_day]}*',
                                   reply_markup=main_kb_adm if student['user_id'] == student['grade']['admin']
                                   else main_kb,
                                   parse_mode='Markdown')
        await bot.send_message(user_id, schedule, reply_markup=custom_kb, parse_mode='Markdown')
        added = morph.parse('добавил')[0]
        name = student['name']
        gender = student['gender']
        for stud in student['grade']['students']:
            if stud != student['user_id']:
                try:
                    await bot.send_message(stud, f'{name} {added.inflect({gender}).word} фотографию по предмету '
                                                 f'"{s_subject}" на {weekday[s_day]}')
                except:
                    pass
    else:
        await bot.send_message(user_id, 'Красивое фото... Но зачем вы его мне отправили?))')


if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(save, 'interval', minutes=1)
    scheduler.add_job(clear_homework, 'cron', hour=6, minute=0)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
