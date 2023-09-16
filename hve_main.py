from matplotlib.ticker import FuncFormatter
from matplotlib import pyplot as plt
from hve_parameters import *
from hve_codes import State
import seaborn as sns
import numpy as np
import math

sns.set_theme()

# === Variables ===
died = [
    math.ceil(N_WEEKS * np.random.rand()) if np.random.rand() < P_DEATH else np.nan
    for i in range(N_PEOPLE)  # Week of death of each person (NaN if the person does not die)
]

vaccines = np.full((N_PEOPLE, len(Vaccine)), np.nan)  # Allocation for vaccination dates
population = np.zeros((N_PEOPLE, N_WEEKS), dtype=np.uint8)  # Allocation for internal state (code) of each person
n_dead = np.zeros((len(State), ))  # Allocation for the number of dead in each category

# === VACCINATION ===
for v in Vaccine:
    for i in range(N_PEOPLE):
        if np.random.rand() < DOSE_UPTAKE[v]:
            # Check if all previous doses were administered
            for j in range(v.value):
                if np.isnan(vaccines[i, j]):
                    break

            # Dose will be administered
            else:
                min_time = 1 if v == Vaccine.DOSE1 else MIN_TIME
                dose_week = max(round(np.random.normal(**DOSE_WEEK_DIST_PARAMS[v])), min_time)

                # Add lower dose week
                if v != Vaccine.DOSE1:
                    dose_week += vaccines[i, v.value - 1]

                # Cannot vaccinate after death
                if dose_week > died[i]:
                    pass

                # HVE kicks in
                elif abs(dose_week - died[i]) < HVE_DURATION:
                    if np.random.rand() > HVE_P:
                        vaccines[i, v.value] = dose_week

                # Vaccinate
                else:
                    vaccines[i, v.value] = dose_week

# # === CONVERT TO CODES ===
for i in range(N_PEOPLE):
    # Convert all dose dates
    for v in Vaccine:
        if not np.isnan(vaccines[i, v.value]):
            population[i, int(vaccines[i, v.value]):] = State.to_code(vaccine=v, higher=False)
            population[i, int(vaccines[i, v.value]) + SPLIT_WEEK:] = State.to_code(vaccine=v, higher=True)

    # Convert death date
    if not np.isnan(died[i]):
        population[i, (int(died[i]) + 1):] = 1  # death coded a week later (so vaccination status is not lost)

# # === COMPUTE THE NUMBER OF DEAD IN EACH CATEGORY ===
for i in range(N_PEOPLE):
    w = np.argwhere(population[i, :] == 1)  # find all weeks when the person is dead
    if len(w):  # if there are any
        w = w[0] - 1  # the week of death (ATTENTION: it's minus one, see the section above!)
        state = population[i, w]  # this is the vaccination status when the person died
        n_dead[list(map(lambda x: x.value, State)).index(state)] += 1  # increase the correct box by one

# === COMPUTE THE PERSON WEEKS IN EACH CATEGORY ===
person_weeks = [np.sum(population.flatten() == s.value) for s in State]  # find all weeks of this state and sum them up
person_years = np.array(person_weeks) / (365.25 / 7)
mortality = n_dead / person_years * FIGURE_PER

# === PLOT THE RESULT ===
plt.figure(figsize=(11, 6))
plt.barh([s.label.format(SPLIT_WEEK) for s in State], mortality, lw=0, color=[COLORS[n] for n in range(len(State))])

plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:,.0f}'))
plt.xlabel(f'Number of deaths per {FIGURE_PER:,.0f} person-years in the category')
plt.tight_layout()
plt.subplots_adjust(left=0.17)
plt.savefig("result.png")
plt.show()
