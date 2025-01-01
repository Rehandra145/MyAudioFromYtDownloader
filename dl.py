import os
from moviepy.audio.io.AudioFileClip import AudioFileClip
import yt_dlp
from ttkbootstrap import Style
from ttkbootstrap.constants import PRIMARY
from ttkbootstrap.widgets import Button
from tkinter import Tk, Label, Entry, filedialog, messagebox, StringVar
import threading
import time
from tkinter.ttk import Progressbar

def clean_title(title):
    keywords_to_remove = [
        "(Official Music Video)", "(Official Video)", "(Official Audio)",
        "(Official Lyric Video)", "(Official)", "(Lyric Video)", "(Lyrics)",
        "(Audio)", "(Music Video)", "(Video)", "(Lyrics Video)", "(Lyric)"
    ]
    for keyword in keywords_to_remove:
        title = title.replace(keyword, "").strip()
    return title

def format_filename(entry):
    title = clean_title(entry.get('title', 'Unknown Title'))
    uploader = entry.get('uploader', 'Unknown Uploader')

    # Check for '-' in title
    if '-' in title:
        return title  # Use title only
    else:
        return f"/%(uploader)s - %(title)s"  # Use uploader - title

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
            progress_label.set(f"Downloading: {current}/{total} files")

        def update_convert_progress(current, total):
            progress_label.set(f"Converting: {current}/{total} files")

        progress_label.set("Starting...")
        time.sleep(3)  # Show "Starting..." for 3 seconds
        progress_label.set("Downloading...")

        download_progress_bar.grid(row=5, column=0, columnspan=2, pady=5)
        download_progress_bar.start()  # Start indeterminate animation
        download_audio_from_playlist(playlist_url, save_path, update_download_progress)
        download_progress_bar.stop()  # Stop animation
        download_progress_bar.grid_forget()

        convert_progress_bar.grid(row=6, column=0, columnspan=2, pady=5)
        convert_progress_bar.start()  # Start indeterminate animation
        convert_all_webm_in_directory(save_path, save_path, progress_callback=update_convert_progress)
        convert_progress_bar.stop()  # Stop animation
        convert_progress_bar.grid_forget()

        messagebox.showinfo("Success", "All files downloaded and converted successfully!")
        url_entry.delete(0, 'end')  # Clear the input field
    except Exception as e:
        download_progress_bar.stop()
        download_progress_bar.grid_forget()
        convert_progress_bar.stop()
        convert_progress_bar.grid_forget()
        print(f"Error during process: {e}")

def start_download():
    playlist_url = url_entry.get().strip()
    save_path = filedialog.askdirectory(title="Select Save Directory")
    if not save_path:
        messagebox.showwarning("Warning", "No save directory selected!")
        return

    progress_label.set("Starting...")

    threading.Thread(target=lambda: start_download_process(playlist_url, save_path, download_progress_bar, convert_progress_bar, progress_label)).start()

def create_gui():
    style = Style("flatly")
    root = style.master
    root.title("YouTube Downloader")
    root.geometry("400x300")

    Label(root, text="YouTube Playlist Downloader", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    Label(root, text="Playlist URL:", font=("Arial", 12)).grid(row=1, column=0, pady=5, padx=10, sticky="e")

    global url_entry
    url_entry = Entry(root, width=40)
    url_entry.grid(row=1, column=1, pady=5, padx=10, sticky="w")

    global download_progress_bar
    download_progress_bar = Progressbar(root, length=400, mode="indeterminate")

    global convert_progress_bar
    convert_progress_bar = Progressbar(root, length=400, mode="indeterminate")

    global progress_label
    progress_label = StringVar()
    progress_label.set("")
    Label(root, textvariable=progress_label, font=("Arial", 10)).grid(row=4, column=0, columnspan=2, pady=10)

    Button(root, text="Download and Convert", command=start_download, bootstyle=PRIMARY, width=30).grid(row=3, column=0, columnspan=2, pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
