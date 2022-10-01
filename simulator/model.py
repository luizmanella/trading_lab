from datetime import timedelta
from database_extractor import database_extractor

class Model:
    def __init__(self):
        self.start_date = None
        self.current_date = None
        self.security_universe = list()

    # --------------------------------------------
    #               GET METHODS
    # --------------------------------------------
    def get_start_date(self):
        return self.start_date

    def get_current_date(self):
        return self.current_date

    # --------------------------------------------
    #               SET METHODS
    # --------------------------------------------

    def set_start_date(self, start_date):
        """
            This method sets the start date.

            Arguments:
            ----------
                start_date - datetime
        """
        self.start_date = start_date

    def set_current_date(self, current_date):
        """
            This method sets the end date.

            Arguments:
            ----------
                end_date - datetime
        """
        self.current_date = current_date

    def set_security_universe(self, universe):
        self.security_universe = universe

    # --------------------------------------------
    #               OTHER METHODS
    # --------------------------------------------
    def pull_data(self, ticker, look_back=None, columns=None):
        """
            This method pulls data for a specific ticker. It
            will pull the currect active day, plus some additional
            look_back period as needed for the model used to
            make trades.
        """
        pass
