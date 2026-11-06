"""Fruit Ninja: 3D Adventure Edition - Procedural Audio & Sound Engine.

Synthesizes rich arcade sound effects and background music using Python standard libraries
and Pygame's mixer, ensuring 100% reliable audio with zero external file dependencies.
"""

import io
import math
import random
import struct
import wave
import pygame


class SoundEngine:
    """Manages sound effects and background music synthesis and playback."""

    def __init__(self):
        self.enabled = False
        self.sfx_enabled = True
        self.music_enabled = True
        self.sfx_volume = 0.8
        self.music_volume = 0.6
        self.sounds = {}
        self.sample_rate = 22050

        # Try initializing pygame mixer
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=512)
            self.enabled = True
            self._generate_all_sounds()
            self._start_ambient_music()
        except Exception as e:
            # Fallback if audio hardware is absent (e.g. dummy driver)
            self.enabled = False

    def _create_wav_sound(self, generator_func) -> pygame.mixer.Sound:
        """Helper to create a pygame Sound from an in-memory mono PCM generator."""
        samples = generator_func()
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            raw = bytearray()
            for s in samples:
                val = max(-32767, min(32767, int(s * 32767)))
                raw.extend(struct.pack('<h', val))
            wav.writeframes(raw)
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def _generate_all_sounds(self):
        """Pre-renders all arcade sound effects."""
        try:
            self.sounds["slice"] = self._create_wav_sound(self._gen_slice)
            self.sounds["splat"] = self._create_wav_sound(self._gen_splat)
            self.sounds["bomb"] = self._create_wav_sound(self._gen_bomb)
            self.sounds["click"] = self._create_wav_sound(self._gen_click)
            self.sounds["combo"] = self._create_wav_sound(self._gen_combo)
            self.sounds["launch"] = self._create_wav_sound(self._gen_launch)
            self.sounds["victory"] = self._create_wav_sound(self._gen_victory)
            self.sounds["game_over"] = self._create_wav_sound(self._gen_game_over)
            self.sounds["achievement"] = self._create_wav_sound(self._gen_achievement)
            self.sounds["quiz_correct"] = self._create_wav_sound(self._gen_quiz_correct)
            self.sounds["quiz_wrong"] = self._create_wav_sound(self._gen_quiz_wrong)
            self.set_sfx_volume(self.sfx_volume)
        except Exception:
            pass

    def _gen_slice(self):
        """Blade slicing swoosh effect (high frequency descending whoosh)."""
        duration = 0.16
        num_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(num_samples):
            t = i / self.sample_rate
            env = math.sin(math.pi * (i / num_samples)) ** 1.5
            freq = 1200 - (t / duration) * 850
            noise = (random.random() * 2 - 1) * 0.45
            tone = math.sin(math.tau * freq * t) * 0.55
            samples.append((tone + noise) * env * 0.8)
        return samples

    def _gen_splat(self):
        """Juicy fruit squish & splatter effect."""
        duration = 0.22
        num_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(num_samples):
            t = i / self.sample_rate
            env = math.exp(-t * 18)
            freq = 420 - t * 900
            tone = math.sin(math.tau * max(60, freq) * t) * 0.6
            noise = (random.random() * 2 - 1) * 0.4
            samples.append((tone + noise) * env * 0.9)
        return samples

    def _gen_bomb(self):
        """Deep explosive rumble & shockwave."""
        duration = 0.55
        num_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(num_samples):
            t = i / self.sample_rate
            env = math.exp(-t * 6.5)
            freq = 90 * math.exp(-t * 4)
            rumble = math.sin(math.tau * freq * t) * 0.7
            noise = (random.random() * 2 - 1) * 0.55
            samples.append((rumble + noise) * env)
        return samples

    def _gen_click(self):
        """Arcade UI button click."""
        duration = 0.04
        num_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(num_samples):
            t = i / self.sample_rate
            env = math.exp(-t * 90)
            tone = math.sin(math.tau * 880 * t) * 0.6
            samples.append(tone * env)
        return samples

    def _gen_combo(self):
        """Uplifting melodic chime for combos."""
        duration = 0.35
        num_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(num_samples):
            t = i / self.sample_rate
            env = math.exp(-t * 5.0)
            note = 523.25 if t < 0.1 else (659.25 if t < 0.2 else 783.99)
            tone = math.sin(math.tau * note * t) * 0.5
            bell = math.sin(math.tau * note * 2 * t) * 0.25
            samples.append((tone + bell) * env * 0.8)
        return samples

    def _gen_launch(self):
        """Subtle upward swish when fruits are propelled upward."""
        duration = 0.12
        num_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(num_samples):
            t = i / self.sample_rate
            env = math.sin(math.pi * (i / num_samples))
            freq = 220 + (t / duration) * 350
            tone = math.sin(math.tau * freq * t) * 0.4
            samples.append(tone * env * 0.5)
        return samples

    def _gen_victory(self):
        """Triumphant tropical fanfare."""
        duration = 0.6
        num_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(num_samples):
            t = i / self.sample_rate
            env = math.exp(-t * 2.5)
            # Arpeggio C5 -> E5 -> G5 -> C6
            if t < 0.12:
                freq = 523.25
            elif t < 0.24:
                freq = 659.25
            elif t < 0.36:
                freq = 783.99
            else:
                freq = 1046.50
            tone = math.sin(math.tau * freq * t) * 0.55
            harm = math.sin(math.tau * freq * 1.5 * t) * 0.2
            samples.append((tone + harm) * env * 0.8)
        return samples

    def _gen_game_over(self):
        """Gentle descending tropical notes."""
        duration = 0.5
        num_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(num_samples):
            t = i / self.sample_rate
            env = math.exp(-t * 3.5)
            freq = 440 if t < 0.16 else (370 if t < 0.32 else 293.66)
            tone = math.sin(math.tau * freq * t) * 0.5
            samples.append(tone * env * 0.7)
        return samples

    def _gen_achievement(self):
        """Sparkling achievement unlock chime."""
        duration = 0.45
        num_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(num_samples):
            t = i / self.sample_rate
            env = math.exp(-t * 4.0)
            note = 880 if t < 0.15 else 1174.66
            tone = math.sin(math.tau * note * t) * 0.5 + math.sin(math.tau * note * 2 * t) * 0.25
            samples.append(tone * env * 0.75)
        return samples

    def _gen_quiz_correct(self):
        """Happy high chime."""
        duration = 0.25
        num_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(num_samples):
            t = i / self.sample_rate
            env = math.exp(-t * 8.0)
            tone = math.sin(math.tau * 784.0 * t) * 0.4 + math.sin(math.tau * 987.77 * t) * 0.3
            samples.append(tone * env * 0.8)
        return samples

    def _gen_quiz_wrong(self):
        """Soft low buzz."""
        duration = 0.22
        num_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(num_samples):
            t = i / self.sample_rate
            env = math.exp(-t * 10.0)
            tone = (math.sin(math.tau * 180.0 * t) + math.sin(math.tau * 175.0 * t)) * 0.4
            samples.append(tone * env * 0.7)
        return samples

    def _start_ambient_music(self):
        """Generates and streams a smooth tropical marimba/calypso ambient loop."""
        if not self.enabled or not self.music_enabled:
            return
        try:
            # 6-second rhythmic tropical chord sequence in C-major (C - Am - F - G)
            duration = 5.8
            num_samples = int(self.sample_rate * duration)
            samples = []
            chord_freqs = [
                [261.63, 329.63, 392.00],  # C
                [220.00, 261.63, 329.63],  # Am
                [174.61, 220.00, 261.63],  # F
                [196.00, 246.94, 293.66],  # G
            ]
            for i in range(num_samples):
                t = i / self.sample_rate
                section = int((t / duration) * 4) % 4
                chord = chord_freqs[section]
                beat_t = (t % 0.36) / 0.36
                beat_env = math.exp(-beat_t * 6.0)

                # Marimba style percussion tone
                s = sum(math.sin(math.tau * f * t) * 0.2 for f in chord)
                samples.append(s * beat_env * 0.45)

            # Store in BytesIO for music stream
            buf = io.BytesIO()
            with wave.open(buf, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(self.sample_rate)
                raw = bytearray()
                for s in samples:
                    val = max(-32767, min(32767, int(s * 32767)))
                    raw.extend(struct.pack('<h', val))
                wav.writeframes(raw)
            buf.seek(0)

            pygame.mixer.music.load(buf)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def play(self, sound_name: str):
        """Plays a registered sound effect if SFX is enabled."""
        if not self.enabled or not self.sfx_enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def set_sfx_volume(self, vol: float):
        self.sfx_volume = max(0.0, min(1.0, vol))
        for snd in self.sounds.values():
            try:
                snd.set_volume(self.sfx_volume)
            except Exception:
                pass

    def set_music_volume(self, vol: float):
        self.music_volume = max(0.0, min(1.0, vol))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except Exception:
            pass

    def toggle_music(self, enable: bool):
        self.music_enabled = enable
        if not self.music_enabled:
            try:
                pygame.mixer.music.pause()
            except Exception:
                pass
        else:
            try:
                pygame.mixer.music.unpause()
            except Exception:
                self._start_ambient_music()

    def toggle_sfx(self, enable: bool):
        self.sfx_enabled = enable


# Global Audio Singleton
_audio_instance = None


def get_audio() -> SoundEngine:
    global _audio_instance
    if _audio_instance is None:
        _audio_instance = SoundEngine()
    return _audio_instance

