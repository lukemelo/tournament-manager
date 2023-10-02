#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QComboBox, QHBoxLayout,
                             QGridLayout, QListWidget, QInputDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget)
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
import random, numpy as np

class TournamentApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Basic initialization
        self.teams = []
        self.matchups = []
        self.results = []
        self.win_count = {}

        # Round robin-related initialization
        self.current_round_robin = 0
        self.total_round_robins = 0
        self.round_robin_winners = {}
        self.sorted_teams = []

        # Setting up the UI with tabs
        self.initUI()
        self.raise_()

    def initUI(self):
        # Tab setup
        self.tab_widget = QTabWidget(self)
        self.team_reg_tab = QWidget()
        self.round_robin_tab = QWidget()
        self.round_robin_results_tab = QWidget()
        self.elimination_bracket_tab = QWidget()
    
        self.tab_widget.addTab(self.team_reg_tab, "Team Registration")
        self.tab_widget.addTab(self.round_robin_tab, "Round Robin")
        self.tab_widget.addTab(self.round_robin_results_tab, "Round Robin Results")
        # self.tab_widget.addTab(self.elimination_bracket_tab, "Elimination Bracket")
        
        # Create a new tab for elimination bracket interaction
        self.elimination_interaction_tab = QWidget()
        self.elimination_interaction_tab_layout = QVBoxLayout()
        self.elimination_interaction_tab.setLayout(self.elimination_interaction_tab_layout)
        self.tab_widget.addTab(self.elimination_interaction_tab, "Elimination Bracket")
    
        self.setCentralWidget(self.tab_widget)
    
        # Initialize the content of each tab
        self.init_team_reg_tab()
        self.init_round_robin_tab()
        self.init_round_robin_results_tab()  # Initialize the Round Robin Results tab here
        # self.init_elimination_bracket_tab()
        # Add initialization for other tabs as needed when you have content for them
    
        self.setWindowTitle('Tournament Software')
        self.show()
    
    def init_round_robin_results_tab(self):
        # Set up a layout for the round_robin_results_tab
        self.round_robin_results_tab_layout = QVBoxLayout()
        self.round_robin_results_tab.setLayout(self.round_robin_results_tab_layout)

        
        
    def init_elimination_bracket_tab(self):
        layout = QVBoxLayout()
        
        self.start_elimination_bracket_button = QPushButton('Start Elimination Bracket', self)
        self.start_elimination_bracket_button.clicked.connect(self.start_elimination_bracket)
        layout.addWidget(self.start_elimination_bracket_button)
        
        self.elimination_bracket_label = QLabel(self)
        layout.addWidget(self.elimination_bracket_label)
        
        self.elimination_bracket_tab.setLayout(layout)
        
    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def init_team_reg_tab(self):
        layout = QVBoxLayout()
        
        self.team_input = QLineEdit(self)
        self.team_input.setPlaceholderText("Enter team name")
        layout.addWidget(self.team_input)

        self.teams_list = QListWidget(self)
        self.teams_list.itemDoubleClicked.connect(self.edit_team)
        layout.addWidget(self.teams_list)

        self.add_team_button = QPushButton('Add Team', self)
        self.add_team_button.clicked.connect(self.add_team)
        layout.addWidget(self.add_team_button)

        self.remove_team_button = QPushButton('Remove Selected Team', self)
        self.remove_team_button.clicked.connect(self.remove_team)
        layout.addWidget(self.remove_team_button)

        self.team_reg_tab.setLayout(layout)

    def init_round_robin_tab(self):
        layout = QVBoxLayout()
        
        self.round_robin_input = QLineEdit(self)
        self.round_robin_input.setPlaceholderText("Number of round robins")
        layout.addWidget(self.round_robin_input)

        self.start_round_robin_button = QPushButton('Start Round Robins', self)
        self.start_round_robin_button.clicked.connect(self.start_round_robins)
        layout.addWidget(self.start_round_robin_button)
        
        self.round_robin_tab.setLayout(layout)

    def add_team(self):
        team_name = self.team_input.text()
        if team_name and team_name not in self.teams:
            self.teams.append(team_name)
            self.team_input.clear()
            self.update_teams_list()

    def update_teams_list(self):
        self.teams_list.clear()
        for index, team in enumerate(self.teams, start=1):
            self.teams_list.addItem(f"{index}: {team}")

    def edit_team(self, item):
        old_name = item.text().split(": ")[1]
        new_name, ok = QInputDialog.getText(self, 'Edit Team', 'Enter new team name:', text=old_name)
        if ok:
            if new_name and new_name not in self.teams:
                index = self.teams.index(old_name)
                self.teams[index] = new_name
                self.update_teams_list()

    def remove_team(self):
        current_item = self.teams_list.currentItem()
        if current_item:
            team_name = current_item.text().split(": ")[1]
            self.teams.remove(team_name)
            self.update_teams_list()
        else:
            QMessageBox.information(self, "Error", "Please select a team to remove!")

    def start_round_robins(self):
        try:
            num_round_robins = int(self.round_robin_input.text())
            
            if len(self.teams) % 2 != 0:  # check if the number of teams is odd
                self.teams.append('bye')  # add a 'bye' team
            
            self.round_robin_matches = []
            self.round_robin_winners = {}
            for _ in range(num_round_robins):
                self.round_robin_matches.append(self.generate_round_robin())

            for team in self.teams:
                self.win_count[team] = 0

            self.current_round_robin = 0
            self.total_round_robins = num_round_robins
            
            # Disable the start_round_robin_button here
            self.start_round_robin_button.setEnabled(False)
            self.round_robin_input.setEnabled(False)

            self.round_robin_selector = QComboBox(self)
            self.round_robin_selector.addItems([f"Round Robin {i+1}" for i in range(num_round_robins)])
            self.round_robin_selector.currentIndexChanged.connect(self.update_round_robin_display)
            self.round_robin_tab.layout().addWidget(self.round_robin_selector)

            self.process_round_robin()  # Add this line to display matchups for round 1
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number of round robins.")

    def generate_round_robin(self):
        all_matches = set(tuple(sorted(match)) for match in self.matchups)  # All previously seen matchups
        unique_found = False
        attempts = 0
    
        while not unique_found and attempts < 10000:  # A limit of 100 attempts to avoid infinite loops
            round_teams = self.teams.copy()
            random.shuffle(round_teams)
            
            round_matches = []
            current_matches = set()
            
            try:
                while round_teams:
                    team = round_teams.pop()  # Take a team from the end
                    
                    # Attempt to find an opponent they haven't faced before.
                    for opponent in round_teams:
                        match = tuple(sorted([team, opponent]))
                        if match not in all_matches and match not in current_matches:
                            round_teams.remove(opponent)
                            current_matches.add(match)
                            round_matches.append((team, opponent))
                            break
                    else:  # This else corresponds to the inner for-loop. It's executed if the for-loop wasn't broken out of.
                        raise ValueError("Repeated match found")
        
                unique_found = True
            except ValueError:
                attempts += 1
    
        if not unique_found:
            QMessageBox.information(self, "Error", "Unable to generate unique matchups. Try reducing the number of round robins or adding more teams.")
            return []
    
        self.matchups.extend(round_matches)
        return round_matches

    def update_round_robin_display(self, index):
        self.save_round_robin_winners()  # Save winners before switching rounds
        self.current_round_robin = index
        self.process_round_robin()

    def save_round_robin_winners(self):
        # Save the selected winners for the current round robin
        winners = [combo.currentText() if combo.currentText() != "-- select winner --" else None for combo in self.combos]
        self.round_robin_winners[self.current_round_robin] = winners

    def process_round_robin(self):
        # Clear the previous round robin layout if it exists
        if hasattr(self, 'grid_layout'):
            for i in reversed(range(self.grid_layout.count())): 
                widget = self.grid_layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
        else:
            # Create grid layout if it doesn't exist
            self.grid_layout = QGridLayout()
            self.round_robin_tab.layout().addLayout(self.grid_layout)
        
        # Check if we still have round robins to display
        if self.current_round_robin < self.total_round_robins:
            # Display current round robin
            matches = self.round_robin_matches[self.current_round_robin]
            self.combos = []  # Keep track of combo boxes
        
            saved_winners = self.round_robin_winners.get(self.current_round_robin, []) # Use .get() to avoid KeyError
        
            for i, match in enumerate(matches):
                self.grid_layout.addWidget(QLabel(match[0]), i, 0)
                self.grid_layout.addWidget(QLabel('vs'), i, 1)
                self.grid_layout.addWidget(QLabel(match[1]), i, 2)
        
                combo = QComboBox()
                combo.addItems(["-- select winner --", match[0], match[1]])
                
                # Check if we have saved winners and set the combo box accordingly
                if saved_winners:
                    winner = saved_winners[i]
                    combo.setCurrentText(winner)
                
                self.grid_layout.addWidget(combo, i, 3)
                self.combos.append(combo)
        
            self.finish_button = QPushButton('Finish Round Robin')
            self.finish_button.clicked.connect(self.finish_round_robin)
            self.grid_layout.addWidget(self.finish_button, i + 1, 2, 1, 2)
        else:
            # All round robins processed
            self.display_scoreboard()

    def finish_round_robin(self):
        all_selected = all([combo.currentText() != "-- select winner --" for combo in self.combos])
    
        if not all_selected:
            QMessageBox.warning(self, "Incomplete Selection", "Please select a winner for all matchups.")
            return
    
        # Save the winners for the current round robin
        current_winners = [combo.currentText() for combo in self.combos]
        self.round_robin_winners[self.current_round_robin] = current_winners
        
        # Reset and update the win count based on all saved round robin winners
        for team in self.teams:
            self.win_count[team] = 0
            
        for round_winners in self.round_robin_winners.values():
            for winner in round_winners:
                self.win_count[winner] += 1
            
        # Increment the counter for the next round robin
        self.current_round_robin += 1
    
        if self.current_round_robin < self.total_round_robins:
            self.process_round_robin()
        else:
            # Switch to the round_robin_results_tab
            self.tab_widget.setCurrentWidget(self.round_robin_results_tab)
            self.display_scoreboard()

    def display_scoreboard(self):
        self.clear_layout(self.round_robin_results_tab_layout)
        
        sorted_scores = sorted(self.win_count.items(), key=lambda x: x[1], reverse=True)

        score_table = QTableWidget()
        score_table.setColumnCount(2)
        score_table.setHorizontalHeaderLabels(["Team", "Wins"])
        score_table.setRowCount(len(self.teams))
        score_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        for i, (team, score) in enumerate(sorted_scores):
            score_table.setItem(i, 0, QTableWidgetItem(team))
            score_table.setItem(i, 1, QTableWidgetItem(str(score)))
        self.round_robin_results_tab_layout.addWidget(score_table)

        # Create and connect the Start Elimination Bracket button
        self.start_elimination_button = QPushButton('Start Elimination Bracket')
        self.start_elimination_button.clicked.connect(self.start_elimination_bracket)
        self.round_robin_results_tab_layout.addWidget(self.start_elimination_button)
        
    def show_winner(self):
        highest_score = max(self.win_count.values())
        winners = [team for team, score in self.win_count.items() if score == highest_score]
        QMessageBox.information(self, "Winner(s)", ", ".join(winners))

    def start_elimination_bracket(self):
        # Disable the "Start Elimination Bracket" button
        sender = self.sender()  # Get the button that triggered this method
        if sender:
            sender.setEnabled(False)  # Disable the button
            
        # Switch to the "Elimination Interaction" tab
        index = self.tab_widget.indexOf(self.elimination_interaction_tab)
        self.tab_widget.setCurrentIndex(index)
        
        # Rest of your existing logic
        if not self.round_robin_winners:  
            QMessageBox.warning(self, "Cannot Start", "Finish all the round robins first.")
            if sender:
                sender.setEnabled(True)  # Enable the button again if the starting condition is not met
            return
    
        self.sorted_teams = sorted(self.win_count.items(), key=lambda x: x[1], reverse=True)
        self.sorted_teams = [team[0] for team in self.sorted_teams]  # Extract the team names sorted by their wins
    
        # Adjust the length of sorted_teams to make it divisible by 2 and 
        # the same length as the elimination_order array
        desired_length = 2**int(np.ceil(np.log2(len(self.sorted_teams))))
        self.sorted_teams += ["BYE"] * (desired_length - len(self.sorted_teams))

        # Update the Elimination Bracket tab with the matchups
        self.rounds_layout = QHBoxLayout()  # Horizontal Layout to hold all rounds (columns)
        self.elimination_interaction_tab_layout.addLayout(self.rounds_layout)
        self.start_elimination_round(0)  # Start the first round
    
    def start_elimination_round(self, round_number):
        # Clear previous widgets if this is the first round
        if round_number == 0:
            self.clear_layout(self.rounds_layout)
        
        if len(self.sorted_teams) == 1:
            QMessageBox.information(self, "Winner", f"The Winner is {self.sorted_teams[0]}!")
            return
        
        # Determine the title of the round
        teams_left = len(self.sorted_teams)
        if teams_left == 2:
            round_title = "Finals"
        elif teams_left == 4:
            round_title = "Semi Finals"
        elif teams_left == 8:
            round_title = "Quarter Finals"
        else:
            round_title = f"Round of {teams_left}"
        
        # Create a QVBoxLayout for the round column
        round_col_layout = QVBoxLayout()
        round_col_layout.addWidget(QLabel(round_title))  # Add title label to the column
        
        # # Create a QVBoxLayout for the round column
        # round_col_layout = QVBoxLayout()
        
        # Split the sorted_teams into matchups
        if round_number == 0:
            n_rounds = int(np.ceil(np.log2(len(self.sorted_teams))))
            elimination_order = self.bracket_gen(n_rounds)  # Corrected Line
            matchups = [(self.sorted_teams[matchup[0]-1], self.sorted_teams[matchup[1]-1]) for matchup in elimination_order]
        else:
            matchups = [(self.sorted_teams[i], self.sorted_teams[i + 1]) for i in range(0, len(self.sorted_teams), 2)]
        
        combos_elimination = []
        space_multiplier = 2 ** round_number  # Calculate the space multiplier based on the round number
        for team1, team2 in matchups:
            # Create SpacerItem above the QComboBox
            round_col_layout.addSpacerItem(QSpacerItem(20, 20 * space_multiplier, QSizePolicy.Minimum, QSizePolicy.Expanding))
            
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(team1))
            hbox.addWidget(QLabel('vs'))
            hbox.addWidget(QLabel(team2))
            
            combo = QComboBox()
            combo.addItems(["-- select winner --", team1, team2])
            hbox.addWidget(combo)
            
            combos_elimination.append(combo)
            round_col_layout.addLayout(hbox)
        
            # Create SpacerItem below the QComboBox
            round_col_layout.addSpacerItem(QSpacerItem(20, 20 * space_multiplier, QSizePolicy.Minimum, QSizePolicy.Expanding))
            
        self.rounds_layout.addLayout(round_col_layout)
        
        # next_round_button = QPushButton(f'Proceed to Round {round_number + 2}')
        # next_round_button.clicked.connect(lambda: self.process_elimination_round(round_number, combos_elimination))
        # round_col_layout.addWidget(next_round_button)
        
        # Inside the start_elimination_round method, after creating the final column layout
        if teams_left == 2:  # If it’s the final round column
            next_round_button = QPushButton('Determine Winner')
            next_round_button.clicked.connect(lambda: self.process_elimination_round(round_number, combos_elimination))  # Connect to the slot
            round_col_layout.addWidget(next_round_button)
        else:
            next_round_button = QPushButton(f'Proceed to Round {round_number + 2}')
            next_round_button.clicked.connect(lambda: self.process_elimination_round(round_number, combos_elimination))  # Connect to the slot
            round_col_layout.addWidget(next_round_button)

        
    
    def process_elimination_round(self, round_number, combos_elimination):
        sender = self.sender()  # Get the button that triggered this method
        if sender:
            sender.setEnabled(False)  # Disable the button
        
        winners = []
        losers = []  # List to hold the losers of the semi-finals
        for combo in combos_elimination:
            winner = combo.currentText()
            if winner == "-- select winner --":
                QMessageBox.warning(self, "Incomplete Selection", "Please select a winner for all matchups.")
                if sender:
                    sender.setEnabled(True)  # Enable the button again if the selection is not complete
                return
            winners.append(winner)
            # Determine the loser and append to the losers list
            index = combo.findText(winner)
            loser_index = 1 if index == 2 else 2
            losers.append(combo.itemText(loser_index))
        
        self.sorted_teams = winners
        self.start_elimination_round(round_number + 1)
        
        # If this is the Semi Finals Round, create Consolation Finals
        if len(winners) == 2:
            # Get the last round column container layout (Finals Column Container)
            finals_col_layout = self.rounds_layout.itemAt(self.rounds_layout.count() - 1).layout()
            
            consolation_label = QLabel("Consolation Finals")
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(losers[0]))
            hbox.addWidget(QLabel('vs'))
            hbox.addWidget(QLabel(losers[1]))
            combo = QComboBox()
            combo.addItems(["-- select winner --", losers[0], losers[1]])
            hbox.addWidget(combo)
            
            # Insert Consolation Finals Label and ComboBox above the "Proceed to next round" button
            finals_col_layout.insertWidget(finals_col_layout.count() - 1, consolation_label)  # Adjusted index
            finals_col_layout.insertLayout(finals_col_layout.count() - 1, hbox)  # Adjusted index

    
    def process_consolation_final(self, combo, button):
        winner = combo.currentText()
        if winner == "-- select winner --":
            QMessageBox.warning(self, "Incomplete Selection", "Please select a winner for the Consolation Finals.")
            return
        button.setEnabled(False)  # Disable the button after determining the consolation winner
        QMessageBox.information(self, "Consolation Winner", f"The Consolation Winner is {winner}!")
    
        def clear_layout(self, layout):
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
    
    def bracket_gen(self,power):
        if power == 1:
            return [[1, 2]]
        elif power == 2:
            return [[1, 4], [3, 2]]
        
        base_list = list(map(lambda x: x + 1, range(2 ** power)))[:2 ** power // 2]
        c_down = 2 ** power
        index = 0
        for i in base_list:
            base_list[index] = [i, c_down - index]
            index += 1
        
        rnd = []
        index_front = 0
        index_end = -1
        for i in base_list:
            rnd = rnd + [[base_list[index_front], base_list[index_end]]]
            index_front += 1
            index_end -= 1
        
        rnd = rnd[:len(rnd) // 2]
        index_front = 0
        index_end = -1
        for i in rnd:
            rnd[index_front] += rnd[index_end]
            index_front += 1
            index_end -= 1
        rnd = rnd[:len(rnd) // 2]
        
        while len(rnd) != 1:
            index = 0
            middle = len(rnd) // 2
            for i in rnd[:middle]:
                rnd[index] += rnd[index + middle]
                index += 1
            rnd = rnd[:middle]
        
        rnd = rnd[0]
        n_rnd = []
        for sublist in rnd:
            if isinstance(sublist[0], list):  # If the element is a list, extend n_rnd with it.
                n_rnd.extend(sublist)
            else:  # Otherwise, append the element itself.
                n_rnd.append(sublist)
    
        # Convert the flat list to a numpy array, reshape it to have 2 columns, then convert it back to a list of lists.
        reshaped_array = np.array(n_rnd).reshape(-1, 2)
        return reshaped_array.tolist()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TournamentApp()
    ex.raise_()  # Bring window to front
    ex.activateWindow()  # Activate the window
    sys.exit(app.exec_())
