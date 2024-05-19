import telebot
import crypto
import random
import time

# Add your bot token here
TOKEN = "7191033335:AAGFFNi1jEfvNQyoMR7e4Uc3Fr-VRED8ll4"

bot = telebot.TeleBot(TOKEN)

userReferrals = {}  # In-memory storage for referral count and mining speed
referralLinks = {}  # In-memory storage for referral links
botUsername = ""  # Variable to store the bot's username
bonus = {}  # In-memory storage for daily bonus claim time

# Function to generate a unique referral link
def generateReferralLink(userId):
    referralId = crypto.random_bytes(4).hex()
    referralLinks[referralId] = userId
    return f"https://t.me/pmm_miner_bot?start={referralId}"

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
    referralId = message.text.split("_start=")[1] if "_start=" in message.text else None

    # Handle referral if the user started with a referral link
    if referralId and referralLinks.get(referralId) and referralLinks[referralId] != userId:
        referrerId = referralLinks[referralId]
        userReferrals[referrerId] = userReferrals.get(referrerId, 0) + 1
        newMiningSpeed = getMiningSpeed(userReferrals[referrerId])
        bot.reply_to(referrerId, f"0.015core/h has been added to your mining speed for the referral. Your current mining speed is {newMiningSpeed:.4f}core/h.")

    # Initialize user's referral count if they don't have one
    userReferrals[userId] = userReferrals.get(userId, 0)

    bot.reply_to(message.chat.id, "Welcome to Pmm core mining Telegram bot!", reply_markup={
        "keyboard": [
            [{"text": "web app", "web_app": {"url": "https://comforting-profiterole-cee7c2.netlify.app/"} }],
            [{"text": "Refer a friend"}, {"text": "Claim Daily Bonus"}],
            [{"text": "Check Balance"}, {"text": "Withdraw"}]
        ]
    })

@bot.message_handler(func=lambda message: message.text == "Refer a friend")
def refer_friend(message):
    userId = message.from_user.id
    userReferrals[userId] = userReferrals.get(userId, 0)
    referralLink = generateReferralLink(userId)
    bot.reply_to(message.chat.id, f"Share this link to refer a friend: {referralLink}")

@bot.message_handler(func=lambda message: message.text == "Claim Daily Bonus")
def claim_bonus(message):
    userId = message.from_user.id
    if claimDailyBonus(userId):
        # Add daily bonus to balance
        # Adjust the bonus amount as needed
        # Here, we're adding 0.1 core
        bot.reply_to(message.chat.id, "Daily bonus claimed successfully. 0.1 core added to your balance.")
    else:
        bot.reply_to(message.chat.id, "You have already claimed your daily bonus today.")

@bot.message_handler(func=lambda message: message.text == "Check Balance")
def check_balance(message):
    userId = message.from_user.id
    total_mined = getTotalMined()  # Get total mined core
    # Placeholder for balance calculation
    balance = 0  # Change this according to your implementation
    bot.reply_to(message.chat.id, f"Your current balance: {balance} core\nTotal mined: {total_mined} core")

@bot.message_handler(func=lambda message: message.text == "Withdraw")
def withdraw(message):
    bot.reply_to(message.chat.id, "Minimum withdrawal is 15 core. Withdrawals will be processed at the end of every week.")

# Launch the bot
bot.polling()
