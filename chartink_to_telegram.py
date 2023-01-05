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

ShortTermUptrend = "( {57960} ( 1 day ago ema ( close,3 ) > 1 day ago ema ( close,8 ) and 2 day ago  ema ( close,3 )<= 2 day ago  ema ( close,8 ) and 1 day ago \"close - 1 candle ago close / 1 candle ago close * 100\" >= 2 and 1 day ago volume >= 100000 and latest close > 1 day ago close ) ) "

NayakLion = "( {57960} ( 1 day ago ema ( close,3 ) > 1 day ago ema ( close,8 ) and 2 day ago  ema ( close,3 )<= 2 day ago  ema ( close,8 ) and 1 day ago \"close - 1 candle ago close / 1 candle ago close * 100\" >= 2 and 1 day ago volume >= 100000 and latest close > 1 day ago close ) ) "

RSIDMI = "( {57960} ( 1 day ago ema ( close,3 ) > 1 day ago ema ( close,8 ) and 2 day ago  ema ( close,3 )<= 2 day ago  ema ( close,8 ) and 1 day ago \"close - 1 candle ago close / 1 candle ago close * 100\" >= 2 and 1 day ago volume >= 100000 and latest close > 1 day ago close ) ) "

conditionArray = { "3 ema cross 8 ema":Condition, 
                   "Short Term Uptrend":ShortTermUptrend, 
                   "Nayak Lion Scanner":NayakLion, 
                   "DMI-RSI":RSIDMI 
                 }

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
    
def isCorrectTimeToalert():
    #print("in alert time check")
    CurrentTime = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
    Alert_Start_Time = 9 * 60 + 20
    Alert_End_Time = 15 * 60 + 50
    
    if (CurrentTime >= Alert_Start_Time and CurrentTime <= Alert_End_Time):        
        return True
    else:        
        return False
    
    
def strategy():
    while (isCorrectTimeToalert()):
        for itr in conditionArray:
            data = GetDataFromChartink(conditionArray[itr])

            if (len(data)==0):
                print("The data is empty")
                SendMessageToTelegram("What Alert: " + str(itr) + "\n No data")
                continue
            else:
                data = data.sort_values(by='per_chg', ascending=False)
                print(data)

                #data.to_csv("Chartink_result.csv")
                #SendTelegramFile("Chartink_result.csv")

                dataMessage = "What Alert: " + str(itr) + "\n"  #Give meaningful alert name here
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
