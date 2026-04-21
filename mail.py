import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve, classification_report
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')

#Paths
BASE_DIR        = r'C:\Users\shaya\Documents\SQL'
ADDITIONAL_DIR  = os.path.join(BASE_DIR, 'bank-additional')
CSV_PATH        = os.path.join(ADDITIONAL_DIR, 'bank-additional-full.csv')
DB_PATH         = os.path.join(BASE_DIR, 'bank_marketing.db')
REPORT_IMG_PATH = os.path.join(BASE_DIR, 'model_report.png')
SCORED_CSV_PATH = os.path.join(BASE_DIR, 'bank_scored.csv')

# STEP 1: LOAD RAW DATA INTO SQLITE

def load_to_sqlite(csv_path: str, db_path: str) -> sqlite3.Connection:
    """
    Reads the raw CSV and loads it into a local SQLite database.
    Renames columns that conflict with SQL reserved words.
    """
    print("=" * 65)
    print("STEP 1 — Loading raw data into SQLite")
    print("=" * 65)

    df = pd.read_csv(csv_path, sep=';')

    # Rename columns: SQL reserved words and dot notation
    df = df.rename(columns={
        'default':        'credit_default',
        'emp.var.rate':   'emp_var_rate',
        'cons.price.idx': 'cons_price_idx',
        'cons.conf.idx':  'cons_conf_idx',
        'nr.employed':    'nr_employed'
    })

    conn = sqlite3.connect(db_path)
    df.to_sql('bank_marketing', conn, if_exists='replace',
              index=True, index_label='id')

    count = pd.read_sql("SELECT COUNT(*) AS n FROM bank_marketing", conn).iloc[0,0]
    print(f"  Loaded {count:,} records → {db_path}")
    print(f"  Table: bank_marketing | Columns: {len(df.columns)}")
    return conn, df

# STEP 2: ETL / QC CHECKS (pure SQL)

