"""Fruit Ninja: 3D Adventure Edition - Main Application Controller.

Coordinates application initialization, state transitions between all 8 game modes,
input routing, and a rock-solid 60 FPS rendering loop with delta-time.
"""

import sys
import pygame
import settings
from progress import ProgressManager
from audio import get_audio
from menu import Menu, SettingsScreen
from gameplay import GameplayManager
from missions import MissionsScreen
from quiz import FruitQuizScreen
from puzzle import FruitPuzzleScreen
from levels import LevelSelectScreen
from rewards import AchievementsScreen, AchievementBanner


def main():
    """Initializes Pygame, loads settings, and runs the master state machine."""
    pygame.init()
    pygame.font.init()

    # Load persistent progress & settings
    progress_mgr = ProgressManager()
    user_settings = progress_mgr.data.get("settings", {})

    # Display flags
    display_flags = pygame.FULLSCREEN if user_settings.get("fullscreen", False) else 0
    screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), display_flags)
    pygame.display.set_caption(settings.TITLE)
    clock = pygame.time.Clock()

    # Audio Engine
    audio = get_audio()
    audio.set_music_volume(user_settings.get("music_volume", 0.6))
    audio.set_sfx_volume(user_settings.get("sfx_volume", 0.8))
    audio.toggle_music(user_settings.get("music_on", True))
    audio.toggle_sfx(user_settings.get("sfx_on", True))

    # Mode Managers
    menu_screen = Menu(screen)
    gameplay_mgr = GameplayManager(screen, progress_mgr)
    missions_screen = MissionsScreen(screen, progress_mgr)
    quiz_screen = FruitQuizScreen(screen, progress_mgr)
    puzzle_screen = FruitPuzzleScreen(screen, progress_mgr)
    level_screen = LevelSelectScreen(screen, progress_mgr)
    achieve_screen = AchievementsScreen(screen, progress_mgr)
    settings_screen = SettingsScreen(screen, progress_mgr)

    current_state = settings.MODE_MAIN_MENU

    running = True
    while running:
        dt = clock.tick(settings.FPS) / 1000.0  # Delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Route input by active screen
            if current_state == settings.MODE_MAIN_MENU:
                action = menu_screen.handle_event(event)
                if action == "QUIT":
                    running = False
                elif action == settings.MODE_CLASSIC:
                    gameplay_mgr.start_classic()
                    current_state = settings.MODE_CLASSIC
                elif action == settings.MODE_MISSIONS:
                    missions_screen.refresh()
                    current_state = settings.MODE_MISSIONS
                elif action == settings.MODE_QUIZ:
                    quiz_screen.reset_quiz()
                    current_state = settings.MODE_QUIZ
                elif action == settings.MODE_PUZZLE:
                    puzzle_screen.reset_puzzle()
                    current_state = settings.MODE_PUZZLE
                elif action == settings.MODE_LEVEL_SELECT:
                    level_screen.refresh()
                    current_state = settings.MODE_LEVEL_SELECT
                elif action == settings.MODE_ACHIEVEMENTS:
                    current_state = settings.MODE_ACHIEVEMENTS
                elif action == settings.MODE_SETTINGS:
                    current_state = settings.MODE_SETTINGS

            elif current_state == settings.MODE_CLASSIC:
                action = gameplay_mgr.handle_event(event)
                if action == "MENU":
                    current_state = settings.MODE_MAIN_MENU

            elif current_state == settings.MODE_MISSIONS:
                action = missions_screen.handle_event(event)
                if action == "BACK":
                    current_state = settings.MODE_MAIN_MENU
                elif action.startswith("PLAY_MISSION_"):
                    mission_id = int(action.replace("PLAY_MISSION_", ""))
                    gameplay_mgr.start_mission(mission_id)
                    current_state = settings.MODE_CLASSIC

            elif current_state == settings.MODE_QUIZ:
                action = quiz_screen.handle_event(event)
                if action == "BACK":
                    current_state = settings.MODE_MAIN_MENU

            elif current_state == settings.MODE_PUZZLE:
                action = puzzle_screen.handle_event(event)
                if action == "BACK":
                    current_state = settings.MODE_MAIN_MENU

            elif current_state == settings.MODE_LEVEL_SELECT:
                action = level_screen.handle_event(event)
                if action == "BACK":
                    current_state = settings.MODE_MAIN_MENU
                elif action.startswith("PLAY_LEVEL_"):
                    lvl_id = int(action.replace("PLAY_LEVEL_", ""))
                    gameplay_mgr.start_level(lvl_id)
                    current_state = settings.MODE_CLASSIC

            elif current_state == settings.MODE_ACHIEVEMENTS:
                action = achieve_screen.handle_event(event)
                if action == "BACK":
                    current_state = settings.MODE_MAIN_MENU

            elif current_state == settings.MODE_SETTINGS:
                action = settings_screen.handle_event(event)
                if action == "BACK":
                    current_state = settings.MODE_MAIN_MENU

        # State updates
        if current_state == settings.MODE_MAIN_MENU:
            menu_screen.update()
        elif current_state == settings.MODE_CLASSIC:
            gameplay_mgr.update(dt)
        elif current_state == settings.MODE_MISSIONS:
            missions_screen.update()
        elif current_state == settings.MODE_QUIZ:
            quiz_screen.update()
        elif current_state == settings.MODE_PUZZLE:
            puzzle_screen.update()
        elif current_state == settings.MODE_LEVEL_SELECT:
            level_screen.update()
        elif current_state == settings.MODE_ACHIEVEMENTS:
            achieve_screen.update()
        elif current_state == settings.MODE_SETTINGS:
            settings_screen.update()

        # Rendering
        if current_state == settings.MODE_MAIN_MENU:
            menu_screen.draw()
        elif current_state == settings.MODE_CLASSIC:
            gameplay_mgr.draw()
        elif current_state == settings.MODE_MISSIONS:
            missions_screen.draw()
        elif current_state == settings.MODE_QUIZ:
            quiz_screen.draw()
        elif current_state == settings.MODE_PUZZLE:
            puzzle_screen.draw()
        elif current_state == settings.MODE_LEVEL_SELECT:
            level_screen.draw()
        elif current_state == settings.MODE_ACHIEVEMENTS:
            achieve_screen.draw()
        elif current_state == settings.MODE_SETTINGS:
            settings_screen.draw()

        pygame.display.flip()

    progress_mgr.save()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
