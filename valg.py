# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 21:30:26 2021

@author: jsg
"""

import pandas as pd

# Result, laws and regulations source:
# https://valgresultat.no/eksport-av-valgresultater?type=st&year=2021
# https://www.valg.no/om-valg/valggjennomforing/lover-og-regler/
# https://www.valg.no/om-valg/valgene-i-norge/stortingsvalg/fordeling-av-utjevningsmandater/
# https://lovdata.no/dokument/NL/lov/2002-06-28-57
# https://lovdata.no/dokument/NL/lov/1814-05-17-nn/KAPITTEL_3#§59
# https://snl.no/valordning_i_Noreg
# https://snl.no/utjevningsmandat

result_file = "~/Documents/edb/valg21/2021-11-10_partifordeling_1_st_2021.csv"
mandates_file = "~/Documents/edb/valg21/settings/mandater.csv"
utjevning_file = "~/Documents/edb/valg21/settings/utjevning1.csv"
sperregrense = 0.04
evening_per_fylke = 1  # Should be calculated from utjevning_file
st_Lagues_mod = 1.4
runcode = "sg4_u1"
log_file = f"C:/Users/jsg/Documents/edb/valg21/valg21_log_{runcode}.txt"
summary_file = f"C:/Users/jsg/Documents/edb/valg21/summary_{runcode}.txt"
comment = "Gjeldende valgregler 2021."
# "Sperregrense 4%, 1 utjevningsmandat per fylke, men fordelt etter antall mandater i hvert fylke, ellers "
# "19 utjevningsmandater fordelt etter mandater i hvert fylke"

#
# total_mandates = 169  # Total mandates in Stortinget. # Now read from file.

# Read results from file
df = pd.read_csv(result_file, sep=";", encoding="utf8")
# Cast to string to be able to test against
df["Fylkenavn"] = df["Fylkenavn"].astype("string")
df["Partikode"] = df["Partikode"].astype("string")
df["Partinavn"] = df["Partinavn"].astype("string")
# df.info()
# df.head()

summary = {}
parties = {}
for parti in df["Partikode"].unique():
    parties[parti] = 0
for fylke in df["Fylkenavn"].unique():
    summary[fylke] = parties.copy()

with open(log_file, "w", encoding="utf-16") as f:
    # Open in write mode only the first time, to avoid overwriting
    f.write("Valgresultater etter Stortingsvalget 2021.\n\n")

# Read number of total mandates per fylke from file
mandates_per_district = pd.read_csv(mandates_file)
max_mandates = mandates_per_district["Antall mandater"].max()
total_mandates = mandates_per_district["Antall mandater"].sum()
mandates_per_district.set_index("Fylkenavn", inplace=True)
# Read number of utjevning mandates per fylke from file
utjevning_per_district = pd.read_csv(utjevning_file)
utjevning_per_district.set_index("Fylkenavn", inplace=True)
overview_mandates = mandates_per_district.copy()
# overview_mandates.rename(columns={"Antall mandater": "Direkte"}, inplace=True)
overview_mandates["Utjevning"] = utjevning_per_district["Antall mandater"]

# Write currently used settings/rules in log
with open(log_file, "a", encoding="utf-16") as f:
    f.write("Mandater per valgdistrikt (fylke):\n"
            + str(mandates_per_district) + "\n\n")
    f.write("Utjevningsmandater per valgdistrikt (fylke):\n"
            + str(utjevning_per_district) + "\n\n")
    f.write(f"Sperregrense: {sperregrense}\n\n")
    f.write(f"St. Lagues modifisert: {st_Lagues_mod}\n\n")
    f.write(comment + "\n\n")

# Calculate number of direct mandates per fylke
direkte_per_district = mandates_per_district.subtract(utjevning_per_district)

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
        df[f"{n}"] = df["Antall stemmer totalt"] / n
    return df


df = calculate_kvotients(df, kvotient_list)
# Adding columns to store results from calculations
df["Direct"] = 0  # Direct mandates
df["Evening"] = 0  # Evening out mandates

print("Regner ut direktemandater")
for fylke in df["Fylkenavn"].unique():
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
        party = df.at[max_row, "Partikode"]
        with open(log_file, "a", encoding="utf-16") as f:
            f.write(f"{party:4s} direkte {fylke}\n")
        # Update summary table
        summary[fylke][party] += 1
        # Remove that kvotient from the list
        # Multiplying with -1 makes sure it is not the largest the next
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
# df.to_csv(f"BeregnetStortingDirekteMandater_{runcode}.csv")

# Make and print nice list of national total direct mandates.
direct_df = df.groupby("Partikode")["Direct"].sum()
direct_df = direct_df.to_frame()
# Skip the parties without mandates
direct_df = direct_df.drop(direct_df[direct_df.Direct < 1].index)
# direct_df.to_csv(f"Direte_mandater_{runcode}.csv")
print(direct_df)

print("\nBeregner antall utjevningsmandater til hvert parti")
# Evening out mandates are only for parties above "sperregrense" nationally
# Calculating national results for all parties
ndf = df.groupby("Partikode")["Antall stemmer totalt"].sum()
# Converting to dataframe (from Series)
ndf = ndf.to_frame()
ndf.to_csv(f"./details/Grunnlag_utjevning_{runcode}.csv")
# Removing blank votes from the total, as they don't count for "oppslutning"
ndf.at["Blanke", "Antall stemmer totalt"] = 0
# print(ndf)
# print("Total votes to calculate oppslutning: "
# + ndf["Antall stemmer totalt"].sum())
ndf["Oppslutning"] = ndf["Antall stemmer totalt"] \
    / ndf["Antall stemmer totalt"].sum()
# print(ndf)
ndf["Direct"] = df.groupby("Partikode")["Direct"].sum()  # There we go
# Removing blank votes, to avoid them getting an evening out mandate
ndf = ndf.drop("BLANKE")
# print(ndf.info())
minst = 0.001
with open(log_file, "a", encoding="utf-16") as f:
    f.write(f"\nPartier med mer enn {100*minst:.2f} % oppslutning:\n")
    f.write(str(100*ndf[ndf.Oppslutning > minst]['Oppslutning']))
    f.write("\n")

# Need to count the number of representatives the small parties
# have won. Small parties are those with oppslutning below the
# sperregrense. These are to be subtracted from those to be divided
# in the national calculation to determine who gets an
# evening out mandate.
small_party_mandates = ndf[ndf.Oppslutning < sperregrense]["Direct"].sum()
# print(f"{small_party_mandates=}")

# Kicking out the parties below the sperregrense threshold
ndf = ndf.drop(ndf[ndf.Oppslutning < sperregrense].index)
# print(ndf)
# Calculating kvotients
ndf = calculate_kvotients(ndf, utjevning_kvotient_list)

# Do the as-if calculation on how many mandates each party should
# have had according to national votes

# The direct mandates already given to the small parties
# should be subtracted from the total
mandates_to_asif = int(total_mandates) - int(small_party_mandates)
# print(f"{mandates_to_asif=}", type(mandates_to_asif))
# print(f"{mandates_to_asif=}")
# print(ndf)
with open(log_file, "a", encoding="utf-16") as f:
    f.write("\n")
too_many_mandates = 1
numb = 0
while too_many_mandates > 0:
    numb += 1
    # Reset as-if calculation
    ndf["asif"] = 0
    # Reset all the kvotients to positive numbers
    # or else, the calculation will be incorrect!
    ndf[utjevning_kvotient_string_list] = \
        abs(ndf[utjevning_kvotient_string_list])
    for n in range(mandates_to_asif):
        # Find max kvotient
        max_column = ndf[utjevning_kvotient_string_list].max().idxmax()
        max_row = ndf[[max_column]].idxmax().max()
        # Give the party with the largest kvotient a mandate
        ndf.at[max_row, "asif"] = ndf.at[max_row, "asif"] + 1
        # Remove that kvotient from the list
        ndf.at[max_row, max_column] *= -1
    # print(ndf["Direct"], ndf["asif"])
    ndf.to_csv(f"./details/Beregning_Utjevning_{runcode}_{numb}.csv")
    # Check if some party got too many mandates
    too_many_mandates = int(ndf[ndf.Direct > ndf.asif]["Direct"].sum())
    # Kick out the parties with too many mandates
    with open(log_file, "a", encoding="utf-16") as f:
        f.write("Partiet er overrepresentert og får ikke utjevningsmandat:\n"
                + str(ndf[ndf.Direct > ndf.asif].index) + "\n")
    ndf = ndf.drop(ndf[ndf.Direct > ndf.asif].index)
    # Adjust number of mandates to distribute
    mandates_to_asif = mandates_to_asif - too_many_mandates
with open(log_file, "a", encoding="utf-16") as f:
    f.write("\n")
ndf["Utjevning"] = ndf["asif"] - ndf["Direct"]
# print("\nParties are underrepr, should have representatives:")
# print(ndf["asif"])
# print("\nParties will get utjevning:")
ndf["Utjevning"] = ndf["Utjevning"].astype(int)
print(ndf["Utjevning"])
ndf.to_csv(f"./details/Beregning_Utjevning_{runcode}.csv")
print("\nDeler ut utjevningsmandater til partier")

# Now, calculate which party gets an evening out mandate in which district.

# Calculate fylkesfaktor

# Getting a list of the total number of votes in each fylke
plopp = df.groupby("Fylkenavn")["Antall stemmer totalt"].sum()
plopp = plopp.to_frame()
# print(plopp.info())
plopp.to_csv(f"./details/Stemmer_per_fylke_{runcode}.csv")

df["Fylkesstemmer"] = 0
# Getting the total number of votes in each fylke into the df:
for idx, row in df.iterrows():
    for ploppidx, plopprow in plopp.iterrows():
        if row["Fylkenavn"] == ploppidx:
            # print(row["Fylkenavn"], ploppidx,)
            df.loc[idx, "Fylkesstemmer"] \
                = plopp.loc[ploppidx, "Antall stemmer totalt"]

# Now, reuse that most elegant methode to get the number of direct mandates in.
df["Direktemandater fra fylket"] = 0
dirdf = df.groupby("Fylkenavn")["Direct"].sum()
dirdf = dirdf.to_frame()
# print(dirdf.info())
dirdf.to_csv(f"./details/Direct_per_fylke_{runcode}.csv")

df["Direktemandater fra fylket"] = 0
# Getting the total number of votes in each fylke into the df:
for idx, row in df.iterrows():
    for dirdfidx, dirdfrow in dirdf.iterrows():
        if row["Fylkenavn"] == dirdfidx:
            df.loc[idx, "Direktemandater fra fylket"] \
                = dirdf.loc[dirdfidx, "Direct"]

df["Fylkesfaktor"] = df["Fylkesstemmer"] / df["Direktemandater fra fylket"]

# Now, revise the number of votes:
df["Revidert stemmetall"] = df["Antall stemmer totalt"] / (2 * df.Direct + 1)
df["Utjevningstall"] = df["Revidert stemmetall"] / df["Fylkesfaktor"]

# Removing the parties which shall not get utjevning
utjevninglist = list(ndf.index.unique())
for idx, row, in df.iterrows():
    if row["Partikode"] not in utjevninglist:
        df.loc[idx, "Utjevningstall"] = 0

utjevning_left = utjevning_per_district["Antall mandater"].sum()
while(utjevning_left > 0):
    max_row = df["Utjevningstall"].idxmax()
    df.loc[max_row, "Evening"] = df.loc[max_row, "Evening"] + 1
    # Only one evening mandate per party from each fylke
    df.loc[max_row, "Utjevningstall"] -= 1
    fylke = df.loc[max_row, "Fylkenavn"]
    parti = df.loc[max_row, "Partikode"]
    with open(log_file, "a", encoding="utf-16") as f:
        f.write(f"{parti:4s} utjevning {fylke}\n")
    summary[fylke][parti] += 1
    # print(ndf["Utjevning"])

    # subtracting mandate from remaining for both the party and the fylke
    utjevning_per_district.loc[fylke, "Antall mandater"] -= 1
    ndf.loc[parti, "Utjevning"] -= 1

    # Removing the Utjevningstall for the parties and districts which have
    # had as many evening out mandates as they should.
    if utjevning_per_district.loc[fylke, "Antall mandater"] <= 0:
        # This district has distributed all mandates
        for idx, row, in df.iterrows():
            if row["Fylkenavn"] == fylke:
                # Have to subtract, not multiply by -1 because this
                # multiplication will be repeated for the parties later.
                df.loc[idx, "Utjevningstall"] -= 2

    if ndf.loc[parti, "Utjevning"] <= 0:
        # This party has had enough mandates
        for idx, row, in df.iterrows():
            if row["Partikode"] == parti:
                df.loc[idx, "Utjevningstall"] -= 4

    utjevning_left1 = utjevning_per_district["Antall mandater"].sum()
    utjevning_left2 = ndf["Utjevning"].sum()

    if utjevning_left1 == utjevning_left2:
        utjevning_left = utjevning_left1
        # print(utjevning_left)
    else:
        print("ÆSJ, har har utjevningsutregniingen gått i frø.")
        print(f"{utjevning_left1=}, {utjevning_left2=}")
        utjevning_left = -17
with open(log_file, "a", encoding="utf-16") as f:
    f.write("\n")

sum_table = pd.DataFrame(summary)
sum_table['Totalt'] = sum_table.sum(axis=1)
# print(sum_table)
# Sorting the columns, i.e. parties from left to right politically
# sum_table = sum_table.reindex(columns=left_to_right)
# print(sum_table)
# sum_table.to_csv("sum.csv")
sum_trans = sum_table.transpose()
sum_trans['Sum'] = sum_trans.sum(axis=1)
# print(sum_trans)
# Sorting the columns, i.e. parties from left to right politically
sum_trans = sum_trans[["NKP", "RØDT", "SV", "A", "RN", "MDG", "FI", "GENE",
                       "GT", "HELSE", "PIR", "PS", "BLANKE", "SP", "PF", "V",
                       "KRF", "H", "PP", "LIBS", "INP", "KYST", "FRP",
                       "KRISTNE", "FNB", "DEMN", "AAN", "Sum"]]
# Removing the parties with no mandates from summary list.
sum_trans = sum_trans.loc[:, (sum_trans.sum(axis=0) > 1)]

# mandate_string = ""

mandate_string = str(overview_mandates)
sum_trans.to_csv("./details/summary.csv")
summary_string = ""
summary = ""
with open("./details/summary.csv", "r") as f:
    summary = f.readlines()
for line in summary:
    parts = line.split(",")
    summary_string += f"{parts[0][:16]:<17}"
    for part in parts[1:-1]:
        summary_string += f"{part:>4}"
    summary_string += f"{parts[-1]:>5}"
# print(summary_string)
with open(log_file, "a", encoding="utf-16") as f:
    f.write(summary_string)

# Summing up mandates for groups of parties.
rg = sum_trans.loc["Totalt"]["RØDT"] \
    + sum_trans.loc["Totalt"]["SV"] \
    + sum_trans.loc["Totalt"]["A"] \
    + sum_trans.loc["Totalt"]["MDG"]

regj = sum_trans.loc["Totalt"]["A"] \
    + sum_trans.loc["Totalt"]["SP"]

r_sv = regj + sum_trans.loc["Totalt"]["SV"]

blueblu = sum_trans.loc["Totalt"]["H"] \
    + sum_trans.loc["Totalt"]["FRP"]

blue = blueblu + sum_trans.loc["Totalt"]["V"] \
    + sum_trans.loc["Totalt"]["KRF"]

blokk_string = f"\nRØDT + SV + A + MDG: {rg}\n"\
    + f"A + SP: {regj}\n"\
    + f"A + SP + SV: {r_sv}\n"\
    + f"V + KRF + H + FRP: {blue}\n"\
    + f"H + FRP: {blueblu}"
with open(log_file, "a", encoding="utf-16") as f:
    f.write(blokk_string)

# Save everything
df.to_csv(f"./details/df_{runcode}.csv")
ndf.to_csv(f"./details/ndf_{runcode}.csv")
with open(summary_file, 'w', encoding="utf-16") as file:
    file.write("Beregnet sammensetning av Stortinget.\n"
               + f"Sperregrense: {sperregrense}\n"
               + f"Utjevningsmandater per fylke: {evening_per_fylke}\n"
               + f"Regelversjon: {runcode}\n"
               + comment + "\n\n"
               + mandate_string + "\n\n"
               + "Representanter på Stortinget:\n"
               + summary_string
               + blokk_string)
