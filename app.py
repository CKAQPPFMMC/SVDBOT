"""
================================================================================
 TASHAN GAME DEMO ACCOUNT SELLER BOT - FIXED
================================================================================
"""

import telebot
from telebot import types
import json
import os
import threading
from datetime import datetime, date

# ==============================================================================
# CONFIGURATION
# ==============================================================================

BOT_TOKEN = "8949992525:AAGG6QXlRTZXa1264kD0iukXd9AmLWCvf0M"
ADMIN_ID = 8587243537

bot = telebot.TeleBot(BOT_TOKEN)

# ==============================================================================
# DATABASE
# ==============================================================================

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
UTRS_FILE = os.path.join(DATA_DIR, "utrs.json")
CHAT_MAP_FILE = os.path.join(DATA_DIR, "chat_map.json")

file_lock = threading.Lock()


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default
    return default


def save_json(path, data):
    with file_lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


users = load_json(USERS_FILE, {})
accounts = load_json(ACCOUNTS_FILE, [])
settings = load_json(
    SETTINGS_FILE,
    {
        "price": "₹199",
        "button_name": "TASHANWIN GAME",
        "qr_file_id": "",
        "upi_id": "",
        "crypto_address": "",
        "crypto_qr_file_id": "",
        "crypto_network": "BEP20",
        "maintenance_mode": "0",
        "auto_payment": "1"
    },
)
utrs = load_json(UTRS_FILE, {})
chat_map = load_json(CHAT_MAP_FILE, {})


def save_users():
    save_json(USERS_FILE, users)


def save_accounts():
    save_json(ACCOUNTS_FILE, accounts)


def save_settings():
    save_json(SETTINGS_FILE, settings)


def save_utrs():
    save_json(UTRS_FILE, utrs)


def save_chat_map():
    save_json(CHAT_MAP_FILE, chat_map)


user_state = {}
admin_state = {"step": None, "data": {}}


def reset_admin_state():
    admin_state["step"] = None
    admin_state["data"] = {}


def get_or_create_user(message):
    uid = str(message.from_user.id)
    now = datetime.now()
    if uid not in users:
        users[uid] = {
            "user_id": message.from_user.id,
            "username": message.from_user.username or "N/A",
            "first_name": message.from_user.first_name or "N/A",
            "join_date": now.strftime("%Y-%m-%d"),
            "join_time": now.strftime("%H:%M:%S"),
            "status": "active",
        }
        save_users()
    else:
        changed = False
        new_username = message.from_user.username or "N/A"
        new_first_name = message.from_user.first_name or "N/A"
        if users[uid].get("username") != new_username:
            users[uid]["username"] = new_username
            changed = True
        if users[uid].get("first_name") != new_first_name:
            users[uid]["first_name"] = new_first_name
            changed = True
        if changed:
            save_users()
    return users[uid]


def is_blocked(user_id):
    record = users.get(str(user_id))
    return bool(record and record.get("status") == "blocked")


def new_utr_id():
    return str(int(datetime.now().timestamp() * 1000))


def safe_send(chat_id, text, **kwargs):
    try:
        bot.send_message(chat_id, text, **kwargs)
        return True
    except Exception:
        return False


# ==============================================================================
# KEYBOARDS
# ==============================================================================

CUSTOM_EMOJI_ID = "6052964261418769099"

CUSTOM_EMOJI_IDS = {'6053362469311617342': '👀', '6053026611459004128': '🙂', '6053061091456457277': '⚡️', '6052879414339837562': '☄️', '6339201691140758295': '🛍', '6053376986301078841': '⛔️', '6052902989415324360': '🚫', '6053062818033309122': '❗️', '6053178490092525561': '‼️', '6053354746960419401': '⁉️', '6339378519239303549': '❓', '6052867933892254014': '⚠️', '6053315100117309042': '⚠️', '6339280615459789282': '🌐', '6052964261418769099': '💬', '6053074925546118479': '💭', '6053337141889471994': '❓', '6053234303192537471': '📊', '6053325330729409422': '🔼', '6053078043692374997': '🔽', '6339230892623403884': '🕯', '6053216517732964810': '📈', '6053183296160930683': '📉', '6053202116707622090': '✔️', '6052869226677410910': '❌', '6053030717447739471': '🆒', '6053142399482339205': '🔔', '6053117209499146201': '🥸', '6053323372224323095': '🤡', '6053242669788830902': '🫦', '6052991826518873591': '📌', '6053104294532487625': '💵', '6052982111302850548': '💸', '6338887905125079808': '💸', '6052949735839374723': '💸', '6339075152814284503': '💸', '6339033053544848591': '💸', '6053387526150823179': '💱', '6053128350644311646': '▶️', '6053134711490878159': '🔴', '6053400449707416241': '🟢', '6052883185321121442': '➡️'}


