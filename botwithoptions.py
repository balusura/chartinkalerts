import telebot

# Replace 'YOUR_API_TOKEN' with your bot's API token
bot = telebot.TeleBot('5963732843:AAGhk6iUG_r5-AsN7m16RSbm7SOK_JUepMc')

# Function to calculate the sum of 2 + 3
def calculate_sum(chat_id):
    result = 2 + 3
    bot.send_message(chat_id, f"The sum of 2 + 3 is {result}")

# Adding custom menu name
@bot.message_handler(commands=['intraday'])
def intraday_menu(message):
    # Call the calculate_sum function when "intraday" menu is selected
    calculate_sum(message.chat.id)

def main():
    # Start the bot
    print("Bot is Running...")
    bot.polling()

if __name__ == "__main__":
    main()
