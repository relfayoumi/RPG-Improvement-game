# game_manager.py
import json
import os
import re
import random
import datetime
import math # Import math for rounding up
from player import Player
from data_loader import load_quests
from config import SAVE_FILE, INITIAL_XP, INITIAL_COINS, INITIAL_TITLE, INITIAL_LEVEL, INITIAL_PUNISHMENT_SUM, QUESTS_CSV

CUSTOM_ACTIONS_FILE = 'custom_actions.json'

class GameManager:
    def __init__(self, force_new_game=False):
        # Hardcoded level/milestone data
        self.levels_data = [
            {'name': 'Level 1: 0 XP - Novice', 'xp_required': 0, 'description': 'Starting point.'},
            {'name': 'Milestone 1: 25 XP - Beginner', 'xp_required': 25, 'description': 'First steps towards mastery.'},
            {'name': 'Milestone 2: 50 XP - Apprentice', 'xp_required': 50, 'description': 'Learning the ropes.'},
            {'name': 'Milestone 3: 100 XP - Junior Apprentice', 'xp_required': 100, 'description': 'Growing stronger.'},
            {'name': 'Milestone 4: 125 XP - Journeyman', 'xp_required': 125, 'description': 'A skilled practitioner.'},
            {'name': 'Level 2: 150 XP - Skilled Journeyman', 'xp_required': 150, 'description': 'Ready for bigger challenges.'},
            {'name': 'Milestone 5: 200 XP - Expert', 'xp_required': 200, 'description': 'Deepening expertise.'},
            {'name': 'Milestone 6: 250 XP - Accomplished Expert', 'xp_required': 250, 'description': 'Mastering the craft.'},
            {'name': 'Level 3: 300 XP - Master', 'xp_required': 300, 'description': 'True mastery achieved.'},
            {'name': 'Milestone 7: 400 XP - Advanced Master', 'xp_required': 400, 'description': 'Refining skills.'},
            {'name': 'Milestone 8: 500 XP - Grandmaster', 'xp_required': 500, 'description': 'Beyond conventional limits.'},
            {'name': 'Milestone 9: 600 XP - Renowned Grandmaster', 'xp_required': 600, 'description': 'A name whispered with respect.'},
            {'name': 'Level 4: 750 XP - Legend', 'xp_required': 750, 'description': 'Entering the annals of history.'},
            {'name': 'Milestone 10: 1000 XP - Living Legend', 'xp_required': 1000, 'description': 'An icon among peers.'},
            {'name': 'Milestone 11: 1100 XP - Immortal', 'xp_required': 1100, 'description': 'Transcending mortal limitations.'},
            {'name': 'Milestone 12: 1250 XP - Ascended Immortal', 'xp_required': 1250, 'description': 'Touched by the divine.'},
            {'name': 'Level 5: 1500 XP - Divine Being', 'xp_required': 1500, 'description': 'A true deity among mortals.'},
            {'name': 'Milestone 13: 2000 XP - Transcendent Being', 'xp_required': 2000, 'description': 'Beyond form and matter.'},
            {'name': 'Level 6: 2500 XP - Supreme', 'xp_required': 2500, 'description': 'Peak existence achieved.'},
            {'name': 'Milestone 14: 3000 XP - Superior Being', 'xp_required': 3000, 'description': 'Surpassing all others.'},
            {'name': 'Milestone 15: 3500 XP - Infinite', 'xp_required': 3500, 'description': 'Boundless power.'},
            {'name': 'Level 7: 4000 XP - Eternal', 'xp_required': 4000, 'description': 'Existing beyond time.'},
            {'name': 'Milestone 16: 5000 XP - Infinite Mastery', 'xp_required': 5000, 'description': 'Mastery without end.'},
            {'name': 'Milestone 17: 6000 XP - Cosmic', 'xp_required': 6000, 'description': 'Connected to the cosmos.'},
            {'name': 'Level 8: 7000 XP - Universal', 'xp_required': 7000, 'description': 'Influencing the universe.'},
            {'name': 'Milestone 18: 8000 XP - Cosmic Overlord', 'xp_required': 8000, 'description': 'Ruler of the stars.'},
            {'name': 'Milestone 19: 9000 XP - Universal Being', 'xp_required': 9000, 'description': 'Embodiment of the universe.'},
            {'name': 'Level 9: 10000 XP - Limitless-Being', 'xp_required': 10000, 'description': 'No boundaries, no limits.'},
            {'name': 'Milestone 20: 12000 XP - Unbounded', 'xp_required': 12000, 'description': 'Completely free from constraints.'},
            {'name': 'Milestone 21: 15000 XP - Infinite Divinity', 'xp_required': 15000, 'description': 'Possessing endless divine power.'},
            {'name': 'Level 10: 20000 XP - \'The Honored one\'', 'xp_required': 20000, 'description': 'The ultimate title.'}
        ]
        # Base Transcension Requirement Map (Transcendence Count -> XP)
        self.transcend_req_map = {
            0: 1500,  # Divine Being
            1: 2000,  # Transcendent Being
            2: 2500,  # Supreme
            3: 3000,  # Superior Being
            4: 3500,  # Infinite
            5: 4000,  # Eternal
            6: 5000,  # Infinite Mastery
            7: 6000,  # Cosmic
            8: 7000,  # Universal
            9: 8000,  # Cosmic Overlord
            10: 9000, # Universal Being
            11: 10000, # Limitless-Being
            12: 12000, # Unbounded
            13: 15000, # Infinite Divinity
            14: 20000  # 'The Honored one'
        }

        # Hardcoded shop items with emojis and restored Skill Tomes
        # Prices increased by 3x
        self.shop_items_data = [
            {'name': 'Small XP Boost', 'emoji': '⚡️', 'description': 'Instantly gain 15 XP.', 'cost': 30, 'effect': 'xp_boost', 'amount': 15},
            {'name': 'Coin Pouch', 'emoji': '💰', 'description': 'Find an extra 10 coins.', 'cost': 15, 'effect': 'add_coins', 'amount': 10}, # Re-added Coin Pouch
            {'name': 'Pet Food', 'emoji': '🍖', 'description': 'One meal for your pet.', 'cost': 15, 'effect': 'add_pet_food', 'amount': 1},
            {'name': 'Punishment Mitigation Potion', 'emoji': '🛡️', 'description': 'Negates your next punishment.', 'cost': 60, 'effect': 'punishment_mitigation'},
            {'name': 'Mystery Pet Egg', 'emoji': '🥚', 'description': 'Hatches a random new pet.', 'cost': 150, 'effect': 'add_pet_egg'},
            {'name': 'Skill Tome (Strength)', 'emoji': '💪', 'description': 'Permanently increases Strength by 10 XP.', 'cost': 180, 'effect': 'gain_skill', 'skill': 'Strength', 'amount': 10},
            {'name': 'Skill Tome (Endurance)', 'emoji': '🏃‍♂️', 'description': 'Permanently increases Endurance by 10 XP.', 'cost': 180, 'effect': 'gain_skill', 'skill': 'Endurance', 'amount': 10},
            {'name': 'Skill Tome (Durability)', 'emoji': '🏋️‍♀️', 'description': 'Permanently increases Durability by 10 XP.', 'cost': 180, 'effect': 'gain_skill', 'skill': 'Durability', 'amount': 10},
            {'name': 'Skill Tome (Intellect)', 'emoji': '🧠', 'description': 'Permanently increases Intellect by 10 XP.', 'cost': 180, 'effect': 'gain_skill', 'skill': 'Intellect', 'amount': 10},
            {'name': 'Skill Tome (Faith)', 'emoji': '🙏', 'description': 'Permanently increases Faith by 10 XP.', 'cost': 180, 'effect': 'gain_skill', 'skill': 'Faith', 'amount': 10},
            {'name': 'XP Multiplier Potion (1hr)', 'emoji': '✨', 'description': 'Doubles XP gain for 1 hour.', 'cost': 300, 'effect': 'xp_multiplier', 'amount': 2, 'duration_minutes': 60},
            {'name': 'Coin Magnet (1hr)', 'emoji': '🧲', 'description': 'Doubles Coin gain for 1 hour.', 'cost': 300, 'effect': 'coin_multiplier', 'amount': 2, 'duration_minutes': 60},
            {'name': 'Master Key', 'emoji': '🗝️', 'description': 'Unlocks a random unobtained title.', 'cost': 500, 'effect': 'unlock_title'},
            {'name': 'Gear Fragment Pouch', 'emoji': '💎', 'description': 'Grants a random piece of gear.', 'cost': 250, 'effect': 'add_gear'}
        ]

        # Revamped punishments
        self.punishments_data = [
            {'name': 'Missed Workout', 'severity': 'Moderate', 'punishment': 5, 'xp_penalty': 10, 'coin_penalty': 5, 'special_chance': 0},
            {'name': 'Binge Eating', 'severity': 'High', 'punishment': 10, 'xp_penalty': 20, 'coin_penalty': 10, 'special_chance': 0.1, 'special_effect': 'pet_loss'},
            {'name': 'Wasted Time', 'severity': 'OK', 'punishment': 3, 'xp_penalty': 5, 'coin_penalty': 2, 'special_chance': 0},
            {'name': 'Late to Bed', 'severity': 'OK', 'punishment': 2, 'xp_penalty': 3, 'coin_penalty': 1, 'special_chance': 0},
            {'name': 'Skipped Reading', 'severity': 'Moderate', 'punishment': 4, 'xp_penalty': 8, 'coin_penalty': 4, 'special_chance': 0.05, 'special_effect': 'title_loss'},
            {'name': 'Unhandled Stress', 'severity': 'High', 'punishment': 7, 'xp_penalty': 15, 'coin_penalty': 8, 'special_chance': 0.1, 'special_effect': 'corruption_gain'},
            {'name': 'Lack of Focus', 'severity': 'OK', 'punishment': 3, 'xp_penalty': 5, 'coin_penalty': 3, 'special_chance': 0.05, 'special_effect': 'skill_decay'},
            {'name': 'Excessive Gaming', 'severity': 'Terrible', 'punishment': 12, 'xp_penalty': 30, 'coin_penalty': 15, 'special_chance': 0.2, 'special_effect': 'reset_streak'},
            {'name': 'Poor Sleep', 'severity': 'Moderate', 'punishment': 6, 'xp_penalty': 12, 'coin_penalty': 6, 'special_chance': 0.05, 'special_effect': 'xp_boost_loss'}
        ]

        # New: Varied and severe penalties for overdue quests
        self.overdue_quest_penalties = [
            lambda: self._penalize_stat_points('Random', 25),
            lambda: self._penalize_pet_loss(),
            lambda: self._penalize_perform_task("Do 100 pushups with no reward"),
            lambda: self._penalize_lose_coins(50),
            lambda: self._penalize_lose_xp(100)
        ]

        # Hardcoded pet data with new additions
        self.pets_data = [
            {'Name': 'Dragonling', 'Type': 'Dragon', 'BenefitDesc': '+{value} XP per task', 'Benefit': {'type': 'xp', 'base_value': 5}, 'Price': 75, 'Level': 1, 'XP': 0, 'XP_to_Evolve': 100},
            {'Name': 'Glimmerwing', 'Type': 'Fairy', 'BenefitDesc': '+{value} Coin per task', 'Benefit': {'type': 'coin', 'base_value': 1}, 'Price': 60, 'Level': 1, 'XP': 0, 'XP_to_Evolve': 80},
            {'Name': 'Stone Golem', 'Type': 'Construct', 'BenefitDesc': 'Punishment -{value}', 'Benefit': {'type': 'punishment', 'base_value': 1}, 'Price': 90, 'Level': 1, 'XP': 0, 'XP_to_Evolve': 120},
            {'Name': 'Phoenix Hatchling', 'Type': 'Mythical', 'BenefitDesc': '+{value} XP per task', 'Benefit': {'type': 'xp', 'base_value': 10}, 'Price': 150, 'Level': 1, 'XP': 0, 'XP_to_Evolve': 150},
            {'Name': 'Book Wyrm', 'Type': 'Magical', 'BenefitDesc': '+{value} Coin per task', 'Benefit': {'type': 'coin', 'base_value': 2}, 'Price': 120, 'Level': 1, 'XP': 0, 'XP_to_Evolve': 100},
            {'Name': 'Guardian Spirit', 'Type': 'Ethereal', 'BenefitDesc': 'Punishment -{value}', 'Benefit': {'type': 'punishment', 'base_value': 2}, 'Price': 180, 'Level': 1, 'XP': 0, 'XP_to_Evolve': 200},
            {'Name': 'Shadow Panther', 'Type': 'Beast', 'BenefitDesc': 'Corruption -{value}', 'Benefit': {'type': 'corruption', 'base_value': 1}, 'Price': 200, 'Level': 1, 'XP': 0, 'XP_to_Evolve': 180},
            {'Name': 'Ironclad Beetle', 'Type': 'Insect', 'BenefitDesc': 'Durability Skill +{value} XP', 'Benefit': {'type': 'skill_durability', 'base_value': 3}, 'Price': 160, 'Level': 1, 'XP': 0, 'XP_to_Evolve': 140}
        ]

        # Arc data (can be expanded)
        # Define the arc data with names, quotes, and month ranges
        self.arcs_data = [
            {'name': 'Genesis Pact', 'quote': 'A silent oath to begin. Foundations laid in secret. Discipline signed in blood.', 'months': [3, 4, 5]}, # March, April, May
            {'name': 'Solar Forge', 'quote': 'The sun beats down. Sweat is currency. Skill is tempered or shattered.', 'months': [6, 7, 8]}, # June, July, August
            {'name': 'Limits Edge', 'quote': 'Final sprint. You’re at the boundary of time, of effort, of yourself.', 'months': [9, 10, 11]}, # September, October, November
            {'name': 'Zero Flux', 'quote': 'Below freezing. Below distraction. The world sleeps — you sharpen in silence.', 'months': [12, 1, 2]} # December, January, February
        ]
        self.current_arc = self._get_current_seasonal_arc() # Initialize current arc based on date

        # REVAMPED: Preset training exercises transcribed from images with sets/reps
        self.strength_exercises = [
            # Body Weight
            {'name': 'Decline Pushups', 'difficulty': 'Very Difficult', 'base_xp': 3, 'base_coin': 0, 'workout_type': 'Upper'},
            {'name': 'Elevated Pike Pushups', 'difficulty': 'Very Difficult', 'base_xp': 3, 'base_coin': 0, 'workout_type': 'Upper'},
            {'name': 'Single Leg Floor Touches', 'difficulty': 'Very Difficult', 'base_xp': 3, 'base_coin': 0, 'workout_type': 'Lower'},
            {'name': 'L-Sit', 'difficulty': 'Very Difficult', 'base_xp': 3, 'base_coin': 0, 'workout_type': 'Full'},
            {'name': 'Finger Pushups', 'difficulty': 'Very Difficult', 'base_xp': 5, 'base_coin': 0, 'workout_type': 'Upper'},
            {'name': 'Pushups', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Upper'},
            {'name': 'Pike Pushups', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Upper'},
            {'name': 'Russian Twists', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Core'},
            {'name': 'Leg Raises', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Core'},
            {'name': 'Lunges (Each side)', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Lower'},
            {'name': 'Pike Shrugs', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Upper'},
            {'name': 'Sit-ups', 'difficulty': 'Mediocre', 'base_xp': 0, 'base_coin': 1, 'workout_type': 'Core'},
            {'name': 'Jumps', 'difficulty': 'Mediocre', 'base_xp': 0, 'base_coin': 1, 'workout_type': 'Lower'},
            {'name': 'Squats', 'difficulty': 'Easy', 'base_xp': 0, 'base_coin': 1, 'workout_type': 'Lower'},
            {'name': 'Wall Curls', 'difficulty': 'Easy', 'base_xp': 0, 'base_coin': 1, 'workout_type': 'Upper'},
            {'name': 'Forward/Backward Arm Circles', 'difficulty': 'Easy', 'base_xp': 0, 'base_coin': 1, 'workout_type': 'Upper'},
            # Weight Training
            {'name': 'Dragon Fly\'s', 'difficulty': 'Very Difficult', 'base_xp': 3, 'base_coin': 0, 'workout_type': 'Upper'},
            {'name': 'Skull Crushers', 'difficulty': 'Very Difficult', 'base_xp': 3, 'base_coin': 0, 'workout_type': 'Upper'},
            {'name': 'Weighted Leg Raises', 'difficulty': 'Very Difficult', 'base_xp': 3, 'base_coin': 0, 'workout_type': 'Core'},
            {'name': 'Elevated Weighted Lunges', 'difficulty': 'Very Difficult', 'base_xp': 3, 'base_coin': 0, 'workout_type': 'Lower'},
            {'name': 'Rows', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Upper'},
            {'name': 'Shoulder Press', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Upper'},
            {'name': '40lbs Squats', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Lower'},
            {'name': 'Weighted Sit-ups', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Core'},
            {'name': 'Weighted Lunges', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Lower'},
            {'name': 'Weighted Russian Twists', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Core'},
            {'name': 'Lateral Raises', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Upper'},
            {'name': 'Bicep Curls', 'difficulty': 'Mediocre', 'base_xp': 0, 'base_coin': 1, 'workout_type': 'Upper'},
            {'name': 'Hammer Curls', 'difficulty': 'Mediocre', 'base_xp': 0, 'base_coin': 1, 'workout_type': 'Upper'},
            {'name': 'Trapezius', 'difficulty': 'Mediocre', 'base_xp': 0, 'base_coin': 1, 'workout_type': 'Upper'},
            {'name': 'Forearm curls (any)', 'difficulty': 'Mediocre', 'base_xp': 0, 'base_coin': 1, 'workout_type': 'Upper'}
        ]

        self.endurance_exercises = [
            {'name': 'Final Gear Cycling', 'difficulty': 'Very Difficult', 'base_xp': 3, 'base_coin': 0, 'duration_target': 120}, # in minutes
            {'name': '10 km Run', 'difficulty': 'Very Difficult', 'base_xp': 3, 'base_coin': 0, 'duration_target': 60},
            {'name': 'Cycling', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'duration_target': 45},
            {'name': 'Shadow Boxing', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'duration_target': 30},
            {'name': 'Swim', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'duration_target': 40},
            {'name': 'Knee Raises', 'difficulty': 'Mediocre', 'base_xp': 0, 'base_coin': 1, 'duration_target': 20},
            {'name': 'Jumping Squats', 'difficulty': 'Mediocre', 'base_xp': 0, 'base_coin': 1, 'duration_target': 25},
            {'name': 'Butt Kicks', 'difficulty': 'Easy', 'base_xp': 0, 'base_coin': 1, 'duration_target': 15},
            {'name': 'Walk', 'difficulty': 'Easy', 'base_xp': 0, 'base_coin': 1, 'duration_target': 60}
        ]

        self.durability_exercises = [
            {'name': 'Tuck Jumps', 'difficulty': 'Very Difficult', 'base_xp': 3, 'base_coin': 0, 'workout_type': 'Core'},
            {'name': 'Plank', 'difficulty': 'Very Difficult', 'base_xp': 3, 'base_coin': 0, 'workout_type': 'Core'},
            {'name': 'Long Jumps', 'difficulty': 'Very Difficult', 'base_xp': 3, 'base_coin': 0, 'workout_type': 'Lower'},
            {'name': 'Crunches', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Core'},
            {'name': 'Jumping Lunges', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Lower'},
            {'name': 'Burpees', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Upper'},
            {'name': 'Twisting Mountain Climbers', 'difficulty': 'Difficult', 'base_xp': 1, 'base_coin': 0, 'workout_type': 'Core'}
        ]

        # Consolidated physical exercises for random selection
        self.all_physical_exercises = {
            'Strength': self.strength_exercises,
            'Endurance': self.endurance_exercises,
            'Durability': self.durability_exercises
        }

        self.intellect_conditioning_activities = {
            'iq': ['Study a new topic for 1 hour', 'Complete a programming challenge', 'Play a game of chess', 'Do homework/assignments'],
            'eq': ['Practice active listening with a friend', 'Write down three things you are grateful for', 'Meditate for 15 minutes'],
            'sq': ['Draw or sketch for 30 minutes', 'Complete a jigsaw puzzle', 'Practice mental rotation exercises'],
            'iaq': ['Write in a journal for 20 minutes', 'Perform a self-reflection on your week', 'Identify one personal bias'],
            'lq': ['Study a new language for 30 minutes', 'Read a chapter of a book', 'Learn 10 new vocabulary words'],
            'nq': ['Spend 30 minutes in nature', 'Identify 3 different types of birds or plants', 'Watch a nature documentary']
        }

        self.side_quest_templates = [
            {'name': 'Tidy Up', 'description': 'Clean your personal room or workspace.', 'xp_reward': 5, 'coin_reward': 2},
            {'name': 'Healthy Meal', 'description': 'Cook a healthy and nutritious breakfast.', 'xp_reward': 5, 'coin_reward': 3},
            {'name': 'Hydration', 'description': 'Drink 8 glasses of water throughout the day.', 'xp_reward': 3, 'coin_reward': 1},
            {'name': 'Quick Stretch', 'description': 'Take 10 minutes to stretch your body.', 'xp_reward': 3, 'coin_reward': 1},
            {'name': 'Mindful Moment', 'description': 'Meditate for 5 minutes without distractions.', 'xp_reward': 4, 'coin_reward': 2},
            {'name': 'Read a Little', 'description': 'Read 10 pages of any book.', 'xp_reward': 5, 'coin_reward': 2},
            {'name': 'Plan Tomorrow', 'description': 'Outline your top 3 priorities for the next day.', 'xp_reward': 4, 'coin_reward': 2},
            {'name': 'Quick Workout', 'description': 'Do 15 minutes of light exercise (e.g., walking).', 'xp_reward': 6, 'coin_reward': 3},
            {'name': 'Declutter Digital', 'description': 'Clean up your computer desktop or phone apps.', 'xp_reward': 4, 'coin_reward': 2},
            {'name': 'Learn a New Word', 'description': 'Learn and use a new vocabulary word today.', 'xp_reward': 3, 'coin_reward': 1},
            {'name': 'Express Gratitude', 'description': 'Tell someone you appreciate them.', 'xp_reward': 5, 'coin_reward': 3}
        ]

        self.daily_task_templates = [
            "Wash your face", "Brush your teeth", "Make your bed", "Tidy room for 5 mins",
            "Plan your day", "Workout", "Work on a project"
        ]

        self.title_effects_data = [
            {'name': 'Workhorse', 'effect': 'Grants 10% more coins from all sources.'},
            {'name': 'Prodigy', 'effect': 'Grants 10% more XP from all sources.'},
            {'name': 'Resilient', 'effect': 'Reduces punishment gain by 10%.'},
            {'name': 'Diligent', 'effect': 'Your daily streak has a chance to not reset on failure.'},
            {'name': 'Legendary Quester', 'effect': 'Grants a permanent 5% XP boost from all quests.'},
            {'name': 'Ascended', 'effect': 'Grants a permanent +0.1 coin multiplier.'},
            {'name': 'Sage', 'effect': 'Grants 10% more Intellect skill XP.'},
            {'name': 'Zealot', 'effect': 'Grants 10% more Faith skill XP.'},
            {'name': 'Indomitable', 'effect': 'Reduces Corruption gain by 15%.'}
        ]

        # New: Achievements Data
        self.achievements_data = {
            'quest_grandmaster': {'name': 'Quest Grandmaster', 'description': 'Complete 20 main quests.', 'reward_text': "'Legendary Quester' title, permanent small XP boost for quests.", 'unlocked': False},
            'transcendent_one': {'name': 'Transcendent One', 'description': 'Transcend 3 times.', 'reward_text': "'Ascended' title, permanent coin multiplier increase.", 'unlocked': False},
            'first_steps': {'name': 'First Steps', 'description': 'Complete your first quest.', 'reward_text': '50 Coins.', 'unlocked': False},
            'pet_lover': {'name': 'Pet Lover', 'description': 'Own 3 pets at the same time.', 'reward_text': '5 Pet Food.', 'unlocked': False},
            'wealthy_adventurer': {'name': 'Wealthy Adventurer', 'description': 'Accumulate 500 coins.', 'reward_text': 'A rare coin pouch and 100 bonus coins.', 'unlocked': False},
            'skill_master': {'name': 'Skill Master', 'description': 'Reach 100 XP in any skill.', 'reward_text': 'A powerful skill tome for a random skill.', 'unlocked': False},
            'gear_collector': {'name': 'Gear Collector', 'description': 'Collect 5 unique pieces of gear.', 'reward_text': 'A legendary gear piece.', 'unlocked': False},
            'daily_master': {'name': 'Daily Master', 'description': 'Complete 7 daily tasks in one day.', 'reward_text': '100 XP and a "Diligent" title.', 'unlocked': False},
            'corruption_cleanse': {'name': 'Corruption Cleanser', 'description': 'Reduce corruption to 0 from a high level (20+).', 'reward_text': 'A "Pure Heart" achievement and 200 XP.', 'unlocked': False},
            'forge_apprentice': {'name': 'Forge Apprentice', 'description': 'Enchant any item to +3.', 'reward_text': '50 coins and a rare enchanting scroll.', 'unlocked': False},
            'master_crafter': {'name': 'Master Crafter', 'description': 'Enchant any item to +5.', 'reward_text': '200 coins and a unique "Artisan" title.', 'unlocked': False},
            'transcended_gear_master': {'name': 'Transcended Gear Master', 'description': 'Roll an extra effect on a transcended item.', 'reward_text': '300 coins and a powerful "Empowered" title.', 'unlocked': False}
        }

        # New: Gear Data
        self.gear_data = {
            'Helmet': [
                {'name': 'Helmet of Wisdom', 'buff': {'type': 'xp_gain', 'value': 0.05}, 'requirements': {'Intellect': 300}},
                {'name': 'Crown of Intellect', 'buff': {'type': 'xp_gain', 'value': 0.10}, 'requirements': {'Intellect': 500}},
                {'name': 'Hood of Shadows', 'buff': {'type': 'punishment_reduction', 'value': 0.02}, 'requirements': {'Faith': 200}},
                {'name': 'Helm of the Berserker', 'buff': {'type': 'strength_xp_gain', 'value': 0.10}, 'requirements': {'Strength': 350}},
                {'name': 'Goggles of Precision', 'buff': {'type': 'intellect_xp_gain', 'value': 0.08}, 'requirements': {'Intellect': 400}}
            ],
            'Chest': [
                {'name': 'Aegis of Resilience', 'buff': {'type': 'punishment_reduction', 'value': 0.05}, 'requirements': {'Durability': 300}},
                {'name': 'Robe of the Archmage', 'buff': {'type': 'xp_gain', 'value': 0.08}, 'requirements': {'Intellect': 450}},
                {'name': 'Cuirass of Valor', 'buff': {'type': 'punishment_reduction', 'value': 0.07}, 'requirements': {'Durability': 400}},
                {'name': 'Vest of the Wind', 'buff': {'type': 'endurance_xp_gain', 'value': 0.10}, 'requirements': {'Endurance': 350}},
                {'name': 'Dragonhide Armor', 'buff': {'type': 'durability_xp_gain', 'value': 0.12}, 'requirements': {'Durability': 500}}
            ],
            'Weapon': [
                {'name': 'Blade of Prosperity', 'buff': {'type': 'coin_gain', 'value': 0.1}, 'requirements': {'Strength': 250}},
                {'name': 'Staff of Enlightenment', 'buff': {'type': 'xp_gain', 'value': 0.07}, 'requirements': {'Intellect': 300}},
                {'name': 'Hammer of Fortune', 'buff': {'type': 'coin_gain', 'value': 0.15}, 'requirements': {'Strength': 400}},
                {'name': 'Orb of Insight', 'buff': {'type': 'intellect_xp_gain', 'value': 0.15}, 'requirements': {'Intellect': 500}},
                {'name': 'Sacred Relic', 'buff': {'type': 'faith_xp_gain', 'value': 0.12}, 'requirements': {'Faith': 450}}
            ],
            'Boots': [
                {'name': 'Boots of Speed', 'buff': {'type': 'quest_speed', 'value': 0.05}, 'requirements': {'Endurance': 200}}, # Note: quest_speed not implemented
                {'name': 'Greaves of Stability', 'buff': {'type': 'punishment_reduction', 'value': 0.03}, 'requirements': {'Durability': 250}},
                {'name': 'Sandals of Swiftness', 'buff': {'type': 'quest_speed', 'value': 0.08}, 'requirements': {'Endurance': 300}},
                {'name': 'Boots of Endurance', 'buff': {'type': 'endurance_xp_gain', 'value': 0.07}, 'requirements': {'Endurance': 350}},
                {'name': 'Treads of the Mighty', 'buff': {'type': 'strength_xp_gain', 'value': 0.05}, 'requirements': {'Strength': 300}}
            ],
        }

        # New: Extra Status Effects for Transcended Gear
        self.extra_status_effects = [
            {'type': 'xp_gain', 'value': 0.03}, # +3% XP Gain
            {'type': 'coin_gain', 'value': 0.03}, # +3% Coin Gain
            {'type': 'punishment_reduction', 'value': 0.01}, # -1% Punishment Gain
            {'type': 'skill_xp_bonus', 'value': 0.05, 'skill': 'Strength'}, # +5% Strength XP
            {'type': 'skill_xp_bonus', 'value': 0.05, 'skill': 'Endurance'}, # +5% Endurance XP
            {'type': 'skill_xp_bonus', 'value': 0.05, 'skill': 'Durability'}, # +5% Durability XP
            {'type': 'skill_xp_bonus', 'value': 0.05, 'skill': 'Intellect'}, # +5% Intellect XP
            {'type': 'skill_xp_bonus', 'value': 0.05, 'skill': 'Faith'}, # +5% Faith XP
            {'type': 'corruption_reduction', 'value': 0.01}, # -1% Corruption
            {'type': 'daily_streak_chance', 'value': 0.02}, # +2% chance for daily streak to not reset
        ]


        self.player = self._load_game() if not force_new_game else Player()

        self.daily_check_message = self._check_and_reset_daily_tasks()
        self.check_overdue_quests()
        self.custom_actions = self._load_custom_actions()


    def _load_custom_actions(self):
        if not os.path.exists(CUSTOM_ACTIONS_FILE):
            return []
        try:
            with open(CUSTOM_ACTIONS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_custom_actions(self):
        with open(CUSTOM_ACTIONS_FILE, 'w') as f:
            json.dump(self.custom_actions, f, indent=4)

    def add_custom_action(self, action_name):
        if action_name not in self.custom_actions:
            self.custom_actions.append(action_name)
            self._save_custom_actions()
            return True
        return False

    def get_all_actions(self):
        base_actions = ["Complete a task", "Procrastinate", "Rest"]
        return list(reversed(self.custom_actions)) + base_actions

    def _load_game(self):
        if os.path.exists(SAVE_FILE):
            try:
                # Check if file is empty
                if os.path.getsize(SAVE_FILE) == 0:
                    print(f"WARNING: Save file '{SAVE_FILE}' is empty. Starting new game.")
                    return Player()
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    print(f"Loaded game data: {data}")
                    player = Player.from_dict(data)
                    # Load custom punishments from player save
                    # Ensure that player.custom_punishments is a list before extending
                    if isinstance(player.custom_punishments, list):
                        self.punishments_data.extend(player.custom_punishments)
                    else:
                        print(f"WARNING: 'custom_punishments' in save file is not a list. Skipping.")
                    return player
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to load game from '{SAVE_FILE}'. Invalid JSON data: {e}. Starting new game.")
                return Player()
            except Exception as e:
                print(f"ERROR: An unexpected error occurred while loading game from '{SAVE_FILE}': {e}. Starting new game.")
                return Player()
        print(f"INFO: Save file '{SAVE_FILE}' not found. Starting new game.")
        return Player()

    def save_game(self):
        # Ensure custom punishments are stored with the player
        self.player.custom_punishments = [p for p in self.punishments_data if p.get('custom')]
        with open(SAVE_FILE, 'w') as f:
            json.dump(self.player.to_dict(), f, indent=4)
        print("Game saved.")

    def reset_game(self):
        self.player = Player()
        self.save_game()
        print("Game reset to initial state.")

    def _get_current_seasonal_arc(self):
        """Determines the current seasonal arc based on the current date."""
        current_month = datetime.datetime.now().month
        for arc in self.arcs_data:
            if current_month in arc['months']:
                return arc
        return {'name': 'Unknown Arc', 'quote': 'The journey continues...', 'months': []} # Fallback

    def get_current_arc_info(self):
        """
        Returns information about the current active arc.
        Prioritizes transcendence buff if active, otherwise returns the seasonal arc.
        """
        if self.player.transcendence_buff_end_time:
            try:
                end_time = datetime.datetime.fromisoformat(self.player.transcendence_buff_end_time)
                if datetime.datetime.now() < end_time:
                    return {'name': 'Transcendent Surge', 'quote': 'Empowered by rebirth, your efforts are doubled!', 'end_date': end_time.strftime('%I:%M %p')}
                else:
                    # Buff expired, clear it
                    self.player.transcendence_buff_end_time = None
                    self.save_game()
            except (ValueError, TypeError):
                # Handle invalid date format in save file
                self.player.transcendence_buff_end_time = None

        # If no transcendence buff, return the current seasonal arc
        current_seasonal_arc = self._get_current_seasonal_arc()
        # For seasonal arcs, the "end_date" is not a specific time, but the end of the arc's period.
        # We can calculate the end of the last month in the arc.
        if current_seasonal_arc['months']:
            last_month_in_arc = max(current_seasonal_arc['months'])
            # Get the last day of the last month in the current year
            # Handle year rollover for Jan/Feb in Zero Flux
            current_year = datetime.datetime.now().year
            if last_month_in_arc in [1, 2] and datetime.datetime.now().month in [12]: # If in Dec and arc ends in Jan/Feb
                current_year += 1
            
            # Find the last day of the month
            if last_month_in_arc == 2: # February
                # Check for leap year
                if (current_year % 4 == 0 and current_year % 100 != 0) or (current_year % 400 == 0):
                    last_day = 29
                else:
                    last_day = 28
            elif last_month_in_arc in [4, 6, 9, 11]: # 30-day months
                last_day = 30
            else: # 31-day months
                last_day = 31

            end_date_obj = datetime.datetime(current_year, last_month_in_arc, last_day, 23, 59, 59)
            current_seasonal_arc['end_date'] = end_date_obj.strftime('%b %d, %Y')
        else:
            current_seasonal_arc['end_date'] = 'N/A' # For unknown arc

        return current_seasonal_arc


    def get_current_level_name(self):
        sorted_levels = sorted(self.levels_data, key=lambda x: x['xp_required'])
        current_level_name = "Novice"
        for level in sorted_levels:
            if self.player.xp >= level['xp_required']:
                current_level_name = level['name']
            else:
                break
        return "Max Level Reached" if self.player.xp >= sorted_levels[-1]['xp_required'] else current_level_name


    def get_xp_for_next_level(self):
        sorted_levels = sorted(self.levels_data, key=lambda x: x['xp_required'])
        for level in sorted_levels:
            if self.player.xp < level['xp_required']:
                return level['xp_required'] - self.player.xp
        return "Max Level Reached"

    def add_xp(self, amount, is_quest=False):
        if self._apply_corruption_failure():
            return "Your laziness gets the better of you... No XP gained due to corruption."

        amount = int(amount) # Ensure amount is an integer

        if self.player.active_title == 'Prodigy':
            amount = int(amount * 1.1)
        if self.player.active_title == 'Legendary Quester' and is_quest:
            amount = int(amount * 1.05)

        # Apply gear buffs
        gear_buff = self._get_gear_buff('xp_gain')
        amount = int(amount * (1 + gear_buff))

        original_xp = self.player.xp
        if self.player.transcendence_buff_end_time:
            try:
                if datetime.datetime.now() < datetime.datetime.fromisoformat(self.player.transcendence_buff_end_time):
                    amount *= 2
            except (ValueError, TypeError):
                pass

        self.player.xp += amount
        if self.player.xp_boost_pending > 0:
            boost_amount = self.player.xp_boost_pending
            self.player.xp += boost_amount
            self.player.xp_boost_pending = 0
            print(f"Applied XP boost! Gained an additional {boost_amount} XP.")

        self._check_for_level_up(original_xp, self.player.xp)
        print(f"Gained {amount} XP. Current XP: {self.player.xp}")
        return None

    def _check_for_level_up(self, old_xp, new_xp):
        sorted_levels = sorted(self.levels_data, key=lambda x: x['xp_required'])
        for level in sorted_levels:
            if old_xp < level['xp_required'] <= new_xp:
                self.player.title = level['name'].split(': ')[1].strip()
                self.player.current_level = level['xp_required']
                print(f"Congratulations! You've reached {level['name']}!")
                self.player.coins += 5
                if random.random() < 0.2:
                    self._unlock_random_title()

    def add_coins(self, amount):
        if self._apply_corruption_failure():
            return "Your laziness gets the better of you... No coins gained due to corruption."

        amount = int(amount) # Ensure amount is an integer

        if self.player.active_title == 'Workhorse':
            amount = int(amount * 1.1)

        # Apply gear buffs
        gear_buff = self._get_gear_buff('coin_gain')
        amount = int(amount * (1 + gear_buff))

        if self.player.transcendence_buff_end_time:
            try:
                if datetime.datetime.now() < datetime.datetime.fromisoformat(self.player.transcendence_buff_end_time):
                    amount *= 2
            except (ValueError, TypeError):
                pass

        actual_amount = amount * self.player.coin_gain_multiplier
        self.player.coins += int(actual_amount)
        print(f"Gained {int(actual_amount)} coins. Current Coins: {self.player.coins}")
        return None

    def perform_action(self, action_type, difficulty=None):
        message = ""
        xp_gain, coin_gain = 0, 0

        if action_type == "Complete a task":
            xp_gain, coin_gain = random.randint(3, 8), random.randint(1, 4)
        elif action_type == "Procrastinate":
            punishment_value = random.randint(3, 8)
            self.apply_punishment_value(punishment_value) # Use the new method
            message = f"You procrastinated. Your punishment sum increased by {punishment_value}."
            self.increment_daily_tasks()
        elif action_type == "Rest":
            if self.player.xp_boost_pending == 0:
                self.player.xp_boost_pending = 5
                message = "You rested and gained a pending XP boost of 5!"
            else:
                message = "You already have an XP boost pending."
            self.increment_daily_tasks()
        elif action_type in self.custom_actions:
            if difficulty is not None:
                xp_gain, coin_gain = int((difficulty / 10) * 25), int((difficulty / 10) * 15)
            else:
                xp_gain, coin_gain = random.randint(1, 3), random.randint(1, 2)
        else:
            message = "Unknown action."

        if xp_gain > 0 or coin_gain > 0:
            xp_msg = self.add_xp(xp_gain)
            coin_msg = self.add_coins(coin_gain)
            message = xp_msg or coin_msg or f"Performed '{action_type}'. Gained {xp_gain} XP and {coin_gain} coins."
            self.increment_daily_tasks()

        if self.player.punishment_sum >= 10:
            self.reset_game()
            message += "\nYour punishment sum reached 10! All game progress has been reset."

        self.save_game()
        return message

    def get_pet_current_benefit(self, pet_name):
        """Calculates the pet's current benefit based on its level."""
        pet_data = self.get_pet_data(pet_name)
        if not pet_data:
            return None, "Unknown Benefit"

        level = pet_data.get('Level', 1)
        benefit_info = pet_data.get('Benefit', {})
        base_value = benefit_info.get('base_value', 0)

        milestones = (level -1) // 5
        bonus = math.ceil(milestones * 0.5 * base_value)
        current_value = base_value + bonus

        desc_template = pet_data.get('BenefitDesc', '{value}')

        return benefit_info.get('type'), current_value, desc_template.format(value=current_value)

    def pet_a_pet(self, pet_name):
        """Handles the logic for petting a pet, including cooldowns and effects."""
        if not self.player.pets or pet_name not in self.player.pets:
            return "You don't have this pet!"

        now = datetime.datetime.now()
        cooldown_end_str = self.player.pet_cooldowns.get(pet_name)

        if cooldown_end_str:
            try:
                cooldown_end_time = datetime.datetime.fromisoformat(cooldown_end_str)
                if now < cooldown_end_time:
                    remaining = cooldown_end_time - now
                    return f"You can't pet {pet_name} yet. Cooldown remaining: {str(remaining).split('.')[0]}"
            except ValueError:
                pass

        self.player.pet_cooldowns[pet_name] = (now + datetime.timedelta(hours=1)).isoformat()

        message = ""
        if random.random() < 0.5:
            # The pet_name passed here is already the name string, not the full pet data.
            # So, we need to fetch the full pet data using get_pet_data.
            pet_data_full = self.get_pet_data(pet_name)
            if pet_data_full:
                benefit_type, benefit_value, benefit_desc = self.get_pet_current_benefit(pet_name)
                message = f"You petted {pet_name} and feel a surge of its power!"

                if benefit_type == 'xp':
                    xp_msg = self.add_xp(benefit_value)
                    message += f"\nYour pet's benefit granted you {benefit_value} additional XP!" if not xp_msg else f"\n{xp_msg}"
                elif benefit_type == 'coin':
                    coin_msg = self.add_coins(benefit_value)
                    message += f"\nYour pet's benefit granted you {benefit_value} additional coin!" if not coin_msg else f"\n{coin_msg}"
                elif benefit_type == 'punishment':
                    if self.player.punishment_sum > 0:
                        self.player.punishment_sum = max(0, self.player.punishment_sum - benefit_value)
                        message += f"\nYour pet mitigated {benefit_value} punishment point(s)!"
                elif benefit_type == 'corruption':
                    self.player.corruption = max(0, self.player.corruption - benefit_value)
                    message += f"\nYour pet helped reduce your corruption by {benefit_value}!"
                elif 'skill' in benefit_type:
                    skill_name = benefit_type.replace('skill_', '').title()
                    self.gain_skill_points(skill_name, benefit_value)
                    message += f"\nYour pet enhanced your {skill_name} skill by {benefit_value} XP!"
            else:
                message = f"Error: Could not retrieve data for pet {pet_name}."
        else:
            message = f"You petted {pet_name}. Nothing special happened this time, but it seemed happy."

        self.increment_daily_tasks()
        self.save_game()
        return message

    def generate_quest(self, category, sub_category=None, details=None):
        quest = {}
        due_date_str = details.get('due_date')

        base_quest = {
            'quest_type': 'main',
            'due_date': due_date_str,
            'steps': details.get('steps', '')
        }

        if category == "Training" and details:
            skill_type = details.get('skill')
            difficulty = details.get('difficulty')

            # Filter exercises by skill and difficulty
            possible_exercises = self.all_physical_exercises.get(skill_type, [])
            filtered_by_difficulty = [e for e in possible_exercises if e['difficulty'] == difficulty]

            if skill_type in ["Strength", "Durability"]:
                workout_type = details.get('workout_type')
                sets = details.get('sets', 1)
                reps = details.get('reps', 10)

                # Then filter by workout type, avoiding last workout type if possible
                filtered_by_type = [e for e in filtered_by_difficulty if e['workout_type'] == workout_type or e['workout_type'] == 'Full']

                if self.player.last_workout_type:
                    balanced_exercises = [e for e in filtered_by_type if e['workout_type'] != self.player.last_workout_type]
                    if balanced_exercises:
                        filtered_by_type = balanced_exercises

                # Check for existing quests with the same workout name, sets, and reps
                active_quest_names = {q['name'] for q in self.player.quests}
                truly_available_exercises = [
                    e for e in filtered_by_type
                    if f"Workout: {sets}x{reps} {e['name']}" not in active_quest_names
                ]

                if not truly_available_exercises:
                    return ("There are no more variations of workouts with those options that are not already active quests. "
                            "Please complete an existing workout quest or change the training options.")

                selected_exercise = random.choice(truly_available_exercises)

                # --- REWARD SCALING LOGIC ---
                total_reps = sets * reps
                # Baseline is 100 reps for 100% reward. Capped at 100%.
                reward_scale_factor = min(1.0, total_reps / 100.0)

                # Base rewards from the exercise are multiplied by the scaling factor
                base_xp = selected_exercise.get('base_xp', 0) * 10 # Increase base reward for more meaningful outcome
                base_coin = selected_exercise.get('base_coin', 0) * 5 # Increase base reward

                xp_reward = math.ceil(base_xp * reward_scale_factor)
                coin_reward = math.ceil(base_coin * reward_scale_factor)
                skill_xp_reward = math.ceil((base_xp * 2) * reward_scale_factor)


                quest_name = f"Workout: {sets}x{reps} {selected_exercise['name']}"
                quest = {
                    'name': quest_name,
                    'description': f"Complete your custom {skill_type} workout. Difficulty: {difficulty}.",
                    'xp_reward': xp_reward,
                    'coin_reward': coin_reward,
                    'skill_reward': {'skill': skill_type, 'amount': skill_xp_reward},
                    'workout_type': selected_exercise['workout_type']
                }
                base_quest['steps'] = f"1. Perform {sets} sets of {reps} reps of {selected_exercise['name']}.\n2. Mark quest as complete."

            elif skill_type == "Endurance":
                duration_target = details.get('duration', 30) # in minutes
                
                # Endurance quests don't filter by body part, but by duration target
                # We need to find an exercise that is suitable for the selected difficulty AND has a duration.
                # Assuming base_xp and base_coin are already defined in endurance_exercises
                suitable_exercises = [e for e in filtered_by_difficulty if 'duration_target' in e]
                if not suitable_exercises:
                    return "No endurance exercises found for the selected difficulty and duration."

                selected_exercise = random.choice(suitable_exercises)

                # Rewards for endurance are based on target duration, adjusted by difficulty
                # Higher difficulty means higher base rewards for the same duration
                difficulty_multiplier = {
                    'Easy': 1.0, 'Mediocre': 1.2, 'Difficult': 1.5, 'Very Difficult': 2.0
                }.get(difficulty, 1.0)

                base_xp_per_min = selected_exercise.get('base_xp', 1) * 0.5 * difficulty_multiplier # Small base, scales with duration
                base_coin_per_min = selected_exercise.get('base_coin', 1) * 0.25 * difficulty_multiplier

                # Total potential rewards if 100% completed
                xp_reward_full = math.ceil(base_xp_per_min * duration_target * 10) # Multiply by 10 for more impact
                coin_reward_full = math.ceil(base_coin_per_min * duration_target * 5) # Multiply by 5 for more impact

                quest_name = f"Endurance: {selected_exercise['name']} ({duration_target} mins)"
                quest = {
                    'name': quest_name,
                    'description': f"Complete {duration_target} minutes of {selected_exercise['name']}. Difficulty: {difficulty}.",
                    'xp_reward': xp_reward_full, # This is the full reward, will be scaled on completion
                    'coin_reward': coin_reward_full, # This is the full reward, will be scaled on completion
                    'skill_reward': {'skill': skill_type, 'amount': math.ceil(xp_reward_full * 0.5)},
                    'duration_target': duration_target, # Store target for completion calculation
                }
                base_quest['steps'] = f"1. Perform {selected_exercise['name']} for {duration_target} minutes.\n2. Mark quest as complete and enter duration completed."


        elif category == "Intellect Conditioning" and details:
            quest = {'name': f"Intellect: {details.get('activity', 'Unknown')}",
                     'description': f"Complete the intellect activity: {details.get('activity', 'Unknown')}.",
                     'xp_reward': 15, 'coin_reward': 5, 'skill_reward': {'skill': 'Intellect', 'amount': 2}}
        elif category == "Faith Goal":
            quest = {'name': "Spiritual Duty",
                     'description': "Engage in a spiritual or mindful activity for the day.",
                     'xp_reward': 10, 'coin_reward': 10, 'skill_reward': {'skill': 'Faith', 'amount': 2}}
        elif category == "Long-Term Project" and details:
             quest = {'name': details.get('project_name', 'Unnamed Project'),
                      'description': f"Work on your long-term project: {details.get('project_name', 'Unnamed Project')}.",
                      'xp_reward': 75, 'coin_reward': 40}

        if quest:
            quest.update(base_quest)
            self.player.quests.append(quest)
            if 'skill_reward' in quest:
                self.add_new_skill(quest['skill_reward']['skill'])
            self.save_game()
            return f"New main quest generated: {quest['name']}"
        return "Failed to generate quest."

    def generate_side_quest(self):
        active_side_quest_names = [q['name'] for q in self.player.quests if q.get('quest_type') == 'side']
        available_templates = [t for t in self.side_quest_templates if t['name'] not in active_side_quest_names]

        if not available_templates:
            return "No new side quests available at the moment."

        template = random.choice(available_templates)
        quest = template.copy()
        quest['quest_type'] = 'side'
        end_of_day = datetime.datetime.now().replace(hour=23, minute=59, second=59)
        quest['due_date'] = end_of_day.isoformat()
        quest['steps'] = "1. Identify the task.\n2. Complete the task.\n3. Mark as complete."

        self.player.quests.append(quest)
        self.save_game()
        return f"New side quest generated: {quest['name']}"

    def get_available_quests(self):
        return self.player.quests

    def complete_quest(self, quest_name, completed_duration=None):
        quest = next((q for q in self.player.quests if q['name'] == quest_name), None)
        if quest:
            if self._apply_corruption_failure():
                self.player.quests.remove(quest)
                self.save_game()
                return "Your laziness gets the better of you... No rewards gained due to corruption."

            is_main = quest.get('quest_type') == 'main'
            xp_reward = int(quest.get('xp_reward', 0))
            coin_reward = int(quest.get('coin_reward', 0))
            skill_info = quest.get('skill_reward', {})

            if quest.get('skill_reward', {}).get('skill') == 'Endurance' and completed_duration is not None:
                duration_target = quest.get('duration_target', 1)
                completion_percentage = min(1.0, completed_duration / duration_target)
                xp_reward = int(xp_reward * completion_percentage)
                coin_reward = int(coin_reward * completion_percentage)
                skill_info['amount'] = int(skill_info.get('amount', 0) * completion_percentage)
                message_duration = f" ({completed_duration}/{duration_target} mins completed)"
            else:
                message_duration = ""

            xp_msg = self.add_xp(xp_reward, is_quest=True)
            coin_msg = self.add_coins(coin_reward)

            if 'workout_type' in quest:
                self.player.last_workout_type = quest['workout_type']

            if skill_info:
                self.gain_skill_points(skill_info['skill'], skill_info['amount'])

            self.player.quests.remove(quest)
            if is_main:
                self.player.main_quests_completed += 1

            self.increment_daily_tasks()

            if random.random() < 0.1:
                self._add_random_gear_to_inventory()

            self.check_achievements()
            self.save_game()

            message = f"Quest '{quest_name}' completed!{message_duration}"
            if xp_msg or coin_msg:
                message += f"\nHowever, {xp_msg or coin_msg}"
            else:
                 message += f" You earned {xp_reward} XP and {coin_reward} coins."

            if is_main and random.random() < 0.1:
                unlocked_title_msg = self._unlock_random_title()
                if unlocked_title_msg:
                    message += f"\n{unlocked_title_msg}"

            return message
        return f"Quest '{quest_name}' not found or already completed."

    def check_overdue_quests(self):
        now = datetime.datetime.now()
        overdue_quests = [q for q in self.player.quests if q.get('due_date') and now > datetime.datetime.fromisoformat(q['due_date'])]

        if not overdue_quests:
            return ""

        message = "The following quests were overdue and have been removed:\n"
        penalty_messages = []
        for quest in overdue_quests:
            message += f"- {quest['name']}\n"
            self.player.quests.remove(quest)

            if quest.get('quest_type') == 'main':
                penalty_func = random.choice(self.overdue_quest_penalties)
                penalty_messages.append(penalty_func())

        if penalty_messages:
            message += "\nYou have suffered for your failure:\n" + "\n".join(filter(None, penalty_messages))

        self.save_game()
        return message

    def _penalize_stat_points(self, skill_name, amount):
        if not self.player.skills:
            return "Your skills were too low to be penalized."

        target_skill = skill_name
        if skill_name == 'Random':
            if not self.player.skills: return ""
            target_skill = random.choice(list(self.player.skills.keys()))

        if target_skill in self.player.skills:
            self.player.skills[target_skill]['xp'] = max(0, self.player.skills[target_skill]['xp'] - amount)
            return f"Your {target_skill} skill has atrophied, losing {amount} XP."
        return ""

    def _penalize_pet_loss(self):
        if self.player.pets:
            lost_pet = random.choice(self.player.pets)
            self.player.pets.remove(lost_pet)
            return f"In a moment of despair, your pet {lost_pet} has run away!"
        return "You had no pets to lose, a small mercy."

    def _penalize_perform_task(self, task_description):
        return f"You are burdened with a new penalty: {task_description}"

    def _penalize_lose_coins(self, amount):
        lost_amount = min(self.player.coins, amount)
        self.player.coins -= lost_amount
        return f"Your purse feels lighter... You lost {lost_amount} coins."

    def _penalize_lose_xp(self, amount):
        lost_amount = min(self.player.xp, amount)
        self.player.xp -= lost_amount
        return f"Your spirit wanes... You lost {lost_amount} XP."

    def get_shop_items(self):
        return self.shop_items_data

    def purchase_cart(self, cart):
        """Processes a shopping cart, applying item effects based on quantity."""
        if not cart:
            return False, "Your cart is empty."

        total_cost = 0
        for item_name, quantity in cart.items():
            item_data = next((i for i in self.shop_items_data if i['name'] == item_name), None)
            if item_data:
                total_cost += item_data['cost'] * quantity

        if self.player.coins < total_cost:
            return False, f"Not enough coins. Cart costs {total_cost}, but you only have {self.player.coins}."

        # Deduct cost and apply effects
        self.player.coins -= total_cost
        purchase_summary = []
        buff_message = ""

        for item_name, quantity in cart.items():
            item_data = next((i for i in self.shop_items_data if i['name'] == item_name), None)
            if item_data:
                # Apply effect for the total quantity purchased
                if item_data['effect'] == 'xp_boost':
                    self.add_xp(item_data['amount'] * quantity)
                elif item_data['effect'] == 'add_coins':
                    self.add_coins(item_data['amount'] * quantity)
                elif item_data['effect'] == 'add_pet_food':
                    self.player.pet_food += item_data['amount'] * quantity
                elif item_data['effect'] == 'gain_skill':
                    self.add_new_skill(item_data['skill'])
                    self.gain_skill_points(item_data['skill'], item_data['amount'] * quantity)
                elif item_data['effect'] == 'xp_multiplier':
                    # Store buff end time directly in player
                    self.player.transcendence_buff_end_time = (datetime.datetime.now() + datetime.timedelta(minutes=item_data['duration_minutes'])).isoformat()
                    buff_message = f"XP gain will be {item_data['amount']}x for {item_data['duration_minutes']} minutes!"
                elif item_data['effect'] == 'coin_multiplier':
                    # This buff needs to be handled on the player object for a timed duration
                    # For now, it's just a message, actual implementation of timed coin buff would be needed
                    self.player.coin_gain_multiplier *= item_data['amount'] # This is a permanent multiplier, needs adjustment if temporary
                    buff_message = f"Coin gain will be {item_data['amount']}x for {item_data['duration_minutes']} minutes!" # This message is temporary, actual multiplier is permanent here
                elif item_data['effect'] == 'unlock_title':
                    for _ in range(quantity): self._unlock_random_title() # Unlock one per quantity
                elif item_data['effect'] == 'add_gear':
                    for _ in range(quantity): self._add_random_gear_to_inventory()
                elif item_data['effect'] == 'punishment_mitigation':
                    self.player.punishment_mitigation_pending = True
                elif item_data['effect'] == 'add_pet_egg':
                    available_pets = [p for p in self.pets_data if p['Name'] not in self.player.pets]
                    if available_pets:
                        new_pet = random.choice(available_pets)
                        # Only add the name of the pet to the player's pets list
                        self.player.pets.append(new_pet['Name'])
                    else: # No new pets to give, refund for this egg
                        self.player.coins += item_data['cost']

                purchase_summary.append(f"{quantity}x {item_name}")

        self.increment_daily_tasks()
        self.check_achievements()
        self.save_game()

        final_message = f"Purchase successful for {total_cost} coins! You bought: {', '.join(purchase_summary)}."
        if buff_message:
            final_message += f"\nBuff applied: {buff_message}"

        return True, final_message


    def get_punishments(self):
        return self.punishments_data

    def add_custom_punishment(self, punishment_data):
        if punishment_data.pop('special_penalty_enabled', False):
            severity_chances = {"OK": 0.05, "Moderate": 0.15, "High": 0.30, "Terrible": 0.50}
            punishment_data['special_chance'] = severity_chances.get(punishment_data['severity'], 0)

            possible_effects = ['pet_loss', 'title_loss', 'skill_decay', 'corruption_gain', 'reset_streak', 'xp_boost_loss']
            punishment_data['special_effect'] = random.choice(possible_effects)

        self.punishments_data.append(punishment_data)
        self.save_game()


    def apply_punishment(self, habit_name):
        punishment = next((p for p in self.punishments_data if p['name'] == habit_name), None)
        if punishment:
            if self.player.punishment_mitigation_pending:
                self.player.punishment_mitigation_pending = False
                return f"Punishment for '{habit_name}' was mitigated by your potion!"

            punishment_value = punishment.get('punishment', 0)
            self.apply_punishment_value(punishment_value)

            self.player.xp = max(0, self.player.xp - punishment.get('xp_penalty', 0))
            self.player.coins = max(0, self.player.coins - punishment.get('coin_penalty', 0))

            message = f"Applied punishment for: {habit_name}. Sum +{punishment_value}, XP -{punishment.get('xp_penalty', 0)}, Coins -{punishment.get('coin_penalty', 0)}."

            if random.random() < punishment.get('special_chance', 0):
                effect = punishment.get('special_effect')
                if effect == 'pet_loss' and self.player.pets:
                    lost_pet = random.choice(self.player.pets)
                    self.player.pets.remove(lost_pet)
                    message += f"\nTERRIBLE LUCK! Your pet {lost_pet} got scared and ran away forever!"
                elif effect == 'title_loss' and len(self.player.unlocked_titles) > 1:
                    losable_titles = [t for t in self.player.unlocked_titles if t != "Novice"]
                    if losable_titles:
                        lost_title = random.choice(losable_titles)
                        self.player.unlocked_titles.remove(lost_title)
                        if self.player.active_title == lost_title:
                            self.player.active_title = None
                        message += f"\nTERRIBLE LUCK! You lost the memory of what it meant to be a '{lost_title}'!"
                elif effect == 'skill_decay':
                    penalty_msg = self._penalize_stat_points('Random', 25)
                    if penalty_msg:
                        message += f"\nTERRIBLE LUCK! {penalty_msg}"
                elif effect == 'corruption_gain':
                    gain_amount = random.randint(5, 15)
                    self.player.corruption += gain_amount
                    message += f"\nTERRIBLE LUCK! Your corruption increased by {gain_amount}!"
                elif effect == 'reset_streak':
                    self.player.daily_streak = 0
                    message += f"\nTERRIBLE LUCK! Your daily streak has been reset to 0!"
                elif effect == 'xp_boost_loss':
                    if self.player.xp_boost_pending > 0:
                        self.player.xp_boost_pending = 0
                        message += f"\nTERRIBLE LUCK! Your pending XP boost was lost!"


            self.increment_daily_tasks()
            if self.player.punishment_sum >= 10:
                self.reset_game()
                message += "\nYour punishment sum reached 10! All game progress has been reset."
            self.save_game()
            return message
        return f"Punishment '{habit_name}' not found."

    def apply_punishment_value(self, value):
        # Apply title and gear buff to the punishment value
        if self.player.active_title == 'Resilient':
            value = int(value * 0.9)
        gear_buff = self._get_gear_buff('punishment_reduction')
        value = int(value * (1 - gear_buff))
        self.player.punishment_sum += value

    def _check_and_reset_daily_tasks(self):
        today = datetime.date.today()
        last_reset_date = datetime.date.fromisoformat(self.player.last_daily_reset_date)
        message = ""
        if last_reset_date < today:
            days_passed = (today - last_reset_date).days
            decay_message = self._decay_skills(days_passed)

            # Check daily streak
            if self.player.daily_tasks_completed >= 5: # Threshold for maintaining streak
                self.player.daily_streak += 1
                message += "Daily streak maintained!\n"
            else:
                # Diligent title effect
                if self.player.active_title == 'Diligent' and random.random() < 0.2: # 20% chance to not reset
                    message += "Your diligence saved your streak this time!\n"
                else:
                    self.player.daily_streak = 0
                    self.player.corruption += 5 * days_passed # Increased corruption for missing days
                    message += f"Daily streak reset! You gained {5 * days_passed} corruption.\n"

            self.player.daily_tasks_completed = 0
            self.player.daily_tasks = {} # Reset daily tasks
            self.player.last_daily_reset_date = today.isoformat()
            self.save_game()
            message = decay_message + message if decay_message else message
        return message

    def _decay_skills(self, days_passed):
        today_str = datetime.date.today().isoformat()
        decay_messages = []
        for skill, data in self.player.skills.items():
            last_updated = datetime.date.fromisoformat(data['last_updated'])
            days_since_update = (datetime.date.today() - last_updated).days

            decay_amount = 0
            if days_since_update >= 7:
                decay_amount = int(2 * (1.5 ** min(days_since_update - 7, 10)))
            elif days_since_update > 0:
                decay_amount = days_since_update * random.randint(1, 2)

            if decay_amount > 0:
                original_xp = data['xp']
                self.player.skills[skill]['xp'] = max(0, original_xp - decay_amount)
                decayed_by = original_xp - self.player.skills[skill]['xp']
                if decayed_by > 0:
                    decay_messages.append(f"'{skill}' decayed by {decayed_by} XP.")

        return "\n".join(decay_messages) if decay_messages else ""

    def get_effective_corruption(self):
        effective_corruption = max(0, self.player.corruption - self.player.daily_streak)
        if self.player.active_title == 'Indomitable':
            effective_corruption = max(0, effective_corruption * 0.85) # 15% reduction
        return effective_corruption


    def _apply_corruption_failure(self):
        return random.randint(1, 100) <= self.get_effective_corruption() * 10

    def increment_daily_tasks(self):
        self.player.daily_tasks_completed += 1

    def complete_daily_task(self, task_name, is_complete):
        # Prevent multiple calls for the same state on the same day
        if self.player.daily_tasks.get(task_name) == is_complete:
            return ""

        self.player.daily_tasks[task_name] = is_complete

        if is_complete:
            xp_change = 1 # Small XP for daily task
            coin_change = 1 # Small Coins for daily task
            self.add_xp(xp_change)
            self.add_coins(coin_change)
            self.increment_daily_tasks()
        else:
            # If unchecking, potentially reverse the effect if already granted, but simpler to ignore for now
            pass
        self.save_game()
        return f"{'Completed' if is_complete else 'Unchecked'} '{task_name}'!"

    def get_pet_data(self, pet_name):
        # Iterate through self.pets_data to find the pet by name
        return next((p for p in self.pets_data if p['Name'] == pet_name), None)

    def feed_pet(self, pet_name):
        if self.player.pet_food <= 0:
            return "You don't have any pet food! Buy some from the shop."

        # Fetch the pet data from the main pets_data list, not player.pets
        pet_in_player = self.get_pet_data(pet_name)
        if pet_in_player:
            self.player.pet_food -= 1
            pet_in_player['XP'] += 10
            message = f"You fed {pet_name}. It gained 10 XP. You have {self.player.pet_food} pet food left."

            if pet_in_player['XP'] >= pet_in_player['XP_to_Evolve']:
                pet_in_player['Level'] += 1
                pet_in_player['XP'] = 0
                pet_in_player['XP_to_Evolve'] = int(pet_in_player['XP_to_Evolve'] * 1.5)
                message += f"\n{pet_in_player['Name']} leveled up to Level {pet_in_player['Level']}!"

            self.save_game()
            return message
        return "Pet not found."

    def play_with_pet(self, pet_name):
        if pet_name not in self.player.pets:
            return "You don't have this pet."

        now = datetime.datetime.now()
        cooldown_end_str = self.player.play_cooldowns.get(pet_name)

        if cooldown_end_str:
            try:
                cooldown_end_time = datetime.datetime.fromisoformat(cooldown_end_str)
                if now < cooldown_end_time:
                    remaining = cooldown_end_time - now
                    return f"You can't play with {pet_name} yet. Cooldown remaining: {str(remaining).split('.')[0]}"
            except ValueError:
                pass

        self.player.play_cooldowns[pet_name] = (now + datetime.timedelta(minutes=10)).isoformat()

        # Fetch the pet data from the main pets_data list, not player.pets
        pet_in_player = self.get_pet_data(pet_name)
        if pet_in_player:
            pet_in_player['XP'] += 15
            message = f"You played with {pet_name}. It gained 15 XP."
            if pet_in_player['XP'] >= pet_in_player['XP_to_Evolve']:
                pet_in_player['Level'] += 1
                pet_in_player['XP'] = 0
                pet_in_player['XP_to_Evolve'] = int(pet_in_player['XP_to_Evolve'] * 1.5)
                message += f" It leveled up to Level {pet_in_player['Level']}!"

            self.save_game()
            return message
        return "Pet not found."

    def get_transcend_requirement(self):
        count = self.player.transcendence_count
        return self.transcend_req_map.get(count, self.transcend_req_map[max(self.transcend_req_map.keys())])

    def transcend(self):
        req_xp = self.get_transcend_requirement()
        if self.player.xp >= req_xp:
            self.player.transcendence_count += 1
            self.player.coin_gain_multiplier += 0.1
            self.player.transcendence_buff_end_time = (datetime.datetime.now() + datetime.timedelta(minutes=30)).isoformat()

            self.player.xp = INITIAL_XP
            self.player.coins = INITIAL_COINS
            self.player.title = INITIAL_TITLE
            self.player.current_level = INITIAL_LEVEL
            self.player.punishment_sum = INITIAL_PUNISHMENT_SUM
            self.player.corruption = 0
            self.player.daily_streak = 0

            preserved_inventory = [item for item in self.player.inventory if item.get('transcended')]
            self.player.inventory = preserved_inventory

            for slot, item in self.player.gear.items():
                if item and not item.get('transcended'):
                    self.player.gear[slot] = None

            self._add_random_gear_to_inventory()

            self.check_achievements()
            self.save_game()
            return (f"You have transcended! This is your {self.player.transcendence_count} time. "
                    f"Your Coin Gain Multiplier is now {self.player.coin_gain_multiplier:.1f}x. "
                    "Progress and non-transcended gear reset, but you feel permanently stronger.")
        return "You do not meet the requirements to Transcend yet."

    def add_new_skill(self, skill_name):
        if skill_name and skill_name not in self.player.skills:
            self.player.skills[skill_name] = {'xp': 0, 'last_updated': datetime.date.today().isoformat()}
            self.save_game()
            return True
        return False

    def gain_skill_points(self, skill_name, amount):
        if skill_name in self.player.skills:
            # Apply title buffs to skill XP gain
            if self.player.active_title == 'Sage' and skill_name == 'Intellect':
                amount = int(amount * 1.1)
            elif self.player.active_title == 'Zealot' and skill_name == 'Faith':
                amount = int(amount * 1.1)

            # Apply gear buffs to skill XP gain (e.g., strength_xp_gain)
            skill_specific_buff = self._get_gear_buff(f'{skill_name.lower()}_xp_gain')
            amount = int(amount * (1 + skill_specific_buff))

            self.player.skills[skill_name]['xp'] += amount
            self.player.skills[skill_name]['last_updated'] = datetime.date.today().isoformat()
            self.save_game()
            return True
        return False

    def _unlock_random_title(self):
        available_titles = [t for t in self.title_effects_data if t['name'] not in self.player.unlocked_titles]
        if available_titles:
            new_title = random.choice(available_titles)
            self.player.unlocked_titles.append(new_title['name'])
            self.save_game()
            return f"Title Unlocked: {new_title['name']}!"
        return None

    def get_unlocked_titles(self):
        return self.player.unlocked_titles

    def get_title_effects(self):
        return self.title_effects_data

    def set_active_title(self, title_name):
        if title_name == "None": title_name = None
        if title_name is None or title_name in self.player.unlocked_titles:
            self.player.active_title = title_name
            self.save_game()
            return f"Active title set to: {title_name}"
        return "You haven't unlocked that title."

    def get_full_player_title(self):
        base = self.player.title
        active = self.player.active_title
        return f"{base} ({active})" if active else base

    def get_achievements(self):
        for key, ach in self.achievements_data.items():
            ach['unlocked'] = key in self.player.achievements
        return self.achievements_data

    def check_achievements(self):
        if self.player.main_quests_completed >= 20 and 'quest_grandmaster' not in self.player.achievements:
            self.player.achievements.append('quest_grandmaster')
            if 'Legendary Quester' not in self.player.unlocked_titles:
                self.player.unlocked_titles.append('Legendary Quester')

        if self.player.transcendence_count >= 3 and 'transcendent_one' not in self.player.achievements:
            self.player.achievements.append('transcendent_one')
            if 'Ascended' not in self.player.unlocked_titles:
                self.player.unlocked_titles.append('Ascended')
            self.player.coin_gain_multiplier += 0.1

        if self.player.main_quests_completed >= 1 and 'first_steps' not in self.player.achievements:
            self.player.achievements.append('first_steps')
            self.add_coins(50)

        if len(self.player.pets) >= 3 and 'pet_lover' not in self.player.achievements:
            self.player.achievements.append('pet_lover')
            self.player.pet_food += 5

        if self.player.coins >= 500 and 'wealthy_adventurer' not in self.player.achievements:
            self.player.achievements.append('wealthy_adventurer')
            self.add_coins(100)

        if any(skill_data['xp'] >= 100 for skill_data in self.player.skills.values()) and 'skill_master' not in self.player.achievements:
            self.player.achievements.append('skill_master')
            skill_tomes = [item for item in self.shop_items_data if item.get('effect') == 'gain_skill']
            if skill_tomes:
                random_tome = random.choice(skill_tomes)
                self.add_new_skill(random_tome['skill'])
                self.gain_skill_points(random_tome['skill'], random_tome['amount'])

        unique_gear_pieces = set()
        for item in self.player.inventory + list(self.player.gear.values()):
            if item:
                unique_gear_pieces.add(item['name'].split(' +')[0].replace('Transcended ', '')) # Remove enchant/transcended for uniqueness
        if len(unique_gear_pieces) >= 5 and 'gear_collector' not in self.player.achievements:
            self.player.achievements.append('gear_collector')
            legendary_gear = {'name': 'Helmet of Legends', 'type': 'Helmet', 'buff': {'type': 'xp_gain', 'value': 0.20}}
            self.player.inventory.append(legendary_gear)

        if self.player.daily_tasks_completed >= 7 and 'daily_master' not in self.player.achievements:
            self.player.achievements.append('daily_master')
            self.add_xp(100)
            if 'Diligent' not in self.player.unlocked_titles:
                self.player.unlocked_titles.append('Diligent')

        if self.player.corruption <= 0 and self._check_corruption_was_high() and 'corruption_cleanse' not in self.player.achievements:
            self.player.achievements.append('corruption_cleanse')
            self.add_xp(200)

        # Check for Forge Apprentice and Master Crafter
        max_enchant_level = 0
        for item in self.player.inventory + list(self.player.gear.values()):
            if item and not item.get('transcended'):
                max_enchant_level = max(max_enchant_level, item.get('enchant_level', 0))

        if max_enchant_level >= 3 and 'forge_apprentice' not in self.player.achievements:
            self.player.achievements.append('forge_apprentice')
            self.add_coins(50) # No actual scroll item, just reward

        if max_enchant_level >= 5 and 'master_crafter' not in self.player.achievements:
            self.player.achievements.append('master_crafter')
            self.add_coins(200)
            if 'Artisan' not in self.player.unlocked_titles:
                self.player.unlocked_titles.append('Artisan')

        # Check for Transcended Gear Master
        transcended_item_with_extra_effect = False
        for item in self.player.inventory + list(self.player.gear.values()):
            if item and item.get('transcended') and item.get('extra_effect'):
                transcended_item_with_extra_effect = True
                break
        if transcended_item_with_extra_effect and 'transcended_gear_master' not in self.player.achievements:
            self.player.achievements.append('transcended_gear_master')
            self.add_coins(300)
            if 'Empowered' not in self.player.unlocked_titles:
                self.player.unlocked_titles.append('Empowered')


    def _check_corruption_was_high(self):
        # This would ideally check a history of corruption, but for simplicity, we'll assume
        # if current corruption is 0 and player has had high punishment_sum in the past
        return self.player.punishment_sum < 5 and random.random() < 0.5 # Simplified check


    def _add_random_gear_to_inventory(self):
        gear_type = random.choice(list(self.gear_data.keys()))
        gear_item = random.choice(self.gear_data[gear_type])

        item_instance = gear_item.copy()
        item_instance['type'] = gear_type

        self.player.inventory.append(item_instance)
        print(f"Found gear: {item_instance['name']}!")
        self.save_game()

    def check_gear_requirements(self, item_to_equip):
        """Checks if the player meets the requirements to equip an item."""
        requirements = item_to_equip.get('requirements', {})
        if not requirements:
            return True, None # No requirements, can equip

        player_skills = self.player.skills
        missing_requirements = []

        for skill, required_xp in requirements.items():
            player_skill_xp = player_skills.get(skill, {}).get('xp', 0)
            if player_skill_xp < required_xp:
                missing_requirements.append(f"{skill}: {player_skill_xp}/{required_xp}")
        
        if missing_requirements:
            return False, "Missing requirements:\n" + "\n".join(missing_requirements)
        return True, None


    def equip_gear(self, item_name):
        item_to_equip = next((item for item in self.player.inventory if item['name'] == item_name), None)
        if not item_to_equip: return "Item not in inventory."

        can_equip, reason = self.check_gear_requirements(item_to_equip)
        if not can_equip:
            return f"Cannot equip {item_name}. {reason}"


        gear_slot = item_to_equip['type']

        if self.player.gear.get(gear_slot):
            self.unequip_gear(gear_slot)

        self.player.gear[gear_slot] = item_to_equip
        self.player.inventory.remove(item_to_equip)
        self.save_game()
        return f"Equipped {item_name}."

    def unequip_gear(self, gear_slot):
        item_to_unequip = self.player.gear.get(gear_slot)
        if not item_to_unequip: return "No item in that slot."

        self.player.inventory.append(item_to_unequip)
        self.player.gear[gear_slot] = None
        self.save_game()
        return f"Unequipped {item_to_unequip['name']}."

    def _get_gear_buff(self, buff_type):
        total_buff = 0
        for slot, item in self.player.gear.items():
            if item:
                # Primary buff
                if item.get('buff', {}).get('type') == buff_type:
                    total_buff += item['buff']['value']
                # Extra effect buff
                if item.get('extra_effect', {}).get('type') == buff_type:
                    total_buff += item['extra_effect']['value']
        return total_buff

    def enchant_gear(self, item_name):
        item_ref = None
        # Check in inventory first
        for i, item in enumerate(self.player.inventory):
            if item['name'] == item_name:
                item_ref = self.player.inventory[i]
                break
        # Check in equipped gear if not found in inventory
        if not item_ref:
            for slot, item in self.player.gear.items():
                if item and item['name'] == item_name:
                    item_ref = self.player.gear[slot]
                    break

        if not item_ref:
            return "Item not found."

        # Removed the check that prevented transcended items from being enchanted.
        # Transcended items can now be enchanted.

        level = item_ref.get('enchant_level', 0)
        cost = 100 * (level + 1)

        if self.player.coins < cost:
            return f"Not enough coins. Enchanting to +{level + 1} costs {cost} coins."

        self.player.coins -= cost
        item_ref['enchant_level'] = level + 1

        if 'buff' in item_ref and 'value' in item_ref['buff']:
            item_ref['buff']['value'] *= 1.1 # Increase existing buff by 10%
            # If it's a skill-specific buff, also increase its base value slightly
            if 'skill_xp_gain' in item_ref['buff']['type']:
                item_ref['buff']['value'] += 0.01 # Small flat increase for skill buffs

        # Handle naming for both regular and transcended items
        base_name_parts = item_ref['name'].split(' +')[0].split('Transcended ')
        base_name = base_name_parts[-1] # Get the part after 'Transcended ' if it exists, otherwise the whole name
        
        if item_ref.get('transcended'):
            item_ref['name'] = f"Transcended {base_name} +{item_ref['enchant_level']}"
        else:
            item_ref['name'] = f"{base_name} +{item_ref['enchant_level']}"

        self.check_achievements() # Recheck achievements after enchant
        self.save_game()
        return f"Successfully enchanted {base_name} to +{level + 1} for {cost} coins!"

    def transcend_gear(self, item_name):
        item_ref = None
        for i, item in enumerate(self.player.inventory):
            if item['name'] == item_name:
                item_ref = self.player.inventory[i]
                break
        if not item_ref:
            for slot, item in self.player.gear.items():
                if item and item['name'] == item_name:
                    item_ref = self.player.gear[slot]
                    break

        if not item_ref:
            return "Item not found."

        if item_ref.get('transcended'):
            return "This item is already Transcended. You can roll an extra effect on it."

        cost = 1000
        if self.player.coins < cost:
            return f"Not enough coins. Transcending an item costs {cost} coins."

        self.player.coins -= cost
        item_ref['transcended'] = True
        
        # Preserve enchant level in the name when transcending
        base_name_parts = item_ref['name'].split(' +')[0]
        enchant_suffix = f" +{item_ref['enchant_level']}" if item_ref.get('enchant_level', 0) > 0 else ""
        item_ref['name'] = f"Transcended {base_name_parts}{enchant_suffix}"

        self.check_achievements()
        self.save_game()
        return f"Successfully paid {cost} coins to Transcend {base_name_parts}. It is now safe from resets."

    def roll_extra_effect(self, item_name):
        item_ref = None
        for i, item in enumerate(self.player.inventory):
            if item['name'] == item_name:
                item_ref = self.player.inventory[i]
                break
        if not item_ref:
            for slot, item in self.player.gear.items():
                if item and item['name'] == item_name:
                    item_ref = self.player.gear[slot]
                    break

        if not item_ref:
            return "Item not found."

        if not item_ref.get('transcended'):
            return "This item is not Transcended. Only Transcended items can have extra effects."

        if 'extra_effect' in item_ref:
            return "This Transcended item already has an extra effect. You cannot roll another."

        cost = 1500
        if self.player.coins < cost:
            return f"Not enough coins. Rolling an extra effect costs {cost} coins."

        self.player.coins -= cost

        # Select a random extra effect from the predefined list
        new_effect = random.choice(self.extra_status_effects)
        item_ref['extra_effect'] = new_effect.copy() # Store a copy to avoid modifying the original template

        self.check_achievements() # Recheck achievements for 'transcended_gear_master'
        self.save_game()

        effect_type = new_effect['type'].replace('_', ' ').title()
        effect_value = new_effect['value']
        effect_value_str = f"{effect_value * 100:.1f}%" if 'gain' in effect_type.lower() or 'reduction' in effect_type.lower() else str(effect_value)
        if new_effect.get('skill'):
            effect_value_str += f" ({new_effect['skill']} Skill)"

        return (f"Successfully paid {cost} coins to roll an extra effect on {item_name}! "
                f"It gained: +{effect_value_str} {effect_type}.")

    def get_sell_price(self, item_data):
        """Calculates the sell price of a given item."""
        base_price = 50 # Base value for any gear, can be adjusted
        
        # Find the original item data from self.gear_data to get its base cost if applicable
        original_item_cost = 0
        for gear_type_list in self.gear_data.values():
            for original_item in gear_type_list:
                # Compare by cleaned name to match original template
                cleaned_original_name = original_item['name'].split(' +')[0].replace('Transcended ', '')
                cleaned_current_name = item_data['name'].split(' +')[0].replace('Transcended ', '')
                if cleaned_original_name == cleaned_current_name:
                    # Assuming a default cost for original items if not explicitly defined
                    # Or we could add a 'base_cost' to the self.gear_data items
                    # For now, let's use a simple multiplier of base_price or a fixed value for original
                    original_item_cost = 100 # Example: base cost of an un-enchanted, non-transcended item
                    break
            if original_item_cost > 0:
                break

        sell_price = max(base_price, original_item_cost * 0.2) # Start with a percentage of original cost or base_price

        enchant_level = item_data.get('enchant_level', 0)
        if enchant_level > 0:
            # Each enchant level adds a significant bonus to sell price
            sell_price += (enchant_level * 50) # +50 coins per enchant level

        if item_data.get('transcended'):
            # Transcended items sell for much more
            sell_price *= 2.5 # 2.5x multiplier for transcended items
            if item_data.get('extra_effect'):
                sell_price += 200 # Additional bonus for having an extra effect

        return int(sell_price)

    def sell_gear(self, item_name):
        item_ref = None
        is_equipped = False
        slot_to_remove = None

        # Check in inventory
        for i, item in enumerate(self.player.inventory):
            if item['name'] == item_name:
                item_ref = self.player.inventory.pop(i)
                break
        
        # Check in equipped gear if not found in inventory
        if not item_ref:
            for slot, item in self.player.gear.items():
                if item and item['name'] == item_name:
                    item_ref = item # Get the item reference
                    slot_to_remove = slot
                    is_equipped = True
                    break
        
        if not item_ref:
            return "Item not found in your inventory or equipped gear."

        sell_price = self.get_sell_price(item_ref)
        self.player.coins += sell_price

        if is_equipped:
            self.player.gear[slot_to_remove] = None # Remove from equipped slot

        self.save_game()
        return f"Successfully sold {item_name} for {sell_price} coins!"

