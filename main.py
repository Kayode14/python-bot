import telebot
import random
import time
from googletrans import Translator

# Add your bot token here
TOKEN = "7191033335:AAGFFNi1jEfvNQyoMR7e4Uc3Fr-VRED8ll4"

bot = telebot.TeleBot(TOKEN)
translator = Translator()

user_data = {}  # In-memory storage for user-specific data

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

# Initialize with English buttons
current_buttons = buttons_en

# Function to generate a unique referral link
def generateReferralLink(userId):
    referralId = ''.join(random.choices('0123456789abcdef', k=8))
    if "referralLinks" not in user_data:
        user_data["referralLinks"] = {}
    user_data["referralLinks"][referralId] = userId
    return f"https://t.me/PMM_MINER_BOT?start={referralId}"

# Function to get mining speed based on referrals
def getMiningSpeed(referrals):
    return 0.015 + (referrals * 0.0015)

# Function to handle daily bonus claim
def claimDailyBonus(userId):
    current_time = time.time()
    if "bonus" not in user_data[userId] or current_time - user_data[userId]["bonus"] >= 24 * 60 * 60:
        user_data[userId]["bonus"] = current_time
        return True
    return False

# Function to get total mined
def getTotalMined(userId):
    # Placeholder for total mined calculation
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

def initialize_user_data(userId):
    if userId not in user_data:
        user_data[userId] = {
            "referrals": 0,
            "balance": 0,
            "bonus": 0
        }

@bot.message_handler(commands=['start'])
def start(message):
    userId = message.from_user.id
    referralId = message.text.split("start=")[1] if "start=" in message.text else None

    initialize_user_data(userId)

    # Handle referral if the user started with a referral link
    if referralId and "referralLinks" in user_data and referralId in user_data["referralLinks"] and user_data["referralLinks"][referralId] != userId:
        referrerId = user_data["referralLinks"][referralId]
        initialize_user_data(referrerId)
        user_data[referrerId]["referrals"] += 1
        newMiningSpeed = getMiningSpeed(user_data[referrerId]["referrals"])
        bot.send_message(referrerId, f"0.015core/h has been added to your mining speed for the referral. Your current mining speed is {newMiningSpeed:.4f}core/h.")
        # Add 0.1 core to referrer's balance
        user_data[referrerId]["balance"] += 0.1

    bot.reply_to(message, "Welcome to Pmm core mining Telegram bot!", reply_markup=create_keyboard(current_buttons))

@bot.message_handler(func=lambda message: message.text in [buttons_en["refer_friend"], buttons_cn["refer_friend"]])
def refer_friend(message):
    userId = message.from_user.id
    initialize_user_data(userId)
    referralLink = generateReferralLink(userId)
    bot.reply_to(message, f"Share this link to refer a friend: {referralLink}")

@bot.message_handler(func=lambda message: message.text in [buttons_en["claim_bonus"], buttons_cn["claim_bonus"]])
def claim_bonus(message):
    userId = message.from_user.id
    initialize_user_data(userId)
    if claimDailyBonus(userId):
        # Add daily bonus to balance
        user_data[userId]["balance"] += 0.1
        bot.reply_to(message, "Daily bonus claimed successfully. 0.1 core added to your balance.")
    else:
        bot.reply_to(message, "You have already claimed your daily bonus today.")

@bot.message_handler(func=lambda message: message.text in [buttons_en["check_balance"], buttons_cn["check_balance"]])
def check_balance(message):
    userId = message.from_user.id
    initialize_user_data(userId)
    total_mined = getTotalMined(userId)  # Get total mined core
    balance = user_data[userId]["balance"]  # Get user's balance
    bot.reply_to(message, f"Your current balance: {balance} core\nTotal mined: {total_mined} core")

@bot.message_handler(func=lambda message: message.text in [buttons_en["withdraw"], buttons_cn["withdraw"]])
def withdraw(message):
    userId = message.from_user.id
    initialize_user_data(userId)
    bot.reply_to(message, "Minimum withdrawal is 15 core. Withdrawals will be processed at the end of every week.")

@bot.message_handler(func=lambda message: message.text in [buttons_en["translate"], buttons_cn["translate"]])
def translate_buttons(message):
    global current_buttons
    if current_buttons == buttons_en:
        current_buttons = buttons_cn
        bot.reply_to(message, "所有按钮已翻译成中文", reply_markup=create_keyboard(current_buttons))
    else:
        current_buttons = buttons_en
        bot.reply_to(message, "All buttons have been translated to English", reply_markup=create_keyboard(current_buttons))

# Launch the bot
bot.polling()
