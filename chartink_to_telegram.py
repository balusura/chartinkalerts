import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from time import sleep

Charting_Link = "https://chartink.com/screener/"
Charting_url = 'https://chartink.com/screener/process'

TelegramBotCredential = '5963732843:AAGhk6iUG_r5-AsN7m16RSbm7SOK_JUepMc'
ReceiverTelegramID = '882232390' #my personal id

#you can set this variable as per your requirment, its 30 minute in gap of 30 second it will check and send the alert
Alert_Check_Duration = 3

#You need to copy paste condition in below mentioned Condition variable

Condition = "( {57960} ( 1 day ago ema ( close,3 ) > 1 day ago ema ( close,8 ) and 2 day ago  ema ( close,3 )<= 2 day ago  ema ( close,8 ) and 1 day ago \"close - 1 candle ago close / 1 candle ago close * 100\" >= 2 and 1 day ago volume >= 100000 and latest close > 1 day ago close ) ) "

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
            df = df.append(item, ignore_index=True)
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
    
def strategy():
    data = GetDataFromChartink(Condition)

    if (len(data)==0):
        print("The data is empty")
    else:
        data = data.sort_values(by='per_chg', ascending=False)
        print(data)

        #data.to_csv("Chartink_result.csv")
        #SendTelegramFile("Chartink_result.csv")

        dataMessage = "What Alert: 30Min BB\n"  #Give meaningful alert name here
        current_time = datetime.datetime.now()
        dataMessage =  dataMessage + "When:" + str(current_time)
        HeaderData  =  "Stock               "  + " %Chg     "  + " Close     "  #Customize your header here
        dataMessage = dataMessage + "\n" + HeaderData

        for ind in data.index:
            dataMessage = dataMessage + "\n" + str(data['nsecode'][ind]).ljust(20) + "        " +  str(data['per_chg'][ind]) + "      " + str(data['close'][ind])
    
        print(dataMessage)

        SendMessageToTelegram(dataMessage)        
        sleep(Alert_Check_Duration)
        
if __name__ == '__main__':  
    strategy()
