import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


plt.style.use('ggplot')

def random_price_walk(price, mu, std, days):
    """
    :description:
        This function performs the random walk.
    
    :arguments:
    :price: (float) stock's current price
    :mu: (float) mean of log-returns
    :std: (float) standard deviation of log-returns
    :days: (int) number of days to predict forward

    :returns: (list) price path from simulation
    """
    price_path = [price]
    for _ in range(days):
        probs = np.random.normal(loc=mu, scale=std)
        price_path.append(price_path[-1]*(1+probs))
    return price_path

def monte_carlo_sim(num_of_sims, price, mu, std, days, low_range, high_range):
    """
    :description:
        Monte Carlo simulation for price prediction assuming log-normal price behavior.
    
    :arguments:
    :num_of_sims: (int) number of simulations to run
    :price: (float) stock's current price
    :mu: (float) mean of log-returns
    :std: (float) standard deviation of log-returns
    :days: (int) number of days to predict forward
    :low_range: (int) low price range for stock
    :high_range: (int) high price range for stock
    """

    # Runs all simulations
    price_path = []
    for s in range(num_of_sims):
        np.random.seed(s)
        p = random_price_walk(price, mu, std, days)
        price_path.append(p)      
    
    # Vectorize to Matrix
    price_path = np.array(price_path)
    print(price_path.shape)

    # Compute daily probabilities
    prob_over_time = ((low_range <= price_path) & (price_path <= high_range)).sum(axis=0)/price_path.shape[0]
    
    print(f'Expected price in {days} days: {price_path[:,-1].mean()}')

    # Plotting results
    plt.plot(prob_over_time)
    plt.xticks(range(prob_over_time.shape[0]))
    plt.title(f'Daily probability of being in range ${low_range} - ${high_range}')
    plt.show()

def etl_data(ticker):
    """
    :description:
        Extracts, tranforms, and outputs the data
    
    :returns: (pd.DataFrame) contains closing price and log-returns
    """
    # Reading data
    df = pd.read_csv(f'./{ticker}.csv')

    # Update column names
    df.columns = list(map(lambda x: x.lower() , df.columns.to_list()))

    # Dropping all other values
    df = df[['close']]

    # Computing log returns
    df['diff'] = np.log(df['close'].shift(-1)/df['close'])

    # Dropping null values
    df.dropna(inplace=True)

    return df

# -----------------------------
# Grab data and compute stats
# -----------------------------
ticker = 'SPY'
df = etl_data(ticker)
mu = df['diff'].mean()
std = df['diff'].std()

# -----------------------------
# Variables for you to change
# -----------------------------
low = 368
high = 390
days = 3

# -----------------------------
# Run Monte Carlos Simulation
# -----------------------------
monte_carlo_sim(
    1000, 
    df['close'].iloc[-1], 
    mu=mu, 
    std=std, 
    days=days, 
    low_range=low, 
    high_range=high
)
