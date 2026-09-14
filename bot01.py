import telebot
import sqlite3
import random
import os
from telebot import types

# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = "8963356222:AAERXBrx16owt6SWIrUxLXmH_E8-lxtqzM0"
ADMIN_ID = 7964728525

PAYMENT_NUMBER = "01831628565"

DB = "appstore.db"
APP_DIR = "apps"

os.makedirs(APP_DIR, exist_ok=True)

bot = telebot.TeleBot(BOT_TOKEN)


# =========================================================
# DATABASE
# =========================================================

def db():
    return sqlite3.connect(DB)


def init_db():

    con = db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0,
            card_number TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price INTEGER,
            file_id TEXT,
            uploader INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            method TEXT,
            trx TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)

    con.commit()
    con.close()


init_db()


# =========================================================
# USER
# =========================================================

def add_user(user):

    con = db()
    cur = con.cursor()

    cur.execute(
        "SELECT user_id FROM users WHERE user_id=?",
        (user.id,)
    )

    exists = cur.fetchone()

    if not exists:

        card = generate_demo_card()

        cur.execute("""
            INSERT INTO users
            (user_id, username, balance, card_number)
            VALUES (?, ?, 0, ?)
        """, (
            user.id,
            user.username or "",
            card
        ))

    else:

        cur.execute("""
            UPDATE users
            SET username=?
            WHERE user_id=?
        """, (
            user.username or "",
            user.id
        ))

    con.commit()
    con.close()


# =========================================================
# DEMO CARD
# =========================================================

def generate_demo_card():

    return (
        "DEMO •••• "
        + str(random.randint(1000, 9999))
        + " •••• "
        + str(random.randint(1000, 9999))
    )


def get_card(user_id):

    con = db()
    cur = con.cursor()

    cur.execute(
        "SELECT card_number FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()

    if row and row[0]:

        card = row[0]

    else:

        card = generate_demo_card()

        cur.execute("""
            UPDATE users
            SET card_number=?
            WHERE user_id=?
        """, (
            card,
            user_id
        ))

        con.commit()

    con.close()

    return card


def get_balance(user_id):

    con = db()
    cur = con.cursor()

    cur.execute(
        "SELECT balance FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()

    con.close()

    return row[0] if row else 0


# =========================================================
# USER KEYBOARD
# =========================================================

def user_keyboard():

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.row(
        "📱 App Store",
        "💰 Balance"
    )

    kb.row(
        "💳 Visa Card",
        "💳 Add Balance"
    )

    kb.row(
        "📦 My Purchases",
        "ℹ️ Help"
    )

    return kb


# =========================================================
# ADMIN KEYBOARD
# =========================================================

def admin_keyboard():

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.row(
        "📊 Dashboard",
        "➕ Add App"
    )

    kb.row(
        "📱 Apps",
        "💳 Payments"
    )

    kb.row(
        "🎁 Give Balance",
        "📢 Broadcast"
    )

    kb.row(
        "⬅️ User Panel"
    )

    return kb


# =========================================================
# START
# =========================================================

@bot.message_handler(commands=["start"])
def start(message):

    add_user(message.from_user)

    if message.from_user.id == ADMIN_ID:

        bot.send_message(
            message.chat.id,
            "🛠️ ADMIN PANEL",
            reply_markup=admin_keyboard()
        )

    else:

        bot.send_message(
            message.chat.id,
            "👋 Welcome to App Store!\n\n"
            "📱 Apps কিনুন\n"
            "💰 Balance দেখুন\n"
            "💳 Demo Card দেখুন",
            reply_markup=user_keyboard()
        )


# =========================================================
# BALANCE
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "💰 Balance"
)
def balance(message):

    add_user(message.from_user)

    bal = get_balance(message.from_user.id)

    bot.send_message(
        message.chat.id,
        "💰 YOUR BALANCE\n\n"
        "━━━━━━━━━━━━━━\n"
        f"⭐ Points: {bal}\n"
        "━━━━━━━━━━━━━━"
    )


# =========================================================
# VISA DEMO CARD
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "💳 Visa Card"
)
def visa_card(message):

    add_user(message.from_user)

    card = get_card(message.from_user.id)
    bal = get_balance(message.from_user.id)

    text = (
        "💳 VIRTUAL DEMO CARD\n\n"
        "╔════════════════════╗\n"
        "║     VISA DEMO      ║\n"
        "║                    ║\n"
        f"║ {card:<18} ║\n"
        "║                    ║\n"
        f"║ {message.from_user.first_name[:18]:<18} ║\n"
        "║                    ║\n"
        f"║ Balance: {bal} ⭐\n"
        "╚════════════════════╝\n\n"
        "⚠️ Demo card only.\n"
        "Real payment/card transaction is not supported."
    )

    bot.send_message(
        message.chat.id,
        text
    )


