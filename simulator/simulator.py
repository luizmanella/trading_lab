# Imports
from calendar import calendar
from parent_portfolio import ParentPortfolio
from equity_portfolio import EquityPortfolio
from trade_manager import TradeManager
import datetime
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
import pandas as pd
from custom_exceptions import CUSTOM_EXCEPTIONS
import matplotlib.pyplot as plt


class Simulator:
    """
    Main simulator object.
    """
    def __init__(self):
        self.start_date = datetime.date(2000, 1, 1)
        self.end_date = datetime.date.today()

        # Maximum we allow to allocate to one security
        self.maximum_single_percent_allocation = 0.05

        # We iterate through this list when simulating trading
        self.trading_schedule = list()

        # Create TradeManager Object
        self.trade_manager = TradeManager()

        # Create ParentPortfolio Object
        self.portfolio = ParentPortfolio()

        # Grabs the security universe
        self.security_universe = dict()

        # Stores Broker
        self.broker = ""

    # --------------------------------------------
    #                SET METHODS
    # -------------------------------------------
    def set_maximum_single_percent_allocation(self, max_percent):
        self.maximum_single_percent_allocation = max_percent

    def set_starting_capital(self, value):
        """
        This method sets the starting capital for the simulation.

        Arguments:
        ----------
            amount - integer
        """
        self.portfolio.set_cash_balance(value)

    def set_start_date(self, start_date):
        """
            This method sets the start date.

            Arguments:
            ----------
                start_date - datetime
        """
        self.start_date = start_date

    def set_end_date(self, end_date):
        """
            This method sets the end date.

            Arguments:
            ----------
                end_date - datetime
        """
        self.end_date = end_date

    def set_minimum_cash_percentage(self, minimum_cash_percentage):
        self.portfolio.set_minimum_cash_percentage(minimum_cash_percentage)

    def set_trading_schedule(self):
        self.trading_schedule = list()


    def set_model_start_date(self):
        self.portfolio.set_model_start_date(self.start_date)

    def set_broker(self, broker):
        self.broker = broker
        self.portfolio.set_broker(self.broker)

    # --------------------------------------------
    #                UPDATE METHODS
    # --------------------------------------------
    def update_all_dates(self, date):
        """
        This method updates all the dates in the parent portfolio,
        model portfolio, and securities by making subsequent calls
        to the methods down the tree.

        Arguments:
        ----------
            date - datetime object
        """
        self.portfolio.set_date(date)
        self.portfolio.update_all_dates()

    def update_relevant(self):
        """
            This method updates the relevant information on market open.
            For example, the current price for an equity.
        """
        self.portfolio.update_relevant()

    def update_pnl(self):
        """
            This method updates all pnl.
        """
        self.portfolio.update_pnl()

    def update_security_universe(self):
        self.security_universe = self.portfolio.get_security_universe()

    def build_trading_schedule(self):
        holidays = CustomBusinessDay(calendar=USFederalHolidayCalendar())
        _dates = pd.date_range(str(self.start_date), str(self.end_date), freq=holidays)
        _dates = [str(i).split()[0] for i in _dates]
        self.trading_schedule = _dates

    # --------------------------------------------
    #                OTHER METHODS
    # --------------------------------------------
    def add_model(self, model_name, model, security_type, security_universe, allocation_percentage):
        """
        This method is meant to instantiate the model
        to be used and the portfolio associated with it.

        Arguments:
            model - class object
            security_type - string
        """
        if model_name in self.portfolio.models.keys():
            raise CUSTOM_EXCEPTIONS['duplicate_model_name']

        portfolio_obj = None
        _model = model()
        if security_type == 'equity':
            portfolio_obj = EquityPortfolio()
            portfolio_obj.allocation_percentage = allocation_percentage
            portfolio_obj.set_security_universe(security_universe)
            _model.set_security_universe(security_universe)
        elif security_type == 'options':
            pass
        elif security_type == 'futures':
            pass
        elif security_type == 'oof':
            pass
        self.portfolio.models[security_type][model_name] = {'model': _model, 'portfolio': portfolio_obj}

    def remove_first_pnl_index(self):
        self.portfolio.pnl = self.portfolio.pnl[1:]
        for security_type in self.portfolio.models:
            for model in self.portfolio.models[security_type]:
                _pnl = self.portfolio.models[security_type][model]['portfolio'].pnl
                self.portfolio.models[security_type][model]['portfolio'].pnl = _pnl[1:]

    def run(self):
        """
        This method runs the simulation. There are a lot of steps.

        Steps:
        -----
        1) Preliminary steps
        2) Distribute money equally between models
                    BEGIN ACTION 1
        3) Update the date on all portfolios and securities
        4) Update the relevant information
        5) Update PNL
        6) Close positions
        7) Open positions
        8) Compute the distribution of the positions
                    BEGIN ACTION 2, 3, and 4
        9) Run models and store their output
        10) Pass signals to Trade Manager for opening/closing

        """


        #                   STEP 1
        # --------------------------------------------
        self.update_security_universe()
        self.build_trading_schedule()
        self.set_model_start_date()

        # Delete the elements of the models dictionary to avoid
        # unnecessary loops
        _to_delete = list()
        for security_type in self.portfolio.models:
            if len(self.portfolio.models[security_type]) == 0:
                _to_delete.append(security_type)

        # Raises custom error if no model was added
        if len(_to_delete) == len(self.portfolio.models):
            raise CUSTOM_EXCEPTIONS['no_model']

        for security_type in _to_delete:
            del self.portfolio.models[security_type]

        # Makes sure only traded security types are account for across everything
        _to_close_structure = dict()
        _to_open_structure = dict()
        for security_type in self.portfolio.models:
            _to_close_structure[security_type] = dict()
            _to_open_structure[security_type] = dict()
            for model in self.portfolio.models[security_type]:
                _to_close_structure[security_type][model] = list()
                _to_open_structure[security_type][model] = dict()

        # Sets base dictionary structure
        self.trade_manager.set_base_structure_positions_to_close(_to_close_structure)
        self.trade_manager.set_base_structure_positions_to_open(_to_open_structure)

        #                   STEP 2
        # --------------------------------------------
        self.portfolio.allocate_all_cash(self.maximum_single_percent_allocation)

        # --------------------------------------------
        #          ACTUALLY START SIMULATION
        # --------------------------------------------

        for date in self.trading_schedule:
            #                   STEP 3
            # ----------------------------------------------
            self.update_all_dates(date)
            #                   STEP 4
            # ----------------------------------------------
            self.update_relevant()
            #                   STEP 5
            # ----------------------------------------------
            self.update_pnl()
            #                   STEP 6
            # ----------------------------------------------
            self.trade_manager.close_all_positions(self.portfolio.close_position)
            #                   STEP 7
            # ----------------------------------------------
            self.trade_manager.open_all_positions(self.portfolio.open_position)
            #                   STEP 8
            # ----------------------------------------------
            self.portfolio.compute_position_distribution()
            #                   STEP 9
            # ----------------------------------------------
            # _all_model_signals structure:
            # {
            #     'equity:
            #     {
            #       'model_name:
            #            {
            #                'ticker': {ticker_info}
            #            },
            #     },
            # }
            _all_model_signals = dict()
            for security_type in self.portfolio.models:
                _all_model_signals[security_type] = dict()
                for model in self.portfolio.models[security_type]:
                    _model_signals = self.portfolio.models[security_type][model]['model'].run()
                    _all_model_signals[security_type][model] = _model_signals


            #                   STEP 10
            # ----------------------------------------------
            # Here we compare the model-dictated portfolio and the current holdings
            # Based on the difference we send signals to the Trade Manager of what
            # we should buy/sell.
            for security_type in _all_model_signals:
                for model in _all_model_signals[security_type]:
                    for ticker in _all_model_signals[security_type][model]:
                        signal_close, signal_open = self.portfolio.models[security_type][model]['portfolio'].compare_security(
                            ticker, _all_model_signals[security_type][model][ticker]
                        )
                        # If we received a signal to close something
                        if signal_close:
                            self.trade_manager.add_new_position_to_close(
                                security_type,
                                model,
                                ticker
                            )
                        # If we received a signal to open something
                        if signal_open:
                            self.trade_manager.add_new_position_to_open(
                                security_type,
                                model, 
                                ticker,
                                _all_model_signals[security_type][model][ticker]
                            )


    def graph_simulation_results(self):
        plt.plot(self.portfolio.pnl)
        plt.show()

    def simulation_results(self, graph=False):
        # TODO: add compute
        if graph:
            self.graph_simulation_results()
