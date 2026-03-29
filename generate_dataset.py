"""
generate_dataset.py
===================
Generates a synthetic dataset of Data Analyst profiles for Argentina and the USA.

Calibration sources (2025):
  - SysArmy Salary Survey 2024-2025  →  https://sueldos.openqube.io/
  - US Bureau of Labor Statistics    →  https://www.bls.gov/
  - Glassdoor Data Analyst USA       →  https://www.glassdoor.com/
  - Stack Overflow Dev Survey 2024   →  https://survey.stackoverflow.co/2024/
  - LinkedIn Jobs (ARG & USA)        →  https://www.linkedin.com/jobs/

Output: da_arg_eeuu_2025.csv  (2,200 records)

Usage:
  pip install pandas numpy
  python generate_dataset.py

Author: Facundo Iván Ramírez Boll
"""

import pandas as pd
import numpy as np
import random

# ── Reproducibility ───────────────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

# ── Skill columns ─────────────────────────────────────────────────────────────
SKILL_COLS = [
    "skill_python",
    "skill_sql",
    "skill_power_bi",
    "skill_tableau",
    "skill_excel",
    "skill_r",
    "skill_dbt_airflow",
    "skill_cloud_aws_gcp_azure",
    "skill_inteligencia_artificial",
]

# ── Skill adoption probability by country and seniority ───────────────────────
# Order matches SKILL_COLS
# Calibrated against Stack Overflow Survey 2024 + LinkedIn Jobs
SKILL_PROB = {
    "Argentina": {
        "Junior":      [0.58, 0.86, 0.72, 0.46, 0.91, 0.18, 0.12, 0.18, 0.44],
        "Semi-Senior": [0.77, 0.93, 0.79, 0.59, 0.88, 0.25, 0.26, 0.32, 0.60],
        "Senior":      [0.90, 0.96, 0.81, 0.66, 0.84, 0.32, 0.42, 0.52, 0.76],
    },
    "EEUU": {
        "Junior":      [0.74, 0.89, 0.46, 0.50, 0.76, 0.30, 0.28, 0.50, 0.68],
        "Semi-Senior": [0.89, 0.94, 0.50, 0.58, 0.73, 0.38, 0.48, 0.70, 0.82],
        "Senior":      [0.94, 0.97, 0.48, 0.60, 0.68, 0.45, 0.64, 0.84, 0.92],
    },
}

# ── Monthly salary benchmarks (USD, median and std dev) ──────────────────────
# ARG: SysArmy 2025 (converted to USD at official + blue rate avg)
# USA: BLS + Glassdoor 2025
SALARIOS = {
    "Argentina": {
        "Junior":      (980,  190),
        "Semi-Senior": (2100, 400),
        "Senior":      (3700, 650),
    },
    "EEUU": {
        "Junior":      (5800,  750),
        "Semi-Senior": (8700,  950),
        "Senior":      (13200, 1900),
    },
}

# ── English proficiency salary premium in Argentina ───────────────────────────
ENGLISH_PREMIUM = {
    "Junior":      1.20,
    "Semi-Senior": 1.24,
    "Senior":      1.30,
}

# ── Probability of advanced English by country and seniority ─────────────────
ENGLISH_PROB = {
    "Argentina": {"Junior": 0.34, "Semi-Senior": 0.49, "Senior": 0.64},
    "EEUU":      {"Junior": 0.96, "Semi-Senior": 0.98, "Senior": 1.00},
}

# ── Work modality distribution ────────────────────────────────────────────────
MODALIDAD_PROB = {
    "Argentina": {
        "Junior":      {"Remoto 100%": 0.38, "Híbrido": 0.42, "Presencial": 0.20},
        "Semi-Senior": {"Remoto 100%": 0.52, "Híbrido": 0.36, "Presencial": 0.12},
        "Senior":      {"Remoto 100%": 0.62, "Híbrido": 0.30, "Presencial": 0.08},
    },
    "EEUU": {
        "Junior":      {"Remoto 100%": 0.40, "Híbrido": 0.44, "Presencial": 0.16},
        "Semi-Senior": {"Remoto 100%": 0.52, "Híbrido": 0.38, "Presencial": 0.10},
        "Senior":      {"Remoto 100%": 0.64, "Híbrido": 0.30, "Presencial": 0.06},
    },
}

