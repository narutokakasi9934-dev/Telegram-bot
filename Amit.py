import telebot
import os
from telebot import types
import sqlite3

# ==================================================
# CONFIG
# ==================================================

BOT_TOKEN = os.getenv("8687278932:AAG6LssTfwFzPx8okZ9tfMlMA1If_ptmqG8")
CHANNEL_USERNAME = "@test_channel1230"
CHANNEL_URL = "https://t.me/test_channel1230"

ADMIN_ID = 8786989840

bot = telebot.TeleBot(BOT_TOKEN)

# ==================================================
# DATABASE
# ==================================================

conn = sqlite3.connect(
    "bot_data.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    username TEXT,
    balance REAL DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    plan TEXT,
    price REAL,
    status TEXT
)
""")

conn.commit()


# ==================================================
# ADMIN CHECK
# ==================================================

def is_admin(user_id):
    return user_id == ADMIN_ID


# ==================================================
# ADD USER
# ==================================================

def add_user(user):

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, first_name, username)
        VALUES (?, ?, ?)
        """,
        (
            user.id,
            user.first_name,
            user.username or ""
        )
    )

    conn.commit()


# ==================================================
# CHANNEL CHECK
# ==================================================

def is_member(user_id):

    try:

        member = bot.get_chat_member(
            CHANNEL_USERNAME,
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except Exception as e:

        print("Membership error:", e)

        return False


def channel_menu():

    keyboard = types.InlineKeyboardMarkup(
        row_width=1
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📢 Join Official Channel",
            url=CHANNEL_URL
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "✅ Verify Membership",
            callback_data="verify_membership"
        )
    )

    return keyboard


def show_join_message(chat_id):

    bot.send_message(
        chat_id,
        "🔒 <b>ACCESS DENIED</b>\n\n"
        "To use this bot, you must join our official "
        "Telegram channel first.\n\n"
        "📢 Join the channel and then click "
        "<b>Verify Membership</b>.\n\n"
        "⚠️ You must be a member to continue.",
        parse_mode="HTML",
        reply_markup=channel_menu()
    )


# ==================================================
# MAIN MENU
# ==================================================

def main_menu(user_id):

    keyboard = types.InlineKeyboardMarkup(
        row_width=2
    )

    keyboard.add(

        types.InlineKeyboardButton(
            "🚀 Create Ad Account",
            callback_data="create_account"
        ),

        types.InlineKeyboardButton(
            "👑 Subscription Plans",
            callback_data="plans"
        )
    )

    keyboard.add(

        types.InlineKeyboardButton(
            "📊 Active Status",
            callback_data="status"
        ),

        types.InlineKeyboardButton(
            "🎁 Refer & Earn",
            callback_data="refer"
        )
    )

    keyboard.add(

        types.InlineKeyboardButton(
            "📋 Created Accounts",
            callback_data="accounts"
        ),

        types.InlineKeyboardButton(
            "💰 Wallet",
            callback_data="wallet"
        )
    )

    keyboard.add(

        types.InlineKeyboardButton(
            "➕ Add Money",
            callback_data="add_money"
        ),

        types.InlineKeyboardButton(
            "🎫 Help & Support",
            callback_data="support"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "👤 My Profile",
            callback_data="profile"
        )
    )

    # ADMIN BUTTON ONLY FOR ADMIN
    if is_admin(user_id):

        keyboard.add(
            types.InlineKeyboardButton(
                "👑 Admin Panel",
                callback_data="admin_panel"
            )
        )

    return keyboard


# ==================================================
# ADMIN MENU
# ==================================================

def admin_menu():

    keyboard = types.InlineKeyboardMarkup(
        row_width=2
    )

    keyboard.add(

        types.InlineKeyboardButton(
            "👥 Users",
            callback_data="admin_users"
        ),

        types.InlineKeyboardButton(
            "📦 Orders",
            callback_data="admin_orders"
        )
    )

    keyboard.add(

        types.InlineKeyboardButton(
            "💰 Add Balance",
            callback_data="admin_add_balance"
        ),

        types.InlineKeyboardButton(
            "🔄 Order Status",
            callback_data="admin_status"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📢 Broadcast",
            callback_data="admin_broadcast"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🔙 Main Menu",
            callback_data="back_main"
        )
    )

    return keyboard


# ==================================================
# START
# ==================================================

