from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.utils.states import StepsQuizze
from core.utils.callbackdata import Quizze
from aiogram.types import CallbackQuery, PollAnswer
from aiogram import Bot
from core.utils.dbconnect import Request
from core.keyboards import inline
import logging
from aiogram.utils.chat_action import ChatActionSender


async def get_quizze(call: CallbackQuery, bot: Bot, callback_data: Quizze, state: FSMContext, request: Request):
    await call.message.delete()

    # async with ChatActionSender.typing(chat_id=call.message.chat.id, bot=bot, initial_sleep=0.5):
    await state.set_state(StepsQuizze.QUIZZE)

    id = callback_data.id
    question, answers, photo_id, solution, correct_answer = (await request.get_data_quizze(id))[1:]

    await call.message.answer_photo(photo=photo_id)
    poll = await call.message.answer_poll(question=f"#{id} {question}", options=answers, type="quiz", correct_option_id=correct_answer,
                                        explanation=solution, is_anonymous=False)

    await state.update_data(poll_id=poll.poll.id)
    await state.update_data(quizze_id=id)
    await state.update_data(correct_answer=correct_answer)

    await call.answer()


async def get_quizze_answer(poll_answer: PollAnswer, bot: Bot, state: FSMContext, request: Request):
    if await state.get_state() != str(StepsQuizze.QUIZZE.state):
        await bot.send_message(poll_answer.user.id, "⚠️ Я могу узнать результат только последней отправленной викторины")
        return

    tmp = await state.get_data()

    if tmp["poll_id"] == poll_answer.poll_id:
        if poll_answer.option_ids[0] == (await state.get_data())["correct_answer"]:
            await bot.send_message(poll_answer.user.id, "🥳 Вы верно ответили на викторину")
            await request.add_data_correct_quizzes(user_id=poll_answer.user.id,
                                                   user_name=poll_answer.user.first_name,
                                                   quizze_id=tmp["quizze_id"])
        else:
            await bot.send_message(poll_answer.user.id, "🙁 Вы неверно ответили на викторину")
            await request.add_data_wrong_quizzes(user_id=poll_answer.user.id,
                                                 user_name=poll_answer.user.first_name,
                                                 quizze_id=tmp["quizze_id"])
        await state.clear()
    else:
        await bot.send_message(poll_answer.user.id, "⚠️ Я могу узнать результат только последней отправленной викторины")
