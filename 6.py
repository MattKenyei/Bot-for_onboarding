from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram import executor
import sqlite3
import asyncio

TOKEN = 'token_here' #change it
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
class Registration(StatesGroup):
    name = State()
    position = State()
    phone = State()
    email = State()
    main_menu = State()
    training = State()
    question_1 = State()
    question_2 = State()
    question_3 = State()
    company_info = State()
    company_menu = State()
    training_type = State()
    video_training = State()
    office_info = State()
    office_tour = State()
async def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    

async def add_user(user_data):
    await create_db()
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO users (id, name, position, phone, email)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_data['id'], user_data['name'], user_data['position'], user_data['phone'], user_data['email']))

    conn.commit()
async def get_worker(id):
    conn = sqlite3.connect('workers.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn = sqlite3.connect('workers.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM workers WHERE id = ?', (id,))
    user_data = cursor.fetchone()

    return user_data
async def get_user(id):
    await create_db()
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
    user_data = cursor.fetchone()

    return user_data

@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    user_data = await get_user(message.from_user.id)
    if user_data is None:
        await message.answer("Добро пожаловать! Введите ваше имя:")
        await Registration.name.set()
    else:
        await message.answer(f"Здравствуйте, с возвращением!")
        await Registration.main_menu.set()
        await show_main_menu(message)

@dp.message_handler(state=Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.from_user.id
        data['name'] = message.text

    await message.answer("Введите вашу должность:")
    await Registration.position.set()

@dp.message_handler(state=Registration.position)
async def process_position(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['position'] = message.text

    await message.answer("Введите ваш номер телефона:")
    await Registration.phone.set()

@dp.message_handler(state=Registration.phone)
async def process_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text

    await message.answer("Введите ваш адрес электронной почты:")
    await Registration.email.set()

@dp.message_handler(state=Registration.email)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text
        
    data_dict = dict(data)
    await add_user(data_dict)
    await message.answer("Спасибо за регистрацию! Вы можете попасть в главное меню, отправив команду /menu")
    await Registration.main_menu.set()

@dp.message_handler(commands='menu', state=Registration.main_menu)
async def show_main_menu(message: types.Message):
    # Создаем клавиатуру главного меню
    keyboard = types.ReplyKeyboardRemove()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Мой профиль"))
    keyboard.add(types.KeyboardButton(text="Обучение"))
    keyboard.add(types.KeyboardButton(text="О компании"))
    keyboard.add(types.KeyboardButton(text="Знакомство с офисом"))
    # Отправляем пользователю главное меню
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.message_handler(Text(equals="Знакомство с офисом"), state=Registration.main_menu)
async def start_office_tour(message: types.Message):
    # Создаем клавиатуру для выбора типа знакомства с офисом
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Главные", "Твой отдел", "Обратиться за помощью", "Выход в меню"]
    keyboard.add(*buttons)

    # Отправляем сообщение с просьбой выбрать тип знакомства
    await message.answer(
        "Выберите тип знакомства с офисом:",
        reply_markup=keyboard
    )
    
    # Переводим пользователя в состояние "выбор типа знакомства с офисом"
    await Registration.office_info.set()

@dp.message_handler(Text(equals="Главные"), state=Registration.office_info)
async def main_office_info(message: types.Message):
    await message.answer(f"Самый главный тут - Зубенко Михаил Петрович, его заместитель - Василий Иванович. Их лучше не зли.")
    await state.finish()
    await Registration.main_menu.set()
    await start_office_tour(message)
@dp.message_handler(Text(equals="Твой отдел"), state=Registration.office_info)
async def department_info(message: types.Message):
    await message.answer(f"Твой начальник - Ваильевна Елена Ивановна, её кабинет 204.\n Так же у нас есть 2 программиста, которые будут сопровождать тебя первое время - Егор и Николай, сидят прямо напротив тебя, знакомься сам.")
    await state.finish()
    await Registration.main_menu.set()
    await start_office_tour(message)
@dp.message_handler(Text(equals="Выход в меню"), state=Registration.office_info)
async def back_menu(message: types.Message):
    #await state.finish()
    await Registration.main_menu.set()
    await show_main_menu(message)
@dp.message_handler(Text(equals="Обратиться за помощью"), state=Registration.office_info)
async def request_help(message: types.Message):
    await message.answer(f"Ни в коем случае не трогай главных!\nПо всем вопросам можешь обращаться ко мне. Твой наставник, Кулебяка. Где найти меня ты знаешь, 101 кабинет, у кулера с водой.")
    await state.finish()
    await Registration.main_menu.set()
    await start_office_tour(message)
# Обработчик нажатия на кнопку "Обучение"
@dp.message_handler(Text(equals="Обучение"), state=Registration.main_menu)
async def start_training(message: types.Message):
    # Создаем клавиатуру для выбора типа обучения
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Тест", "Видео-обучение", "Фото твоего трона"]
    keyboard.add(*buttons)

    # Отправляем сообщение с просьбой выбрать тип обучения
    await message.answer(
        "Выберите тип обучения:",
        reply_markup=keyboard
    )
    
    # Переводим пользователя в состояние "выбор типа обучения"
    await Registration.training_type.set()
@dp.message_handler(Text(equals="Тест"), state=Registration.training_type)
async def start_quest(message: types.Message, state: FSMContext):
    worker_data = await get_worker(message.from_user.id)
    # Отправляем первый вопрос квеста
    if worker_data is None:
        await message.answer("Первый вопрос теста: Что вы умеете?")

        # Переводим пользователя в состояние "квест, вопрос 1"
        await Registration.question_1.set()
    else:
        await message.answer(f"Тест уже пройден")
        await Registration.main_menu.set()
        await show_main_menu(message)


@dp.message_handler(Text(equals="Видео-обучение"), state=Registration.training_type)
async def start_video_training(message: types.Message, state: FSMContext):
    # Отправляем ссылку на видео
    await message.answer("Ссылка на видео: https://www.youtube.com/watch?v=xvFZjo5PgG0", reply_markup=back_keyboard())

    # Переводим пользователя в состояние "видео-обучение"
    await Registration.video_training.set()
    await state.finish()
    await Registration.main_menu.set()
    await start_training(message)
def back_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Назад")
    return keyboard
@dp.message_handler(Text(equals="Фото твоего трона"), state=Registration.training_type)
async def start_photo_training(message: types.Message, state: FSMContext):
    worker_data = await get_worker(message.from_user.id)
    if worker_data is not None:
        with open('photo.jpg', 'rb') as photo:
            await message.answer_photo(photo, caption='Твой трон')        
    else:
        with open('photo.jpg', 'rb') as photo:
            await message.answer_photo(photo, caption='Твой трон, если пройдёшь обучение')
        
# Обработчик ответа на первый вопрос
@dp.message_handler(state=Registration.question_1)
async def answer_question_1(message: types.Message, state: FSMContext):
    # Получаем ответ пользователя на вопрос 1 и сохраняем его в хранилище состояний
    async with state.proxy() as data:
        data['question_1'] = message.text

    # Отправляем пользователю второй вопрос
    await message.answer(
        "2. Какие задачи вы должны решать ежедневно?",
    )
    
    # Переводим пользователя в состояние "вопрос 2"
    await Registration.question_2.set()


# Обработчик ответа на второй вопрос
@dp.message_handler(state=Registration.question_2)
async def answer_question_2(message: types.Message, state: FSMContext):
    # Получаем ответ пользователя на вопрос 2 и сохраняем его в хранилище состояний
    async with state.proxy() as data:
        data['question_2'] = message.text

    # Отправляем пользователю третий вопрос
    await message.answer(
        "3. Какие инструменты и технологии вы используете в работе?",
    )
    
    # Переводим пользователя в состояние "вопрос 3"
    await Registration.question_3.set()

async def save_user_data_to_db(user_data):
    conn = sqlite3.connect('workers.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn = sqlite3.connect('workers.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO workers (id, name, position, phone, email)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_data['id'], user_data['name'], user_data['position'], user_data['phone'], user_data['email']))

    conn.commit()
# Обработчик ответа на третий вопрос
@dp.message_handler(state=Registration.question_3)
async def answer_question_3(message: types.Message, state: FSMContext):
    # Получаем ответ пользователя на вопрос 3 и сохраняем его в хранилище состояний
    async with state.proxy() as data:
        user_data = await get_user(message.from_user.id)
        data['question_3'] = message.text
        user_data = {
        'id': message.from_user.id,
        'name': user_data[1],
        'position': user_data[2],
        'phone': user_data[3],
        'email': user_data[4],
        'question_1': data['question_1'],
        'question_2': data['question_2'],
        'question_3': data['question_3']
    }
    await save_user_data_to_db(user_data)
# Отправляем пользователю сообщение об успешном завершении обучения
    await message.answer(
        "Поздравляем, вы успешно прошли обучение! Теперь вы можете использовать нашего бота полноценно.\n\n"
        "Ваши ответы:\n"
        f"1. {data['question_1']}\n"
        f"2. {data['question_2']}\n"
        f"3. {data['question_3']}"
    )
    check=True
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Вернуться в главное меню"))
    
    await state.finish()
    await Registration.main_menu.set()
    await show_main_menu(message)
# Обработчик нажатия на кнопку "О компании"
@dp.message_handler(Text(equals="О компании"), state=Registration.main_menu)
async def about_company(message: types.Message):
    # Создаем клавиатуру с уровнями информации о компании
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Уровень 1"))
    keyboard.add(types.KeyboardButton(text="Уровень 2"))
    keyboard.add(types.KeyboardButton(text="Уровень 3"))
    keyboard.add(types.KeyboardButton(text="Вернуться в главное меню"))

    # Отправляем пользователю первый уровень информации о компании
    await message.answer(
        "Выберите уровень информации о компании:",
        reply_markup=keyboard
    )

    # Переводим пользователя в состояние "информация о компании"
    await Registration.company_info.set()


# Обработчик выбора уровня информации о компании
@dp.message_handler(state=Registration.company_info)
async def about_company_level(message: types.Message, state: FSMContext):
    # Получаем выбранный пользователем уровень информации о компании
    level = message.text.lower()

    if level == "уровень 1":
        # Отправляем пользователю информацию о компании на уровне 1
        await message.answer(
            "Уровень 1: Мы занимаемся разработкой программного обеспечения.",
        )
    elif level == "уровень 2":
        # Отправляем пользователю информацию о компании на уровне 2
        await message.answer(
            "Уровень 2: Компания работает в следующих направлениях: разработка программного обеспечения для бизнеса, "
            "разработка мобильных приложений, веб-разработка, разработка игр. В компании работают специалисты высокого "
            "уровня.",
        )
    elif level == "уровень 3":
        # Отправляем пользователю информацию о компании на уровне 3
        await message.answer(
            "Уровень 3: Компания была основана в 2010 году и уже более 10 лет успешно работает на рынке. "
            "Мы сотрудничаем с крупными заказчиками и всегда готовы предложить индивидуальный подход к каждому "
            "клиенту.",
        )
    elif level == "Главное меню":
        await state.finish()
        await Registration.main_menu.set()
        await show_main_menu(message)
        return
    else:
        await state.finish()
        await Registration.main_menu.set()
        await show_main_menu(message)
        return

    await message.answer("Чтобы вернуться в главное меню, выберите 'Главное меню'.")

@dp.message_handler(Text(equals="Мой профиль"), state=Registration.main_menu)
async def show_profile(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardRemove()
    user_data = await get_user(message.from_user.id)
    if user_data:
        profile_text = f"Ваш профиль:\n\nИмя: {user_data[1]}\nДолжность: {user_data[2]}\nТелефон: {user_data[3]}\nEmail: {user_data[4]}"
    else:
        profile_text = "Профиль не найден"
    await message.answer(profile_text)
    
    

    await show_main_menu(message)
    #await Registration.main_menu.set()
    

if __name__ == '__main__':
    check=False
    executor.start_polling(dp, skip_updates=True)
