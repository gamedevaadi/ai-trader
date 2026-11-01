"""Plot the selected top three candidates against the equal-weight benchmark."""
from pathlib import Path

import matplotlib.pyplot as plt

import compare
import engine


def main():
    evaluation = compare.evaluate_training_window()
    start, end = evaluation["window"]
    backtests = evaluation["backtests"]
    top_three = evaluation["top_three"]
    benchmark = backtests[compare.BENCHMARK]["log"]["return"].loc[start:end]
    if benchmark.empty:
        raise ValueError("The selected training window has no benchmark returns.")

    days = benchmark.index.to_numpy()
    x = [days[0] - 1, *days.tolist()]
    benchmark_value = engine.STARTING_CAPITAL * (1 + benchmark).cumprod()

    fig, ax = plt.subplots(figsize=(12, 7))
    for label in top_three:
        returns = backtests[label]["log"]["return"].loc[start:end]
        if returns.empty or not returns.index.equals(benchmark.index):
            raise ValueError(f"{label} does not align with the benchmark days.")
        values = engine.STARTING_CAPITAL * (1 + returns).cumprod()
        ax.plot(
            x,
            [engine.STARTING_CAPITAL, *values.tolist()],
            label=label,
            linewidth=1.8,
        )

    ax.plot(
        x,
        [engine.STARTING_CAPITAL, *benchmark_value.tolist()],
        label=compare.BENCHMARK,
        linewidth=1.6,
        linestyle="--",
        alpha=0.85,
    )
    ax.axvline(
        evaluation["validation_start"],
        color="gray",
        linewidth=1,
        linestyle=":",
        label="Selection slice starts",
    )
    ax.set_title(
        f"Top three strategy candidates: days {start}-{end} (log scale)"
    )
    ax.set_xlabel("Day")
    ax.set_ylabel("Portfolio value (₹, log scale)")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda value, _: f"₹{value:,.0f}")
    )
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    output = Path(__file__).resolve().parent / "portfolio_growth.png"
    fig.savefig(output, dpi=160)
    plt.close(fig)
    print(f"Saved top-three portfolio growth graph: {output}")


if __name__ == "__main__":
    main()
