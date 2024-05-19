import telebot
import random
import time
from googletrans import Translator

# Add your bot token here
TOKEN = "7191033335:AAGFFNi1jEfvNQyoMR7e4Uc3Fr-VRED8ll4"

bot = telebot.TeleBot(TOKEN)
translator = Translator()

userReferrals = {}  # In-memory storage for referral count and mining speed
referralLinks = {}  # In-memory storage for referral links
bonus = {}  # In-memory storage for daily bonus claim time
balances = {}  # In-memory storage for user balances

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

@bot.message_handler(commands=['start'])
def start(message):
    userId = message.from_user.id
    referralId = message.text.split("start=")[1] if "start=" in message.text else None

    # Handle referral if the user started with a referral link
    if referralId and referralLinks.get(referralId) and referralLinks[referralId] != userId:
        referrerId = referralLinks[referralId]
        userReferrals[referrerId] = userReferrals.get(referrerId, 0) + 1
        newMiningSpeed = getMiningSpeed(userReferrals[referrerId])
        bot.send_message(referrerId, f"0.015core/h has been added to your mining speed for the referral. Your current mining speed is {newMiningSpeed:.4f}core/h.")
        # Add 0.1 core to referrer's balance
        balances[referrerId] = balances.get(referrerId, 0) + 0.1

    # Initialize user's referral count if they don't have one
    userReferrals[userId] = userReferrals.get(userId, 0)

    bot.reply_to(message, "Welcome to Pmm core mining Telegram bot!", reply_markup=telebot.types.ReplyKeyboardMarkup(row_width=2).add(
        telebot.types.KeyboardButton("Start Mining", web_app=telebot.types.WebAppInfo(url="https://comforting-profiterole-cee7c2.netlify.app/")),
        telebot.types.KeyboardButton("Refer a friend to earn 0.1 core and +0.015core/hr mining speed"),
        telebot.types.KeyboardButton("Claim Daily Bonus"),
        telebot.types.KeyboardButton("Check Balance"),
        telebot.types.KeyboardButton("Withdraw"),
        telebot.types.KeyboardButton("Translate (EN/CH)")
    ))

@bot.message_handler(func=lambda message: message.text == "Refer a friend to earn 0.1 core and +0.015core/hr mining speed")
def refer_friend(message):
    userId = message.from_user.id
    userReferrals[userId] = userReferrals.get(userId, 0)
    referralLink = generateReferralLink(userId)
    bot.reply_to(message, f"Share this link to refer a friend: {referralLink}")

@bot.message_handler(func=lambda message: message.text == "Claim Daily Bonus")
def claim_bonus(message):
    userId = message.from_user.id
    if claimDailyBonus(userId):
        # Add daily bonus to balance
        # Here, we're adding 0.1 core
        balances[userId] = balances.get(userId, 0) + 0.1
        bot.reply_to(message, "Daily bonus claimed successfully. 0.1 core added to your balance.")
    else:
        bot.reply_to(message, "You have already claimed your daily bonus today.")

@bot.message_handler(func=lambda message: message.text == "Check Balance")
def check_balance(message):
    userId = message.from_user.id
    total_mined = getTotalMined()  # Get total mined core
    balance = balances.get(userId, 0)  # Get user's balance
    bot.reply_to(message, f"Your current balance: {balance} core\nTotal mined: {total_mined} core")

@bot.message_handler(func=lambda message: message.text == "Withdraw")
def withdraw(message):
    bot.reply_to(message, "Minimum withdrawal is 15 core. Withdrawals will be processed at the end of every week.")

@bot.message_handler(func=lambda message: message.text == "Translate (EN/CH)")
def ask_translation(message):
    bot.reply_to(message, "Please send the text you want to translate.")

@bot.message_handler(func=lambda message: True)
def translate_message(message):
    userId = message.from_user.id
    if message.text.startswith("/"):
        return  # Skip commands

    if message.reply_to_message and message.reply_to_message.text == "Please send the text you want to translate.":
        translated_text = translator.translate(message.text, src='auto', dest='zh-cn' if message.text.isascii() else 'en').text
        bot.reply_to(message, translated_text)

# Launch the bot
bot.polling()