def styled_button(text, style="primary", emoji_id=None):
    """Create a Telegram reply-keyboard button with color + custom emoji icon."""
    button = types.KeyboardButton(text)
    button.icon_custom_emoji_id = str(emoji_id or CUSTOM_EMOJI_ID)
    button.style = style
    return button


def emoji_id_for(text):
    """Pick a matching custom emoji ID while keeping the original button text unchanged."""
    mapping = {
        "➕ Set QR Code": "6053376986301078841",
        "📥 Set Account Credentials": "6053234303192537471",
        "💰 Set Price": "6053104294532487625",
        "📝 Pending UTRs": "6053074925546118479",
        "✏️ Set Button Name": "6052991826518873591",
        "👥 Users": "6053362469311617342",
        "🚫 Block User": "6052902989415324360",
        "✅ Unblock User": "6053202116707622090",
        "📋 Blocked Users": "6053376986301078841",
        "📢 Broadcast": "6053142399482339205",
        "💳 Payment Settings": "6053387526150823179",
        "🔧 Maintenance Mode": "6052867933892254014",
        "🔙 Exit": "6052883185321121442",
        "💬 Chat with Admin": "6052964261418769099",
        "🔹 Set UPI ID": "6053387526150823179",
        "🔹 Set Crypto Address": "6339280615459789282",
        "🔹 Set Crypto QR Code": "6339201691140758295",
        "🔹 Toggle Auto Payment": "6053400449707416241",
        "🔙 Back to Admin Menu": "6052883185321121442",
    }
    return mapping.get(text, CUSTOM_EMOJI_ID)


def button_style(text):
    """Pick a consistent color for admin buttons without changing their text."""
    if any(word in text for word in ["Block", "Broadcast", "Maintenance"]):
        return "danger"
    if any(word in text for word in ["Set QR", "Set Account", "Set Price", "Payment Settings", "Set Button"]):
        return "primary"
    return "success"


ADMIN_MENU_BUTTONS = [
    "➕ Set QR Code",
    "📥 Set Account Credentials",
    "💰 Set Price",
    "📝 Pending UTRs",
    "✏️ Set Button Name",
    "👥 Users",
    "🚫 Block User",
    "✅ Unblock User",
    "📋 Blocked Users",
    "📢 Broadcast",
    "💳 Payment Settings",
    "🔧 Maintenance Mode",
    "🔙 Exit",
]

CHAT_BUTTON_TEXT = "💬 Chat with Admin"


def main_menu_keyboard():
    """LEFT: Game Button | RIGHT: Chat with Admin"""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        styled_button(settings.get("button_name", "TASHANWIN GAME"), "success", "6339201691140758295"),
        styled_button(CHAT_BUTTON_TEXT, "primary", emoji_id_for(CHAT_BUTTON_TEXT))
    )
    return kb


def admin_menu_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(*[styled_button(t, button_style(t), emoji_id_for(t)) for t in ADMIN_MENU_BUTTONS])
    return kb


def utr_action_keyboard(utr_id):
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"approve:{utr_id}"),
        types.InlineKeyboardButton("⏳ Pending", callback_data=f"pending:{utr_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"reject:{utr_id}"),
    )
    return kb


def payment_options_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("💳 UPI", callback_data="pay_upi"),
        types.InlineKeyboardButton("🪙 Crypto (BEP20)", callback_data="pay_crypto"),
    )
    return kb


# ==============================================================================
# /start COMMAND
# ==============================================================================

