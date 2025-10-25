import time
import json
import sys
from DrissionPage import ChromiumPage, ChromiumOptions, Chromium


class JDCli:
    def __init__(self, config_path='./dp_configs.ini'):
        self.config_path = config_path
        self.browser = None
        self.page = None
    
    def init_browser(self, headless=False):
        co = ChromiumOptions(ini_path=self.config_path)
        co.headless(headless)
        self.browser = Chromium(addr_or_opts=co)
        return self.browser
    
    def load_cookies(self, cookie_path='jd_cookies.json'):
        with open(cookie_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def setup_page(self, url, cookies):
        if not self.browser:
            self.init_browser()
        self.page = self.browser.new_tab(url=url)
        self.page.set.cookies(cookies)
        return self.page
    
    def perform_click_sequence(self):
        try:
            self.page.ele('css:.get-module-normal-content-btn.get-module-btn').click()
            self.page.ele('css:.b1.ok').click()
            return True
        except:
            return False
    
    def check_response(self, packet):
        res = packet.response
        if isinstance(res.body, dict):
            success = res.body.get('success')
            message = res.body.get('message')
            print(f"success: {success}, message: {message}")
            return success is True
        return False
    
    def run_script(self, product_url, api_url):
        cookies = self.load_cookies()
        self.setup_page(product_url, cookies)
        
        self.page.ele('css:.activity-banner').click()
        time.sleep(0.5)
        
        listener = self.page.listen.start(api_url)
        
        while True:
            if self.perform_click_sequence():
                for packet in self.page.listen.steps(count=1):
                    if self.check_response(packet):
                        return
            time.sleep(0.05)
    
    def close(self):
        if self.browser:
            self.browser.quit()


def save_cookie():
    page = ChromiumPage()
    page.get('https://passport.jd.com/new/login.aspx')
    input('请在浏览器中手动登录京东，登录完成后按回车继续...')
    cookies_list = page.cookies(all_domains=True, all_info=True)
    with open('jd_cookies.json', 'w', encoding='utf-8') as f:
        json.dump(cookies_list, f, ensure_ascii=False, indent=2)
    print('Cookie已保存！')
    page.quit()


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python jd_cli.py save_cookie    # 保存Cookie")
        print("  python jd_cli.py run            # 运行抢购脚本")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'save_cookie':
        save_cookie()
    elif cmd == 'run':
        cli = JDCli()
        try:
            cli.run_script(
                'https://item.jd.com/100278222322.html',
                'https://api.m.jd.com/api?fid=bindingQualification'
            )
        except Exception as e:
            print(f"错误: {e}")
        finally:
            cli.close()
    else:
        print("未知命令")


if __name__ == "__main__":
    main()
