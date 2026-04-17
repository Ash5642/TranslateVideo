import moviepy.editor as mp

def extract_audio2(video_path, output_audio_path):
    with open(output_audio_path, mode="w+") as af:
        pass
    video_clip = mp.VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(output_audio_path)
    audio_clip.close()
    video_clip.close()


def extract_audio(video_path, output_audio_path):
    import boto3
    client = boto3.client('transcribe', region_name=aws_region, use_ssl=True)
    