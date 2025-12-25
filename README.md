# 小红书双爬虫系统

这是一个基于Chrome和Firefox双浏览器的小红书笔记爬虫系统，能够高效地爬取小红书的图片和视频内容。

## 🚀 项目特点

- **双爬虫并行**：Chrome和Firefox爬虫同时运行，提高爬取效率
- **智能分工**：Chrome爬虫负责图片+视频，Firefox爬虫专注图片
- **防反爬机制**：模拟人类行为、随机延时、验证码邮件提醒
- **数据持久化**：自动保存笔记文本、图片和视频

## 📁 项目结构

```
xhs_spider/
├── RedNoteSpider-chrome/          # Chrome爬虫
│   ├── main.py                     # 主程序
│   ├── client.py                   # 浏览器客户端
│   ├── utils.py                    # 工具函数
│   └── notes/                      # 爬取数据存储
│       ├── texts/                  # 图片笔记
│       └── videos/                 # 视频笔记
├── RedNoteSpider-firefox/          # Firefox爬虫
│   ├── main.py                     # 主程序
│   ├── client.py                   # 浏览器客户端
│   ├── utils.py                    # 工具函数
│   ├── firefox_profile/            # Firefox配置文件
│   ├── log/                        # 日志文件
│   └── notes/                      # 爬取数据存储
├── run_spiders.py                  # 统一启动脚本
├── requirements.txt                # 依赖包列表
└── README.md                       # 说明文档
```

## 🛠️ 环境要求

### 软件依赖
- Python 3.8+
- Chrome浏览器
- Firefox浏览器
- ChromeDriver
- GeckoDriver (Firefox)

### Python包依赖
所有依赖包已列在 `requirements.txt` 中：
- loguru
- requests
- DrissionPage
- selenium

## 📦 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/Voyager2004/RedNotesSpider.git
   cd xhs_spider
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **下载浏览器驱动**
   - ChromeDriver: 下载并放置在系统PATH或项目目录
   - GeckoDriver: 下载并放置在Firefox爬虫目录

## 🚀 使用方法

### 方法一：双爬虫并行运行（推荐）
```bash
python run_spiders.py
```

### 方法二：单独运行爬虫
```bash
# 只运行Chrome爬虫
cd RedNoteSpider-chrome
python main.py

# 只运行Firefox爬虫
cd RedNoteSpider-firefox
python main.py
```

## ⚙️ 爬虫配置

### Chrome爬虫特点
- **编号规则**：从1开始递增（笔记1, 笔记2, ...）
- **爬取内容**：图片笔记 + 视频笔记
- **目标数量**：总计5000个笔记，其中50个视频
- **存储位置**：`RedNoteSpider-chrome/notes/`

### Firefox爬虫特点
- **编号规则**：从5000开始递减（笔记5000, 笔记4999, ...）
- **爬取内容**：仅图片笔记（跳过视频）
- **目标数量**：5000个图片笔记
- **存储位置**：`RedNoteSpider-firefox/notes/`
- **日志记录**：详细日志保存在 `log/Firefox_crawler.log`

## 📊 数据格式

每个笔记文件夹包含：
- `info.json`：笔记元信息（标题、正文、爬虫标识等）
- `image0.webp, image1.webp, ...`：图片文件
- `video.mp4`：视频文件（仅Chrome爬虫）

示例 `info.json`：
```json
{
    "title": "笔记标题",
    "text": "笔记正文内容",
    "crawler": "Chrome",
    "note_number": 1,
    "image_count": 3
}
```

## 🔧 高级功能

### 验证码处理
- 自动检测验证码
- 邮件提醒功能
- 手动处理后继续运行

### 反爬虫机制
- 随机延时（1-8秒）
- 模拟人类滚动行为
- 随机鼠标移动
- 用户代理轮换
- 会话持久化

### 错误恢复
- 自动重试机制
- 断点续爬功能
- 详细日志记录

## 📝 注意事项

1. **首次运行**：需要手动扫码登录小红书账号
2. **网络环境**：建议在稳定的网络环境下运行
3. **运行时间**：爬取大量数据需要较长时间，建议夜间运行
4. **存储空间**：确保有足够的磁盘空间存储图片和视频
5. **合规使用**：请遵守小红书的使用条款，仅用于学习研究

## 🐛 常见问题

### Q: 依赖包安装失败
A: 尝试升级pip：`pip install --upgrade pip`，然后重新安装

### Q: 浏览器启动失败
A: 检查ChromeDriver和GeckoDriver是否正确安装并在PATH中

### Q: 验证码频繁出现
A: 适当增加延时时间，或更换IP地址

### Q: 爬取速度慢
A: 可以调整延时参数，但要注意反爬虫风险

## 📞 技术支持

如有问题，请查看日志文件：
- Chrome爬虫：控制台输出
- Firefox爬虫：`RedNoteSpider-firefox/log/Firefox_crawler.log`

---


**免责声明**：本项目仅供学习和研究使用，请遵守相关法律法规和网站使用条款。
