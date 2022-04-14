from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import numpy as np


class MyGame:
    def __init__(self, n_players):
        self.n_players = n_players
        self.n_actions_of_player = []
        self.payoffs = []
        self.jumps = []
        self.final_rs = []

    def setNActionsOfPlayer(self, n_actions_of_player):
        self.n_actions_of_player = n_actions_of_player
        product_list = np.prod(n_actions_of_player)
        for p in range(self.n_players - 1):
            product_list = product_list / n_actions_of_player[p]
            self.jumps.append(int(product_list))
        self.jumps.append(1)

    def setPayoffs(self, payoffs):
        self.payoffs = payoffs

    def check_zero_sum(self):
        for payoff in self.payoffs:
            if sum(payoff) != 0:
                return False
        return True

    def pure_Nash_equilibria(self):
        nash_candiates = []
        for i in range(self.n_players):
            flag = [0 for i in range(len(self.payoffs))]
            player_best_select = []
            for j in range(len(self.payoffs)):
                if flag[j] == 0:
                    idx = j
                    tmp_max = self.payoffs[idx][i]
                    tmp_best_idx = []
                    for tmp_action in range(self.n_actions_of_player[i]):
                        gain = self.payoffs[idx][i]
                        if gain == tmp_max:
                            tmp_best_idx.append(idx)
                        elif gain > tmp_max:
                            tmp_best_idx.clear()
                            tmp_best_idx.append(idx)
                            tmp_max = gain
                        flag[idx] = 1
                        idx = idx + self.jumps[i]
                    player_best_select = player_best_select + tmp_best_idx
            if len(nash_candiates) == 0:
                nash_candiates = player_best_select
            else:
                nash_candiates = list(set(nash_candiates).intersection(player_best_select))
        return nash_candiates

    def find_dominated_strategy(self):
        final_result = []
        dominant_rs = []
        for player in range(self.n_players):
            n_actions = self.n_actions_of_player[player]
            gains_of_all_actions = []
            for action in range(n_actions):
                gain_list = []
                ind = action * self.jumps[player]
                flag = 0
                len_of_list = int(len(self.payoffs) / n_actions)
                while len(gain_list) < len_of_list:
                    tmp_gain = self.payoffs[ind][player]
                    gain_list.append(tmp_gain)
                    flag = flag + 1
                    if flag == self.jumps[player]:
                        prev_jumps = self.jumps[player]
                        if player > 0:
                            prev_jumps = self.jumps[player - 1]
                        ind = ind + prev_jumps - self.jumps[player] + 1
                        flag = 0
                    else:
                        ind = ind + 1
                gains_of_all_actions.append(gain_list)
            for i in range(len(gains_of_all_actions) - 1):
                for j in range(i + 1, len(gains_of_all_actions)):
                    if not gains_of_all_actions[i] == gains_of_all_actions[j]:
                        is_dominated = True
                        tmp_len = len(gains_of_all_actions[i])
                        tmp_flag = 0
                        counter = 0
                        weakly_dominated = False
                        while tmp_flag == 0 and counter < tmp_len:
                            if gains_of_all_actions[i][counter] < gains_of_all_actions[j][counter]:
                                tmp_flag = -1
                            elif gains_of_all_actions[i][counter] > gains_of_all_actions[j][counter]:
                                tmp_flag = 1
                            else:
                                counter = counter + 1
                        if counter > 0:
                            weakly_dominated = True
                        for idx in range(1, tmp_len):
                            if tmp_flag * gains_of_all_actions[i][idx] < tmp_flag * gains_of_all_actions[j][idx]:
                                is_dominated = False
                                break
                            elif gains_of_all_actions[i][idx] == gains_of_all_actions[j][idx]:
                                weakly_dominated = True
                        if is_dominated:
                            if tmp_flag == -1:
                                final_result.append((player, j, i, weakly_dominated))
                                lst_tmp = [param for param in final_result if param[1] == j and param[0] == player]
                                if len(lst_tmp) == len(gains_of_all_actions) - 1:
                                    weakly_dominant = False
                                    for item_tmp in lst_tmp:
                                        if item_tmp[3] is True:
                                            weakly_dominant = True
                                    dominant_rs.append((player, j, weakly_dominant))
                            else:
                                final_result.append((player, i, j, weakly_dominated))
                                lst_tmp = [param for param in final_result if param[1] == i and param[0] == player]
                                if len(lst_tmp) == len(gains_of_all_actions) - 1:
                                    weakly_dominant = False
                                    for item_tmp in lst_tmp:
                                        if item_tmp[3] is True:
                                            weakly_dominant = True
                                    dominant_rs.append((player, i, weakly_dominant))
        return final_result, dominant_rs

    def find_mixed_Nash(self, dominated_strategy):
        rs = []
        gain_player_1 = [gain[0] for gain in self.payoffs]
        gain_player_2 = [gain[1] for gain in self.payoffs]
        flag_1 = True
        flag_2 = True
        if len(dominated_strategy) > 0:
            for strategy in dominated_strategy:
                if not strategy[3]:
                    player = strategy[0]
                    if player == 0:
                        flag_1 = False
                    else:
                        flag_2 = False
                    rs.append((player, 1.0, 0))
        # p - prob of action 1 player 1
        if flag_1:
            if gain_player_2[0] - gain_player_2[1] - gain_player_2[2] + gain_player_2[3] == 0:
                rs.insert(0, (0, -1, -1))
            else:
                p = (gain_player_2[3] - gain_player_2[2]) / (
                        gain_player_2[0] - gain_player_2[1] - gain_player_2[2] + gain_player_2[3])
                if p > 1.0:
                    rs.insert(0, (0, -1, -1))
                elif p == 1.0:
                    rs.insert(0, (0, p, -1))
                else:
                    rs.insert(0, (0, p, 1.0 - p))

        # q - prob of action 1 player 2
        if flag_2:
            if gain_player_1[0] - gain_player_1[1] - gain_player_1[2] + gain_player_1[3] == 0:
                rs.append((1, -1, -1))
            else:
                q = (gain_player_1[3] - gain_player_1[1]) / (
                        gain_player_1[0] - gain_player_1[1] - gain_player_1[2] + gain_player_1[3])
                if q > 1.0:
                    rs.append((1, -1, -1))
                elif q == 1.0:
                    rs.append((1, q, -1))
                else:
                    rs.append((1, q, 1.0 - q))
        return rs

    def get_payoff_from_index(self, index):
        return self.payoffs[index]

    def get_payoff(self, p1_action, p2_action):
        idx = p1_action * 2 + p2_action
        gains = self.get_payoff_from_index(idx)
        return gains

    def get_actions_form_pure_Nash(self):
        rs = []
        list_idx = self.pure_Nash_equilibria()
        for idx in list_idx:
            n = idx
            action_combination = []
            for player in range(self.n_players):
                action_combination.insert(0, "Action " + str((n % (self.n_actions_of_player[player])) + 1))
                n = int(n / (self.n_actions_of_player[player]))
            rs.append(tuple(action_combination))
        return rs

    def solve_the_game(self, mode):
        is_zero_sum = self.check_zero_sum()
        nash = self.pure_Nash_equilibria()
        pure_nash = []
        if len(nash) > 0:
            for n in nash:
                pure_nash.append(self.get_payoff_from_index(n))
        dominated_strategy, dominant_strategy = self.find_dominated_strategy()

        if mode == 0:
            nash_mix = self.find_mixed_Nash(dominated_strategy)
        else:
            nash_mix = None
        rs = [is_zero_sum, pure_nash, nash_mix, dominated_strategy, dominant_strategy]
        self.final_rs = rs
        return rs


