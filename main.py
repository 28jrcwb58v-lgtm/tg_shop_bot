import os
import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from mock_data import ORDERS_DB, STATUSES

load_dotenv()
BOT_TOKEN= os.getenv("BOT_TOKEN")
ADMIN_IDS=[1898742616, 713534340, 673063761]


bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in ADMIN_IDS

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Список заказов")],
            [KeyboardButton(text="🔄 Обновить данные")]
        ],
        resize_keyboard=True
    )

def get_order_list_keyboard():
    buttons = []
    for order_id, data in ORDERS_DB.items():
        text = f"Заказ №{order_id} | {data['status']} | {data['total']}₽"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"view_{order_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_order_detail_keyboard(order_id):
    buttons = []
    row = []
    for status in STATUSES:
        row.append(InlineKeyboardButton(text=status, callback_data=f"status_{order_id}_{status}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text=" Назад к списку", callback_data="back_to_list")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(Command("start"), AdminFilter())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Приветствую, Администратор!\nЯ бот для управления заказами.\nИспользуйте меню ниже.",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "📦 Список заказов", AdminFilter())
async def show_orders(message: Message):
    await message.answer("📦 Актуальные заказы:", reply_markup=get_order_list_keyboard())

@router.message(F.text == "🔄 Обновить данные", AdminFilter())
async def refresh_data(message: Message):
    await message.answer("✅ Данные обновлены!", reply_markup=get_main_keyboard())

@router.callback_query(F.data.startswith("view_"), AdminFilter())
async def process_order_view(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[1])
    order = ORDERS_DB.get(order_id)
    if not order:
        await callback.answer("Заказ не найден", show_alert=True)
        return
    
    text = (
        f"🧾 <b>Заказ №{order['id']}</b>\n\n"
        f"📧 <b>Почта клиента:</b> {order['client_email']}\n"
        f"🛒 <b>Состав:</b> {order['items']}\n"
        f"🚦 <b>Статус:</b> {order['status']}\n\n"
        f" <b>Ключ:</b> {order['total']} \n"

        f"Выберите новый статус:"
    )
    await callback.message.edit_text(text, reply_markup=get_order_detail_keyboard(order_id), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("status_"), AdminFilter())
async def process_status_change(callback: CallbackQuery):
    parts = callback.data.split("_", 2)
    order_id = int(parts[1])
    new_status = parts[2]
    if order_id in ORDERS_DB:
        old_status = ORDERS_DB[order_id]["status"]
        ORDERS_DB[order_id]["status"] = new_status
        await callback.message.edit_text(
            f"✅ Статус изменён!\n{old_status} ➡️ {new_status}",
            reply_markup=get_order_detail_keyboard(order_id)
        )
    await callback.answer()

@router.callback_query(F.data == "back_to_list", AdminFilter())
async def back_to_list(callback: CallbackQuery):
    await callback.message.edit_text("📦 Актуальные заказы:", reply_markup=get_order_list_keyboard())
    await callback.answer()

@router.message(~AdminFilter())
async def not_admin(message: Message):
    await message.answer("⛔ Доступ запрещён!")

async def main():
    print("✅ Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен")
