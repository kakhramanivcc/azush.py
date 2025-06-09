import telebot
from telebot import types
from datetime import datetime

TOKEN = "7512582232:AAHDXhengLRkMmrRJnojj-FbLQD5KfPaZXQ"
ADMIN_ID = 7339338932  # int bo'lishi kerak
ADMIN_USERNAME = "@adibaparfyume"

CHANNELS = ['@abbossheyx_oyin']  # Kanallar ro'yxati

bot = telebot.TeleBot(TOKEN)
user_data = {}

# Kanalga obuna ekanligini tekshirish funksiyasi
def check_subscriptions(user_id):
    for ch in CHANNELS:
        res = bot.get_chat_member(ch, user_id)
        if res.status not in ['member', 'creator', 'administrator']:
            return False
    return True

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.InlineKeyboardMarkup()
    for ch in CHANNELS:
        markup.add(types.InlineKeyboardButton("Obuna bo'lish", url=f"https://t.me/{ch[1:]}"))
    markup.add(types.InlineKeyboardButton("✅ Obuna bo‘ldim", callback_data="check_subs"))
    bot.send_message(message.chat.id, "Botdan foydalanish uchun pastdagi kanallarga obuna bo‘ling:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def handle_subscription_check(call):
    if check_subscriptions(call.from_user.id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🛍 Braslet xarid qilish")
        markup.add("👤 Mening profilim", "💬 Admin bilan bog‘lanish")
        bot.send_message(call.message.chat.id, "Tabriklaymiz! Siz kanallarga muvaffaqiyatli obuna bo‘ldingiz!", reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "Iltimos, barcha kanallarga obuna bo‘ling.", show_alert=True)

@bot.message_handler(func=lambda m: m.text == "🛍 Braslet xarid qilish")
def braslet_info(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Buyurtma berish", callback_data="order_now"))
    bot.send_message(message.chat.id, "🖤 Brend Shop Braslet\n💰 Narxi: 19 000 so'm", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "order_now")
def order_process(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💳 Tolov qilish", callback_data="pay_now"))
    bot.send_message(call.message.chat.id, "Iltimos, braslet uchun tolov qiling:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "pay_now")
def payment_info(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Tolov chekini yuborish", callback_data="upload_check"))
    text = "8600 1129 2770 7000\nKhodjiev Kakhraman\n\nIltimos tolov qilganingizdan so‘ng chekni yuboring."
    bot.send_message(call.message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "upload_check")
def ask_for_check(call):
    bot.send_message(call.message.chat.id, "Iltimos, shu yerga tolov chek rasmini yuboring va tasdiqlanishini kuting.")
    bot.register_next_step_handler(call.message, receive_check)

def receive_check(message):
    if message.photo:
        user_id = message.from_user.id
        user_data[user_id] = {
            'check_msg_id': message.message_id,
            'username': message.from_user.username or "No username"
        }
        bot.send_message(message.chat.id, "Iltimos, chek tasdiqlanishini kuting.")
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Tasdiqlandi", callback_data=f"confirm_{user_id}"),
            types.InlineKeyboardButton("❌ Tasdiqlanmadi", callback_data=f"reject_{user_id}")
        )
        bot.send_message(ADMIN_ID,
                         f"🆕 Yangi tolov chek keldi!\nFoydalanuvchi ID: {user_id}\nUsername: @{user_data[user_id]['username']}\nChekni tasdiqlang:",
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Rasm yuboring, iltimos.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_") or call.data.startswith("reject_"))
def handle_admin_response(call):
    user_id = int(call.data.split("_")[1])
    if call.data.startswith("confirm_"):
        bot.send_message(user_id, "✅ Tolov tasdiqlandi!\n\nIsm Familya, telefon raqamingiz va manzilingizni yuboring. Tez orada siz bilan bog‘lanamiz!")
        bot.send_message(call.message.chat.id, f"✅ Raxmat! Siz {user_id} uchun tolovni tasdiqladingiz.")
        bot.register_next_step_handler_by_chat_id(user_id, collect_info)
    else:
        bot.send_message(user_id, "❌ Tolov rad etildi. Iltimos to‘g‘ri chek yuboring.")
        bot.send_message(call.message.chat.id, f"❌ Siz {user_id} uchun tolovni rad qildingiz.")

def collect_info(message):
    user_id = message.from_user.id
    text = message.text.strip()

    # Oddiy tekshiruv: ism, telefon va manzilni vergul bilan ajratib olish
    if ',' not in text:
        bot.send_message(user_id, "Iltimos, Ism Familya, Telefon raqam va Manzilingizni vergul bilan ajratib yuboring (masalan: Ali Vali, +998901234567, Toshkent).")
        bot.register_next_step_handler_by_chat_id(user_id, collect_info)
        return

    parts = [p.strip() for p in text.split(',')]
    if len(parts) < 3:
        bot.send_message(user_id, "To‘liq maʼlumot yuboring: Ism Familya, Telefon raqam, Manzil.")
        bot.register_next_step_handler_by_chat_id(user_id, collect_info)
        return

    # Oddiy telefon raqam tekshiruvi
    if not (parts[1].startswith('+') and parts[1][1:].isdigit()):
        bot.send_message(user_id, "Telefon raqamni +998XXYYYYYYY formatida yozing.")
        bot.register_next_step_handler_by_chat_id(user_id, collect_info)
        return

    user_data[user_id]['info'] = {
        'name': parts[0],
        'phone': parts[1],
        'address': parts[2],
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    bot.send_message(user_id, "✅ Ma'lumot qabul qilindi!")
    bot.send_message(user_id, "🏠 Asosiy menyu", reply_markup=main_menu())

    # Adminga to‘liq ma’lumot yuborish
    info_text = (
        f"📩 Yangi buyurtma!\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Username: @{user_data[user_id]['username']}\n"
        f"🕒 Vaqt: {user_data[user_id]['info']['time']}\n\n"
        f"👤 Ism Familya: {user_data[user_id]['info']['name']}\n"
        f"📞 Telefon: {user_data[user_id]['info']['phone']}\n"
        f"🏠 Manzil: {user_data[user_id]['info']['address']}"
    )
    bot.send_message(ADMIN_ID, info_text)

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🛍 Braslet xarid qilish")
    markup.add("👤 Mening profilim", "💬 Admin bilan bog‘lanish")
    return markup

@bot.message_handler(func=lambda m: m.text == "💬 Admin bilan bog‘lanish")
def contact_admin(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Admin bilan bog‘lanish", url="https://t.me/adibaparfyume"))
    bot.send_message(message.chat.id, "Savollaringiz bo‘lsa, admin bilan bog‘lanishingiz mumkin:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "👤 Mening profilim")
def my_profile(message):
    user_id = message.from_user.id
    info = user_data.get(user_id, {}).get('info', "Hozircha ma'lumot mavjud emas.")
    if isinstance(info, dict):
        text = (f"📝 Siz haqingizda:\n\n"
                f"Ism Familya: {info.get('name', '-')}\n"
                f"Telefon: {info.get('phone', '-')}\n"
                f"Manzil: {info.get('address', '-')}\n"
                f"Soat: {info.get('time', '-')}")
    else:
        text = info
    bot.send_message(message.chat.id, text)

bot.polling()