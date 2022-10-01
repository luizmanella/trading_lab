from equity import Equity
import math

class EquityPortfolio:
    def __init__(self):
        self.maximum_percentage_single_security = 0
        self.allocation_percentage = 0
        self.cash_balance = 0
        self.allocated_balance = 0
        self.pnl = []
        self.date = None
        self.securities = dict()   # { 'ticker' : object (e.g. Equity Obj, ... }
        self.openings_failed = 0
        self.position_distribution_historical = dict()
        self.security_universe = list()
        self.broker = ""

    # --------------------------------------------
    #               SET METHODS
    # --------------------------------------------
    def set_cash_balance(self, cash_balance):
        self.cash_balance = cash_balance

    def set_date(self, date):
        self.date = date

    def set_allocation_percentage(self, allocation_percentage):
        self.allocation_percentage = allocation_percentage

    def set_maximum_percentage_single_security(self, max_percentage):
        self.maximum_percentage_single_security = max_percentage

    def set_security_universe(self, universe):
        self.security_universe = universe

    def set_broker(self, broker):
        self.broker = broker

    # --------------------------------------------
    #               GET METHODS
    # --------------------------------------------
    def get_cash_balance(self):
        return self.cash_balance

    def get_allocated_balance(self):
        return self.allocated_balance

    def get_pnl(self):
        return self.pnl

    def get_date(self):
        return self.date

    def get_all_securities(self):
        """
        This methods returns all the securities currently held.

        Return
        ------
        { 'ticker' : ticker, 'position_type : 1 or -1 }
        """
        securities_list = list()
        for security in self.securities:
            securities_list.append({
                'ticker': security,
                'position_type': self.securities[security].get_position_type()
            })
        return securities_list

    def get_all_tickers(self):
        return self.securities.keys()

    def get_allocation_percentage(self):
        return self.allocation_percentage

    def get_security_universe(self):
        return self.security_universe

    # --------------------------------------------
    #               UPDATE METHODS
    # --------------------------------------------

    def update_all_dates(self):
        if len(self.securities) != 0:
            for security in self.securities:
                self.securities[security].set_date(self.date)

    def update_pnl(self):
        """
        This method combines the pnl of all the securities
        and accounts for cash_balance and allocated_balance.

        Computation
        -----------
        sum_all_securities_pnl + self.cash_balance _ self.allocated_balance
        """
        _securities_pnl =  0
        for security in self.securities:
            self.securities[security].update_pnl()
            _historical_pnl = self.securities[security].get_pnl()
            _securities_pnl += _historical_pnl[-1]
        self.pnl.append(_securities_pnl)

    def update_relevant(self):
        for security in self.securities:
            self.securities[security].update_relevant()

    # --------------------------------------------
    #                OTHER METHODS
    # --------------------------------------------
    def close_position(self, ticker):
        self.securities[ticker].charge_commission()
        _pnl_from_position = self.securities[ticker].get_pnl()
        _pnl_from_position = _pnl_from_position[-1]
        _cash_balance_from_position = self.securities[ticker].get_cash_balance()
        _allocated_balance_from_position = self.securities[ticker].get_allocated_balance()
        self.cash_balance += _pnl_from_position +_allocated_balance_from_position + _cash_balance_from_position
        self.allocated_balance -= _allocated_balance_from_position + _cash_balance_from_position

        del self.securities[ticker]

        # return is used to update the parent portfolio
        return _pnl_from_position

    def open_position(self, ticker, security_info):
        # Create new Equity
        new_position = Equity()

        # Run all appropriate set methods
        new_position.set_ticker(ticker)
        new_position.set_allocation_percentage(security_info['allocation_percentage'])
        new_position.set_position_type(security_info['position_type'])
        new_position.set_commission(self.broker)
        new_position.set_date(self.date)

        # Updates the current price
        new_position.update_relevant()

        # Compute and store share count
        new_position.open_price = new_position.current_price

        # Now we check if we are trading the minimum accepted amount
        _min_acceptable_shares = math.ceil(200/new_position.open_price)
        _max_acceptable_investment = self.maximum_percentage_single_security * (self.cash_balance + self.allocated_balance)
        _expected_investment = new_position.allocation_percentage * self.cash_balance

        _max_share_possible = int(_max_acceptable_investment/new_position.open_price)

        if _min_acceptable_shares <= _max_share_possible:
            # Update these in proper order
            if _max_acceptable_investment < _expected_investment:
                _amount_to_allocate = int(_max_acceptable_investment)
            else:
                _amount_to_allocate = int(_expected_investment)
            # Allocate base amount of cash and move from Equity Portfolio
            # to equity object
            self.cash_balance -= _amount_to_allocate
            self.allocated_balance += _amount_to_allocate
            new_position.cash_balance += _amount_to_allocate
            # Compute number of shares to hold
            new_position.compute_number_of_shares()


            # Move money around the Equity Obj when entering position
            _amount_to_allocate = new_position.number_of_shares * new_position.current_price
            new_position.cash_balance -= _amount_to_allocate
            new_position.allocated_balance += _amount_to_allocate

            # Charge commissions
            new_position.charge_commission()

            # Store the new position in the dictionary of securitiesFlo
            self.securities[ticker] = new_position
        else:
            self.openings_failed += 1

    def compute_position_distribution(self):
        _temp_distribution = list()
        for security in self.securities:
            _security_cash_balance = self.securities[security].get_cash_balance()
            _security_allocated_balance = self.securities[security].get_allocated_balance()
            _security_total_allocated = _security_cash_balance + _security_allocated_balance
            _temp_distribution.append(_security_total_allocated/(self.cash_balance + self.allocated_balance))
        self.position_distribution_historical[self.date] = _temp_distribution

    def compare_security(self, security, security_info):
        """
        The method returns a tuple. First item is for closing, second is for opening
        """
        if security in self.securities.keys():
            if security_info == self.securities[security].get_position_type() or security_info == 404:
                # Case where you have a security and you are to continue holding it
                # or the case where you have no data and want nothing to happen
                return (False, False)
            elif security_info == 0:
                # Case where you have a position and need to close it
                return (True, False)
            else:
                # Case where you have a position (long|short) and are given an opposite signal (short|long)
                return (True, True)
        elif security_info == 404:
            # This case is for precaution...if there's no data, then do nohting
            return (False, False)
        else:
            # Case where you do not have an open position but got signal to open it
            return (False, True)