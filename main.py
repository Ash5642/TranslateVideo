import sys, json, random, os, time, argparse
import torch
from dotenv import load_dotenv

load_dotenv('vars.env')

torch.cuda.empty_cache()


parser = argparse.ArgumentParser()
parser.add_argument("-e", "--existing")
parser.add_argument("-f", "--faces", type=str),
parser.add_argument("-v", "--video", type=str)
parser.add_argument("-t", "--target", type=str)



args = parser.parse_args()

def update_progress():
    with open(progress_file_name, mode="w+") as prog_file:
        prog_file.write(json.dumps(progress))

step_list = [
    "upload",
    #"faces",
    "audio_extract",
    "audio_split",
    "text_extract",
    "speaker_split",
    "translate",
    "audio_generate",
    "audio_combine"
]
key = random.randint(0, 1000)
progress = {
    "progress":[],
    "video":args.video,
    "key":key,
    "languages":{
        "source":"en",
        "target":args.target
    },
    "dirs":{
        "intermediate_dir":f"projects/project_{key}/intermediate/",
        "media_dir":f"projects/project_{key}/media/",
        "root":f"projects/project_{key}/",

        "speaker_spliced":f"projects/project_{key}/media/speaker_spliced/",
        "generated_speech":f"projects/project_{key}/media/generated/"
    },
    "files":{
        "original_face_set":"media/faces"
    },
    "target_language":args.target
}



progress_file_name = ""


if args.existing != None:
    progress_file_name = args.existing
    with open(progress_file_name, mode="r") as prog_file:
        progress = json.loads(prog_file.read())

else:
    for directory in progress['dirs'].keys():
        os.makedirs(os.path.dirname(progress['dirs'][directory]), exist_ok=True)
    progress_file_name = progress['dirs']['root']+"progress.json"
    progress['files']['progress'] = progress_file_name
    print(f"Project ID: {progress['key']}")
    with open(progress_file_name, mode="w+") as prog_file:
        prog_file.write(json.dumps(progress))
    
extract_first = True      

for step in step_list:
    if step not in progress['progress']:
        print(f"Starrting step {step}")
        if step == "upload":
            from pipeline import s3_upload
            progress = s3_upload.upload(progress)
        if step == 'faces':
            from pipeline import face_detect
            face_detect.find_faces(progress)
        if step == "audio_extract":
            from pipeline import speech_extract
            progress['files']['extracted_speech'] = f"media/extracted_speech/extracted_{progress['key']}.mp3"
            speech_extract.extract_audio(progress['video'], progress['files']['extracted_speech'])
        if step == "audio_split":
            from pipeline import audio_split
            progress['files']['split_speech'] = f"media/split_speech/split_{progress['key']}"
            audio_split.split_audio(progress['files']['extracted_speech'], progress['files']['split_speech'])
            progress['files']['split_speech'] = progress['files']['split_speech']+f"/mdx_extra/extracted_{progress['key']}"
        if step == "text_extract":
            from pipeline import speech_to_text
            speech_to_text_complete = False
            while not speech_to_text_complete:
                speech_to_text_complete = speech_to_text.speech_to_text(progress)
                if speech_to_text_complete:
                    print("transcript generated")
                    break
                if extract_first:
                    print(f"checking job status", end="")
                else:
                    print(".", end="")
                time.sleep(1)
            print("")
        if step == 'speaker_split':
            from pipeline import speaker_split
            speaker_split.split(progress)
        if step == "translate":
            from pipeline import translate
            translate.translate_file(progress)

        if step == "audio_generate":
            from pipeline import speech_gen
            progress['files']['generated_speech'] = f"media/generated_speech/generated_{progress['key']}"
            speech_gen.generate(progress, 'remote')
        if step == "audio_combine":
            from pipeline import combine_audio
            progress['files']['combined_video'] = f"media/combined_speech/combined_video_{progress['key']}.mp4"
            progress['files']['combined_audio'] = f"media/combined_speech/combined_audio_{progress['key']}.wav"

            combine_audio.combine(progress)
        progress['progress'].append(step)
        with open(progress_file_name, mode="w") as prog_file:
            prog_file.write(json.dumps(progress))