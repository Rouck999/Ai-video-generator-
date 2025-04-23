
import gradio as gr
from PIL import Image
from moviepy.editor import VideoFileClip, AudioFileClip
import numpy as np
import cv2
from PIL import ImageEnhance

def preprocess_image(image: Image.Image):
    image = image.resize((512, 512))
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.1)
    sharpener = ImageEnhance.Sharpness(image)
    image = sharpener.enhance(1.5)
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(1.2)
    return image

def create_video_from_image(image: Image.Image, output_path="output_video.mp4", duration=5, fps=24):
    frame_count = duration * fps
    width, height = image.size
    video_size = (width, height)

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, video_size)

    frame_np = np.array(image)
    frame = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)

    for i in range(frame_count):
        zoom = 1 + (i / frame_count) * 0.1
        zoomed_frame = cv2.resize(frame, None, fx=zoom, fy=zoom)
        center_x, center_y = zoomed_frame.shape[1]//2, zoomed_frame.shape[0]//2
        crop_frame = zoomed_frame[center_y - height//2:center_y + height//2,
                                  center_x - width//2:center_x + width//2]
        out.write(crop_frame)

    out.release()
    return output_path

def add_audio_to_video(video_path, audio_path="bg_music.mp3", output_path="final_video_with_audio.mp4"):
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path).subclip(0, video_clip.duration)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path

def generate_video(image, duration, fps):
    processed_image = preprocess_image(image)
    video_path = create_video_from_image(processed_image, duration=duration, fps=fps)
    final_video = add_audio_to_video(video_path)
    return "Video generated successfully!", final_video

interface = gr.Interface(fn=generate_video,
                         inputs=[gr.Image(type="pil"), gr.Slider(minimum=1, maximum=10, value=5),
                                 gr.Slider(minimum=5, maximum=60, value=24)],
                         outputs=[gr.Textbox(), gr.File()],
                         title="AI Image to Video Generator",
                         description="Upload an image, adjust duration and fps, and generate your video.")

interface.launch(share=True)
