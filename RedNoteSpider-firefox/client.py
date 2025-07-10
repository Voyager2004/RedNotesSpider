import time
import random
import re
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from loguru import logger

# 邮件配置 - 请根据需要填写您的邮箱信息
EMAIL_CONFIG = {
    'smtp_server': '',  # SMTP服务器地址，如：smtp.qq.com
    'smtp_port': 587,
    'sender_email': '',  # 发送方邮箱
    'sender_password': '',  # 邮箱授权码
    'receiver_email': ''  # 接收方邮箱
}

# 全局浏览器实例
_browser_instance = None

def send_captcha_alert():
    """发送验证码提醒邮件"""
    # 检查邮件配置是否完整
    if not all(EMAIL_CONFIG.values()):
        logger.warning("Firefox爬虫邮件配置不完整，跳过邮件发送")
        return
        
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['receiver_email']
        msg['Subject'] = 'Firefox爬虫 - 验证码提醒'
        
        body = f"""
        Firefox小红书爬虫遇到验证码，需要手动处理！
        
        时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
        浏览器: Firefox
        状态: 等待手动验证
        
        请及时处理验证码以继续爬取。
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['receiver_email'], text)
        server.quit()
        
        logger.success("Firefox爬虫验证码提醒邮件发送成功")
    except Exception as e:
        logger.error(f"Firefox爬虫发送邮件失败: {e}")

def get_browser():
    """获取或创建Firefox浏览器实例"""
    global _browser_instance
    if _browser_instance is None:
        _browser_instance = _init_firefox_browser()
        _browser_instance.get('https://www.xiaohongshu.com/explore')
        input("请在Firefox浏览器中手动扫码登录，完成后按回车继续…")
        logger.success("Firefox爬虫登录完成")
    return _browser_instance

def get_page_html(url):
    """获取指定URL的HTML内容"""
    browser = get_browser()
    
    time.sleep(random.uniform(2, 5))
    
    browser.get(url)
    
    _simulate_human_behavior(browser)
    
    if _check_captcha(browser):
        input("Firefox爬虫检测到验证码，请手动完成验证后按回车继续...")
    
    return browser.page_source

def _simulate_human_behavior(browser):
    """模拟人类浏览行为"""
    try:
        # 随机滚动
        scroll_times = random.randint(1, 3)
        for _ in range(scroll_times):
            scroll_distance = random.randint(200, 800)
            browser.execute_script(f"window.scrollBy(0, {scroll_distance});")
            time.sleep(random.uniform(0.5, 1.5))
        
        # 随机鼠标移动
        if random.random() < 0.3:
            actions = ActionChains(browser)
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            actions.move_by_offset(x, y).perform()
            time.sleep(random.uniform(0.2, 0.8))
    except Exception as e:
        logger.warning(f"Firefox爬虫模拟人类行为时出错: {e}")

def _check_captcha(browser):
    """检查是否出现验证码"""
    try:
        # 更精确的验证码检测选择器
        captcha_selectors = [
            'div[class*="captcha-container"]',
            'div[class*="verification-code"]',
            'div[class*="slider-verify"]',
            'img[src*="captcha"]',
            'div[id*="captcha"]',
            'div[class="verify-slider"]',
            'div[class="captcha-box"]'
        ]
        
        # 检测验证码元素，并确保元素可见
        for selector in captcha_selectors:
            try:
                elements = browser.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.size['height'] > 0 and element.size['width'] > 0:
                        logger.warning(f"Firefox爬虫检测到验证码元素: {selector}")
                        send_captcha_alert()
                        return True
            except:
                continue
        
        # 检测页面源码中的验证码关键词（更严格）
        page_source = browser.page_source.lower()
        captcha_keywords = [
            'please complete the verification',
            '请完成验证',
            'captcha verification',
            'slider verification',
            '滑动验证',
            'security verification'
        ]
        
        for keyword in captcha_keywords:
            if keyword in page_source:
                logger.warning(f"Firefox爬虫页面内容包含验证关键词: {keyword}")
                send_captcha_alert()
                return True
        
        # 检测特定的验证码页面URL
        current_url = browser.current_url.lower()
        if any(pattern in current_url for pattern in ['captcha', 'verify', 'challenge']) and 'xiaohongshu.com' in current_url:
            logger.warning(f"Firefox爬虫URL疑似验证页面: {current_url}")
            send_captcha_alert()
            return True
            
    except Exception as e:
        logger.warning(f"Firefox爬虫验证码检测时出错: {e}")
    
    return False

def _init_firefox_browser():
    """初始化Firefox浏览器配置"""
    options = Options()
    
    # 设置Firefox配置文件路径
    profile_path = os.path.abspath("firefox_profile")
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
    
    # 创建Firefox配置文件
    firefox_profile = webdriver.FirefoxProfile(profile_path)
    
    # 设置用户代理
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"
    ]
    firefox_profile.set_preference("general.useragent.override", random.choice(user_agents))
    
    # 禁用通知
    firefox_profile.set_preference("dom.webnotifications.enabled", False)
    
    # 设置窗口大小
    width = random.randint(1200, 1600)
    height = random.randint(800, 1000)
    options.add_argument(f"--width={width}")
    options.add_argument(f"--height={height}")
    
    # 将配置文件设置到options中
    options.profile = firefox_profile
    
    # 检测geckodriver路径
    geckodriver_path = None
    possible_paths = [
        "./geckodriver.exe",
        "geckodriver.exe",
        "C:\\geckodriver\\geckodriver.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            geckodriver_path = path
            break
    
    try:
        if geckodriver_path:
            service = Service(geckodriver_path)
            browser = webdriver.Firefox(service=service, options=options)
        else:
            # 尝试使用系统PATH中的geckodriver
            browser = webdriver.Firefox(options=options)
        
        logger.info("Firefox浏览器初始化成功")
        return browser
        
    except Exception as e:
        logger.error(f"Firefox浏览器初始化失败: {e}")
        logger.error("请确保已安装Firefox浏览器和geckodriver")
        raise

def get_user_profiles():
    """获取用户配置文件"""
    browser = get_browser()
    
    if 'explore' not in browser.current_url:
        browser.get('https://www.xiaohongshu.com/explore')
    
    _simulate_human_behavior(browser)
    
    if _check_captcha(browser):
        input("Firefox爬虫检测到验证码，请手动完成验证后按回车继续...")
    
    html = browser.page_source
    author_divs = re.findall(r'<div class="author-wrapper"[^>]*>(.*?)</div>', html, re.S)

    hrefs = []
    for div in author_divs:
        match = re.search(r'<a[^>]+href="([^"]+)"', div)
        if match:
            hrefs.append(match.group(1))

    return hrefs