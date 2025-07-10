import subprocess
import threading
import time
import os
import sys
from loguru import logger

def run_chrome_spider():
    """运行Chrome爬虫"""
    try:
        logger.info("启动Chrome爬虫...")
        os.chdir("RedNoteSpider-chrome")
        subprocess.run([sys.executable, "main.py"], check=True)
    except Exception as e:
        logger.error(f"Chrome爬虫运行出错: {e}")
    finally:
        os.chdir("..")

def run_firefox_spider():
    """运行Firefox爬虫"""
    try:
        logger.info("启动Firefox爬虫...")
        os.chdir("RedNoteSpider-firefox")
        subprocess.run([sys.executable, "main.py"], check=True)
    except Exception as e:
        logger.error(f"Firefox爬虫运行出错: {e}")
    finally:
        os.chdir("..")

def main():
    """主函数：同时启动两个爬虫"""
    logger.info("=== 小红书双爬虫启动器 ===")
    logger.info("Chrome爬虫：爬取图片和视频笔记，编号从1开始递增")
    logger.info("Firefox爬虫：只爬取图片笔记，编号从5000开始递减")
    
    # 创建线程
    chrome_thread = threading.Thread(target=run_chrome_spider, name="Chrome-Spider")
    firefox_thread = threading.Thread(target=run_firefox_spider, name="Firefox-Spider")
    
    # 启动线程
    logger.info("正在启动Chrome爬虫线程...")
    chrome_thread.start()
    
    # 稍微延迟启动Firefox爬虫，避免同时请求
    time.sleep(10)
    logger.info("正在启动Firefox爬虫线程...")
    firefox_thread.start()
    
    # 等待两个线程完成
    logger.info("两个爬虫已启动，等待完成...")
    chrome_thread.join()
    firefox_thread.join()
    
    logger.info("所有爬虫已完成！")

if __name__ == "__main__":
    main()