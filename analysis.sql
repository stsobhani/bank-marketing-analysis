--   sqlite3 "C:\Users\shaya\Documents\SQL\bank_marketing.db"
--   .read "C:/Users/shaya/Documents/SQL/bank_setup.sql"
--   .mode csv
--   .separator ";"
--   .import --skip 1 "C:/Users/shaya/Documents/SQL/bank-additional/bank-additional-full.csv" bank_marketing
--   .read "C:/Users/shaya/Documents/SQL/bank_analysis.sql"

-- Set output formatting
.headers on
.mode column
.width 25 10 12 12

-- Quality Control and Data Cleaning

SELECT '=== A1: RECORD COUNT (should be 41188) ===' AS query;
SELECT COUNT(*) AS total_records FROM bank_marketing;

SELECT '=== A2: VERIFY NO HEADER ROW IN DATA ===' AS query;
SELECT COUNT(*) AS bad_rows_if_zero FROM bank_marketing WHERE age = 'age';

SELECT '=== A3: DATASET SUMMARY ===' AS query;
SELECT
    COUNT(*)                                                        AS total_records,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)                     AS subscribed,
    SUM(CASE WHEN y = 'no'  THEN 1 ELSE 0 END)                     AS not_subscribed,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                            AS response_rate_pct,
    MIN(age)                                                        AS min_age,
    MAX(age)                                                        AS max_age,
    ROUND(AVG(age), 1)                                              AS avg_age,
    SUM(CASE WHEN pdays = 999 THEN 1 ELSE 0 END)                   AS never_prev_contacted
FROM bank_marketing;

SELECT '=== A4: UNKNOWN / MISSING VALUE COUNTS ===' AS query;
SELECT
    SUM(CASE WHEN job       = 'unknown' THEN 1 ELSE 0 END)          AS unknown_job,
    SUM(CASE WHEN education = 'unknown' THEN 1 ELSE 0 END)          AS unknown_education,
    SUM(CASE WHEN "default" = 'unknown' THEN 1 ELSE 0 END)          AS unknown_default,
    SUM(CASE WHEN housing   = 'unknown' THEN 1 ELSE 0 END)          AS unknown_housing,
    SUM(CASE WHEN loan      = 'unknown' THEN 1 ELSE 0 END)          AS unknown_loan,
    SUM(CASE WHEN contact   = 'unknown' THEN 1 ELSE 0 END)          AS unknown_contact
FROM bank_marketing;

-- Response rate by segment

SELECT '=== B1: RESPONSE RATE BY JOB ===' AS query;
SELECT
    job,
    COUNT(*)                                                         AS contacts,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)                      AS subscribed,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
GROUP BY job
ORDER BY response_rate_pct DESC;

SELECT '=== B2: RESPONSE RATE BY AGE BAND ===' AS query;
SELECT
    CASE
        WHEN age < 25 THEN '1_18-24'
        WHEN age < 35 THEN '2_25-34'
        WHEN age < 45 THEN '3_35-44'
        WHEN age < 55 THEN '4_45-54'
        WHEN age < 65 THEN '5_55-64'
        ELSE               '6_65+'
    END                                                              AS age_band,
    COUNT(*)                                                         AS contacts,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)                      AS subscribed,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
GROUP BY age_band
ORDER BY age_band;

SELECT '=== B3: RESPONSE RATE BY EDUCATION ===' AS query;
SELECT
    education,
    COUNT(*)                                                         AS contacts,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)                      AS subscribed,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
GROUP BY education
ORDER BY response_rate_pct DESC;

SELECT '=== B4: RESPONSE RATE BY MONTH (SEASONALITY) ===' AS query;
SELECT
    month,
    COUNT(*)                                                         AS contacts,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)                      AS subscribed,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
GROUP BY month
ORDER BY response_rate_pct DESC;

SELECT '=== B5: RESPONSE RATE BY CONTACT CHANNEL ===' AS query;
SELECT
    contact,
    COUNT(*)                                                         AS contacts,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)                      AS subscribed,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
GROUP BY contact;

SELECT '=== B6: EFFECT OF PRIOR CAMPAIGN OUTCOME ===' AS query;
SELECT
    poutcome,
    COUNT(*)                                                         AS contacts,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)                      AS subscribed,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
GROUP BY poutcome
ORDER BY response_rate_pct DESC;

SELECT '=== B7: DIMINISHING RETURNS — CONTACTS IN THIS CAMPAIGN ===' AS query;
SELECT
    CASE
        WHEN campaign = 1              THEN '1_one_contact'
        WHEN campaign = 2              THEN '2_two_contacts'
        WHEN campaign = 3              THEN '3_three_contacts'
        WHEN campaign BETWEEN 4 AND 5  THEN '4_four_to_five'
        ELSE                               '5_six_or_more'
    END                                                              AS contacts_made,
    COUNT(*)                                                         AS records,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)                      AS subscribed,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
GROUP BY contacts_made
ORDER BY contacts_made;

SELECT '=== B8: RESPONSE BY MARITAL STATUS ===' AS query;
SELECT
    marital,
    COUNT(*)                                                         AS contacts,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
GROUP BY marital
ORDER BY response_rate_pct DESC;

SELECT '=== B9: LOAN STATUS CROSS-TAB ===' AS query;
SELECT
    housing,
    loan,
    COUNT(*)                                                         AS contacts,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
WHERE housing != 'unknown' AND loan != 'unknown'
GROUP BY housing, loan
ORDER BY response_rate_pct DESC;

--Macroeconomic analysis

