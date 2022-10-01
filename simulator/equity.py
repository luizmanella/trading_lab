from database_extractor import database_extractor
import datetime

class Equity:
    """
    This class is the object representation of a
    stock, etf, or adr. It will hold all necessary methods
    to properly handle the trading of some stock.

    Functionalities:
    - Store security information
    - Manage allocation amount
    - Methods to properly
    """
    def __init__(self):
        self.ticker = None
        self.cash_balance = 0
        self.allocated_balance = 0
        self.allocation_percentage = 0
        self.position_type = None # Should be 1 or -1 for long short
        self.number_of_shares = 0
        self.open_price = 0
        self.current_price = 0
        self.pnl = []
        self.commission = 0
        self.date = None

    # --------------------------------------------
    #                GET METHODS
    # --------------------------------------------
    def get_ticker(self):
        return self.ticker

    def get_cash_balance(self):
        return self.cash_balance

    def get_allocated_balance(self):
        return self.allocated_balance

    def get_allocation_percentage(self):
        return self.allocation_percentage

    def get_position_type(self):
        return self.position_type

    def get_number_of_shares(self):
        return self.number_of_shares

    def get_open_price(self):
        _start_date = self.date
        _split_date = _start_date.split('-')
        _end_date = datetime.date(
            int(_split_date[0]),
            int(_split_date[1]),
            int(_split_date[2])
        )
        _end_date = _end_date + datetime.timedelta(days=1)
        _end_date = str(_end_date)
        _data = database_extractor.equities_get_historical_price_time_bars(
                data_source='P:/Equities',
                symbol=self.ticker,
                timespan='Daily',
                start_date=_start_date,
                end_date=_end_date
        )

        if _data.shape[0] == 0:
            # This means we have no data for this day...possibly a holiday
            # that wasn't covered by the trading calendar building process
            # Remedy -> pass the last price found backwards in time
            _split_start = _start_date.split('-')
            _start_date = datetime.date(
                year=int(_split_start[0]),
                month=int(_split_start[1]),
                day=int(_split_start[2])
            )
            _start_date = str(_start_date - datetime.timedelta(days=5))
            _data = database_extractor.equities_get_historical_price_time_bars(
                data_source='P:/Equities',
                symbol=self.ticker,
                timespan='Daily',
                start_date=_start_date,
                end_date=_end_date
            )
        _open = _data['open'].values[-1]

        return _open

    def get_current_price(self):
        return self.current_price

    def get_pnl(self):
        return self.pnl

    def get_commission(self):
        return self.commission

    def get_date(self):
        return self.date

    # --------------------------------------------
    #                SET METHODS
    # --------------------------------------------
    def set_ticker(self, ticker):
        self.ticker = ticker

    def set_cash_balance(self, cash_balance):
        self.cash_balance = cash_balance

    def set_allocated_balance(self, allocated_balance):
        self.allocated_balance = allocated_balance

    def set_allocation_percentage(self, allocation_percentage):
        self.allocation_percentage = allocation_percentage

    def set_position_type(self, position_type):
        self.position_type = position_type

    def set_number_of_shares(self, number_of_shares):
        self.number_of_shares = number_of_shares

    def set_open_price(self, open_price):
        self.open_price = open_price

    def set_current_price(self, current_price):
        self.current_price = current_price

    def set_commission(self, broker):
        # TODO: pull commission from database
        commission = 0
        self.commission = commission

    def set_date(self, date):
        self.date = date

    # --------------------------------------------
    #                UPDATE METHODS
    # --------------------------------------------
    def update_relevant(self):
        _today = self.date
        _current_price = self.get_open_price()
        self.current_price = _current_price

    def update_pnl(self):
        self.pnl.append((self.current_price-self.open_price)*self.position_type*self.number_of_shares)

    def compute_number_of_shares(self):
        self.number_of_shares = int(self.cash_balance/self.open_price)

    # --------------------------------------------
    #                OTHER METHODS
    # --------------------------------------------
    def charge_commission(self):
        self.cash_balance -= self.commission