def generate_UI_payoffs(n_actions_of_player, n_player):
    framex = Frame(frame1)
    framex.pack(pady=10)
    frameList.append(framex)
    l_player2 = Label(framex, text="Player II")
    l_player2.grid(row=0, column=2, columnspan=4)
    l_player1 = Label(framex, text="Player I")
    l_player1.grid(row=2, column=0, rowspan=2, padx=5)
    for i in range(n_actions_of_player[1]):
        txt_label = "Action " + str(i + 1)
        temp_label = Label(framex, text=txt_label)
        temp_label.grid(row=1, column=i * 2 + 2, columnspan=2)
    for i in range(n_actions_of_player[0]):
        txt_label = "Action " + str(i + 1)
        temp_label = Label(framex, text=txt_label)
        temp_label.grid(row=i + 2, column=1, pady=2)
        for j in range(n_actions_of_player[1] * n_player):
            temp_e = Entry(framex, width=5)
            temp_e.grid(row=i + 2, column=j + 2, padx=2)
            entriesPayoffs.append(temp_e)
    button_next.config(text="Solve")


def get_payoffs_from_entry(n_player):
    payoffs = []
    dummy_list = []
    for entry in entriesPayoffs:
        dummy_list.append(int(entry.get()))
        if len(dummy_list) == n_player:
            payoffs.append(tuple(dummy_list))
            dummy_list.clear()
    return payoffs


