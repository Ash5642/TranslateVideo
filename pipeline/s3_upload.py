import boto3
import json, os
s3 = boto3.client('s3', region_name='ap-south-1', use_ssl=True)
# Or using resources
def upload(progress):
    if 's3_video' in progress:
        return progress
    key = progress['dirs']['media_dir']+progress['video']
    
    upload_details = s3.upload_file(
        progress['video'], 
        os.getenv("AWS_S3_ACCESS_POINT"), 
        key
    )
    print(upload_details)
    progress['s3_video'] = f"{os.getenv("AWS_S3_BUCKET_URL")}{key}"
    upload_faces(progress)
    return progress

def upload_faces(progress):
    from pathlib import Path
    import shutil

    # Basic usage: Destination must NOT exist beforehand
    shutil.copytree(progress['files']['original_face_set'], progress['dirs']['media_dir']+"faces/")

    p = Path(progress['dirs']['media_dir']+"faces/")
    face_list = []
    for item in p.iterdir():
        current_face = {
            "name":item.name,
            "images":[]
        }
        print(item.name)
        for file in item.iterdir():
            if file.is_file():
                
                face_key = progress['dirs']['media_dir']+f"faces/{item.name}/{file.name}"
                s3.upload_file(
                    file, 
                    os.getenv("AWS_S3_ACCESS_POINT"), 
                    face_key
                )
                current_face['images'].append(face_key)
        face_list.append(current_face)
                

    rekognition_client = boto3.client('rekognition', region_name='ap-south-1')
    collection_id = f'face_collection_{progress['key']}'
    try:
        print(f'Creating collection: {collection_id}')
        response = rekognition_client.create_collection(CollectionId=collection_id)
        print(f'Collection ARN: {response["CollectionArn"]}')
        progress['files']['collection'] = response
        progress['files']['collection']['collection_id'] = collection_id
    except Exception as e:
        print(f'Error: {e}')
    
    for face in face_list:
        for image in face['images']:
            response = rekognition_client.index_faces(
                CollectionId=collection_id,
                Image={'S3Object': {'Bucket': os.getenv("AWS_S3_BUCKET"), 'Name': image}},
                ExternalImageId=face['name'], # Optional: Name to associate with the face
                MaxFaces=1,
                QualityFilter="AUTO", # Filters out low-quality faces
                DetectionAttributes=['DEFAULT']
            )

