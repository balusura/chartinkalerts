import telebot
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from time import sleep

Charting_Link = "https://chartink.com/screener/"
Charting_url = 'https://chartink.com/screener/process'

TelegramBotCredential = '5963732843:AAGhk6iUG_r5-AsN7m16RSbm7SOK_JUepMc'
ReceiverTelegramID = '882232390' #my personal id

#you can set this variable as per your requirment, its waiting time before next execution (15 minute = 15 * 60)
Alert_Check_Duration = 5*60

#You need to copy paste condition in below mentioned Condition variable
#Execute this at Kaushal swing at 9.15 and check the stock to have great move by the end of teh day
CANDLE_PATTERN = "( {cash} ( ( {cash} ( 3 months ago close < 3 months ago open and 2 months ago close < 2 months ago open and 2 months ago low < 3 months ago low and 1 month ago close > 1 month ago open and 1 month ago close > 2 months ago high and 1 month ago rsi( 14 ) > 55 and monthly close > 1 month ago high and market cap > 1000 ) ) ) )"
GOLDEN_ENTRY = " ( {cash} ( 2 months ago open > 2 months ago lower bollinger band( 20 , 2 ) and 2 months ago low > 2 months ago lower bollinger band( 20 , 2 ) and 2 months ago close < 2 months ago upper bollinger band( 20 , 2 ) and 2 months ago high < 2 months ago upper bollinger band( 20 , 2 ) and 2 months ago close > 2 months ago open and 1 month ago close > 1 month ago open and 1 month ago close > 1 month ago upper bollinger band( 20 , 2 ) and monthly close > 1 month ago high ) )" 
KAUSAL_SWING = "( {cash} ( latest open = latest low and latest macd line( 26,12,9 ) > latest macd signal( 26,12,9 ) and latest close > latest max( 20 , latest open ) and latest volume > 1 day ago volume and latest open > 80 and [0] 30 minute macd line( 26,12,9 ) > [0] 30 minute macd signal( 26,12,9 ) and latest volume > latest sma( volume,10 ) * 1.5 and latest avg true range( 14 ) > 8 and latest adx( 14 ) > 19 ) ) "

BossScanner = "( {cash} ( latest close > latest upper bollinger band( 20 , 2 ) and weekly close > weekly upper bollinger band( 20 , 2 ) and monthly close > monthly upper bollinger band( 20 , 2 ) and latest rsi( 14 ) > 60 and weekly rsi( 14 ) > 60 and monthly rsi( 14 ) > 60 and monthly wma( monthly close , 30 ) > monthly wma( monthly close , 50 ) and 1 month ago  wma( monthly close , 30 )<= 1 month ago  wma( monthly close , 50 ) and monthly wma( monthly close , 30 ) > 60 and monthly wma( monthly close , 50 ) > 60 ) )"

BFSSwing = "( {cash} ( latest close > latest sum( close  *  volume, 20 ) / sum( volume ,20 ) and 1 day ago  close <= 1 day ago  sum( close  *  volume, 20 ) / sum( volume ,20 ) and latest close > 100 and latest adx di positive( 14 ) > latest adx di negative( 14 ) and latest volume > latest sma( volume,10 ) and weekly rsi( 14 ) > 60 and weekly close > weekly upper bollinger band( 20 , 2 ) ) )"

NayakLion = "( {cash} ( latest close > latest upper bollinger band( 20 , 2 ) and 1 day ago  close <= 1 day ago  upper bollinger band( 20 , 2 ) and weekly close > weekly upper bollinger band( 20 , 2 ) and 1 week ago  close <= 1 week ago  upper bollinger band( 20 , 2 ) and monthly close > monthly upper bollinger band( 20 , 2 ) and 1 month ago  close <= 1 month ago  upper bollinger band( 20 , 2 ) and latest volume > 100000 ) )"

def GetDataFromChartink(payload):
    payload = {'scan_clause': payload}
    
    with requests.Session() as s:
        r = s.get(Charting_Link)
        soup = BeautifulSoup(r.text, "html.parser")
        csrf = soup.select_one("[name='csrf-token']")['content']
        s.headers['x-csrf-token'] = csrf
        r = s.post(Charting_url, data=payload)

        df = pd.DataFrame()
        for item in r.json()['data']:
            df = df._append(item, ignore_index=True)
    return df
    
def SendMessageToTelegram(Message):
    try:
        Url = "https://api.telegram.org/bot" + str(TelegramBotCredential) +  "/sendMessage?chat_id=" + str(ReceiverTelegramID)
        
        textdata ={ "text":Message}
        response = requests.request("POST",Url,params=textdata)
    except Exception as e:
        Message = str(e) + ": Exception occur in SendMessageToTelegram"
        print(Message)  
		
		
def SendTelegramFile(FileName):
    Documentfile={'document':open(FileName,'rb')}
    
    Fileurl = "https://api.telegram.org/bot" + str(TelegramBotCredential) +  "/sendDocument?chat_id=" + str(ReceiverTelegramID)
      
    response = requests.request("POST",Fileurl,files=Documentfile)

def SendMessageToTelegramWithURL(messages):
    # Combine all messages into one
    message_text = "\n".join(messages)
    send_message_url = f"https://api.telegram.org/bot{TelegramBotCredential}/sendMessage"
    payload = {
        "chat_id": ReceiverTelegramID,
        "text": message_text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True  # Disable URL previews
    }
    response = requests.post(send_message_url, json=payload)
       
def golden_entry(chat_id):
    messages = []  # Initialize an empty list to store messages
    desc = "Monthly BB Blast"
    bot.send_message(chat_id, f"Golden-Entry Scanner \n{desc}")
    data = GetDataFromChartink(GOLDEN_ENTRY)
    if (len(data)==0):
        print("The data is empty")
        SendMessageToTelegram("What Alert: " + "golden_entry" + "\n No data")
    else:
        data = data.sort_values(by='per_chg', ascending=False)
        print(data)

        dataMessage = "What Alert: " + "golden_entry" + "\n"  #Give meaningful alert name here
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%d/%m/%y %H:%M")
        dataMessage =  dataMessage + "When: " + str(formatted_time)                    
        dataMessage = dataMessage + "\n"
        i = 0
        for ind in data.index:
            stock_name = str(data['nsecode'][ind])
            stock_url = f"https://in.tradingview.com/chart/?symbol=NSE:{stock_name}"
            cmp_price = " CMP:" + str(data['close'][ind]) + "  (" + str(data['per_chg'][ind]) + "%)"
            if i == 0:
                dataText = dataMessage
                SendMessageToTelegram(dataText)
            else:
                dataText = ""
            messages.append(f"[{stock_name}]({stock_url}) {cmp_price}")
            i = i + 1
    
        print(messages)
        SendMessageToTelegramWithURL(messages)

# Replace 'YOUR_API_TOKEN' with your bot's API token
bot = telebot.TeleBot(TelegramBotCredential)

# Adding custom menu name
@bot.message_handler(commands=['golden_entry'])
def golden_entry_menu(message):
    golden_entry(message.chat.id)

def main():
    # Start the bot
    print("Bot is Running...")
    bot.polling()

if __name__ == "__main__":
    main()