def generate_result_UI(result):
    frame1_3 = Frame(frame1, borderwidth=1, relief=SOLID)
    frame1_3.pack()
    frameList.append(frame1_3)
    idx = 0
    print(result)
    # Zero sum
    is_zero_sum = result[0]
    if not is_zero_sum:
        txt = "The game is not Zero-sum"
    else:
        txt = "The game is Zero-sum"
    tmp = Label(frame1_3, text=str(txt))
    tmp.grid(row=idx, column=0, sticky="W")
    idx = idx + 1
    # Pure Nash
    pure_nash = result[1]
    pure_nash_actions_form = m_Game.get_actions_form_pure_Nash()
    if len(pure_nash) == 0:
        txt = "\nThere is no pure Nash Equilibrium"
    else:
        txt = "\nPure Nash Equilibrium: " + str(pure_nash)
    tmp = Label(frame1_3, text=str(txt))
    tmp.grid(row=idx, column=0, sticky="W")
    idx = idx + 1
    if len(pure_nash) !=0:
        txt = "In actions form: "+str(pure_nash_actions_form)
        tmp = Label(frame1_3, text=str(txt))
        tmp.grid(row=idx, column=0, sticky="W")
        idx = idx + 1
    # Mix Nash
    mix_nash = result[2]
    if mix_nash is not None:
        if len(mix_nash) > 0:
            txt = "\nMixed Nash Equilibrium: "
            for mn in mix_nash:
                player = mn[0]
                prob = mn[1]
                rv_prob = mn[2]
                if prob == 0.0 or prob == 1.0:
                    if rv_prob != -1:
                        tmp_txt = "\nPlayer {0} has a dominant strategy so he never mixes strategies in a solution"
                        txt = txt + tmp_txt.format(player + 1, prob, rv_prob)
                elif prob != -1:
                    tmp_txt = "\nPlayer {0} plays the mixed strategy of (Action 1, Action 2) = ({1:.7f},{2:.7f})"
                    txt = txt + tmp_txt.format(player + 1, prob, rv_prob)
                else:
                    tmp_txt = "\nEvery profile (Action 1, Action 2) of player {0} can be part of a mixed strategy solution"
                    txt = txt + tmp_txt.format(player + 1)
        else:
            txt = "\nThere exist no Nash equilibrium in mixed strategies"
        tmp = Label(frame1_3, text=str(txt), justify=LEFT)
        tmp.grid(row=idx, column=0, sticky="W")
        idx = idx + 1
    # Dominated strategies
    dominated_strategies = result[3]
    if len(dominated_strategies) > 0:
        txt = "\nDominated strategies: "
        tmp_txt = "\nPlayer {0}: Strategy {1} is {2}dominated by strategy {3}"
        for d_strategy in dominated_strategies:
            player = d_strategy[0]
            dominated_s = d_strategy[1]
            week_s = d_strategy[2]
            weakly_dominated = d_strategy[3]
            temp = ""
            if weakly_dominated:
                temp = "weakly "
            txt = txt + tmp_txt.format(player + 1, week_s + 1, temp, dominated_s + 1)
    else:
        txt = "\nThere is no dominated strategy"
    tmp = Label(frame1_3, text=str(txt), justify=LEFT)
    tmp.grid(row=idx, column=0, sticky="W")
    idx = idx + 1
    # Dominant strategies
    dominant_strategies = result[4]
    if len(dominant_strategies) > 0:
        txt = "\nDominant strategies: "
        tmp_txt = "\nPlayer {0}: Strategy {1} is {2}dominant strategy"
        for dominant_strategy in dominant_strategies:
            player = dominant_strategy[0]
            dominant_s = dominant_strategy[1]
            weakly = dominant_strategy[2]
            temp = ""
            if weakly:
                temp = "weakly "
            txt = txt + tmp_txt.format(player + 1, dominant_s + 1, temp)
    else:
        txt = "\nThere is no dominant strategy"
    tmp = Label(frame1_3, text=str(txt), justify=LEFT)
    tmp.grid(row=idx, column=0, sticky="W")


