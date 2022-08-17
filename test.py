import pandas as pd

df1=pd.DataFrame({'A':[1,2,3,3],'B':[2,3,4,4]})
df2=pd.DataFrame({'A':[1],'B':[2]})
df1.index.name = 'key'
df2.index.name = 'key'

print(pd.concat([df1, df2]).drop_duplicates(keep=False))

