import telebot
import random
import time
from googletrans import Translator

# Add your bot token here
TOKEN = "YOUR_BOT_TOKEN"

bot = telebot.TeleBot(TOKEN)
translator = Translator()

user_data = {}  # In-memory storage for user data

# Button texts in English
buttons_en = {
    "start_mining": "Start Mining",
    "refer_friend": "Refer a friend to earn 0.1 core and +0.015core/hr mining speed",
    "claim_bonus": "Claim Daily Bonus",
    "check_balance": "Check Balance",
    "withdraw": "Withdraw",
    "translate": "Translate to Chinese"
}

# Button texts in Chinese
buttons_cn = {
    "start_mining": "开始挖矿",
    "refer_friend": "推荐朋友赚取 0.1 核心并 +0.015 核心/小时挖矿速度",
    "claim_bonus": "领取每日奖金",
    "check_balance": "检查余额",
    "withdraw": "提取",
    "translate": "翻译成英文"
}

# Function to generate a unique referral link
def generate_referral_link(user_id):
    referral_id = ''.join(random.choices('0123456789abcdef', k=8))
    if "referral_links" not in user_data:
        user_data["referral_links"] = {}
    user_data["referral_links"][referral_id] = user_id
    return f"https://t.me/PMM_MINER_BOT?start={referral_id}"

# Function to get mining speed based on referrals
def get_mining_speed(referrals):
    return 0.015 + (referrals * 0.0015)

# Function to handle daily bonus claim
def claim_daily_bonus(user_id):
    current_time = time.time()
    if "bonus" not in user_data[user_id]:
        user_data[user_id]["bonus"] = 0
    if current_time - user_data[user_id]["bonus"] >= 24 * 60 * 60:
        user_data[user_id]["bonus"] = current_time
        return True
    return False

# Function to get total mined (Placeholder)
def get_total_mined():
    return 0  # Change this according to your implementation

def create_keyboard(buttons):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    keyboard.add(
        telebot.types.KeyboardButton(buttons["start_mining"], web_app=telebot.types.WebAppInfo(url="https://comforting-profiterole-cee7c2.netlify.app/")),
        telebot.types.KeyboardButton(buttons["refer_friend"]),
        telebot.types.KeyboardButton(buttons["claim_bonus"]),
        telebot.types.KeyboardButton(buttons["check_balance"]),
        telebot.types.KeyboardButton(buttons["withdraw"]),
        telebot.types.KeyboardButton(buttons["translate"])
    )
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Initialize user data if they don't exist
    if user_id not in user_data:
        user_data[user_id] = {
            "referrals": 0,
            "balance": 0,
            "mining_speed": 0.015,
            "bonus": 0,
            "language": "en"
        }

    referral_id = message.text.split("start=")[1] if "start=" in message.text else None

    # Handle referral if the user started with a referral link
    if referral_id and "referral_links" in user_data and referral_id in user_data["referral_links"]:
        referrer_id = user_data["referral_links"][referral_id]
        if referrer_id != user_id:
            user_data[referrer_id]["referrals"] += 1
            new_mining_speed = get_mining_speed(user_data[referrer_id]["referrals"])
            user_data[referrer_id]["mining_speed"] = new_mining_speed
            user_data[referrer_id]["balance"] += 0.1
            bot.send_message(referrer_id, f"0.015core/h has been added to your mining speed for the referral. Your current mining speed is {new_mining_speed:.4f}core/h.")

    bot.reply_to(message, "Welcome to Pmm core mining Telegram bot!", reply_markup=create_keyboard(buttons_en if user_data[user_id]["language"] == "en" else buttons_cn))

@bot.message_handler(func=lambda message: message.text in [buttons_en["refer_friend"], buttons_cn["refer_friend"]])
def refer_friend(message):
    user_id = message.from_user.id
    referral_link = generate_referral_link(user_id)
    bot.reply_to(message, f"Share this link to refer a friend: {referral_link}")

@bot.message_handler(func=lambda message: message.text in [buttons_en["claim_bonus"], buttons_cn["claim_bonus"]])
def claim_bonus(message):
    user_id = message.from_user.id
    if claim_daily_bonus(user_id):
        user_data[user_id]["balance"] += 0.1
        bot.reply_to(message, "Daily bonus claimed successfully. 0.1 core added to your balance.")
    else:
        bot.reply_to(message, "You have already claimed your daily bonus today.")

@bot.message_handler(func=lambda message: message.text in [buttons_en["check_balance"], buttons_cn["check_balance"]])
def check_balance(message):
    user_id = message.from_user.id
    total_mined = get_total_mined()  # Placeholder for total mined core
    balance = user_data[user_id]["balance"]  # Get user's balance
    bot.reply_to(message, f"Your current balance: {balance} core\nTotal mined: {total_mined} core")

@bot.message_handler(func=lambda message: message.text in [buttons_en["withdraw"], buttons_cn["withdraw"]])
def withdraw(message):
    bot.reply_to(message, "Minimum withdrawal is 15 core. Withdrawals will be processed at the end of every week.")

@bot.message_handler(func=lambda message: message.text in [buttons_en["translate"], buttons_cn["translate"]])
def translate_buttons(message):
    user_id = message.from_user.id
    user_data[user_id]["language"] = "cn" if user_data[user_id]["language"] == "en" else "en"
    if user_data[user_id]["language"] == "cn":
        bot.reply_to(message, "所有按钮已翻译成中文", reply_markup=create_keyboard(buttons_cn))
    else:
        bot.reply_to(message, "All buttons have been translated to English", reply_markup=create_keyboard(buttons_en))

# Launch the bot
bot.polling()
