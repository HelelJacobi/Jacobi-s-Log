#Recomendations

#defining parameters

# For MSAVI:

# {Lower limit} to 0.2 – Value 1
# 0.2 to 0.4 – Value 2
# 0.4 to 0.6 – Value 3
# 0.6 to {Upper limit} – Value 4

# For NDVI:

#   {Lower limit} to 0.1 – Value 1
# 	0.1 to 0.2 – Value 2
# 	0.2 to 0.3 – Value 3
# 	0.3 to {Upper limit} – Value 4

# For NDMI:

#  {Lower limit} to 0 – Value 1
# 	0 to 0.2 – Value 2
# 	0.2 to 0.4 – Value 3
# 	0.4 to {Upper limit} – Value 4

#ledgend

#NVDI

# 1.Excellent Crop Condition:
# Description: Thriving with optimal growth and vitality. They exhibit strong and uniform development, excellent leaf coverage, and are free from pests and diseases.
# Indicators: Healthy green foliage, uniform growth, high crop density, no signs of stress, and absence of pests or diseases.
# 2.Good Crop Condition:
# Description: Generally healthy and growing well, but there may be some minor issues or variations in growth. Overall, they are productive and have the potential for a successful harvest.
# Indicators: Satisfactory growth, moderate uniformity, minimal signs of stress, and effective management of minor issues such as pests or nutrient deficiencies.
# 3.Fair Crop Condition:
# Description: May exhibit noticeable stress or challenges that affect their development. There might be some areas of slower growth, signs of pests or diseases, or other factors impacting overall crop health.
# Indicators: Visible stress, uneven growth, presence of pests or diseases that require management, and moderate impact on overall crop productivity.
# 4.Poor Crop Condition:
# Description: Crops are struggling and face significant challenges that hinder their growth and productivity. This may include severe pest infestations, diseases, nutrient deficiencies, or adverse environmental conditions.
# Indicators: Severe stress, stunted or distorted growth, widespread presence of pests or diseases, and a substantial negative impact on crop yield and quality.

#NDMI

#1.Optimal Soil Moisture:
# Description: Soil moisture is at an ideal level for plant growth and development. There is sufficient water for crops, promoting healthy root systems and robust vegetation.
# Indicators: Soil feels moist but not waterlogged, and crops show no signs of water stress.
# 2.Adequate Soil Moisture:
# Description: Soil moisture is sufficient for crop growth, but it may not be at the optimal level. Crops are adequately supplied with water, and growth is generally good.
# Indicators: Soil feels moderately moist, and crops are growing well without signs of wilting.
# 3.Moderate Soil Moisture Stress:
# Description: Soil moisture is becoming limiting, and crops may experience stress. There is a need for additional irrigation to maintain optimal growth.
# Indicators: Soil is drying out, and crops may show signs of wilting or stress, especially during the hottest parts of the day.
# 4.Severe Soil Moisture Stress:
# Description: Soil moisture is critically low, significantly impacting crop growth. Crops are under severe water stress, and there is an urgent need for irrigation or rainfall.
# Indicators: Soil is dry, crops are visibly stressed, leaves may curl or droop, and there is a risk of yield reduction.

#Input data

MSAVI=float(input("Please input MSAVI value: "))
print("   ")
NDRE=float(input("Please input NDRE value: "))
print("   ")
NDMI=float(input("Please input NDMI value: "))

#Runtime stacking blocker

ndre_value=0
nvdi_value=0
ndmi_value=0
msavi_value=0

#If statements

print("   ")
print("Recomendations are as follows: ")
print("   ")

#Template

# if Index <= 0.1:index_value=1
# elif (Index > 0.1)and(Index < 0.2):index_value=2
# elif (Index >= 0.2)and(Index < 0.3):index_value=3
# elif (Index >= 0.3)and(Index <= 1.0):index_value=4
# else :print("Invalid Index input.")
#print("  ")
# if index_value == 0:print("Index input not registered.")
# elif index_value == 1:print("Recommendation 1")
# elif index_value == 2:print("Recommendation 2")
# elif index_value == 3:print("Recommendation 3")
# elif index_value == 4:print("Recommendation 4")
# else :print("Could not obtain recommendation from index.")

#MSAVI

if (MSAVI >= -1.0)and(MSAVI <= 0.2):msavi_value=1
elif (MSAVI > 0.2)and(MSAVI <= 0.4):msavi_value=2
elif (MSAVI > 0.4)and(MSAVI <= 0.6):msavi_value=3
elif (MSAVI > 0.6)and(MSAVI <= 1.0):msavi_value=4
else :print("Invalid MSAVI input.")
print(" Crop development reading:  ")
if msavi_value == 0:print("MSAVI input not registered.")
elif msavi_value == 1:print("Bare soil: Minimal crop detection.")
elif msavi_value == 2:print("Germination stage: Seedling detection.")
elif msavi_value == 3:print("Leaf developmant stage detected.")
elif msavi_value == 4:print("NVDI suited for further analysis.")
else :print("Could not obtain recommendation for MSVAI, attention required !!!")