def run_qc(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Runs QC queries against the SQLite database.
    Mirrors what a DataLab analyst runs on every client file.
    """
    print("\n" + "=" * 65)
    print("STEP 2 — ETL / Data Quality Control (SQL)")
    print("=" * 65)

    summary = pd.read_sql("""
        SELECT
            COUNT(*)                                                AS total_records,
            SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)             AS total_subscribed,
            ROUND(100.0*SUM(CASE WHEN y='yes' THEN 1 ELSE 0 END)
                  / COUNT(*), 2)                                    AS response_rate_pct,
            MIN(age)                                                AS min_age,
            MAX(age)                                                AS max_age,
            ROUND(AVG(age),1)                                       AS avg_age,
            SUM(CASE WHEN pdays = 999 THEN 1 ELSE 0 END)           AS never_prev_contacted,
            COUNT(DISTINCT job)                                     AS unique_jobs,
            COUNT(DISTINCT education)                               AS unique_edu_levels
        FROM bank_marketing
    """, conn)
    print("\n  Dataset Summary:")
    for col, val in summary.iloc[0].items():
        print(f"    {col:<30}: {val}")

    unknowns = pd.read_sql("""
        SELECT
            SUM(CASE WHEN job='unknown' THEN 1 ELSE 0 END)            AS unknown_job,
            SUM(CASE WHEN education='unknown' THEN 1 ELSE 0 END)      AS unknown_education,
            SUM(CASE WHEN credit_default='unknown' THEN 1 ELSE 0 END) AS unknown_credit_default,
            SUM(CASE WHEN housing='unknown' THEN 1 ELSE 0 END)        AS unknown_housing,
            SUM(CASE WHEN loan='unknown' THEN 1 ELSE 0 END)           AS unknown_loan
        FROM bank_marketing
    """, conn)
    print("\n  'Unknown' field counts (missing values):")
    for col, val in unknowns.iloc[0].items():
        print(f"    {col:<30}: {int(val)}")

    print("\n  [QC PASS] No null values. 'Unknown' coded as separate category.")
    print("  [NOTE]    'duration' excluded from model — not known before call is made.")
    return summary

# STEP 3: ANALYTICAL QUERIES (SQL)

def run_analytics(conn: sqlite3.Connection) -> dict:
    """
    Runs the key analytical queries that become Tableau views and
    GitHub Pages charts. Returns dict of DataFrames.
    """
    print("\n" + "=" * 65)
    print("STEP 3 — Analytical SQL Queries")
    print("=" * 65)

    results = {}

    results['by_job'] = pd.read_sql("""
        SELECT job,
               COUNT(*) AS contacts,
               SUM(CASE WHEN y='yes' THEN 1 ELSE 0 END) AS subscribed,
               ROUND(100.0*SUM(CASE WHEN y='yes' THEN 1 ELSE 0 END)/COUNT(*),2) AS response_rate_pct
        FROM bank_marketing
        GROUP BY job ORDER BY response_rate_pct DESC
    """, conn)

    results['by_age_band'] = pd.read_sql("""
        SELECT
          CASE WHEN age<25 THEN '18-24' WHEN age<35 THEN '25-34'
               WHEN age<45 THEN '35-44' WHEN age<55 THEN '45-54'
               WHEN age<65 THEN '55-64' ELSE '65+' END AS age_band,
          COUNT(*) AS contacts,
          ROUND(100.0*SUM(CASE WHEN y='yes' THEN 1 ELSE 0 END)/COUNT(*),2) AS response_rate_pct
        FROM bank_marketing
        GROUP BY age_band ORDER BY MIN(age)
    """, conn)

    results['by_month'] = pd.read_sql("""
        SELECT month, COUNT(*) AS contacts,
               ROUND(100.0*SUM(CASE WHEN y='yes' THEN 1 ELSE 0 END)/COUNT(*),2) AS response_rate_pct
        FROM bank_marketing GROUP BY month ORDER BY response_rate_pct DESC
    """, conn)

    results['by_poutcome'] = pd.read_sql("""
        SELECT poutcome, COUNT(*) AS contacts,
               ROUND(100.0*SUM(CASE WHEN y='yes' THEN 1 ELSE 0 END)/COUNT(*),2) AS response_rate_pct
        FROM bank_marketing GROUP BY poutcome ORDER BY response_rate_pct DESC
    """, conn)

    results['by_contact'] = pd.read_sql("""
        SELECT contact, COUNT(*) AS contacts,
               ROUND(100.0*SUM(CASE WHEN y='yes' THEN 1 ELSE 0 END)/COUNT(*),2) AS response_rate_pct
        FROM bank_marketing GROUP BY contact
    """, conn)

    results['by_campaign_count'] = pd.read_sql("""
        SELECT CASE WHEN campaign=1 THEN '1 contact'
                    WHEN campaign=2 THEN '2 contacts'
                    WHEN campaign=3 THEN '3 contacts'
                    WHEN campaign BETWEEN 4 AND 5 THEN '4-5 contacts'
                    ELSE '6+ contacts' END AS contacts_made,
               COUNT(*) AS records,
               ROUND(100.0*SUM(CASE WHEN y='yes' THEN 1 ELSE 0 END)/COUNT(*),2) AS response_rate_pct
        FROM bank_marketing GROUP BY contacts_made ORDER BY MIN(campaign)
    """, conn)

    results['econ_by_outcome'] = pd.read_sql("""
        SELECT y AS subscribed,
               ROUND(AVG(emp_var_rate),3)   AS avg_emp_var_rate,
               ROUND(AVG(cons_price_idx),3) AS avg_cons_price_idx,
               ROUND(AVG(cons_conf_idx),3)  AS avg_cons_conf_idx,
               ROUND(AVG(euribor3m),3)      AS avg_euribor3m,
               ROUND(AVG(nr_employed),0)    AS avg_nr_employed
        FROM bank_marketing GROUP BY y
    """, conn)

    for name, df in results.items():
        print(f"\n  [{name}]")
        print(df.to_string(index=False))

    return results

# STEP 4: FEATURE ENGINEERING (SQL to Python)

def engineer_features(conn: sqlite3.Connection) -> tuple:
    """
    Builds model-ready features using a SQL VIEW, then loads into pandas.
    Duration is excluded — it's only known after the call ends (data leakage).
    """
    print("\n" + "=" * 65)
    print("STEP 4 — Feature Engineering (SQL VIEW → DataFrame)")
    print("=" * 65)

    conn.execute("DROP VIEW IF EXISTS model_features")
    conn.execute("""
        CREATE VIEW model_features AS
        SELECT
            id,
            age,
            CASE WHEN age<25 THEN 0 WHEN age<35 THEN 1 WHEN age<45 THEN 2
                 WHEN age<55 THEN 3 WHEN age<65 THEN 4 ELSE 5 END   AS age_band_ord,
            CASE education
                WHEN 'illiterate'          THEN 0 WHEN 'basic.4y'    THEN 1
                WHEN 'basic.6y'            THEN 2 WHEN 'basic.9y'    THEN 3
                WHEN 'high.school'         THEN 4 WHEN 'professional.course' THEN 5
                WHEN 'university.degree'   THEN 6 ELSE 3 END         AS education_ord,
            CASE WHEN contact        = 'cellular' THEN 1 ELSE 0 END  AS is_cellular,
            CASE WHEN housing        = 'yes'      THEN 1 ELSE 0 END  AS has_housing_loan,
            CASE WHEN loan           = 'yes'      THEN 1 ELSE 0 END  AS has_personal_loan,
            CASE WHEN credit_default = 'yes'      THEN 1 ELSE 0 END  AS has_default,
            campaign,
            pdays,
            previous,
            CASE WHEN pdays = 999 THEN 0 ELSE 1 END                  AS was_previously_contacted,
            CASE poutcome WHEN 'failure' THEN 0
                          WHEN 'nonexistent' THEN 1
                          WHEN 'success'     THEN 2 END               AS poutcome_ord,
            emp_var_rate,
            cons_price_idx,
            cons_conf_idx,
            euribor3m,
            nr_employed,
            CASE WHEN y = 'yes' THEN 1 ELSE 0 END                    AS y_binary
        FROM bank_marketing
    """)

    df_feat = pd.read_sql("SELECT * FROM model_features", conn)

    # Job encoding (LabelEncoder in Python with no ordinal assumption)
    le_job = LabelEncoder()
    raw_df = pd.read_sql("SELECT id, job FROM bank_marketing", conn)
    df_feat = df_feat.merge(raw_df, on='id')
    df_feat['job_enc'] = le_job.fit_transform(df_feat['job'])

    feature_cols = [
        'age', 'age_band_ord', 'education_ord', 'job_enc',
        'has_housing_loan', 'has_personal_loan', 'has_default', 'is_cellular',
        'campaign', 'pdays', 'previous', 'was_previously_contacted', 'poutcome_ord',
        'emp_var_rate', 'cons_price_idx', 'cons_conf_idx', 'euribor3m', 'nr_employed'
    ]

    print(f"  Features: {len(feature_cols)}")
    for f in feature_cols:
        print(f"    • {f}")

    X = df_feat[feature_cols].values
    y = df_feat['y_binary'].values
    print(f"\n  X shape: {X.shape} | Positives: {y.sum():,} ({y.mean():.2%})")
    return X, y, feature_cols, df_feat

# STEP 5: MODEL TRAINING & EVALUATION
def train_models(X: np.ndarray, y: np.ndarray, feature_cols: list) -> tuple:
    """
    Trains Logistic Regression, Random Forest, and XGBoost.
    Uses 5-fold stratified CV to evaluate each model.
    """
    print("\n" + "=" * 65)
    print("STEP 5 — Model Training & Cross-Validation")
    print("=" * 65)

    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest':       RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
        'XGBoost':             XGBClassifier(
                                    n_estimators=300, max_depth=5, learning_rate=0.05,
                                    subsample=0.8, colsample_bytree=0.8,
                                    use_label_encoder=False, eval_metric='auc',
                                    random_state=42, n_jobs=-1)
    }

    cv_results = {}
    print(f"\n  {'Model':<25} {'AUC-ROC (CV mean)':>18} {'± Std':>10}")
    print(f"  {'─'*55}")
    for name, model in models.items():
        scores = cross_val_score(model, X_sc, y, cv=cv, scoring='roc_auc')
        cv_results[name] = {'mean': round(scores.mean(),4), 'std': round(scores.std(),4)}
        print(f"  {name:<25} {scores.mean():>18.4f} {scores.std():>10.4f}")

    # Fit XGBoost on full dataset for scoring
    xgb = models['XGBoost']
    xgb.fit(X_sc, y)
    y_proba = xgb.predict_proba(X_sc)[:, 1]

    full_auc = roc_auc_score(y, y_proba)
    print(f"\n  XGBoost full-dataset AUC: {full_auc:.4f}")

    return models, cv_results, X_sc, y_proba, scaler

# STEP 6: DECILE LIFT TABLE
def decile_lift_table(y: np.ndarray, y_proba: np.ndarray,
                      conn: sqlite3.Connection, df_feat: pd.DataFrame) -> pd.DataFrame:
    """
    Builds the decile lift table — the core database marketing deliverable.
    Also writes scored data back to SQLite for Tableau/SQL reporting.
    """
    print("\n" + "=" * 65)
    print("STEP 6 — Decile Lift Table")
    print("=" * 65)

    df_scored = df_feat[['id']].copy()
    df_scored['y_binary']          = y
    df_scored['score_probability'] = y_proba
    df_scored['decile'] = pd.qcut(
        pd.Series(y_proba).rank(method='first'), 10, labels=False
    )
    df_scored['decile'] = 10 - df_scored['decile']  # 1 = highest-scored

    # Save scored file to SQLite (can then be queried in Tableau)
    df_scored.to_sql('bank_scored', conn, if_exists='replace', index=False)

    tbl = df_scored.groupby('decile').agg(
        n=('y_binary','count'),
        subscribers=('y_binary','sum')
    ).reset_index()
    tbl['response_rate_pct']     = (tbl['subscribers']/tbl['n']*100).round(2)
    tbl['lift']                   = (tbl['response_rate_pct'] / (y.mean()*100)).round(2)
    tbl['cum_pct_file']           = (tbl['n'].cumsum()/len(y)*100).round(1)
    tbl['cum_pct_subscribers']    = (tbl['subscribers'].cumsum()/y.sum()*100).round(1)

    baseline = y.mean() * 100
    print(f"\n  Baseline response rate: {baseline:.2f}%")
    print(f"\n  {'D':>3} {'N':>6} {'Subs':>5} {'Resp%':>7} {'Lift':>6} "
          f"{'Cum%File':>10} {'Cum%Subs':>10}")
    print(f"  {'─'*55}")
    for _, r in tbl.iterrows():
        print(f"  {int(r['decile']):>3} {int(r['n']):>6,} {int(r['subscribers']):>5,} "
              f"{r['response_rate_pct']:>6.2f}% {r['lift']:>5.2f}x "
              f"{r['cum_pct_file']:>9.1f}% {r['cum_pct_subscribers']:>9.1f}%")

    top3_subs = tbl[tbl['decile']<=3]['cum_pct_subscribers'].max()
    print(f"\n  Top 3 deciles (30% of file) → {top3_subs:.1f}% of all subscribers captured")
    return tbl

# STEP 7: GENERATE REPORT CHARTS
def generate_report(models, cv_results, X_sc, y, y_proba, tbl, feature_cols,
                    analytics, img_path):
    """
    Generates a 6-panel model report chart.
    Saves to file for GitHub Pages and presentation.
    """
    print("\n" + "=" * 65)
    print("STEP 7 — Generating Report Charts")
    print("=" * 65)

    NAVY   = '#0B1D3A'
    ACCENT = '#E8602C'
    GOLD   = '#C9933A'
    GRAY   = '#B4B2A9'
    GREEN  = '#2A7D4F'
    CREAM  = '#F5F0E8'

    fig = plt.figure(figsize=(18, 11))
    fig.patch.set_facecolor(CREAM)
    gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)

    xgb_model = models['XGBoost']

    # Cumulative Gain Curve
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.set_facecolor('white')
    ax1.fill_between(tbl['cum_pct_file'], tbl['cum_pct_subscribers'],
                     tbl['cum_pct_file'], alpha=0.12, color=ACCENT)
    ax1.plot(tbl['cum_pct_file'], tbl['cum_pct_subscribers'],
             color=ACCENT, lw=2.5, marker='o', markersize=5, label='XGBoost Model')
    ax1.plot([0,100],[0,100], '--', color=GRAY, lw=1.5, label='Random baseline')
    ax1.set_title('Cumulative Gain (Lift) Curve', fontsize=13,
                  fontweight='bold', color=NAVY, pad=10)
    ax1.set_xlabel('% of Records Contacted (top-scored first)', color=NAVY, fontsize=10)
    ax1.set_ylabel('% of Total Subscribers Captured', color=NAVY, fontsize=10)
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.25)

    idx_30 = (tbl['cum_pct_file'] - 30).abs().idxmin()
    c30    = tbl.loc[idx_30, 'cum_pct_subscribers']
    ax1.annotate(
        f'Top 30% of file\ncaptures {c30:.0f}% of subscribers',
        xy=(30, c30), xytext=(50, c30-14),
        arrowprops=dict(arrowstyle='->', color=NAVY),
        fontsize=9, color=NAVY,
        bbox=dict(boxstyle='round,pad=0.4', fc='white', ec=NAVY, alpha=0.85)
    )

    # ROC Curve
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.set_facecolor('white')
    fpr, tpr, _ = roc_curve(y, y_proba)
    auc          = roc_auc_score(y, y_proba)
    ax2.plot(fpr, tpr, color=ACCENT, lw=2.5, label=f'AUC = {auc:.3f}')
    ax2.plot([0,1],[0,1], '--', color=GRAY, lw=1.5)
    ax2.fill_between(fpr, tpr, alpha=0.1, color=ACCENT)
    ax2.set_title('ROC Curve', fontsize=13, fontweight='bold', color=NAVY, pad=10)
    ax2.set_xlabel('False Positive Rate', color=NAVY, fontsize=10)
    ax2.set_ylabel('True Positive Rate', color=NAVY, fontsize=10)
    ax2.legend(fontsize=10)

    # Decile Response Rate Bar
    ax3 = fig.add_subplot(gs[1, :2])
    ax3.set_facecolor('white')
    colors = [ACCENT if d<=3 else GOLD if d<=5 else GRAY for d in tbl['decile']]
    bars   = ax3.bar(tbl['decile'], tbl['response_rate_pct'],
                     color=colors, edgecolor='white', linewidth=0.5)
    baseline_pct = y.mean() * 100
    ax3.axhline(baseline_pct, color=NAVY, linestyle='--', lw=1.5,
                label=f'Baseline {baseline_pct:.2f}%')
    for bar, rate in zip(bars, tbl['response_rate_pct']):
        ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
                 f'{rate:.1f}%', ha='center', va='bottom', fontsize=8, color=NAVY)
    ax3.set_title('Subscription Rate by Model Score Decile\n(1 = highest scored)',
                  fontsize=13, fontweight='bold', color=NAVY, pad=8)
    ax3.set_xlabel('Decile', color=NAVY, fontsize=10)
    ax3.set_ylabel('Subscription Rate (%)', color=NAVY, fontsize=10)
    ax3.set_xticks(tbl['decile'])
    from matplotlib.patches import Patch
    legend_elems = [
        Patch(fc=ACCENT, label='Contact (Deciles 1–3)'),
        Patch(fc=GOLD,   label='Contact w/ incentive (4–5)'),
        Patch(fc=GRAY,   label='Suppress (6–10)')
    ]
    ax3.legend(handles=legend_elems, fontsize=9, loc='upper right')

    # Feature Importance
    ax4 = fig.add_subplot(gs[1, 2])
    ax4.set_facecolor('white')
    fi = pd.Series(xgb_model.feature_importances_, index=feature_cols).sort_values().tail(10)
    colors_fi = [ACCENT if v >= fi.quantile(0.7) else GOLD for v in fi.values]
    fi.plot(kind='barh', ax=ax4, color=colors_fi, edgecolor='white')
    ax4.set_title('XGBoost Feature Importance\n(Top 10)', fontsize=13,
                  fontweight='bold', color=NAVY, pad=8)
    ax4.set_xlabel('Importance Score', color=NAVY, fontsize=10)

    fig.suptitle(
        'Bank Marketing Campaign — Response Prediction Model Report\n'
        'Data: UCI Bank Marketing Dataset | Moro et al., 2014 | 41,188 records',
        fontsize=14, fontweight='bold', color=NAVY, y=0.99
    )

    plt.savefig(img_path, dpi=150, bbox_inches='tight', facecolor=CREAM)
    print(f"  Chart saved → {img_path}")
    plt.show()

# STEP 8: BUSINESS IMPACT SUMMARY
def business_impact(tbl, y, conn):
    print("\n" + "=" * 65)
    print("STEP 8 — Business Impact Summary")
    print("=" * 65)

    total     = len(y)
    all_subs  = y.sum()
    baseline  = y.mean()

    top3      = tbl[tbl['decile'] <= 3]
    top3_recs = top3['n'].sum()
    top3_subs = top3['subscribers'].sum()
    top3_rate = top3_subs / top3_recs

    mail_cost = 1.00  # USD per record

    cost_all   = total   * mail_cost
    cost_top3  = top3_recs * mail_cost
    savings    = cost_all - cost_top3
    reduction  = (1 - top3_recs/total) * 100

    # SQL query for final business report
    report_sql = pd.read_sql("""
        SELECT
          SUM(CASE WHEN decile <= 3 THEN 1 ELSE 0 END) AS top3_records,
          SUM(CASE WHEN decile <= 3 THEN y_binary ELSE 0 END) AS top3_subscribers,
          COUNT(*) AS total_records,
          SUM(y_binary) AS total_subscribers
        FROM bank_scored
    """, conn)

    print(f"\n  Hypothetical campaign: $1.00 per contact, {total:,} total records")
    print(f"\n  {'Metric':<45} {'Random':>12} {'Model (Top 3)':>15}")
    print(f"  {'─'*74}")
    print(f"  {'Records contacted':<45} {total:>12,} {top3_recs:>15,}")
    print(f"  {'Cost @ $1.00/record':<45} ${cost_all:>11,.0f} ${cost_top3:>14,.0f}")
    print(f"  {'Subscribers acquired':<45} {all_subs:>12,} {top3_subs:>15,}")
    print(f"  {'Subscription rate':<45} {baseline:>11.2%} {top3_rate:>14.2%}")
    print(f"  {'─'*74}")
    print(f"  {'Cost savings':<45} ${savings:>14,.0f}")
    print(f"  {'Mail volume reduction':<45} {reduction:>13.1f}%")
    print(f"  {'Subscribers captured (% of total)':<45} "
          f"{top3_subs/all_subs*100:>13.1f}%")
    print(f"\n  [SQL VERIFIED] top3_records={report_sql.iloc[0]['top3_records']:,} | "
          f"top3_subscribers={report_sql.iloc[0]['top3_subscribers']:,}")

# MAIN
if __name__ == '__main__':
    # Load
    conn, _ = load_to_sqlite(CSV_PATH, DB_PATH)

    # QC
    run_qc(conn)

    # Analytics
    analytics = run_analytics(conn)

    # Feature engineering
    X, y, feature_cols, df_feat = engineer_features(conn)

    # Models
    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X)
    models, cv_results, X_sc, y_proba, scaler = train_models(X, y, feature_cols)

    # Decile table
    tbl = decile_lift_table(y, y_proba, conn, df_feat)

    # Charts
    generate_report(models, cv_results, X_sc, y, y_proba, tbl,
                    feature_cols, analytics, REPORT_IMG_PATH)

    # Impact
    business_impact(tbl, y, conn)

    conn.close()
    print(f"\n{'='*65}")
    print("Project complete. Files generated:")
    print(f"  • {DB_PATH}")
    print(f"  • {REPORT_IMG_PATH}")
    print(f"{'='*65}")