# =========================================================
# ADD BALANCE
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "💳 Add Balance"
)
def add_balance(message):

    bot.send_message(
        message.chat.id,
        "💳 ADD BALANCE\n\n"
        "bKash: 01831628565\n"
        "Nagad: 01831628565\n\n"
        "📌 Payment করার পরে Transaction ID দিন।\n"
        "Admin verification-এর পরে balance যোগ হবে।"
    )

    msg = bot.send_message(
        message.chat.id,
        "💰 কত Points যোগ করতে চান?\n\n"
        "Example: 100"
    )

    bot.register_next_step_handler(
        msg,
        payment_amount
    )


def payment_amount(message):

    try:

        amount = int(message.text)

        if amount <= 0:
            raise ValueError

    except:

        bot.send_message(
            message.chat.id,
            "❌ সঠিক amount দিন।"
        )

        return

    msg = bot.send_message(
        message.chat.id,
        f"💰 Amount: {amount} Points\n\n"
        "Payment Method লিখুন:\n"
        "bKash অথবা Nagad"
    )

    bot.register_next_step_handler(
        msg,
        lambda m: payment_method(
            m,
            amount
        )
    )


def payment_method(message, amount):

    method = message.text.strip()

    if method.lower() not in [
        "bkash",
        "nagad",
        "bKash".lower(),
        "Nagad".lower()
    ]:

        bot.send_message(
            message.chat.id,
            "❌ শুধু bKash অথবা Nagad লিখুন।"
        )

        return

    msg = bot.send_message(
        message.chat.id,
        "🧾 Transaction ID দিন:"
    )

    bot.register_next_step_handler(
        msg,
        lambda m: save_payment(
            m,
            amount,
            method
        )
    )


