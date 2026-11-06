"""Fruit Ninja: 3D Adventure Edition - Fruit Quiz Trivia Mode.

Implements:
- 16 diverse educational & arcade trivia questions about fruits, nutrition, and trivia
- 2.5D fruit sprite illustrations beside each question card
- 4 rounded multiple-choice answer buttons with instant feedback (Green / Red)
- Score tracking, progress indicator (e.g. "Question 4 of 16")
- Results screen with star rewards and replay options
"""

from typing import List, Dict, Any
import pygame
import settings
from menu import FruitArcadeButton, TropicalBackground, get_font
from fruit import FruitSpriteCache
from progress import ProgressManager
from audio import get_audio


QUIZ_QUESTIONS = [
    {
        "fruit": "watermelon",
        "question": "What percentage of a Watermelon is composed of water?",
        "options": ["About 65%", "About 92%", "About 80%", "About 50%"],
        "correct": 1,
        "fact": "Watermelons are 92% water, making them the ultimate thirst-quencher!"
    },
    {
        "fruit": "banana",
        "question": "Botanically speaking, what kind of plant structure is a banana?",
        "options": ["A Root Vegetable", "A Berry", "A Citrus", "A Stone Fruit"],
        "correct": 1,
        "fact": "Bananas are technically large berries grown on giant herbaceous plants!"
    },
    {
        "fruit": "orange",
        "question": "Oranges are renowned worldwide for being rich in which vital vitamin?",
        "options": ["Vitamin D", "Vitamin C", "Vitamin B12", "Vitamin K"],
        "correct": 1,
        "fact": "One medium orange provides over 70 mg of immune-boosting Vitamin C!"
    },
    {
        "fruit": "strawberry",
        "question": "What makes the Strawberry unique among common fruits?",
        "options": ["Grows underwater", "Seeds on the outside", "Has zero sugar", "Never rots"],
        "correct": 1,
        "fact": "Strawberries are the only fruit that wear their seeds on the outside!"
    },
    {
        "fruit": "pineapple",
        "question": "How long does a Pineapple plant typically take to produce a single fruit?",
        "options": ["2 to 3 weeks", "Almost 2 to 3 years", "6 months", "10 years"],
        "correct": 1,
        "fact": "It takes nearly 2 to 3 years for a pineapple plant to produce a ripe crown!"
    },
    {
        "fruit": "mango",
        "question": "Which tropical fruit is celebrated in folklore as the 'King of Fruits'?",
        "options": ["The Coconut", "The Mango", "The Lime", "The Apple"],
        "correct": 1,
        "fact": "Mangoes are hailed as the King of Fruits due to their sweet, royal aroma!"
    },
    {
        "fruit": "kiwi",
        "question": "What was the Kiwi fruit originally called before being named in New Zealand?",
        "options": ["Chinese Gooseberry", "Fuzzy Melon", "Green Plum", "Island Berry"],
        "correct": 0,
        "fact": "Kiwis were originally known as Chinese Gooseberries before export!"
    },
    {
        "fruit": "apple",
        "question": "Why do fresh apples float when placed in a bucket of water?",
        "options": ["High oil content", "25% of volume is air", "Zero gravity core", "Hollow seeds"],
        "correct": 1,
        "fact": "Apples float because 25% of their internal volume consists of air pockets!"
    },
    {
        "fruit": "dragonfruit",
        "question": "Dragonfruit (Pitaya) actually grows on what type of plant?",
        "options": ["A climbing Cactus", "A Palm tree", "A Pine tree", "A Water Lily"],
        "correct": 0,
        "fact": "Dragonfruit grows on night-blooming climbing cactus vines!"
    },
    {
        "fruit": "coconut",
        "question": "Which tropical palm product can float across ocean currents for months?",
        "options": ["Coconut", "Mango", "Banana", "Watermelon"],
        "correct": 0,
        "fact": "Coconuts have buoyant, fibrous husks capable of crossing entire oceans!"
    },
    {
        "fruit": "lime",
        "question": "Why did historical British sailors eat limes on long maritime voyages?",
        "options": ["To stay awake", "To prevent Scurvy", "For night vision", "To ward off sharks"],
        "correct": 1,
        "fact": "Limes provided Vitamin C to protect sailors from scurvy, earning them the nickname 'limeys'!"
    },
    {
        "fruit": "banana",
        "question": "Which mineral is abundant in bananas, supporting muscle and nerve health?",
        "options": ["Potassium", "Iron", "Zinc", "Sodium"],
        "correct": 0,
        "fact": "Bananas are rich in potassium, vital for healthy heart and muscle rhythm!"
    },
    {
        "fruit": "orange",
        "question": "Which country is the world's leading producer of sweet oranges?",
        "options": ["Canada", "Brazil", "Norway", "Iceland"],
        "correct": 1,
        "fact": "Brazil produces about one-third of the entire world's sweet oranges!"
    },
    {
        "fruit": "watermelon",
        "question": "In what ancient country were watermelons found depicted in hieroglyphics?",
        "options": ["Ancient Egypt", "Ancient Greece", "Rome", "Babylon"],
        "correct": 0,
        "fact": "Watermelon seeds were placed in the tombs of Egyptian Pharaohs like King Tut!"
    },
    {
        "fruit": "apple",
        "question": "Approximately how many recognized varieties of apples exist worldwide?",
        "options": ["Over 7,500 varieties", "Only 50 varieties", "About 200", "Exactly 500"],
        "correct": 0,
        "fact": "Over 7,500 cultivated apple varieties exist across the globe!"
    },
    {
        "fruit": "pineapple",
        "question": "What special natural enzyme in pineapples breaks down proteins?",
        "options": ["Bromelain", "Papain", "Pepsin", "Amylase"],
        "correct": 0,
        "fact": "Bromelain in pineapples is an enzyme that tenderizes proteins and aids digestion!"
    }
]


