# valg21

This script calculates the political composition of the Norwegian parlament
Stortinget based on the results from the national election.

The number of votes for each political party in each electorial district
(fylke) decides which parties get how many mandates from which district.

In the script it is possible to play with some of the election rules:
the number of evening out mandates in each fylke and also the sperregrense.
These are set at the top of the source file itself.

To run successfully tou need the source file and three other files:
- Download the election results from
`https://valgresultat.no/eksport-av-valgresultater?type=st&year=2021`
(party distribution, county level) and give this file as result_file.
- The list of how many (total) mandates there are
in each fylke. This file `settings/mandater.csv` should be in the repo.
- The list of how many of the mandates are evening out mandates
in each fylke. This file `settings/utjevning.csv` should be in the repo.

The script will print a very short summary to terminal, a one page summary
to file and a more detailed log to file.

The code seems to give correct results, but is only lightly quality controlled.
The code should probably be linted, but isn't.