def save_payment(message, amount, method):

    user_id = message.from_user.id
    trx = message.text.strip()

    con = db()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO payments
        (user_id, amount, method, trx, status)
        VALUES (?, ?, ?, ?, 'pending')
    """, (
        user_id,
        amount,
        method,
        trx
    ))

    payment_id = cur.lastrowid

    con.commit()
    con.close()

    bot.send_message(
        user_id,
        "✅ PAYMENT REQUEST SUBMITTED\n\n"
        f"💰 Amount: {amount} Points\n"
        f"💳 Method: {method}\n"
        f"🧾 TRX: {trx}\n\n"
        "⏳ Admin verification চলছে।"
    )

    bot.send_message(
        ADMIN_ID,
        "💳 NEW PAYMENT\n\n"
        f"🆔 Payment ID: {payment_id}\n"
        f"👤 User ID: {user_id}\n"
        f"💰 Amount: {amount}\n"
        f"💳 Method: {method}\n"
        f"🧾 TRX: {trx}",
        reply_markup=payment_buttons(payment_id)
    )


# =========================================================
# PAYMENT BUTTONS
# =========================================================

def payment_buttons(payment_id):

    kb = types.InlineKeyboardMarkup()

    kb.row(
        types.InlineKeyboardButton(
            "✅ Approve",
            callback_data=f"approve_{payment_id}"
        ),
        types.InlineKeyboardButton(
            "❌ Reject",
            callback_data=f"reject_{payment_id}"
        )
    )

    return kb


# =========================================================
# PAYMENT APPROVE / REJECT
# =========================================================

@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("approve_")
    or call.data.startswith("reject_")
)
def payment_action(call):

    if call.from_user.id != ADMIN_ID:

        bot.answer_callback_query(
            call.id,
            "Access denied."
        )

        return

    action, payment_id = call.data.split("_")

    payment_id = int(payment_id)

    con = db()
    cur = con.cursor()

    cur.execute("""
        SELECT user_id, amount, status
        FROM payments
        WHERE id=?
    """, (
        payment_id,
    ))

    payment = cur.fetchone()

    if not payment:

        con.close()

        bot.answer_callback_query(
            call.id,
            "Payment not found."
        )

        return

    user_id, amount, status = payment

    if status != "pending":

        con.close()

        bot.answer_callback_query(
            call.id,
            "Already processed."
        )

        return

    if action == "approve":

        cur.execute("""
            UPDATE users
            SET balance=balance+?
            WHERE user_id=?
        """, (
            amount,
            user_id
        ))

        cur.execute("""
            UPDATE payments
            SET status='approved'
            WHERE id=?
        """, (
            payment_id,
        ))

        con.commit()
        con.close()

        new_balance = get_balance(user_id)

        bot.send_message(
            user_id,
            "✅ PAYMENT APPROVED\n\n"
            f"⭐ Added: {amount} Points\n"
            f"💰 Balance: {new_balance} Points"
        )

        bot.answer_callback_query(
            call.id,
            "Approved!"
        )

    else:

        cur.execute("""
            UPDATE payments
            SET status='rejected'
            WHERE id=?
        """, (
            payment_id,
        ))

        con.commit()
        con.close()

        bot.send_message(
            user_id,
            "❌ Payment rejected.\n\n"
            "প্রয়োজনে আবার payment request করুন।"
        )

        bot.answer_callback_query(
            call.id,
            "Rejected!"
        )

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None
    )


# =========================================================
# APP STORE
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "📱 App Store"
)
def app_store(message):

    con = db()
    cur = con.cursor()

    cur.execute("""
        SELECT id, name, description, price
        FROM apps
        ORDER BY id DESC
    """)

    apps = cur.fetchall()

    con.close()

    if not apps:

        bot.send_message(
            message.chat.id,
            "📭 এখনো কোনো App available নেই।"
        )

        return

    for app_id, name, desc, price in apps:

        kb = types.InlineKeyboardMarkup()

        kb.add(
            types.InlineKeyboardButton(
                f"📥 Buy • {price} ⭐",
                callback_data=f"buy_{app_id}"
            )
        )

        bot.send_message(
            message.chat.id,
            f"📱 {name}\n\n"
            f"{desc}\n\n"
            f"💰 Price: {price} Points",
            reply_markup=kb
        )


# =========================================================
# BUY APP
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("buy_")
)
def buy_app(call):

    user_id = call.from_user.id
    app_id = int(call.data.split("_")[1])

    con = db()
    cur = con.cursor()

    cur.execute("""
        SELECT name, price, file_id
        FROM apps
        WHERE id=?
    """, (
        app_id,
    ))

    app = cur.fetchone()

    if not app:

        con.close()

        bot.answer_callback_query(
            call.id,
            "App not found."
        )

        return

    name, price, file_id = app

    cur.execute("""
        SELECT balance
        FROM users
        WHERE user_id=?
    """, (
        user_id,
    ))

    row = cur.fetchone()

    balance = row[0] if row else 0

    if balance < price:

        con.close()

        bot.answer_callback_query(
            call.id,
            "Balance কম!",
            show_alert=True
        )

        return

    new_balance = balance - price

    cur.execute("""
        UPDATE users
        SET balance=?
        WHERE user_id=?
    """, (
        new_balance,
        user_id
    ))

    con.commit()
    con.close()

    bot.answer_callback_query(
        call.id,
        "Purchase successful!"
    )

    bot.send_document(
        user_id,
        file_id,
        caption=(
            f"📱 {name}\n\n"
            "✅ Purchase successful\n"
            f"⭐ Remaining: {new_balance}"
        )
    )


# =========================================================
# MY PURCHASES
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "📦 My Purchases"
)
def my_purchases(message):

    bot.send_message(
        message.chat.id,
        "📦 My Purchases\n\n"
        "এই version-এ purchase history আলাদা করে রাখা হয়নি।"
    )


# =========================================================
# HELP
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "ℹ️ Help"
)
def help_menu(message):

    bot.send_message(
        message.chat.id,
        "ℹ️ HELP\n\n"
        "📱 App Store → App দেখুন ও কিনুন\n"
        "💰 Balance → Points দেখুন\n"
        "💳 Visa Card → Demo card দেখুন\n"
        "💳 Add Balance → bKash/Nagad payment request\n\n"
        f"💳 Payment Number: {PAYMENT_NUMBER}"
    )


# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin(message):

    return message.from_user.id == ADMIN_ID


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "📊 Dashboard"
)
def dashboard(message):

    if not is_admin(message):
        return

    con = db()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM apps")
    apps = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM payments
        WHERE status='pending'
    """)

    pending = cur.fetchone()[0]

    con.close()

    bot.send_message(
        message.chat.id,
        "📊 ADMIN DASHBOARD\n\n"
        f"👥 Users: {users}\n"
        f"📱 Apps: {apps}\n"
        f"💳 Pending Payments: {pending}"
    )


