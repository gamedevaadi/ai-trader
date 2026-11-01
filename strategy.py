"""Three fixed candidates trained only on the first 10-year window."""
import numpy as np

TEAM_NAME = "Risk-Aware Strategy Candidates"
TRAIN_WINDOW = (0, 2519)
MIN_EXPOSURE = 0.30
MODEL = {}


def train(data):
    """Validate the selected window and record its stock universe."""
    close = data["close"]
    if close.empty:
        raise ValueError("Training data is empty.")
    if len(close) != 2520:
        raise ValueError(
            f"Expected exactly 2520 training days; got {len(close)}."
        )
    if (
        int(close.index[0]) != TRAIN_WINDOW[0]
        or int(close.index[-1]) != TRAIN_WINDOW[1]
    ):
        raise ValueError(
            f"Expected training days {TRAIN_WINDOW[0]}-{TRAIN_WINDOW[1]}, "
            f"got {close.index[0]}-{close.index[-1]}."
        )
    MODEL["stocks"] = tuple(close.columns)
    MODEL["training_days"] = len(close)


def _equal_weight(stocks, exposure):
    if not stocks:
        raise ValueError("Price history has no stocks.")
    weight = exposure / len(stocks)
    return {stock: weight for stock in stocks}


def _market_is_risk_on(close):
    if len(close) < 201:
        return False
    market_returns = close.pct_change().mean(axis=1).fillna(0.0)
    market_index = (1.0 + market_returns).cumprod()
    above_long_trend = market_index.iloc[-1] > market_index.iloc[-200:].mean()
    positive_medium_momentum = market_index.iloc[-1] > market_index.iloc[-127]
    return bool(above_long_trend and positive_medium_momentum)


def decide_strategy_1(history):
    """Equal-weight at 50% exposure in a confirmed uptrend, otherwise 30%."""
    close = history["close"]
    stocks = list(close.columns)
    exposure = 0.50 if _market_is_risk_on(close) else MIN_EXPOSURE
    return _equal_weight(stocks, exposure)


def decide_strategy_2(history):
    """Equal-weight at 45% exposure in a confirmed uptrend, otherwise 30%."""
    close = history["close"]
    stocks = list(close.columns)
    exposure = 0.45 if _market_is_risk_on(close) else MIN_EXPOSURE
    return _equal_weight(stocks, exposure)


def decide_strategy_3(history):
    """Inverse-volatility weights at 45% in an uptrend, otherwise 30%."""
    close = history["close"]
    stocks = list(close.columns)
    if not stocks:
        raise ValueError("Price history has no stocks.")

    exposure = 0.45 if _market_is_risk_on(close) else MIN_EXPOSURE
    if len(close) < 64:
        return _equal_weight(stocks, exposure)

    volatility = close.pct_change().tail(63).std().reindex(stocks)
    if not np.isfinite(volatility.to_numpy()).all() or (volatility <= 0).any():
        return _equal_weight(stocks, exposure)

    raw_weights = 1.0 / volatility
    raw_weights *= exposure / raw_weights.sum()
    return raw_weights.to_dict()


decide = decide_strategy_1


if __name__ == "__main__":
    raise SystemExit("Run python compare.py to evaluate the three candidates.")
