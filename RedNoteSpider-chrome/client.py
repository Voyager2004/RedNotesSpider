import requests
import re
import time
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from DrissionPage import ChromiumPage, ChromiumOptions
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
        logger.warning("邮件配置不完整，跳过邮件发送")
        return
        
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['receiver_email']
        msg['Subject'] = '小红书爬虫 - Chrome验证码提醒'
        
        body = f"""
        小红书Chrome爬虫遇到验证码，需要手动处理！
        
        时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
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
        
        logger.success("验证码提醒邮件发送成功")
    except Exception as e:
        logger.error(f"发送邮件失败: {e}")

def get_browser():
    """获取或创建浏览器实例"""
    global _browser_instance
    if _browser_instance is None:
        _browser_instance = _init_browser()
        # 打开小红书首页并等待登录
        _browser_instance.get('https://www.xiaohongshu.com/explore')
        input("请在浏览器中手动扫码登录，完成后按回车继续…")
        logger.success("登录完成")
    return _browser_instance

def get_user_profiles():
    # 获取浏览器实例
    page = get_browser()
    
    # 确保在explore页面
    if 'explore' not in page.url:
        page.get('https://www.xiaohongshu.com/explore')
    
    # 模拟人类行为：随机滚动
    _simulate_human_behavior(page)
    
    # 检查是否有验证码
    if _check_captcha(page):
        input("检测到验证码，请手动完成验证后按回车继续...")
    
    # 获取页面HTML内容
    html = page.html

    # 先匹配所有 <div class=\"author-wrapper\"> ... </div> 块
    author_divs = re.findall(r'<div class=\"author-wrapper\"[^>]*>(.*?)</div>', html, re.S)

    hrefs = []
    for div in author_divs:
        # 在每个 author-wrapper 里匹配 <a href=\"...\">
        match = re.search(r'<a[^>]+href=\"([^\"]+)\"', div)
        if match:
            hrefs.append(match.group(1))

    return hrefs

def get_page_html(url):
    """获取指定URL的HTML内容"""
    page = get_browser()
    
    # 随机延时
    time.sleep(random.uniform(2, 5))
    
    page.get(url)
    
    # 模拟人类行为
    _simulate_human_behavior(page)
    
    # 检查验证码
    if _check_captcha(page):
        input("检测到验证码，请手动完成验证后按回车继续...")
    
    return page.html

def _simulate_human_behavior(page):
    """模拟人类浏览行为"""
    try:
        # 随机滚动
        scroll_times = random.randint(1, 3)
        for _ in range(scroll_times):
            # 随机滚动距离 - 使用正确的滚动方法
            scroll_distance = random.randint(200, 800)
            page.scroll.down(scroll_distance)  # 修改这里：使用 down() 方法
            time.sleep(random.uniform(0.5, 1.5))
        
        # 随机移动鼠标
        if random.random() < 0.3:  # 30%概率移动鼠标
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            page.actions.move_to((x, y))
            time.sleep(random.uniform(0.2, 0.8))
    except Exception as e:
        logger.warning(f"模拟人类行为时出错: {e}")

def _check_captcha(page):
    """检查是否出现验证码"""
    try:
        # 检查常见的验证码元素
        captcha_selectors = [
            'img[class*=captcha]',
            'div[class*=captcha]',
            'div[class*=verify]',
            'div[class*=slider]',
            '.captcha',
            '.verify',
            '[data-testid*=captcha]'
        ]
        
        for selector in captcha_selectors:
            if page.ele(selector, timeout=1):
                logger.warning("检测到验证码")
                send_captcha_alert()  # 发送邮件提醒
                return True
        
        # 检查页面标题或URL是否包含验证相关关键词
        if any(keyword in page.title.lower() for keyword in ['verify', 'captcha', '验证']):
            logger.warning("页面标题包含验证关键词")
            send_captcha_alert()  # 发送邮件提醒
            return True
            
        if any(keyword in page.url.lower() for keyword in ['verify', 'captcha', 'challenge']):
            logger.warning("URL包含验证关键词")
            send_captcha_alert()  # 发送邮件提醒
            return True
            
    except Exception as e:
        logger.warning(f"验证码检测时出错: {e}")
    
    return False

def _init_browser():
    """初始化浏览器配置"""
    PROFILE_DIR = Path("chrome_profile")
    
    opts = ChromiumOptions()
    opts.headless(False)
    opts.set_paths(
        user_data_path=str(PROFILE_DIR)  # 持久化浏览器数据
    )
    
    # 设置更真实的浏览器特征
    opts.set_argument('--disable-blink-features=AutomationControlled')
    opts.set_argument('--disable-features=IsolateOrigins,site-per-process')
    
    # 随机化窗口大小
    width = random.randint(1200, 1600)
    height = random.randint(800, 1000)
    opts.set_argument(f'--window-size={width},{height}')
    
    # 设置用户代理
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ]
    opts.set_argument(f"--user-agent={random.choice(user_agents)}")
    
    # 禁用WebDriver特征
    opts.set_argument("--disable-web-security")
    opts.set_argument("--allow-running-insecure-content")
    opts.set_argument("--disable-dev-shm-usage")
    opts.set_argument("--no-sandbox")
    
    # 禁用自动化检测
    opts.set_argument("--disable-blink-features=AutomationControlled")
    opts.set_argument("--exclude-switches=enable-automation")
    opts.set_argument("--disable-extensions-file-access-check")
    
    return ChromiumPage(opts)
