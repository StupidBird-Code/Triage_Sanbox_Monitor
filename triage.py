import requests
import datetime
from bs4 import BeautifulSoup
import hashlib
import random
import json
import time
import os
import re

user_agent = {
              "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
             }
#proxies = {'https': '127.0.0.1:7890'}
proxies = {}
write_file = 'triage_ioc.txt'

def get_webcontent(url):
    
    try:
        response = requests.get(url,proxies=proxies,headers=user_agent,timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            return soup
    except requests.exceptions.RequestException as e:
        print("[ERROR]:Fail to get WebContent!", e)
        return False
            

def parse_sample_class(element):

    sample_class = []
    temp = element.split('span class=')
    if len(temp)<2:
        return sample_class
    else:
        for str in temp:
            if str.find('span')!=-1:
                sample_class.append(str.split('">')[-1].split('</')[0])
        return sample_class
        
def get_sample_c2(sample_id):
    
    sanbox_url = 'https://tria.ge/' + sample_id
    print(sanbox_url)
    soup = get_webcontent(sanbox_url)
    if soup == False:
        return []
    temp = soup.find_all("span", class_="clipboard")
    regex = re.compile('(?<=title=").*?(?=")')
    c2 = regex.findall(str(temp))
    return c2
   
def download_from_url(url,save_file):
    
    try:
        response = requests.get(url,proxies=proxies,stream=True,timeout=8)
        if response.status_code == 200:
            with open(save_file, "wb") as f:
                for ch in response:            
                    f.write(ch)
                f.close()          
    except requests.exceptions.RequestException as e:
        print("Error downloading file:"+save_file, e)
        
def write_to_file(str):

    with open(write_file,'a',encoding='utf-8') as d:
        d.write(str+'\n')
        d.close

def parse_triage():        
    
    soup= get_webcontent('https://tria.ge/reports/public')
    if soup == False:
        return
    #print(soup)
    #print('——————————————————————————————————————————————————————')
    
    createtime = soup.find_all("div", class_="column-created")
    hash = soup.find_all("div", class_="column-hash")
    filename = soup.find_all("div", class_="column-target")
    fileclass = soup.find_all("div", class_="tags nano")
    score = soup.find_all("div", class_="column-score")
    regex = re.compile('(?<=data-sample-id=").*?(?=")')  #提取href=""之间的url链接
    sample_id = regex.findall(str(soup))
    
    i = 0
    while i<len(createtime):
    
        if str(score[i]).find('Running')!=-1 or str(score[i]).find('Submission')!=-1:
            i = i + 1
            continue
            
        create_time = str(createtime[i]).split('">')[-1].split('</')[0]
        print(create_time)
        
        file_name = str(filename[i]).split('title="')[-1].split('">')[0]
        print(file_name)
        
        sha256 = str(hash[i]).split('clipboard="')[-1].split('"')[0]
        if sha256.find('<div class=')==-1:
            print(sha256)
        else:
            print("")
            
        file_class = parse_sample_class(str(fileclass[i]))
        print(file_class)
        
        sanbox_score = str(score[i]).split('">')[-1].split('</')[0]
        print(sanbox_score)
        
        print(sample_id[i])
        
        if sanbox_score!='' and int(sanbox_score)>=8:
            c2 = get_sample_c2(sample_id[i])
            print(c2)
        
        if int(sanbox_score)>=8:
            if len(sha256) ==64:
                write_to_file(sha256)
            if c2!=[] and len(c2)<5:
                for domain in c2:
                    write_to_file(domain)
        
        #if len(sha256) ==64:
            #print('Download sample:',sha256)
            #download_url = 'https://tria.ge/samples/' + sample_id[i] +'/sample.zip'
            #save_file = './sample/' + sha256
            #download_from_url(download_url,save_file)
        
        #input()
        
        time.sleep(10)
        
        print('--------------------------------------------------------------------------------------------')
        
        i = i + 1

        
if __name__ == "__main__":

    if not os.path.exists('sample'):
        os.makedirs('sample')
        
    while 1:
        parse_triage()
        time.sleep(300)
        print(datetime.datetime.now())
            
    
        

        
    