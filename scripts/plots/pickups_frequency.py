from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import seaborn as sns
sns.set_theme(rc={'figure.figsize':(22, 8)})

dataset = pd.read_csv('/Users/benatkinson/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/Projects/flatiron-flows/data/csv/bikeLogsAval_5min.csv')

data_columns = ['pickups_sum']
dataset['date_time'] = pd.to_datetime(dataset['date_time'])
dataset = dataset.sort_values(by='date_time')
dataset = dataset.set_index('date_time')


dataset_5min = np.log(dataset[['pickups_sum']]+1)


# dataset_30min = dataset_5min[data_columns].rolling(6, center=True).mean()

# dataset_30min_mean = dataset_5min[data_columns].resample('30min').mean()

# dataset_1day = dataset_5min[data_columns].rolling(window=288, center=True, min_periods=288).mean()
# dataset_reset = dataset_30min_mean.reset_index()

dataset_5min['Weekday Name'] = dataset_5min.index.weekday
dataset_5min['Hour'] = dataset_5min.index.hour
dataset_5min['Hour'].astype(int)
dataset_5min['Weekday Name'].astype(int)


dataset_30min = dataset_5min[data_columns].rolling(6, center=True).mean()

dataset_30min_mean = dataset_5min[data_columns].resample('30min').mean()

dataset_1day = dataset_5min[data_columns].rolling(window=288, center=True, min_periods=288).mean()
print(dataset)
# print(dataset_30min_mean)

start, end = '2025-10-05', '2025-10-15'

fig, ax = plt.subplots()

ax.plot(dataset_5min.loc[start:end, 'pickups_sum'],
marker='.', linestyle='-', linewidth=0.5, label='5min')

ax.plot(dataset_30min.loc[start:end, 'pickups_sum'],
marker='.', linestyle='-', label='30min Rolling Mean')

ax.plot(dataset_30min_mean.loc[start:end, 'pickups_sum'],
marker='o', markersize=6, linestyle='-', label='30min Mean Resample')

ax.set_ylabel('log(pickups_sum +1)')
ax.legend()

# plt.show()

fig, ax = plt.subplots()
ax.plot(dataset_30min['pickups_sum'], linewidth=2, label='30min Rolling Mean')
ax.plot(dataset_1day['pickups_sum'], color='0.2', linewidth=3,
label='Trend (1-d Rolling Mean)')
ax.plot(dataset_5min['pickups_sum'], marker='.', markersize=2, color='0.6',
linestyle='None', label='5min')

ax.legend()
ax.set_xlabel('Date')
ax.set_ylabel('log(pickups_sum +1)')
ax.set_title('Trends in BCycle Pickups')

plt.savefig('pickup_trends.png')
plt.show()
