from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import pyperclip
import os

url = 'https://learn.dict.naver.com/wordbook/jakodict/#/my/cards?wbId=9787c6d9d1be48a7abd02c6bffc1aa3b&qt=0&st=0&name=단어&tab=list'
user_id = (input("네이버 아이디 입력 : "))
user_pw = (input("네이버 비밀번호 입력 : "))
num = int(input("총 페이지 수 입력 : "))   #페이지 수 설정

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

driver.get(url)
driver.implicitly_wait(3)   #3초안에 웹페이지를 load 하면 바로 넘어가거나, 3초를 기다림

id = driver.find_element(By.ID, 'id')
id.click()
pyperclip.copy(user_id) #user_id 변수 복사
id.send_keys(Keys.CONTROL, 'v') #붙여넣기

pw = driver.find_element(By.ID, 'pw')
pw.click()
pyperclip.copy(user_pw)
pw.send_keys(Keys.CONTROL, 'v')

driver.find_element(By.XPATH, '//*[@id="log.login"]').click()   #로그인 버튼 클릭
time.sleep(1)

try:    #처음 등록하는 기기일 시 "등록 안함" 클릭
    driver.find_element(By.ID, 'new.dontsave').click()
    time.sleep(1)
except:
    pass

file = open(os.path.join(os.path.expanduser('~'),'Desktop\\')+'word_anki.txt', 'w', encoding='UTF-8')  #저장할 파일 열기 (바탕화면)

page = 1

while True:
    html = driver.page_source   #driver가 위치한 웹페이지의 소스 코드
    soup = BeautifulSoup(html,'html.parser')    #html parser 실행
    divs = soup.findAll('div', 'inner_card')    #단어 목록을 div단위로 추출 (한 페이지에 20개)

    for div in divs:
        word = div.find('a').get_text().replace('\n','').replace('	','').replace('-','')   #단어를 찾아 텍스트 추출, 엔터 제거, 공백 제거, 하이픈 제거 (한자와 히라가나를 모두 추출)
        if '[' in word: #괄호가 있다면 실행(한자가 있다면 실행)
            file.write(word.split('[')[0]+'\t') #히라가나 추출 #('['를 경계로 히라가나와 한자 분리)
            file.write(word.split('[')[1].replace(']','')+'\t')  #한자 추출, '[' 제거
        else:   #괄호가 없다면 실행
            file.write(word+'\t'+word+'\t')
        
        meanings = div.findAll('div', 'mean_desc') #단어의 모든 뜻 찾기, div태그이면서 mean_desc 클래스
        for meaning in meanings:
            if meaning.em is not None: #값이 none이 아니라면 실행
                meaning.em.decompose() #em 태그 제거  
            file.write(meaning.get_text().replace('\n',"").replace('	',"")+'<br>') #뜻에서 텍스트 추출, 엔터 제거, 공백(탭?)제거 + 줄바꿈   
        
        file.write('\t')
        
        exams = div.findAll('li','item_example')    #단어의 모든 예문 찾기
        for exam in exams:
            origin = exam.find('p','origin')    #예문 추출
            file.write(origin.get_text().replace('\n',"").replace('	',"")+'<br>') 
            translate = exam.find('p','translate')  #예문 해석 추출
            file.write(translate.get_text().replace('\n',"").replace('	',"")+'<br><br>')
        
        try:    #참고어가 있다면 실행
            refer = div.find('span', 'title_origin')    #참고어 찾기
            file.write('\t')
            file.write(refer.get_text())
        except:
            pass
                
        file.write('\n')
        
    if page == num: #마지막 페이지에 도달하면 break
        break
    driver.find_element(By.CLASS_NAME, 'btn.btn_next._next_page_btn').click()   #다음 페이지 버튼 클릭
    page+=1 #페이지 카운트
    time.sleep(1)

file.close()
print("끝")
time.sleep(60)