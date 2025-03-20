import random
import pandas as pd
import ace_tools as tools  # For displaying the results

# CONFIGURATION
starting_bankroll = .25  # Total bankroll
starting_bet = 1         # Initial bet size
win_probability = 0.30   # Probability of winning (adjust per game)
loss_multiplier = 1.5    # Increase bet by this factor after a loss
win_multiplier = 0.5     # Decrease bet by this factor after a win (0.5 means reduce by 50%)
profit_target = 150      # Stop when bankroll reaches this amount
max_rounds = 1000        # Maximum rounds to play

# Simulation variables
bankroll = starting_bankroll
bet = starting_bet
rounds = []

for round_num in range(1, max_rounds + 1):
    if bankroll < bet:
        break  # Stop if the bankroll can't cover the next bet
    if bankroll >= profit_target:
        break  # Stop if profit target is reached

    win = random.random() < win_probability  # Determine win/loss

    if win:
        bankroll += bet  # Add win amount
        bet = max(starting_bet, bet * win_multiplier)  # Reduce bet on win
    else:
        bankroll -= bet  # Deduct loss
        bet = min(bankroll, bet * loss_multiplier)  # Increase bet after loss

    rounds.append([round_num, bankroll, bet, "Win" if win else "Loss"])

# Create and display results
df = pd.DataFrame(rounds, columns=["Round", "Bankroll", "Next Bet", "Result"])
tools.display_dataframe_to_user(name="Martingale Betting Simulation", dataframe=df)
