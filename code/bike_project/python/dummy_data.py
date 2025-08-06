import numpy as np
import pandas as pd 

df = pd.DataFrame(np.random.randint(0, 15, size=(100, 1)), columns = ['a'])
#df_2 = pd.DataFrame(np.random.randint(0, 15, size=(100, 1)), columns = ['b'])

print(df)

df['prev'] = df['a']
df_prev = df['prev']
df_prev_t = df_prev.T

for i in range(13):
    df_prev_t.pop(i)

df_prev = df_prev_t.T
df_prev = df_prev.reset_index(drop=True)

print(df_prev)



#print(index)
df['curr'] = df['a']

index = ((len(df['curr'])) - (13))

df_curr = df['curr']
df_curr_t = df_curr.T


for i in range(13):
    df_curr_t.pop(index + i)

df_curr = df_curr_t.T
#print (df_name.head(10))
#df_curr = df_curr.reset_index()
print(df_curr)

