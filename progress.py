"""Fruit Ninja: 3D Adventure Edition - Persistent Save & Progress System.

Safely saves and loads player metrics, unlocked levels, mission stars, achievements,
and audio/gameplay settings to data/progress.json with automatic corrupt-file recovery.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import settings


class ProgressManager:
    """Handles persistent game save data in JSON format."""

    def __init__(self, filepath: Path = settings.PROGRESS_FILE):
        self.filepath = filepath
        self.data: Dict[str, Any] = {}
        self.on_achievement_unlocked = None
        self.load()

    def _default_data(self) -> Dict[str, Any]:
        """Default robust progress template."""
        return {
            "high_score": 0,
            "total_slices": 0,
            "total_games": 0,
            "stars_earned": 0,
            "unlocked_levels": [1],
            "level_stars": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
            "completed_missions": [],
            "mission_stars": {},
            "unlocked_achievements": [],
            "settings": {
                "music_volume": 0.6,
                "sfx_volume": 0.8,
                "music_on": True,
                "sfx_on": True,
                "fullscreen": False,
                "difficulty": "Normal"
            }
        }

    def load(self) -> Dict[str, Any]:
        """Loads player progress from JSON file, ensuring all required keys exist."""
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    defaults = self._default_data()
                    # Ensure nested dictionary keys exist
                    for k, v in defaults.items():
                        if k not in loaded:
                            loaded[k] = v
                        elif isinstance(v, dict):
                            for sub_k, sub_v in v.items():
                                if sub_k not in loaded[k]:
                                    loaded[k][sub_k] = sub_v
                    self.data = loaded
            except Exception:
                self.data = self._default_data()
                self.save()
        else:
            self.data = self._default_data()
            self.save()
        return self.data

    def save(self):
        """Saves current player progress to JSON file."""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def add_slices(self, count: int):
        self.data["total_slices"] = self.data.get("total_slices", 0) + count
        self.save()

    def record_game(self, score: int, slices: int):
        self.data["total_games"] = self.data.get("total_games", 0) + 1
        self.data["total_slices"] = self.data.get("total_slices", 0) + slices
        if score > self.data.get("high_score", 0):
            self.data["high_score"] = score
        self.save()

    def unlock_level(self, level_num: int):
        levels = self.data.get("unlocked_levels", [1])
        if level_num not in levels:
            levels.append(level_num)
            levels.sort()
            self.data["unlocked_levels"] = levels
            self.save()

    def set_level_stars(self, level_num: int, stars: int):
        l_stars = self.data.get("level_stars", {})
        key = str(level_num)
        prev = l_stars.get(key, 0)
        if stars > prev:
            diff = stars - prev
            l_stars[key] = stars
            self.data["stars_earned"] = self.data.get("stars_earned", 0) + diff
            self.data["level_stars"] = l_stars
            self.save()

    def complete_mission(self, mission_id: int, stars: int = 1):
        completed = self.data.get("completed_missions", [])
        if mission_id not in completed:
            completed.append(mission_id)
            self.data["completed_missions"] = completed
            self.data["stars_earned"] = self.data.get("stars_earned", 0) + stars
            self.save()

    def unlock_achievement(self, ach_id: str) -> bool:
        """Returns True if this is a newly unlocked achievement."""
        achs = self.data.get("unlocked_achievements", [])
        if ach_id not in achs:
            achs.append(ach_id)
            self.data["unlocked_achievements"] = achs
            self.data["stars_earned"] = self.data.get("stars_earned", 0) + 5
            self.save()
            if callable(self.on_achievement_unlocked):
                try:
                    self.on_achievement_unlocked(ach_id)
                except Exception:
                    pass
            return True
        return False

    def reset_progress(self):
        """Resets all metrics to default."""
        self.data = self._default_data()
        self.save()
