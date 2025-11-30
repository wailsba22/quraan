"""
Standalone Android APK Builder using Kivy
This will create a native Android app that runs without a server
"""

# Install required packages first:
# pip install kivy kivymd buildozer

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.clock import Clock
import threading
from quran_video_generator import QuranVideoGenerator

class RandomScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        layout.add_widget(Label(text='Random Video Generation', size_hint_y=0.1, font_size=24))
        
        # Count input
        layout.add_widget(Label(text='Number of Videos:', size_hint_y=0.08))
        self.count_input = TextInput(text='1', multiline=False, size_hint_y=0.1)
        layout.add_widget(self.count_input)
        
        # Language selector
        layout.add_widget(Label(text='Second Language:', size_hint_y=0.08))
        self.language_spinner = Spinner(
            text='English',
            values=('English', 'French', 'Urdu', 'Turkish', 'Indonesian', 'Bengali', 'Spanish', 'Russian', 'German', 'Chinese'),
            size_hint_y=0.1
        )
        layout.add_widget(self.language_spinner)
        
        # Generate button
        self.gen_btn = Button(text='Generate Videos', size_hint_y=0.12)
        self.gen_btn.bind(on_press=self.generate)
        layout.add_widget(self.gen_btn)
        
        # Progress bar
        self.progress = ProgressBar(max=100, size_hint_y=0.1)
        layout.add_widget(self.progress)
        
        # Status label
        self.status_label = Label(text='Ready', size_hint_y=0.1)
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
        
    def generate(self, instance):
        self.gen_btn.disabled = True
        self.status_label.text = 'Generating...'
        
        lang_map = {
            'English': 'en', 'French': 'fr', 'Urdu': 'ur',
            'Turkish': 'tr', 'Indonesian': 'id', 'Bengali': 'bn',
            'Spanish': 'es', 'Russian': 'ru', 'German': 'de', 'Chinese': 'zh'
        }
        
        count = int(self.count_input.text)
        lang = lang_map[self.language_spinner.text]
        
        # Run in thread
        thread = threading.Thread(target=self.generate_worker, args=(count, lang))
        thread.start()
    
    def generate_worker(self, count, lang):
        try:
            from android.storage import primary_external_storage_path
            output_dir = primary_external_storage_path() + '/QuranVideos'
        except:
            output_dir = 'output'
        
        generator = QuranVideoGenerator(output_dir=output_dir, background_videos_dir='backgrounds')
        generator.subtitle_languages = ['ar', lang]
        
        for i in range(count):
            def update_progress(progress):
                Clock.schedule_once(lambda dt: setattr(self.progress, 'value', ((i + progress/100) / count) * 100))
            
            generator.generate_random_video(progress_callback=update_progress)
        
        Clock.schedule_once(lambda dt: self.on_complete())
    
    def on_complete(self):
        self.status_label.text = 'Complete!'
        self.gen_btn.disabled = False
        self.progress.value = 100

class CustomScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text='Custom Video Generation', size_hint_y=0.1, font_size=24))
        
        # Surah input
        layout.add_widget(Label(text='Surah (1-114):', size_hint_y=0.08))
        self.surah_input = TextInput(text='1', multiline=False, size_hint_y=0.1)
        layout.add_widget(self.surah_input)
        
        # Ayah inputs
        row = BoxLayout(size_hint_y=0.15)
        col1 = BoxLayout(orientation='vertical')
        col1.add_widget(Label(text='Start Ayah:'))
        self.ayah_start = TextInput(text='1', multiline=False)
        col1.add_widget(self.ayah_start)
        
        col2 = BoxLayout(orientation='vertical')
        col2.add_widget(Label(text='End Ayah:'))
        self.ayah_end = TextInput(text='7', multiline=False)
        col2.add_widget(self.ayah_end)
        
        row.add_widget(col1)
        row.add_widget(col2)
        layout.add_widget(row)
        
        # Reciter
        layout.add_widget(Label(text='Reciter:', size_hint_y=0.08))
        self.reciter_spinner = Spinner(
            text='Mishary Alafasy',
            values=('Mishary Alafasy', 'Abdul Basit', 'Al-Minshawi', 'Al-Hussary', 'Al-Shatri'),
            size_hint_y=0.1
        )
        layout.add_widget(self.reciter_spinner)
        
        # Generate button
        self.gen_btn = Button(text='Generate Video', size_hint_y=0.12)
        self.gen_btn.bind(on_press=self.generate)
        layout.add_widget(self.gen_btn)
        
        # Progress
        self.progress = ProgressBar(max=100, size_hint_y=0.1)
        layout.add_widget(self.progress)
        
        self.status_label = Label(text='Ready', size_hint_y=0.1)
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def generate(self, instance):
        self.gen_btn.disabled = True
        self.status_label.text = 'Generating...'
        
        reciter_map = {
            'Mishary Alafasy': 'ar.alafasy',
            'Abdul Basit': 'ar.abdulbasitmurattal',
            'Al-Minshawi': 'ar.minshawi',
            'Al-Hussary': 'ar.husary',
            'Al-Shatri': 'ar.shaatree'
        }
        
        surah = int(self.surah_input.text)
        ayah_start = int(self.ayah_start.text)
        ayah_end = int(self.ayah_end.text)
        reciter = reciter_map[self.reciter_spinner.text]
        
        thread = threading.Thread(target=self.generate_worker, args=(surah, ayah_start, ayah_end, reciter))
        thread.start()
    
    def generate_worker(self, surah, ayah_start, ayah_end, reciter):
        try:
            from android.storage import primary_external_storage_path
            output_dir = primary_external_storage_path() + '/QuranVideos'
        except:
            output_dir = 'output'
        
        generator = QuranVideoGenerator(output_dir=output_dir, background_videos_dir='backgrounds')
        
        def update_progress(progress):
            Clock.schedule_once(lambda dt: setattr(self.progress, 'value', progress))
        
        generator.generate_video(surah, ayah_start, ayah_end, reciter, progress_callback=update_progress)
        Clock.schedule_once(lambda dt: self.on_complete())
    
    def on_complete(self):
        self.status_label.text = 'Complete!'
        self.gen_btn.disabled = False
        self.progress.value = 100

class QuranVideoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(RandomScreen(name='random'))
        sm.add_widget(CustomScreen(name='custom'))
        return sm

if __name__ == '__main__':
    QuranVideoApp().run()