# =========================================================
# ADMIN ADD APP
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "➕ Add App"
)
def add_app(message):

    if not is_admin(message):
        return

    msg = bot.send_message(
        message.chat.id,
        "📱 App Name লিখুন:"
    )

    bot.register_next_step_handler(
        msg,
        admin_app_name
    )


def admin_app_name(message):

    name = message.text.strip()

    msg = bot.send_message(
        message.chat.id,
        "📝 Description লিখুন:"
    )

    bot.register_next_step_handler(
        msg,
        lambda m: admin_app_description(
            m,
            name
        )
    )


def admin_app_description(message, name):

    desc = message.text.strip()

    msg = bot.send_message(
        message.chat.id,
        "💰 Price কত Points?"
    )

    bot.register_next_step_handler(
        msg,
        lambda m: admin_app_price(
            m,
            name,
            desc
        )
    )


def admin_app_price(message, name, desc):

    try:

        price = int(message.text)

        if price < 0:
            raise ValueError

    except:

        bot.send_message(
            message.chat.id,
            "❌ Price number হতে হবে।"
        )

        return

    msg = bot.send_message(
        message.chat.id,
        "📤 এখন App file/document পাঠান:"
    )

    bot.register_next_step_handler(
        msg,
        lambda m: admin_app_file(
            m,
            name,
            desc,
            price
        )
    )


def admin_app_file(
    message,
    name,
    desc,
    price
):

    if not message.document:

        bot.send_message(
            message.chat.id,
            "❌ Document হিসেবে App file পাঠান।"
        )

        return

    file_id = message.document.file_id

    con = db()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO apps
        (name, description, price, file_id, uploader)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        desc,
        price,
        file_id,
        message.from_user.id
    ))

    con.commit()
    con.close()

    bot.send_message(
        message.chat.id,
        "✅ APP ADDED\n\n"
        f"📱 {name}\n"
        f"💰 Price: {price} Points"
    )


