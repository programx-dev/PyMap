from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.utils.statequizze import StepsQuizze
from core.utils.callbackdata import Quizze
from aiogram.types import CallbackQuery
from aiogram import Bot
from core.utils.dbconnect import Request
from core.keyboards import inline
import logging


async def init_quizze(call: CallbackQuery, bot: Bot, callback_data: Quizze, state: FSMContext, request: Request):
    id = callback_data.id

    await state.set_state(StepsQuizze.GET_QUZZE)
    await state.update_data(quizze=id)
    await state.update_data(know=0)
    await state.update_data(didnt_know=0)
    await state.update_data(current=0)

    children = (await request.get_quizze(id=id))[3]
    question = (await request.get_quizze(children[0]))[1]

    info_bar = f"✅ Знаю 0 | 📚 Выучить 0 | 1 / {len(children)}"
    message = info_bar + "\n" * 2 + question

    await call.message.answer(text=message, reply_markup=await inline.get_inline_keyboard_question())
    await call.answer()


async def get_quizze(call: CallbackQuery, bot: Bot, state: FSMContext, request: Request):
    tmp = await state.get_data()
    id = tmp["quizze"]

    if call.data == "know":
        tmp["know"] += 1
        await state.update_data(know=tmp["know"])
    elif call.data == "dont_know":
        tmp["didnt_know"] += 1
        await state.update_data(didnt_know=tmp["didnt_know"])

    children = (await request.get_quizze(id=id))[3]
    question, answer = (await request.get_quizze(children[tmp["current"]]))[1:3]

    status = "✅ Знаю" if call.data == "know" else "📚Выучить"
    info_bar = f"{status} | {tmp['current'] + 1} / {len(children)}"
    message = info_bar + "\n" * 2 + question + "\n" * 2 + answer

    await call.message.edit_text(text=message, reply_markup=None)

    tmp["current"] += 1
    await state.update_data(current=tmp["current"])

    children = (await request.get_quizze(id=id))[3]

    if tmp["current"] == len(children):
        name = (await request.get_quizze(id=id))[1]
        message = f"Результат прохождения теста \"{name}\"\n\n"\
                  f"Выполнено {tmp['current']} \ {tmp['current']}\n"\
                  f"✅ Знаю {tmp['know']}\n📚 Выучить {tmp['didnt_know']}\n"

        await call.message.edit_text(text=message, reply_markup=None)
        await state.clear()
        await call.answer()

        return

    question = (await request.get_quizze(children[tmp["current"]]))[1]

    message = f"✅ Знаю {tmp['know']} | 📚Выучить {tmp['didnt_know']} | {tmp['current'] + 1} / {len(children)}\n\n" + question

    await call.message.answer(text=message, reply_markup=await inline.get_inline_keyboard_question())
    await call.answer()


async def get_answer_quizze(call: CallbackQuery, bot: Bot, state: FSMContext, request: Request):
    tmp = await state.get_data()
    id = tmp["quizze"]

    children = (await request.get_quizze(id=id))[3]
    question, answer = (await request.get_quizze(children[tmp["current"]]))[1:3]

    message = f"✅ Знаю {tmp['know']} | 📚 Выучить {tmp['didnt_know']} | {tmp['current'] + 1} / {len(children)}\n\n" + \
        (answer if call.data == "show_answer" else question)

    await call.message.edit_text(text=message, reply_markup=await inline.get_inline_keyboard_question(show_answer=call.data == "show_question"))
    await call.answer()


async def get_ignore(message: Message, bot: Bot, state: FSMContext, request: Request):
    await message.delete()
    await message.answer(text="Во время выполнения тестирования нельзя выполнять другие команды."
                              "Для досрочного завершения тестирования /cancel")


async def get_stop_confirm(message: Message, bot: Bot, state: FSMContext, request: Request):
    await message.delete()
    await message.answer(text="Завершить тест досрочно?", reply_markup=await inline.get_stop_test())


async def stop_test(call: CallbackQuery, bot: Bot, state: FSMContext, request: Request):
    await call.message.delete()

    if call.data == "stop_test":
        tmp = await state.get_data()
        id = tmp["quizze"]
        name, _, children = (await request.get_quizze(id=id))[1:]
        message = f"Результат прохождения теста \"{name}\"\n\n"\
                  f"Выполнено {tmp['current']} \ {len(children)}\n"\
                  f"✅ Знаю {tmp['know']}\n📚 Выучить {tmp['didnt_know']}\n"

        await call.message.answer(text=message)
        await state.clear()
        await call.answer()
        return

    await call.answer()
