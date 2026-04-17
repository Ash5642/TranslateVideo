import json, os
import boto3


transcribe = boto3.client('transcribe', region_name='ap-south-1', use_ssl=True)
s3 = boto3.client('s3', region_name='ap-south-1', use_ssl=True)

def speech_to_text(progress):
    if 'transcribe_job' in progress:
        if "raw_transcript" not in progress['files']:
        
            response = transcribe.get_transcription_job(
                TranscriptionJobName=progress['transcribe_job'] ,
            )
            if response['TranscriptionJob']['TranscriptionJobStatus'] != 'COMPLETED':
                return False
            s3.download_file(
                os.getenv("AWS_S3_ACCESS_POINT"), 
                progress['transcript_url'], 
                progress['dirs']['intermediate_dir']+"raw_transcript.json"
            )
            progress['files']['raw_transcript'] = progress['dirs']['intermediate_dir']+"raw_transcript.json"
            print("transcript generated")
        else:
            print("using stored transcript")
        transcript = {
            "speech":[

            ],
            "speakers":[

            ]
        }
        raw_transcript = None
        progress['files']['raw_transcript'] = progress['dirs']['intermediate_dir']+"raw_transcript.json"
        with open(progress['files']['raw_transcript'], mode="r") as raw_transcript_file:
            raw_transcript = json.loads(raw_transcript_file.read())

        sentence = ""
        start_time = None
        end_time = None
        speaker_list = []
        for item in raw_transcript['results']['items']:
            sentence = sentence + " " + item['alternatives'][0]['content']
            speaker_list.append(item['speaker_label'])
            if item['type'] != 'punctuation' or item['alternatives'][0]['content'] not in ['?', '.', '!']:
                if start_time == None:
                    start_time = item['start_time']
                print(sentence)
                if 'end_time' in item:
                    end_time = item['end_time']
            else:
                max_speaker = None
                max_speaker_count = 0
                for speaker in list(set(speaker_list)):
                    if speaker_list.count(speaker)>max_speaker_count:
                        max_speaker = speaker
                if max_speaker not in transcript['speakers']:
                    transcript['speakers'].append(max_speaker)
                    transcript['speech'].append(
                        {
                            "speech":[],
                            "speaker":max_speaker,
                            
                        }
                    )
                speaker_index = transcript['speakers'].index(max_speaker)
                transcript['speech'][speaker_index]['speech'].append(
                    {
                        "text":sentence,
                        "start":float(start_time),
                        "end":float(end_time),
                        "duration":float(end_time) - float(start_time)
                    }
                )
                sentence = ""
                start_time = None
                max_speaker_count = 0
                max_speaker = None
                speaker_list = []
        progress['files']['transcript'] = progress['dirs']['intermediate_dir']+"transcript.json"
        with open(progress['files']['transcript'] , mode="w") as transcript_file:
            transcript_file.write(json.dumps(transcript, ensure_ascii=False))
        return True
        
    else:
        transcribe_job_key = f"transcribe{progress['key']}"
        transcript_url = f"translate/project_{progress['key']}/transcription.json"
        response = transcribe.start_transcription_job(
            TranscriptionJobName=transcribe_job_key,
            MediaFormat=progress['video'].split('.')[1],
            Media={
                'MediaFileUri': progress['s3_video']
            },
            Settings = {
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': 4
            },
        
            OutputBucketName=os.getenv("AWS_S3_ACCESS_POINT"),
            OutputKey=transcript_url,
            IdentifyLanguage=True,
            
        )
        progress['transcribe_job'] = transcribe_job_key
        progress['transcript_url'] = transcript_url
        """
            with open(progress['files']['text_file'], mode="w+") as text_out:
                text_out.write(json.dumps(output))
            with open("intermediate/temp_text_out.json", mode="w+") as text_out:
                text_out.write(json.dumps(data))
        """
    return False

