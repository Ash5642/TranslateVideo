import whisper_timestamped as whisper
import json
import torch, re
from num2words import num2words

torch.cuda.empty_cache()


def speech_to_text(audio_file, out_file, model_name):
    audio = whisper.load_audio(audio_file)
    model = whisper.load_model("base")
    data = None
    if model_name ==  "whisper":
        data = whisper.transcribe(model, audio, language="en")
        

    #convert numbers to word form
    output = {
        "text":[],
        "sentences":[]
    }
    sentence = ""
    sentence_start = 0
    word_count = 0
    for segment in data['segments']:
        for word in segment['words']:
            word_count = word_count+1
            if sentence == "":
                sentence_start = word['start']
            sentence = sentence+" "+word['text']
            if word['text'][-1] in ['.', '?']:
                output['text'].append(
                    {
                        "start":sentence_start,
                        "end":word['end'],
                        "text":re.sub(r"(\d+)", lambda x: num2words(int(x.group(0))), sentence),
                        "translated":[],
                        "word_count":word_count,
                        "generated_speech":[],
                        "models":{
                            "speech_to_text":model_name,
                            "translation":None,
                            "text_to_speech":None
                        }

                    }
                )
                sentence = ""
                word_count = 0


    with open(out_file, mode="w+") as text_out:
        text_out.write(json.dumps(output))
    with open("intermediate/temp_text_out.json", mode="w+") as text_out:
        text_out.write(json.dumps(data))
    return data

