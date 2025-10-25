import json
from DrissionPage import ChromiumPage


page = ChromiumPage()
page.get('https://passport.jd.com/new/login.aspx')

input('请在浏览器中手动登录京东，登录完成后按回车继续...')
cookies_list = page.cookies(all_domains=True, all_info=True)
with open('jd_cookies.json', 'w', encoding='utf-8') as f:
        json.dump(cookies_list, f, ensure_ascii=False, indent=2)
print('Cookie已保存！')

page.quit()