"""
Fast Quran Video Generator with Automatic Transcription
Generates videos with Arabic text and audio synchronized
"""

import os
import json
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
import requests
from PIL import Image, ImageDraw, ImageFont
import tempfile
import random
import sys

# Windows-specific: Hide console windows for subprocess calls
if sys.platform == 'win32':
    import subprocess
    # CREATE_NO_WINDOW flag for Windows
    SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW
else:
    SUBPROCESS_FLAGS = 0


class QuranVideoGenerator:
    def __init__(self, output_dir: str = "output", background_videos_dir: str = "backgrounds"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.background_videos_dir = Path(background_videos_dir)
        # Don't auto-create background folder - let user set it up
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Find FFmpeg executable
        self.ffmpeg_path = self._find_ffmpeg()
        
        # Progress callback (set by GUI for live updates and cancellation)
        self.progress_callback = None
        
        # Quality settings (can be modified by GUI)
        self.quality_preset = "medium"  # FFmpeg encoding preset
        self.quality_crf = "32"  # CRF value (lower = better quality)
        self.audio_bitrate = "96k"  # Audio bitrate
        self.target_duration = 90  # Target video length in seconds
        self.max_duration = 100  # Hard limit for video length
        
        # Language settings (can be modified by GUI)
        self.subtitle_languages = ["ar", "en"]  # Default: Arabic + English
        
        # Available reciters (more options)
        self.reciters = [
            "ar.alafasy",           # Mishary Alafasy
            "ar.abdulbasitmurattal", # Abdul Basit
            "ar.minshawi",          # Al-Minshawi
            "ar.husary",            # Al-Husary
            "ar.shaatree",          # Ash-Shaatree
            "ar.abdurrahmaansudais", # Abdurrahman As-Sudais
            "ar.mahermuaiqly",      # Maher Al-Muaiqly
            "ar.muhammadayyoub",    # Muhammad Ayyub
            "ar.saadalghaamidi"     # Saad Al-Ghamadi
        ]
        
        # Surah info: (surah_number, total_ayahs)
        self.surahs = [
            (1, 7), (2, 286), (3, 200), (4, 176), (5, 120), (6, 165), (7, 206),
            (8, 75), (9, 129), (10, 109), (11, 123), (12, 111), (13, 43), (14, 52),
            (15, 99), (16, 128), (17, 111), (18, 110), (19, 98), (20, 135), (21, 112),
            (22, 78), (23, 118), (24, 64), (25, 77), (26, 227), (27, 93), (28, 88),
            (29, 69), (30, 60), (31, 34), (32, 30), (33, 73), (34, 54), (35, 45),
            (36, 83), (37, 182), (38, 88), (39, 75), (40, 85), (41, 54), (42, 53),
            (43, 89), (44, 59), (45, 37), (46, 35), (47, 38), (48, 29), (49, 18),
            (50, 45), (51, 60), (52, 49), (53, 62), (54, 55), (55, 78), (56, 96),
            (57, 29), (58, 22), (59, 24), (60, 13), (61, 14), (62, 11), (63, 11),
            (64, 18), (65, 12), (66, 12), (67, 30), (68, 52), (69, 52), (70, 44),
            (71, 28), (72, 28), (73, 20), (74, 56), (75, 40), (76, 31), (77, 50),
            (78, 40), (79, 46), (80, 42), (81, 29), (82, 19), (83, 36), (84, 25),
            (85, 22), (86, 17), (87, 19), (88, 26), (89, 30), (90, 20), (91, 15),
            (92, 21), (93, 11), (94, 8), (95, 8), (96, 19), (97, 5), (98, 8),
            (99, 8), (100, 11), (101, 11), (102, 8), (103, 3), (104, 9), (105, 5),
            (106, 4), (107, 7), (108, 3), (109, 6), (110, 3), (111, 5), (112, 4),
            (113, 5), (114, 6)
        ]
        
        # Surah names in English
        self.surah_names = {
            1: "Al-Fatiha", 2: "Al-Baqarah", 3: "Aal-E-Imran", 4: "An-Nisa",
            5: "Al-Maidah", 6: "Al-Anam", 7: "Al-Araf", 8: "Al-Anfal",
            9: "At-Tawbah", 10: "Yunus", 11: "Hud", 12: "Yusuf",
            13: "Ar-Rad", 14: "Ibrahim", 15: "Al-Hijr", 16: "An-Nahl",
            17: "Al-Isra", 18: "Al-Kahf", 19: "Maryam", 20: "Ta-Ha",
            21: "Al-Anbiya", 22: "Al-Hajj", 23: "Al-Muminun", 24: "An-Nur",
            25: "Al-Furqan", 26: "Ash-Shuara", 27: "An-Naml", 28: "Al-Qasas",
            29: "Al-Ankabut", 30: "Ar-Rum", 31: "Luqman", 32: "As-Sajdah",
            33: "Al-Ahzab", 34: "Saba", 35: "Fatir", 36: "Ya-Sin",
            37: "As-Saffat", 38: "Sad", 39: "Az-Zumar", 40: "Ghafir",
            41: "Fussilat", 42: "Ash-Shura", 43: "Az-Zukhruf", 44: "Ad-Dukhan",
            45: "Al-Jathiyah", 46: "Al-Ahqaf", 47: "Muhammad", 48: "Al-Fath",
            49: "Al-Hujurat", 50: "Qaf", 51: "Adh-Dhariyat", 52: "At-Tur",
            53: "An-Najm", 54: "Al-Qamar", 55: "Ar-Rahman", 56: "Al-Waqiah",
            57: "Al-Hadid", 58: "Al-Mujadila", 59: "Al-Hashr", 60: "Al-Mumtahanah",
            61: "As-Saff", 62: "Al-Jumuah", 63: "Al-Munafiqun", 64: "At-Taghabun",
            65: "At-Talaq", 66: "At-Tahrim", 67: "Al-Mulk", 68: "Al-Qalam",
            69: "Al-Haqqah", 70: "Al-Maarij", 71: "Nuh", 72: "Al-Jinn",
            73: "Al-Muzzammil", 74: "Al-Muddaththir", 75: "Al-Qiyamah", 76: "Al-Insan",
            77: "Al-Mursalat", 78: "An-Naba", 79: "An-Naziat", 80: "Abasa",
            81: "At-Takwir", 82: "Al-Infitar", 83: "Al-Mutaffifin", 84: "Al-Inshiqaq",
            85: "Al-Buruj", 86: "At-Tariq", 87: "Al-Ala", 88: "Al-Ghashiyah",
            89: "Al-Fajr", 90: "Al-Balad", 91: "Ash-Shams", 92: "Al-Layl",
            93: "Ad-Duha", 94: "Ash-Sharh", 95: "At-Tin", 96: "Al-Alaq",
            97: "Al-Qadr", 98: "Al-Bayyinah", 99: "Az-Zalzalah", 100: "Al-Adiyat",
            101: "Al-Qariah", 102: "At-Takathur", 103: "Al-Asr", 104: "Al-Humazah",
            105: "Al-Fil", 106: "Quraysh", 107: "Al-Maun", 108: "Al-Kawthar",
            109: "Al-Kafirun", 110: "An-Nasr", 111: "Al-Masad", 112: "Al-Ikhlas",
            113: "Al-Falaq", 114: "An-Nas"
        }
    
    def _find_ffmpeg(self) -> str:
        """Find FFmpeg executable in various locations"""
        # Check if running as PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running as compiled EXE
            base_path = Path(sys.executable).parent
        else:
            # Running as script
            base_path = Path(__file__).parent
        
        # Possible FFmpeg locations
        possible_paths = [
            base_path / "ffmpeg" / "bin" / "ffmpeg.exe",
            base_path / "ffmpeg.exe",
            Path("ffmpeg") / "bin" / "ffmpeg.exe",
            Path("ffmpeg.exe"),
        ]
        
        # Check file system paths
        for path in possible_paths:
            if path.exists():
                print(f"✓ Found FFmpeg at: {path}")
                return str(path.resolve())
        
        # Try system PATH
        try:
            result = subprocess.run(["ffmpeg", "-version"], 
                                  capture_output=True, 
                                  creationflags=SUBPROCESS_FLAGS if sys.platform == 'win32' else 0)
            if result.returncode == 0:
                print("✓ Found FFmpeg in system PATH")
                return "ffmpeg"
        except:
            pass
        
        # Last resort - check in common Windows locations
        common_locations = [
            Path(r"C:\ffmpeg\bin\ffmpeg.exe"),
            Path(r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"),
        ]
        for path in common_locations:
            if path.exists():
                print(f"✓ Found FFmpeg at: {path}")
                return str(path.resolve())
        
        print("⚠️ FFmpeg not found! Please ensure ffmpeg.exe is in the same folder as the app.")
        raise FileNotFoundError("FFmpeg executable not found. Please install FFmpeg or place it in the 'ffmpeg/bin/' folder.")
    
    def _get_ffprobe_path(self) -> str:
        """Get ffprobe path based on ffmpeg path"""
        ffmpeg_path = Path(self.ffmpeg_path)
        
        # If ffmpeg is in a bin folder, ffprobe should be there too
        if ffmpeg_path.name == "ffmpeg.exe":
            ffprobe = ffmpeg_path.parent / "ffprobe.exe"
            if ffprobe.exists():
                return str(ffprobe)
        elif ffmpeg_path.name == "ffmpeg":
            # Unix-style or in PATH
            return "ffprobe"
        
        # Fallback: try to replace name
        return str(ffmpeg_path).replace("ffmpeg.exe", "ffprobe.exe").replace("ffmpeg", "ffprobe")
        
    def get_ayah_data(self, surah: int, ayah_start: int, ayah_end: int, reciter: str = "ar.alafasy") -> List[dict]:
        """
        Fetch ayah text (Arabic + translation) and audio from Quran API
        Uses the configured second language from subtitle_languages
        """
        # Get translation edition code from subtitle_languages
        # subtitle_languages[0] is always 'ar', [1] is the second language
        second_lang = self.subtitle_languages[1] if len(self.subtitle_languages) > 1 else "en"
        
        # Map language codes to API edition identifiers
        translation_map = {
            "en": "en.sahih",
            "fr": "fr.hamidullah",
            "ur": "ur.jalandhry",
            "tr": "tr.diyanet",
            "id": "id.indonesian",
            "bn": "bn.bengali",
            "es": "es.cortes",
            "ru": "ru.kuliev",
            "de": "de.bubenheim",
            "zh": "zh.jian"
        }
        
        translation_edition = translation_map.get(second_lang, "en.sahih")
        
        ayahs = []
        for ayah_num in range(ayah_start, ayah_end + 1):
            # Get Arabic text and translation
            combined_url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah_num}/editions/{reciter},{translation_edition}"
            response = requests.get(combined_url)
            data = response.json()
            
            if data['code'] == 200:
                arabic_data = data['data'][0]  # Audio + Arabic
                translation_data = data['data'][1]  # Translation in selected language
                
                # Check if audio URL exists (some reciters might not have all ayahs)
                if 'audio' not in arabic_data or not arabic_data['audio']:
                    print(f"⚠️  Surah {surah}:{ayah_num} - No audio available for this reciter")
                    continue
                
                ayahs.append({
                    'number': ayah_num,
                    'arabic': arabic_data['text'],
                    'translation': translation_data['text'],
                    'audio_url': arabic_data['audio'],
                    'surah': surah
                })
                print(f"✓ Fetched Surah {surah}:{ayah_num}")
        
        return ayahs
    
    def download_audio(self, ayahs: List[dict], max_duration: float = 95.0) -> Tuple[List[str], int]:
        """
        Download audio files for each ayah
        Stops early if total duration approaches max_duration to avoid waste
        """
        # Ensure temp directory exists (in case it was cleaned up)
        if not self.temp_dir.exists():
            self.temp_dir = Path(tempfile.mkdtemp())
        
        audio_files = []
        total_duration = 0.0
        ayahs_used = 0
        
        for i, ayah in enumerate(ayahs):
            audio_path = self.temp_dir / f"audio_{i}.mp3"
            response = requests.get(ayah['audio_url'])
            audio_path.write_bytes(response.content)
            
            # Check duration of this audio file
            result = subprocess.run(
                [self._get_ffprobe_path(), '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)],
                capture_output=True, text=True, creationflags=SUBPROCESS_FLAGS
            )
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                total_duration += duration
                
                # Stop if adding this would exceed our limit
                if total_duration > max_duration and i > 0:
                    print(f"⚠️  Reached {total_duration:.1f}s (max: {max_duration:.1f}s)")
                    print(f"   Stopping at ayah {i}/{len(ayahs)} to avoid waste")
                    # Remove the last file we just downloaded since it puts us over
                    audio_path.unlink()
                    break
                
                audio_files.append(str(audio_path))
                ayahs_used = i + 1
                print(f"✓ Downloaded audio {i+1}/{len(ayahs)} ({duration:.1f}s, total: {total_duration:.1f}s)")
            else:
                # If we can't get duration, just add it
                audio_files.append(str(audio_path))
                ayahs_used = i + 1
                print(f"✓ Downloaded audio {i+1}/{len(ayahs)}")
        
        # Return both audio files and the actual number of ayahs used
        # Update the ayahs list to match what we actually downloaded
        return audio_files, ayahs_used
    
    def create_subtitle_file(self, ayahs: List[dict], audio_files: List[str]) -> str:
        """Create ASS subtitle file with Arabic text"""
        # Ensure temp directory exists (in case it was cleaned up)
        if not self.temp_dir.exists():
            self.temp_dir = Path(tempfile.mkdtemp())
        
        # Get audio durations
        durations = []
        for audio_file in audio_files:
            result = subprocess.run(
                [self._get_ffprobe_path(), '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', audio_file],
                capture_output=True, text=True, creationflags=SUBPROCESS_FLAGS
            )
            if result.returncode != 0:
                print(f"Warning: Could not get duration for {audio_file}")
                durations.append(5.0)  # Default fallback
            else:
                durations.append(float(result.stdout.strip()))
        
        # Create ASS subtitle content with Arabic (center) and English (bottom)
        ass_content = """[Script Info]
Title: Quran Subtitles
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Arabic,Arial,8,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,5,120,120,450,1
Style: English,Arial,6,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,120,120,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        # Create ASS subtitle content with Arabic (center) and English (bottom)
        ass_content = """[Script Info]
Title: Quran Subtitles
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Arabic,Arial,8,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,5,80,80,450,1
Style: English,Arial,6,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,80,80,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        current_time = 0
        for i, (ayah, duration) in enumerate(zip(ayahs, durations)):
            start_time = self._format_time(current_time)
            end_time = self._format_time(current_time + duration)
            
            # Clean texts
            arabic_text = ayah['arabic'].replace('\n', ' ').strip()
            translation_text = ayah.get('translation', ayah.get('english', '')).replace('\n', ' ').strip()
            
            # Split long text into chunks (max 2 lines worth of words)
            arabic_chunks = self._split_text_smart(arabic_text, max_chars_per_line=25, max_lines=2)
            translation_chunks = self._split_text_smart(translation_text, max_chars_per_line=30, max_lines=2)
            
            # Calculate time per chunk
            chunk_count = max(len(arabic_chunks), len(translation_chunks))
            chunk_duration = duration / chunk_count if chunk_count > 0 else duration
            
            # Create dialogue for each chunk
            for chunk_idx in range(chunk_count):
                chunk_start = current_time + (chunk_idx * chunk_duration)
                chunk_end = chunk_start + chunk_duration
                
                chunk_start_time = self._format_time(chunk_start)
                chunk_end_time = self._format_time(chunk_end)
                
                # Get text chunk (or empty if this chunk doesn't exist)
                arabic_chunk = arabic_chunks[chunk_idx] if chunk_idx < len(arabic_chunks) else ""
                translation_chunk = translation_chunks[chunk_idx] if chunk_idx < len(translation_chunks) else ""
                
                if arabic_chunk:
                    ass_content += f"Dialogue: 0,{chunk_start_time},{chunk_end_time},Arabic,,0,0,0,,{arabic_chunk}\n"
                if translation_chunk:
                    ass_content += f"Dialogue: 0,{chunk_start_time},{chunk_end_time},English,,0,0,0,,{translation_chunk}\n"
            
            current_time += duration
        
        subtitle_path = self.temp_dir / "subtitles.ass"
        subtitle_path.write_text(ass_content, encoding='utf-8')
        return str(subtitle_path)
    
    def _split_text_smart(self, text: str, max_chars_per_line: int = 40, max_lines: int = 2) -> List[str]:
        """
        Split text into chunks that fit within max_lines, breaking at word boundaries
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        current_lines = 1
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            potential_length = current_length + word_length
            
            # Check if adding this word exceeds line length
            if potential_length > max_chars_per_line:
                current_lines += 1
                current_length = word_length
                
                # If we've exceeded max lines, start a new chunk
                if current_lines > max_lines:
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                    current_chunk = [word]
                    current_lines = 1
                    current_length = word_length
                else:
                    current_chunk.append(word)
            else:
                current_chunk.append(word)
                current_length += word_length
        
        # Add remaining words
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks if chunks else [text]
    
    def _format_time(self, seconds: float) -> str:
        """Convert seconds to ASS time format (H:MM:SS.CS)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"
    
    def merge_audio_files(self, audio_files: List[str]) -> str:
        """Merge multiple audio files into one"""
        # Ensure temp directory exists (in case it was cleaned up)
        if not self.temp_dir.exists():
            self.temp_dir = Path(tempfile.mkdtemp())
        
        concat_file = self.temp_dir / "concat.txt"
        with open(concat_file, 'w') as f:
            for audio_file in audio_files:
                # Use forward slashes for FFmpeg on Windows
                audio_file_unix = audio_file.replace('\\', '/')
                f.write(f"file '{audio_file_unix}'\n")
        
        merged_audio = self.temp_dir / "merged_audio.mp3"
        
        try:
            subprocess.run([
                self.ffmpeg_path, '-f', 'concat', '-safe', '0', '-i', str(concat_file),
                '-c', 'copy', str(merged_audio), '-y'
            ], check=True, capture_output=True, text=True, creationflags=SUBPROCESS_FLAGS)
        except subprocess.CalledProcessError as e:
            print(f"Error merging audio: {e.stderr}")
            raise
        
        print("✓ Merged audio files")
        return str(merged_audio)
    
    def get_random_background_video(self) -> Optional[str]:
        """Get a random video from background_videos folder"""
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(self.background_videos_dir.glob(f'*{ext}'))
        
        if video_files:
            selected = random.choice(video_files)
            print(f"✓ Selected background video: {selected.name}")
            return str(selected)
        return None
    
    def get_video_duration(self, video_path: str) -> float:
        """Get duration of a video file"""
        result = subprocess.run(
            [self._get_ffprobe_path(), '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
            capture_output=True, text=True, creationflags=SUBPROCESS_FLAGS
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
        return 0
    
    def calculate_ayahs_for_duration(self, target_duration: float) -> Tuple[int, int, int]:
        """Calculate which ayahs to use based on target video duration"""
        # Target around 90 seconds with hard 100s cap
        # Be conservative to avoid downloading verses we'll discard
        target = 85.0  # Aim for 85s to stay safely under 100s cap
        
        # Randomly select a surah
        surah_num, total_ayahs = random.choice(self.surahs)
        
        # Start from a random ayah
        max_start = max(1, total_ayahs - 4)  # Leave room for at least a few ayahs
        ayah_start = random.randint(1, max_start)
        
        # Estimate: average 6-7 seconds per ayah (more conservative)
        # Start with fewer ayahs to avoid waste from 100s cap
        estimated_ayahs = int(target / 7)  # Aim for ~12 ayahs (~84s), safer estimate
        estimated_ayahs = max(3, min(estimated_ayahs, 14))  # Cap at 14 instead of 17
        
        ayah_end = min(ayah_start + estimated_ayahs - 1, total_ayahs)
        
        return surah_num, ayah_start, ayah_end
    
    def create_background_video(self, duration: float, width: int = 1080, height: int = 1920) -> str:
        """Create a simple gradient background video (9:16 ratio)"""
        bg_video = self.temp_dir / "background.mp4"
        
        # Create solid color background (green Islamic color)
        try:
            subprocess.run([
                self.ffmpeg_path, '-f', 'lavfi', '-i', f'color=c=#0F5132:s={width}x{height}:d={duration}',
                '-pix_fmt', 'yuv420p', str(bg_video), '-y'
            ], check=True, capture_output=True, text=True, creationflags=SUBPROCESS_FLAGS)
        except subprocess.CalledProcessError as e:
            print(f"Error creating background: {e.stderr}")
            raise
        
        print("✓ Created background video")
        return str(bg_video)
    
    def resize_video_to_portrait(self, input_video: str, target_duration: float) -> str:
        """Resize and loop video to 9:16 portrait format"""
        output_video = self.temp_dir / "resized_background.mp4"
        
        try:
            subprocess.run([
                self.ffmpeg_path,
                '-stream_loop', '-1',  # Loop video
                '-i', input_video,
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
                '-t', str(target_duration),
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-an',  # Remove audio from background
                str(output_video),
                '-y'
            ], check=True, capture_output=True, text=True, creationflags=SUBPROCESS_FLAGS)
        except subprocess.CalledProcessError as e:
            print(f"Error resizing video: {e.stderr}")
            raise
        
        print("✓ Resized background to 9:16")
        return str(output_video)
    
    def generate_random_video(self, output_filename: Optional[str] = None) -> str:
        """
        Generate video with random background, random surah, and random reciter
        Matches content length to background video duration
        
        Returns:
            Path to the generated video file
        """
        print("\n🎬 Starting RANDOM video generation\n")
        
        # Step 1: Get random background video
        print("🎥 Selecting random background video...")
        background_video = self.get_random_background_video()
        
        if not background_video:
            print("⚠️  No videos found in background_videos folder!")
            print("   Creating default background...")
            target_duration = 30.0  # Default 30 seconds
            background = self.create_background_video(target_duration)
        else:
            # Get video duration
            video_duration = self.get_video_duration(background_video)
            target_duration = video_duration
            print(f"✓ Background duration: {video_duration:.1f}s")
        
        # Step 2: Calculate which ayahs to use
        print("\n📖 Calculating random Quran selection...")
        surah, ayah_start, ayah_end = self.calculate_ayahs_for_duration(target_duration)
        
        # Step 3: Select random reciter
        reciter = random.choice(self.reciters)
        reciter_names = {
            "ar.alafasy": "Mishary Alafasy",
            "ar.abdulbasitmurattal": "Abdul Basit",
            "ar.minshawi": "Al-Minshawi",
            "ar.husary": "Al-Husary",
            "ar.shaatree": "Ash-Shaatree"
        }
        print(f"✓ Surah: {surah}, Ayah: {ayah_start}-{ayah_end}")
        print(f"✓ Reciter: {reciter_names.get(reciter, reciter)}")
        
        # Step 4: Get ayah data
        print("\n📖 Fetching Quran data...")
        ayahs = self.get_ayah_data(surah, ayah_start, ayah_end, reciter)
        
        # Continue with normal generation...
        return self._generate_video_internal(
            ayahs=ayahs,
            surah=surah,
            ayah_start=ayah_start,
            ayah_end=ayah_end,
            reciter=reciter,
            background_video=background_video if background_video else None,
            target_duration=target_duration,
            output_filename=output_filename
        )
    
    def generate_video(
        self, 
        surah: int, 
        ayah_start: int, 
        ayah_end: int,
        reciter: str = "ar.alafasy",
        output_filename: Optional[str] = None
    ) -> str:
        """
        Main function to generate the complete video
        
        Args:
            surah: Surah number (1-114)
            ayah_start: Starting ayah number
            ayah_end: Ending ayah number
            reciter: Reciter identifier
            output_filename: Custom output filename (optional)
        
        Returns:
            Path to the generated video file
        """
        print(f"\n🎬 Starting video generation for Surah {surah}, Ayah {ayah_start}-{ayah_end}\n")
        
        # Step 1: Get ayah data
        print("📖 Fetching Quran data...")
        ayahs = self.get_ayah_data(surah, ayah_start, ayah_end, reciter)
        
        return self._generate_video_internal(
            ayahs=ayahs,
            surah=surah,
            ayah_start=ayah_start,
            ayah_end=ayah_end,
            reciter=reciter,
            background_video=None,
            target_duration=None,
            output_filename=output_filename
        )
    
    def _generate_video_internal(
        self,
        ayahs: List[dict],
        surah: int,
        ayah_start: int,
        ayah_end: int,
        reciter: str,
        background_video: Optional[str],
        target_duration: Optional[float],
        output_filename: Optional[str]
    ) -> str:
        """Internal method to generate video with given parameters"""
        
        # Check for cancellation
        if self.progress_callback and not self.progress_callback(5):
            raise Exception("Cancelled by user")
        
        # Get reciter short name for filename
        reciter_short_names = {
            "ar.alafasy": "Alafasy",
            "ar.abdulbasitmurattal": "AbdulBasit",
            "ar.minshawi": "Minshawi",
            "ar.husary": "Husary",
            "ar.shaatree": "Shaatree"
        }
        reciter_name = reciter_short_names.get(reciter, reciter.replace('ar.', ''))
        
        # Step 2: Download audio (with smart duration checking)
        print("\n🎵 Downloading audio files...")
        if self.progress_callback and not self.progress_callback(10):
            raise Exception("Cancelled by user")
        
        # Use 95% of max_duration as buffer to avoid downloads that get cut
        max_dl_duration = float(self.max_duration) * 0.95
        audio_files, ayahs_used = self.download_audio(ayahs, max_duration=max_dl_duration)
        
        # Update ayah_end to reflect what we actually used
        if ayahs_used < len(ayahs):
            actual_end = ayah_start + ayahs_used - 1
            print(f"ℹ️  Adjusted range to {ayah_start}-{actual_end} ({ayahs_used} ayahs)")
            ayah_end = actual_end
            ayahs = ayahs[:ayahs_used]  # Trim the ayahs list
        
        # Step 3: Merge audio
        print("\n🔊 Merging audio...")
        if self.progress_callback and not self.progress_callback(40):
            raise Exception("Cancelled by user")
        merged_audio = self.merge_audio_files(audio_files)
        
        # Step 4: Get total duration
        result = subprocess.run(
            [self._get_ffprobe_path(), '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', merged_audio],
            capture_output=True, text=True, creationflags=SUBPROCESS_FLAGS
        )
        total_duration = float(result.stdout.strip())
        
        # Hard limit: use configured max duration
        max_limit = float(self.max_duration)  # From settings
        target_limit = float(self.target_duration)  # From settings
        
        if total_duration > max_limit:
            print(f"⚠️  Video too long ({total_duration:.1f}s)! Trimming to {target_limit:.1f}s")
            total_duration = target_limit
        elif total_duration > target_limit:
            print(f"ℹ️  Video is {total_duration:.1f}s (over target but within max limit)")
        
        # Step 5: Create subtitles
        print("📝 Creating subtitles...")
        if self.progress_callback and not self.progress_callback(50):
            raise Exception("Cancelled by user")
        subtitle_file = self.create_subtitle_file(ayahs, audio_files)
        
        # Step 6: Prepare background
        print("🎨 Preparing background...")
        if self.progress_callback and not self.progress_callback(60):
            raise Exception("Cancelled by user")
        if background_video:
            background = self.resize_video_to_portrait(background_video, total_duration)
        else:
            background = self.create_background_video(total_duration, width=1080, height=1920)
        
        # Step 7: Combine everything
        print("\n🎬 Generating final video (this may take a moment)...)")
        if self.progress_callback and not self.progress_callback(70):
            raise Exception("Cancelled by user")
        
        if output_filename is None:
            # Get surah name
            surah_name = self.surah_names.get(surah, f"Surah{surah}")
            # Format: "SurahName brwayt ReciterName ayahs X-Y.mp4"
            output_filename = f"{surah_name} brwayt {reciter_name} ayahs {ayah_start}-{ayah_end}.mp4"
        
        output_path = self.output_dir / output_filename
        
        # Fix Windows path for FFmpeg subtitle filter - use forward slashes
        subtitle_file_escaped = subtitle_file.replace('\\', '/').replace(':', '\\:')
        
        # Use compression settings (configurable from GUI)
        try:
            result = subprocess.run([
                self.ffmpeg_path,
                '-i', background,
                '-i', merged_audio,
                '-vf', f"ass='{subtitle_file_escaped}'",
                '-map', '0:v',
                '-map', '1:a',
                '-c:v', 'libx264',
                '-preset', self.quality_preset,  # From settings
                '-crf', self.quality_crf,  # From settings
                '-c:a', 'aac',
                '-b:a', self.audio_bitrate,  # From settings
                '-shortest',
                str(output_path),
                '-y'
            ], check=True, capture_output=False, creationflags=SUBPROCESS_FLAGS)
        except subprocess.CalledProcessError as e:
            print(f"\n❌ FFmpeg Error!")
            print(f"Command: {' '.join(e.cmd)}")
            print(f"Error output: {e.stderr}")
            
            # Try without subtitles as fallback
            print("\n⚠️  Retrying without subtitles...")
            subprocess.run([
                self.ffmpeg_path,
                '-i', background,
                '-i', merged_audio,
                '-map', '0:v',
                '-map', '1:a',
                '-c:v', 'libx264',
                '-preset', self.quality_preset,
                '-crf', self.quality_crf,
                '-c:a', 'aac',
                '-b:a', self.audio_bitrate,
                '-shortest',
                str(output_path),
                '-y'
            ], check=True, capture_output=False, creationflags=SUBPROCESS_FLAGS)
        
        if self.progress_callback and not self.progress_callback(95):
            raise Exception("Cancelled by user")
        
        print(f"\n✅ Video generated successfully!")
        print(f"📁 Output: {output_path}")
        print(f"⏱️  Duration: {total_duration:.1f} seconds")
        
        # Cleanup temp files
        self._cleanup()
        
        if self.progress_callback:
            self.progress_callback(100)
        
        return str(output_path)
    
    def _cleanup(self):
        """Clean up temporary files"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        print("🧹 Cleaned up temporary files")


# Example usage
if __name__ == "__main__":
    # Create generator instance
    generator = QuranVideoGenerator(output_dir="output")
    
    # Generate video for Al-Fatiha (Surah 1, Ayah 1-7)
    video_path = generator.generate_video(
        surah=1,
        ayah_start=1,
        ayah_end=7,
        reciter="ar.alafasy",  # Change reciter if needed
        output_filename="al_fatiha.mp4"
    )
    
    print(f"\n🎉 Done! Video saved to: {video_path}")
