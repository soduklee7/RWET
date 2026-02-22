import pandas as pd
import json

# Define the data extracted from Table 6
table6_CFR1066_1005 = {
    "Symbol": [
        "ρCH4", "ρCH3OH", "ρC2H5OH", "ρC2H4O", "ρC3H8", "ρC3H7OH", "ρCO", "ρCO2", 
        "ρHC-gas", "ρCH2O", "ρHC-liq", "ρNMHC-gas", "ρNMHC-liq", "ρNMHCE-gas", 
        "ρNMHCE-liq", "ρNOx", "ρN2O", "ρTHC-liq", "ρTHCE-liq"
    ],
    "Quantity": [
        "density of methane", "density of methanol", "C1-equivalent density of ethanol",
        "C1-equivalent density of acetaldehyde", "density of propane", "C1-equivalent density of propanol",
        "density of carbon monoxide", "density of carbon dioxide", "effective density of hydrocarbon—gaseous fuel",
        "density of formaldehyde", "effective density of hydrocarbon—liquid fuel", 
        "effective density of nonmethane hydrocarbon—gaseous fuel", "effective density of nonmethane hydrocarbon—liquid fuel",
        "effective density of nonmethane equivalent hydrocarbon—gaseous fuel", "effective density of nonmethane equivalent hydrocarbon—liquid fuel",
        "effective density of oxides of nitrogen", "density of nitrous oxide", 
        "effective density of total hydrocarbon—liquid fuel", "effective density of total equivalent hydrocarbon—liquid fuel"
    ],
    "g_per_m3": [
        "666.905", "1332.02", "957.559", "915.658", "611.035", "832.74", "1164.41", "1829.53", 
        "(see 3)", "1248.21", "576.816", "(see 3)", "576.816", "(see 3)", "576.816", "1912.5", "1829.66", "576.816", "576.816"
    ],
    "g_per_ft3": [
        "18.8847", "37.7185", "27.1151", "25.9285", "17.3026", "23.5806", "32.9725", "51.8064", 
        "(see 3)", "35.3455", "16.3336", "(see 3)", "16.3336", "(see 3)", "16.3336", "54.156", "51.8103", "16.3336", "16.3336"
    ]
}

# 1. Create the DataFrame
df = pd.DataFrame(table6_CFR1066_1005)

# 2. Save to CSV
df.to_csv("Table6_CFR1066_1005.csv", index=False)

# 3. Save to JSON
# Using 'records' orientation often makes it easier to read in web applications
df.to_json("Table6_CFR1066_1005.json", orient="records", indent=4)

print("Files saved successfully as 'Table6_CFR1066_1005.csv' and 'Table6_CFR1066_1005.json'.")