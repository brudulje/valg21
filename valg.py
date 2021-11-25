# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 21:30:26 2021

@author: jsg
"""

import pandas as pd

result_file = "~/Documents/edb/valg21/2021-11-10_partifordeling_1_st_2021.csv"
mandates_file = "~/Documents/edb/valg21/mandater.csv"
df = pd.read_csv(result_file, sep=";")

sperregrense = 0.04 
# df.info()
# df.head()

# Produce list of mandates and districts.
# mandater = df.groupby("Fylkenavn")["Antall mandater"].sum()
# mandater.to_csv("~/Documents/edb/valg21/mandater.csv")

# Cast to string to be able to test against
df["Fylkenavn"] = df["Fylkenavn"].astype("string")
df["Partikode"] = df["Partikode"].astype("string")
df["Partinavn"] = df["Partinavn"].astype("string")
# ak = df["Fylkenavn" == "Akershus"] # you wish
# ak = df[df["Fylkenavn"] == "Akershus"]
# print(ak.info())

# df.dtypes
# election_result = df[["Fylkenummer", "Fylkenavn", "Partikode", 
#                       "Partinavn", "Antall stemmer totalt"]]
# election_result.astype({"Fylkenummer": 'int32'}) # nix
# election_result.astype({"Fylkenavn": "string"}) # nope
# election_result.info()
# election_result.head()

mandates_per_district = pd.read_csv(mandates_file)
# print(mandates_per_district)
max_mandates = mandates_per_district["Antall mandater"].max()
# print(max_mandates)
st_Lagues_mod = 1.4
kvotient_list = [st_Lagues_mod]
for n in range(3, 2 * max_mandates, 2):
    kvotient_list.append(n)
# Calculating kvotients for all districts and parties
for n in kvotient_list:
    # print(n)
    df[f"{int(n)}"] = df["Antall stemmer totalt"] / n
# print(df.info())

# Adding column to store results from calculations
df["Direct"] = 0  # Direct mandates
df["Evening"] = 0  # Evening out mandates
# ['{:.2f}'.format(x) for x in nums]
kvotient_string_list = [f"{int(n)}" for n in kvotient_list]
# print(kvotient_string_list)

maxValue = df[kvotient_string_list].max()
# print(maxValue)

# Splitting by fylke, calculating separately
# fylke_result = df[(df["Fylkenavn"] == "Akershus")]
# fylke_result = election_result[(election_result["Fylkenummer"] == 1)]
# fylke_result.info()
# print(fylke_result)
# print(fylke_result.tail())
# print(df["Fylkenavn"].unique())
for fylke in df["Fylkenavn"].unique():
    mandates = mandates_per_district[
        mandates_per_district["Fylkenavn"] == fylke].iat[0, 1]
    # print(fylke, mandates)
    fylke_result = df[(df["Fylkenavn"] == fylke)]

# Saving one mandate for the evening out mandate
    for n in range(mandates - 1):
        # Find max kvotient
        max_column = fylke_result[kvotient_string_list].max().idxmax()
        # print(f"{max_column=}")
        max_row = fylke_result[[max_column]].idxmax().max()
        # print(f"{max_row}")
        # print(fylke_result.at[max_row, max_column])
        
        # Give the party with the largest kvotient a mandate
        df.at[max_row, "Direct"] = df.at[max_row, "Direct"] + 1
        # Remove that kvotient from the list
        fylke_result.at[max_row, max_column] = 0.0
    # fylke_result.info()

# # Checking my calculations
# bom = 0        
# for idx, row in df.iterrows():
#     if not (row["Antall mandater"] 
#             - row["Antall utjevningsmandater"]) == row["Direct"]:
#         print("Æsj", row["Antall mandater"], row["Direct"])
#         bom += 1
#     elif row["Direct"] > 0:
#         print("Jadda", row["Antall mandater"], row["Direct"])
# print(f"{bom=}")
df.to_csv("BeregnetStorting.csv")

# Evening out mandates are only for parties sabove "sperregrense" nationaly

# Calculating national results for all parties
ndf = df.groupby("Partinavn")["Antall stemmer totalt"].sum()
# print(ndf, type(ndf))
# Converting to dataframe (from Series)
ndf = ndf.to_frame()
# print(ndf, type(ndf))

# print(ndf, type(ndf))
# Fjerner blanke
ndf.at["Blanke", "Antall stemmer totalt"] = 0
# print(ndf)
ndf["Oppslutning"] = ndf["Antall stemmer totalt"] \
    / ndf["Antall stemmer totalt"].sum()
# print(ndf)
# Kicking out the parties below the sperregrense threshold
ndf = ndf.drop(ndf[ndf.Oppslutning < sperregrense].index)
print(ndf)
