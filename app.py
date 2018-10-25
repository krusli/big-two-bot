from random import shuffle
from time import sleep
import requests, json, itertools, sys

def is_single(cards):
    if len(cards) == 1:
        return True
    return False

def is_pair(cards):
    if len(cards) == 2 and float(cards[0][:-1]) == float(cards[1][:-1]):
        return True
    return False

def is_straight(cards):
    # checks if there are 5 cards and the differences in card values are all 1
    if len(cards) != 5:
        return False

    cards = sorted(cards, key=lambda card: float(card[:-1]))
    for i in range(1, len(cards)):
        if float(cards[i][:-1]) != float(cards[i-1][:-1]) + 1:
            return False

    return True

def is_flush(cards):
    # checks if there are 5 cards, and all their suits are the same
    if len(cards) != 5:
        return False

    for i in range(1, len(cards)):
        if cards[i][-1] != cards[i-1][-1]:
            return False

    return True

def is_fullhouse(cards):
    # checks if there are 5 cards, that there is a triple and a pair
    cards = sorted(cards, key=lambda card: float(card[:-1]))
    card_counts = {}
    for card in cards:
        if card[:-1] not in card_counts.keys():
            card_counts[card[:-1]] = 1
        else:
            card_counts[card[:-1]] += 1
    # convert values to list of values (i.e. discard the keys, use the values only)
    card_counts = sorted(list(card_counts.values()))

    if len(card_counts) != 2:   # if there are more than two values in card_counts
        return False
    if card_counts[0] != 2: # if there is no pair
        return False
    if card_counts[1] != 3: # if there is no three-of-a-kind, might be superfluous since we did check. Just here to be safe.
        return False
    return True

def is_fourofakind(cards):
    card_values = [i[:-1] for i in cards]
    value_counts = {}
    for value in card_values:
        if value not in value_counts.keys():
            value_counts[value] = 1
        else:
            value_counts[value] += 1
    value_counts = list(value_counts.values())
    if 4 not in value_counts:
        return False
    return True

def is_straightflush(cards):
    if is_flush(cards) and is_straight(cards):
        return True
    return False

