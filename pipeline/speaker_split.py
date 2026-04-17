from pydub import AudioSegment
import json, os

def split(progress):
    transcript = None
    with open(progress['files']['transcript'], mode="r") as transcript_file:
        transcript = json.loads(transcript_file.read())
    full_sound = AudioSegment.from_file(progress['video'], progress['video'].split('.')[1])
    for speaker in transcript['speech']:
        speaker_audio = AudioSegment.empty()
        os.makedirs(os.path.dirname(progress['dirs']['speaker_spliced']+f"speaker_{speaker['speaker']}/"), exist_ok=True)
        for sentence_id, speech in enumerate(speaker['speech']):
            sentence_audio = full_sound[float(speech['start'])*1000:float(speech['end'])*1000]
            speaker_audio = speaker_audio + sentence_audio
            speech['source_audio'] = progress['dirs']['speaker_spliced']+f"speaker_{speaker['speaker']}/sentence_{sentence_id}.mp3"
            sentence_audio.export(speech['source_audio'], format="mp3")
        speaker_audio.export(progress['dirs']['speaker_spliced']+f"speaker_{speaker['speaker']}/combined.mp3", format="mp3")
        speaker['speaker_spliced'] = progress['dirs']['speaker_spliced']+f"speaker_{speaker['speaker']}/combined.mp3"
    with open(progress['files']['transcript'], mode="w") as transcript_file:
        transcript_file.write(json.dumps(transcript, ensure_ascii=False))