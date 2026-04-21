-- 1. Drop and recreate with correct column names
DROP TABLE IF EXISTS bank_marketing;

CREATE TABLE bank_marketing (
    age             INTEGER,
    job             TEXT,
    marital         TEXT,
    education       TEXT,
    "default"       TEXT,
    housing         TEXT,
    loan            TEXT,
    contact         TEXT,
    month           TEXT,
    day_of_week     TEXT,
    duration        INTEGER,
    campaign        INTEGER,
    pdays           INTEGER,
    previous        INTEGER,
    poutcome        TEXT,
    "emp.var.rate"  REAL,
    "cons.price.idx" REAL,
    "cons.conf.idx"  REAL,
    euribor3m       REAL,
    "nr.employed"   REAL,
    y               TEXT
);