def doNext():
    global step, m_Game
    mode = dropdownList_mode.get()
    if mode == "2 Players - 2 Actions":
        if step == 0:
            n_actions_of_player = [2, 2]
            n_player = 2
            m_Game = MyGame(n_player)
            m_Game.setNActionsOfPlayer(n_actions_of_player)
            generate_UI_payoffs(n_actions_of_player, n_player)
            step = step + 1
            return
        if step == 1:
            button_next["state"] = "disabled"
            payoffs = get_payoffs_from_entry(m_Game.n_players)
            m_Game.setPayoffs(payoffs)
            generate_result_UI(m_Game.solve_the_game(0))
            if len(m_Game.final_rs[2]) > 0:
                button_simulate.pack(side=RIGHT, padx=20, pady=5)
            return
    if mode == "2 Players - Many Actions":
        if step == 0:
            n_player = 2
            m_Game = MyGame(n_player)
            frame1_2 = Frame(frame1)
            frame1_2.pack(pady=10)
            frameList.append(frame1_2)
            l_action_player1 = Label(frame1_2, text="Number actions of Player I: ")
            l_action_player1.grid(row=0, column=0)
            e_action_player1 = Entry(frame1_2)
            e_action_player1.grid(row=0, column=1)
            entriesList.append(e_action_player1)
            l_action_player2 = Label(frame1_2, text="Number actions of Player II: ")
            l_action_player2.grid(row=1, column=0)
            e_action_player2 = Entry(frame1_2)
            e_action_player2.grid(row=1, column=1)
            entriesList.append(e_action_player2)
            step = step + 1
            return
        if step == 1:
            n_actions_of_player = []
            for e in entriesList:
                n_actions_of_player.append(int(e.get()))
            entriesList.clear()
            m_Game.setNActionsOfPlayer(n_actions_of_player)
            generate_UI_payoffs(n_actions_of_player, m_Game.n_players)
            step = step + 1
            return
        if step == 2:
            button_next["state"] = "disabled"
            payoffs = get_payoffs_from_entry(m_Game.n_players)
            m_Game.setPayoffs(payoffs)
            generate_result_UI(m_Game.solve_the_game(1))
            return
    else:
        if step == 0:
            frame1_2 = Frame(frame1)
            frame1_2.pack(pady=10)
            frameList.append(frame1_2)
            l_nPlayers = Label(frame1_2, text="Number of Players: ")
            l_nPlayers.grid(row=0, column=0)
            e_nPlayers = Entry(frame1_2)
            e_nPlayers.grid(row=0, column=1)
            entriesList.append(e_nPlayers)
            step = step + 1
            return
        if step == 1:
            n_player = int(entriesList[0].get())
            entriesList.clear()
            m_Game = MyGame(n_player)
            frame1_3 = Frame(frame1)
            frame1_3.pack(pady=10)
            frameList.append(frame1_3)
            for i in range(m_Game.n_players):
                l_action_player = Label(frame1_3, text="Number actions of Player " + str(i + 1) + ": ")
                l_action_player.grid(row=i, column=0)
                e_action_player = Entry(frame1_3)
                e_action_player.grid(row=i, column=1)
                entriesList.append(e_action_player)
            step = step + 1
            return
        if step == 2:
            n_actions_of_player = []
            for e in entriesList:
                n_actions_of_player.append(int(e.get()))
            entriesList.clear()
            m_Game.setNActionsOfPlayer(n_actions_of_player)
            frame1_4 = Frame(frame1)
            frame1_4.pack(pady=10)
            frameList.append(frame1_4)
            for i in range(m_Game.n_players):
                l_playeri = Label(frame1_4, text="Player " + str(i + 1))
                l_playeri.grid(row=0, column=i)
            l_payoffs = Label(frame1_4, text="Payoffs")
            l_payoffs.grid(row=0, column=m_Game.n_players, columnspan=m_Game.n_players)
            total_combine = 1
            for n_action in n_actions_of_player:
                total_combine = total_combine * n_action
            p_actions = [0 for i in range(m_Game.n_players)]
            for i in range(total_combine):
                for p in range(m_Game.n_players):
                    txt_label = "Action " + str(p_actions[p] + 1)
                    temp_label = Label(frame1_4, text=txt_label)
                    temp_label.grid(row=i + 1, column=p, padx=5)
                p_actions[m_Game.n_players - 1] = p_actions[m_Game.n_players - 1] + 1
                for p in range(m_Game.n_players):
                    index = m_Game.n_players - p - 1
                    if p_actions[index] == n_actions_of_player[index]:
                        p_actions[index] = 0
                        p_actions[index - 1] = p_actions[index - 1] + 1
                for j in range(m_Game.n_players):
                    temp_e = Entry(frame1_4, width=5)
                    temp_e.grid(row=i + 1, column=m_Game.n_players + j, padx=2)
                    entriesPayoffs.append(temp_e)
            step = step + 1
            button_next.config(text="Solve")
            return
        if step == 3:
            button_next["state"] = "disabled"
            # hide not important frames:
            last_frame = frameList[len(frameList) - 1]
            for frame in frameList:
                if frame != last_frame:
                    frame.pack_forget()
            payoffs = get_payoffs_from_entry(m_Game.n_players)
            m_Game.setPayoffs(payoffs)
            generate_result_UI(m_Game.solve_the_game(2))
            return


