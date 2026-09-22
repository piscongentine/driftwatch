"""Turn Feast features into model input; build, save and load the model.

Reads : out/model.pkl (load).
Writes: out/model.pkl (save).
Train and drift-check both import this, so they always encode features the same way.
"""
import pickle
import sys
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # lets `import config` work when run as a script
import config  # noqa: E402


def build():
    """A plain logistic regression. Standardizing first keeps every sensor on the same scale; C=10 barely regularizes."""
    return make_pipeline(StandardScaler(), LogisticRegression(C=10, max_iter=1000))


def encode(df):
    """Sensors as numbers, plus one 0/1 column per machine mode. The mode list is fixed, so train and live agree."""
    x = df[config.NUMERIC].astype(float).copy()
    for m in config.MODES:
        x[f"mode_{m}"] = (df["mode"] == m).astype(float)
    return x


def predict(model, df):
    """Probability that each row is a machine about to fail."""
    return model.predict_proba(encode(df))[:, 1]


def save(model):
    config.MODEL.parent.mkdir(parents=True, exist_ok=True)
    with open(config.MODEL, "wb") as f:
        pickle.dump(model, f)


def load():
    with open(config.MODEL, "rb") as f:
        return pickle.load(f)  # our own file, written by train.py
