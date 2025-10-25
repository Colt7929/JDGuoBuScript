import time
import json
import sys
import datetime
import socket
import struct
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
            print("等待北京时间9:00...")
            self.wait_until_target_time(9, 0, 0)
            print("开始执行抢购...")
            self.page.ele('css:.b1.ok').click()
            return True
        except:
            return False
    
    def perform_click_sequence_with_time(self,target_hour, target_minute, target_second):
        try:
            self.page.ele('css:.get-module-normal-content-btn.get-module-btn').click()
            print(f"等待北京时间{target_hour:02d}:{target_minute:02d}:{target_second:02d}...")
            self.wait_until_target_time(target_hour, target_minute, target_second)
            print("开始执行抢购...")
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
    
    def get_ntp_time(self):
        """获取NTP服务器时间（更精确的网络时间）"""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.settimeout(5)
            data = b'\x1b' + 47 * b'\0'
            client.sendto(data, ('time.windows.com', 123))
            data, _ = client.recvfrom(1024)
            client.close()
            
            if data:
                t = struct.unpack('!12I', data)[10]
                t -= 2208988800  # 1900-1970
                return datetime.datetime.fromtimestamp(t)
        except:
            pass
        return datetime.datetime.now()
    
    def sync_system_time(self):
        """同步系统时间与网络时间"""
        ntp_time = self.get_ntp_time()
        local_time = datetime.datetime.now()
        time_diff = (ntp_time - local_time).total_seconds()
        
        if abs(time_diff) > 1:
            print(f"时间校准: 本地时间 {local_time.strftime('%H:%M:%S')}, 网络时间 {ntp_time.strftime('%H:%M:%S')}")
            return ntp_time
        return local_time
    
    def wait_until_target_time(self, target_hour, target_minute, target_second):
        """精确等待直到北京时间指定时间"""
        if datetime.datetime.now().hour < target_hour:
            print("时间校准中...")
            self.sync_system_time()
        
        while True:
            now = self.sync_system_time()
            target_time = now.replace(hour=target_hour, minute=target_minute, second=target_second, microsecond=0)
            
            if now >= target_time:
                break
                
            time_diff = (target_time - now).total_seconds()
            

            if time_diff > 300:
                time.sleep(300)   # 5分钟
            elif time_diff > 60:
                time.sleep(60)    # 1分钟
            elif time_diff > 10:
                time.sleep(1)     # 1秒
            elif time_diff > 1:
                time.sleep(0.1)   # 100毫秒
            else:
                time.sleep(time_diff) 
    
    def run_script(self, product_url, api_url):
        cookies = self.load_cookies()
        self.setup_page(product_url, cookies)
        
        self.page.ele('css:.activity-banner').click()
        time.sleep(0.5)
        
        listener = self.page.listen.start(api_url)
        
        if self.perform_click_sequence():
            for packet in self.page.listen.steps(count=1):
                if self.check_response(packet):
                    return
    
    def run_script_with_time(self, product_url, api_url, target_hour, target_minute, target_second):        
        cookies = self.load_cookies()
        self.setup_page(product_url, cookies)
        
        self.page.ele('css:.activity-banner').click()
        time.sleep(0.5)
        
        listener = self.page.listen.start(api_url)
        
        if self.perform_click_sequence_with_time(target_hour, target_minute, target_second):
            for packet in self.page.listen.steps(count=1):
                if self.check_response(packet):
                    return
    
    def close(self):
        if self.browser:
            self.browser.quit()


def parse_time_input(time_str):
    """解析时间输入格式 HH:MM:SS"""
    try:
        parts = time_str.split(':')
        if len(parts) != 3:
            raise ValueError("时间格式错误")
        
        hour = int(parts[0])
        minute = int(parts[1])
        second = int(parts[2])
        
        if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
            raise ValueError("时间值超出范围")
        
        return hour, minute, second
    except ValueError as e:
        print(f"时间格式错误: {e}")
        print("请使用 HH:MM:SS 格式，例如 09:00:00")
        return None

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
        print("  python jd_cli.py run [HH:MM:SS] # 运行抢购脚本，可指定时间")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'save_cookie':
        save_cookie()
    elif cmd == 'run':
        # 默认时间为09:00:00
        target_hour, target_minute, target_second = 9, 0, 0
        
        # 如果提供了时间参数
        if len(sys.argv) >= 3:
            time_input = sys.argv[2]
            parsed_time = parse_time_input(time_input)
            if parsed_time:
                target_hour, target_minute, target_second = parsed_time
            else:
                return
        
        print(f"目标抢购时间: {target_hour:02d}:{target_minute:02d}:{target_second:02d}")
        
        cli = JDCli()
        try:
            cli.run_script_with_time(
                'https://item.jd.com/100278222322.html',
                'https://api.m.jd.com/api?fid=bindingQualification',
                target_hour, target_minute, target_second
            )
        except Exception as e:
            print(f"错误: {e}")
        finally:
            cli.close()
    else:
        print("未知命令")


if __name__ == "__main__":
    main()