def doSimulate():
    global m_Game, s_step
    if s_step == 0:
        frame1_simulate = Frame(frame1)
        frame1_simulate.pack(pady=10)
        frameList.append(frame1_simulate)
        l_prob_1 = Label(frame1_simulate, text="Mix strategy of player 1 (p): ")
        l_prob_1.grid(row=0, column=0)
        e_prob_1 = Entry(frame1_simulate)
        e_prob_1.grid(row=0, column=1)
        entriesList.append(e_prob_1)
        l_prob_2 = Label(frame1_simulate, text="Mix strategy of player 2 (q): ")
        l_prob_2.grid(row=1, column=0)
        e_prob_2 = Entry(frame1_simulate)
        e_prob_2.grid(row=1, column=1)
        entriesList.append(e_prob_2)
        button_simulate.config(text="Simulate")
        s_step = s_step + 1
        return
    if s_step == 1:
        button_simulate["state"] = "disabled"
        mix_nash = m_Game.final_rs[2]
        calculated_prob_1 = 0.0
        calculated_prob_2 = 0.0
        for mn in mix_nash:
            if mn[0] == 0 and mn[2] != -1:
                calculated_prob_1 = mn[1]
            elif mn[0] == 1 and mn[2] != -1:
                calculated_prob_2 = mn[1]
        if calculated_prob_1 == 0.0:
            calculated_prob_1 = 0.5
        if calculated_prob_2 == 0.0:
            calculated_prob_2 = 0.5
        if len(entriesList[0].get()) == 0:
            entered_prob_p = calculated_prob_1
        else:
            entered_prob_p = float(entriesList[0].get())
        if len(entriesList[1].get()) == 0:
            entered_prob_q = calculated_prob_2
        else:
            entered_prob_q = float(entriesList[1].get())
        if entered_prob_p > 1.0:
            entered_prob_p = 1.0
        if entered_prob_q > 1.0:
            entered_prob_q = 1.0
        # create new windows
        simulate_window = Toplevel(root)
        simulate_window.title("Simulator")
        simulate_window.geometry("800x300")
        result = ScrolledText(simulate_window, width=800, wrap=NONE)
        result.pack(padx=40)
        actions = [0, 1]
        entered_probs_1 = [entered_prob_p, 1.0 - entered_prob_p]
        entered_probs_2 = [entered_prob_q, 1.0 - entered_prob_q]
        calculated_probs_1 = [calculated_prob_1, 1.0 - calculated_prob_1]
        calculated_probs_2 = [calculated_prob_2, 1.0 - calculated_prob_2]
        p1_entered_sums = 0
        p2_entered_sums = 0
        p1_calculated_sums = 0
        p2_calculated_sums = 0
        str_output = "--------Round {0}--------\n" + \
                     "  Payoffs of entered mixed strategy: " + \
                     "Player 1 (Action {1}) gain {2} and player 2 (Action {3}) gain {4}\n" + \
                     "  Payoffs of calculated mixed strategy: " + \
                     "Player 1 (Action {5}) gain {6} and player 2 (Action {7}) gain {8}\n"
        for count in range(200):
            # Entered probs
            p1_action_entered = np.random.choice(actions, 1, p=entered_probs_1)[0]
            p2_action_entered = np.random.choice(actions, 1, p=entered_probs_2)[0]
            tmp_payoff = m_Game.get_payoff(p1_action_entered, p2_action_entered)
            p1_action_entered_payoff = tmp_payoff[0]
            p1_entered_sums = p1_entered_sums + p1_action_entered_payoff
            p2_action_entered_payoff = tmp_payoff[1]
            p2_entered_sums = p2_entered_sums + p2_action_entered_payoff
            # Calculated probs
            p1_action_calculated = np.random.choice(actions, 1, p=calculated_probs_1)[0]
            p2_action_calculated = np.random.choice(actions, 1, p=calculated_probs_2)[0]
            tmp_payoff = m_Game.get_payoff(p1_action_calculated, p2_action_calculated)
            p1_action_calculated_payoff = tmp_payoff[0]
            p1_calculated_sums = p1_calculated_sums + p1_action_calculated_payoff
            p2_action_calculated_payoff = tmp_payoff[1]
            p2_calculated_sums = p2_calculated_sums + p2_action_calculated_payoff
            # print result of each round
            result.insert(END, str_output.format(count, p1_action_entered + 1, p1_action_entered_payoff,
                                                 p2_action_entered + 1,
                                                 p2_action_entered_payoff, p1_action_calculated + 1,
                                                 p1_action_calculated_payoff, p2_action_calculated + 1,
                                                 p2_action_calculated_payoff))
        result.insert(END, "-----------------------\n")
        result.insert(END,
                      "Average payoffs of entered mixed strategy: Player 1 - {0:.7f} and  Player 2 - {1:.7f}\n".format(
                          float(p1_entered_sums / 100), float(p2_entered_sums / 100)))
        result.insert(END,
                      "Average payoff of calculated mixed strategy:  Player 1 - {0:.7f} and  Player 2 - {1:.7f}\n".format(
                          float(p1_calculated_sums / 100), float(p2_calculated_sums / 100)))
        return


