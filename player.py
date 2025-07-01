# player.py
import datetime # Import datetime module

class Player:
    def __init__(self, xp=0, coins=0, title="Novice", current_level=0, punishment_sum=0,
                 xp_boost_pending=0, coin_gain_multiplier=1.0, punishment_mitigation_pending=False,
                 pets=None, daily_tasks_completed=0, last_daily_reset_date=None,
                 # Skills are now a dict to track XP and decay
                 skills=None,
                 pet_cooldowns=None, transcendence_buff_end_time=None, daily_tasks=None,
                 quests=None, pet_food=0, play_cooldowns=None,
                 corruption=0, daily_streak=0, unlocked_titles=None, active_title=None,
                 # New attributes for gear, achievements, and transcendence
                 gear=None, inventory=None, achievements=None, transcendence_count=0, main_quests_completed=0,
                 custom_punishments=None, last_workout_type=None): # Added last_workout_type
        self.xp = xp
        self.coins = coins
        self.title = title
        self.current_level = current_level # Stores the XP threshold for the current level
        self.punishment_sum = punishment_sum
        self.xp_boost_pending = xp_boost_pending
        self.coin_gain_multiplier = coin_gain_multiplier
        self.punishment_mitigation_pending = punishment_mitigation_pending
        self.pets = pets if pets is not None else []
        self.quests = quests if quests is not None else []

        self.daily_tasks_completed = daily_tasks_completed
        self.last_daily_reset_date = last_daily_reset_date if last_daily_reset_date is not None else datetime.date.today().isoformat()

        # Skill attributes - format: {'skill_name': {'xp': 10, 'last_updated': 'YYYY-MM-DD'}}
        self.skills = skills if skills is not None else {}

        # Feature attributes
        self.pet_cooldowns = pet_cooldowns if pet_cooldowns is not None else {}
        self.play_cooldowns = play_cooldowns if play_cooldowns is not None else {}
        self.transcendence_buff_end_time = transcendence_buff_end_time
        self.pet_food = pet_food
        self.daily_tasks = daily_tasks if daily_tasks is not None else {}

        # Streak, Corruption, and Titles
        self.corruption = corruption
        self.daily_streak = daily_streak
        self.unlocked_titles = unlocked_titles if unlocked_titles is not None else ["Novice"]
        self.active_title = active_title

        # New Attributes
        self.gear = gear if gear is not None else {'Helmet': None, 'Chest': None, 'Weapon': None, 'Boots': None}
        self.inventory = inventory if inventory is not None else []
        self.achievements = achievements if achievements is not None else []
        self.transcendence_count = transcendence_count
        self.main_quests_completed = main_quests_completed
        self.custom_punishments = custom_punishments if custom_punishments is not None else []

        # Attribute for workout balancing
        self.last_workout_type = last_workout_type


    def to_dict(self):
        """Converts player object to a dictionary for saving."""
        return {
            'xp': self.xp,
            'coins': self.coins,
            'title': self.title,
            'current_level': self.current_level,
            'punishment_sum': self.punishment_sum,
            'xp_boost_pending': self.xp_boost_pending,
            'coin_gain_multiplier': self.coin_gain_multiplier,
            'punishment_mitigation_pending': self.punishment_mitigation_pending,
            'pets': self.pets,
            'quests': self.quests,
            'daily_tasks_completed': self.daily_tasks_completed,
            'last_daily_reset_date': self.last_daily_reset_date,
            'skills': self.skills,
            'pet_cooldowns': self.pet_cooldowns,
            'play_cooldowns': self.play_cooldowns,
            'transcendence_buff_end_time': self.transcendence_buff_end_time,
            'daily_tasks': self.daily_tasks,
            'pet_food': self.pet_food,
            'corruption': self.corruption,
            'daily_streak': self.daily_streak,
            'unlocked_titles': self.unlocked_titles,
            'active_title': self.active_title,
            # New attributes
            'gear': self.gear,
            'inventory': self.inventory,
            'achievements': self.achievements,
            'transcendence_count': self.transcendence_count,
            'main_quests_completed': self.main_quests_completed,
            'custom_punishments': self.custom_punishments,
            'last_workout_type': self.last_workout_type # Added for saving
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Player object from a dictionary."""
        # Legacy support for old skills format
        skills_data = data.get('skills', {})
        if isinstance(skills_data, dict) and skills_data and not isinstance(next(iter(skills_data.values())), dict):
            # This is the old format (e.g., {'strength': 10}), convert it
            new_skills = {}
            for skill, value in skills_data.items():
                new_skills[skill] = {'xp': value, 'last_updated': datetime.date.today().isoformat()}
            data['skills'] = new_skills

        # Ensure achievements are always a list, even if loaded as a dict from old save
        achievements_data = data.get('achievements', [])
        if isinstance(achievements_data, dict):
            achievements_data = list(achievements_data.keys()) # Convert dict keys to a list

        return cls(
            xp=data.get('xp', 0),
            coins=data.get('coins', 0),
            title=data.get('title', "Novice"),
            current_level=data.get('current_level', 0),
            punishment_sum=data.get('punishment_sum', 0),
            xp_boost_pending=data.get('xp_boost_pending', 0),
            coin_gain_multiplier=data.get('coin_gain_multiplier', 1.0),
            punishment_mitigation_pending=data.get('punishment_mitigation_pending', False),
            pets=data.get('pets', []),
            quests=data.get('quests', []),
            daily_tasks_completed=data.get('daily_tasks_completed', 0),
            last_daily_reset_date=data.get('last_daily_reset_date', datetime.date.today().isoformat()),
            skills=data.get('skills', {}),
            pet_cooldowns=data.get('pet_cooldowns', {}),
            play_cooldowns=data.get('play_cooldowns', {}),
            transcendence_buff_end_time=data.get('transcendence_buff_end_time', None),
            daily_tasks=data.get('daily_tasks', {}),
            pet_food=data.get('pet_food', 0),
            corruption=data.get('corruption', 0),
            daily_streak=data.get('daily_streak', 0),
            unlocked_titles=data.get('unlocked_titles', ["Novice"]),
            active_title=data.get('active_title', None),
            # New attributes with defaults for backward compatibility
            gear=data.get('gear', {'Helmet': None, 'Chest': None, 'Weapon': None, 'Boots': None}),
            inventory=data.get('inventory', []),
            achievements=achievements_data, # Use the potentially converted list
            transcendence_count=data.get('transcendence_count', 0),
            main_quests_completed=data.get('main_quests_completed', 0),
            custom_punishments=data.get('custom_punishments', []),
            last_workout_type=data.get('last_workout_type', None) # Added for loading
        )
