import time
import json
import random
from DrissionPage import ChromiumPage
from DrissionPage import ChromiumOptions, SessionOptions, Chromium

co = ChromiumOptions(ini_path=r'./dp_configs.ini')
co.headless(False)
browser = Chromium(addr_or_opts=co)
page = browser.new_tab(url='https://item.jd.com/100278222322.html')
with open('jd_cookies.json', 'r', encoding='utf-8') as f:
    cookies_list = json.load(f)

page.set.cookies(cookies_list)
page.ele('css:.activity-banner').click()
time.sleep(2)
listen = page.listen.start('https://api.m.jd.com/api?fid=bindingQualification')
while True:
    try:
        page.ele('css:.get-module-normal-content-btn.get-module-btn ').click()
        page.ele('css:.b1.ok').click()

        for packet in page.listen.steps(count=1):
            res = packet.response
            if isinstance(res.body, dict):
                success = res.body.get('success')
                message = res.body.get('message')
                print(f"success: {success}, message: {message}")
                
                if success is True:
                    print("操作成功，退出循环")
                    exit() 
                elif success is False:
                    print(f"{message}")
    except Exception as e:
        print(f"操作出错：{e}，停止循环")
        break
