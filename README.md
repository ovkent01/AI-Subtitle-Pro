# AI Subtitle Pro 极速双语字幕生成器

这是一个为了给自己省时间而开发的极简 Windows 桌面端工具。拖拽视频，一键生成带有精准时间轴的 `.srt` 双语字幕。

## ✨ 核心特点
* **极致极简**：没有复杂的配置，拖拽即用，无任何多余弹窗。
* **双核驱动**：底层调用 Whisper 提取高精度原声，接入 Google 翻译 API 实现双语对齐。
* **显卡加速**：自动调用 NVIDIA 显卡 (CUDA) 狂飙运算，拒绝 CPU 卡顿。

## 🚀 如何使用
1.  在 [Releases] 页面下载最新版的 `.exe` 压缩包。
2.  解压后双击运行 `AI_Subtitle_Pro.exe`。
3.  将你的视频（支持 mp4, mov, wav, mp3）拖拽到软件虚线框内。
4.  点击“开始处理”，等待几秒钟，同名 `.srt` 字幕文件会自动生成在视频所在的同一个文件夹里。

## 🛠️ 本地开发指南
如果你想修改源代码：
1. 确保安装了 `Python` 和现代包管理器 `uv`。
2. 安装核心依赖：
   ```bash
   uv pip install faster-whisper deep-translator customtkinter tkinterdnd2
   ```
3. 运行代码：
   ```bash
   python app_cloud.py
   ```

