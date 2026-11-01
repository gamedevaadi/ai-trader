# Alpha Arena — Three Risk-Aware Strategies

## Agent and evaluation scope

The submission contains exactly three strategy candidates. `decide` selects
**Strategy 1**, which equally weights all stocks at 50% gross exposure when
the broad market is above its 200-day average and has positive 126-day
momentum, and 30% otherwise.

All local comparisons use exactly `TRAIN_WINDOW = (0, 2519)` (2,520 days).
`train()` rejects other lengths or endpoints. No rows, stocks, or dates are
removed from the official `data/train.csv`. Decisions use only the engine's
trailing history, which is limited to 252 days.

The final 20% of this permitted window (days 2016–2519) is used to order the
three candidates by return, subject to zero errors, at least 30% average
exposure, and no worse than 15% maximum drawdown on that slice. It remains
part of the training data, so it is **not** an independent secret-period test
and does not prove generalization.

## Results

Full-window results include the engine's warm-up and use the local
transaction cost of 0.003. The same three candidates are shown in the graph;
the equal-weight benchmark is included as a comparison.

| Candidate | Full return | Ending value | Sharpe | Calmar | Max drawdown | Accuracy | Costs | Avg. exposure | Selection-slice return |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Strategy 1: higher-exposure confirmed trend** | **289.18%** | **₹389,177** | **1.50** | **0.99** | **-14.98%** | **51.39%** | **3.57%** | **46.52%** | **21.90%** |
| Strategy 2: confirmed market trend | 250.97% | ₹350,972 | 1.53 | 1.01 | -13.48% | 51.39% | 2.70% | 42.39% | 19.83% |
| Strategy 3: trend-gated inverse volatility | 244.65% | ₹344,650 | 1.55 | 1.00 | -13.50% | 51.39% | 6.39% | 42.39% | 19.29% |
| Equal-weight benchmark | 1901.36% | ₹2,001,365 | 1.62 | 1.32 | -27.15% | 51.39% | 0.30% | 100.00% | 51.43% |

These are historical, in-sample comparisons—not predictions. Strategy 1 has
the highest candidate return but its full-window drawdown (-14.98%) is close
to the 15% threshold and its Calmar (0.99) is just below 1. Strategy 2 is the
more conservative candidate. None of the three beats the equal-weight
benchmark or reaches 52% trading accuracy. Secret-period performance remains
unknown.

### Strategy rules

All three candidates are long-only and keep gross exposure between 30% and 50%.

1. **Higher-exposure confirmed trend (selected):** equal-weight all stocks at
   50% when the compounded broad-market index is above its 200-day average and
   has positive 126-day momentum; otherwise allocate 30%.
2. **Confirmed market trend:** the same market signal, with 45% exposure when
   confirmed and 30% otherwise.
3. **Trend-gated inverse volatility:** use the same 45%/30% market-regime
   exposure as Strategy 2, sized inversely to each stock's trailing 63-day
   close-to-close volatility.

The broad-market index compounds the mean daily return across stocks in the
available history. The agent does not use day-number shortcuts, future prices,
external files, or network access inside `strategy.py`.

## Fees, data, and rules

The local simulator charges `0.003` (0.3%) per unit of portfolio weight
traded, reflecting the latest fee update supplied for this task. The kit's
starter README mentions 0.1%; use the organizer's current scoring engine and
fee rule for final evaluation. Do not submit a locally modified `engine.py`.

The supplied dataset contains 3,708 days for 12 stocks. The agent and local
comparison explicitly use days 0–2519 only. The equal-weight benchmark's
1901.36% return reflects the source prices; altering the data to make results
look more typical would make the comparison misleading. The official rule
PDFs and dataset are preserved.

## Run and inspect

From the project directory:

```powershell
python compare.py
python visualization.py
```

`compare.py` reports the three candidates and benchmark, writes
`strategy_results.csv`, and ranks the candidates using the final 20% selection
slice. `visualization.py` writes `portfolio_growth.png` with exactly three
candidate curves plus the equal-weight benchmark. It uses a logarithmic
portfolio-value axis to keep each candidate readable next to the much larger
benchmark. `strategy.py` contains exactly three candidate rules and sets
`decide = decide_strategy_1`.

The engine begins backtests on day 50 for signal warm-up; returns are measured
through day 2519. All three candidates completed the local backtest with zero
errors and their average exposures are at least 30%.

## Competition checklist

- The training window is exactly 2,520 days; `train()` rejects another length
  or endpoint.
- `decide()` uses only the supplied trailing history and does not access the
  full dataset.
- Weights are finite, long-only, and at most 50% gross, below the engine's
  100% maximum.
- Every candidate maintains at least 30% gross exposure.
- `strategy.py` uses NumPy and the Python standard library only; it has no
  network or data-file access.
- Results are labeled in-sample; secret-period generalization is unknown.

## Deliverables

1. `strategy.py` — exactly three candidates; `decide` selects Strategy 1.
2. `strategy_results.csv` — metrics for those candidates and the benchmark.
3. `portfolio_growth.png` — three strategy curves plus benchmark.
4. `README.md` — approach, training window, features, assumptions, and caveats.
5. `submission.pptx` — presentation of the final agent and measured results.
