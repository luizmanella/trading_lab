class TradeManager:
    """
        This class is the object representation of a trade manager.
        It handles the physical trading and decisions regarding
        physical trading but does NOT deal with risk management. It
        will eventually interact with the microstructures module.

        Functionalities:
        - open positions
        - store information about opening/closing positions
        - makes decision about IF opening and closing should happen
    """
    def __init__(self):
        # positions_to_close have structure
        # {'security_type': {'model_name': list(tickers), ...}
        self.positions_to_close = dict()
        # positions_to_open have structure
        # {'security_type': {'model_name': {'ticker':{__information__}, ...}
        self.positions_to_open = dict()


    # --------------------------------------------
    #               GET METHODS
    # --------------------------------------------
    def get_positions_to_close(self):
        return self.positions_to_close

    def get_positions_to_open(self):
        return self.positions_to_open

    # --------------------------------------------
    #               SET METHODS
    # --------------------------------------------
    def set_base_structure_positions_to_close(self, structure):
        self.positions_to_close = structure

    def set_base_structure_positions_to_open(self, structure):
        self.positions_to_open = structure


    # --------------------------------------------
    #               UPDATE METHODS
    # --------------------------------------------

    # --------------------------------------------
    #               OTHER METHODS
    # ----------------------
    # ----------------------


    def add_new_position_to_close(self, security_type, model, ticker):
        self.positions_to_close[security_type][model].append(ticker)

    def add_new_position_to_open(self, security_type, model, ticker, ticker_info):
        self.positions_to_open[security_type][model][ticker] = ticker_info

    def close_all_positions(self, close_position):
        """
            This method closes all positions that are to be close.
            It is a bit sophisticated in the sense that it uses some what
            of a pointer through the parameter

            Arguments:
            ----------
                close_position - pointer (to parent_portfolio)
        """
        for security_type in self.positions_to_close:
            for model in self.positions_to_close[security_type]:
                if len(self.positions_to_close[security_type][model]) != 0:
                    for security in self.positions_to_close[security_type][model]:
                        close_position(security_type, model, security)
                    # make list empty since all positions were closed
                    self.positions_to_close[security_type][model] = list()

    def open_all_positions(self, open_position):
        """
            This method opens all positions that are to be opened.
            It is a bit sophisticated in the sense that it uses somewhat
            of a pointer through the parameter

            Arguments:
            ----------
                open_position - pointer (to parent_portfolio)
        """
        for security_type in self.positions_to_open:
            for model in self.positions_to_open[security_type]:
                _number_of_securities = len(self.positions_to_open[security_type][model])

                # Only runs opening if there are positions to close
                if _number_of_securities != 0:
                    _allocation_percentage = int((1/_number_of_securities)*100)/100

                    for security in self.positions_to_open[security_type][model]:
                        _security_info = dict()
                        # Grab information about the new position
                        _security_info['position_type'] = self.positions_to_open[security_type][model][security]
                        # Sets the allocation_percentage
                        _security_info['allocation_percentage'] = _allocation_percentage
                        # Runs the open_position method from ParentPortfolio
                        open_position(security_type, model, security, _security_info)
                    # make list empty since all positions were opened
                    self.positions_to_open[security_type][model] = dict()