def doClear():
    global frameList, step, entriesList, entriesPayoffs, m_Game, s_step, dropList
    for frame in frameList:
        frame.pack_forget()
    step = 0
    s_step = 0
    entriesList = []
    entriesPayoffs = []
    frameList = []
    dropList = []
    m_Game = None
    button_next.config(text="Next")
    button_next["state"] = "normal"
    button_simulate.config(text="Simulate with p,q")
    button_simulate["state"] = "normal"
    button_simulate.pack_forget()


root = Tk()
root.geometry("800x700")
root.title("Game Theory Project")
df_font = font.Font(family='Helvitica', size=10)
root.option_add("*Font", df_font)
frame1 = Frame(root, width=800, height=650, borderwidth=1)
frame1.pack()
frame1.pack_propagate(0)
frame2 = Frame(root, width=800, height=50, relief=RAISED, borderwidth=1)
frame2.pack(side="bottom")
frame2.pack_propagate(0)
# ----------
frame1_1 = Frame(frame1)
frame1_1.pack(pady=10)
label_mode = Label(frame1, text="Select mode: ")
label_mode.pack()
modeList = ["2 Players - 2 Actions", "2 Players - Many Actions", "Many Players - Many Actions"]
dropdownList_mode = ttk.Combobox(frame1, values=modeList, width=25)
dropdownList_mode.set(modeList[0])
dropdownList_mode.pack()
# ----------
button_reset = Button(frame2, text="Clear", bg='white', fg='black', height=2, width=15, command=doClear)
button_reset.pack(side=LEFT, padx=50, pady=5)
button_next = Button(frame2, text="Next", bg='white', fg='black', height=2, width=15, command=doNext)
button_next.pack(side=RIGHT, padx=50, pady=5)
button_simulate = Button(frame2, text="Simulate with p,q", bg='white', fg='black', height=2, width=15,
                         command=doSimulate)
# ----------
step = 0
s_step = 0
entriesList = []
entriesPayoffs = []
frameList = []
m_Game = None
dropList = []
# ----------
root.mainloop()
