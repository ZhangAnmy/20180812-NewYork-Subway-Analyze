
# coding: utf-8

# 事件说明：
# 文档为2011年五月纽约市所有地铁客流量与天气状况的数据。对文档中的数据进行分析，分析不同天气状况，不同时间段内，不同地铁站，客流量的情况。
# 
# 问题的提出与述求：
# 1.哪些因素影响地铁的客流量？
#   --天气(雨天/雾天)、周末、节假日。
#   --气温对客流量的影响。
# 2.哪个车站的乘客量最多？哪个最少？各车站之间客流量差异多大？
# 3.哪些时间段内地铁中的客流量最多？哪些时间段客流量最少？

# In[1]:


#数据分析与处理：
#1.加载csv文档
import pandas as pd
import numpy as np

subway_df = pd.read_csv('nyc-subway-weather.csv')


# 预览数据，主要使用info、head、describe方法大致预览加载的数据

# In[2]:


subway_df.info()


# In[3]:


subway_df.head()


# In[4]:


subway_df.describe()


# 从以上数据可以看出，文档中总共有27列，42649条数据，且每列没有数据却失的情况。

# 问题分析阶段：

# In[5]:


#计算相关性--皮尔逊积矩相关系数 NumPy 的 corrcoef() 函数可用来计算皮尔逊积矩相关系数，也简称为“相关系数”。
def correlation(x,y):
    std_x = (x - x.mean())/x.std(ddof=0)
    std_y = (y - y.mean())/y.std(ddof=0)   
    
    return (std_x * std_y).mean()


# In[6]:


#计算每小时入站人数‘ENTRIESn_hourly’与当天平均降水量‘meanprecipi’的相关性
correlation(subway_df['ENTRIESn_hourly'],subway_df['meanprecipi'])


# 结果为正数0.0356，说明每小时的入站人数与降水量成正相关，即：降水量大，入站人数多，但是值很小，说明两者的相关度不是很高。

# In[7]:


#计算每小时入站人数‘ENTRIESn_hourly’与每小时增加的乘坐地铁的人数‘ENTRIESn’的相关性
correlation(subway_df['ENTRIESn_hourly'],subway_df['ENTRIESn'])


# 结果为正数0.586，说明两者成正相关。两者的相关度较高，但相比于最大值1还有差距。

# In[23]:


entries_and_exits = pd.DataFrame({
    'ENTRIESn':subway_df['ENTRIESn'],
    'EXITSn':subway_df['EXITSn']
})


# In[16]:


#得到每小时的地铁进出人数
def get_hourly_entries_and_exits(entries_and_exits):
    hourly_entries_and_exits = entries_and_exits - entries_and_exits.shift(1)
    return hourly_entries_and_exits


# In[25]:


get_hourly_entries_and_exits(entries_and_exits)


# In[26]:


import matplotlib.pyplot as plt
import seaborn as sns


# In[34]:


#获得地铁站每天每小时的平均客流量
subway_df_data = subway_df.groupby('DATEn')
print (subway_df_data.mean()['ENTRIESn_hourly'])


# In[42]:


plt.plot(subway_df_data.mean()['ENTRIESn_hourly'])


# 从图中可以看出，平均每天每小时的客流量为1000-2400

# In[44]:


#计算一周每天的平均客流量
subway_df.groupby('day_week').mean()


# In[47]:


#计算一周每天平均每小时的客流量
ridership_by_day = subway_df.groupby('day_week').mean()['ENTRIESn_hourly']
print (ridership_by_day)


# In[48]:


ridership_by_day.plot()


# 从图中可以看出每周每天每小时的平均客流量为1000-2300，跟之前计算的每月每天每小时的平均客流量基本吻合。且day_week为5和6，即：周六周日期间，平均每小时的客流量最少。

# In[49]:


def get_diff(df):
    return df.diff()


# In[50]:


def get_hourly_entries_and_exits(entries_and_exits):
    group_data = entries_and_exits.groupby('UNIT')['ENTRIESn','EXITSn'].apply(get_diff)
    return group_data


# In[51]:


ridership_df = pd.DataFrame({
    'UNIT': subway_df['UNIT'],
    'TIMEn': subway_df['TIMEn'],
    'ENTRIESn': subway_df['ENTRIESn'],
    'EXITSn': subway_df['EXITSn']
})


# In[52]:


get_hourly_entries_and_exits(ridership_df)


# In[53]:


#获取雨天与乘客量的关系 0-不下雨 1-下雨
ridership_by_rain = subway_df.groupby('rain',as_index=False).mean()['ENTRIESn_hourly']


# In[54]:


print (ridership_by_rain)


# In[55]:


#雨天和晴天平均地铁客流量直方图
ridership_by_rain.plot(kind='bar')


# 从图中可以看出，雨天(1)地铁客流量比晴天要多。符合实际情况。

# In[67]:


#获取雾天与乘客量的关系 0-没雾 1-有雾
ridership_by_fog = subway_df.groupby('fog',as_index=False).mean()['ENTRIESn_hourly']
print (ridership_by_fog)


# In[68]:


ridership_by_fog.plot(kind='bar')


# In[103]:


#获取气温与乘客量的关系 
ridership_by_temp = subway_df.groupby('tempi',as_index=False).mean()
x_axis = ridership_by_temp['tempi']
y_axis = ridership_by_temp['ENTRIESn_hourly']


# In[87]:


plt.plot(x_axis,y_axis,color='r',markerfacecolor='blue',marker='o')


# In[56]:


#获取不同位置的平均客流量
data_by_location = subway_df.groupby(['latitude','longitude'],as_index=False).mean()


# In[59]:


data_by_location.head()['latitude']


# In[61]:


scaled_entries = data_by_location['ENTRIESn_hourly'] /data_by_location['ENTRIESn_hourly'].std()


# In[63]:


#以经纬度作为 x 和 y 轴、客流量作为气泡大小的地铁站散点图
plt.scatter(data_by_location['latitude'],data_by_location['longitude'],s=scaled_entries*3)


# 图中气泡越大的地方表明客流量越多
