import requests
import time
import random
from client import get_user_profiles, get_page_html
from urllib.parse import urljoin
import json
import os
from utils import download_pic, download_video, extract_note_dict, get_blogs
from loguru import logger

# 若无notes文件夹，则创建
os.makedirs("./notes/texts", exist_ok=True)
os.makedirs("./notes/videos", exist_ok=True)

# 重新计算已存在的笔记数量（更准确的计算方式）
def count_existing_notes():
    text_count = len([name for name in os.listdir("./notes/texts") if os.path.isdir(os.path.join("./notes/texts", name))])
    video_count = len([name for name in os.listdir("./notes/videos") if os.path.isdir(os.path.join("./notes/videos", name))])
    total_count = text_count + video_count
    return total_count, video_count

# 获取下一个笔记编号
def get_next_note_number():
    all_dirs = []
    
    # 收集所有笔记目录
    for folder in ["./notes/texts", "./notes/videos"]:
        for name in os.listdir(folder):
            if os.path.isdir(os.path.join(folder, name)) and name.startswith("笔记"):
                try:
                    # 提取编号
                    num = int(name.replace("笔记", ""))
                    all_dirs.append(num)
                except ValueError:
                    continue
    
    # 返回最大编号+1，如果没有则从1开始
    return max(all_dirs) + 1 if all_dirs else 1

# 初始计数
total_count, video_count = count_existing_notes()
next_note_num = get_next_note_number()

logger.info(f"当前已有笔记总数: {total_count}, 视频笔记数: {video_count}")
logger.info(f"下一个笔记编号: {next_note_num}")

# 添加请求计数器，用于控制频率
request_count = 0
max_requests_per_session = 50  # 每轮最多请求50次

while total_count < 5000 or video_count < 50:
    print(f"目前总量：{total_count}, 视频总量：{video_count}, 下一个编号：{next_note_num}")

    # 每处理一定数量后休息更短时间（优化后）
    if request_count > 0 and request_count % max_requests_per_session == 0:
        rest_time = random.randint(120, 300)  # 2-5分钟（原来是5-10分钟）
        logger.info(f"已处理{request_count}个请求，休息{rest_time}秒...")
        time.sleep(rest_time)

    try:
        # 获取explore页面的HTML
        html = get_page_html('https://www.xiaohongshu.com/explore')
        blogs = get_blogs(html)
        request_count += 1

        # 对主页的每一篇帖子
        for blog in blogs:
            # 随机延时，模拟人类浏览（稍微缩短）
            time.sleep(random.uniform(1, 3))  # 原来是3-8秒
            
            blog_url = urljoin("https://xiaohongshu.com", blog)
            html = get_page_html(blog_url)
            request_count += 1
            
            notes_block = extract_note_dict(html)
            
            if not notes_block:
                continue
                
            try:
                firstNoteId = notes_block["firstNoteId"]
                # 标题
                title = notes_block["noteDetailMap"][firstNoteId]["note"]["title"]

                # 正文
                text = notes_block["noteDetailMap"][firstNoteId]["note"]["desc"]
            except Exception as e:
                logger.warning(f"解析笔记信息失败: {e}")
                continue

            # 图片链接
            try:
                image_urls = [image["infoList"][0]["url"] for image in notes_block["noteDetailMap"][firstNoteId]["note"]["imageList"]]
            except:
                image_urls = []

            # 视频链接(可能无)
            if "video" in notes_block["noteDetailMap"][firstNoteId]["note"].keys() and video_count < 50:
                filedir = f"./notes/videos/笔记{next_note_num}"
                os.makedirs(filedir, exist_ok=True)
                try:
                    video_url = notes_block["noteDetailMap"][firstNoteId]["note"]["video"]["media"]["stream"]["h264"][0]["masterUrl"]
                    download_video(video_url, filedir+"/video.mp4")
                    video_count += 1
                    logger.success(f"下载视频笔记{next_note_num}成功")
                except Exception as e:
                    logger.error(f"下载视频失败: {e}")
                    continue
            else:
                filedir = f"./notes/texts/笔记{next_note_num}"
                os.makedirs(filedir, exist_ok=True)
                for idx, image_url in enumerate(image_urls):
                    try:
                        download_pic(image_url, filedir+f"/image{idx}.webp")
                    except Exception as e:
                        logger.warning(f"下载图片{idx}失败: {e}")
                logger.success(f"下载文本笔记{next_note_num}成功")

            # 保存笔记信息
            info = {"title": title, "text": text}
            with open(f'{filedir}/info.json', 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=4)
            
            total_count += 1
            next_note_num += 1
            
            # 每处理一个笔记后随机延时（稍微缩短）
            time.sleep(random.uniform(1, 4))  # 原来是5-12秒
            
            # 达到单轮限制后跳出内层循环
            if request_count >= max_requests_per_session:
                break
                
    except Exception as e:
        logger.error(f"处理过程中出错: {e}")
        # 出错时等待更长时间
        time.sleep(random.uniform(30, 60))
        continue
        time.sleep(2)



