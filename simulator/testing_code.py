from simulator import Simulator
import datetime
from test_model import DummyModel, DummyModel2

import sys
import os
cwd = os.getcwd()
sys.path.insert(0, f"{os.path.join(cwd, 'database_extractor')}")

# Create simulator object
sim = Simulator()

# Set the amount you want your account to start with
sim.set_starting_capital(1e6)

# Set broker
sim.set_broker('IB')

# Set the percentage of cash you want to hold when distributing funds
sim.set_minimum_cash_percentage(0.03)

# OPTIONAL - Automatically 0.05 (5%)
# This sets a limit on how large a position can be with respect to the portfolio
# sim.set_maximum_single_percent_allocation(0.05)
sim.set_maximum_single_percent_allocation(.5)

# OPTIONAL
# Set start and end date
# Must be done before screening
start = datetime.date(2022, 1, 1)
end = datetime.date(2022, 8, 20)
sim.set_start_date(start_date=start)
sim.set_end_date(end_date=end)


# -------------------------------------------------------------------
m1_universe = ['SPY']
m2_universe = ['GLD']

sim.add_model(
    model_name='DummyModel',
    model=DummyModel,
    security_type="equity",
    security_universe=m1_universe,
    allocation_percentage=1
)
# sim.add_model(
#     model_name='DummyModel2',
#     model=DummyModel2,
#     security_type="equity",
#     security_universe=m2_universe,
#     allocation_percentage=0.5
# )
sim.run()
sim.simulation_results(graph=True)

