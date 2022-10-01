from custom_exceptions import CUSTOM_EXCEPTIONS

class ParentPortfolio:
    def __init__(self):
        self.minimum_cash_percentage = 0
        self.cash_balance = 0
        self.allocated_balance = 0
        self.pnl = []
        self.date = None
        # dictionary structure:
        #       {'equity:
        #           {
        #               'model_name:
        #                   {
        #                       'model': obj,
        #                       'portfolio': obj
        #                   },
        #               'model_name_2' : {...},
    #               },
        #       }
        self.models = {
            'equity': dict(),
            'options': dict(),
            'futures': dict(),
            'oof': dict()
        }
        self.broker = ""

    # --------------------------------------------
    #                SET METHODS
    # --------------------------------------------
    def set_cash_balance(self, cash_balance):
        self.cash_balance = cash_balance

    def set_date(self, date):
        self.date = date

    def set_minimum_cash_percentage(self, minimum_cash_percentage):
        self.minimum_cash_percentage = minimum_cash_percentage

    def set_broker(self, broker):
        self.broker = broker
        for security_type in self.models:
            for model in self.models[security_type]:
                self.models[security_type][model]['portfolio'].set_broker(self.broker)

    # --------------------------------------------
    #                GET METHODS
    # --------------------------------------------
    def get_cash_balance(self):
        return self.cash_balance

    def get_allocated_balance(self):
        return self.allocated_balance

    def get_pnl(self):
        return self.pnl

    def get_all_securities(self):
        held_securities = dict()
        # iterates through: equity, options, futures, oof
        for security_type in self.models:
            held_securities[security_type] = list()
            # iterates through the models in a list of models
            for model in self.models[security_type]:
                # grabs the model portfolio securities and adds to the list
                held_securities[security_type] += self.models[security_type][model]['portfolio'].get_all_securities()
        return held_securities

    def get_security_universe(self):
        held_securities = dict()
        for security_type in self.models:
            held_securities[security_type] = list()
            for model in self.models[security_type]:
                held_securities[security_type] += self.models[security_type][model]['portfolio'].get_security_universe()

        return held_securities

    def set_model_start_date(self, start_date):
        for security_type in self.models:
            for model in self.models[security_type]:
                self.models[security_type][model]['model'].set_start_date(start_date)

    # --------------------------------------------
    #                UPDATE METHODS
    # --------------------------------------------
    def update_all_dates(self):
        # iterates through: equity, options, futures, oof
        for security_type in self.models:
            # iterates through the models in a list of models
            for model in self.models[security_type]:
                self.models[security_type][model]['model'].set_current_date(self.date)
                self.models[security_type][model]['portfolio'].set_date(self.date)
                self.models[security_type][model]['portfolio'].update_all_dates()

    def update_pnl(self):
        """
        This method first update the pnl down the tree and
        then combines the pnl of all the models and
        accounts for cash_balance and allocated_balance.

        Computation
        -----------
        sum_all_model_pnl + self.cash_balance + self.allocated_balance
        """
        _models_pnl = 0
        for security_type in self.models:
            for model in self.models[security_type]:
                self.models[security_type][model]['portfolio'].update_pnl()
                historical_pnl = self.models[security_type][model]['portfolio'].get_pnl()
                _models_pnl += historical_pnl[-1]

        self.pnl.append(_models_pnl + self.cash_balance + self.allocated_balance)

    def update_relevant(self):
        """
            This method updates the relevant information on market open.
            For example, the current price for an equity.
        """
        for security_type in self.models:
            for model in self.models[security_type]:
                self.models[security_type][model]['portfolio'].update_relevant()

    # --------------------------------------------
    #               OTHER METHODS
    # --------------------------------------------

    def close_position(self, security_type, model, ticker):
        error = True
        _securities = self.models[security_type][model]['portfolio'].get_all_tickers()
        if ticker in _securities:
            _pnl_from_position = self.models[security_type][model]['portfolio'].close_position(ticker)
            self.allocated_balance += _pnl_from_position
            error = False

        if error:
            raise CUSTOM_EXCEPTIONS['closing_security_issue'](ticker)

    def open_position(self, security_type, model, ticker, security_info):
        # Grabs the correct model using the security_type and model parameters
        # Grabs the portfolio of this model and runs open_position
        # The overhead of opening is led by the Model Portfolio
        self.models[security_type][model]['portfolio'].open_position(ticker, security_info)

    def allocate_all_cash(self, max_percentage):
        _portfolio_cash_balance = self.cash_balance
        _to_distribute = int(_portfolio_cash_balance*(1-self.minimum_cash_percentage))



        # iterates through: equity, options, futures, oof
        for security_type in self.models:
            # iterates through the models in a list of models
            for model in self.models[security_type]:
                _model_allocation_percentage = self.models[security_type][model]['portfolio'].get_allocation_percentage()
                _to_allocate = int(_to_distribute*_model_allocation_percentage)

                _max_allowed_single_security = int((max_percentage/_model_allocation_percentage)*100)/100

                self.cash_balance -= _to_allocate
                self.allocated_balance += _to_allocate
                self.models[security_type][model]['portfolio'].set_cash_balance(_to_allocate)
                self.models[security_type][model]['portfolio'].set_maximum_percentage_single_security(_max_allowed_single_security)

    def compute_position_distribution(self):
        for security_type in self.models:
            for model in self.models[security_type]:
                self.models[security_type][model]['portfolio'].compute_position_distribution()