# ── Industries ────────────────────────────────────────────────────────────────
INDUSTRIAS = {
    "Argentina": [
        "Fintech", "E-commerce", "Consultoría", "Telecomunicaciones",
        "Salud", "Tecnología/SaaS", "Banca", "Manufactura", "Gobierno", "Retail",
    ],
    "EEUU": [
        "Tech/SaaS", "Fintech", "Healthcare", "E-commerce", "Consulting",
        "Finance", "Media", "Government", "Manufacturing", "Retail",
    ],
}

# ── Generation parameters ─────────────────────────────────────────────────────
N_RECORDS   = {"Argentina": 1200, "EEUU": 1000}
SENIORITIES = ["Junior", "Semi-Senior", "Senior"]
SEN_WEIGHTS = [0.32, 0.44, 0.24]   # realistic market distribution
EXP_RANGE   = {"Junior": (0, 2.5), "Semi-Senior": (2.5, 6), "Senior": (6, 15)}


def generate_record(pais: str, seniority: str) -> dict:
    """Generate a single synthetic professional profile."""

    # --- Salary ---
    median, std = SALARIOS[pais][seniority]
    english = random.random() < ENGLISH_PROB[pais][seniority]
    salary = max(400, int(np.random.normal(median, std)))
    if pais == "Argentina" and english:
        salary = int(salary * ENGLISH_PREMIUM[seniority])
    salary = round(salary / 50) * 50  # round to nearest 50

    # --- Work modality ---
    mod_probs = MODALIDAD_PROB[pais][seniority]
    modality = random.choices(
        list(mod_probs.keys()), weights=list(mod_probs.values())
    )[0]

    # --- Skills (binary flags) ---
    skill_values = [
        1 if random.random() < p else 0
        for p in SKILL_PROB[pais][seniority]
    ]

    # --- Other fields ---
    exp = round(random.uniform(*EXP_RANGE[seniority]), 1)
    sat = round(max(1.0, min(5.0, np.random.normal(
        3.9 if pais == "EEUU" else 3.5, 0.7
    ))), 1)

    record = {
        "pais":             pais,
        "seniority":        seniority,
        "salario_usd":      salary,
        "ingles_avanzado":  english,
        "modalidad":        modality,
        "industria":        random.choice(INDUSTRIAS[pais]),
        "anios_exp":        exp,
        "satisfaccion":     sat,
    }
    for col, val in zip(SKILL_COLS, skill_values):
        record[col] = val

    return record


def main():
    records = []
    for pais in ["Argentina", "EEUU"]:
        for _ in range(N_RECORDS[pais]):
            seniority = random.choices(SENIORITIES, weights=SEN_WEIGHTS)[0]
            records.append(generate_record(pais, seniority))

    df = (
        pd.DataFrame(records)
        .sample(frac=1, random_state=42)
        .reset_index(drop=True)
    )

    output = "da_arg_eeuu_2025.csv"
    df.to_csv(output, index=False)

    # Summary
    print(f"✅  Dataset saved → {output}")
    print(f"    Total records : {len(df):,}")
    print(f"\n  Median salary by country and seniority (USD/month):")
    print(df.groupby(["pais", "seniority"])["salario_usd"]
            .median().round(0).to_string())
    print(f"\n  % with advanced English (Argentina):")
    print(df[df["pais"] == "Argentina"]
            .groupby("seniority")["ingles_avanzado"]
            .mean().mul(100).round(1).to_string())
    print(f"\n  AI tool adoption (%):")
    print(df.groupby(["pais", "seniority"])["skill_inteligencia_artificial"]
            .mean().mul(100).round(1).to_string())
    print(f"\nNext step: run  python analysis.py  to generate the 8 charts.")


if __name__ == "__main__":
    main()
