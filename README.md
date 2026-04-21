# Bank Marketing Campaign Analysis

An end-to-end data analytics project exploring the drivers of customer subscription behavior in a real-world bank marketing campaign. The project uses SQL, Python, and Tableau to analyze 41,188 customer records from the UCI Machine Learning Repository and identify the key factors influencing term deposit subscriptions.

---

## Project Objective

The goal of this project is to understand:
- What customer characteristics influence subscription to a term deposit
- How campaign timing and contact history affect conversion rates
- How macroeconomic indicators impact customer behavior

---

## Tools & Technologies

- **SQL (SQLite)**: data structuring and feature engineering
- **Python (Pandas)**: data preprocessing and transformation
- **Tableau**: interactive dashboard development
- **GitHub Pages**: portfolio deployment

---

## Dataset

- Source: UCI Machine Learning Repository  
- Study: Moro, Cortez & Rita (2014)  
- Records: 41,188 customer interactions  
- Target variable: `y`

Dataset link:  
https://archive.ics.uci.edu/dataset/222/bank+marketing

---

## Key Features Engineered

- Age bands (e.g., 25–34, 35–44, etc.)
- Campaign contact buckets
- Previous contact flag `pdays`
- Education ranking
- Euribor interest rate bands
- Binary subscription indicator `subscribed_num`

---

## Key Insights

- Previously successful clients have a **much higher conversion rate (~65%)** compared to new contacts (~9%)
- Subscription rates vary significantly by **job type and age group**
- Campaign effectiveness is strongly influenced by **macro-economic conditions (euribor rates)**
- Contact frequency and timing play a critical role in conversion likelihood

---

## Dashboard

The final interactive Tableau dashboard includes:
- Customer segmentation analysis (job, age, education)
- Campaign performance over time (month, contact frequency)
- Prior campaign outcome impact
- Macroeconomic effect (euribor rate vs response)

View live dashboard:  
https://stsobhani.github.io/bank-marketing-analysis/

---

## Methodology

1. Data cleaning and preprocessing in Python
2. Feature engineering using SQL (SQLite views)
3. Exploratory analysis of customer behavior patterns
4. Tableau dashboard development for visualization
5. Deployment via GitHub Pages

---

## Repository Structure
