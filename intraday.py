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
Alert_Check_Duration = 2*60

#You need to copy paste condition in below mentioned Condition variable
#Execute this at Kaushal swing at 9.15 and check the stock to have great move by the end of teh day
KAUSAL_SWING = "( {cash} ( latest open = latest low and latest macd line( 26,12,9 ) > latest macd signal( 26,12,9 ) and latest close > latest max( 20 , latest open ) and latest volume > 1 day ago volume and latest open > 80 and [0] 30 minute macd line( 26,12,9 ) > [0] 30 minute macd signal( 26,12,9 ) and latest volume > latest sma( volume,10 ) * 1.5 and latest avg true range( 14 ) > 8 and latest adx( 14 ) > 19 ) ) "

BossScanner = "( {cash} ( latest close > latest upper bollinger band( 20 , 2 ) and weekly close > weekly upper bollinger band( 20 , 2 ) and monthly close > monthly upper bollinger band( 20 , 2 ) and latest rsi( 14 ) > 60 and weekly rsi( 14 ) > 60 and monthly rsi( 14 ) > 60 and monthly wma( monthly close , 30 ) > monthly wma( monthly close , 50 ) and 1 month ago  wma( monthly close , 30 )<= 1 month ago  wma( monthly close , 50 ) and monthly wma( monthly close , 30 ) > 60 and monthly wma( monthly close , 50 ) > 60 ) )"

BFSSwing = "( {cash} ( latest close > latest sum( close  *  volume, 20 ) / sum( volume ,20 ) and 1 day ago  close <= 1 day ago  sum( close  *  volume, 20 ) / sum( volume ,20 ) and latest close > 100 and latest adx di positive( 14 ) > latest adx di negative( 14 ) and latest volume > latest sma( volume,10 ) and weekly rsi( 14 ) > 60 and weekly close > weekly upper bollinger band( 20 , 2 ) ) )"

NayakLion = "( {cash} ( latest close > latest upper bollinger band( 20 , 2 ) and 1 day ago  close <= 1 day ago  upper bollinger band( 20 , 2 ) and weekly close > weekly upper bollinger band( 20 , 2 ) and 1 week ago  close <= 1 week ago  upper bollinger band( 20 , 2 ) and monthly close > monthly upper bollinger band( 20 , 2 ) and 1 month ago  close <= 1 month ago  upper bollinger band( 20 , 2 ) and latest volume > 100000 ) )"

Int_UBB_O_L = "( {33489} ( latest close > latest upper bollinger band( 20 , 2 ) and 1 day ago  close <= 1 day ago  upper bollinger band( 20 , 2 ) and latest open = latest low ) )"
Int_NCPR_O_L = "( {33489} ( abs( ( ( ( 1 day ago high + 1 day ago low + 1 day ago close / 3 ) + ( ( 1 day ago high + 1 day ago low + 1 day ago close / 3 ) - ( 1 day ago high + 1 day ago low / 2 ) ) - ( 1 day ago high + 1 day ago low / 2 ) ) ) ) < ( 1 day ago close * 0.001 ) and latest close > 300 and( {33489} ( [=1] 15 minute open = [=1] 15 minute high or [=1] 15 minute open = [=1] 15 minute low ) ) ) )"

conditionArray = { 
	           "Int_UBB_O_L":Int_UBB_O_L,
	           "Int_NCPR_O_L":Int_NCPR_O_L
                   
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
    print("in alert time check")
    CurrentTime = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
    Alert_Start_Time = 8 * 30 + 00
    Alert_End_Time = 17 * 60 + 00
    print("current time " + str(CurrentTime) + "  " + " starttime: " + str(Alert_Start_Time) + " end time: " + str(Alert_End_Time))
    
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
                #SendMessageToTelegram("What Alert: " + str(itr) + "\n No data")
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
