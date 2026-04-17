import demucs.separate

def split_audio(input_file, output_folder):
    print("splitting")
    demucs.separate.main(["-o", output_folder, "--mp3", "--two-stems", "vocals", "-n", "mdx_extra", input_file]) 