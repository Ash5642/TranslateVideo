
import json, time, os


aws_translate = None
def translate_file(progress):
    transcript = None
    with open(progress['files']['transcript'], mode="r") as transcript_file:
        transcript = json.loads(transcript_file.read())
    for speaker in transcript['speech']:
        for speech in speaker['speech']:
    
            speech['translated'] = translate_aws(speech, progress['languages']['source'], progress['languages']['target'])
    print(transcript)
    with open(progress['files']['transcript'], mode="w") as transcript_file:
        transcript_file.write(json.dumps(transcript, ensure_ascii=False))


        
def translate_translategemma(segment, source_language, target_language):
    from ollama import chat
    from ollama import ChatResponse
    response: ChatResponse = chat(model='translategemma:12b', messages=[
    {
        'role': 'user',
        'content': f"""
            You are a professional {source_language} ({source_language}) to {target_language} ({target_language}) translator. Your goal is to accurately convey the meaning and nuances of the original {source_language} text with {segment['word_count']} or fewer number of words while adhering to {target_language} grammar, vocabulary, and cultural sensitivities.
            Produce only the {target_language} translation, without any additional explanations or commentary. Please translate the following {source_language} text into {target_language}:
            {segment['text']}
        """
    },
    ])
    return response.message.content

def translate_aws(segment, source_language, target_language):
    import boto3
    aws_translate = boto3.client(service_name='translate', region_name="ap-south-1", use_ssl=True)
    result = aws_translate.translate_text(
        Text=segment['text'],         
        SourceLanguageCode="en", 
        TargetLanguageCode="hi",
        Settings={
            "Brevity": "ON"
        }
    )
    return result.get('TranslatedText')

def translate_aws_batch(progress):
    import boto3
    aws_translate = boto3.client(service_name='translate', region_name="ap-south-1", use_ssl=True)
    response = aws_translate.start_text_translation_job(
        JobName='string',
        InputDataConfig={
            'S3Uri': progress['transcript_url'],
            'ContentType': 'string'
        },
        OutputDataConfig={
            'S3Uri': progress['dirs']['intermediate_dir'],
            
        },
        DataAccessRoleArn='arn:aws:s3:ap-south-1:981268234088:accesspoint/home-test',
        SourceLanguageCode='en',
        TargetLanguageCodes=[
            'hi',
        ],
        
        ClientToken='string',
        Settings={
            'Brevity': 'ON'
        }
    )