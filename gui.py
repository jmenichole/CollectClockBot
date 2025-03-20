import sys
import datetime
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QCheckBox, QScrollArea,
    QMainWindow, QHBoxLayout, QListWidget, QListWidgetItem, QAbstractItemView
)
from PyQt5.QtCore import Qt, QTimer  # Correct import for QTimer
from database import update_status, get_status

USER_ID = "TEST_USER"
RESET_TIME_HOURS = 24  # Time until bonuses reset

CASINO_LINKS = {
    "Sportzino": "https://sportzino.com/signup/8a105ba6-7ada-45c8-b021-f478ac03c7c4",
    "Sidepot": "https://sidepot.us",
    "Casino Click": "https://casino.click",
    "Shuffle": "https://shuffle.com?r=jHR7JnWRPF",
    "Fortune Coins": "https://www.fortunecoins.com/signup/3c08936f-8979-4f87-b377-efdbff519029",
    "Pulsz": "https://www.pulsz.com/?invited_by=utfk4r",
    "Pulsz Bingo": "https://pulszbingo.com",
    "Stake US": "https://stake.us/?c=Jmenichole",
    "Wow Vegas": "https://www.wowvegas.com/?raf=3615494",
    "McLuck": "https://www.mcluck.com/?r=908900038",
    "Mega Bonanza": "https://www.megabonanza.com/?r=72781897",
    "High 5 Casino": "https://high5casino.com/gc?adId=INV001%3AJmenichole",
    "Lucky Bird": "https://luckybird.io/?c=c_jmenichole",
    "Spree": "https://spree.com/?r=440894",
    "Crown Coins": "https://crowncoinscasino.com",
    "Real Prize": "https://www.realprize.com/refer/317136",
    "Clubs Poker": "https://play.clubs.poker/?referralCode=104192",
    "Hello Millions": "https://www.hellomillions.com/referred-by-friend?r=26d6760f%2F1236643867",
    "Chanced": "https://chanced.com/c/m9q2mi",
    "PlayFame": "https://www.playfame.com/?r=1275975417",
    "Jackpota": "https://www.jackpota.com/?r=85453282",
    "Zula Casino": "https://www.zulacasino.com/signup/221ddd92-862e-45d8-acc0-4cd2c26f7cdd",
    "Ding Ding Ding": "https://dingdingding.com/?referral=190cd69a-5af4-51bf-b418-9a35effcdf04",
    "Cases.gg": "https://cases.gg/r/JMENICHOLE",
    "Trust Dice": "https://trustdice.win/faucet/?ref=u_jmenichole",
    "Punt": "https://punt.com/c/cg60pd",
    "Fortune Wheelz": "https://fortunewheelz.com/?invited_by=P36ZS6",
    "Zoot": "https://getzoot.us/?referralCode=ZOOTwithJMENICHOLE",
    "MyPrize.us": "https://myprize.us/invite/quietMorning197",
    "Modo.us": "https://modo.us?referralCode=61MN6A",
    "Spinsala": "https://spinsala.com/en?invite=daym",
    "Gamba": "https://gamba.com?c=Jme",
    "Clash.gg": "https://clash.gg/r/stakestats",
    "Chumba": "https://Chumbacasino.com",
    "Luckyland Slots": "https://luckylandslots.com",
    "Legendz": "https://legendz.com/?referred_by_id=221602"
}

class CollectClockApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_status()

    def initUI(self):
        self.setWindowTitle("CollectClock Bonus Tracker")
        self.setGeometry(100, 100, 450, 600)
        self.setMinimumSize(450, 400)

        # Scrollable List Widget
        self.casino_list = QListWidget()
        self.casino_list.setSelectionMode(QAbstractItemView.NoSelection)
        self.casino_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.casino_list.setDefaultDropAction(Qt.MoveAction)

        # Populate the list with casinos
        self.checkboxes = {}
        self.timers = {}

        for casino, link in CASINO_LINKS.items():
            item_widget = QWidget()
            layout = QHBoxLayout()

            # Clickable link
            casino_label = QLabel(f'<a href="{link}">{casino}</a>')
            casino_label.setOpenExternalLinks(True)
            casino_label.setTextInteractionFlags(Qt.TextBrowserInteraction)

            # Checkbox
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(lambda state, c=casino: self.update_status(c, state))

            # Timer label
            timer_label = QLabel("")
            timer_label.setFixedWidth(100)  # Keep timers aligned

            # Layout setup
            layout.addWidget(checkbox)
            layout.addWidget(casino_label)
            layout.addWidget(timer_label)
            layout.setStretch(1, 1)
            item_widget.setLayout(layout)

            # Add to list
            item = QListWidgetItem(self.casino_list)
            item.setSizeHint(item_widget.sizeHint())
            self.casino_list.addItem(item)
            self.casino_list.setItemWidget(item, item_widget)

            # Store checkbox and timer
            self.checkboxes[casino] = (checkbox, timer_label)

        # Scroll area setup
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.casino_list)

        # Set main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        central_widget.setLayout(main_layout)

        self.setCentralWidget(central_widget)

    def load_status(self):
        user_data = get_status(USER_ID)
        current_time = datetime.datetime.now()

        for casino, collected, timestamp in user_data:
            if casino in self.checkboxes:
                checkbox, timer_label = self.checkboxes[casino]
                last_collected = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                elapsed_time = (current_time - last_collected).total_seconds()
                remaining_time = RESET_TIME_HOURS * 3600 - elapsed_time

                if elapsed_time < RESET_TIME_HOURS * 3600:
                    checkbox.setChecked(True)
                    checkbox.setEnabled(False)
                    self.start_timer(casino, remaining_time)
                else:
                    checkbox.setChecked(False)
                    checkbox.setEnabled(True)
                    timer_label.setText("Available Now")

    def update_status(self, casino, state):
        if state == 2:  # Checked
            update_status(USER_ID, casino, 1)
            self.start_timer(casino, RESET_TIME_HOURS * 3600)

    def start_timer(self, casino, duration):
        if casino in self.timers:
            self.timers[casino].stop()

        # Create a new countdown timer
        self.timers[casino] = QTimer(self)
        self.timers[casino].setInterval(1000)  # Update every second
        self.timers[casino].timeout.connect(lambda: self.update_timer(casino))
        self.timers[casino].start()

        # Store end time
        end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
        self.checkboxes[casino][1].setProperty("end_time", end_time)
        self.update_timer(casino)

    def update_timer(self, casino):
        timer_label = self.checkboxes[casino][1]
        end_time = timer_label.property("end_time")
        remaining_time = (end_time - datetime.datetime.now()).total_seconds()

        if remaining_time > 0:
            hours, remainder = divmod(int(remaining_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            timer_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")
        else:
            timer_label.setText("Available Now")
            self.checkboxes[casino][0].setEnabled(True)
            self.timers[casino].stop()

app = QApplication(sys.argv)
window = CollectClockApp()
window.show()
sys.exit(app.exec_())
