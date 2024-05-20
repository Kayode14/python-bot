import telebot
import random
import time
from googletrans import Translator

# Add your bot token here
TOKEN = "7191033335:AAGFFNi1jEfvNQyoMR7e4Uc3Fr-VRED8ll4"
GROUP_ID = "@PMM_CORE"  # Replace with your group's ID

bot = telebot.TeleBot(TOKEN)
translator = Translator()

userReferrals = {}  # In-memory storage for referral count and mining speed
referralLinks = {}  # In-memory storage for referral links
bonus = {}  # In-memory storage for daily bonus claim time
balances = {}  # In-memory storage for user balances
user_data = {}  # In-memory storage for all user data, including balance and language preference

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
    referralLinks[referralId] = userId
    return f"https://t.me/PMM_MINER_BOT?start={referralId}"

# Function to get mining speed based on referrals
def getMiningSpeed(referrals):
    return 0.015 + (referrals * 0.0015)

# Function to handle daily bonus claim
def claimDailyBonus(userId):
    current_time = time.time()
    if userId not in bonus or current_time - bonus[userId] >= 24 * 60 * 60:
        bonus[userId] = current_time
        return True
    return False

# Function to get total mined
def getTotalMined():
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

def is_member(user_id, group_id):
    try:
        member_status = bot.get_chat_member(group_id, user_id).status
        return member_status in ['member', 'administrator', 'creator']
    except:
        return False

def ensure_user_initialized(user_id):
    if user_id not in user_data:
        user_data[user_id] = {"balance": 0, "language": "en"}

@bot.message_handler(commands=['start'])
def start(message):
    userId = message.from_user.id
    referralId = message.text.split("start=")[1] if "start=" in message.text else None

    # Ensure user data is initialized
    ensure_user_initialized(userId)

    if not is_member(userId, GROUP_ID):
        bot.reply_to(message, f"Please join our group {GROUP_ID} first to use the bot.")
        return

    # Handle referral if the user started with a referral link
    if referralId and referralLinks.get(referralId) and referralLinks[referralId] != userId:
        referrerId = referralLinks[referralId]
        ensure_user_initialized(referrerId)  # Ensure referrer data is initialized
        userReferrals[referrerId] = userReferrals.get(referrerId, 0) + 1
        newMiningSpeed = getMiningSpeed(userReferrals[referrerId])
        bot.send_message(referrerId, f"0.015core/h has been added to your mining speed for the referral. Your current mining speed is {newMiningSpeed:.4f}core/h.")
        # Add 0.1 core to referrer's balance
        user_data[referrerId]["balance"] += 0.1

    # Add 0.1 core to new user's balance for joining the group
    user_data[userId]["balance"] += 0.1
    bot.send_message(userId, "You have earned 0.1 core for joining the group.")

    # Initialize user's referral count if they don't have one
    userReferrals[userId] = userReferrals.get(userId, 0)

    bot.reply_to(message, "Welcome to Pmm core mining Telegram bot!", reply_markup=create_keyboard(current_buttons))

@bot.message_handler(func=lambda message: message.text == current_buttons["refer_friend"])
def refer_friend(message):
    userId = message.from_user.id
    ensure_user_initialized(userId)
    userReferrals[userId] = userReferrals.get(userId, 0)
    referralLink = generateReferralLink(userId)
    bot.reply_to(message, f"Share this link to refer a friend: {referralLink}")

@bot.message_handler(func=lambda message: message.text == current_buttons["claim_bonus"])
def claim_bonus(message):
    userId = message.from_user.id
    ensure_user_initialized(userId)
    if claimDailyBonus(userId):
        # Add daily bonus to balance
        # Here, we're adding 0.1 core
        user_data[userId]["balance"] += 0.1
        bot.reply_to(message, "Daily bonus claimed successfully. 0.1 core added to your balance.")
    else:
        bot.reply_to(message, "You have already claimed your daily bonus today.")

@bot.message_handler(func=lambda message: message.text == current_buttons["check_balance"])
def check_balance(message):
    userId = message.from_user.id
    ensure_user_initialized(userId)
    total_mined = getTotalMined()  # Get total mined core
    balance = user_data[userId]["balance"]  # Get user's balance
    bot.reply_to(message, f"Your current balance: {balance} core\nTotal mined: {total_mined} core")

@bot.message_handler(func=lambda message: message.text == current_buttons["withdraw"])
def withdraw(message):
    userId = message.from_user.id
    ensure_user_initialized(userId)
    bot.reply_to(message, "Minimum withdrawal is 15 core. Withdrawals will be processed at the end of every week.")

@bot.message_handler(func=lambda message: message.text == current_buttons["translate"])
def translate_buttons(message):
    userId = message.from_user.id
    ensure_user_initialized(userId)
    if user_data[userId]["language"] == "en":
        user_data[userId]["language"] = "cn"
        current_buttons = buttons_cn
        bot.reply_to(message, "所有按钮已翻译成中文", reply_markup=create_keyboard(current_buttons))
    else:
        user_data[userId]["language"] = "en"
        current_buttons = buttons_en
        bot.reply_to(message, "All buttons have been translated to English", reply_markup=create_keyboard(current_buttons))

# Launch the bot
bot.polling()
