import os
import sys
import threading
import datetime
import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator

# ==========================================
# 1. 寻路魔法：精准挂载 NVIDIA DLL 计算库
# ==========================================
for path in sys.path:
    cublas_bin = os.path.join(path, "nvidia", "cublas", "bin")
    cudnn_bin = os.path.join(path, "nvidia", "cudnn", "bin")
    
    if os.path.exists(cublas_bin):
        os.add_dll_directory(cublas_bin)
    if os.path.exists(cudnn_bin):
        os.add_dll_directory(cudnn_bin)

# ==========================================
# 2. 界面支持与主题设置
# ==========================================
class CTk(ctk.CTk, TkinterDnD.DnDWrapper):
    """让 CustomTkinter 继承拖拽底层协议的核心类"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue") 

# ==========================================
# 3. 应用程序主类
# ==========================================
class CloudSubtitleApp(CTk):
    def __init__(self):
        super().__init__()

        self.title("AI 双语字幕生成器 (Cloud 极速版)")
        self.geometry("550x400")
        self.resizable(False, False)

        self.video_path = None

        # --- UI 布局 ---
        self.title_label = ctk.CTkLabel(self, text="云端双语字幕极速生成", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=(30, 10))

        self.sub_label = ctk.CTkLabel(self, text="支持 mp4, mov, wav, mp3 格式", text_color="gray", font=("Arial", 12))
        self.sub_label.pack(pady=(0, 20))

        # 核心区：拖拽/点击释放区
        self.drop_zone = ctk.CTkFrame(
            self, width=400, height=150, corner_radius=15,
            fg_color="#2b2b2b", border_width=2, border_color="#4a4a4a", cursor="hand2"
        )
        self.drop_zone.pack(pady=10)
        self.drop_zone.pack_propagate(False) 

        self.file_label = ctk.CTkLabel(
            self.drop_zone, 
            text="📁\n\n拖拽文件到此处\n或 点击选择文件", 
            text_color="silver", font=("Arial", 14), cursor="hand2"
        )
        self.file_label.pack(expand=True)

        # 底部执行按钮
        self.btn_start = ctk.CTkButton(
            self, text="开始处理", font=("Arial", 16, "bold"),
            height=45, width=200, corner_radius=8, state="disabled",
            command=self.on_start_click
        )
        self.btn_start.pack(pady=(25, 0))

        # --- 事件绑定 ---
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.on_file_drop)
        self.drop_zone.bind("<Button-1>", self.on_click_select)
        self.file_label.bind("<Button-1>", self.on_click_select)

    # --- 交互逻辑 ---
    def on_click_select(self, event):
        filepath = filedialog.askopenfilename(
            title="选择音视频文件",
            filetypes=[("Media Files", "*.mp4 *.mov *.avi *.wav *.mp3"), ("All Files", "*.*")]
        )
        if filepath: self.handle_selected_file(filepath)

    def on_file_drop(self, event):
        filepath = event.data.strip("{}")
        self.handle_selected_file(filepath)

    def handle_selected_file(self, filepath):
        valid_extensions = ['.mp4', '.mov', '.avi', '.wav', '.mp3']
        if not any(filepath.lower().endswith(ext) for ext in valid_extensions):
            self.file_label.configure(text="❌ 格式不支持，请重新选择", text_color="#ff6b6b")
            self.drop_zone.configure(border_color="#ff6b6b")
            return

        self.video_path = filepath
        filename = os.path.basename(filepath)
        
        self.file_label.configure(text=f"✅ 已就绪\n\n{filename}", text_color="#51cf66")
        self.drop_zone.configure(border_color="#51cf66")
        self.btn_start.configure(state="normal")

    def on_start_click(self):
        if not self.video_path: return
            
        self.btn_start.configure(state="disabled", text="引擎全速运转中...")
        self.file_label.configure(text="⏳ 正在调用显卡提取原声并请求云端翻译...\n请耐心等待，切勿关闭窗口", text_color="#fcc419")
        self.drop_zone.configure(border_color="#fcc419")

        # 开启后台线程，防止界面卡死
        threading.Thread(target=self.run_ai_engine, daemon=True).start()

    # --- 核心 AI 处理引擎 (后台线程运行) ---
    def run_ai_engine(self):
        output_srt = os.path.splitext(self.video_path)[0] + ".srt"
        
        try:
            # 1. 加载 Whisper 模型到 GTX 1650
            model = WhisperModel("small", device="cuda", compute_type="float16")
            # 2. 初始化云端 Google 翻译器
            translator = GoogleTranslator(source='auto', target='en')

            # 3. 提取原声
            segments, info = model.transcribe(self.video_path, task="transcribe", beam_size=5)

            # 4. 写入双语 SRT
            with open(output_srt, "w", encoding="utf-8") as srt_file:
                for i, segment in enumerate(segments, start=1):
                    start_time = str(datetime.timedelta(seconds=segment.start))[:-3].replace('.', ',')
                    end_time = str(datetime.timedelta(seconds=segment.end))[:-3].replace('.', ',')
                    
                    if len(start_time.split(':')[0]) == 1: start_time = "0" + start_time
                    if len(end_time.split(':')[0]) == 1: end_time = "0" + end_time

                    original_text = segment.text.strip()
                    if not original_text: continue
                    
                    # 联网翻译（增加容错处理）
                    try:
                        english_text = translator.translate(original_text)
                    except Exception:
                        english_text = "[网络波动，翻译失败]"

                    srt_file.write(f"{i}\n")
                    srt_file.write(f"{start_time} --> {end_time}\n")
                    srt_file.write(f"{original_text}\n")
                    srt_file.write(f"{english_text}\n\n")
                    
                    # 终端依然可以看进度
                    print(f"[{start_time}] {original_text}  -->  {english_text}")

            # 成功完成后的 UI 更新
            filename = os.path.basename(output_srt)
            self.file_label.configure(text=f"🎉 处理完成！\n\n字幕已自动生成为同名文件：\n{filename}", text_color="#51cf66")
            self.drop_zone.configure(border_color="#51cf66")

        except Exception as e:
            # 报错时的 UI 更新
            self.file_label.configure(text=f"❌ 发生致命错误:\n{str(e)}", text_color="#ff6b6b")
            self.drop_zone.configure(border_color="#ff6b6b")
            
        finally:
            # 无论成功失败，恢复按钮状态
            self.btn_start.configure(state="normal", text="再次生成")

# ==========================================
# 启动入口
# ==========================================
if __name__ == "__main__":
    app = CloudSubtitleApp()
    app.mainloop()