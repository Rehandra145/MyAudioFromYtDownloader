import os
from moviepy.audio.io.AudioFileClip import AudioFileClip
import yt_dlp
from tkinter import Tk, Label, Entry, filedialog, messagebox, StringVar, Frame, ttk
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

def start_download_process(playlist_url, save_path, download_progress_bar, convert_progress_bar, progress_label, download_btn):
    try:
        download_btn.pack_forget()
        def update_download_progress(current, total):
            progress_label.set(f"Downloaded: {current}/{total} files")
            download_progress_bar['value'] = (current / total) * 100
            root.update_idletasks()

        def update_convert_progress(current, total):
            progress_label.set(f"Converted: {current}/{total} files")
            convert_progress_bar['value'] = (current / total) * 100
            root.update_idletasks()

        def reset_progress_bars():
            download_progress_bar['value'] = 0
            convert_progress_bar['value'] = 0
            progress_label.set("Ready to download")
            download_progress_bar.pack_forget()
            convert_progress_bar.pack_forget()
            download_btn.pack()
            root.update_idletasks()

        # Start download process
        download_progress_bar.pack()
        convert_progress_bar.pack_forget()

        progress_label.set("Downloading...")
        download_audio_from_playlist(playlist_url, save_path, update_download_progress)

        # Switch to conversion process
        download_progress_bar.pack_forget()
        convert_progress_bar.pack()

        progress_label.set("Converting...")
        convert_all_webm_in_directory(save_path, save_path, progress_callback=update_convert_progress)

        # Reset UI after completion
        reset_progress_bars()
        
        messagebox.showinfo("Success", "All files downloaded and converted successfully!")
        url_entry.delete(0, 'end')
    except Exception as e:
        print(f"Error during process: {e}")
        # Reset UI in case of error
        reset_progress_bars()

def start_download():
    playlist_url = url_entry.get().strip()
    if not playlist_url:
        messagebox.showwarning("Warning", "Please enter a playlist URL!")
        return
        
    save_path = filedialog.askdirectory(title="Select Save Directory")
    if not save_path:
        messagebox.showwarning("Warning", "No save directory selected!")
        return

    progress_label.set("Starting...")
    download_progress_bar.pack_forget()
    convert_progress_bar.pack_forget()

    threading.Thread(
        target=lambda: start_download_process(
            playlist_url, save_path, download_progress_bar, convert_progress_bar, progress_label, download_btn
        )
    ).start()

def create_gui():
    global root
    root = Tk()
    root.title("Elegant Music Downloader")
    root.geometry("600x400")
    root.configure(bg='#f5f5f5')
    
    # Configure styles
    style = ttk.Style()
    style.theme_use('clam')
    
    style.configure(
        'Custom.TButton',
        background='#4a90e2',
        foreground='white',
        padding=(20, 10),
        font=('Helvetica', 11),
        borderwidth=0
    )
    
    style.configure(
        'Custom.Horizontal.TProgressbar',
        troughcolor='#f0f0f0',
        background='#4a90e2',
        thickness=10
    )
    
    # Create main container
    main_frame = Frame(root, bg='#f5f5f5', padx=40, pady=30)
    main_frame.pack(fill='both', expand=True)
    
    # Title with modern styling
    title_frame = Frame(main_frame, bg='#f5f5f5')
    title_frame.pack(fill='x', pady=(0, 30))
    
    Label(
        title_frame,
        text="Music Downloader",
        font=("Helvetica", 24, "bold"),
        fg='#2c3e50',
        bg='#f5f5f5'
    ).pack()
    
    Label(
        title_frame,
        text="Download and convert YouTube playlists to MP3",
        font=("Helvetica", 12),
        fg='#7f8c8d',
        bg='#f5f5f5'
    ).pack(pady=(5, 0))
    
    # URL input container
    input_frame = Frame(main_frame, bg='#f5f5f5')
    input_frame.pack(fill='x', pady=(0, 20))
    
    Label(
        input_frame,
        text="Playlist URL",
        font=("Helvetica", 11),
        fg='#2c3e50',
        bg='#f5f5f5'
    ).pack(anchor='w')
    
    global url_entry
    url_entry = Entry(
        input_frame,
        font=("Helvetica", 11),
        bg='white',
        fg='#2c3e50',
        relief='solid',
        bd=1
    )
    url_entry.pack(fill='x', pady=(5, 0))
    
    # Progress container
    progress_frame = Frame(main_frame, bg='#f5f5f5')
    progress_frame.pack(fill='x', pady=20)
    
    global progress_label
    progress_label = StringVar()
    progress_label.set("")
    Label(
        progress_frame,
        textvariable=progress_label,
        font=("Helvetica", 11),
        fg='#7f8c8d',
        bg='#f5f5f5'
    ).pack(anchor='w', pady=(0, 10))
    
    global download_progress_bar
    download_progress_bar = ttk.Progressbar(
        progress_frame,
        style='Custom.Horizontal.TProgressbar',
        length=520,
        mode="determinate"
    )
    download_progress_bar.pack(fill='x')
    download_progress_bar.pack_forget()
    
    global convert_progress_bar
    convert_progress_bar = ttk.Progressbar(
        progress_frame,
        style='Custom.Horizontal.TProgressbar',
        length=520,
        mode="determinate"
    )
    convert_progress_bar.pack(fill='x')
    convert_progress_bar.pack_forget()
    
    # Button container
    button_frame = Frame(main_frame, bg='#f5f5f5')
    button_frame.pack(fill='x', pady=(20, 0))
    
    global download_btn
    download_btn = ttk.Button(
        button_frame,
        text="Download and Convert",
        style='Custom.TButton',
        command=start_download
    )
    download_btn.pack()
    
    # Status container
    status_frame = Frame(main_frame, bg='#f5f5f5')
    status_frame.pack(fill='x', pady=(20, 0))
    
    Label(
        status_frame,
        text="Ready to download",
        font=("Helvetica", 10),
        fg='#95a5a6',
        bg='#f5f5f5'
    ).pack()

    root.mainloop()

if __name__ == "__main__":
    create_gui()