class FruitQuizScreen:
    """Fully playable multiple-choice fruit trivia game mode."""

    def __init__(self, screen: pygame.Surface, progress_mgr: ProgressManager):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.progress_mgr = progress_mgr

        self.background = TropicalBackground(self.width, self.height)
        self.font_header = get_font(36, bold=True)
        self.font_question = get_font(21, bold=True)
        self.font_fact = get_font(16, bold=False)
        self.font_badge = get_font(16, bold=True)

        self.btn_back = FruitArcadeButton(
            pygame.Rect(40, 25, 170, 44),
            "< BACK",
            base_color=settings.TROPICAL_TEAL,
            accent_color=settings.LIME_GREEN,
            font_size=18,
            action_id="BACK"
        )

        # State
        self.current_index = 0
        self.score = 0
        self.correct_answers = 0
        self.state = "QUESTION"  # "QUESTION", "FEEDBACK", "RESULTS"
        self.feedback_timer = 0
        self.selected_option = -1
        self.is_last_correct = False

        # Results buttons
        self.btn_restart = None
        self.btn_results_menu = None

        self.option_buttons = []
        self._load_current_question()

    def reset_quiz(self):
        self.current_index = 0
        self.score = 0
        self.correct_answers = 0
        self.state = "QUESTION"
        self._load_current_question()

    def _load_current_question(self):
        self.option_buttons.clear()
        if self.current_index >= len(QUIZ_QUESTIONS):
            self._trigger_results()
            return

        q = QUIZ_QUESTIONS[self.current_index]
        cx = self.width // 2

        btn_w = 640
        btn_h = 52
        start_y = 350
        gap_y = 14

        for i, opt in enumerate(q["options"]):
            btn = FruitArcadeButton(
                pygame.Rect(cx - btn_w // 2, start_y + i * (btn_h + gap_y), btn_w, btn_h),
                f"{chr(65 + i)})  {opt}",
                base_color=(35, 75, 62),
                accent_color=settings.TROPICAL_TEAL,
                text_color=settings.CREAM_WHITE,
                font_size=18,
                action_id=f"OPT_{i}"
            )
            self.option_buttons.append(btn)

    def _trigger_results(self):
        self.state = "RESULTS"
        cx = self.width // 2
        cy = self.height // 2

        # Save achievement if score is high
        if self.correct_answers >= 10:
            self.progress_mgr.unlock_achievement("fruit_expert")

        stars_awarded = 1 if self.correct_answers >= 8 else (2 if self.correct_answers >= 12 else (3 if self.correct_answers >= 15 else 0))
        if stars_awarded > 0:
            self.progress_mgr.data["stars_earned"] = self.progress_mgr.data.get("stars_earned", 0) + stars_awarded
            self.progress_mgr.save()

        get_audio().play("victory" if self.correct_answers >= 8 else "game_over")

        btn_w, btn_h = 240, 54
        self.btn_restart = FruitArcadeButton(
            pygame.Rect(cx - btn_w - 15, cy + 120, btn_w, btn_h),
            "RESTART QUIZ",
            base_color=settings.TROPICAL_ORANGE,
            accent_color=settings.MANGO_YELLOW,
            font_size=20,
            action_id="RESTART"
        )
        self.btn_results_menu = FruitArcadeButton(
            pygame.Rect(cx + 15, cy + 120, btn_w, btn_h),
            "MAIN MENU",
            base_color=settings.TROPICAL_TEAL,
            accent_color=settings.LIME_GREEN,
            font_size=20,
            action_id="MENU"
        )

    def handle_event(self, event: pygame.event.Event) -> str:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            get_audio().play("click")
            return "BACK"

        a_back = self.btn_back.handle_event(event)
        if a_back == "BACK":
            get_audio().play("click")
            return "BACK"

        if self.state == "QUESTION":
            for i, btn in enumerate(self.option_buttons):
                action = btn.handle_event(event)
                if action.startswith("OPT_"):
                    self.selected_option = i
                    correct_idx = QUIZ_QUESTIONS[self.current_index]["correct"]
                    if i == correct_idx:
                        self.is_last_correct = True
                        self.correct_answers += 1
                        self.score += 100
                        get_audio().play("quiz_correct")
                    else:
                        self.is_last_correct = False
                        get_audio().play("quiz_wrong")

                    self.state = "FEEDBACK"
                    self.feedback_timer = 70  # ~1.2s delay to show correct answer and fact
                    return ""

        elif self.state == "RESULTS":
            if self.btn_restart and self.btn_restart.handle_event(event) == "RESTART":
                get_audio().play("click")
                self.reset_quiz()
                return ""
            if self.btn_results_menu and self.btn_results_menu.handle_event(event) == "MENU":
                get_audio().play("click")
                return "BACK"

        return ""

    def update(self):
        self.btn_back.update()
        if self.state == "QUESTION":
            for btn in self.option_buttons:
                btn.update()
        elif self.state == "FEEDBACK":
            self.feedback_timer -= 1
            if self.feedback_timer <= 0:
                self.current_index += 1
                self.state = "QUESTION"
                self.selected_option = -1
                self._load_current_question()
        elif self.state == "RESULTS":
            if self.btn_restart:
                self.btn_restart.update()
            if self.btn_results_menu:
                self.btn_results_menu.update()

    def draw(self):
        self.background.draw(self.screen)

        # Header Title
        title_surf = self.font_header.render("TROPICAL FRUIT QUIZ", True, settings.MANGO_YELLOW)
        self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 26))

        # Top Right: Score Pod
        score_pill = pygame.Rect(self.width - 200, 25, 160, 44)
        pygame.draw.rect(self.screen, (20, 50, 40), score_pill, border_radius=16)
        pygame.draw.rect(self.screen, settings.MANGO_YELLOW, score_pill, width=2, border_radius=16)
        score_txt = self.font_badge.render(f"SCORE: {self.score}", True, settings.MANGO_YELLOW)
        self.screen.blit(score_txt, (score_pill.centerx - score_txt.get_width() // 2, score_pill.centery - score_txt.get_height() // 2))

        # Back Button
        self.btn_back.draw(self.screen)

        if self.state in ["QUESTION", "FEEDBACK"]:
            q = QUIZ_QUESTIONS[self.current_index]
            cx = self.width // 2

            # Question Card Container
            card_w, card_h = 760, 180
            card_rect = pygame.Rect(cx - card_w // 2, 110, card_w, card_h)
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, (23, 63, 53, 240), (0, 0, card_w, card_h), border_radius=22)
            pygame.draw.rect(card_surf, settings.UI_BORDER_GOLD, (0, 0, card_w, card_h), width=2, border_radius=22)
            self.screen.blit(card_surf, card_rect.topleft)

            # Fruit Sprite Illustration on left of card
            fruit_surf = FruitSpriteCache.get_whole_surface(q["fruit"], radius=42)
            self.screen.blit(fruit_surf, (card_rect.x + 30, card_rect.centery - 42))

            # Progress Indicator: "Question X of 16"
            prog_txt = self.font_badge.render(f"Question {self.current_index + 1} of {len(QUIZ_QUESTIONS)}", True, settings.LIME_GREEN)
            self.screen.blit(prog_txt, (card_rect.x + 130, card_rect.y + 25))

            # Question Text
            q_surf = self.font_question.render(q["question"], True, settings.CREAM_WHITE)
            self.screen.blit(q_surf, (card_rect.x + 130, card_rect.y + 58))

            # Feedback / Fun Fact Banner
            if self.state == "FEEDBACK":
                res_col = settings.LIME_GREEN if self.is_last_correct else settings.WATERMELON_PINK
                res_str = "CORRECT!" if self.is_last_correct else "INCORRECT!"
                res_surf = self.font_badge.render(res_str, True, res_col)
                self.screen.blit(res_surf, (card_rect.x + 130, card_rect.y + 105))

                fact_surf = self.font_fact.render(f"Fact: {q['fact']}", True, settings.MANGO_YELLOW)
                self.screen.blit(fact_surf, (card_rect.x + 130, card_rect.y + 135))

            # Draw Option Buttons
            for i, btn in enumerate(self.option_buttons):
                if self.state == "FEEDBACK":
                    correct_idx = q["correct"]
                    if i == correct_idx:
                        btn.base_color = settings.LIME_GREEN
                        btn.text_color = (15, 45, 25)
                    elif i == self.selected_option and not self.is_last_correct:
                        btn.base_color = settings.WATERMELON_PINK
                        btn.text_color = settings.WHITE
                btn.draw(self.screen)

        elif self.state == "RESULTS":
            cx, cy = self.width // 2, self.height // 2
            card_w, card_h = 580, 420
            card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2 - 20, card_w, card_h)

            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, (23, 63, 53, 250), (0, 0, card_w, card_h), border_radius=22)
            pygame.draw.rect(card_surf, settings.UI_BORDER_GOLD, (0, 0, card_w, card_h), width=3, border_radius=22)
            self.screen.blit(card_surf, card_rect.topleft)

            # Title
            r_title = self.font_header.render("QUIZ COMPLETED!", True, settings.MANGO_YELLOW)
            self.screen.blit(r_title, (cx - r_title.get_width() // 2, card_rect.y + 35))

            # Correct Count & Accuracy
            total = len(QUIZ_QUESTIONS)
            acc = int((self.correct_answers / total) * 100)
            c_surf = self.font_question.render(f"Correct Answers: {self.correct_answers} / {total} ({acc}%)", True, settings.CREAM_WHITE)
            self.screen.blit(c_surf, (cx - c_surf.get_width() // 2, card_rect.y + 110))

            # Final Score
            s_surf = self.font_question.render(f"Total Points: {self.score}", True, settings.LIME_GREEN)
            self.screen.blit(s_surf, (cx - s_surf.get_width() // 2, card_rect.y + 160))

            # Rating
            rating_str = "Master Botanist!" if acc >= 80 else ("Knowledgeable Ninja!" if acc >= 50 else "Keep Studying Fruits!")
            rat_surf = self.font_badge.render(rating_str, True, settings.MANGO_YELLOW)
            self.screen.blit(rat_surf, (cx - rat_surf.get_width() // 2, card_rect.y + 215))

            # Buttons
            if self.btn_restart:
                self.btn_restart.draw(self.screen)
            if self.btn_results_menu:
                self.btn_results_menu.draw(self.screen)