@bot.message_handler(commands=["start"])
def cmd_start(message):
    if settings.get("maintenance_mode") == "1":
        bot.send_message(
            message.chat.id,
            "🔧 <b>Bot is under maintenance</b>\n\nPlease check back later.",
            parse_mode="HTML"
        )
        return

    user_data = get_or_create_user(message)
    uname = user_data.get("first_name", "User")

    if is_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 You have been blocked by Admin.")
        return

    user_state.pop(message.from_user.id, None)

    button_name = settings.get("button_name", "TASHANWIN GAME")
    price = settings.get("price", "N/A")

    welcome_text = (
        f"👋 Welcome {uname}!\n\n"
        f"📢 We provide demo accounts for *{button_name}*.\n\n"
        f"💡 *How it works:*\n"
        f"1️⃣ Click '{button_name}'\n"
        f"2️⃣ Pay ₹{price} via UPI or Crypto (BEP20)\n"
        f"3️⃣ Submit 12-digit UTR/Transaction ID & payment screenshot\n"
        f"4️⃣ Get approved & receive login details\n\n"
        "Tap a button below to get started 👇"
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


# ==============================================================================
# /admin COMMAND
# ==============================================================================

@bot.message_handler(commands=["admin"])
def cmd_admin(message):
    if message.from_user.id != ADMIN_ID:
        return

    reset_admin_state()
    bot.send_message(
        message.chat.id,
        "🛠️ <b>Admin Panel</b>\n\nSelect an option below:",
        parse_mode="HTML",
        reply_markup=admin_menu_keyboard(),
    )


# ==============================================================================
# MASTER TEXT HANDLER
# ==============================================================================

@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if settings.get("maintenance_mode") == "1" and user_id != ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "🔧 <b>Bot is under maintenance</b>\n\nPlease check back later.",
            parse_mode="HTML"
        )
        return

    # Admin reply to user
    if user_id == ADMIN_ID and message.reply_to_message:
        handle_admin_chat_reply(message)
        return

    # Admin step
    if user_id == ADMIN_ID and admin_state["step"]:
        handle_admin_step(message)
        return

    # Admin menu
    if user_id == ADMIN_ID and text in ADMIN_MENU_BUTTONS:
        handle_admin_menu(message)
        return

    if user_id == ADMIN_ID:
        return

    # --- USER ---
    get_or_create_user(message)

    if is_blocked(user_id):
        bot.send_message(message.chat.id, "🚫 You have been blocked by Admin.")
        return

    # Chat mode - forward and auto back to main menu
    if user_state.get(user_id) == "chat_mode":
        forward_to_admin(message)
        user_state.pop(user_id, None)
        bot.send_message(
            message.chat.id,
            "✅ Message sent to Admin.\n\n🔙 Returning to main menu...",
            reply_markup=main_menu_keyboard()
        )
        return

    # UTR submission
    if user_state.get(user_id) == "awaiting_utr":
        process_utr_submission(message)
        return

    # Game button
    if text == settings.get("button_name", "TASHANWIN GAME"):
        start_buy_flow(message)
        return

    # Chat button
    if text == CHAT_BUTTON_TEXT:
        user_state[user_id] = "chat_mode"
        bot.send_message(
            message.chat.id,
            "💬 You're now chatting with Admin.\n"
            "Type your message and it will be forwarded to Admin.\n"
            "Admin will reply here shortly.\n\n"
            "⚠️ After sending message, you'll return to main menu.",
            reply_markup=main_menu_keyboard()
        )
        return

    bot.send_message(
        message.chat.id,
        "🤖 Please use the buttons below to continue.",
        reply_markup=main_menu_keyboard(),
    )


def start_buy_flow(message):
    if not settings.get("qr_file_id"):
        bot.send_message(
            message.chat.id,
            f"⚠️ QR Code is not set up yet. Please contact Admin via '{CHAT_BUTTON_TEXT}'.",
        )
        return

    caption = (
        f"💰 <b>Price:</b> {settings.get('price', 'N/A')}\n\n"
        "📱 Please select your payment method below:"
    )
    bot.send_photo(
        message.chat.id,
        settings["qr_file_id"],
        caption=caption,
        parse_mode="HTML",
        reply_markup=payment_options_keyboard(),
    )


# ==============================================================================
# PAYMENT METHOD SELECTION
# ==============================================================================

@bot.callback_query_handler(func=lambda call: call.data in ["pay_upi", "pay_crypto"])
def handle_payment_method(call):
    user_id = call.from_user.id

    if is_blocked(user_id):
        bot.answer_callback_query(call.id, "🚫 You are blocked.")
        return

    payment_type = "UPI" if call.data == "pay_upi" else "Crypto (BEP20)"
    
    user_state[user_id] = "awaiting_utr"
    if not hasattr(handle_payment_method, "payment_types"):
        handle_payment_method.payment_types = {}
    handle_payment_method.payment_types[str(user_id)] = payment_type

    if payment_type == "UPI":
        upi_id = settings.get("upi_id", "")
        qr_text = "💳 Scan QR code above and pay via UPI"
        if upi_id:
            qr_text = f"💳 Pay via UPI ID: `{upi_id}`"
        if settings.get("qr_file_id"):
            bot.send_photo(
                call.message.chat.id,
                settings["qr_file_id"],
                caption=f"💳 <b>UPI Payment</b>\n\n{qr_text}\n\n💰 Price: {settings.get('price', 'N/A')}",
                parse_mode="HTML"
            )
    else:
        crypto_address = settings.get("crypto_address", "")
        crypto_network = settings.get("crypto_network", "BEP20")
        qr_text = f"🪙 Send via {crypto_network} Network"
        if crypto_address:
            qr_text = f"🪙 Send to Address:\n<code>{crypto_address}</code>\n\n🌐 Network: {crypto_network}"
        
        if settings.get("crypto_qr_file_id"):
            bot.send_photo(
                call.message.chat.id,
                settings["crypto_qr_file_id"],
                caption=f"🪙 <b>Crypto Payment</b>\n\n{qr_text}\n\n💰 Price: {settings.get('price', 'N/A')}",
                parse_mode="HTML"
            )
        else:
            bot.send_message(
                call.message.chat.id,
                f"🪙 <b>Crypto Payment</b>\n\n{qr_text}\n\n💰 Price: {settings.get('price', 'N/A')}\n\n⚠️ Crypto QR Code not set by Admin.",
                parse_mode="HTML"
            )

    bot.answer_callback_query(call.id)
    
    bot.send_message(
        call.message.chat.id,
        "1️⃣ Complete the payment using the QR code above.\n"
        "2️⃣ Send your <b>12-digit UTR/Transaction ID</b>.\n"
        "3️⃣ Then send a screenshot of your payment.\n\n"
        "📌 Make sure the ID is correct before submitting.",
        parse_mode="HTML"
    )


