# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 21:30:26 2021

@author: jsg
"""

import pandas as pd
import numpy as np

# Result, laws and regulations source:
# https://valgresultat.no/eksport-av-valgresultater?type=st&year=2021
# https://www.valg.no/om-valg/valggjennomforing/lover-og-regler/
# https://www.valg.no/om-valg/valgene-i-norge/stortingsvalg/fordeling-av-utjevningsmandater/
# https://lovdata.no/dokument/NL/lov/2002-06-28-57
# https://lovdata.no/dokument/NL/lov/1814-05-17-nn/KAPITTEL_3#§59
# https://snl.no/valordning_i_Noreg
# https://snl.no/utjevningsmandat

result_file = "~/Documents/edb/valg21/2022-02-12_partifordeling_1_st_2021.csv"
mandates_file = "~/Documents/edb/valg21/mandater.csv"
utjevning_file = "~/Documents/edb/valg21/utjevning.csv"
sperregrense = 0.04
# total_mandates = 169  # Total mandates in Stortinget. # Now read from file.

# Read results from file
df = pd.read_csv(result_file, sep=";")
# Cast to string to be able to test against
df["Fylkenavn"] = df["Fylkenavn"].astype("string")
# df["Partikode"] = df["Partikode"].astype("string")
df["Partinavn"] = df["Partinavn"].astype("string")

# df.info()
# df.head()

# Read number of total mandates per fylke from file
mandates_per_district = pd.read_csv(mandates_file)
max_mandates = mandates_per_district["Antall mandater"].max()
total_mandates = mandates_per_district["Antall mandater"].sum()
mandates_per_district.set_index("Fylkenavn", inplace=True)

# Read number of utjevning mandates per fylke from file
utjevning_per_district = pd.read_csv(utjevning_file)
utjevning_per_district.set_index("Fylkenavn", inplace=True)

# Calculate number of direct mandates per fylke
direkte_per_district = mandates_per_district.subtract(utjevning_per_district)
# print("Direkte mandater per fylke\n", direkte_per_district)

st_Lagues_mod = 1.4

kvotient_list = [st_Lagues_mod]
for n in range(3, 2 * max_mandates, 2):
    # Will allow one single party to win all mandates,
    # even from the largest fylke
    kvotient_list.append(n)
kvotient_string_list = [f"{n}" for n in kvotient_list]

utjevning_kvotient_list = [st_Lagues_mod]
# Need to make this list longer than for max mandates from a single fylke
# in order to reuse it for the national evening out mandates.
for n in range(3, 2 * total_mandates, 2):
    utjevning_kvotient_list.append(n)
utjevning_kvotient_string_list = [f"{n}" for n in utjevning_kvotient_list]


def calculate_kvotients(df, kvotient_list):
    # Calculating kvotients for all districts and parties
    for n in kvotient_list:
        # print(n)
        df[f"{n}"] = df["Antall stemmer totalt"] / n
    # print(df.info())
    return df


print("Total votes, entire nation:", df["Antall stemmer totalt"].sum())
df = calculate_kvotients(df, kvotient_list)
# Adding columns to store results from calculations
df["Direct"] = 0  # Direct mandates
df["Evening"] = 0  # Evening out mandates
# print(kvotient_string_list)

for fylke in df["Fylkenavn"].unique():
    # mandates = mandates_per_district.at[fylke, "Antall mandater"]
    # utjevning = utjevning_per_district.at[fylke, "Antall mandater"]
    direct = direkte_per_district.at[fylke, "Antall mandater"]
    # print(fylke, mandates)
    fylke_result = df[(df["Fylkenavn"] == fylke)]

    # Saving appropriate mandates for the utjevning mandates
    for n in range(direct):
        # Find max kvotient
        max_column = fylke_result[kvotient_string_list].max().idxmax()
        max_row = fylke_result[[max_column]].idxmax().max()
        # print(f"{max_column=}, {max_row}",
        #       + fylke_result.at[max_row, max_column])

        # Give the party with the largest kvotient a mandate
        df.at[max_row, "Direct"] = df.at[max_row, "Direct"] + 1
        # Remove that kvotient from the list
        # Multiplying with -1 makes sure it is not the larges the next
        # time round, while still keeping the value for controlling
        # the result later if needed.
        fylke_result.at[max_row, max_column] *= -1
    # fylke_result.info()

# Checking my calculations
# bom = 0
# for idx, row in df.iterrows():
#     if not (row["Antall mandater"]
#             - row["Antall utjevningsmandater"]) == row["Direct"]:
#         print("Æsj", row["Antall mandater"], row["Direct"])
#         bom += 1
#     elif row["Direct"] > 0:
#         # print("Jadda", row["Antall mandater"], row["Direct"], end="  ")
#         pass
# print(f"{bom=}")
df.to_csv("BeregnetStortingDirekteMandater.csv")

# Make and print nice list of national total direct mandates.
direct_df = df.groupby("Partinavn")["Direct"].sum()
direct_df = direct_df.to_frame()  # "Direct").reset_index()
# direct_df = df.groupby(["Partinavn"], as_index=False)["Direct"].sum()  #####
# direct_df.set_index("Partinavn", inplace=True)  #####
# Skip the parties without mandates
direct_df = direct_df.drop(direct_df[direct_df.Direct < 1].index)
# direct_df.set_index('Partinavn', inplace=True)
direct_df.to_csv("Direte_mandater.csv")
print(direct_df)

print("\nUtjevning på gang...")
# Evening out mandates are only for parties above "sperregrense" nationaly
# Calculating national results for all parties
ndf = df.groupby("Partinavn")["Antall stemmer totalt"].sum()
# print(ndf, type(ndf))
# Converting to dataframe (from Series)
ndf = ndf.to_frame()
# print(ndf)  # , type(ndf))
ndf.to_csv("Grunnlag_utjevning.csv")
# # print(ndf, type(ndf))
# # Blanke stemmer er ikke en del av grunnlaget for oppslutning.
# # Removing blank votes from the total
ndf.at["Blanke", "Antall stemmer totalt"] = 0
# # print(ndf)
# print("Total votes to calculate oppslutning: ", ndf["Antall stemmer totalt"].sum())
ndf["Oppslutning"] = ndf["Antall stemmer totalt"] \
    / ndf["Antall stemmer totalt"].sum()
# print(ndf)
ndf["Direct"] = df.groupby("Partinavn")["Direct"].sum()  # There we go

# print(ndf.info())
# print(ndf)

# Need to count the number of representatives the small parties
# have won. These are to be subtracted from those to be divided
# in the national calculation to determine who gets an
# evening out mandate.
small_party_mandates = ndf[ndf.Oppslutning < sperregrense]["Direct"].sum()
# print(f"{small_party_mandates=}")

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

# print(f"{mandates_to_asif=}")
# print(ndf)
too_many_mandates = 1
numb = 0
while too_many_mandates > 0:
    numb += 1
    # Reset as-if calculation
    ndf["asif"] = 0
    # print(f"{mandates_to_asif=}")
    # Reset all the kvotients to positive numbers
    # or else, the calculation will be incorrect!
    ndf[utjevning_kvotient_string_list] = abs(ndf[utjevning_kvotient_string_list])
    for n in range(mandates_to_asif):
        # Find max kvotient
        max_column = ndf[utjevning_kvotient_string_list].max().idxmax()
        max_row = ndf[[max_column]].idxmax().max()
        # Give the party with the largest kvotient a mandate
        ndf.at[max_row, "asif"] = ndf.at[max_row, "asif"] + 1
        # Remove that kvotient from the list
        ndf.at[max_row, max_column] *= -1  # This is the culprit!
    # print(ndf["Direct"], ndf["asif"])
    ndf.to_csv(f"Beregning_Utjevning_{numb}.csv")
    # Check if some party got too many mandates
    too_many_mandates = ndf[ndf.Direct > ndf.asif]["Direct"].sum()
    # print(ndf["asif"])
    # print(f"{too_many_mandates=}")
    # Kick out the parties with too many mandates
    # print("Dropping ", ndf[ndf.Direct > ndf.asif].index)
    ndf = ndf.drop(ndf[ndf.Direct > ndf.asif].index)
    # Adjust number of mandates to distribute
    mandates_to_asif = mandates_to_asif - too_many_mandates
ndf["Utjevning"] = ndf["asif"] - ndf["Direct"]
print("\nParties are underrepr, should have representatives:")
print(ndf["asif"])
print("\nParties will get utgjevning:")
print(ndf["Utjevning"])

# Now, calculate which party gets a compensatory mandate in which district.

# Calculate fylkesfaktor

# Getting a list of the total number of votes in each fylke
plopp = df.groupby("Fylkenavn")["Antall stemmer totalt"].sum()
plopp = plopp.to_frame()
print(plopp.info())
print("\n\nPlopp\n", plopp, type(plopp))
plopp.to_csv("Stemmer_per_fylke.csv")

df["Fylkesstemmer"] = 0
# Getting the total number of votes in each fylke into the df:
for idx, row in df.iterrows():
    for ploppidx, plopprow in plopp.iterrows():
        if row["Fylkenavn"] == ploppidx:
            # print(row["Fylkenavn"], ploppidx,)
            df.loc[idx, "Fylkesstemmer"] = plopp.loc[ploppidx, "Antall stemmer totalt"]

# Now, reuse that most elegant methode to get the number of direct mandates in.
df["Direktemandater fra fylket"] = 0
dirdf = df.groupby("Fylkenavn")["Direct"].sum()
dirdf = dirdf.to_frame()
print(dirdf.info())
print("\n\nDirdf\n", dirdf, type(dirdf))
dirdf.to_csv("Direct_per_fylke.csv")

df["Direktemandater fra fylket"] = 0
# Getting the total number of votes in each fylke into the df:
for idx, row in df.iterrows():
    for dirdfidx, dirdfrow in dirdf.iterrows():
        if row["Fylkenavn"] == dirdfidx:
            # print(row["Fylkenavn"], ploppidx,)
            df.loc[idx, "Direktemandater fra fylket"] = dirdf.loc[dirdfidx, "Direct"]

df["Fylkesfaktor"] = df["Fylkesstemmer"] / df["Direktemandater fra fylket"]

# Now, revise the number of votes:
df["Revidert stemmetall"] = np.where(df["Direct"] == 0, \
                          df["Antall stemmer totalt"], \
                          df["Antall stemmer totalt"] / (2 * df.Direct + 1))
df["Utjevningstall"] = df["Revidert stemmetall"] / df["Fylkesfaktor"]
# df
df.to_csv("df.csv")
