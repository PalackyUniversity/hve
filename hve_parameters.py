from hve_codes import Vaccine, State
import os

# === PARAMETERS ===
N_PEOPLE = 170_000  # number of individuals in the model (roughly matches the 70+ population in the CPZP data)
N_DEATHS = 17_000   # number of deaths (2021-2022; roughly matches the deaths in the 70+ population in the CPZP data)
N_WEEKS = 2 * 52    # years 2021 and 2022

N_RUNS = 500        # number of simulation

DOSE_WEEK_DIST_PARAMS = {
    Vaccine.DOSE1: {"loc": 20, "scale": 3},  # mean, std of normally distributed weeks of dose 1
    Vaccine.DOSE2: {"loc": 20, "scale": 3},  # mean, std of normally distributed weeks of dose 2
    Vaccine.DOSE3: {"loc": 20, "scale": 3}   # mean, std of normally distributed weeks óf dose 3
}

DOSE_UPTAKE = {
    Vaccine.DOSE1: 0.82,  # fraction of N_people who took dose1
    Vaccine.DOSE2: 0.96,  # fraction of dose1 recipients who took dose2
    Vaccine.DOSE3: 0.82   # fraction od dose2 recipients who took dose3
}

# If dose[n+1] should be given earlier than "MIN_TIME" after dose[n], it will be given "MIN_TIME" after dose[n]
MIN_TIME = 4  # there have to be at least 4 weeks beteen consecutive doses

# === THE DEATH STEP ===
# - We now distribute the deaths independently of the vaccine doses.
# - The deaths are simulated BEFORE any vaccines are simulated.
P_DEATH = N_DEATHS / N_PEOPLE  # probability of dying sometimes during the simulated period

# === THE VACCINATION STEP ===
HVE_DURATION = 26  # How many weeks to look into the past
HVE_P = 0.5        # Probability that a vaccine dose will NOT be given due to HVE; set to 0 to disable HVE

# === VISUALIZATION ===
SPLIT_WEEK = 4    # the first 4 weeks after a dose are considered less than SPLIT_WEEK and the rest more than SPLIT_WEEK
FIGURE_PER = 1e5  # per 100 000 person years
COLORS = [
    # Gray (unvaccinated)
    (0.70, 0.70, 0.70),

    # Red
    (0.95, 0.15, 0.15),
    (0.95, 0.40, 0.15),

    # Green
    (0.15, 0.75, 0.15),
    (0.15, 0.85, 0.15),

    # Blue
    (0.15, 0.15, 1.00),
    (0.15, 0.50, 1.00),

    # Purple
    (0.95, 0.15, 0.95),
    (0.95, 0.50, 0.95)
]

RESULT_DIR = "result"

# === SANITY CHECKS ===
for i in Vaccine:
    assert i in DOSE_UPTAKE, f"Missing definition of parameter for vaccine {i.name} in DOSE_UPTAKE"
    assert i in DOSE_WEEK_DIST_PARAMS, f"Missing definition of parameter for vaccine {i.name} in DOSE_WEEK_DIST_PARAMS"

assert len(COLORS) >= len(State), f"Not enough colors defined in COLORS ({len(COLORS)}/{len(State)})"
assert 0 < N_DEATHS < N_PEOPLE, f"Incorrect amount of deaths"
assert N_WEEKS > 0, f"Number of weeks must be positive"
assert 0 <= HVE_P <= 1, "Probability of HVE must be between 0 and 1"
assert 0 < SPLIT_WEEK < N_WEEKS, "SPLIT_WEEK must be smaller than N_WEEKS and greather than 0"
assert 0 < HVE_DURATION < N_WEEKS, "HVE_DURATION must be smaller than N_WEEKS and greather than 0"
assert 0 < MIN_TIME < N_WEEKS, "MIN_TIME must be smaller than N_WEEKS and greather than 0"
assert 0 < FIGURE_PER, "FIGURE_PER must be positive"
assert 0 < P_DEATH < 1, "P_DEATH must be between 0 and 1"
assert all(0 <= v <= 1 for v in DOSE_UPTAKE.values()), "All values in DOSE_UPTAKE must be between 0 and 1"
assert all(0 < v["loc"] < N_WEEKS for v in DOSE_WEEK_DIST_PARAMS.values()), "All locs in DOSE_WEEK_DIST_PARAMS must be lower than N_WEEKS and greater than 0"
assert all(0 <= v["scale"] for v in DOSE_WEEK_DIST_PARAMS.values()), "All scales in DOSE_WEEK_DIST_PARAMS must be greater than 0"

os.makedirs(RESULT_DIR, exist_ok=True)
