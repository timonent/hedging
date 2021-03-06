import concurrent.futures
import itertools as it
import threading
import click
from hedger import Hedger
from options_data import OptionsData

#-------------------------------------------------------------------------

@click.command(no_args_is_help=True)
@click.option("--portfolio-size", "-p", multiple=True, type=click.IntRange(min=1, max=5),
              help="Size of the portfolio to be hedged.")
@click.option("--schedule", "-s", multiple=True, type=click.IntRange(min=1, max=10),
              help="Hedging schedule to consider (in days).")
@click.option("--hedge-type", "-h", multiple=True, type=click.Choice(["delta", "delta-vega"], case_sensitive=True))
def execute_cmdline(portfolio_size, schedule, hedge_type):
    """Evaluate delta and delta-vega hedging performance on portfolios of
       at-the-money call options on S&P 100 during the trading year of 2010."""

    portfolio_size = sorted(set(portfolio_size))
    schedule = sorted(set(schedule))
    hedge_type = sorted(x.replace("-", "_") for x in set(hedge_type))

    data = OptionsData()
    sheets = data.get_sheet_names()

    task_params = it.product(hedge_type, sheets, portfolio_size, schedule)
    results = []

    print("Performing hedging in parallel...")
    with concurrent.futures.ProcessPoolExecutor() as executor:
        stats_futures = [executor.submit(getattr(Hedger, f"{hedge_type}_hedge"), data, *params) for hedge_type, *params in task_params]
        for stats in concurrent.futures.as_completed(stats_futures):
            results.append(stats.result())

    for result in results:
        print(result)

#-------------------------------------------------------------------------

if __name__ == "__main__":
    execute_cmdline()
    
#-------------------------------------------------------------------------
