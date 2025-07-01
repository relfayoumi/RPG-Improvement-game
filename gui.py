# gui.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QScrollArea, QMessageBox, QGridLayout, QFrame, QLineEdit,
    QComboBox, QSizePolicy, QListWidget, QInputDialog, QListWidgetItem,
    QTextEdit, QDateEdit, QProgressBar, QSpacerItem, QSplitter, QDialog,
    QDialogButtonBox, QFormLayout, QSpinBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QDate, QSize , QEasingCurve, QPropertyAnimation
from PyQt5.QtGui import QFont, QIcon, QColor, QFontMetrics

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np

import datetime
from functools import partial
import math

class CustomPunishmentDialog(QDialog):
    """Dialog for creating a new custom punishment."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Custom Punishment")
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["OK", "Moderate", "High", "Terrible"])
        self.points_spin = QSpinBox()
        self.points_spin.setRange(0, 50)
        self.xp_spin = QSpinBox()
        self.xp_spin.setRange(0, 100)
        self.coin_spin = QSpinBox()
        self.coin_spin.setRange(0, 100)
        self.special_penalty_checkbox = QCheckBox("Add chance for special penalty?")

        layout.addRow("Name:", self.name_input)
        layout.addRow("Severity:", self.severity_combo)
        layout.addRow("Punishment Points:", self.points_spin)
        layout.addRow("XP Penalty:", self.xp_spin)
        layout.addRow("Coin Penalty:", self.coin_spin)
        layout.addRow(self.special_penalty_checkbox)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self):
        return {
            'name': self.name_input.text(),
            'severity': self.severity_combo.currentText(),
            'punishment': self.points_spin.value(),
            'xp_penalty': self.xp_spin.value(),
            'coin_penalty': self.coin_spin.value(),
            'special_penalty_enabled': self.special_penalty_checkbox.isChecked(),
            'custom': True
        }

class GameGUI(QMainWindow):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self._block_daily_task_signal = False
        self.shopping_cart = {} # For the shop cart

        self.setWindowTitle("Self-Improvement RPG")
        self.setGeometry(100, 100, 1400, 900) # Increased size for new layouts

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        self._create_time_section()
        self.main_layout.addWidget(self.time_frame)

        self._create_player_stats_widget()
        self.main_layout.addWidget(self.stats_frame)

        self._create_tab_widget()
        self.main_layout.addWidget(self.tab_widget)

        if self.game_manager.daily_check_message:
            QMessageBox.information(self, "Daily Report", self.game_manager.daily_check_message)

        overdue_message = self.game_manager.check_overdue_quests()
        if overdue_message:
            QMessageBox.warning(self, "Overdue Quests", overdue_message)

        self._update_all_displays()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timers)
        self.timer.start(1000)

    def _create_time_section(self):
        self.time_frame = QFrame(self)
        self.time_frame.setFrameShape(QFrame.StyledPanel)
        time_layout = QHBoxLayout(self.time_frame)
        self.date_label = QLabel()
        self.time_label = QLabel()
        self.arc_label = QLabel()
        self.arc_quote_label = QLabel() # New label for the arc quote
        self.arc_quote_label.setWordWrap(True) # Ensure quote wraps
        time_layout.addWidget(self.date_label)
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.arc_label)
        time_layout.addWidget(self.arc_quote_label) # Add quote label
        time_layout.addStretch(1)

    def _update_timers(self):
        now = QDateTime.currentDateTime()
        self.date_label.setText(f"🗓️ {now.toString('yyyy-MM-dd')}")
        self.time_label.setText(f"⏰ {now.toString('hh:mm:ss AP')}")
        arc_info = self.game_manager.get_current_arc_info()
        self.arc_label.setText(f"✨ Arc: {arc_info['name']} | Ends: {arc_info['end_date']}")
        self.arc_quote_label.setText(f"<i>\"{arc_info['quote']}\"</i>") # Display the quote
        if self.tab_widget.tabText(self.tab_widget.currentIndex()) == "Quests":
            self._update_quest_timers_text()
        # The animation is now handled in _update_transcend_display, no need for separate timer call here.
        # if self.tab_widget.tabText(self.tab_widget.currentIndex()) == "Transcend":
        #     self._animate_transcend_title() # This line was causing the crash

    def _create_player_stats_widget(self):
        self.stats_frame = QFrame(self)
        self.stats_frame.setFrameShape(QFrame.StyledPanel)
        self.stats_frame.setFrameShadow(QFrame.Raised)

        stats_layout = QGridLayout(self.stats_frame)
        self.title_label = QLabel()
        self.level_label = QLabel()
        self.xp_label = QLabel()
        self.coins_label = QLabel()
        self.punishment_label = QLabel()
        self.daily_tasks_completed_label = QLabel()
        self.xp_boost_label = QLabel()
        self.coin_multiplier_label = QLabel()
        self.punishment_mitigation_label = QLabel()

        stats_layout.addWidget(self.title_label, 0, 0)
        stats_layout.addWidget(self.level_label, 0, 1)
        stats_layout.addWidget(self.xp_label, 1, 0)
        stats_layout.addWidget(self.coins_label, 1, 1)
        stats_layout.addWidget(self.punishment_label, 2, 0)
        stats_layout.addWidget(self.daily_tasks_completed_label, 2, 1)
        stats_layout.addWidget(self.xp_boost_label, 3, 0)
        stats_layout.addWidget(self.coin_multiplier_label, 3, 1)
        stats_layout.addWidget(self.punishment_mitigation_label, 4, 0, 1, 2)

    def _update_player_stats_display(self):
        player = self.game_manager.player
        self.title_label.setText(f"👑 <b>Title:</b> {self.game_manager.get_full_player_title()}")
        self.level_label.setText(f"📊 <b>Level:</b> {self.game_manager.get_current_level_name()} (XP to next: {self.game_manager.get_xp_for_next_level()})")
        self.xp_label.setText(f"⚡️ <b>XP:</b> {player.xp}")
        self.coins_label.setText(f"💰 <b>Coins:</b> {player.coins}")
        self.punishment_label.setText(f"💀 <b>Punishment:</b> {player.punishment_sum}")
        self.xp_boost_label.setText(f"🚀 <b>XP Boost Pending:</b> {player.xp_boost_pending}")
        self.coin_multiplier_label.setText(f"📈 <b>Coin Multiplier:</b> {player.coin_gain_multiplier:.1f}x")
        self.punishment_mitigation_label.setText(f"🛡️ <b>Punishment Mitigation:</b> {'Yes' if player.punishment_mitigation_pending else 'No'}")
        self.daily_tasks_completed_label.setText(f"✔️ <b>Daily Actions:</b> {player.daily_tasks_completed}")

    def _create_tab_widget(self):
        self.tab_widget = QTabWidget(self)
        self._create_player_tab()
        self._create_quests_tab()
        self._create_pets_tab()
        self._create_shop_tab()
        self._create_forge_tab()
        self._create_punishments_tab()
        self._create_achievements_tab()
        self._create_transcend_tab()

        self.tab_widget.addTab(self.player_tab, "Player & Skills")
        self.tab_widget.addTab(self.quests_tab, "Quests")
        self.tab_widget.addTab(self.pets_tab, "Pets")
        self.tab_widget.addTab(self.shop_tab, "Shop")
        self.tab_widget.addTab(self.forge_tab, "Forge")
        self.tab_widget.addTab(self.punishments_tab, "Punishments")
        self.tab_widget.addTab(self.achievements_tab, "Achievements")
        self.tab_widget.addTab(self.transcend_tab, "Transcend")

        self.tab_widget.currentChanged.connect(self._on_tab_change)

    def _on_tab_change(self, index):
        tab_name = self.tab_widget.tabText(index)
        if tab_name == "Player & Skills": self._update_player_tab()
        elif tab_name == "Quests": self._update_quests_display()
        elif tab_name == "Pets": self._update_pets_display()
        elif tab_name == "Shop": self._update_shop_display()
        elif tab_name == "Forge": self._update_forge_display()
        elif tab_name == "Punishments": self._update_punishments_display()
        elif tab_name == "Achievements": self._update_achievements_display()
        elif tab_name == "Transcend": self._update_transcend_display()
        self._update_player_stats_display()

    def _create_player_tab(self):
        self.player_tab = QWidget()
        main_layout = QHBoxLayout(self.player_tab)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignTop)

        streak_box = QFrame(); streak_box.setFrameShape(QFrame.StyledPanel)
        streak_layout = QGridLayout(streak_box)
        self.streak_label = QLabel()
        self.corruption_label = QLabel()
        self.effective_corruption_label = QLabel()
        streak_layout.addWidget(QLabel("<b>🔥 Daily Streak:</b>"), 0, 0)
        streak_layout.addWidget(self.streak_label, 0, 1)
        streak_layout.addWidget(QLabel("<b>💀 Corruption:</b>"), 1, 0)
        streak_layout.addWidget(self.corruption_label, 1, 1)
        streak_layout.addWidget(QLabel("<b>⚖️ Effective Failure Chance:</b>"), 2, 0)
        streak_layout.addWidget(self.effective_corruption_label, 2, 1)
        left_layout.addWidget(streak_box)

        title_box = QFrame(); title_box.setFrameShape(QFrame.StyledPanel)
        title_layout = QVBoxLayout(title_box)
        title_layout.addWidget(QLabel("<b>🏆 Active Title</b>"))
        self.titles_combo_box = QComboBox()
        self.titles_combo_box.currentTextChanged.connect(self._set_active_title)
        self.title_effect_label = QLabel()
        title_layout.addWidget(self.titles_combo_box)
        title_layout.addWidget(self.title_effect_label)
        left_layout.addWidget(title_box)

        gear_box = QFrame(); gear_box.setFrameShape(QFrame.StyledPanel)
        gear_layout = QVBoxLayout(gear_box)
        gear_layout.addWidget(QLabel("<b>🛡️ Gear</b>"))
        self.gear_display_layout = QGridLayout()
        gear_layout.addLayout(self.gear_display_layout)

        unequip_layout = QHBoxLayout()
        self.unequip_combo_box = QComboBox()
        self.unequip_button = QPushButton("Unequip")
        self.unequip_button.clicked.connect(self._unequip_selected_gear)
        unequip_layout.addWidget(self.unequip_combo_box)
        unequip_layout.addWidget(self.unequip_button)
        gear_layout.addLayout(unequip_layout)

        self.inventory_list = QListWidget()
        self.inventory_list.itemDoubleClicked.connect(self._equip_item_from_inventory)
        self.inventory_list.itemClicked.connect(self._show_inventory_item_details)

        gear_layout.addWidget(QLabel("<b>Inventory (Double-click to equip)</b>"))
        gear_layout.addWidget(self.inventory_list)

        self.inventory_item_buffs_label = QLabel("Click an item for details.")
        self.inventory_item_buffs_label.setWordWrap(True)
        gear_layout.addWidget(self.inventory_item_buffs_label)

        left_layout.addWidget(gear_box)
        left_layout.addStretch(1)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Combined Stat Boosts Display
        combined_stats_box = QFrame(); combined_stats_box.setFrameShape(QFrame.StyledPanel)
        combined_stats_layout = QVBoxLayout(combined_stats_box)
        combined_stats_layout.addWidget(QLabel("<b>📈 Combined Stat Boosts:</b>"))
        self.combined_xp_boost_label = QLabel("XP Gain: +0%")
        self.combined_coin_boost_label = QLabel("Coin Gain: +0%")
        self.combined_punishment_reduction_label = QLabel("Punishment Reduction: +0%")
        self.combined_strength_boost_label = QLabel("Strength XP: +0%")
        self.combined_endurance_boost_label = QLabel("Endurance XP: +0%")
        self.combined_durability_boost_label = QLabel("Durability XP: +0%")
        self.combined_intellect_boost_label = QLabel("Intellect XP: +0%")
        self.combined_faith_boost_label = QLabel("Faith XP: +0%")
        self.combined_corruption_reduction_label = QLabel("Corruption Reduction: +0%")
        self.combined_daily_streak_chance_label = QLabel("Daily Streak Save Chance: +0%")


        combined_stats_layout.addWidget(self.combined_xp_boost_label)
        combined_stats_layout.addWidget(self.combined_coin_boost_label)
        combined_stats_layout.addWidget(self.combined_punishment_reduction_label)
        combined_stats_layout.addWidget(self.combined_strength_boost_label)
        combined_stats_layout.addWidget(self.combined_endurance_boost_label)
        combined_stats_layout.addWidget(self.combined_durability_boost_label)
        combined_stats_layout.addWidget(self.combined_intellect_boost_label)
        combined_stats_layout.addWidget(self.combined_faith_boost_label)
        combined_stats_layout.addWidget(self.combined_corruption_reduction_label)
        combined_stats_layout.addWidget(self.combined_daily_streak_chance_label)

        right_layout.addWidget(combined_stats_box)

        self.skills_figure, self.skills_ax = plt.subplots()
        self.skills_canvas = FigureCanvasQTAgg(self.skills_figure)

        add_skill_layout = QHBoxLayout()
        self.new_skill_input = QLineEdit()
        self.new_skill_input.setPlaceholderText("New Skill Name...")
        self.add_skill_button = QPushButton("Add Skill")
        self.add_skill_button.clicked.connect(self._add_new_skill)
        add_skill_layout.addWidget(self.new_skill_input)
        add_skill_layout.addWidget(self.add_skill_button)

        right_layout.addWidget(QLabel("<b>⭐ Skills Distribution</b>"))
        right_layout.addWidget(self.skills_canvas)
        right_layout.addLayout(add_skill_layout)

        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 1)

    def _update_player_tab(self):
        player = self.game_manager.player
        effective_corruption = self.game_manager.get_effective_corruption()
        self.streak_label.setText(f"{player.daily_streak} Days")
        self.corruption_label.setText(str(player.corruption))
        self.effective_corruption_label.setText(f"{effective_corruption * 10}%")

        self.titles_combo_box.blockSignals(True)
        self.titles_combo_box.clear()
        self.titles_combo_box.addItem("None")
        self.titles_combo_box.addItems(self.game_manager.get_unlocked_titles())
        self.titles_combo_box.setCurrentText(player.active_title or "None")
        self.titles_combo_box.blockSignals(False)
        self._update_title_effect_display()

        self._update_gear_display()
        self._update_skills_chart()
        self.inventory_item_buffs_label.setText("Click an item for details.")
        self._update_combined_stat_boosts()


    def _update_title_effect_display(self):
        title_name = self.titles_combo_box.currentText()
        effect_data = next((t for t in self.game_manager.get_title_effects() if t['name'] == title_name), None)
        self.title_effect_label.setText(f"<b>Effect:</b> {effect_data['effect']}" if effect_data else "<b>Effect:</b> None")

    def _set_active_title(self, title_name):
        self.game_manager.set_active_title(title_name)
        self._update_player_tab()
        self._update_player_stats_display()

    def _update_gear_display(self):
        for i in reversed(range(self.gear_display_layout.count())):
            self.gear_display_layout.itemAt(i).widget().setParent(None)

        player_gear = self.game_manager.player.gear
        row = 0
        self.unequip_combo_box.clear()
        self.unequip_button.setEnabled(False)

        for slot, item in player_gear.items():
            if item:
                slot_label = QLabel(f"<b>{slot}:</b>")
                item_name = item['name'] if item else "Empty"
                item_label = QLabel(item_name)
                if item and item.get('transcended'):
                    item_label.setStyleSheet("color: purple; font-weight: bold;")
                else:
                    item_label.setStyleSheet("")
                self.gear_display_layout.addWidget(slot_label, row, 0)
                self.gear_display_layout.addWidget(item_label, row, 1)
                row += 1
                self.unequip_combo_box.addItem(slot)
                self.unequip_button.setEnabled(True)

        self.inventory_list.clear()
        if not self.game_manager.player.inventory:
            self.inventory_list.addItem("Inventory is empty.")
        else:
            for item in self.game_manager.player.inventory:
                list_item = QListWidgetItem(f"{item['name']} ({item['type']})")
                if item.get('transcended'):
                    list_item.setForeground(QColor('purple'))
                list_item.setData(Qt.UserRole, item)
                self.inventory_list.addItem(list_item)

    def _equip_item_from_inventory(self, item):
        item_data = item.data(Qt.UserRole)
        message = self.game_manager.equip_gear(item_data['name'])
        QMessageBox.information(self, "Equip Gear", message)
        self._update_player_tab()

    def _unequip_selected_gear(self):
        selected_slot = self.unequip_combo_box.currentText()
        if selected_slot:
            message = self.game_manager.unequip_gear(selected_slot)
            QMessageBox.information(self, "Unequip Gear", message)
            self._update_player_tab()
        else:
            QMessageBox.warning(self, "No Slot Selected", "Please select a gear slot to unequip from.")

    def _show_inventory_item_details(self, item):
        item_data = item.data(Qt.UserRole)
        if item_data:
            details = f"<b>{item_data['name']} ({item_data['type']})</b><br>"
            if item_data.get('transcended'):
                details += "<b style='color:purple;'>Transcended</b><br>"

            buffs = []
            if 'buff' in item_data:
                buff_type = item_data['buff']['type'].replace('_', ' ').title()
                buff_value = item_data['buff']['value']
                buff_value_str = f"{buff_value * 100:.1f}%" if 'gain' in buff_type.lower() or 'reduction' in buff_type.lower() else str(buff_value)
                buffs.append(f"+{buff_value_str} {buff_type}")
            if 'extra_effect' in item_data and item_data['extra_effect']:
                effect = item_data['extra_effect']
                effect_type = effect['type'].replace('_', ' ').title()
                effect_value = effect['value']
                effect_value_str = f"{effect_value * 100:.1f}%" if 'gain' in effect_type.lower() or 'reduction' in effect_type.lower() else str(effect_value)
                buffs.append(f"Extra: +{effect_value_str} {effect_type}")

            if buffs:
                details += "Buffs: " + ", ".join(buffs)
            else:
                details += "No specific buffs."

            # Display requirements
            requirements = item_data.get('requirements', {})
            if requirements:
                req_strings = [f"{skill}: {req_xp}" for skill, req_xp in requirements.items()]
                details += "<br><b>Requirements:</b> " + ", ".join(req_strings)
            
            self.inventory_item_buffs_label.setText(details)
        else:
            self.inventory_item_buffs_label.setText("Click an item for details.")


    def _update_combined_stat_boosts(self):
        # Initialize all potential buff types
        xp_gain_buff = self.game_manager._get_gear_buff('xp_gain')
        coin_gain_buff = self.game_manager._get_gear_buff('coin_gain')
        punishment_reduction_buff = self.game_manager._get_gear_buff('punishment_reduction')
        strength_xp_boost = self.game_manager._get_gear_buff('strength_xp_gain')
        endurance_xp_boost = self.game_manager._get_gear_buff('endurance_xp_gain')
        durability_xp_boost = self.game_manager._get_gear_buff('durability_xp_gain')
        intellect_xp_boost = self.game_manager._get_gear_buff('intellect_xp_gain')
        faith_xp_boost = self.game_manager._get_gear_buff('faith_xp_gain')
        corruption_reduction_buff = self.game_manager._get_gear_buff('corruption_reduction')
        daily_streak_chance_buff = self.game_manager._get_gear_buff('daily_streak_chance')


        # Add active title effects
        active_title_name = self.game_manager.player.active_title
        if active_title_name:
            if active_title_name == 'Prodigy':
                xp_gain_buff += 0.10
            elif active_title_name == 'Workhorse':
                coin_gain_buff += 0.10
            elif active_title_name == 'Resilient':
                punishment_reduction_buff += 0.10 # This is a direct reduction, not percentage
            elif active_title_name == 'Legendary Quester':
                xp_gain_buff += 0.05 # This is specific to quests, but can be displayed as general boost
            elif active_title_name == 'Ascended':
                coin_gain_buff += 0.10 # This is direct multiplier, but represents percentage increase too
            elif active_title_name == 'Sage':
                intellect_xp_boost += 0.10
            elif active_title_name == 'Zealot':
                faith_xp_boost += 0.10
            elif active_title_name == 'Indomitable':
                corruption_reduction_buff += 0.15 # This is a direct reduction

        self.combined_xp_boost_label.setText(f"XP Gain: +{xp_gain_buff * 100:.1f}%")
        self.combined_coin_boost_label.setText(f"Coin Gain: +{coin_gain_buff * 100:.1f}%")
        self.combined_punishment_reduction_label.setText(f"Punishment Reduction: {punishment_reduction_buff * 100:.1f}%")
        self.combined_strength_boost_label.setText(f"Strength XP: +{strength_xp_boost * 100:.1f}%")
        self.combined_endurance_boost_label.setText(f"Endurance XP: +{endurance_xp_boost * 100:.1f}%")
        self.combined_durability_boost_label.setText(f"Durability XP: +{durability_xp_boost * 100:.1f}%")
        self.combined_intellect_boost_label.setText(f"Intellect XP: +{intellect_xp_boost * 100:.1f}%")
        self.combined_faith_boost_label.setText(f"Faith XP: +{faith_xp_boost * 100:.1f}%")
        self.combined_corruption_reduction_label.setText(f"Corruption Reduction: +{corruption_reduction_buff * 100:.1f}%")
        self.combined_daily_streak_chance_label.setText(f"Daily Streak Save Chance: +{daily_streak_chance_buff * 100:.1f}%")


    def _add_new_skill(self):
        skill_name = self.new_skill_input.text().strip().title()
        if not skill_name:
            QMessageBox.warning(self, "Error", "Skill name cannot be empty.")
            return

        if self.game_manager.add_new_skill(skill_name):
            self.new_skill_input.clear()
            self._update_skills_chart()
        else:
            QMessageBox.warning(self, "Error", "Could not add skill. It may already exist.")

    def _update_skills_chart(self):
        skills = self.game_manager.player.skills
        self.skills_ax.clear()

        desired_skills = ["Strength", "Endurance", "Durability", "Intellect", "Faith"]
        labels_for_pie = []
        values = []

        for skill_name in desired_skills:
            if skill_name in skills and skills[skill_name]['xp'] > 0:
                labels_for_pie.append(skill_name)
                values.append(skills[skill_name]['xp'])

        if not values:
            self.skills_ax.text(0.5, 0.5, "No XP in core skills.", ha='center', va='center', transform=self.skills_ax.transAxes)
            self.skills_canvas.draw()
            return

        total_xp = sum(values)
        if total_xp == 0:
            self.skills_ax.text(0.5, 0.5, "No XP in core skills.", ha='center', va='center', transform=self.skills_ax.transAxes)
            self.skills_canvas.draw()
            return

        formatted_labels = [f"{label}: {val} ({(val/total_xp)*100:.1f}%)" for label, val in zip(labels_for_pie, values)]
        colors = ['#8A2BE2', '#66CDAA', '#1E90FF', '#FF69B4', '#FFD700']

        wedges, texts = self.skills_ax.pie(values,
                                           labels=formatted_labels,
                                           autopct=None,
                                           startangle=90,
                                           wedgeprops=dict(width=0.3),
                                           colors=colors,
                                           labeldistance=1.05)
        self.skills_ax.text(0, 0, f"{total_xp}", ha='center', va='center', fontsize=24)
        self.skills_ax.axis('equal')
        self.skills_figure.tight_layout()
        self.skills_canvas.draw()

    # --- QUESTS TAB (REVAMPED) ---
    def _create_quests_tab(self):
        self.quests_tab = QWidget()
        main_layout = QHBoxLayout(self.quests_tab)
        self.splitter = QSplitter(Qt.Horizontal)

        # Left side: Quest Generation and Lists
        left_scroll_area = QScrollArea()
        left_scroll_area.setWidgetResizable(True)
        left_widget_content = QWidget()
        left_layout = QVBoxLayout(left_widget_content)
        left_layout.setAlignment(Qt.AlignTop)
        left_scroll_area.setWidget(left_widget_content)

        # --- Daily Tasks Box ---
        daily_tasks_box = QFrame(); daily_tasks_box.setFrameShape(QFrame.StyledPanel)
        daily_tasks_layout = QVBoxLayout(daily_tasks_box)
        daily_tasks_layout.addWidget(QLabel("<b>✔️ Daily Tasks:</b>"))
        self.daily_tasks_list_layout = QVBoxLayout()
        daily_tasks_layout.addLayout(self.daily_tasks_list_layout)
        left_layout.addWidget(daily_tasks_box)


        # --- Generation Box ---
        generation_box = QFrame(); generation_box.setFrameShape(QFrame.StyledPanel)
        generation_layout = QVBoxLayout(generation_box)
        generation_layout.addWidget(QLabel("<b>Generate a New Main Quest:</b>"))

        self.quest_category_combo = QComboBox()
        self.quest_category_combo.addItems(["", "Training", "Intellect Conditioning", "Faith Goal", "Long-Term Project"])
        self.quest_category_combo.currentTextChanged.connect(self._on_quest_category_change)
        generation_layout.addWidget(self.quest_category_combo)

        # REVAMPED: Container for training specific inputs
        self.training_inputs_container = QWidget()
        training_inputs_layout = QFormLayout(self.training_inputs_container) # Use QFormLayout for label-widget pairs
        training_inputs_layout.setContentsMargins(0, 0, 0, 0)
        
        # Difficulty selection
        self.quest_difficulty_combo = QComboBox()
        self.quest_difficulty_combo.addItems(["", "Easy", "Mediocre", "Difficult", "Very Difficult"])
        training_inputs_layout.addRow("Difficulty:", self.quest_difficulty_combo)

        # Training Part selection
        self.quest_training_part_combo = QComboBox()
        self.quest_training_part_combo.addItems([
            "", 
            "Strength (Upper Body)", "Strength (Lower Body)", "Strength (Core)", "Strength (Full Body)",
            "Endurance", 
            "Durability (Core)", "Durability (Lower)", "Durability (Upper)"
        ])
        training_inputs_layout.addRow("Training Part:", self.quest_training_part_combo)

        # Sets and Reps for Strength/Durability
        self.sets_reps_widget = QWidget()
        sets_reps_layout = QHBoxLayout(self.sets_reps_widget)
        sets_reps_layout.setContentsMargins(0, 0, 0, 0)
        self.quest_sets_input = QSpinBox(); self.quest_sets_input.setRange(1, 100); self.quest_sets_input.setValue(4)
        self.quest_reps_input = QSpinBox(); self.quest_reps_input.setRange(1, 100); self.quest_reps_input.setValue(12)
        sets_reps_layout.addWidget(QLabel("Sets:"))
        sets_reps_layout.addWidget(self.quest_sets_input)
        sets_reps_layout.addWidget(QLabel("Reps:"))
        sets_reps_layout.addWidget(self.quest_reps_input)
        training_inputs_layout.addRow(self.sets_reps_widget)

        # Duration for Endurance
        self.duration_widget = QWidget()
        duration_layout = QHBoxLayout(self.duration_widget)
        duration_layout.setContentsMargins(0, 0, 0, 0)
        self.quest_duration_input = QSpinBox(); self.quest_duration_input.setRange(5, 240); self.quest_duration_input.setValue(30)
        duration_layout.addWidget(QLabel("Duration (minutes):"))
        duration_layout.addWidget(self.quest_duration_input)
        training_inputs_layout.addRow(self.duration_widget)
        
        # Connect signals to the new update function
        self.quest_difficulty_combo.currentTextChanged.connect(self._update_training_quest_ui)
        self.quest_training_part_combo.currentTextChanged.connect(self._update_training_quest_ui)

        generation_layout.addWidget(self.training_inputs_container)
        
        # Other quest widgets
        self.long_term_quest_widget = QWidget()
        long_term_layout = QGridLayout(self.long_term_quest_widget)
        long_term_layout.setContentsMargins(0,0,0,0)
        long_term_layout.addWidget(QLabel("Project Name:"), 0, 0)
        self.quest_project_name_input = QLineEdit()
        long_term_layout.addWidget(self.quest_project_name_input, 0, 1)
        long_term_layout.addWidget(QLabel("Due Date:"), 1, 0)
        self.quest_due_date_input = QDateEdit(calendarPopup=True)
        self.quest_due_date_input.setDate(QDate.currentDate().addDays(30))
        long_term_layout.addWidget(self.quest_due_date_input, 1, 1)
        generation_layout.addWidget(self.long_term_quest_widget)

        self.intellect_goal_widgets = QWidget()
        intellect_layout = QGridLayout(self.intellect_goal_widgets)
        intellect_layout.setContentsMargins(0,0,0,0)
        self.quest_int_sub_cat_combo = QComboBox()
        self.quest_int_sub_cat_combo.addItems(list(self.game_manager.intellect_conditioning_activities.keys()))
        self.quest_int_sub_cat_combo.currentTextChanged.connect(self._on_intellect_sub_category_change)
        intellect_layout.addWidget(QLabel("Type:"), 0, 0)
        intellect_layout.addWidget(self.quest_int_sub_cat_combo, 0, 1)
        self.quest_activity_combo = QComboBox()
        intellect_layout.addWidget(QLabel("Activity:"), 1, 0)
        intellect_layout.addWidget(self.quest_activity_combo, 1, 1)
        generation_layout.addWidget(self.intellect_goal_widgets)

        button_layout = QHBoxLayout()
        self.generate_quest_button = QPushButton("Generate Main Quest")
        self.generate_quest_button.clicked.connect(self._generate_new_main_quest)
        button_layout.addWidget(self.generate_quest_button)
        self.generate_side_quest_button = QPushButton("Generate Side")
        self.generate_side_quest_button.clicked.connect(self._generate_new_side_quest)
        button_layout.addWidget(self.generate_side_quest_button)
        generation_layout.addLayout(button_layout)

        left_layout.addWidget(generation_box)
        
        # --- Quest Lists ---
        self.main_quests_list = QListWidget()
        self.side_quests_list = QListWidget()
        self.main_quests_list.itemSelectionChanged.connect(self._show_quest_details)
        self.side_quests_list.itemSelectionChanged.connect(self._show_quest_details)

        self.main_quests_label = QLabel(f"<b>🎯 Main Quests (Last Workout: {self.game_manager.player.last_workout_type or 'None'})</b>")
        left_layout.addWidget(self.main_quests_label)
        left_layout.addWidget(self.main_quests_list)
        left_layout.addWidget(QLabel("<b>📜 Side Quests:</b>"))
        left_layout.addWidget(self.side_quests_list)
        self.complete_quest_button = QPushButton("Complete Selected Quest")
        self.complete_quest_button.clicked.connect(self._complete_selected_quest)
        left_layout.addWidget(self.complete_quest_button)
        left_layout.addStretch(1)

        # Right side: Quest Details
        self.quest_details_panel = QFrame(); self.quest_details_panel.setFrameShape(QFrame.StyledPanel)
        details_layout = QVBoxLayout(self.quest_details_panel)
        self.details_title = QLabel(); self.details_title.setWordWrap(True)
        self.details_rewards_label = QLabel(); self.details_rewards_label.setWordWrap(True)
        self.details_steps_label = QLabel(); self.details_steps_label.setWordWrap(True)
        self.details_duration_input_label = QLabel("Enter duration completed (minutes):")
        self.details_duration_input = QSpinBox(); self.details_duration_input.setRange(0, 999)
        self.details_confirm_duration_button = QPushButton("Confirm Completion")
        self.details_confirm_duration_button.clicked.connect(self._confirm_endurance_quest_completion)

        details_layout.addWidget(self.details_title)
        details_layout.addWidget(self.details_rewards_label)
        details_layout.addWidget(self.details_steps_label)
        details_layout.addWidget(self.details_duration_input_label)
        details_layout.addWidget(self.details_duration_input)
        details_layout.addWidget(self.details_confirm_duration_button)
        details_layout.addStretch(1)
        self.quest_details_panel.setVisible(False)

        self.splitter.addWidget(left_scroll_area)
        self.splitter.addWidget(self.quest_details_panel)
        self.splitter.setSizes([700, 300])
        main_layout.addWidget(self.splitter)
        
        # Initial state setup
        self._on_quest_category_change("")

    def _on_quest_category_change(self, text):
        # Hide all specific input widgets first
        self.training_inputs_container.setVisible(False)
        self.intellect_goal_widgets.setVisible(False)
        self.long_term_quest_widget.setVisible(False)
        self.generate_quest_button.setText("Generate Main Quest") # Default text
        self.generate_quest_button.setEnabled(False)

        if text == "Training":
            self.training_inputs_container.setVisible(True)
            self.generate_quest_button.setText("Generate Workout Plan")
            # Reset training fields
            self.quest_difficulty_combo.setCurrentIndex(0)
            self.quest_training_part_combo.setCurrentIndex(0)
            self._update_training_quest_ui() # Update UI based on reset fields
        elif text == "Intellect Conditioning":
            self.intellect_goal_widgets.setVisible(True)
            self._on_intellect_sub_category_change(self.quest_int_sub_cat_combo.currentText())
            self.generate_quest_button.setEnabled(True)
        elif text == "Faith Goal":
            self.generate_quest_button.setEnabled(True)
        elif text == "Long-Term Project":
            self.long_term_quest_widget.setVisible(True)
            # Could add a check for project name to enable button
            self.generate_quest_button.setEnabled(True) # For now, enable it

    def _update_training_quest_ui(self):
        """Shows/hides training-specific widgets and enables/disables the generate button."""
        training_part = self.quest_training_part_combo.currentText()
        difficulty = self.quest_difficulty_combo.currentText()

        # Default state
        self.sets_reps_widget.setVisible(False)
        self.duration_widget.setVisible(False)
        self.generate_quest_button.setEnabled(False)

        if not training_part or not difficulty:
            return # Not enough info to proceed

        if "Strength" in training_part or "Durability" in training_part:
            self.sets_reps_widget.setVisible(True)
            self.generate_quest_button.setEnabled(True)
        elif "Endurance" in training_part:
            self.duration_widget.setVisible(True)
            self.generate_quest_button.setEnabled(True)

    def _on_intellect_sub_category_change(self, text):
        self.quest_activity_combo.clear()
        self.quest_activity_combo.addItems(self.game_manager.intellect_conditioning_activities.get(text, []))
        self.generate_quest_button.setEnabled(True)


    def _generate_new_main_quest(self):
        category = self.quest_category_combo.currentText()
        if not category:
            QMessageBox.warning(self, "Selection Needed", "Please select a quest category.")
            return

        details = {}
        end_of_day = datetime.datetime.now().replace(hour=23, minute=59, second=59)
        details['due_date'] = end_of_day.isoformat()
        details['steps'] = "Complete the generated objective."

        if category == "Training":
            details['difficulty'] = self.quest_difficulty_combo.currentText()
            details['training_part'] = self.quest_training_part_combo.currentText()

            if not details['difficulty'] or not details['training_part']:
                QMessageBox.warning(self, "Input Needed", "Please select a difficulty and training part.")
                return

            if "Strength" in details['training_part'] or "Durability" in details['training_part']:
                details['sets'] = self.quest_sets_input.value()
                details['reps'] = self.quest_reps_input.value()
            elif "Endurance" in details['training_part']:
                details['duration'] = self.quest_duration_input.value()

        elif category == "Intellect Conditioning":
            details['activity'] = self.quest_activity_combo.currentText()
            if not details['activity']:
                 QMessageBox.warning(self, "Input Needed", "Please select an intellect activity."); return
        elif category == "Faith Goal":
            pass # No extra details needed
        elif category == "Long-Term Project":
            due_datetime = datetime.datetime.combine(self.quest_due_date_input.date().toPyDate(), datetime.time(23, 59, 59))
            details['due_date'] = due_datetime.isoformat()
            details['project_name'] = self.quest_project_name_input.text()
            if not details['project_name']:
                 QMessageBox.warning(self, "Input Needed", "Please provide a project name."); return

        message = self.game_manager.generate_quest(category, details=details)
        if "Failed" in message or "There are no more variations" in message:
            QMessageBox.warning(self, "Quest Generation Failed", message)
        else:
            QMessageBox.information(self, "Quest Generation", message)
        self._update_quests_display()

    def _generate_new_side_quest(self):
        message = self.game_manager.generate_side_quest()
        QMessageBox.information(self, "Side Quest Generation", message)
        self._update_quests_display()

    def _update_quests_display(self):
        self.main_quests_list.clear()
        self.side_quests_list.clear()
        quests = self.game_manager.get_available_quests()

        self.main_quests_label.setText(f"<b>🎯 Main Quests (Last Workout: {self.game_manager.player.last_workout_type or 'None'})</b>")

        main_quests_exist = any(q.get('quest_type') != 'side' for q in quests)
        side_quests_exist = any(q.get('quest_type') == 'side' for q in quests)

        for quest in quests:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, quest)
            if quest.get('quest_type') == 'side': self.side_quests_list.addItem(item)
            else: self.main_quests_list.addItem(item)

        if not main_quests_exist: self.main_quests_list.addItem("No active main quests.")
        if not side_quests_exist: self.side_quests_list.addItem("No active side quests.")
        self._update_quest_timers_text()
        self._update_daily_tasks_display() # Update daily tasks here

    def _update_quest_timers_text(self):
        now = datetime.datetime.now()
        for list_widget in [self.main_quests_list, self.side_quests_list]:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                quest_data = item.data(Qt.UserRole)
                if not quest_data: continue
                due_date_str = quest_data.get('due_date')
                time_left_str = ""
                if due_date_str:
                    try:
                        due_date = datetime.datetime.fromisoformat(due_date_str)
                        time_left = due_date - now
                        if time_left.total_seconds() < 0:
                            time_left_str = " (Overdue)"; item.setForeground(QColor('red'))
                        else:
                            days, rem = divmod(time_left.total_seconds(), 86400)
                            hours, rem = divmod(rem, 3600)
                            minutes, _ = divmod(rem, 60)
                            time_left_str = f" (Due: {int(days)}d {int(hours)}h {int(minutes)}m)"
                    except (ValueError, TypeError): time_left_str = " (Invalid Date)"
                item.setText(f"{quest_data['name']}{time_left_str}")

    def _update_daily_tasks_display(self):
        # Clear existing checkboxes
        for i in reversed(range(self.daily_tasks_list_layout.count())):
            widget = self.daily_tasks_list_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self._block_daily_task_signal = True # Block signals during update

        for task_name in self.game_manager.daily_task_templates:
            checkbox = QCheckBox(task_name)
            # Check if the task is already completed for today in player data
            checkbox.setChecked(self.game_manager.player.daily_tasks.get(task_name, False))
            checkbox.stateChanged.connect(partial(self._on_daily_task_checked, task_name))
            self.daily_tasks_list_layout.addWidget(checkbox)
        self._block_daily_task_signal = False # Re-enable signals


    def _on_daily_task_checked(self, task_name, state):
        if self._block_daily_task_signal: return # Prevent recursive calls

        is_complete = bool(state) # 0 for unchecked, 2 for checked
        message = self.game_manager.complete_daily_task(task_name, is_complete)
        if message:
            QMessageBox.information(self, "Daily Task", message)
        self._update_player_stats_display()


    def _show_quest_details(self):
        selected_item = None
        if self.main_quests_list.selectedItems():
            selected_item = self.main_quests_list.selectedItems()[0]
            self.side_quests_list.clearSelection() # Clear other list's selection
        elif self.side_quests_list.selectedItems():
            selected_item = self.side_quests_list.selectedItems()[0]
            self.main_quests_list.clearSelection() # Clear other list's selection

        if selected_item and selected_item.data(Qt.UserRole):
            quest = selected_item.data(Qt.UserRole)
            self.details_title.setText(f"<h3>{quest['name']}</h3>")
            rewards = f"⚡️ {quest.get('xp_reward', 0)} XP, 💰 {quest.get('coin_reward', 0)} Coins"
            if quest.get('skill_reward'):
                rewards += f", ⭐ +{quest['skill_reward']['amount']} {quest['skill_reward']['skill']} XP"
            self.details_rewards_label.setText(rewards)
            steps_html = quest.get('steps', 'No steps.').replace('\n', '<br>')
            self.details_steps_label.setText(f"<b>Steps:</b><br>{steps_html}")

            # Show/hide duration input for Endurance quests
            if quest.get('skill_reward', {}).get('skill') == 'Endurance':
                self.details_duration_input_label.setVisible(True)
                self.details_duration_input.setVisible(True)
                self.details_confirm_duration_button.setVisible(True)
                self.complete_quest_button.setVisible(False) # Hide general complete button
                target_duration = quest.get('duration_target', 0)
                self.details_duration_input.setRange(0, target_duration)
                self.details_duration_input_label.setText(f"Enter duration completed (minutes, max {target_duration}):")
            else:
                self.details_duration_input_label.setVisible(False)
                self.details_duration_input.setVisible(False)
                self.details_confirm_duration_button.setVisible(False)
                self.complete_quest_button.setVisible(True)


            self.quest_details_panel.setVisible(True)
        else:
            self.quest_details_panel.setVisible(False)

    def _complete_selected_quest(self):
        selected_item = None
        if self.main_quests_list.selectedItems():
            selected_item = self.main_quests_list.selectedItems()[0]
        elif self.side_quests_list.selectedItems():
            selected_item = self.side_quests_list.selectedItems()[0]

        if selected_item and selected_item.data(Qt.UserRole):
            quest_data = selected_item.data(Qt.UserRole)
            if quest_data.get('skill_reward', {}).get('skill') == 'Endurance':
                QMessageBox.warning(self, "Endurance Quest", "Please use the 'Confirm Completion' button and enter duration for Endurance quests.")
                return

            quest_name = quest_data['name']
            message = self.game_manager.complete_quest(quest_name)
            QMessageBox.information(self, "Quest Completion", message)
            self.quest_details_panel.setVisible(False)
            self._update_all_displays()
        else:
            QMessageBox.warning(self, "No Quest Selected", "Please select a quest to complete.")

    def _confirm_endurance_quest_completion(self):
        selected_item = None
        if self.main_quests_list.selectedItems():
            selected_item = self.main_quests_list.selectedItems()[0]
        elif self.side_quests_list.selectedItems():
            selected_item = self.side_quests_list.selectedItems()[0]

        if selected_item and selected_item.data(Qt.UserRole):
            quest_data = selected_item.data(Qt.UserRole)
            if quest_data.get('skill_reward', {}).get('skill') == 'Endurance':
                completed_duration = self.details_duration_input.value()
                quest_name = quest_data['name']
                message = self.game_manager.complete_quest(quest_name, completed_duration=completed_duration)
                QMessageBox.information(self, "Endurance Quest Completion", message)
                self.quest_details_panel.setVisible(False)
                self._update_all_displays()
            else:
                QMessageBox.warning(self, "Invalid Quest Type", "This button is only for Endurance quests.")
        else:
            QMessageBox.warning(self, "No Quest Selected", "Please select an Endurance quest to complete.")


    # --- PETS TAB ---
    def _create_pets_tab(self):
        self.pets_tab = QWidget()
        layout = QVBoxLayout(self.pets_tab)
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("<b>🐾 Your Pets:</b>"))
        top_layout.addStretch()
        self.pet_food_label = QLabel("Pet Food: 0")
        top_layout.addWidget(self.pet_food_label)
        layout.addLayout(top_layout)
        self.pets_list_widget = QListWidget()
        layout.addWidget(self.pets_list_widget)
        self.pets_list_widget.itemSelectionChanged.connect(self._show_pet_details)
        self.pet_details_label = QLabel("Select a pet to see details.", self)
        self.pet_details_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.pet_details_label)
        pet_action_layout = QHBoxLayout()
        self.pet_the_pet_button = QPushButton("Pet")
        self.pet_the_pet_button.clicked.connect(self._pet_selected_pet)
        pet_action_layout.addWidget(self.pet_the_pet_button)
        self.feed_pet_button = QPushButton("Feed Pet")
        self.feed_pet_button.clicked.connect(self._feed_selected_pet)
        pet_action_layout.addWidget(self.feed_pet_button)
        self.play_with_pet_button = QPushButton("Play with Pet")
        self.play_with_pet_button.clicked.connect(self._play_with_selected_pet)
        pet_action_layout.addWidget(self.play_with_pet_button)
        layout.addLayout(pet_action_layout)
        layout.addStretch(1)

    def _update_pets_display(self):
        self.pets_list_widget.clear()
        self.pet_food_label.setText(f"🍖 Pet Food: {self.game_manager.player.pet_food}")
        pets = self.game_manager.player.pets
        if not pets:
            self.pets_list_widget.addItem("You don't have any pets yet. Buy one from the shop!")
            self.pet_details_label.setText("No pets owned.")
        else:
            for pet_name in pets:
                pet_data = self.game_manager.get_pet_data(pet_name)
                if pet_data:
                    item_text = f"{pet_data['Name']} (Level: {pet_data['Level']}, XP: {pet_data['XP']}/{pet_data['XP_to_Evolve']})"
                    item = QListWidgetItem(item_text); item.setData(Qt.UserRole, pet_name)
                    self.pets_list_widget.addItem(item)
            if self.pets_list_widget.currentRow() == -1: self.pets_list_widget.setCurrentRow(0)
            self._show_pet_details()

    def _show_pet_details(self):
        selected_items = self.pets_list_widget.selectedItems()
        if not selected_items:
            self.pet_details_label.setText("Select a pet to see details."); return
        pet_name = selected_items[0].data(Qt.UserRole)
        pet_data = self.game_manager.get_pet_data(pet_name)
        if pet_data:
            _, _, benefit_desc = self.game_manager.get_pet_current_benefit(pet_name)
            details = (f"<b>Name:</b> {pet_data['Name']} | <b>Type:</b> {pet_data['Type']}<br>"
                       f"<b>Level:</b> {pet_data['Level']} | <b>XP:</b> {pet_data['XP']}/{pet_data['XP_to_Evolve']}<br>"
                       f"<b>Benefit:</b> {benefit_desc}")
            now = datetime.datetime.now()
            cooldown_end_str = self.game_manager.player.pet_cooldowns.get(pet_name)
            if cooldown_end_str and now < datetime.datetime.fromisoformat(cooldown_end_str):
                remaining = datetime.datetime.fromisoformat(cooldown_end_str) - now
                details += f"<br><i>Petting Cooldown: {str(remaining).split('.')[0]} remaining</i>"
            play_cooldown_end_str = self.game_manager.player.play_cooldowns.get(pet_name)
            if play_cooldown_end_str and now < datetime.datetime.fromisoformat(play_cooldown_end_str):
                remaining = datetime.datetime.fromisoformat(play_cooldown_end_str) - now
                details += f"<br><i>Playing Cooldown: {str(remaining).split('.')[0]} remaining</i>"
            self.pet_details_label.setText(details)
        else: self.pet_details_label.setText(f"Details for {pet_name} not found.")

    def _pet_selected_pet(self):
        if self.pets_list_widget.selectedItems():
            message = self.game_manager.pet_a_pet(self.pets_list_widget.selectedItems()[0].data(Qt.UserRole))
            QMessageBox.information(self, "Pet Interaction", message); self._update_all_displays()
        else: QMessageBox.warning(self, "No Pet Selected", "Please select a pet to pet.")
    def _feed_selected_pet(self):
        if self.pets_list_widget.selectedItems():
            message = self.game_manager.feed_pet(self.pets_list_widget.selectedItems()[0].data(Qt.UserRole))
            QMessageBox.information(self, "Feed Pet", message); self._update_all_displays()
        else: QMessageBox.warning(self, "No Pet Selected", "Please select a pet to feed.")
    def _play_with_selected_pet(self):
        if self.pets_list_widget.selectedItems():
            message = self.game_manager.play_with_pet(self.pets_list_widget.selectedItems()[0].data(Qt.UserRole))
            QMessageBox.information(self, "Play With Pet", message); self._update_all_displays()
        else: QMessageBox.warning(self, "No Pet Selected", "Please select a pet to play with.")

    # --- SHOP TAB (REVAMPED WITH CART) ---
    def _create_shop_tab(self):
        self.shop_tab = QWidget()
        layout = QHBoxLayout(self.shop_tab)

        # Left side: Item listings
        item_panel = QFrame(); item_panel.setFrameShape(QFrame.StyledPanel)
        item_layout = QVBoxLayout(item_panel)
        item_layout.addWidget(QLabel("<h2>🛒 Shop</h2>"))
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True)
        item_layout.addWidget(scroll_area)
        self.shop_content_widget = QWidget()
        self.shop_grid_layout = QGridLayout(self.shop_content_widget)
        scroll_area.setWidget(self.shop_content_widget)

        # Right side: Cart
        cart_panel = QFrame(); cart_panel.setFrameShape(QFrame.StyledPanel)
        cart_layout = QVBoxLayout(cart_panel)
        cart_layout.addWidget(QLabel("<h3>Shopping Cart</h3>"))
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Qty", "Cost", ""])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        cart_layout.addWidget(self.cart_table)

        self.cart_total_label = QLabel("<b>Total: 0 Coins</b>")
        self.cart_total_label.setAlignment(Qt.AlignRight)
        cart_layout.addWidget(self.cart_total_label)

        cart_buttons_layout = QHBoxLayout()
        self.purchase_cart_button = QPushButton("Purchase All")
        self.purchase_cart_button.clicked.connect(self._purchase_cart)
        self.clear_cart_button = QPushButton("Clear Cart")
        self.clear_cart_button.clicked.connect(self._clear_cart)
        cart_buttons_layout.addWidget(self.clear_cart_button)
        cart_buttons_layout.addWidget(self.purchase_cart_button)
        cart_layout.addLayout(cart_buttons_layout)

        layout.addWidget(item_panel, 2) # Give more space to items
        layout.addWidget(cart_panel, 1) # Give less space to cart

    def _update_shop_display(self):
        # Clear existing item cards from the grid
        while self.shop_grid_layout.count():
            self.shop_grid_layout.takeAt(0).widget().deleteLater()

        shop_items = self.game_manager.get_shop_items()
        row, col = 0, 0
        for item in shop_items:
            # Create a "card" for each item
            card = QFrame(); card.setFrameShape(QFrame.StyledPanel)
            card_layout = QVBoxLayout(card)

            name_label = QLabel(f"{item.get('emoji', '')} <b>{item['name']}</b>")
            desc_label = QLabel(item['description']); desc_label.setWordWrap(True)
            cost_label = QLabel(f"💰 {item['cost']} Coins")

            card_layout.addWidget(name_label)
            card_layout.addWidget(desc_label)
            card_layout.addWidget(cost_label)

            # Add quantity selector and "Add to Cart" button
            add_to_cart_layout = QHBoxLayout()
            quantity_spin = QSpinBox(); quantity_spin.setRange(1, 99); quantity_spin.setFixedWidth(50)
            add_button = QPushButton("Add to Cart")
            add_button.clicked.connect(partial(self._add_to_cart, item, quantity_spin))

            add_to_cart_layout.addWidget(QLabel("Qty:"))
            add_to_cart_layout.addWidget(quantity_spin)
            add_to_cart_layout.addWidget(add_button)
            card_layout.addLayout(add_to_cart_layout)

            self.shop_grid_layout.addWidget(card, row, col)
            col += 1
            if col > 1: # Create a 2-column layout
                col = 0
                row += 1

        self._update_cart_display()

    def _add_to_cart(self, item, quantity_spin):
        item_name = item['name']
        quantity = quantity_spin.value()

        # Add item and quantity to the cart dictionary
        if item_name in self.shopping_cart:
            self.shopping_cart[item_name] += quantity
        else:
            self.shopping_cart[item_name] = quantity

        self._update_cart_display()
        quantity_spin.setValue(1) # Reset for next use

    def _update_cart_display(self):
        self.cart_table.setRowCount(0) # Clear the table
        total_cost = 0

        shop_items = self.game_manager.get_shop_items()

        # Repopulate the table from the shopping_cart dictionary
        for item_name, quantity in self.shopping_cart.items():
            item_data = next((i for i in shop_items if i['name'] == item_name), None)
            if item_data:
                row_position = self.cart_table.rowCount()
                self.cart_table.insertRow(row_position)

                cost = item_data['cost'] * quantity
                total_cost += cost

                self.cart_table.setItem(row_position, 0, QTableWidgetItem(item_name))
                self.cart_table.setItem(row_position, 1, QTableWidgetItem(str(quantity)))
                self.cart_table.setItem(row_position, 2, QTableWidgetItem(f"{cost}"))

                # Add a "Remove" button to each row
                remove_button = QPushButton("Remove")
                remove_button.clicked.connect(partial(self._remove_from_cart, item_name))
                self.cart_table.setCellWidget(row_position, 3, remove_button)

        self.cart_total_label.setText(f"<b>Total: {total_cost} Coins</b>")
        # Enable purchase button only if cart has items and player has enough coins
        self.purchase_cart_button.setEnabled(total_cost > 0 and self.game_manager.player.coins >= total_cost)

    def _remove_from_cart(self, item_name):
        if item_name in self.shopping_cart:
            del self.shopping_cart[item_name]
            self._update_cart_display()

    def _clear_cart(self):
        self.shopping_cart.clear()
        self._update_cart_display()

    def _purchase_cart(self):
        if not self.shopping_cart:
            QMessageBox.warning(self, "Empty Cart", "Your shopping cart is empty.")
            return

        success, message = self.game_manager.purchase_cart(self.shopping_cart)

        if success:
            QMessageBox.information(self, "Purchase Successful", message)
            self._clear_cart()
            self._update_all_displays()
        else:
            QMessageBox.warning(self, "Purchase Failed", message)

    # --- FORGE TAB ---
    def _create_forge_tab(self):
        self.forge_tab = QWidget()
        layout = QHBoxLayout(self.forge_tab)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("<b>Equipped Gear</b>"))
        self.forge_equipped_list = QListWidget()
        left_layout.addWidget(self.forge_equipped_list)
        left_layout.addWidget(QLabel("<b>Inventory Gear</b>"))
        self.forge_inventory_list = QListWidget()
        left_layout.addWidget(self.forge_inventory_list)

        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_panel)
        self.forge_item_name = QLabel("Select an item to upgrade")
        self.forge_item_name.setFont(QFont("Arial", 14, QFont.Bold))
        self.forge_item_details = QLabel()
        self.forge_item_details.setWordWrap(True)

        self.enchant_button = QPushButton("Enchant Item")
        self.enchant_button.clicked.connect(self._enchant_selected_item)
        self.transcend_item_button = QPushButton("Transcend Item")
        self.transcend_item_button.clicked.connect(self._transcend_selected_item)
        # New button for rolling extra effect
        self.roll_extra_effect_button = QPushButton("Roll Extra Effect (1500 Coins)")
        self.roll_extra_effect_button.clicked.connect(self._roll_extra_effect_on_item)
        self.roll_extra_effect_button.setVisible(False)

        # New button for selling item
        self.sell_item_button = QPushButton("Sell Item")
        self.sell_item_button.clicked.connect(self._sell_selected_item)
        self.sell_item_button.setVisible(False) # Initially hidden


        right_layout.addWidget(self.forge_item_name)
        right_layout.addWidget(self.forge_item_details)
        right_layout.addStretch()
        right_layout.addWidget(self.enchant_button)
        right_layout.addWidget(self.transcend_item_button)
        right_layout.addWidget(self.roll_extra_effect_button) # Add the new button
        right_layout.addWidget(self.sell_item_button) # Add the sell button


        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 1)

        # Connect item selection signals to the detail display
        self.forge_equipped_list.itemClicked.connect(self._show_forge_item_details)
        self.forge_inventory_list.itemClicked.connect(self._show_forge_item_details)

    def _update_forge_display(self):
        self.forge_equipped_list.clear()
        self.forge_inventory_list.clear()
        self._clear_forge_details()

        for slot, item in self.game_manager.player.gear.items():
            if item:
                list_item = QListWidgetItem(f"{item['name']} ({item['type']})")
                if item.get('transcended'): list_item.setForeground(QColor('purple'))
                list_item.setData(Qt.UserRole, item)
                self.forge_equipped_list.addItem(list_item)

        for item in self.game_manager.player.inventory:
            list_item = QListWidgetItem(f"{item['name']} ({item['type']})")
            if item.get('transcended'): 
                list_item.setForeground(QColor('purple'))
            list_item.setData(Qt.UserRole, item) # Ensure item data is stored
            self.forge_inventory_list.addItem(list_item)

    def _show_forge_item_details(self, item):
        # Clear selection in the other list to ensure only one item is selected
        sender = self.sender()
        if sender == self.forge_equipped_list:
            self.forge_inventory_list.clearSelection()
        else: # sender == self.forge_inventory_list
            self.forge_equipped_list.clearSelection()

        item_data = item.data(Qt.UserRole)
        if not item_data:
            self._clear_forge_details()
            return

        self.forge_item_name.setText(item_data['name'])

        details = ""
        is_transcended = item_data.get('transcended', False)
        enchant_level = item_data.get('enchant_level', 0)

        buffs_display = []
        if 'buff' in item_data:
            buff_type = item_data['buff']['type'].replace('_', ' ').title()
            buff_value = item_data['buff']['value']
            buff_value_str = f"{buff_value * 100:.2f}%" if 'gain' in buff_type.lower() or 'reduction' in buff_type.lower() else str(buff_value)
            buffs_display.append(f"Primary: +{buff_value_str} {buff_type}")

        if 'extra_effect' in item_data and item_data['extra_effect']:
            effect = item_data['extra_effect']
            effect_type = effect['type'].replace('_', ' ').title()
            effect_value = effect['value']
            effect_value_str = f"{effect_value * 100:.2f}%" if 'gain' in effect_type.lower() or 'reduction' in effect_type.lower() else str(effect_value)
            buffs_display.append(f"Extra: +{effect_value_str} {effect_type}")

        details += "<b>Buffs:</b><br>" + "<br>".join(buffs_display) if buffs_display else "<b>No specific buffs.</b><br>"

        # Display requirements
        requirements = item_data.get('requirements', {})
        if requirements:
            req_strings = []
            for skill, required_xp in requirements.items():
                player_skill_xp = self.game_manager.player.skills.get(skill, {}).get('xp', 0)
                color = "green" if player_skill_xp >= required_xp else "red"
                req_strings.append(f"<span style='color:{color}'>{skill}: {player_skill_xp}/{required_xp}</span>")
            details += "<br><b>Requirements:</b> " + ", ".join(req_strings)
        
        can_equip, _ = self.game_manager.check_gear_requirements(item_data)

        # Always show enchant and transcend buttons, but enable/disable based on conditions
        self.enchant_button.setVisible(True)
        self.transcend_item_button.setVisible(True)
        self.roll_extra_effect_button.setVisible(False) # Hide by default, show if transcended and no extra effect

        next_level_cost = 100 * (enchant_level + 1)
        details += f"<br><b>Enchant Level:</b> +{enchant_level}\n"
        details += f"<b>Next Enchant Cost:</b> {next_level_cost} Coins\n"
        self.enchant_button.setEnabled(self.game_manager.player.coins >= next_level_cost)
        self.enchant_button.setText(f"Enchant (+{enchant_level+1}) for {next_level_cost} Coins")

        transcend_cost = 1000
        details += f"<b>Transcend Cost:</b> {transcend_cost} Coins\n"
        self.transcend_item_button.setEnabled(self.game_manager.player.coins >= transcend_cost)
        self.transcend_item_button.setText(f"Transcend Item for {transcend_cost} Coins")

        if is_transcended:
            details += "<br><b style='color:purple;'>This item is Transcended.</b><br>It will not be destroyed on character Transcendence."
            # Enchant button is still visible and enabled/disabled by cost check
            # Transcend button is not applicable if already transcended
            self.transcend_item_button.setEnabled(False)
            self.transcend_item_button.setText("Already Transcended")
            
            if 'extra_effect' not in item_data:
                self.roll_extra_effect_button.setVisible(True)
                self.roll_extra_effect_button.setEnabled(self.game_manager.player.coins >= 1500)
            else:
                self.roll_extra_effect_button.setVisible(False) # Hide if already has extra effect

        # Sell Price
        sell_price = self.game_manager.get_sell_price(item_data)
        details += f"<br><b>Sell Price:</b> {sell_price} Coins"
        self.sell_item_button.setVisible(True)
        self.sell_item_button.setEnabled(True) # Always allow selling if an item is selected

        self.forge_item_details.setText(details)

    def _clear_forge_details(self):
        self.forge_item_name.setText("Select an item to upgrade")
        self.forge_item_details.setText("")
        self.enchant_button.setEnabled(False)
        self.enchant_button.setText("Enchant Item")
        self.transcend_item_button.setEnabled(False)
        self.transcend_item_button.setText("Transcend Item")
        self.roll_extra_effect_button.setVisible(False)
        self.roll_extra_effect_button.setEnabled(False)
        self.sell_item_button.setVisible(False) # Hide sell button when no item selected
        self.sell_item_button.setEnabled(False)

    def _get_selected_forge_item(self):
        # Check both lists for a selected item
        if self.forge_equipped_list.selectedItems():
            return self.forge_equipped_list.selectedItems()[0]
        if self.forge_inventory_list.selectedItems():
            return self.forge_inventory_list.selectedItems()[0]
        return None

    def _enchant_selected_item(self):
        item_widget = self._get_selected_forge_item()
        if not item_widget:
            QMessageBox.warning(self, "No Item", "Please select an item to enchant.")
            return

        item_name = item_widget.data(Qt.UserRole)['name']
        message = self.game_manager.enchant_gear(item_name)
        QMessageBox.information(self, "Enchanting Result", message)
        self._update_all_displays()

    def _transcend_selected_item(self):
        item_widget = self._get_selected_forge_item()
        if not item_widget:
            QMessageBox.warning(self, "No Item", "Please select an item to transcend.")
            return

        reply = QMessageBox.question(self, 'Confirm Transcend Item',
                                     "Are you sure you want to make this item permanent? This is expensive and irreversible.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            item_name = item_widget.data(Qt.UserRole)['name']
            message = self.game_manager.transcend_gear(item_name)
            QMessageBox.information(self, "Transcendence Result", message)
            self._update_all_displays()

    def _roll_extra_effect_on_item(self):
        item_widget = self._get_selected_forge_item()
        if not item_widget:
            QMessageBox.warning(self, "No Item", "Please select an item to roll an extra effect on.")
            return
        
        item_name = item_widget.data(Qt.UserRole)['name']
        message = self.game_manager.roll_extra_effect(item_name)
        QMessageBox.information(self, "Extra Effect Roll", message)
        self._update_all_displays()

    def _sell_selected_item(self):
        item_widget = self._get_selected_forge_item()
        if not item_widget:
            QMessageBox.warning(self, "No Item", "Please select an item to sell.")
            return

        item_data = item_widget.data(Qt.UserRole)
        item_name = item_data['name']
        sell_price = self.game_manager.get_sell_price(item_data) # Get price for confirmation message

        reply = QMessageBox.question(self, 'Confirm Sell Item',
                                     f"Are you sure you want to sell {item_name} for {sell_price} coins?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            message = self.game_manager.sell_gear(item_name)
            QMessageBox.information(self, "Sell Item Result", message)
            self._update_all_displays()


    # --- PUNISHMENTS TAB ---
    def _create_punishments_tab(self):
        self.punishments_tab = QWidget()
        layout = QHBoxLayout(self.punishments_tab)
        self.punishments_list = QListWidget()
        self.punishments_list.setWordWrap(True)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignTop)
        apply_btn = QPushButton("Apply Selected Punishment")
        apply_btn.clicked.connect(self._apply_selected_punishment)
        create_btn = QPushButton("Create New Punishment")
        create_btn.clicked.connect(self._create_new_punishment)
        right_layout.addWidget(apply_btn)
        right_layout.addWidget(create_btn)
        layout.addWidget(self.punishments_list, 2)
        layout.addWidget(right_panel, 1)

    def _update_punishments_display(self):
        self.punishments_list.clear()
        severity_order = {"Terrible": 0, "High": 1, "Moderate": 2, "OK": 3}
        severity_colors = {"OK": "green", "Moderate": "orange", "High": "red", "Terrible": "darkred"}

        sorted_punishments = sorted(
            self.game_manager.get_punishments(),
            key=lambda p: severity_order.get(p['severity'], 99)
        )

        for p in sorted_punishments:
            item_text = (f"<b>{p['name']}</b> ({p['severity']})<br>"
                         f"Points: {p['punishment']} | XP: -{p.get('xp_penalty', 0)} | Coins: -{p.get('coin_penalty', 0)}")
            if p.get('special_chance', 0) > 0:
                effect_name = p.get('special_effect', 'a penalty').replace('_', ' ')
                item_text += f"<br><i>({p['special_chance']*100:.0f}% chance of special penalty: {effect_name})</i>"

            item = QListWidgetItem()
            label = QLabel(item_text)
            label.setStyleSheet(f"color: {severity_colors.get(p['severity'], 'black')}; padding: 5px;")
            label.setWordWrap(True)
            # Calculate height hint based on content
            font_metrics = QFontMetrics(label.font())
            text_height = font_metrics.boundingRect(label.text()).height()
            # Estimate number of lines based on fixed width, add padding
            num_lines = label.text().count('<br>') + 1
            item.setSizeHint(QSize(self.punishments_list.width(), text_height * num_lines + 20))


            self.punishments_list.addItem(item)
            self.punishments_list.setItemWidget(item, label)
            item.setData(Qt.UserRole, p)

    def _apply_selected_punishment(self):
        selected = self.punishments_list.currentItem()
        if selected:
            punishment_name = selected.data(Qt.UserRole)['name']
            message = self.game_manager.apply_punishment(punishment_name)
            QMessageBox.warning(self, "Punishment Applied", message)
            self._update_all_displays()
        else: QMessageBox.information(self, "Info", "Select a punishment first.")

    def _create_new_punishment(self):
        dialog = CustomPunishmentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data['name']:
                self.game_manager.add_custom_punishment(data)
                self._update_punishments_display()
            else: QMessageBox.warning(self, "Input Error", "Punishment name cannot be empty.")

    # --- ACHIEVEMENTS TAB ---
    def _create_achievements_tab(self):
        self.achievements_tab = QWidget()
        layout = QVBoxLayout(self.achievements_tab)
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        content_widget = QWidget()
        self.achievements_layout = QVBoxLayout(content_widget)
        self.achievements_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(content_widget)

    def _update_achievements_display(self):
        while self.achievements_layout.count():
            self.achievements_layout.takeAt(0).widget().deleteLater()
        achievements = self.game_manager.get_achievements()
        for key, ach in achievements.items():
            card = QFrame(); card.setFrameShape(QFrame.StyledPanel)
            card_layout = QVBoxLayout(card)
            name_text = f"🏆 {ach['name']}" if ach['unlocked'] else f"🔒 {ach['name']}"
            name_label = QLabel(f"<b>{name_text}</b>")
            desc_label = QLabel(ach['description'])
            reward_label = QLabel(f"<i>Reward: {ach['reward_text']}</i>")
            if not ach['unlocked']:
                name_label.setStyleSheet("color: grey;"); desc_label.setStyleSheet("color: grey;")
                reward_label.setStyleSheet("color: grey;")
            card_layout.addWidget(name_label); card_layout.addWidget(desc_label); card_layout.addWidget(reward_label)
            self.achievements_layout.addWidget(card)

    # --- TRANSCEND TAB ---
    def _create_transcend_tab(self):
        self.transcend_tab = QWidget()
        layout = QVBoxLayout(self.transcend_tab)
        layout.setAlignment(Qt.AlignTop)
        self.transcend_title = QLabel()
        self.transcend_title.setFont(QFont("Arial", 24, QFont.Bold))
        self.transcend_title.setAlignment(Qt.AlignCenter)
        self.transcend_title.setStyleSheet("color: blue;") # Initial color
        
        # Animation for the transcend title
        # Initialize with the target property as 'font' and the QLabel as the target object
        self.transcend_animation = QPropertyAnimation(self.transcend_title, b"font")
        self.transcend_animation.setDuration(1500)
        self.transcend_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.transcend_animation.setLoopCount(-1) # Loop indefinitely


        desc = QLabel("Reset your journey to gain permanent power and unlock new potentials.")
        desc.setAlignment(Qt.AlignCenter); desc.setWordWrap(True)
        status_box = QFrame(); status_box.setFrameShape(QFrame.StyledPanel)
        status_layout = QVBoxLayout(status_box)
        status_title = QLabel("Your Progress to Divinity"); status_title.setFont(QFont("Arial", 14, QFont.Bold))
        self.transcend_progress_bar = QProgressBar()
        self.transcend_progress_label = QLabel()
        status_layout.addWidget(status_title); status_layout.addWidget(self.transcend_progress_bar)
        status_layout.addWidget(self.transcend_progress_label)
        benefits_box = QFrame(); benefits_box.setFrameShape(QFrame.StyledPanel)
        benefits_layout = QVBoxLayout(benefits_box)
        benefits_title = QLabel("Rewards of Rebirth"); benefits_title.setFont(QFont("Arial", 14, QFont.Bold))
        benefits_text = QLabel("✅ <b>Permanent Bonus:</b> +0.1x Coin Gain Multiplier per transcension.<br>"
                               "✅ <b>Transcension Gift:</b> Receive a random piece of gear.<br>"
                               "✅ <b>Temporary Buff:</b> 30 minutes of 2x XP and Coin gain.<br>"
                               "🔄 <b>Progress Reset:</b> XP, Coins, Title, Corruption, and non-Transcended gear will be reset.")
        benefits_text.setWordWrap(True)
        benefits_layout.addWidget(benefits_title); benefits_layout.addWidget(benefits_text)
        self.transcend_button = QPushButton()
        self.transcend_button.setFont(QFont("Arial", 16, QFont.Bold))
        self.transcend_button.clicked.connect(self._confirm_transcend)
        
        layout.addWidget(self.transcend_title); layout.addWidget(desc); layout.addSpacing(20)
        layout.addWidget(status_box); layout.addSpacing(20); layout.addWidget(benefits_box)
        layout.addStretch(1); layout.addWidget(self.transcend_button)

    def _update_transcend_display(self):
        player = self.game_manager.player
        required_xp = self.game_manager.get_transcend_requirement()
        self.transcend_title.setText(f"✨ Transcension (Count: {player.transcendence_count}) ✨")
        self.transcend_progress_bar.setRange(0, required_xp)
        self.transcend_progress_bar.setValue(min(player.xp, required_xp))
        self.transcend_progress_label.setText(f"XP: {player.xp} / {required_xp}")
        if player.xp >= required_xp:
            self.transcend_button.setEnabled(True); self.transcend_button.setText("✨ Transcend Now! ✨")
        else:
            self.transcend_button.setEnabled(False); self.transcend_button.setText("🔒 Divinity Awaits... 🔒")
        
        # Start/stop animation based on transcendence readiness
        if player.xp >= required_xp:
            self._start_transcend_animation()
        else:
            self._stop_transcend_animation()
            self.transcend_title.setStyleSheet("color: blue;") # Reset color


    def _start_transcend_animation(self):
        if self.transcend_animation.state() != QPropertyAnimation.Running:
            # Re-initialize animation each time to animate 'font' properly
            self.transcend_animation.setStartValue(QFont("Arial", 24, QFont.Bold)) # Base font size
            self.transcend_animation.setEndValue(QFont("Arial", 30, QFont.Bold)) # Larger font size for animation
            self.transcend_animation.start()
            self.transcend_title.setStyleSheet("color: purple;") # Make it stand out when ready


    def _stop_transcend_animation(self):
        if self.transcend_animation.state() == QPropertyAnimation.Running:
            self.transcend_animation.stop()
            self.transcend_title.setFont(QFont("Arial", 24, QFont.Bold)) # Reset to base font size
            self.transcend_title.setStyleSheet("color: blue;") # Reset color


    def _confirm_transcend(self):
        reply = QMessageBox.question(self, "Confirm Transcend",
                                     "Are you sure you want to Transcend? This will reset your progress, level, and non-Transcended gear for a permanent bonus.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            message = self.game_manager.transcend()
            QMessageBox.information(self, "Transcended!", message)
            self._update_all_displays()
            self._stop_transcend_animation() # Stop animation after transcending

    # --- GLOBAL UPDATE & CLOSE --新技术-
    def _update_all_displays(self):
        self._update_player_stats_display()
        self._on_tab_change(self.tab_widget.currentIndex())

    def closeEvent(self, event):
        self.game_manager.save_game()
        super().closeEvent(event)
