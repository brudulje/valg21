# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 21:30:26 2021

@author: jsg
"""

import pandas as pd

result_file = "~/Documents/edb/valg21/2021-11-10_partifordeling_1_st_2021.csv"
df = pd.read_csv(result_file, sep=";")
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

mandates_per_district = pd.read_csv("~/Documents/edb/valg21/mandater.csv")
max_mandates = mandates_per_district["Antall mandater"].max()
# print(max_mandates)
kvotient_list = [1.4]
for n in range(3, 2 * max_mandates, 2):
    kvotient_list.append(n)
# Calculating kvotients for all districts and parties
for n in kvotient_list:
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
fylke_result = df[(df["Fylkenavn"] == "Akershus")]
# fylke_result = election_result[(election_result["Fylkenummer"] == 1)]
# fylke_result.info()
print(fylke_result)
# print(fylke_result.tail())

# Find max kvotient
print(fylke_result[kvotient_string_list].idxmax())        
