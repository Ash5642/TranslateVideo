
import json, num2words, time, os
from moviepy.editor import AudioFileClip

# generate speech by cloning a voice using default settings

def generate(progress, method):
    if method == 'remote':
        import requests
        r = requests.post('http://127.0.0.1:8000', json={"progress": progress['files']['progress']})
        return
    text = {}
    text_trasnslated = ""
    tts = None
    with open(progress['files']['transcript'], mode="r") as text_file:
        text = json.loads(text_file.read())

    for speaker in text['speech']:
        os.makedirs(os.path.dirname(progress['dirs']['generated_speech']+f"{speaker['speaker']}"), exist_ok=True)
        for sentence_id, sentence in enumerate(speaker['speech']):
            if tts == None:
                from TTS.api import TTS
                tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
            generated_audio_path = progress['dirs']['generated_speech']+f"{speaker['speaker']}/speech_{sentence_id}.wav"
            print(f"generating\t{speaker['speaker']}\t{sentence_id+1}/{len(speaker['speech'])}")
            final_gen = False
            audio_scale = float(1)
            while not final_gen:
                print(f"using scal factor {audio_scale}")
                tts.tts_to_file(
                    text=sentence['translated'],
                    file_path=generated_audio_path,
                    speaker_wav=sentence['source_audio'],
                    language=progress['languages']['target'],
                    speed = audio_scale
                )
                audio_written_file = AudioFileClip(generated_audio_path)
                if audio_written_file.duration > (sentence['duration']+min(sentence['duration']*0.05, 1)):
                    audio_scale = audio_scale*(audio_written_file.duration/sentence['duration'])
                    print(f"retrying with scale {audio_scale}")


                    

            sentence['generated'] = {
                "path":generated_audio_path,
                "lenght":audio_written_file.duration
            }
    with open(progress['files']['transcript'], mode="w") as text_file:
        text_file.write(json.dumps(text, ensure_ascii=False))

    """for seg_num, line in enumerate(text['text']):
        for translation_num, translation in enumerate(line['translated']):
            out_segment_file = f"{out_file}/segment_{seg_num}_{translation_num}.wav"
            if [model, f"translated/{translation_num}"] not in [[existing_out['model'], existing_out['text']] for existing_out in line['generated_speech']]:
                scale_factor = 1
                final = False
                start_time = line['start']
                end_time = line['end']
                while not final:
                    print(f"Translating {seg_num} @{scale_factor}")
                    time_start = time.time()
                    match model:
                        case "xtts":
                            if tts == None:
                                from TTS.api import TTS
                                tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
                            tts.tts_to_file(
                                text=translation['translated'],
                                file_path=[out_segment_file],
                                speaker_wav=voice_file,
                                language=language,
                                speed=scale_factor
                            )
                    time_end = time.time()
                    audio_written_file = AudioFileClip(out_segment_file)
                    if ((end_time- start_time)) < (audio_written_file.duration*0.8):
                        scale_factor = scale_factor*((audio_written_file.duration)/((end_time-start_time)*0.8))
                        if scale_factor>2 and line!=text['text'][-1]:
                            end_time = text['text'][seg_num+1]['end']
                            scale_factor = scale_factor*((audio_written_file.duration)/((end_time-start_time)*0.8))
                            print('jumping')
                            continue
                        print(f"Generated speech too long ({end_time-start_time} vs {audio_written_file.duration}), scaing with {scale_factor}")
                        continue
                    line['generated_speech'].append(
                        {
                            "model":model,
                            "output":out_segment_file,
                            "duration":audio_written_file.duration,
                            "scale":scale_factor,
                            "text":f"translated/{translation_num}",
                            "meta":{
                                "model":model,
                                "processing_time":time_end-time_start
                            }
                        }
                    )
                    break
            else:
                print("SKIPPING")
            with open(text_path, mode="w") as text_file:
                text_file.write(json.dumps(text, ensure_ascii=False))
"""
