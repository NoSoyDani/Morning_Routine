import requests
import json
import time
import os
from os import remove
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from playsound import playsound
from gtts import gTTS
from aemet import Aemet
from datetime import datetime

#Obtein an ApiKey here:   https://opendata.aemet.es/centrodedescargas/altaUsuario?
aemetKey="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJoZWxpby52ZXJzaW9uMUBnbWFpbC5jb20iLCJqdGkiOiIyZWViMzlmYi1hY2U3LTRlZWYtYjQ2ZS1lYjdkMWIwZDgyY2MiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTU5NzYwMzkyMiwidXNlcklkIjoiMmVlYjM5ZmItYWNlNy00ZWVmLWI0NmUtZWI3ZDFiMGQ4MmNjIiwicm9sZSI6IiJ9.-Xh3kjIwSqmb85sXlif4phNzb9LjN1xNzrg2KY_KNNo"
#https://www.ine.es/daco/daco42/codmun/codmunmapa.htm
provinceCode="11"
townCode="11014" #ProvinceCode+TownCode

def date():
    date=datetime.now()
    months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    day = date.day
    month = months[date.month - 1]
    year = date.year
    date_format = "Hoy es {} de {} del {} \n".format(day, month, year)
    return date_format

def moment():

    now = datetime.now()
    now_format=now.strftime('%I:%M:%S').split(":")
    hour=now_format[0]
    min=now_format[1]
    if(str(hour)[0]=="0"):
        hour=hour[1]
    moment_format="Son las {} y {} \n".format(hour,min)
    return moment_format

def aemetProvince(province):
    url = "https://opendata.aemet.es/opendata/api/prediccion/provincia/hoy/{}".format(provinceCode)
    querystring = {"api_key":aemetKey}
    headers = {
        'cache-control': "no-cache"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    jsonToPythonDicc = json.loads(response.text)
    urlData=jsonToPythonDicc['datos']
    r = urlopen(urlData)
    relevantInformation = str(BeautifulSoup(r.read(), "html.parser"))
    r.close()
    parcialInit=relevantInformation.find(province)
    parcialMedium=relevantInformation.find(province,parcialInit+1)
    parcialFinal=relevantInformation.find("TEMPERATURAS")
    informationSummary=relevantInformation[parcialMedium+len(province):parcialFinal]+'\n'
    return informationSummary


def aemetTown(day): #Day 0 is today, 1 tomorrow ...

    url = "https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/{}".format(townCode)
    querystring = {"api_key":aemetKey}
    headers = {
        'cache-control': "no-cache"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    jsonToPythonDicc = json.loads(response.text)
    dataUrl=jsonToPythonDicc['datos']
    responseData = requests.request("GET", dataUrl)
    jsonToPythonDiccData = json.loads(responseData.text)
    daySelected=jsonToPythonDiccData[0]["prediccion"]["dia"][day]["fecha"]
    maximumTemperature=jsonToPythonDiccData[0]["prediccion"]["dia"][day]["temperatura"]["maxima"]
    minimumTemperature=jsonToPythonDiccData[0]["prediccion"]["dia"][day]["temperatura"]["minima"]
    probabilityOfPrecipitation=jsonToPythonDiccData[0]["prediccion"]["dia"][day]["probPrecipitacion"][0]["value"]
    maximumHumidity=jsonToPythonDiccData[0]["prediccion"]["dia"][day]["humedadRelativa"]["maxima"]
    minimumHumidity=jsonToPythonDiccData[0]["prediccion"]["dia"][day]["humedadRelativa"]["minima"]

    result="La temperatura máxima será de {} grados,siendo la mínima de {} grados, a su vez la probabilidad de precipitaciones es del {} por ciento.El ambiente posee una humedad entre {} y {} por ciento \n".format(maximumTemperature,minimumTemperature,probabilityOfPrecipitation,minimumHumidity,maximumHumidity)
    return result

def sunData(lat,lng,variation):
    latitude=str(lat)
    longitude=str(lng)
    url="https://api.sunrise-sunset.org/json?lat={}&lng={}&date=today".format(latitude,longitude)
    response = requests.request("GET", url)
    jsonToPythonDicc = json.loads(response.text)
    sunrise=jsonToPythonDicc["results"]["sunrise"]
    sunset=jsonToPythonDicc["results"]["sunset"]
    sunrise=sunrise[:-2].split(":") #Without AM or PM
    sunset=sunset[:-2].split(":")
    sunriseHour=int(sunrise[0])+variation
    sunriseMinutes=sunrise[1]
    sunsetHour=int(sunset[0])+variation
    sunsetMinutes=sunset[1]
    result="Amanece a las {} y {} minutos y anochece a las {} y {} \n".format(sunriseHour,sunriseMinutes,sunsetHour,sunsetMinutes)
    return result


def routineSummary(date,moment,aemetProvince,aemetTown,sunData):
    summary=moment+date+sunData+aemetTown+aemetProvince
    return summary

def speech(txt):
    language = 'es-es'
    spch = gTTS(text=txt, lang=language, slow=False)
    spch.save("./Audios/heliosays.mp3")
    playsound("./Audios/heliosays.mp3")
    remove("./Audios/heliosays.mp3")


speech(routineSummary(date(),moment(),aemetProvince("CÁDIZ"),aemetTown(0),sunData(36.2768,-6.08844,2)))
