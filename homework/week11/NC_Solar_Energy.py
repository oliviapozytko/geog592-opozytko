#!/usr/bin/env python
# coding: utf-8

# In[25]:


import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse
from matplotlib.backends.backend_pdf import PdfPages


# In[26]:


solar_land_share = 0.01        # 1% of each county's land
solar_mw_per_km2 = 35          # illustrative solar capacity density (MW/km²)
capacity_factor = 0.20        # illustrative annual fraction of full output
hours_per_year= 8760

# Choose a few counties while testing; set to None to make pages for all 100.
COUNTIES_TO_REPORT = ["Alamance", "Durham", "Orange", "Wake"]

assert 0 <= solar_land_share <= 1
assert solar_mw_per_km2 > 0
assert 0 <= capacity_factor <= 1


# In[27]:


url_0 = "https://www2.census.gov/geo/tiger/GENZ2024/shp/"
url_county = "cb_2024_us_county_500k.zip"
url_state = "cb_2024_us_state_500k.zip"  

counties = gpd.read_file(url_0 + url_county)
nc_counties = counties.loc[counties["STATEFP"] == "37"].to_crs(6543).copy()
nc_counties = nc_counties.sort_values("NAME").reset_index(drop=True)

#Used AI to find solar estimates use Census ALAND, which is expressed in square meters.
nc_counties["land_km2"] = nc_counties["ALAND"] / 1_000_000
nc_counties["solar_km2"] = nc_counties["land_km2"] * solar_land_share
nc_counties["solar_mw"] = nc_counties["solar_km2"] * solar_mw_per_km2
nc_counties["annual_mwh"] = nc_counties["solar_mw"] * hours_per_year* capacity_factor


# In[28]:


#kept your original code 
def county_map(county, ax):
    selected = nc_counties[nc_counties["NAME"] == county]
    selected.plot(ax=ax, edgecolor="black", facecolor="#7b9b90")
    ax.set_axis_off()


def locator_map(county, ax):
    selected = nc_counties[nc_counties["NAME"] == county]
    nc_counties.plot(ax=ax, edgecolor="gray", facecolor="white")
    selected.plot(ax=ax, edgecolor="black", facecolor="#7b9b90")
    ax.set_axis_off()


# In[29]:


def county_pie(county, ax):
    selected = nc_counties[nc_counties["NAME"] == county]

    land = selected["land_km2"].iloc[0]
    solar_land = selected["solar_km2"].iloc[0]
    other_land = land - solar_land

    ax.pie(
        [solar_land, other_land],
        labels=["Solar scenario", "Other land"],
        colors=["gold", "olivedrab"],
        autopct="%.1f%%",
        startangle=90
    )

    ax.set_title("Hypothetical solar land use")


# In[30]:


#making a pie chart to find land for solar vs all other land 

def county_pie(county, ax):
    selected = nc_counties[nc_counties["NAME"] == county]

    land = selected["land_km2"].iloc[0]
    solar_land = selected["solar_km2"].iloc[0]
    other_land = land - solar_land

    ax.pie(
        [solar_land, other_land],
        labels=["Solar scenario", "Other land"],
        colors=["gold", "olivedrab"],
        autopct="%.1f%%",
        startangle=90
    )

    ax.set_title("Hypothetical solar land use")


# In[31]:


# reused most code, i changed the land/water metrics with solar scenarios
def county_info(county, ax):
    selected = nc_counties[nc_counties["NAME"] == county]

    solar_area = selected["solar_km2"].iloc[0]
    solar_capacity = selected["solar_mw"].iloc[0]
    annual_energy = selected["annual_mwh"].iloc[0]


    mountain = Polygon(
        [(0.02, 0.60), (0.09, 0.80), (0.14, 0.69),
         (0.19, 0.76), (0.25, 0.60)],
        facecolor="olivedrab",
        transform=ax.transAxes
    )
    ax.add_patch(mountain)


    sun = Ellipse(
        (0.13, 0.30), width=0.15, height=0.15,
        facecolor="gold", transform=ax.transAxes
    )
    ax.add_patch(sun)

    ax.text(
        0.32, 0.80,
        f"SOLAR LAND SCENARIO\n{solar_area:,.2f} km²\n"
        f"({solar_land_share:.0%} of county land)",
        transform=ax.transAxes, fontsize=12,
        color="olivedrab", va="top"
    )

    ax.text(
        0.32, 0.40,
        f"ESTIMATED CAPACITY\n{solar_capacity:,.0f} MW\n"
        f"ANNUAL ENERGY\n{annual_energy:,.0f} MWh",
        transform=ax.transAxes, fontsize=12,
        color="darkgoldenrod", va="top"
    )

    ax.set_axis_off()


# In[32]:


#reused your code
def county_figure(county, pdf):

    fig = plt.figure(figsize=(12, 8))

    ax_county = fig.add_axes([0.05, 0.23, 0.55, 0.54])
    ax_locator = fig.add_axes([0.05, 0.08, 0.25, 0.12])
    ax_pie = fig.add_axes([0.65, 0.48, 0.30, 0.30])
    ax_info = fig.add_axes([0.65, 0.12, 0.30, 0.32])

    county_map(county, ax_county)
    locator_map(county, ax_locator)
    county_pie(county, ax_pie)
    county_info(county, ax_info)

    fig.text(0.05, 0.94, "NORTH CAROLINA / County Solar Energy Potential Atlas",
             fontsize=10, color="olivedrab")
    fig.text(0.05, 0.87, f"{county} County", fontsize=28, fontweight="bold")

    fig.text(0.05, 0.03,
             "Source: U.S. Census Bureau (ALAND) | Scenario, not measured solar potential",
             fontsize=8, color="gray")
    fig.text(0.05, 0.005,
             f"Assumptions: {solar_land_share:.0%} of land; {solar_mw_per_km2:g} MW/km²; "
             f"{capacity_factor:.0%} capacity factor",
             fontsize=8, color="gray")

    pdf.savefig(fig)
    plt.close(fig)


# In[ ]:





# In[ ]:


if COUNTIES_TO_REPORT is None:
    selected_counties = list(nc_counties["NAME"])
else:
    selected_counties = list(COUNTIES_TO_REPORT)
    unknown = sorted(set(selected_counties) - set(nc_counties["NAME"]))
    if unknown:
        raise ValueError(f"Unknown NC county name(s): {unknown}")

with PdfPages("NC_County_Solar_Atlas.pdf") as pdf:
    for county in selected_counties:
        county_figure(county, pdf)

# Additional usable tabular output.
nc_counties.loc[nc_counties["NAME"].isin(selected_counties),
                ["NAME", "land_km2", "solar_km2", "solar_mw", "annual_mwh"]].to_csv(
    "NC_County_Solar_Estimates.csv", index=False
)
print(f"Saved {len(selected_counties)} atlas pages and a CSV of scenario estimates.")


# In[44]:


import nbformat
from nbconvert import PythonExporter

notebook_file = "homework11.ipynb"

exporter = PythonExporter()

code, resources = exporter.from_filename(notebook_file)

with open("NC_Solar_Energy.py", "w", encoding="utf-8") as file:
    file.write(code)

print("Python script created !")

