import requests
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0"  # 可加上请求头防止被拒
}

def download_video(url, filename):
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def download_pic(url, filedir):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filedir, "wb") as f:
            f.write(response.content)

def extract_note_dict(html_text):
    """从html文件中提取对应note: {...} 的内容"""
    pattern = r'"note"\s*:\s*\{'
    match = re.search(pattern, html_text)
    if not match:
        print("❌ 未找到 '\"note\": {'")
        return None

    start = match.end() - 1
    text = html_text[start:]

    # 配对大括号
    count = 0
    end = None
    for i, c in enumerate(text):
        if c == '{':
            count += 1
        elif c == '}':
            count -= 1
            if count == 0:
                end = i + 1
                break

    if end is None:
        print("❌ 大括号不匹配")
        return None

    json_text = text[:end]

    # 清理非法控制字符（如 \x0e）
    json_text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', json_text)

    try:
        note_dict = json.loads(json_text)
        return note_dict
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        print(json_text[max(0, e.pos - 50):e.pos + 50])
        return None


def get_blogs(html):
    """正则表达式匹配 class="cover mask ld" 的 <a> 标签里的 href"""
    pattern = r'<a[^>]*class="cover mask ld"[^>]*href="([^"]+)"'

    matches = re.findall(pattern, html)

    return matches