@bot.message_handler(commands=["start"])
def start(message):

    add_user(message.from_user)

    if not is_member(message.from_user.id):

        show_join_message(
            message.chat.id
        )

        return

    bot.send_message(

        message.chat.id,

        "🤖 <b>Welcome to Our Service Bot</b>\n\n"

        f"Hello <b>{message.from_user.first_name}</b>! 👋\n\n"

        "Choose an option from the menu below.\n\n"

        "💳 Fast & Secure\n"
        "📦 Easy Order Management\n"
        "🎁 Referral Rewards\n"
        "🎫 Support",

        parse_mode="HTML",

        reply_markup=main_menu(
            message.from_user.id
        )
    )


# ==================================================
# ADMIN COMMAND
# ==================================================

@bot.message_handler(commands=["admin"])
def admin_command(message):

    if not is_admin(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "❌ You are not authorized."
        )

        return

    bot.send_message(

        message.chat.id,

        "👑 <b>ADMIN PANEL</b>\n\n"
        "Welcome, Admin.\n\n"
        "Select an option:",

        parse_mode="HTML",

        reply_markup=admin_menu()
    )


# ==================================================
# CALLBACK HANDLER
# ==================================================

@bot.callback_query_handler(
    func=lambda call: True
)
def callbacks(call):

    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # ----------------------------------------------
    # VERIFY
    # ----------------------------------------------

    if call.data == "verify_membership":

        if is_member(call.from_user.id):

            bot.answer_callback_query(
                call.id,
                "✅ Membership verified!"
            )

            bot.edit_message_text(

                "✅ <b>Membership Verified!</b>\n\n"
                "Welcome to the bot. 🎉\n\n"
                "Choose an option below.",

                chat_id,
                message_id,

                parse_mode="HTML",

                reply_markup=main_menu(
                    call.from_user.id
                )
            )

        else:

            bot.answer_callback_query(
                call.id,
                "❌ Please join the channel first.",
                show_alert=True
            )

        return

    # ----------------------------------------------
    # ADMIN PANEL
    # ----------------------------------------------

    if call.data == "admin_panel":

        if not is_admin(call.from_user.id):

            bot.answer_callback_query(
                call.id,
                "❌ Not authorized.",
                show_alert=True
            )

            return

        bot.answer_callback_query(
            call.id
        )

        bot.edit_message_text(

            "👑 <b>ADMIN PANEL</b>\n\n"
            "Select an option:",

            chat_id,
            message_id,

            parse_mode="HTML",

            reply_markup=admin_menu()
        )

        return

    # ----------------------------------------------
    # ADMIN USERS
    # ----------------------------------------------

    if call.data == "admin_users":

        if not is_admin(call.from_user.id):
            return

        cursor.execute(
            "SELECT COUNT(*) FROM users"
        )

        total = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT user_id, first_name, username
            FROM users
            ORDER BY rowid DESC
            LIMIT 10
            """
        )

        users = cursor.fetchall()

        text = (
            "👥 <b>USERS</b>\n\n"
            f"Total Users: <b>{total}</b>\n\n"
        )

        for user_id, name, username in users:

            text += (
                f"👤 {name}\n"
                f"🆔 <code>{user_id}</code>\n"
                f"📛 @{username or 'Not Set'}\n\n"
            )

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 Admin Panel",
                callback_data="admin_panel"
            )
        )

        bot.edit_message_text(

            text,

            chat_id,
            message_id,

            parse_mode="HTML",

            reply_markup=keyboard
        )

        return

    # ----------------------------------------------
    # ADMIN ORDERS
    # ----------------------------------------------

    if call.data == "admin_orders":

        if not is_admin(call.from_user.id):
            return

        cursor.execute(
            """
            SELECT id, user_id, plan, price, status
            FROM orders
            ORDER BY id DESC
            LIMIT 10
            """
        )

        orders = cursor.fetchall()

        if not orders:

            text = (
                "📦 <b>ORDERS</b>\n\n"
                "No orders found."
            )

        else:

            text = "📦 <b>RECENT ORDERS</b>\n\n"

            for order in orders:

                order_id = order[0]
                user_id = order[1]
                plan = order[2]
                price = order[3]
                status = order[4]

                text += (
                    f"🆔 Order #{order_id}\n"
                    f"👤 User: <code>{user_id}</code>\n"
                    f"📦 {plan}\n"
                    f"💰 ₹{price}\n"
                    f"📊 {status}\n\n"
                )

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 Admin Panel",
                callback_data="admin_panel"
            )
        )

        bot.edit_message_text(

            text,

            chat_id,
            message_id,

            parse_mode="HTML",

            reply_markup=keyboard
        )

        return

    # ----------------------------------------------
    # ADD BALANCE
    # ----------------------------------------------

    if call.data == "admin_add_balance":

        if not is_admin(call.from_user.id):
            return

        msg = bot.send_message(

            chat_id,

            "💰 <b>ADD BALANCE</b>\n\n"

            "Send:\n"
            "<code>UserID Amount</code>\n\n"

            "Example:\n"
            "<code>123456789 100</code>",

            parse_mode="HTML"
        )

        bot.register_next_step_handler(
            msg,
            process_add_balance
        )

        return

    # ----------------------------------------------
    # ORDER STATUS
    # ----------------------------------------------

    if call.data == "admin_status":

        if not is_admin(call.from_user.id):
            return

        msg = bot.send_message(

            chat_id,

            "🔄 <b>ORDER STATUS</b>\n\n"

            "Send:\n"
            "<code>OrderID Status</code>\n\n"

            "Example:\n"
            "<code>12 Completed</code>",

            parse_mode="HTML"
        )

        bot.register_next_step_handler(
            msg,
            process_order_status
        )

        return

    # ----------------------------------------------
    # BROADCAST
    # ----------------------------------------------

    if call.data == "admin_broadcast":

        if not is_admin(call.from_user.id):
            return

        msg = bot.send_message(

            chat_id,

            "📢 <b>BROADCAST</b>\n\n"
            "Send the message you want to broadcast.",

            parse_mode="HTML"
        )

        bot.register_next_step_handler(
            msg,
            process_broadcast
        )

        return

    # ----------------------------------------------
    # CREATE ACCOUNT
    # ----------------------------------------------

    if call.data == "create_account":

        keyboard = types.InlineKeyboardMarkup(
            row_width=1
        )

        keyboard.add(

            types.InlineKeyboardButton(
                "📦 Basic Account - ₹100",
                callback_data="basic_account"
            ),

            types.InlineKeyboardButton(
                "⭐ Premium Account - ₹250",
                callback_data="premium_account"
            ),

            types.InlineKeyboardButton(
                "🔙 Back",
                callback_data="back_main"
            )
        )

        bot.edit_message_text(

            "🚀 <b>CREATE AD ACCOUNT</b>\n\n"
            "Select a plan:",

            chat_id,
            message_id,

            parse_mode="HTML",

            reply_markup=keyboard
        )

        return

    # ----------------------------------------------
    # BASIC
    # ----------------------------------------------

    if call.data == "basic_account":

        order_account(
            call,
            "Basic Account",
            100
        )

        return

    # ----------------------------------------------
    # PREMIUM
    # ----------------------------------------------

    if call.data == "premium_account":

        order_account(
            call,
            "Premium Account",
            250
        )

        return

    # ----------------------------------------------
    # PLANS
    # ----------------------------------------------

    if call.data == "plans":

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 Back",
                callback_data="back_main"
            )
        )

        bot.edit_message_text(

            "👑 <b>SUBSCRIPTION PLANS</b>\n\n"

            "📦 <b>Basic Plan</b>\n"
            "💰 Price: ₹100\n"
            "⏱ Duration: 30 Days\n\n"

            "⭐ <b>Premium Plan</b>\n"
            "💰 Price: ₹250\n"
            "⏱ Duration: 30 Days",

            chat_id,
            message_id,

            parse_mode="HTML",

            reply_markup=keyboard
        )

        return

    # ----------------------------------------------
    # STATUS
    # ----------------------------------------------

    if call.data == "status":

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 Back",
                callback_data="back_main"
            )
        )

        bot.edit_message_text(

            "📊 <b>ACTIVE STATUS</b>\n\n"
            "You currently have no active orders.",

            chat_id,
            message_id,

            parse_mode="HTML",

            reply_markup=keyboard
        )

        return

    # ----------------------------------------------
    # REFER
    # ----------------------------------------------

    if call.data == "refer":

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 Back",
                callback_data="back_main"
            )
        )

        bot.edit_message_text(

            "🎁 <b>REFER & EARN</b>\n\n"
            "Referral system will be connected here.",

            chat_id,
            message_id,

            parse_mode="HTML",

            reply_markup=keyboard
        )

        return

    # ----------------------------------------------
    # ACCOUNTS
    # ----------------------------------------------

    if call.data == "accounts":

        cursor.execute(
            """
            SELECT plan, price, status
            FROM orders
            WHERE user_id=?
            """,
            (call.from_user.id,)
        )

        orders = cursor.fetchall()

        if orders:

            text = (
                "📋 <b>CREATED ACCOUNTS</b>\n\n"
            )

            for plan, price, status in orders:

                text += (
                    f"📦 {plan}\n"
                    f"💰 ₹{price}\n"
                    f"📊 {status}\n\n"
                )

        else:

            text = (
                "📋 <b>CREATED ACCOUNTS</b>\n\n"
                "No accounts found."
            )

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 Back",
                callback_data="back_main"
            )
        )

        bot.edit_message_text(

            text,

            chat_id,
            message_id,

            parse_mode="HTML",

            reply_markup=keyboard
        )

        return

    # ----------------------------------------------
    # WALLET
    # ----------------------------------------------

    if call.data == "wallet":

        show_wallet(
            chat_id,
            message_id,
            call.from_user.id
        )

        return

    # ----------------------------------------------
    # ADD MONEY
    # ----------------------------------------------

    if call.data == "add_money":

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 Back",
                callback_data="back_main"
            )
        )

        bot.edit_message_text(

            "➕ <b>ADD MONEY</b>\n\n"
            "Payment system will be connected here.\n\n"
            "⚠️ Real payment is not connected yet.",

            chat_id,
            message_id,

            parse_mode="HTML",

            reply_markup=keyboard
        )

        return

    # ----------------------------------------------
    # SUPPORT
    # ----------------------------------------------

    if call.data == "support":

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 Back",
                callback_data="back_main"
            )
        )

        bot.edit_message_text(

            "🎫 <b>HELP & SUPPORT</b>\n\n"
            "Contact support for assistance.",

            chat_id,
            message_id,

            parse_mode="HTML",

            reply_markup=keyboard
        )

        return

    # ----------------------------------------------
    # PROFILE
    # ----------------------------------------------

    if call.data == "profile":

        cursor.execute(
            "SELECT balance FROM users WHERE user_id=?",
            (call.from_user.id,)
        )

        result = cursor.fetchone()

        balance = result[0] if result else 0

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 Back",
                callback_data="back_main"
            )
        )

        user = call.from_user

        bot.edit_message_text(

            f"👤 <b>MY PROFILE</b>\n\n"
            f"Name: {user.first_name}\n"
            f"Username: @{user.username or 'Not Set'}\n"
            f"Telegram ID: <code>{user.id}</code>\n"
            f"Wallet: ₹{balance:.2f}",

            chat_id,
            message_id,

            parse_mode="HTML",

            reply_markup=keyboard
        )

        return

    # ----------------------------------------------
    # BACK
    # ----------------------------------------------

    if call.data == "back_main":

        bot.edit_message_text(

            "🤖 <b>Main Menu</b>\n\n"
            "Choose an option:",

            chat_id,
            message_id,

            parse_mode="HTML",

            reply_markup=main_menu(
                call.from_user.id
            )
        )

        return


# ==================================================
# ADD BALANCE PROCESS
# ==================================================

def process_add_balance(message):

    if not is_admin(message.from_user.id):
        return

    try:

        parts = message.text.split()

        if len(parts) != 2:
            raise ValueError

        user_id = int(parts[0])
        amount = float(parts[1])

        if amount <= 0:
            raise ValueError

        cursor.execute(
            "SELECT balance FROM users WHERE user_id=?",
            (user_id,)
        )

        result = cursor.fetchone()

        if not result:

            bot.send_message(
                message.chat.id,
                "❌ User not found."
            )

            return

        new_balance = result[0] + amount

        cursor.execute(
            """
            UPDATE users
            SET balance=?
            WHERE user_id=?
            """,
            (new_balance, user_id)
        )

        conn.commit()

        bot.send_message(

            message.chat.id,

            f"✅ <b>Balance Updated</b>\n\n"
            f"👤 User ID: <code>{user_id}</code>\n"
            f"➕ Added: ₹{amount:.2f}\n"
            f"💰 New Balance: ₹{new_balance:.2f}",

            parse_mode="HTML"
        )

    except:

        bot.send_message(

            message.chat.id,

            "❌ Invalid format.\n\n"
            "Use:\n"
            "<code>UserID Amount</code>\n\n"
            "Example:\n"
            "<code>123456789 100</code>",

            parse_mode="HTML"
        )


# ==================================================
# ORDER STATUS PROCESS
# ==================================================

def process_order_status(message):

    if not is_admin(message.from_user.id):
        return

    try:

        parts = message.text.split(
            maxsplit=1
        )

        if len(parts) != 2:
            raise ValueError

        order_id = int(parts[0])
        status = parts[1].strip()

        cursor.execute(
            "SELECT id FROM orders WHERE id=?",
            (order_id,)
        )

        result = cursor.fetchone()

        if not result:

            bot.send_message(
                message.chat.id,
                "❌ Order not found."
            )

            return

        cursor.execute(
            """
            UPDATE orders
            SET status=?
            WHERE id=?
            """,
            (status, order_id)
        )

        conn.commit()

        bot.send_message(

            message.chat.id,

            f"✅ <b>Order Updated</b>\n\n"
            f"🆔 Order: #{order_id}\n"
            f"📊 Status: {status}",

            parse_mode="HTML"
        )

    except:

        bot.send_message(

            message.chat.id,

            "❌ Invalid format.\n\n"
            "Use:\n"
            "<code>OrderID Status</code>\n\n"
            "Example:\n"
            "<code>12 Completed</code>",

            parse_mode="HTML"
        )


# ==================================================
# BROADCAST
# ==================================================

def process_broadcast(message):

    if not is_admin(message.from_user.id):
        return

    text = message.text

    cursor.execute(
        "SELECT user_id FROM users"
    )

    users = cursor.fetchall()

    sent = 0
    failed = 0

    for row in users:

        user_id = row[0]

        try:

            bot.send_message(
                user_id,
                "📢 <b>Announcement</b>\n\n"
                + text,
                parse_mode="HTML"
            )

            sent += 1

        except:

            failed += 1

    bot.send_message(

        message.chat.id,

        f"✅ <b>Broadcast Finished</b>\n\n"
        f"📨 Sent: {sent}\n"
        f"❌ Failed: {failed}",

        parse_mode="HTML"
    )


# ==================================================
# ORDER FUNCTION
# ==================================================

def order_account(call, plan, price):

    user_id = call.from_user.id

    cursor.execute(
        "SELECT balance FROM users WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()

    balance = result[0] if result else 0

    if balance < price:

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "➕ Add Money",
                callback_data="add_money"
            )
        )

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 Back",
                callback_data="create_account"
            )
        )

        bot.edit_message_text(

            "❌ <b>Insufficient Balance</b>\n\n"
            f"📦 Plan: {plan}\n"
            f"💰 Price: ₹{price}\n"
            f"💳 Balance: ₹{balance:.2f}\n\n"
            "Please add money first.",

            call.message.chat.id,
            call.message.message_id,

            parse_mode="HTML",

            reply_markup=keyboard
        )

        return

    new_balance = balance - price

    cursor.execute(
        """
        UPDATE users
        SET balance=?
        WHERE user_id=?
        """,
        (new_balance, user_id)
    )

    cursor.execute(
        """
        INSERT INTO orders
        (user_id, plan, price, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            plan,
            price,
            "Pending"
        )
    )

    conn.commit()

    bot.edit_message_text(

        "✅ <b>ORDER CREATED</b>\n\n"
        f"📦 Plan: {plan}\n"
        f"💰 Price: ₹{price}\n"
        f"💳 Remaining Balance: ₹{new_balance:.2f}\n\n"
        "📊 Status: Pending",

        call.message.chat.id,
        call.message.message_id,

        parse_mode="HTML",

        reply_markup=main_menu(
            user_id
        )
    )


# ==================================================
# WALLET
# ==================================================

def show_wallet(
    chat_id,
    message_id,
    user_id
):

    cursor.execute(
        "SELECT balance FROM users WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()

    balance = result[0] if result else 0

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "➕ Add Money",
            callback_data="add_money"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🔙 Back",
            callback_data="back_main"
        )
    )

    bot.edit_message_text(

        f"💰 <b>WALLET</b>\n\n"
        f"Balance: ₹{balance:.2f}",

        chat_id,
        message_id,

        parse_mode="HTML",

        reply_markup=keyboard
    )


# ==================================================
# RUN BOT
# ==================================================

import time

print("🤖 Bot is running...")

while True:
    try:
        bot.polling(
            none_stop=True,
            interval=1,
            timeout=20,
            long_polling_timeout=20
        )

    except Exception as e:
        print("⚠️ Connection lost:", e)
        print("🔄 Reconnecting in 5 seconds...")
        time.sleep(5)