def convert_ranks_to_numbers(cards):
    # convert all higher-ranked cards to numerical rank
    converted_cards = []
    value_dict = {'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 15}
    for card in cards:
        if card[:-1] in value_dict:
            value = value_dict[card[:-1]]
        else:
            value = card[:-1]
        converted_cards.append(str(value) + card[-1])
    return(converted_cards)

def trick_type(cards):
    cards = convert_ranks_to_numbers(cards)

    tests = ['single', 'pair', 'straight', 'flush', 'fullhouse', 'fourofakind', 'straightflush']
    test_array = [is_single(cards), is_pair(cards), is_straight(cards), is_flush(cards), is_fullhouse(cards), is_fourofakind(cards), is_straightflush(cards)]
    indices = [indice for indice, entry in enumerate(test_array) if entry == 1]

    return_list = []
    for index in indices:
        return_list.append(tests[index])

    if len(return_list) == 1:
        return str(return_list[0])
    elif 'straightflush' in return_list:
        return 'straightflush'

def valid_play(last_trick, play):
    """returns True if played cards' value is greater than last trick, False if not, and -1 if invalid play"""

    def convert_cards(cards):
        # convert all higher-ranked cards to numerical rank
        converted_cards = []
        for card in cards:
            if card[:-1] == 'J':
                value = 11
            elif card[:-1] == 'Q':
                value = 12
            elif card[:-1] == 'K':
               value = 13
            elif card[:-1] == 'A':
                value = 14
            elif card[:-1] == '2':
                value = 15
            else:
                value = card[:-1]
            converted_cards.append(str(value) + card[-1])
        cards = converted_cards

        # convert all suits to numerical representation
        converted_cards = []
        for card in cards:
            if card[-1] == 'D':
                value = '.2'
            elif card[-1] == 'C':
                value = '.4'
            elif card[-1] == 'H':
                value = '.6'
            elif card[-1] == 'S':
                value = '.8'
            else:
                value = card[-1]
            converted_cards.append(str(card[:-1]) + value)
        cards = converted_cards
        return cards

    play_converted = convert_cards(play)
    last_trick_converted = convert_cards(last_trick)

    trick_ranks = {'single': 1, 'pair': 2, 'straight': 3, 'flush': 4, 'fullhouse': 5, 'fourofakind': 6, 'straightflush': 7}
    try:
        # convert play and last_trick to float
        play_converted = [float(entry) for entry in play_converted]
        last_trick_converted = [float(entry) for entry in last_trick_converted]

        if trick_type(play) == None or trick_type(last_trick) == None:
            return False

        if trick_ranks[trick_type(play)] == trick_ranks[trick_type(last_trick)]:
            play_trick_type = trick_type(play)
            if play_trick_type == 'single' or play_trick_type == 'pair' or play_trick_type == 'straight' or play_trick_type == 'straightflush':
                if max(play_converted) > max(last_trick_converted):
                    return True
            if play_trick_type == 'flush':
                highest_value = {}
                highest_value['last_trick'] = max([float(str(i)) for i in last_trick_converted])
                highest_value['play'] = max([float(str(i)) for i in play_converted])

                if highest_value['play'] > highest_value['last_trick']:
                    return True

            if play_trick_type == 'fourofakind':
                def find_value_of_fourofakind(cards):
                    value_counts = {}
                    for card in cards: # for the values in the list of cards
                        if str(card)[:-1] not in value_counts.keys():
                            value_counts[str(card)[:-1]] = 1
                        else:
                            value_counts[str(card)[:-1]] += 1

                    # convert value_counts to tuples (key, value)
                    value_counts = value_counts.items()
                    for entry in value_counts:
                        if entry[1] == 4:
                            return float(entry[0])

                if find_value_of_fourofakind(play_converted) > find_value_of_fourofakind(last_trick_converted):
                    return True

            if play_trick_type == 'fullhouse':
                def find_value_of_fullhouse(cards):
                    value_counts = {}
                    for card in cards: # for the values in the list of cards
                        if str(card)[:-1] not in value_counts.keys():
                            value_counts[str(card)[:-1]] = 1
                        else:
                            value_counts[str(card)[:-1]] += 1

                    # convert value_counts to tuples (key, value)
                    value_counts = value_counts.items()
                    for entry in value_counts:
                        if entry[1] == 3:
                            return float(entry[0])

                if find_value_of_fullhouse(play_converted) > find_value_of_fullhouse(last_trick_converted):
                    return True
            return False

        elif trick_ranks[trick_type(play)] > 2 and trick_ranks[trick_type(last_trick)] > 2 and trick_ranks[trick_type(play)] > trick_ranks[trick_type(last_trick)]:
            return True

        else: # if invalid play
            return False
    except ValueError:
        return False

    except NameError:
         return False


# ----- Operating variables for the bot -----
# This will load the last update we've checked, so as to not pass old messages through the bot
try:
    with open('last_update.txt', 'r') as f:
        last_update = int(f.readline().strip())
except FileNotFoundError:
    last_update = 0

# TODO populate token
token = ''
# This is the url for communicating with your bot
url = 'https://api.telegram.org/bot%s/' % token

# group_id = -25226377
group_id = -30547532

game_data = {'players': {}, 'turn_order': [], 'turn': '', 'trick': [], 'status': 0, 'pass_players': [], 'usernames': {}, 'one_card_left_players': []}

# ----- Big Two functions -----
def convert_suit_to_unicode(cards):
    converted_cards = []
    for card in cards:
        if card[-1] == 'C':
            value = '♣'
        elif card[-1] == 'D':
            value = '♦'
        elif card[-1] == 'H':
            value = '♥'
        elif card[-1] == 'S':
            value = '♠'
        else:
            value = ''
        converted_cards.append(card[:-1] + value)
    return converted_cards

def send_hand(player):
    def convert_cards(cards):

        # convert all higher-ranked cards to numerical rank, and vice versa
        # function can convert numerical rank back to rank
        converted_cards = []
        for card in cards:
            if card[:-1] == 'J':
                value = 11
            elif card[:-1] == 'Q':
                value = 12
            elif card[:-1] == 'K':
                value = 13
            elif card[:-1] == 'A':
                value = 14
            elif card[:-1] == '2':
                value = 15
            elif card[:-1] == '11':
                value = 'J'
            elif card[:-1] == '12':
                value = 'Q'
            elif card[:-1] == '13':
                value = 'K'
            elif card[:-1] == '14':
                value = 'A'
            elif card[:-1] == '15':
                value = '2'
            else:
                value = card[:-1]
            converted_cards.append(str(value) + card[-1])

        return converted_cards

    player_hand = convert_cards(game_data['players'][player])
    player_hand = sorted(player_hand, key = lambda x: float(x[:-1])) # sort according to value
    player_hand = convert_cards(player_hand) # convert back to non-numerical values
    player_hand_output = convert_suit_to_unicode(player_hand)

    player_hand = game_data['players'][player]

    send_message(player, 'Your hand:\n' + ', '.join(player_hand_output))

def send_combinations(player):
    def convert_cards(cards):

        # convert all higher-ranked cards to numerical rank, and vice versa
        # function can convert numerical rank back to rank
        converted_cards = []
        for card in cards:
            if card[:-1] == 'J':
                value = 11
            elif card[:-1] == 'Q':
                value = 12
            elif card[:-1] == 'K':
                value = 13
            elif card[:-1] == 'A':
                value = 14
            elif card[:-1] == '2':
                value = 15
            elif card[:-1] == '11':
                value = 'J'
            elif card[:-1] == '12':
                value = 'Q'
            elif card[:-1] == '13':
                value = 'K'
            elif card[:-1] == '14':
                value = 'A'
            elif card[:-1] == '15':
                value = '2'
            else:
                value = card[:-1]
            converted_cards.append(str(value) + card[-1])

        return converted_cards

    try:
        player_hand = convert_cards(game_data['players'][player])
        player_hand = sorted(player_hand, key = lambda x: float(x[:-1])) # sort according to value
        player_hand = convert_cards(player_hand) # convert back to non-numerical values
        player_hand_output = convert_suit_to_unicode(player_hand)

        # generate all possible combinations from player's hand
        possible_combinations = []
        for card_length in [1, 2, 5]:
            for combination in itertools.combinations(player_hand, card_length):
                possible_combinations.append(list(combination))

        possible_plays = {}
        for play in possible_combinations:
            play_type = trick_type(play)
            if play_type not in possible_plays:
                possible_plays[play_type] = [play]
            else:
                possible_plays[play_type].append(play)


        # sort
        for play_type in possible_plays:
            for i in range(len(possible_plays[play_type])):
                possible_plays[play_type][i] = convert_cards(possible_plays[play_type][i])
                possible_plays[play_type][i] = sorted(possible_plays[play_type][i], key = lambda x: float(x[:-1]))
            possible_plays[play_type] = sorted(possible_plays[play_type], key = lambda x: x[0][:-1])


        output_string = "Possible combinations:\n"
        output_string += "single\n" + ', '.join(player_hand_output) + "\n\n"
        for play_type in possible_plays:
            if play_type not in [None, "single"]:
                output_string += str(play_type) + "\n"
                for play in possible_plays[play_type]:
                    # convert higher rank back to alphabetical, suits to unicode symbols
                    output_string += "- " + ', '.join(convert_suit_to_unicode(convert_cards(play))) + "\n"
                output_string += "\n"

        send_message(player, output_string)
    except KeyError:
        pass

def next_turn():
    # update current turn
    if game_data['turn_order'].index(game_data['turn']) + 1 > len(game_data['turn_order']) - 1:
        next_turn_index = game_data['turn_order'].index(game_data['turn']) + 1 - len(game_data['turn_order'])
        game_data['turn'] = game_data['turn_order'][next_turn_index]

    else:
        next_turn_index = game_data['turn_order'].index(game_data['turn']) + 1
        game_data['turn'] = game_data['turn_order'][next_turn_index]

    # send message to group, tell us whose turn it is
    send_message(group_id, '@' + game_data['usernames'][game_data['turn']] + "'s turn.")

    if game_data['turn'] in game_data['pass_players']:
        next_turn()

# ----- Messaging functions -----
def send_message(chatid, message):
# function to send messages to chatid.
    i = 0
    while True and i < 5:
        try:
            requests.get(url + 'sendMessage', params=dict(chat_id = chatid, text = message))
            break
        except requests.ConnectionError:
            logger.error('ConnectionError', exc_info = True)
            i += 1

# ----- main bot code block -----
# We want to keep checking for updates. So this must be a never ending loop
while True:
    # My chat is up and running, I need to maintain it! Get me all chat updates
    try:
        get_updates = json.loads(requests.get(url + 'getUpdates', dict(offset=last_update)).text)
    except:
        pass
    # Ok, I've got 'em. Let's iterate through each one
    for update in get_updates['result']:
        # First make sure I haven't read this update yet
        if last_update < update['update_id']:
            last_update = update['update_id']
            # I've got a new update!
            # Write the value for last_update to file
            with open('last_update.txt', 'w') as file2:
                file2.write(str(last_update))

            if 'message' in update.keys():
                # check if the latest update is a message as to avoid a KeyError for update['message']['text']
                if 'text' in update['message'].keys():
                    try: # general error handling, pass on to logger (to be implemented)
                        if update['message']['text'].startswith("/status"):
                            send_message(update['message']['chat']['id'], "I'm up and running!")
                        if update['message']['text'].startswith("/newgame"):
                            game_data = {'players': {}, 'turn_order': [], 'turn': '', 'trick': [], 'status': 0, 'pass_players': [], 'usernames': {}, 'one_card_left_players': []}
                            send_message(group_id, "New game started! Use /join in a private chat with @big_two_bot to join the game.")
                        if update['message']['text'].startswith("/join"):
                            if update['message']['chat']['type'] == 'group':
                                send_message(update['message']['chat']['id'], "Please /join from a private chat with @big_two_bot.")
                            elif update['message']['chat']['type'] == 'private':
                                if update['message']['chat']['id'] not in game_data['players'].keys() and len(list(game_data['players'].keys())) <= 4:
                                    player_ID = update['message']['chat']['id']

                                    # save username
                                    try:
                                        game_data['usernames'][player_ID] = update['message']['chat']['username']
                                    except KeyError:
                                        game_data['usernames'][player_ID] = 'user'

                                    send_message(group_id, '@' + game_data['usernames'][player_ID] + ' has joined the game!')
                                    game_data['players'][player_ID] = [] # initialise empty deck for the player
                        if update['message']['text'].startswith("/startgame") and len(game_data['players'].keys()) > 1 and len(game_data['players'].keys()) < 5 and game_data['status'] == 0:
                            # update game status to 'started'
                            game_data['status'] = 1

                            # create a deck of 52 cards
                            suits = ['C', 'D', 'H', 'S']
                            cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
                            deck = []
                            for suit in suits:
                                for card in cards:
                                    deck.append(card + suit)

                            # shuffle the deck
                            shuffle(deck)

                            # divide according to number of players
                            no_of_cards_per_player = 13

                            while True:
                                # distribute the deck to players
                                for player in game_data['players'].keys():
                                    for i in range(no_of_cards_per_player):
                                        game_data['players'][player].append(deck.pop(0))

                                distributed_cards = []
                                for player in game_data['players'].keys():
                                    distributed_cards.extend(game_data['players'][player])

                                if '3D' in distributed_cards:
                                    break
                                else:
                                    suits = ['C', 'D', 'H', 'S']
                                    cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
                                    deck = []
                                    for player in game_data['players'].keys():
                                        game_data['players'][player] = []
                                    for suit in suits:
                                        for card in cards:
                                            deck.append(card + suit)

                                    shuffle(deck)

                            # set player with 3 of diamonds as current_turn
                            for player in game_data['players'].keys():
                                if '3D' in game_data['players'][player]:
                                    game_data['turn'] = player

                            # determine turn order
                            game_data['turn_order'].append(game_data['turn'])
                            turn_order_others = [i for i in game_data['players'].keys() if i != game_data['turn']]
                            shuffle(turn_order_others)
                            game_data['turn_order'].extend(turn_order_others)

                            # send turn order to group
                            turn_order_list = [game_data['usernames'][entry] for entry in game_data['turn_order']]
                            send_message(group_id, 'Turn order: ' + ', '.join(turn_order_list))

                            # send decks to each player
                            for player in game_data['players'].keys():
                                send_hand(player)

                        if update['message']['text'].startswith("/play ") and update['message']['chat']['id'] == game_data['turn']:
                            play = update['message']['text'].upper()
                            play = play.split()
                            play = play[1:]

                            def update_hand(play, player_ID):
                                card_indices = [no for no, data in enumerate(game_data['players'][player_ID]) if data in play]
                                while len(card_indices) > 0:
                                    del game_data['players'][player_ID][card_indices[0]]
                                    card_indices = [no for no, data in enumerate(game_data['players'][player_ID]) if data in play]

                            def format_trick_for_output():
                                trick = game_data['trick']
                                trick_converted = []
                                for entry in trick:
                                    trick_converted.append(convert_suit_to_unicode(entry))

                                trick = trick_converted

                                return trick

                            message_data = update['message']['text'].split()
                            print(message_data)
                            if len(game_data['trick']) == 0 and game_data['status'] == 1: # if first card played
                                if '3D' in message_data[1:] or '3d' in message_data[1:]:
                                    print(trick_type(play))
                                    if trick_type(play) != None:
                                        game_data['trick'].append(play)
                                        send_message(group_id, "Last trick:\n" + str(format_trick_for_output()[-1]))
                                        update_hand(play, update['message']['chat']['id'])
                                        send_hand(update['message']['chat']['id'])
                                        next_turn()
                                        game_data['status'] = 2 # after 3 of diamonds played, set status to 2
                                else:
                                   send_message(game_data['turn'], "Please start with the 3 of Diamonds.")


                            else:
                                def is_in_hand(play, hand):
                                    hand_permutations = itertools.permutations(hand, len(play))
                                    if tuple(play) in hand_permutations:
                                        return True
                                    return False

                                if len(game_data['trick']) > 0:
                                    is_valid_play = valid_play(game_data['trick'][-1], play)
                                elif is_in_hand(play, game_data['players'][update['message']['chat']['id']]):
                                    if trick_type(play) != None:
                                        is_valid_play = True
                                    else:
                                        is_valid_play = False
                                else:
                                    is_valid_play = False



                                if is_valid_play and is_in_hand(play, game_data['players'][update['message']['chat']['id']]):
                                    game_data['trick'].append(play)
                                    send_message(group_id, "Last trick:\n" + str(format_trick_for_output()[-1]))
                                    update_hand(play, update['message']['chat']['id'])
                                    send_hand(update['message']['chat']['id'])
                                    next_turn()
                                elif not is_in_hand(play, game_data['players'][update['message']['chat']['id']]):
                                    send_message(game_data['turn'], "You do not have the cards to make this play.")
                                else:
                                	send_message(game_data['turn'], "Invalid play.")

                        if update['message']['text'].startswith("/pass") and update['message']['chat']['id'] == game_data['turn'] and len(game_data['pass_players']) < len(game_data['players']) - 1 and game_data['status'] == 2:
                        # add username to game_data['pass_players']
                            game_data['pass_players'].append(game_data['turn'])
                            send_message(group_id, '@' + game_data['usernames'][update['message']['chat']['id']] + " passed.")
                            next_turn()

                        if update['message']['text'].startswith("/hand") and update['message']['chat']['type'] == 'private':
                            try:
                                send_hand(update['message']['chat']['id'])
                            except KeyError:
                                pass

                        if update['message']['text'].startswith("/combos") and update['message']['chat']['type'] == 'private':
                            send_combinations(update['message']['chat']['id'])

                        if update['message']['text'].startswith("/plays") and update['message']['chat']['type'] == 'private' and game_data['turn'] == update['message']['chat']['id']:
                            try:
                                def convert_cards_for_plays(cards):
                                    # convert all higher-ranked cards to numerical rank, and vice versa
                                    # function can convert numerical rank back to rank
                                    converted_cards = []
                                    for card in cards:
                                        if card[:-1] == 'J':
                                            value = 11
                                        elif card[:-1] == 'Q':
                                            value = 12
                                        elif card[:-1] == 'K':
                                            value = 13
                                        elif card[:-1] == 'A':
                                            value = 14
                                        elif card[:-1] == '2':
                                            value = 15
                                        elif card[:-1] == '11':
                                            value = 'J'
                                        elif card[:-1] == '12':
                                            value = 'Q'
                                        elif card[:-1] == '13':
                                            value = 'K'
                                        elif card[:-1] == '14':
                                            value = 'A'
                                        elif card[:-1] == '15':
                                            value = '2'
                                        else:
                                            value = card[:-1]
                                        converted_cards.append(str(value) + card[-1])

                                    return converted_cards

                                player_hand = game_data['players'][update['message']['chat']['id']]
                                player_hand = convert_cards_for_plays(game_data['players'][update['message']['chat']['id']])
                                player_hand = sorted(player_hand, key = lambda x: float(x[:-1])) # sort according to value
                                player_hand = convert_cards_for_plays(player_hand) # convert back to non-numerical values
                                player_hand_output = convert_suit_to_unicode(player_hand)

                                possible_combinations = []
                                for card_length in [1, 2, 5]:
                                    for combination in itertools.combinations(player_hand, card_length):
                                        possible_combinations.append(list(combination))

                                valid_plays = {}
                                for play in possible_combinations:
                                    play_type = trick_type(play)
                                    if len(game_data['trick']) > 0:
                                        if valid_play(game_data['trick'][-1], play):
                                            if play_type not in valid_plays:
                                                valid_plays[play_type] = [play]
                                            else:
                                                valid_plays[play_type].append(play)
                                    else:
                                        if play_type not in valid_plays:
                                            valid_plays[play_type] = [play]
                                        else:
                                            valid_plays[play_type].append(play)

                                for play_type in valid_plays:
                                    for i in range(len(valid_plays[play_type])):
                                        valid_plays[play_type][i] = convert_cards_for_plays(valid_plays[play_type][i]) # convert all ranks to numerical
                                        valid_plays[play_type][i] = sorted(valid_plays[play_type][i], key = lambda x: float(x[:-1]))
                                    valid_plays[play_type] = sorted(valid_plays[play_type], key = lambda x: x[0][:-1])

                                output_string = "Valid plays:"
                                if 'single' in valid_plays:
                                    output_string += "\n" + 'single' + "\n"
                                    single_cards = [str(convert_suit_to_unicode(convert_cards_for_plays(x))[0]) for x in valid_plays['single']]
                                    single_cards = convert_cards_for_plays(single_cards)
                                    single_cards = sorted(single_cards, key = lambda x: float(x[:-1]))
                                    single_cards = convert_cards_for_plays(single_cards)
                                    output_string += ', '.join(single_cards) + '\n'
                                for play_type in valid_plays:
                                    if play_type not in [None, "single"]:
                                        output_string += "\n" + str(play_type) + "\n"
                                        for play in valid_plays[play_type]:
                                            output_string += "- " + ", ".join(convert_suit_to_unicode(convert_cards_for_plays(play))) + "\n"


                                send_message(update['message']['chat']['id'], output_string)
                            except KeyError:
                                pass
                            except IndexError:
                                pass

                        if update['message']['text'].startswith("/turn"):
                            try:
                                send_message(update['message']['chat']['id'], '@' + game_data['usernames'][game_data['turn']] + "'s turn.")
                            except KeyError:
                                pass

                        if update['message']['text'].startswith("/lasttrick"):
                            def format_trick_for_output():
                                trick = game_data['trick']
                                trick_converted = []
                                for entry in trick:
                                    trick_converted.append(convert_suit_to_unicode(entry))

                                trick = trick_converted

                                return trick
                            if len(game_data['trick']) != 0:
                                send_message(update['message']['chat']['id'], "Last trick:\n" + str(format_trick_for_output()[-1]))
                            else:
                                send_message(update['message']['chat']['id'], "Last trick:\n" + '[]')
                        print(game_data)

                    except ZeroDivisionError:
                        print(sys.exc_info()[0])


                    # below code is run on every iteration
                    try:
                        if game_data['status'] == 0:
                            raise NameError
                        # ----- checks to be run on each iteration if a game is ongoing -----

                        # if others passed already, go to player that is not in 'pass' list in game_data
                        if len(game_data['pass_players']) == len(game_data['players']) - 1:
                            pass_count = {}
                            for player in game_data['players'].keys():
                                if player not in pass_count.keys():
                                    pass_count[player] = 1
                            # convert pass_counts to tuples
                            pass_count = pass_count.items()

                            for entry in pass_count:
                                if entry[1] == 0:
                                    game_data['turn'] = entry[0]   # set turn to player that has not passed

                            # clear list of tricks
                            game_data['trick'] = []

                            # remove pass_players
                            game_data['pass_players'] = []
                            send_message(group_id, '@' + game_data['usernames'][game_data['turn']] + "'s turn to start a new trick.")



                        # check if any player's deck lengths are 1, if found, send one card left notification
                        for player in game_data['players'].keys():
                            if len(game_data['players'][player]) == 1 and game_data['status'] == 2 and player not in game_data['one_card_left_players']:
                                send_message(group_id, '@' + game_data['usernames'][player] + ' has one card left!')
                                game_data['one_card_left_players'].append(player)

                        # check if any player's deck lengths are 0, if found, declare winner
                        players = game_data['players'].keys()
                        for player in players:
                            if len(game_data['players'][player]) == 0 and game_data['status'] == 2:
                                send_message(group_id, 'The winner is @' + game_data['usernames'][player] + '.')
                                del(game_data['players'][player])
                                del(game_data['turn_order'][game_data['turn_order'].index(player)])
                                game_data = {'players': {}, 'turn_order': [], 'turn': '', 'trick': [], 'status': 0, 'pass_players': [], 'usernames': {}, 'one_card_left_players': []}
                                send_message(group_id, "New game started! Use /join in a private chat with @big_two_bot to join the game.")
                                break
                        del players


                    except NameError:
                        pass
                    except IndexError:
                        pass
    sleep(2)
