import os
from moviepy.audio.io.AudioFileClip import AudioFileClip
import yt_dlp
from tkinter import Tk, Label, Entry, filedialog, messagebox, StringVar
from tkinter.ttk import Progressbar, Button
import threading

def clean_title(title):
    keywords_to_remove = [
        "(Official Music Video)", "(Official Video)", "(OFFICIAL VIDEO)", "(Official Audio)",
        "(Official Lyric Video)", "(Official Lyrics Video)", "(Official)", "(Lyric Video)", "(Lyrics)",
        "(Full Album Stream)", "(Audio)", "(Music Video)", "(Video)", "(Lyrics Video)", "(Lyric)",
        "(OFFICIAL AUDIO STREAM)", "(Guitar Playthrough)"
    ]
    for keyword in keywords_to_remove:
        title = title.replace(keyword, "").strip()
    return title

def clean_uploader(uploader):
    # Jika nama uploader mengandung " - Topic", ambil bagian sebelum " - Topic"
    if " - Topic" in uploader:
        uploader = uploader.split(" - Topic")[0].strip()
    return uploader

def format_filename(entry):
    title = clean_title(entry.get('title', 'Unknown Title'))
    uploader = clean_uploader(entry.get('uploader', 'Unknown Uploader'))

    if '-' in title:
        return title
    else:
        return f"{uploader} - {title}"


def download_audio_from_playlist(playlist_url, save_path, progress_callback):
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info_dict = ydl.extract_info(playlist_url, download=False)

            if 'entries' in info_dict:
                total_entries = len(info_dict['entries'])
                for index, entry in enumerate(info_dict['entries']):
                    formatted_title = format_filename(entry)
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'extractaudio': True,
                        'outtmpl': f"{save_path}/{formatted_title}.%(ext)s",
                        'postprocessors': [],
                        'no_cache_dir': True,
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_inner:
                        ydl_inner.download([entry['webpage_url']])
                        progress_callback(index + 1, total_entries)
            else:
                formatted_title = format_filename(info_dict)
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'extractaudio': True,
                    'outtmpl': f"{save_path}/{formatted_title}.%(ext)s",
                    'postprocessors': [],
                    'no_cache_dir': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_inner:
                    ydl_inner.download([playlist_url])
                    progress_callback(1, 1)
    except Exception as e:
        messagebox.showerror("Error", f"Error downloading playlist or video: {e}")
        raise e

def convert_webm_to_mp3(input_file, output_file, bitrate="256k", progress_callback=None, total_files=1, current_file=1):
    try:
        with AudioFileClip(input_file) as audio:
            audio.write_audiofile(output_file, codec='mp3', bitrate=bitrate)
        os.remove(input_file)
        if progress_callback:
            progress_callback(current_file, total_files)
    except Exception as e:
        messagebox.showerror("Error", f"Error converting {input_file}: {e}")
        raise e

def convert_all_webm_in_directory(directory, output_directory, bitrate="256k", progress_callback=None):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    webm_files = [f for f in os.listdir(directory) if f.endswith(".webm")]
    total_files = len(webm_files)

    for index, filename in enumerate(webm_files):
        input_path = os.path.join(directory, filename)
        output_filename = f"{os.path.splitext(filename)[0]}.mp3"
        output_path = os.path.join(output_directory, output_filename)
        convert_webm_to_mp3(input_path, output_path, bitrate, progress_callback, total_files, index + 1)

def start_download_process(playlist_url, save_path, download_progress_bar, convert_progress_bar, progress_label):
    try:
        def update_download_progress(current, total):
            progress_label.set(f"Downloaded: {current}/{total} files")
            download_progress_bar['value'] = (current / total) * 100
            root.update_idletasks()

        def update_convert_progress(current, total):
            progress_label.set(f"Converted: {current}/{total} files")
            convert_progress_bar['value'] = (current / total) * 100
            root.update_idletasks()

        download_progress_bar.grid()
        convert_progress_bar.grid_remove()

        progress_label.set("Downloading...")
        download_audio_from_playlist(playlist_url, save_path, update_download_progress)

        download_progress_bar.grid_remove()
        convert_progress_bar.grid()

        progress_label.set("Converting...")
        convert_all_webm_in_directory(save_path, save_path, progress_callback=update_convert_progress)

        messagebox.showinfo("Success", "All files downloaded and converted successfully!")
        url_entry.delete(0, 'end')
    except Exception as e:
        print(f"Error during process: {e}")

def start_download():
    playlist_url = url_entry.get().strip()
    save_path = filedialog.askdirectory(title="Select Save Directory")
    if not save_path:
        messagebox.showwarning("Warning", "No save directory selected!")
        return

    progress_label.set("Starting...")
    download_progress_bar.grid_remove()
    convert_progress_bar.grid_remove()

    threading.Thread(
        target=lambda: start_download_process(
            playlist_url, save_path, download_progress_bar, convert_progress_bar, progress_label
        )
    ).start()

def create_gui():
    global root
    root = Tk()
    root.title("YouTube Downloader")
    root.geometry("400x300")

    Label(root, text="YouTube Playlist Downloader", font=("Arial", 16, "bold")).grid(
        row=0, column=0, columnspan=2, pady=10)

    Label(root, text="Playlist URL:", font=("Arial", 12)).grid(
        row=1, column=0, pady=5, padx=10, sticky="e")

    global url_entry
    url_entry = Entry(root, width=40)
    url_entry.grid(row=1, column=1, pady=5, padx=10, sticky="w")

    global download_progress_bar
    download_progress_bar = Progressbar(root, length=400, mode="determinate")
    download_progress_bar.grid(row=5, column=0, columnspan=2, pady=5)
    download_progress_bar.grid_remove()  # Sembunyikan di awal

    global convert_progress_bar
    convert_progress_bar = Progressbar(root, length=400, mode="determinate")
    convert_progress_bar.grid(row=6, column=0, columnspan=2, pady=5)
    convert_progress_bar.grid_remove()  # Sembunyikan di awal

    global progress_label
    progress_label = StringVar()
    progress_label.set("")
    Label(root, textvariable=progress_label, font=("Arial", 10)).grid(
        row=4, column=0, columnspan=2, pady=10)

    Button(root, text="Download and Convert", command=start_download).grid(
        row=3, column=0, columnspan=2, pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
