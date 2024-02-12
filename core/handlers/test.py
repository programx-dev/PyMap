from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.utils.states import StepsTest
from core.utils.callbackdata import Test
from aiogram.types import CallbackQuery
from aiogram import Bot
from core.utils.dbconnect import Request
from core.keyboards import inline_kb
import logging
from aiogram.utils.chat_action import ChatActionSender


async def init_test(call: CallbackQuery, bot: Bot, callback_data: Test, state: FSMContext, request: Request):
    id = callback_data.id

    await call.message.delete()

    # async with ChatActionSender.typing(chat_id=call.message.chat.id, bot=bot, initial_sleep=0.5):
    await state.set_state(StepsTest.TEST)
    await state.update_data(test=id)
    await state.update_data(know=0)
    await state.update_data(not_know=0)
    await state.update_data(skip=0)
    await state.update_data(current=0)

    children = (await request.get_data_test(id=id))[3]
    question = (await request.get_data_test(children[0]))[1]

    info_bar = f"✅ <i>Знаю 0</i> | 📚 <i>Выучить 0</i> | ⏭ <i>Пропущено 0</i> | <b>Вопрос 1 / {len(children)}</b>"
    message = info_bar + f"\n\n<b>{question}</b>"

    await call.message.answer(text=message, reply_markup=await inline_kb.get_inline_keyboard_test())
    await call.answer()


async def get_test(call: CallbackQuery, bot: Bot, state: FSMContext, request: Request):
    # async with ChatActionSender.typing(chat_id=call.message.chat.id, bot=bot, initial_sleep=0.5):
    tmp = await state.get_data()
    id = tmp["test"]

    if call.data == "know":
        tmp["know"] += 1
        await state.update_data(know=tmp["know"])
    elif call.data == "not_know":
        tmp["not_know"] += 1
        await state.update_data(not_know=tmp["not_know"])
    elif call.data == "skip":
        tmp["skip"] += 1
        await state.update_data(skip=tmp["skip"])

    children = (await request.get_data_test(id=id))[3]
    question, answer = (await request.get_data_test(children[tmp["current"]]))[1:3]

    status = "✅ Знаю"
    if call.data == "not_know":
        status = "📚 Выучить"
    elif call.data == "skip":
        status = "⏭ Пропущено"

    info_bar = f"<i>{status}</i> |  <b>Вопрос {tmp['current'] + 1} / {len(children)}</b>"
    message = info_bar + f"\n\n<b>{question}</b>" + "\n" * 2 + answer

    await call.message.edit_text(text=message, reply_markup=None)

    tmp["current"] += 1
    await state.update_data(current=tmp["current"])

    if tmp["current"] == len(children):
        name = (await request.get_data_test(id=id))[1]
        message = f"📊 Результат прохождения теста <i>{name}</i>\n\n"\
                f"<b>Выполнено {tmp['current']} \ {tmp['current']}</b>\n"\
                f"✅ <i>Знаю</i> <b>{tmp['know']}</b>\n📚 <i>Выучить</i> <b>{tmp['not_know']}</b>\n"\
                f"⏭ <i>Пропущено</i> <b>{tmp['skip']}</b>\n"

        await call.message.answer(text=message, reply_markup=None)
        await state.clear()
        await call.answer()

        return

    question = (await request.get_data_test(children[tmp["current"]]))[1]

    message = f"✅ <i>Знаю {tmp['know']}</i> | 📚 <i>Выучить {tmp['not_know']}</i> | ⏭ <i>Пропущено {tmp['skip']}</i> | <b>Вопрос {tmp['current'] + 1} / {len(children)}</b>"\
        f"\n\n<b>{question}</b>"

    await call.message.answer(text=message, reply_markup=await inline_kb.get_inline_keyboard_test())
    await call.answer()


async def get_answer_test(call: CallbackQuery, bot: Bot, state: FSMContext, request: Request):
    tmp = await state.get_data()
    id = tmp["test"]

    children = (await request.get_data_test(id=id))[3]
    question, answer = (await request.get_data_test(children[tmp["current"]]))[1:3]

    message = f"✅ <i>Знаю {tmp['know']}</i> | 📚 <i>Выучить {tmp['not_know']}</i> | ⏭ <i>Пропущено {tmp['skip']}</i> | <b>Вопрос {tmp['current'] + 1} / {len(children)}</b>\n\n" +\
        (answer if call.data == "show_answer" else question)

    await call.message.edit_text(text=message, reply_markup=await inline_kb.get_inline_keyboard_test(show_answer=call.data == "show_question"))
    await call.answer()
        

async def get_ignore(message: Message, bot: Bot, state: FSMContext, request: Request):
    await message.delete()
    await message.answer(text="Во время выполнения тестирования нельзя выполнять другие команды."
                              "Для досрочного завершения тестирования /cancel")


async def get_stop_confirm(message: Message, bot: Bot, state: FSMContext, request: Request):
    await message.delete()
    await message.answer(text="Завершить тестирование досрочно?", reply_markup=await inline_kb.get_stop_test())


async def stop_test(call: CallbackQuery, bot: Bot, state: FSMContext, request: Request):
    await call.message.delete()

    # async with ChatActionSender.typing(chat_id=call.message.chat.id, bot=bot, initial_sleep=0.5):
    if call.data == "stop_test":
        tmp = await state.get_data()
        id = tmp["test"]
        name, _, children = (await request.get_data_test(id=id))[1:]
        message = f"📊 Результат прохождения теста \"{name}\"\n\n"\
                f"<b>Выполнено {tmp['current']} \ {len(children)}</b>\n"\
                f"✅ <i>Знаю</i> <b>{tmp['know']}</b>\n📚 <i>Выучить</i> <b>{tmp['not_know']}</b>\n"\
                f"⏭ <i>Пропущено</i> <b>{tmp['skip']}</b>\n"

        await call.message.answer(text=message)
        await state.clear()
        await call.answer()
        return

    await call.answer()