SELECT '=== C1: ECONOMIC INDICATORS BY SUBSCRIPTION OUTCOME ===' AS query;
SELECT
    y                                                                AS subscribed,
    ROUND(AVG("emp.var.rate"), 3)                                    AS avg_employment_var_rate,
    ROUND(AVG("cons.price.idx"), 3)                                  AS avg_consumer_price_idx,
    ROUND(AVG("cons.conf.idx"), 3)                                   AS avg_consumer_conf_idx,
    ROUND(AVG(euribor3m), 3)                                         AS avg_euribor_3m,
    ROUND(AVG("nr.employed"), 0)                                     AS avg_nr_employed
FROM bank_marketing
GROUP BY y;

SELECT '=== C2: RESPONSE RATE BY EURIBOR RATE BAND ===' AS query;
SELECT
    CASE
        WHEN euribor3m < 1.5  THEN '1_Low_under_1.5pct'
        WHEN euribor3m < 3.5  THEN '2_Medium_1.5_to_3.5pct'
        ELSE                       '3_High_above_3.5pct'
    END                                                              AS euribor_band,
    COUNT(*)                                                         AS contacts,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)                      AS subscribed,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
GROUP BY euribor_band
ORDER BY euribor_band;

SELECT '=== C3: RESPONSE RATE BY EMPLOYMENT VARIATION RATE BAND ===' AS query;
SELECT
    CASE
        WHEN "emp.var.rate" < -1.5 THEN '1_Contracting_below_neg1.5'
        WHEN "emp.var.rate" < 0    THEN '2_Slight_contraction'
        WHEN "emp.var.rate" < 1.0  THEN '3_Slight_expansion'
        ELSE                            '4_Expanding_above_1.0'
    END                                                              AS emp_var_band,
    COUNT(*)                                                         AS contacts,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
GROUP BY emp_var_band
ORDER BY emp_var_band;

-- Feature Engineering View
DROP VIEW IF EXISTS model_features;

CREATE VIEW model_features AS
SELECT
    rowid                                                            AS id,
    age,
    CASE
        WHEN age < 25 THEN 0
        WHEN age < 35 THEN 1
        WHEN age < 45 THEN 2
        WHEN age < 55 THEN 3
        WHEN age < 65 THEN 4
        ELSE 5
    END                                                              AS age_band_ord,

    CASE education
        WHEN 'illiterate'           THEN 0
        WHEN 'basic.4y'             THEN 1
        WHEN 'basic.6y'             THEN 2
        WHEN 'basic.9y'             THEN 3
        WHEN 'high.school'          THEN 4
        WHEN 'professional.course'  THEN 5
        WHEN 'university.degree'    THEN 6
        ELSE 3
    END                                                              AS education_ord,

    CASE WHEN contact   = 'cellular' THEN 1 ELSE 0 END               AS is_cellular,
    CASE WHEN housing   = 'yes'      THEN 1 ELSE 0 END               AS has_housing_loan,
    CASE WHEN loan      = 'yes'      THEN 1 ELSE 0 END               AS has_personal_loan,
    CASE WHEN "default" = 'yes'      THEN 1 ELSE 0 END               AS has_default,

    campaign,
    pdays,
    previous,
    CASE WHEN pdays = 999 THEN 0 ELSE 1 END                          AS was_previously_contacted,

    CASE poutcome
        WHEN 'failure'     THEN 0
        WHEN 'nonexistent' THEN 1
        WHEN 'success'     THEN 2
    END                                                              AS poutcome_ord,

    "emp.var.rate"                                                   AS emp_var_rate,
    "cons.price.idx"                                                 AS cons_price_idx,
    "cons.conf.idx"                                                  AS cons_conf_idx,
    euribor3m,
    "nr.employed"                                                    AS nr_employed,

    CASE WHEN y = 'yes' THEN 1 ELSE 0 END                           AS y_binary,
    job,
    y

FROM bank_marketing;

SELECT '=== D1: VERIFY model_features VIEW (first 5 rows) ===' AS query;
SELECT * FROM model_features LIMIT 5;

SELECT '=== D2: FEATURE VIEW ROW COUNT ===' AS query;
SELECT COUNT(*) AS rows_in_view,
       SUM(y_binary) AS total_subscribed,
       ROUND(100.0 * SUM(y_binary) / COUNT(*), 2) AS response_rate_pct
FROM model_features;

-- Summary statistics for presentation
SELECT '=== E1: TOP 5 HIGHEST-RESPONSE JOB+MONTH COMBOS ===' AS query;
SELECT
    job,
    month,
    COUNT(*)                                                         AS contacts,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
GROUP BY job, month
HAVING COUNT(*) >= 50
ORDER BY response_rate_pct DESC
LIMIT 10;

SELECT '=== E2: PREVIOUSLY CONTACTED VS FIRST-TIME CONTACTS ===' AS query;
SELECT
    CASE WHEN pdays = 999 THEN 'First-time contact' ELSE 'Previously contacted' END AS contact_history,
    COUNT(*)                                                         AS records,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)                      AS subscribed,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
GROUP BY contact_history;

SELECT '=== E3: CELLULAR + PREVIOUSLY SUCCESSFUL = BEST SEGMENT ===' AS query;
SELECT
    contact,
    poutcome,
    COUNT(*)                                                         AS records,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                             AS response_rate_pct
FROM bank_marketing
GROUP BY contact, poutcome
ORDER BY response_rate_pct DESC;

SELECT '=== ALL ANALYSIS COMPLETE ===' AS query;
SELECT
    '41,188 real records from UCI Bank Marketing Dataset' AS data_source,
    'Moro, Cortez & Rita (2014)'                          AS citation,
    'No data was simulated or invented'                   AS integrity_note;