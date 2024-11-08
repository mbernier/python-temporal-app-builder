from dataobjs import StandardDeck, Player, PokerScorer
from datetime import timedelta
from temporalio import activity, workflow


@activity.defn
async def poker_activity() -> None:
        # activity.logger.critical("Running activity")
    player = Player()

    points = 100

    end = False
    while not end:
        print("You have {0} points".format(points))
        print()

        points -= 5

        # Hand Loop
        deck = StandardDeck()
        deck.shuffle()

        # Deal Out
        for i in range(5):
            player.addCard(deck.deal())

        # Make them visible
        for card in player.cards:
            card.showing = True
        print(player.cards)

        validInput = False
        while not validInput:
            print("Which cards do you want to discard? ( ie. 1, 2, 3 )")
            print("*Just hit return to hold all, type exit to quit")
            inputStr = input()

            if inputStr == "exit":
                end = True
                break

            try:
                inputList = [int(inp.strip()) for inp in inputStr.split(",") if inp]

                for inp in inputList:
                    if inp > 6:
                        continue
                    if inp < 1:
                        continue

                for inp in inputList:
                    player.cards[inp - 1] = deck.deal()
                    player.cards[inp - 1].showing = True

                validInput = True
            except:
                print("Input Error: use commas to separated the cards you want to hold")

            print(player.cards)
            # Score
            score = PokerScorer(player.cards)
            straight = score.straight()
            flush = score.flush()
            highestCount = score.highestCount()
            pairs = score.pairs()

            # Royal flush
            if straight and flush and straight == 14:
                print("Royal Flush!!!")
                print("+2000")
                points += 2000

            # Straight flush
            elif straight and flush:
                print("Straight Flush!")
                print("+250")
                points += 250

            # 4 of a kind
            elif score.fourKind():
                print("Four of a kind!")
                print("+125")
                points += 125

            # Full House
            elif score.fullHouse():
                print("Full House!")
                print("+40")
                points += 40

            # Flush
            elif flush:
                print("Flush!")
                print("+25")
                points += 25

            # Straight
            elif straight:
                print("Straight!")
                print("+20")
                points += 20

            # 3 of a kind
            elif highestCount == 3:
                print("Three of a Kind!")
                print("+15")
                points += 15

            # 2 pair
            elif len(pairs) == 2:
                print("Two Pairs!")
                print("+10")
                points += 10

            # Jacks or better
            elif pairs and pairs[0] > 10:
                print("Jacks or Better!")
                print("+5")
                points += 5

            player.cards = []

            print() 
            print()
            print()






@workflow.defn
class PokerWorkflow:

    @workflow.run
    async def run(self) -> None:
        # workflow.logger.critical("Running workflow")
        print await workflow.execute_activity(
                    poker_activity,
                    start_to_close_timeout=timedelta(seconds=10),
                )
                



