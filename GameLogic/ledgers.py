
class PinochleLedger:

    min_balance_allowed = 1

    def __init__(self):
        self.accounts = {}

    def add_player(self, player, account_value=0):
        self.accounts[player] = account_value

    def remove_player(self, player):
        if player in self.accounts:
            del self.accounts[player]

    def check_player_has_sufficient_balance(self, player):
        return self.accounts[player] >= self.min_balance_allowed

    def make_deposit(self, player, amount):
        self.accounts[player] += amount

    def make_withdrawal(self, player, amount):
        if self.accounts[player] >= amount:
            self.accounts[player] -= amount
        else:
            print('Trying to withdraw more money than available')
            raise ValueError

    def check_balances(self):
        assert all([val > 0 for val in self.accounts.values()]), 'Ledger NOT BALANCED !!!'

    def __getitem__(self, item):
        return self.accounts[item]

    def __setitem__(self, key, value):
        self.accounts[key] = value
