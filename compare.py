"""Compare three fixed candidates on the allowed training window."""
from pathlib import Path

import pandas as pd

import engine
import strategy

HERE = Path(__file__).resolve().parent
VALIDATION_FRACTION = 0.20
MAX_VALIDATION_DRAWDOWN = 15.0
MIN_VALIDATION_EXPOSURE = 30.0
BENCHMARK = "Equal-weight benchmark"
DECISIONS = (
    ("Strategy 1: higher-exposure confirmed trend", strategy.decide_strategy_1),
    ("Strategy 2: confirmed market trend", strategy.decide_strategy_2),
    ("Strategy 3: trend-gated inverse volatility", strategy.decide_strategy_3),
    (BENCHMARK, engine.equal_weight),
)


def evaluate_training_window():
    start, end = strategy.TRAIN_WINDOW
    prices = pd.read_csv(HERE / "data" / "train.csv")
    prices = prices.loc[prices["day"].between(start, end)]
    data = {
        field: prices.pivot(
            index="day",
            columns="stock",
            values=field,
        ).sort_index()
        for field in engine.FIELDS
    }
    window = engine.train_agent(strategy, data, window=strategy.TRAIN_WINDOW)
    validation_start = start + int(
        (end - start + 1) * (1.0 - VALIDATION_FRACTION)
    )

    backtests = {}
    rows = {}
    for label, decision in DECISIONS:
        result = engine.backtest(
            decision,
            data,
            start_day=50,
            verbose=False,
        )
        backtests[label] = result
        full = result["metrics"]
        validation_log = result["log"].loc[
            result["log"].index >= validation_start
        ]
        if validation_log.empty:
            raise ValueError("The chronological validation slice is empty.")
        validation = engine.metrics(validation_log)
        rows[label] = {
            "top_3": False,
            "total_return_%": full["total_return_%"],
            "ending_value_Rs": engine.STARTING_CAPITAL
            * (1 + full["total_return_%"] / 100),
            "sharpe": full["sharpe"],
            "calmar": full["calmar"],
            "max_drawdown_%": full["max_drawdown_%"],
            "trading_accuracy_%": full["trading_accuracy_%"],
            "costs_paid_%": full["costs_paid_%"],
            "avg_exposure_%": full["avg_exposure_%"],
            "validation_return_%": validation["total_return_%"],
            "validation_sharpe": validation["sharpe"],
            "validation_calmar": validation["calmar"],
            "validation_max_drawdown_%": validation["max_drawdown_%"],
            "validation_accuracy_%": validation["trading_accuracy_%"],
            "validation_costs_paid_%": validation["costs_paid_%"],
            "validation_avg_exposure_%": validation["avg_exposure_%"],
            "backtest_errors": result["errors"],
        }

    table = pd.DataFrame.from_dict(rows, orient="index")
    candidates = table.drop(index=BENCHMARK)
    eligible = candidates.loc[
        (candidates["backtest_errors"] == 0)
        & (
            candidates["validation_max_drawdown_%"]
            >= -MAX_VALIDATION_DRAWDOWN
        )
        & (
            candidates["validation_avg_exposure_%"]
            >= MIN_VALIDATION_EXPOSURE
        )
    ]
    if len(eligible) < 3:
        raise RuntimeError(
            "Fewer than three strategies met the validation reliability, "
            "drawdown, and exposure requirements."
        )
    top_three = eligible.sort_values(
        "validation_return_%", ascending=False
    ).head(3).index.tolist()
    table.loc[top_three, "top_3"] = True
    return {
        "data": data,
        "window": window,
        "validation_start": validation_start,
        "backtests": backtests,
        "table": table,
        "top_three": top_three,
    }


def compare_training_window():
    evaluation = evaluate_training_window()
    table = evaluation["table"]
    start, end = evaluation["window"]
    print(
        f"\nTraining window: days {start}-{end}; chronological selection "
        f"slice: days {evaluation['validation_start']}-{end}; "
        f"simulator transaction cost: {engine.COST_PER_TRADE:.3%} "
        "per traded weight.\n"
    )
    print(table.round(2).to_string())
    print("\nTop three candidates (validation return, subject to risk/exposure gates):")
    for rank, label in enumerate(evaluation["top_three"], start=1):
        print(f"{rank}. {label}")

    output = HERE / "strategy_results.csv"
    table.round(3).to_csv(output)
    print(f"\nSaved {output}")
    return evaluation


if __name__ == "__main__":
    compare_training_window()