# ==============================================================================
# UTR SUBMISSION
# ==============================================================================

def process_utr_submission(message):
    user_id = message.from_user.id
    utr_text = message.text.strip()

    if not (utr_text.isdigit() and len(utr_text) == 12):
        bot.send_message(
            message.chat.id,
            "❌ Invalid UTR/Transaction ID.\n"
            "Please send a valid *12-digit* UTR/Transaction ID.",
            parse_mode="Markdown",
        )
        return

    user_state[user_id] = "awaiting_screenshot"
    if not hasattr(process_utr_submission, "utr_data"):
        process_utr_submission.utr_data = {}
    process_utr_submission.utr_data[str(user_id)] = utr_text

    bot.send_message(
        message.chat.id,
        f"✅ UTR/Transaction ID `{utr_text}` received!\n\n"
        "📸 Now please send a screenshot of your payment.\n"
        "Send the screenshot as a photo.",
        parse_mode="Markdown",
    )


# ==============================================================================
# PHOTO HANDLER
# ==============================================================================

@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    user_id = message.from_user.id

    if user_id == ADMIN_ID and message.reply_to_message:
        handle_admin_chat_reply(message)
        return

    if user_id == ADMIN_ID and admin_state["step"] == "set_qr":
        file_id = message.photo[-1].file_id
        settings["qr_file_id"] = file_id
        save_settings()
        reset_admin_state()
        bot.send_message(
            message.chat.id,
            "✅ QR Code updated!",
            reply_markup=admin_menu_keyboard(),
        )
        return

    if user_id == ADMIN_ID and admin_state["step"] == "set_crypto_qr":
        file_id = message.photo[-1].file_id
        settings["crypto_qr_file_id"] = file_id
        save_settings()
        reset_admin_state()
        bot.send_message(
            message.chat.id,
            "✅ Crypto QR Code updated!",
            reply_markup=admin_menu_keyboard(),
        )
        return

    if user_id == ADMIN_ID:
        return

    get_or_create_user(message)
    if is_blocked(user_id):
        bot.send_message(message.chat.id, "🚫 You have been blocked by Admin.")
        return

    # Chat mode - forward and auto back
    if user_state.get(user_id) == "chat_mode":
        forward_to_admin(message)
        user_state.pop(user_id, None)
        bot.send_message(
            message.chat.id,
            "✅ Message sent to Admin.\n\n🔙 Returning to main menu...",
            reply_markup=main_menu_keyboard()
        )
        return

    if user_state.get(user_id) == "awaiting_screenshot":
        process_screenshot_submission(message)
        return

    bot.send_message(
        message.chat.id,
        "🤖 Please use the buttons below to continue.",
        reply_markup=main_menu_keyboard(),
    )