print("   ")

#NVDI

while msavi_value == 4:
    NVDI=float(input("Please input NVDI value: "))
    print("   ")
    if (NVDI >= -1.0)and(NVDI <= 0.1):nvdi_value=1
    elif (NVDI > 0.1)and(NVDI <= 0.2):nvdi_value=2
    elif (NVDI > 0.2)and(NVDI <= 0.3):nvdi_value=3
    elif (NVDI > 0.3)and(NVDI <= 1.0):nvdi_value=4
    else :print("Invalid NDVI input.")
    print(" Moisture reading recommends:  ")
    if nvdi_value == 0:print("NDVI input not registered.")
    elif nvdi_value == 1:print("Conduct a thorough assessment to identify and address major stressors.Implement immediate interventions to manage pests, diseases, or nutrient deficiencies.Adjust irrigation practices to alleviate stress.Seek assistance from agricultural experts or extension services for specialized guidance.")
    elif nvdi_value == 2:print("Conduct a detailed analysis to identify specific stress factors.Implement pest and disease management strategies promptly.Adjust irrigation and fertilization plans based on observed deficiencies.Consider using crop protection products judiciously.")
    elif nvdi_value == 3:print("Continue regular monitoring but pay attention to minor issues.Implement measures for improving uniformity in growth.Consider optimizing fertilization and irrigation schedules.")
    elif nvdi_value == 4:print("Continue with regular monitoring and maintenance practices.Implement precision agriculture techniques for optimal resource utilization.Ensure proper irrigation, fertilization, and pest control practices.")
    else :print("Could not obtain recommendation for NVDI, attention required !!!")
    break
else :print("NVDI not necessary.")

print("   ")

#NRDE

if NDRE <= 0.2:ndre_value=1
elif (NDRE > 0.2)and(NDRE <= 0.6):ndre_value=2
elif (NDRE > 0.6)and(NDRE <= 1.0):ndre_value=3
else :print("Invalid NDRE input.")
print(" Yeild reading: ")
if ndre_value == 0:print("NDRE input not registered.")
elif ndre_value == 1:print("Bare soil/ developing crop")
elif ndre_value == 2:print("Unhealthy/ Not mature")
elif ndre_value == 3:print("Healthy, mature. ripening")
else :print("Could not obtain recommendation from NDRE.")

#NDMI

if (NDMI >= -1.0)and(NDMI <= -0.8):ndmi_value=1
elif (NDMI > -0.8)and(NDMI <= -0.6):ndmi_value=2
elif (NDMI > -0.6)and(NDMI <= -0.4):ndmi_value=3
elif (NDMI > -0.4)and(NDMI <= -0.2):ndmi_value=4
elif (NDMI > -0.2)and(NDMI <= 0.0):ndmi_value=5
elif (NDMI > 0.0)and(NDMI <= 0.2):ndmi_value=6
elif (NDMI > 0.2)and(NDMI <= 0.4):ndmi_value=7
elif (NDMI > 0.4)and(NDMI <= 0.6):ndmi_value=8
elif (NDMI > 0.6)and(NDMI <= 0.8):ndmi_value=9
elif (NDMI > 0.8)and(NDMI <= 1.0):ndmi_value=10
else :print("Invalid NDMI input.")
print("  Vegetation water content reading: ")
if ndmi_value == 0:print("NDMI input not registered.")
elif ndmi_value == 1:print("Bare, lack of vegetation.")
elif ndmi_value == 2:print("Almost absent canopy cover.")
elif ndmi_value == 3:print("Very low canopy cover.")
elif ndmi_value == 4:print("If low canopy cover, dry.")
elif ndmi_value == 5:print("If mid-low canopy cover, high water stress; if low canopy cover, low water stress.")
elif ndmi_value == 6:print("If average canopy cover, high water stress; if mid-low canopy cover, low water stress.")
elif ndmi_value == 7:print("If mid-high canopy cover, high water stress; if average canopy cover, low water stress.")
elif ndmi_value == 8:print("If high canopy cover, no water stress.")
elif ndmi_value == 9:print("If very high canopy cover, no water stress.")
elif ndmi_value == 10:print("If total canopy cover, no water stress/waterlogging.")
else :print("Could not obtain recommendation for NDMI, attention required !!!")

print("   ")
