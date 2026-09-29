import asyncio
import json
import os
import re
import requests
from edge_tts import Communicate
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip, concatenate_videoclips

# ==================== 配置区 ====================
# 默认使用免费的爽文经典男声 "zh-CN-YunxiNeural"（云希）
VOICE = "zh-CN-YunxiNeural" 
OUTPUT_DIR = "output_novel_video"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 示例爽文剧本片段
NOVEL_SCRIPT = [
    {"text": "少年陈凡被退婚当日，全场长老皆出言嘲讽！", "prompt": "angry young man, ancient fantasy martial arts, anime style, dramatic lighting"},
    {"text": "谁知他反手掏出九品丹方，轰动了整个沧州城！", "prompt": "shocked elders, ancient Chinese fantasy hall, luminous magic pill recipe, anime concept art"},
    {"text": "从今日起，曾辱我者，我必百倍奉还！", "prompt": "overpowered young hero, glowing eyes, sword aura, domineering posture, cinematic anime"}
]

# ==================== 1. 免费配音生成 (Edge-TTS) ====================
async def generate_audio(text, output_path):
    communicate = Communicate(text, VOICE)
    await communicate.save(output_path)

# ==================== 2. 免费画图接口 (Pollinations API) ====================
def download_image(prompt, output_path):
    encoded_prompt = requests.utils.quote(f"{prompt}, high quality, 8k, masterpiece")
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true"
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)

# ==================== 3. 自动化合成流水线 ====================
async def process_novel_agent():
    clips = []
    print("🚀 爽文小说视频 Agent 启动...")

    for idx, scene in enumerate(NOVEL_SCRIPT):
        print(f"🎬 正在处理第 {idx+1}/{len(NOVEL_SCRIPT)} 幕...")
        
        audio_path = os.path.join(OUTPUT_DIR, f"audio_{idx}.mp3")
        img_path = os.path.join(OUTPUT_DIR, f"image_{idx}.jpg")
        
        # 1. 生成语音
        await generate_audio(scene["text"], audio_path)
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        
        # 2. 生成对应 AI 插画
        download_image(scene["prompt"], img_path)
        
        # 3. 构建慢速推拉镜头的图片 Clip
        img_clip = ImageClip(img_path).set_duration(duration)
        img_clip = img_clip.resize(lambda t: 1 + 0.03 * t) # 轻微放大产生推镜效果
        
        # 4. 叠加音频
        video_segment = img_clip.set_audio(audio_clip)
        clips.append(video_segment)

    print("✂️ 正在进行最终全自动拼接与导出...")
    final_video = concatenate_videoclips(clips, method="compose")
    final_output_path = os.path.join(OUTPUT_DIR, "final_novel_short.mp4")
    
    # 导出适应短视频平台（竖屏 1080x1920 30fps）
    final_video.write_videofile(
        final_output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )
    print(f"✅ 视频生成完毕！输出文件存放在：{final_output_path}")

if __name__ == "__main__":
    asyncio.run(process_novel_agent())