def process_screenshot_submission(message):
    user_id = message.from_user.id
    file_id = message.photo[-1].file_id

    utr_text = "N/A"
    if hasattr(process_utr_submission, "utr_data"):
        utr_text = process_utr_submission.utr_data.get(str(user_id), "N/A")

    payment_type = "UPI"
    if hasattr(handle_payment_method, "payment_types"):
        payment_type = handle_payment_method.payment_types.get(str(user_id), "UPI")

    user_record = users.get(str(user_id), {})
    utr_id = new_utr_id()
    now = datetime.now()

    utrs[utr_id] = {
        "utr_id": utr_id,
        "user_id": user_id,
        "username": user_record.get("username", "N/A"),
        "first_name": user_record.get("first_name", "N/A"),
        "utr": utr_text,
        "payment_type": payment_type,
        "screenshot_file_id": file_id,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "status": "Pending",
    }
    save_utrs()

    user_state.pop(user_id, None)
    if hasattr(process_utr_submission, "utr_data"):
        process_utr_submission.utr_data.pop(str(user_id), None)
    if hasattr(handle_payment_method, "payment_types"):
        handle_payment_method.payment_types.pop(str(user_id), None)

    bot.send_message(
        message.chat.id,
        "✅ Your payment has been submitted!\n"
        f"📱 Payment Method: {payment_type}\n"
        f"🆔 UTR/Transaction ID: `{utr_text}`\n"
        "🕒 Please wait while Admin verifies your payment.\n\n"
        "🔙 Returning to main menu...",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

    notify_admin_of_utr(utrs[utr_id])


def notify_admin_of_utr(record):
    text = format_utr_details(record)
    try:
        bot.send_message(
            ADMIN_ID,
            text,
            parse_mode="HTML",
            reply_markup=utr_action_keyboard(record["utr_id"]),
        )
        if record.get("screenshot_file_id"):
            bot.send_photo(
                ADMIN_ID,
                record["screenshot_file_id"],
                caption="📸 Payment Screenshot",
            )
    except Exception:
        pass


def format_utr_details(record):
    return (
        "🆕 <b>New Payment Submission</b>\n\n"
        f"👤 User ID: <code>{record['user_id']}</code>\n"
        f"🔖 Username: @{record.get('username', 'N/A')}\n"
        f"📛 Name: {record.get('first_name', 'N/A')}\n"
        f"📱 Payment Method: {record.get('payment_type', 'N/A')}\n"
        f"💳 UTR/Transaction ID: <code>{record['utr']}</code>\n"
        f"📅 Date: {record['date']}\n"
        f"⏰ Time: {record['time']}\n"
        f"📊 Status: {record['status']}"
    )


def forward_to_admin(message):
    """Forward user message with full details - shows current message time"""
    user_id = message.from_user.id
    user_record = users.get(str(user_id), {})
    
    # Current time when user sent the message
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%d-%m-%Y")
    
    user_info = (
        f"📩 <b>New Message from User</b>\n\n"
        f"👤 User ID: <code>{user_id}</code>\n"
        f"🔖 Username: @{user_record.get('username', 'N/A')}\n"
        f"📛 Name: {user_record.get('first_name', 'N/A')}\n"
        f"📅 Message Date: {current_date}\n"
        f"⏰ Message Time: {current_time}\n"
        f"📊 Status: {user_record.get('status', 'active')}\n"
        f"{'─' * 30}\n\n"
        f"💬 <b>Message:</b>\n"
    )
    
    try:
        bot.send_message(ADMIN_ID, user_info, parse_mode="HTML")
        forwarded = bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        chat_map[str(forwarded.message_id)] = user_id
        save_chat_map()
    except Exception as e:
        print(f"Forward error: {e}")
        bot.send_message(
            message.chat.id, 
            "⚠️ Could not deliver your message. Please try again."
        )


def handle_admin_chat_reply(message):
    replied_id = str(message.reply_to_message.message_id)
    target_user_id = chat_map.get(replied_id)

    if not target_user_id:
        bot.send_message(
            message.chat.id,
            "⚠️ Could not find the original user.",
        )
        return

    try:
        bot.copy_message(target_user_id, message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "✅ Reply sent.")
    except Exception:
        bot.send_message(message.chat.id, "❌ Failed to send reply.")


# ==============================================================================
# ADMIN MENU
# ==============================================================================

def handle_admin_menu(message):
    text = message.text

    if text == "➕ Set QR Code":
        admin_state["step"] = "set_qr"
        bot.send_message(message.chat.id, "📷 Please send the new QR Code image.")

    elif text == "📥 Set Account Credentials":
        admin_state["step"] = "set_account_username"
        admin_state["data"] = {}
        bot.send_message(message.chat.id, "👤 Send the account *Username*:", parse_mode="Markdown")

    elif text == "💰 Set Price":
        admin_state["step"] = "set_price"
        bot.send_message(message.chat.id, f"💰 Current price: {settings.get('price')}\nSend the new price:")

    elif text == "📝 Pending UTRs":
        show_pending_utrs(message)

    elif text == "✏️ Set Button Name":
        admin_state["step"] = "set_button_name"
        bot.send_message(message.chat.id, f"✏️ Current button name: {settings.get('button_name')}\nSend new name:")

    elif text == "👥 Users":
        show_user_stats(message)

    elif text == "🚫 Block User":
        admin_state["step"] = "block_user"
        bot.send_message(message.chat.id, "🚫 Send User ID to block:")

    elif text == "✅ Unblock User":
        admin_state["step"] = "unblock_user"
        bot.send_message(message.chat.id, "✅ Send User ID to unblock:")

    elif text == "📋 Blocked Users":
        show_blocked_users(message)

    elif text == "📢 Broadcast":
        admin_state["step"] = "broadcast"
        bot.send_message(message.chat.id, "📢 Send message to broadcast:")

    elif text == "💳 Payment Settings":
        show_payment_settings_menu(message)

    elif text == "🔧 Maintenance Mode":
        toggle_maintenance_mode(message)

    elif text == "🔙 Exit":
        reset_admin_state()
        bot.send_message(
            message.chat.id,
            "🔙 Admin Panel closed.",
            reply_markup=types.ReplyKeyboardRemove(),
        )


# ==============================================================================
# MAINTENANCE MODE
# ==============================================================================

def toggle_maintenance_mode(message):
    current = settings.get("maintenance_mode", "0")
    new_mode = "0" if current == "1" else "1"
    settings["maintenance_mode"] = new_mode
    save_settings()
    
    status = "ON" if new_mode == "1" else "OFF"
    bot.send_message(
        message.chat.id,
        f"🔧 <b>Maintenance Mode</b>\n\nStatus: {status}",
        parse_mode="HTML",
        reply_markup=admin_menu_keyboard()
    )


def toggle_auto_payment(message):
    current = settings.get("auto_payment", "1")
    new_val = "0" if current == "1" else "1"
    settings["auto_payment"] = new_val
    save_settings()
    
    status = "ON" if new_val == "1" else "OFF"
    bot.send_message(
        message.chat.id,
        f"⚡ <b>Auto Payment</b>\n\nStatus: {status}",
        parse_mode="HTML",
        reply_markup=admin_menu_keyboard()
    )


# ==============================================================================
# PAYMENT SETTINGS
# ==============================================================================

def show_payment_settings_menu(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        styled_button("🔹 Set UPI ID", "primary"),
        styled_button("🔹 Set Crypto Address", "primary"),
        styled_button("🔹 Set Crypto QR Code", "primary"),
        styled_button("🔹 Toggle Auto Payment", "success"),
        styled_button("🔙 Back to Admin Menu", "danger"),
    )
    bot.send_message(
        message.chat.id,
        f"💳 <b>Payment Settings</b>\n\n"
        f"📌 UPI ID: `{settings.get('upi_id', 'Not Set')}`\n"
        f"🪙 Crypto: `{settings.get('crypto_address', 'Not Set')}`\n"
        f"🌐 Network: {settings.get('crypto_network', 'BEP20')}\n"
        f"⚡ Auto Payment: {'✅ ON' if settings.get('auto_payment', '1') == '1' else '❌ OFF'}",
        parse_mode="HTML",
        reply_markup=kb,
    )
    admin_state["step"] = "payment_settings_menu"


# ==============================================================================
# ADMIN STEP HANDLER
# ==============================================================================

def handle_admin_step(message):
    step = admin_state["step"]
    text = message.text.strip()

    if step == "payment_settings_menu":
        if text == "🔹 Set UPI ID":
            admin_state["step"] = "set_upi_id"
            bot.send_message(message.chat.id, "💳 Send new UPI ID:")
            return
        elif text == "🔹 Set Crypto Address":
            admin_state["step"] = "set_crypto_address"
            bot.send_message(message.chat.id, "🪙 Send new Crypto Address:")
            return
        elif text == "🔹 Set Crypto QR Code":
            admin_state["step"] = "set_crypto_qr"
            bot.send_message(message.chat.id, "🖼️ Send Crypto QR Code photo:")
            return
        elif text == "🔹 Toggle Auto Payment":
            toggle_auto_payment(message)
            return
        elif text == "🔙 Back to Admin Menu":
            reset_admin_state()
            bot.send_message(message.chat.id, "🛠️ Admin Panel", reply_markup=admin_menu_keyboard())
            return
        else:
            bot.send_message(message.chat.id, "⚠️ Use buttons below.")
            return

    if step == "set_upi_id":
        settings["upi_id"] = text
        save_settings()
        reset_admin_state()
        bot.send_message(message.chat.id, f"✅ UPI ID updated: `{text}`", parse_mode="Markdown", reply_markup=admin_menu_keyboard())
        return

    if step == "set_crypto_address":
        settings["crypto_address"] = text
        settings["crypto_network"] = "BEP20"
        save_settings()
        reset_admin_state()
        bot.send_message(message.chat.id, f"✅ Crypto Address updated: `{text}`", parse_mode="Markdown", reply_markup=admin_menu_keyboard())
        return

    if step == "set_crypto_qr":
        bot.send_message(message.chat.id, "📷 Please send a *photo* for Crypto QR.", parse_mode="Markdown")
        return

    if step == "set_qr":
        bot.send_message(message.chat.id, "📷 Please send a *photo* for QR Code.", parse_mode="Markdown")
        return

    if step == "set_account_username":
        admin_state["data"]["username"] = text
        admin_state["step"] = "set_account_password"
        bot.send_message(message.chat.id, "🔑 Send Password:", parse_mode="Markdown")
        return

    if step == "set_account_password":
        admin_state["data"]["password"] = text
        admin_state["step"] = "set_account_link"
        bot.send_message(message.chat.id, "🔗 Send Login Link:", parse_mode="Markdown")
        return

    if step == "set_account_link":
        admin_state["data"]["link"] = text
        accounts.append({
            "username": admin_state["data"]["username"],
            "password": admin_state["data"]["password"],
            "link": admin_state["data"]["link"],
        })
        save_accounts()
        reset_admin_state()
        bot.send_message(message.chat.id, f"✅ Account added! Stock: {len(accounts)}", reply_markup=admin_menu_keyboard())
        return

    if step == "set_price":
        settings["price"] = text
        save_settings()
        reset_admin_state()
        bot.send_message(message.chat.id, f"✅ Price updated: {settings['price']}", reply_markup=admin_menu_keyboard())
        return

    if step == "set_button_name":
        if not text:
            bot.send_message(message.chat.id, "❌ Name cannot be empty.")
            return
        settings["button_name"] = text
        save_settings()
        reset_admin_state()
        bot.send_message(message.chat.id, f"✅ Button name: {text}", reply_markup=admin_menu_keyboard())
        return

    if step == "block_user":
        target_id = extract_user_id(text)
        if target_id is None:
            bot.send_message(message.chat.id, "❌ Invalid ID.")
            return
        uid_str = str(target_id)
        if uid_str not in users:
            bot.send_message(message.chat.id, "❌ User not found.")
        else:
            users[uid_str]["status"] = "blocked"
            save_users()
            bot.send_message(message.chat.id, f"🚫 User {target_id} blocked.")
            safe_send(target_id, "🚫 You have been blocked.")
        reset_admin_state()
        bot.send_message(message.chat.id, "Admin Panel:", reply_markup=admin_menu_keyboard())
        return

    if step == "unblock_user":
        target_id = extract_user_id(text)
        if target_id is None:
            bot.send_message(message.chat.id, "❌ Invalid ID.")
            return
        uid_str = str(target_id)
        if uid_str not in users:
            bot.send_message(message.chat.id, "❌ User not found.")
        else:
            users[uid_str]["status"] = "active"
            save_users()
            bot.send_message(message.chat.id, f"✅ User {target_id} unblocked.")
            safe_send(target_id, "✅ You have been unblocked. Send /start")
        reset_admin_state()
        bot.send_message(message.chat.id, "Admin Panel:", reply_markup=admin_menu_keyboard())
        return

    if step == "broadcast":
        run_broadcast(message)
        reset_admin_state()
        return


def extract_user_id(text):
    text = text.strip()
    if text.isdigit():
        return int(text)
    return None


# ==============================================================================
# PENDING UTRs
# ==============================================================================

def show_pending_utrs(message):
    pending = [r for r in utrs.values() if r["status"] == "Pending"]

    if not pending:
        bot.send_message(message.chat.id, "📭 No pending UTRs.")
        return

    bot.send_message(message.chat.id, f"📝 {len(pending)} pending UTR(s):")
    for record in pending:
        bot.send_message(
            message.chat.id,
            format_utr_details(record),
            parse_mode="HTML",
            reply_markup=utr_action_keyboard(record["utr_id"]),
        )
        if record.get("screenshot_file_id"):
            bot.send_photo(message.chat.id, record["screenshot_file_id"], caption="📸 Screenshot")


# ==============================================================================
# CALLBACK HANDLER
# ==============================================================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ Unauthorized.")
        return

    try:
        action, utr_id = call.data.split(":", 1)
    except ValueError:
        bot.answer_callback_query(call.id)
        return

    record = utrs.get(utr_id)
    if not record:
        bot.answer_callback_query(call.id, "⚠️ Not found.")
        return

    if action == "approve":
        approve_utr(call, record)
    elif action == "pending":
        mark_utr_pending(call, record)
    elif action == "reject":
        reject_utr(call, record)
    else:
        bot.answer_callback_query(call.id)


def approve_utr(call, record):
    if record["status"] == "Approved":
        bot.answer_callback_query(call.id, "Already approved.")
        return

    if not accounts:
        bot.answer_callback_query(call.id, "⚠️ No stock!", show_alert=True)
        safe_send(ADMIN_ID, "⚠️ No accounts in stock!")
        return

    account = accounts.pop(0)
    save_accounts()

    record["status"] = "Approved"
    save_utrs()

    account_text = (
        "✅ <b>Payment Approved!</b>\n\n"
        f"👤 Username: <code>{account['username']}</code>\n"
        f"🔑 Password: <code>{account['password']}</code>\n"
        f"🔗 Login: {account['link']}\n\n"
        "🎮 Enjoy!"
    )
    delivered = safe_send(record["user_id"], account_text, parse_mode="HTML")

    try:
        bot.edit_message_text(
            format_utr_details(record) + ("\n\n✅ Delivered." if delivered else "\n\n⚠️ Failed."),
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML",
        )
    except Exception:
        pass

    bot.answer_callback_query(call.id, "✅ Approved.")


def mark_utr_pending(call, record):
    record["status"] = "Pending"
    save_utrs()

    safe_send(record["user_id"], "🕒 Your UTR is Pending. Please wait.")

    try:
        bot.edit_message_text(
            format_utr_details(record) + "\n\n🕒 Marked Pending.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML",
            reply_markup=utr_action_keyboard(record["utr_id"]),
        )
    except Exception:
        pass

    bot.answer_callback_query(call.id, "🕒 Pending.")


def reject_utr(call, record):
    record["status"] = "Rejected"
    save_utrs()

    safe_send(record["user_id"], "❌ Payment Not Found. Please submit again.")

    try:
        bot.edit_message_text(
            format_utr_details(record) + "\n\n❌ Rejected.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML",
        )
    except Exception:
        pass

    bot.answer_callback_query(call.id, "❌ Rejected.")


# ==============================================================================
# USER STATS
# ==============================================================================

def show_user_stats(message):
    total_users = len(users)
    today_str = date.today().strftime("%Y-%m-%d")
    today_joined = sum(1 for u in users.values() if u.get("join_date") == today_str)
    blocked_count = sum(1 for u in users.values() if u.get("status") == "blocked")

    approved_count = sum(1 for r in utrs.values() if r["status"] == "Approved")
    pending_count = sum(1 for r in utrs.values() if r["status"] == "Pending")
    rejected_count = sum(1 for r in utrs.values() if r["status"] == "Rejected")

    text = (
        f"👥 <b>User Statistics</b>\n\n"
        f"👤 Total: {total_users}\n"
        f"🆕 Today: {today_joined}\n"
        f"🚫 Blocked: {blocked_count}\n\n"
        f"✅ Approved: {approved_count}\n"
        f"⏳ Pending: {pending_count}\n"
        f"❌ Rejected: {rejected_count}\n\n"
        f"📦 Stock: {len(accounts)}"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")


def show_blocked_users(message):
    blocked = [u for u in users.values() if u.get("status") == "blocked"]

    if not blocked:
        bot.send_message(message.chat.id, "📋 No blocked users.")
        return

    lines = [f"📋 <b>Blocked Users ({len(blocked)})</b>\n"]
    for u in blocked:
        lines.append(f"🆔 <code>{u['user_id']}</code> | @{u.get('username', 'N/A')}")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode="HTML")


# ==============================================================================
# BROADCAST
# ==============================================================================

def run_broadcast(message):
    broadcast_text = message.text
    success = 0
    failed = 0

    bot.send_message(message.chat.id, "📢 Broadcasting...")

    for uid_str, u in users.items():
        if u.get("status") == "blocked":
            continue
        if int(uid_str) == ADMIN_ID:
            continue
        if safe_send(int(uid_str), broadcast_text):
            success += 1
        else:
            failed += 1

    bot.send_message(
        message.chat.id,
        f"📢 <b>Broadcast Complete</b>\n\n✅ Success: {success}\n❌ Failed: {failed}",
        parse_mode="HTML",
        reply_markup=admin_menu_keyboard()
    )


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    print("🤖 Bot starting...")
    print(f"📦 Users: {len(users)}, Stock: {len(accounts)}, UTRs: {len(utrs)}")
    print(f"🔧 Maintenance: {'ON' if settings.get('maintenance_mode') == '1' else 'OFF'}")
    print(f"⚡ Auto Payment: {'ON' if settings.get('auto_payment', '1') == '1' else 'OFF'}")
    bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
