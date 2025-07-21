import requests
import numpy as np

bcycle_url = "https://gbfs.bcycle.com"

def get_bcycle_json(name):
    url = f"{bcycle_url}/bcycle_boulder/{name}"
    response = requests.get(url)

    if response.status_code == 200:
        bcycle_data = response.json()
        return bcycle_data
    else:
        print(f"Failed to retrive data {response.status_code}")


request_names = [
    'station_information',
    'station_status'
]

station_array = np.array([0, 14, 19, 29, 34, 35, 37, 40, 42, 44, 47, 52, 53])

info_columns = [
    'lat',
    'lon',
    'name',
    'station_id'
]

status_columns = [
    'num_docks_available',
    'num_bikes_available'
]

for i in range(len(request_names)):
    bcycle_json = get_bcycle_json(request_names[i])
    if bcycle_json:
        for j in range(len(station_array)):
            if i == 0:
                for k in range(len(info_columns)):
                    print(station_array[j], "==", bcycle_json["data"]["stations"][station_array[j]][info_columns[k]])
            if i == 1:
                for k in range(len(status_columns)):
                    print(station_array[j], "==", bcycle_json["data"]["stations"][station_array[j]][status_columns[k]])

# if bcycle_json:
#     for i in range(len(station_array)):
#         for j in range(len(status_columns)):
#             print(station_array[i], "==", bcycle_json["data"]["stations"][station_array[i]][status_columns[j]])
        # print("index:", station_array[i], bcycle_info["data"]["stations"][station_array[i]]["name"])