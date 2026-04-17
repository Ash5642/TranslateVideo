from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip
import json

def combine(progress):
    with open(progress['files']['transcript'], mode="r") as text_file:
        text = json.loads(text_file.read())
    #sound = AudioSegment.from_file(bg_audio_file, format="mp3")
    video_clip = VideoFileClip(progress['video'])
    video_audio_file = AudioFileClip(progress['video'])
    sound = AudioSegment.silent(duration=video_audio_file.duration*1000)
    for speaker in text['speech']:
        for segment in speaker['speech']:
            sound = sound.overlay(AudioSegment.from_file(segment['generated']['path'], format="wav"), position=float(segment['start'])*1000)
    progress['files']['output_audio'] = progress['dirs']['media_dir']+"output_audio.wav"   
    sound.export(progress['files']['output_audio'], format="wav")
    audio_file = AudioFileClip(progress['files']['output_audio'])
    
     
    progress['files']['output_video'] = progress['dirs']['media_dir']+"output_video.mp4"    
    merged_file = video_clip.set_audio(audio_file)
    merged_file.write_videofile(progress['files']['output_video'])
