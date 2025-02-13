import requests
from bs4 import BeautifulSoup

import cv2
import numpy as np
import pytesseract

import os
from datetime import datetime

import time


# 標頭
headers = { "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"}

# tesseract 應用程式位址
pytesseract.pytesseract.tesseract_cmd=r"D:\tesseract\tesseract.exe"


session = requests.Session()

#------------------------------------------------------------------------

# 處理驗證碼/返回驗證碼
def captchaImage(captchaImage_np):
        
    img = cv2.imdecode(captchaImage_np, cv2.IMREAD_GRAYSCALE) # 使用 OpenCV 解碼圖片(灰階開啟)
    
    # cv2.imshow("original-gray",img) # 預覽圖片
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)) # 建立操作元素
    img2 = cv2.erode(img, kernel)  # 侵蝕-消除噪點
    # cv2.imshow("erode",img2)
    
    
    img2 = cv2.dilate(img2, kernel)    # 再膨脹，白色小點消失
    # cv2.imshow('dilate', captchaImage2)
    
    cv2.imwrite('captchaImage2.png', img2) # 存圖
    
    # cv2.waitKey(0)                  
    # cv2.destroyAllWindows()
    
    ans = str.strip(pytesseract.image_to_string("captchaImage2.png",config="--psm 6")).replace(" ", "")
    print(ans)
    
    return ans


def stock(stockLabel):
    while True:
        
        # 1. 請求頁面
        url = "https://bsr.twse.com.tw/bshtm/bsMenu.aspx"
        r = session.get(url, headers=headers)
        
        # 2. 解析頁面
        stock_page = BeautifulSoup(r.content, "html.parser")
        
        # 3. 處理驗證碼圖片連結
        time.sleep(1)
        captchaImageSrc = r"https://bsr.twse.com.tw/bshtm/" + stock_page.select("div#Panel_bshtm img")[0].get("src")
        imgData = requests.get(captchaImageSrc, headers=headers)
    
        # 4. 處理驗證碼圖片
        captchaImage_np = np.frombuffer(imgData.content, np.uint8) # 使用 frombuffer 創建 NumPy 陣列
        
        # 5. 辨識驗證碼
        ans = captchaImage(captchaImage_np)
        
        # 6. 送出請求
        # 處理 payload
        __VIEWSTATE = stock_page.find("input", id="__VIEWSTATE").get("value")
        __VIEWSTATEGENERATOR = stock_page.find("input", id="__VIEWSTATEGENERATOR").get("value")
        __EVENTVALIDATION = stock_page.find("input", id="__EVENTVALIDATION").get("value")
    
        payload = {
                    "__EVENTTARGET":"", 
                    "__EVENTARGUMENT":"", 
                    "__LASTFOCUS":"", 
                    "__VIEWSTATE": __VIEWSTATE,
                    "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
                    "__EVENTVALIDATION": __EVENTVALIDATION,
                    "RadioButton_Normal": "RadioButton_Normal",
                    "TextBox_Stkno": stockLabel,
                    "CaptchaControl1": ans,
                    "btnOK": "查詢"
                    }
    
        # 7. POST請求後的頁面抓取
        response = session.post(url, headers=headers, data=payload) 
        result_page = BeautifulSoup(response.content,"html.parser")

        # 8. 找出csv下載連結
        csv_url = result_page.find("a", id="HyperLink_DownloadCSV")
        
        # 9. 如果有連結，下載資料，否則重新驗證
        if csv_url:
            
            csv_url = "https://bsr.twse.com.tw/bshtm/" + csv_url.get("href")
            
            print("驗證成功-開始下載csv")
            csv_data = session.get(csv_url, headers=headers) 
            
            current_time = datetime.today().strftime("%Y%m%d")
            f_name = f"{stockLabel}_{current_time}.csv"
            folder_path = r"./Stockdata"
            path = os.path.join(folder_path, f_name)
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            with open(path, "wb") as file:
                file.write(csv_data.content)
                print("下載完成")
            return
        else:
            print("重新驗證")


stockLabel = input("請輸入股票代號: ")

stock(stockLabel)