# =========================================================
# ADMIN PAYMENTS
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "💳 Payments"
)
def payments(message):

    if not is_admin(message):
        return

    con = db()
    cur = con.cursor()

    cur.execute("""
        SELECT id, user_id, amount, method, trx
        FROM payments
        WHERE status='pending'
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    con.close()

    if not rows:

        bot.send_message(
            message.chat.id,
            "✅ No pending payments."
        )

        return

    for pid, uid, amount, method, trx in rows:

        bot.send_message(
            message.chat.id,
            "💳 PAYMENT\n\n"
            f"🆔 ID: {pid}\n"
            f"👤 User: {uid}\n"
            f"💰 Amount: {amount}\n"
            f"💳 Method: {method}\n"
            f"🧾 TRX: {trx}",
            reply_markup=payment_buttons(pid)
        )


# =========================================================
# ADMIN GIVE BALANCE
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "🎁 Give Balance"
)
def give_balance(message):

    if not is_admin(message):
        return

    msg = bot.send_message(
        message.chat.id,
        "User ID এবং amount দিন:\n\n"
        "Example:\n"
        "123456789 500"
    )

    bot.register_next_step_handler(
        msg,
        process_give_balance
    )


def process_give_balance(message):

    try:

        uid, amount = message.text.split()

        uid = int(uid)
        amount = int(amount)

        if amount <= 0:
            raise ValueError

    except:

        bot.send_message(
            message.chat.id,
            "❌ Format ভুল।"
        )

        return

    con = db()
    cur = con.cursor()

    cur.execute("""
        UPDATE users
        SET balance=balance+?
        WHERE user_id=?
    """, (
        amount,
        uid
    ))

    updated = cur.rowcount

    con.commit()
    con.close()

    if updated == 0:

        bot.send_message(
            message.chat.id,
            "❌ User পাওয়া যায়নি।"
        )

        return

    bot.send_message(
        message.chat.id,
        f"✅ {amount} Points added to {uid}"
    )

    try:

        bot.send_message(
            uid,
            f"🎁 Admin আপনাকে {amount} Points দিয়েছে!\n\n"
            f"💰 Balance: {get_balance(uid)}"
        )

    except:
        pass


# =========================================================
# ADMIN APPS
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "📱 Apps"
)
def admin_apps(message):

    if not is_admin(message):
        return

    con = db()
    cur = con.cursor()

    cur.execute("""
        SELECT id, name, price
        FROM apps
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    con.close()

    if not rows:

        bot.send_message(
            message.chat.id,
            "📭 No apps."
        )

        return

    text = "📱 APP LIST\n\n"

    for app_id, name, price in rows:

        text += (
            f"#{app_id} — {name}\n"
            f"💰 {price} Points\n\n"
        )

    bot.send_message(
        message.chat.id,
        text
    )


# =========================================================
# BROADCAST
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "📢 Broadcast"
)
def broadcast(message):

    if not is_admin(message):
        return

    msg = bot.send_message(
        message.chat.id,
        "📢 Broadcast message লিখুন:"
    )

    bot.register_next_step_handler(
        msg,
        process_broadcast
    )


def process_broadcast(message):

    con = db()
    cur = con.cursor()

    cur.execute(
        "SELECT user_id FROM users"
    )

    users = cur.fetchall()

    con.close()

    sent = 0

    for row in users:

        try:

            bot.send_message(
                row[0],
                "📢 BROADCAST\n\n"
                + message.text
            )

            sent += 1

        except:
            pass

    bot.send_message(
        ADMIN_ID,
        f"✅ Broadcast sent: {sent} users"
    )


# =========================================================
# USER PANEL
# =========================================================

@bot.message_handler(
    func=lambda m: m.text == "⬅️ User Panel"
)
def user_panel(message):

    add_user(message.from_user)

    bot.send_message(
        message.chat.id,
        "👤 USER PANEL",
        reply_markup=user_keyboard()
    )


# =========================================================
# RUN BOT
# =========================================================

print("================================")
print("🤖 APP STORE BOT STARTED")
print("================================")

bot.infinity_polling()