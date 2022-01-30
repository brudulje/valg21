# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 21:30:26 2021

@author: jsg
"""

import pandas as pd

result_file = "~/Documents/edb/valg21/2021-11-10_partifordeling_1_st_2021.csv"
mandates_file = "~/Documents/edb/valg21/mandater.csv"
sperregrense = 0.04
total_mandates = 169  # Total mandates in Stortinget.
# df.info()
# df.head()

# Produce list of mandates and districts.
# mandater = df.groupby("Fylkenavn")["Antall mandater"].sum()
# mandater.to_csv("~/Documents/edb/valg21/mandater.csv")

df = pd.read_csv(result_file, sep=";")

# Cast to string to be able to test against
df["Fylkenavn"] = df["Fylkenavn"].astype("string")
df["Partikode"] = df["Partikode"].astype("string")
df["Partinavn"] = df["Partinavn"].astype("string")

# df.info()
# df.head()

mandates_per_district = pd.read_csv(mandates_file)
# print(mandates_per_district)
max_mandates = mandates_per_district["Antall mandater"].max()
# print(max_mandates)
st_Lagues_mod = 1.4
kvotient_list = [st_Lagues_mod]
utjevning_kvotient_list = [st_Lagues_mod]
# Need to make this list longer than for max mandates from a single fylke
# in order to reuse it for the national evening out mandates.
for n in range(3, 2 * max_mandates, 2):
    kvotient_list.append(n)
kvotient_string_list = [f"{int(n)}" for n in kvotient_list]
for n in range(3, 2 * total_mandates, 2):
    utjevning_kvotient_list.append(n)
utjevning_kvotient_string_list = [f"{int(n)}" for n in utjevning_kvotient_list]


def calculate_kvotients(df, kvotient_list):
    # Calculating kvotients for all districts and parties
    for n in kvotient_list:
        # print(n)
        df[f"{int(n)}"] = df["Antall stemmer totalt"] / n
    # print(df.info())
    return df


df = calculate_kvotients(df, kvotient_list)
# Adding columns to store results from calculations
df["Direct"] = 0  # Direct mandates
df["Evening"] = 0  # Evening out mandates
# print(kvotient_string_list)


for fylke in df["Fylkenavn"].unique():
    mandates = mandates_per_district[
        mandates_per_district["Fylkenavn"] == fylke
    ].iat[0, 1]
    # print(fylke, mandates)
    fylke_result = df[(df["Fylkenavn"] == fylke)]

    # Saving one mandate for the evening out mandate
    for n in range(mandates - 1):
        # Find max kvotient
        max_column = fylke_result[kvotient_string_list].max().idxmax()
        max_row = fylke_result[[max_column]].idxmax().max()
        # print(f"{max_column=}")
        # print(f"{max_row}")
        # print(fylke_result.at[max_row, max_column])
        
        # Give the party with the largest kvotient a mandate
        df.at[max_row, "Direct"] = df.at[max_row, "Direct"] + 1
        # Remove that kvotient from the list
        fylke_result.at[max_row, max_column] = 0.0
    # fylke_result.info()

# Checking my calculations
# bom = 0        
# for idx, row in df.iterrows():
#     if not (row["Antall mandater"] 
#             - row["Antall utjevningsmandater"]) == row["Direct"]:
#         print("Æsj", row["Antall mandater"], row["Direct"])
#         bom += 1
#     elif row["Direct"] > 0:
#         print("Jadda", row["Antall mandater"], row["Direct"], end="  ")
# print(f"{bom=}")
# df.to_csv("BeregnetStortingUtenUtjevning.csv")

# TODO Start by acalculating the teoretical number of mandates for
# all parties if the entire nation was one single district.

# XXX 

# Evening out mandates are only for parties above "sperregrense" nationaly


# Calculating national results for all parties
ndf = df.groupby("Partinavn")["Antall stemmer totalt"].sum()
# print(ndf, type(ndf))
# Converting to dataframe (from Series)
ndf = ndf.to_frame()
# print(ndf)  # , type(ndf))

# # print(ndf, type(ndf))
## Blanke stemmer er ikke en del av grunnlaget for oppslutning.
# # FRemoving blank votes from the total
ndf.at["Blanke", "Antall stemmer totalt"] = 0
# # print(ndf)
ndf["Oppslutning"] = ndf["Antall stemmer totalt"] \
    / ndf["Antall stemmer totalt"].sum()
# print(ndf)
dir_series = df.groupby("Partinavn")["Direct"].sum()
# print(dir_series, type(dir_series))
# ndf = pd.concat([ndf, dir_series.to_frame()])  # Nope, not quite
# ndf.merge(dir_series, left_index=True, right_index=True)  # Nope
ndf["Direct"] = dir_series  # There we go

# print(dir_series)
# print(ndf.info())
# print(ndf)

# Need to count the number of representatives the small parties
# have won. These are to be subtracted from those to be divided
# in the national calculation to determine who gets an 
# evening out mandate.
small_party_mandates = ndf[ndf.Oppslutning < sperregrense]["Direct"].sum()
print(f"{small_party_mandates=}")

# Kicking out the parties below the sperregrense threshold
ndf = ndf.drop(ndf[ndf.Oppslutning < sperregrense].index)
# print(ndf)
# Calculating kvotients
ndf = calculate_kvotients(ndf, utjevning_kvotient_list)
# print(ndf)

# Do the as-if calculation on how many mandates each party should 
# have had according to national votes

# The direct mandates already given to the small parties
# should be subtracted from the total

mandates_to_asif = total_mandates - small_party_mandates
print(f"{mandates_to_asif=}")
# print(ndf)
too_many_mandates = 1
while too_many_mandates > 0:
    # Reset as-if calculation
    ndf["asif"] = 0
    print(f"{mandates_to_asif=}")
    for n in range(mandates_to_asif):
        # Find max kvotient
        max_column = ndf[utjevning_kvotient_string_list].max().idxmax()
        max_row = ndf[[max_column]].idxmax().max()
        # Give the party with the largest kvotient a mandate
        ndf.at[max_row, "asif"] = ndf.at[max_row, "asif"] + 1
        # Remove that kvotient from the list
        ndf.at[max_row, max_column] = 0.0
    print(ndf["Direct"], ndf["asif"])
    # Check if some party got too many mandates
    too_many_mandates = ndf[ndf.Direct > ndf.asif]["Direct"].sum()
    print(f"{too_many_mandates=}")

    # Kick out the parties with too many mandates
    ndf = ndf.drop(ndf[ndf.Direct > ndf.asif].index)    
    # Adjust number of mandates to distribute
    mandates_to_asif = mandates_to_asif - too_many_mandates

# This seems to work, but the numbers are slightly wrong.
# Here, Høyre gets 2, and Frp gets 3,
# but according to official numbers is shoule be 1 and 4

# # Calculating the number of evening out mandates for each party
# for n in range(19):
#     # Find max kvotient
#     max_column = ndf[kvotient_string_list].max().idxmax()
#     max_row = ndf[[max_column]].idxmax().max()
#     print(f"{max_column=}", type(max_column))
#     print(f"{max_row=}", type(max_row))
    
#     # Give the party with the largest kvotient a mandate
#     ndf.at[max_row, "Evening"] = ndf.at[max_row, "Evening"] + 1
#     # Remove that kvotient from the list
#     ndf.at[max_row, max_column] = 0.0
# print(ndf)
