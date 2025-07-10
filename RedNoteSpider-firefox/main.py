import time
import random
from client import get_page_html
from urllib.parse import urljoin
import json
import os
from utils import download_pic, extract_note_dict, get_blogs
from loguru import logger

# 配置日志
logger.add("log/Firefox_crawler.log", rotation="1 day")

# 创建目录
os.makedirs("./notes/texts", exist_ok=True)
os.makedirs("./log", exist_ok=True)

def count_existing_notes():
    """计算已存在的笔记数量"""
    text_count = len([name for name in os.listdir("./notes/texts") if os.path.isdir(os.path.join("./notes/texts", name))])
    return text_count

def get_next_note_number():
    """获取下一个笔记编号（从5000开始倒数）"""
    all_dirs = []
    for name in os.listdir("./notes/texts"):
        if os.path.isdir(os.path.join("./notes/texts", name)) and name.startswith("笔记"):
            try:
                num = int(name.replace("笔记", ""))
                all_dirs.append(num)
            except ValueError:
                continue
    
    # 如果没有笔记，从5000开始
    if not all_dirs:
        return 5000
    
    # 找到最小的编号，然后减1（倒数）
    min_num = min(all_dirs)
    return min_num - 1 if min_num > 1 else 1

# 初始计数
total_count = count_existing_notes()
next_note_num = get_next_note_number()

logger.info(f"Firefox爬虫启动 - 当前已有笔记总数: {total_count}, 下一个编号: {next_note_num}")
logger.info("Firefox爬虫配置: 从5000开始倒数，只爬取图片笔记，不爬取视频")

# 请求计数器
request_count = 0
max_requests_per_session = 40  # Firefox爬虫每轮请求数

# 爬取目标：从5000倒数到1
while next_note_num > 0 and total_count < 5000:
    print(f"Firefox爬虫 - 目前总量：{total_count}, 下一个编号：{next_note_num}")

    # 休息策略
    if request_count > 0 and request_count % max_requests_per_session == 0:
        rest_time = random.randint(60, 100)
        logger.info(f"Firefox爬虫已处理{request_count}个请求，休息{rest_time}秒...")
        time.sleep(rest_time)

    try:
        html = get_page_html('https://www.xiaohongshu.com/explore')
        blogs = get_blogs(html)
        request_count += 1

        for blog in blogs:
            time.sleep(random.uniform(1, 3))  # Firefox爬虫延时
            
            blog_url = urljoin("https://xiaohongshu.com", blog)
            html = get_page_html(blog_url)
            request_count += 1
            
            notes_block = extract_note_dict(html)
            if not notes_block:
                continue
                
            try:
                firstNoteId = notes_block["firstNoteId"]
                title = notes_block["noteDetailMap"][firstNoteId]["note"]["title"]
                text = notes_block["noteDetailMap"][firstNoteId]["note"]["desc"]
            except Exception as e:
                logger.warning(f"Firefox爬虫解析笔记信息失败: {e}")
                continue

            # 检查是否为视频笔记，如果是则跳过
            if "video" in notes_block["noteDetailMap"][firstNoteId]["note"].keys():
                logger.info(f"跳过视频笔记: {title[:20]}...")
                continue

            # 只处理图片笔记
            try:
                image_urls = [image["infoList"][0]["url"] for image in notes_block["noteDetailMap"][firstNoteId]["note"]["imageList"]]
            except:
                image_urls = []

            if not image_urls:
                logger.info(f"跳过无图片的笔记: {title[:20]}...")
                continue

            # 创建文件夹并下载图片
            filedir = f"./notes/texts/笔记{next_note_num}"
            os.makedirs(filedir, exist_ok=True)
            
            downloaded_images = 0
            for idx, image_url in enumerate(image_urls):
                try:
                    download_pic(image_url, filedir+f"/image{idx}.webp")
                    downloaded_images += 1
                except Exception as e:
                    logger.warning(f"Firefox爬虫下载图片{idx}失败: {e}")
            
            if downloaded_images > 0:
                # 保存笔记信息
                info = {
                    "title": title, 
                    "text": text, 
                    "crawler": "Firefox",
                    "note_number": next_note_num,
                    "image_count": downloaded_images
                }
                with open(f'{filedir}/info.json', 'w', encoding='utf-8') as f:
                    json.dump(info, f, ensure_ascii=False, indent=4)
                
                total_count += 1
                logger.success(f"Firefox爬虫下载图片笔记{next_note_num}成功，共{downloaded_images}张图片")
                
                # 倒数递减
                next_note_num -= 1
            else:
                # 如果没有成功下载任何图片，删除空文件夹
                try:
                    os.rmdir(filedir)
                except:
                    pass
                logger.warning(f"笔记{next_note_num}没有成功下载任何图片，跳过")
            
            time.sleep(random.uniform(1, 4))
            
            if request_count >= max_requests_per_session:
                break
                
    except Exception as e:
        logger.error(f"Firefox爬虫处理过程中出错: {e}")
        time.sleep(random.uniform(30, 60))
        continue

logger.info(f"Firefox爬虫完成！总共爬取了{total_count}个图片笔记")