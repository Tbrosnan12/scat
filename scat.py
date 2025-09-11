import folium
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import branca.colormap as cm
import math

dir="/home/thomas/Downloads/hackathon_2025/scat/"

Sites = pd.read_csv(f"{dir}/dcc_traffic_signals_20221130.csv")
Data = pd.read_csv(f"{dir}/SCATSNovember2023_collapsed.csv")
ids=Sites["SiteID"]
lats = Sites["Lat"]
longs = Sites["Long"]


data_sites=Data["Site"]
data_vol=Data["Sum_Volume"]
times=Data["End_Time"]

# ROUGH DUBLIN CO-ORDS
ref_lat=53.348754
ref_lon=-6.257607


# CORRELATION MATRIX
def mean(x): 
    N=len(x)
    return (1/N)*sum(x)

def Cov(x,y):
    N=len(x)
    covariance = 0 
    x_bar = mean(x)
    y_bar = mean(y)
    for i in range(len(x)):
            covariance += (x[i]-x_bar)*(y[i]-y_bar)
            #print(covariance)
    return covariance*1/N    

def std(x):
     return np.sqrt(mean(x**2)-mean(x)**2) 


# Long Mile Road
#long_mile_id=379

long_mile_good_id=219
# FIX DATA


N=len(ids)
good_ids=[]
for j in range(N):
    row=Data.loc[Data["Site"] == ids[j], "End_Time"].tolist()
    volume=Data.loc[Data["Site"] == ids[j], "Sum_Volume"].tolist()
    if all(v == 0 for v in volume):   # remove the null detectors
        continue
    if len(row)>650:
        # if j==515:         # < ------  random bad data point 
        #    print("")  
        #else: 
        good_ids.append(ids[j])
        #if j==long_mile_id:         
         #   long_mile_good_id=len(good_ids)

N=len(good_ids)
ref=np.array(Data.loc[Data["Site"] == 2, "End_Time"].tolist())
times=np.zeros(shape=(N,len(ref)))
volumes=np.zeros(shape=(N,len(ref)))
for j in range(N):
    row=Data.loc[Data["Site"] == good_ids[j], "End_Time"].tolist()
    volume=Data.loc[Data["Site"] == good_ids[j], "Sum_Volume"].tolist()
    if len(row)!=len(ref):
        for i in range(len(ref)):
            if i==(len(row)):
                row.append(ref[i])
                if i==0:
                    volume.append(0)
                else:
                    volume.append(volume[i-1])
            elif row[i]!=ref[i]:
                row.insert(i,ref[i])
                if i==0:
                    volume.insert(i,volume[i+1])
                else:
                    volume.insert(i,(volume[i-1]+volume[i+1])/2)
    times[j,:]=np.array(row)
    volumes[j,:]=np.array(volume)
    
    


#CORRELATION MATRIX              
count=0
C = np.zeros(shape=(N, N))
for i in range(len(good_ids)):
    volumes_1 = volumes[i, :]
    std1 = np.std(volumes_1)
    for j in range(i, len(good_ids)):
        volumes_2 = volumes[j, :]
        std2 = np.std(volumes_2)

        denom = std1 * std2
        if denom == 0:
            print(volumes_2)
            count+=1
            C[i, j] = 0.0
        else:
            C[i, j] = Cov(volumes_1, volumes_2) / denom

print(count)

box_width=1/100
boxs= np.arange(box_width/2-1,1+box_width/2,box_width)
freq=np.zeros(len(boxs))

for i in range(len(C)):
    for j in range(i, len(C)):
        for index,box_val in enumerate(boxs):
            if (box_val-box_width/2)<=C[i,j]<(box_val+box_width/2):
                freq[index]+=1
plt.figure()
plt.bar(boxs,freq,width=box_width)
#plt.plot(boxs,freq,'o',markersize='0.1')
plt.show()


# DISTANCE MATRIX
D=np.sqrt(0.5*(1-C))



#DISTANCE FORMULA
import math

def distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth 
    given their latitude and longitude in decimal degrees.

    Parameters:
        lat1, lon1 : float - Latitude and Longitude of point 1
        lat2, lon2 : float - Latitude and Longitude of point 2

    Returns:
        distance in kilometers (float)
    """
    # Radius of Earth in kilometers
    R = 6371.0

    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c





# COLOURS
start_color = 100  # less blue
end_color   = 255  # blue

def value_to_rgb(val, gamma=4.0):
    """Nonlinear blue gradient stretching values near 1"""
    if math.isnan(val):
        return "rgb(0,0,0)"  # gray for NaNs
    
    # Normalize val ∈ [-1,1] → v ∈ [0,1]
    v = (val + 1) / 2  
    
    # Apply gamma correction (keeps 0 → 0 and 1 → 1)
    v = v**gamma  
    
    # Interpolate between start and end color
    rgb = (1 - v) * start_color + v * end_color
    return f"rgb(0,0,{int(rgb)})"



# CREATE MAP
m = folium.Map(
    location=[ref_lat,ref_lon],
    zoom_start=12,
    tiles='OpenStreetMap'
)



# ADD SITE MARKERS
for i in range(len(good_ids)):
    color = value_to_rgb(C[i,long_mile_good_id])
    if i==long_mile_good_id:
        color='red'
    for j in range(len(ids)):
        if good_ids[i]==ids[j]:
            id_index=j
    folium.CircleMarker(
        location=[lats[id_index], longs[id_index]],
        radius=4,
        popup=f"Correlation: {C[i,long_mile_good_id]},id_No: {i}",
        color=color,
        fillOpacity=0.8).add_to(m) 



m.save(f"{dir}/dublin_scat_map.html")