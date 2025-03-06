import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import tkinter.font as tkfont
import pygame
import threading
import os
from gtts import gTTS
import soundfile as sf
import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize pygame mixer
pygame.mixer.init()

class WaveformVisualizer:
    def __init__(self, master, width=600, height=100):  
        """Create a waveform visualization canvas"""
        self.master = master
        self.width = width
        self.height = height
        
        # Create matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(6, 1), dpi=100)  
        self.ax.set_facecolor('#E6D5C1')  # Match app's background
        self.ax.set_title('Audio Waveform', fontsize=10)
        self.ax.set_xlabel('Time', fontsize=8)
        self.ax.set_ylabel('Amplitude', fontsize=8)
        
        # Embed matplotlib figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.X, padx=10, pady=10)

    def update_waveform(self, audio_data):
        """Update waveform visualization"""
        self.ax.clear()
        self.ax.set_facecolor('#E6D5C1')
        self.ax.plot(audio_data)
        self.ax.set_title('Audio Waveform', fontsize=10)
        self.ax.set_xlabel('Time', fontsize=8)
        self.ax.set_ylabel('Amplitude', fontsize=8)
        self.canvas.draw()

class TTSConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Text-to-Speech Narrator")
        self.root.geometry("1000x900")
        
        # Soft Gold & Brown Color Palette
        self.colors = {
            'background': '#F5E6D3',      # Warm beige
            'text_area_bg': '#E6D5C1',    # Soft light brown
            'button_bg': '#5D4037',       # Dark brown
            'button_text': '#3E2723',     # Very dark brown
            'accent': '#8D6E63'           # Soft brown accent
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['background'])
        self.root.option_add('*Font', 'Caveat 14')  # Handwritten-style font

        # Create main frame
        self.main_frame = tk.Frame(self.root, bg=self.colors['background'])
        self.main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Title
        title_font = tkfont.Font(family='Caveat', size=24, weight='bold')
        self.title_label = tk.Label(self.main_frame, 
                                    text="Audiobook Narrator", 
                                    font=title_font, 
                                    bg=self.colors['background'], 
                                    fg=self.colors['accent'])
        self.title_label.pack(pady=(0, 20))

        # Waveform Visualizer
        self.waveform_visualizer = WaveformVisualizer(self.main_frame)

        # Text Area
        text_frame = tk.Frame(self.main_frame, bg=self.colors['background'])
        text_frame.pack(fill=tk.X, pady=10)

        text_label = tk.Label(text_frame, text="Enter Your Text:", 
                              bg=self.colors['background'], 
                              fg=self.colors['accent'])
        text_label.pack(anchor='w')

        text_area_frame = tk.Frame(text_frame, bg=self.colors['background'])
        text_area_frame.pack(fill=tk.X)

        self.text_area = tk.Text(text_area_frame, 
                                  height=10, 
                                  width=80, 
                                  bg=self.colors['text_area_bg'], 
                                  fg='black', 
                                  font=('Caveat', 14), 
                                  wrap=tk.WORD, 
                                  insertbackground=self.colors['accent'],
                                  borderwidth=2,
                                  relief=tk.GROOVE)
        self.text_area.pack(side=tk.LEFT, expand=True, fill=tk.X)

        scrollbar = tk.Scrollbar(text_area_frame, 
                                 command=self.text_area.yview,
                                 bg=self.colors['accent'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scrollbar.set)

        # Controls Frame
        controls_frame = tk.Frame(self.main_frame, bg=self.colors['background'])
        controls_frame.pack(fill=tk.X, pady=10)

        # Voice Selection
        voice_frame = tk.Frame(controls_frame, bg=self.colors['background'])
        voice_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(voice_frame, text="Voice:", 
                 bg=self.colors['background'], 
                 fg=self.colors['accent']).pack()
        
        # Enhanced Voice Selection
        self.voice_var = tk.StringVar(value="male")
        voices = ["male", "female", "robotic"]
        
        self.voice_dropdown = ttk.Combobox(voice_frame, 
                                           textvariable=self.voice_var, 
                                           values=voices, 
                                           state="readonly", 
                                           width=15,
                                           style='Custom.TCombobox')
        self.voice_dropdown.pack()
        self.voice_dropdown.bind('<<ComboboxSelected>>', self.update_voice)

        # Speed Slider
        speed_frame = tk.Frame(controls_frame, bg=self.colors['background'])
        speed_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(speed_frame, text="Speed:", 
                 bg=self.colors['background'], 
                 fg=self.colors['accent']).pack()
        self.speed_var = tk.IntVar(value=150)
        self.speed_slider = tk.Scale(speed_frame, 
                                     from_=50, to=250, 
                                     orient=tk.HORIZONTAL, 
                                     variable=self.speed_var, 
                                     length=150, 
                                     bg=self.colors['background'], 
                                     fg=self.colors['accent'], 
                                     troughcolor=self.colors['text_area_bg'],
                                     resolution=10,
                                     label='Words per Minute')
        self.speed_slider.pack()

        # Pitch Slider
        pitch_frame = tk.Frame(controls_frame, bg=self.colors['background'])
        pitch_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(pitch_frame, text="Pitch:", 
                 bg=self.colors['background'], 
                 fg=self.colors['accent']).pack()
        self.pitch_var = tk.IntVar(value=0)
        self.pitch_slider = tk.Scale(pitch_frame, 
                                     from_=-10, to=10, 
                                     orient=tk.HORIZONTAL, 
                                     variable=self.pitch_var, 
                                     length=150, 
                                     bg=self.colors['background'], 
                                     fg=self.colors['accent'], 
                                     troughcolor=self.colors['text_area_bg'],
                                     resolution=1,
                                     label='Pitch Shift')
        self.pitch_slider.pack()

        # Buttons Frame
        buttons_frame = tk.Frame(self.main_frame, bg=self.colors['background'])
        buttons_frame.pack(fill=tk.X, pady=20)

        # Button Style
        button_style = {
            'font': ('Caveat', 14, 'bold'),
            'bg': self.colors['button_bg'],
            'fg': self.colors['button_text'],
            'activebackground': self.colors['accent'],
            'activeforeground': 'black',
            'relief': tk.GROOVE,
            'borderwidth': 3
        }

        # Play Button
        self.play_button = tk.Button(buttons_frame, text="Play", 
                                     command=self.play_text, 
                                     **button_style)
        self.play_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # Save Button
        self.save_button = tk.Button(buttons_frame, text="Save MP3", 
                                     command=self.save_text, 
                                     **button_style)
        self.save_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # Close Button
        self.close_button = tk.Button(buttons_frame, text="Close", 
                                     command=self.close_app, 
                                     **button_style)
        self.close_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # Reset Button
        self.reset_button = tk.Button(buttons_frame, text="Reset", 
                                     command=self.reset_app, 
                                     **button_style)
        self.reset_button.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        # Status Bar
        self.status_var = tk.StringVar(value="Ready to Narrate")
        self.status_bar = tk.Label(self.main_frame, 
                                   textvariable=self.status_var, 
                                   bd=1, 
                                   relief=tk.SUNKEN, 
                                   anchor=tk.W, 
                                   bg=self.colors['text_area_bg'], 
                                   fg=self.colors['accent'])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        # Disable buttons initially
        self.update_button_states()

    def update_voice(self, event=None):
        """Update TTS engine voice"""
        selected_voice = self.voice_var.get()

    def play_text(self):
        try:
            text = self.text_area.get("1.0", tk.END).strip()
            
            if not text:
                messagebox.showwarning("Warning", "Please enter some text to convert.")
                return

            # Prepare audio file
            temp_audio_file = "temp.mp3"
            
            # Use gTTS to convert text to speech
            tts = gTTS(text=text, lang='en')
            tts.save(temp_audio_file)  # Save to a temporary file

            # Read audio for waveform visualization
            audio_data, _ = sf.read(temp_audio_file)
            self.waveform_visualizer.update_waveform(audio_data)

            # Play audio
            pygame.mixer.music.load(temp_audio_file)
            pygame.mixer.music.play()

            # Update status
            self.status_var.set(f"Playing text...")

        except Exception as e:
            self.show_error(f"Playback error: {str(e)}")

    def close_app(self):
        self.root.quit()

    def reset_app(self):
        self.text_area.delete('1.0', tk.END)
        self.status_var.set("Ready to Narrate")
        self.update_button_states()

    def save_text(self):
        try:
            text = self.text_area.get("1.0", tk.END).strip()
            
            if not text:
                messagebox.showwarning("Warning", "Please enter some text to save.")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".mp3",
                filetypes=[("MP3 files", "*.mp3"), ("WAV files", "*.wav"), ("All files", "*.*")]
            )

            if not file_path:
                return

            # Use gTTS to convert text to speech
            tts = gTTS(text=text, lang='en')
            tts.save(file_path)  # Save as MP3 file

            messagebox.showinfo("Success", f"Audio saved to {file_path}")
            self.status_var.set(f"Audio saved to {os.path.basename(file_path)}")

        except Exception as e:
            self.show_error(f"Error saving audio: {str(e)}")

    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.status_var.set("Error occurred")

    def update_button_states(self):
        text_content = self.text_area.get("1.0", tk.END).strip()
        state = tk.NORMAL if text_content else tk.DISABLED
        
        self.play_button.config(state=state)
        self.save_button.config(state=state)

    def on_text_change(self, event=None):
        self.update_button_states()

# Main application setup
root = tk.Tk()
app = TTSConverter(root)
app.text_area.bind('<KeyRelease>', app.on_text_change)
root.protocol("WM_DELETE_WINDOW", root.quit)
root.mainloop()