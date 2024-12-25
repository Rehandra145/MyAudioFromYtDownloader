import os
from moviepy.audio.io.AudioFileClip import AudioFileClip
import yt_dlp

#title handler
def get_outtmpl(uploader, title, ext, save_path):
    kata_kata_hapus = [
        "(Official Music Video)",
        "(Official Video)",
        "(Official Audio)",
        "(Official Lyric Video)",
        "(Official)",
        "(Lyric Video)",
        "(Lyrics)",
        "(Audio)",
        "(Music Video)",
        "(Video)",
        "(Lyrics Video)",
        "(Lyric)"
    ]
    for kata in kata_kata_hapus:
        title = title.replace(kata, "").strip()
    if '-' not in title.lower():
        return f"{save_path}/{uploader} - {title}.{ext}"
    else:
        return f"{save_path}/{title}.{ext}"

def download_audio_from_playlist(playlist_url, save_path="C:/Users/infinix/Music/Hp"):
    print(f"Files will be saved to: {save_path}")
    with yt_dlp.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(playlist_url, download=False)
        uploader = info_dict.get('uploader', 'Unknown Artist')
        title = info_dict.get('title', 'Unknown Title')
        ext = info_dict.get('ext', 'mp3')
        outtmpl = get_outtmpl(uploader, title, ext, save_path)

    # Konfigurasi opsi unduhan
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True, 
        'outtmpl': outtmpl, 
        'postprocessors': [], 
        'no_cache_dir': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

def convert_webm_to_mp3(input_file, output_file, bitrate="256k"):
    try:
        video = AudioFileClip(input_file)
        video.write_audiofile(output_file, codec='mp3', bitrate=bitrate)
        print(f"Conversion successful: {input_file} -> {output_file}")
        os.remove(input_file)
        print(f"Deleted original WebM file: {input_file}")
    except Exception as e:
        print(f"Error converting {input_file}: {e}")

def convert_all_webm_in_directory(directory, output_directory, bitrate="256k"):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Folder '{output_directory}' has been created.")
    for filename in os.listdir(directory):
        if filename.endswith(".webm"):  
            input_path = os.path.join(directory, filename)
            output_filename = f"{os.path.splitext(filename)[0]}.mp3"
            output_path = os.path.join(output_directory, output_filename)
            convert_webm_to_mp3(input_path, output_path, bitrate)

if __name__ == "__main__":
    playlist_url = input("Enter YouTube playlist URL: ")
    save_path = "C:/Users/infinix/Music/Hp"
    download_audio_from_playlist(playlist_url, save_path)
    convert_all_webm_in_directory(save_path, save_path)