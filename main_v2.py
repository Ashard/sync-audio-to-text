import PySimpleGUI as sg
from striprtf.striprtf import rtf_to_text
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import ColorClip
import os,sys

# Constants
FONT_SIZES = []
for i in range(0, 100):
    FONT_SIZES.append(i)

FONT_TYPES = []
for font in TextClip.list("font"):
    FONT_TYPES.append(font)

FONT_COLORS = ["black", "white", "yellow", "blue", "red"]

TEXT_FILE_PATH = "text_file_path"
AUDIO_FILE_PATH = "audio_file_path"
FONT = "font"
FONT_SIZE = "font_size"
FONT_COLOR = "font_color"
CENTER = "center"
DUR_PER_WORD = "dur_per_word"
NUM_WORDS = "num_words"
BG_VIDEO_PATH = "bg_video_path"
TEXT_DISP_DUR = "text_disp_dur"


def create_video(values):
    text_file_path = values.get(TEXT_FILE_PATH)
    audio_file_path = values.get(AUDIO_FILE_PATH)

    text_file = ""
    with open(text_file_path, "r") as f:
        text_file = rtf_to_text(f.read())

    audio_clip = AudioFileClip(audio_file_path)
    bg_video = None
    if values.get(BG_VIDEO_PATH) != "":
        bg_video = VideoFileClip(values.get(BG_VIDEO_PATH))

    if text_file != "" and audio_clip != None:
        words_list = text_file.split(" ")
        num_of_words = 5

        sentences = []
        i = 0
        while i < len(words_list):
            if i + num_of_words >= len(words_list):
                words = words_list[i:]
                sentences.append(words)
            else:
                words = words_list[i:i + num_of_words]
                sentences.append(words)
            i += num_of_words

        total_video_dur = audio_clip.duration
        sent_dur = total_video_dur/len(sentences)
        font = values.get(FONT)
        font_color = values.get(FONT_COLOR)
        font_size = int(values.get(FONT_SIZE))
        text_pos = ("center", "bottom")
        if bool(values.get(CENTER)) == True:
            text_pos = "center"

        print("total video dur: " + str(total_video_dur))
        print("sent dur: " + str(sent_dur))

        text_clips = []
        curr_time = 0
        for sent in sentences:
            sent = " ".join(sent)
            sent = TextClip(txt=sent, color=font_color, fontsize=font_size, font=font)
            sent = sent.set_position(text_pos)
            sent = sent.set_start(curr_time)
            sent = sent.set_duration(sent_dur)
            text_clips.append(sent)
            curr_time += sent_dur

        output_video = None
        if bg_video != None:
            if bg_video.duration < audio_clip.duration:
                dur_diff = audio_clip.duration - bg_video.duration
                black_background_clip = ColorClip(size=(bg_video.size[1], bg_video.size[0]), color=[0, 0, 0], duration=dur_diff)
                bg_video = concatenate_videoclips([bg_video, black_background_clip])

            final_clips = [bg_video] + text_clips
            output_video = CompositeVideoClip(final_clips)
        else:
            output_video = CompositeVideoClip(text_clips, size=(1920, 1080))

        output_video = output_video.set_duration(audio_clip.duration)

        output_path = os.path.dirname(__file__)
        output_path = os.path.join(output_path, "output.mp4")

        output_video.audio = audio_clip
        output_video.write_videofile(preset="ultrafast", threads=os.cpu_count()*4, filename=output_path, fps=24,
                                     audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True)


# UI Code starts here
sg.theme('Dark Amber')
layout = [ [sg.Text(text="Text file:"), sg.FileBrowse(key=TEXT_FILE_PATH, tooltip="Text file")],
           [sg.Text(text="Audio file:"), sg.FileBrowse(key=AUDIO_FILE_PATH, tooltip="Audio file")],
           [sg.Text(text="Background video:"), sg.FileBrowse(key=BG_VIDEO_PATH, tooltip="Background video")],
           [sg.Text(text="Font:"), sg.Combo(key=FONT, values=FONT_TYPES, readonly=True, default_value="Arial")],
           [sg.Text(text="Font size:"), sg.Combo(key=FONT_SIZE, values=FONT_SIZES, default_value=30)],
           [sg.Text(text="Font color:"), sg.Combo(key=FONT_COLOR, values=FONT_COLORS, default_value="white")],
           [sg.Checkbox(key=CENTER, text="Center text", default=False)],
           [sg.Button("Submit")]
            ]

window = sg.Window("praveensanthosh", layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == "Submit":
        create_video(values)

window.close()