import folium
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

dir="/home/thomas/Downloads/hackathon_2025/scat/"

Sites = pd.read_csv(f"{dir}/dcc_traffic_signals_20221130.csv")
Data = pd.read_csv(f"{dir}/SCATSMarch2025_collapsed.csv")
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
long_mile_id=767


# FIX DATA
N=len(ids)
good_ids=[]
for j in range(N):
    row=Data.loc[Data["Site"] == ids[j], "End_Time"].tolist()
    if len(row)>330:
        if j==515:         # < ------  random bad data point 
            print("")  
        else: 
            good_ids.append(ids[j])
        if j==long_mile_id:         # < ------  random bad data point 
           long_mile_good_id=len(good_ids)


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
    if j==341:
        print("here")
    else: 
        times[j,:]=np.array(row)
        volumes[j,:]=np.array(volume)
    
    


#CORRELATION MATRIX              

C=np.empty(shape=(N,N))
for i in range(len(good_ids)):
  volumes_1=volumes[i,:]
  for j in range(i,len(good_ids),1):
      volumes_2=volumes[j,:]
      # print(len(volumes),len(volumes_2))
      C[i,j] = Cov(volumes_1,volumes_2)/(std(volumes_1)*std(volumes_2))



box_width=1/100
boxs= np.arange(box_width/2,1+box_width/2,box_width)
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



# CREATE MAP
m = folium.Map(
    location=[ref_lat,ref_lon],
    zoom_start=12,
    tiles='OpenStreetMap'
)





# Add some major intersections as markers
for i in range(len(lats)):
    rad=1
    for j in range(len(one_am_sites)):
         if data_sites[i]==one_am_sites[j]:
            rad=one_am_volumes[j]/100
            if rad<1:
                rad=1
    folium.CircleMarker(
        location=[lats[i], longs[i]],
        radius=rad,
        popup=f"SiteId: {ids[i]})",
        color='red',
        fillOpacity=0.8).add_to(m) 



m.save(f"{dir}/dublin_scat_map.html")