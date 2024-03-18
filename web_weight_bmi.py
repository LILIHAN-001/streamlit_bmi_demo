import numpy as np
import pandas as pd
import streamlit as st
from sklearn import preprocessing
import pickle
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 函数 # 
# 计算BMI
def bmi(height, weight):  
    bmi_value = float(weight) / (float(height) / 100) ** 2
    bmi_value = round(bmi_value, 2)
    top_status = [(14.9, '极瘦'), (18.5, '偏瘦'),
                  (25.0, '正常'), (30.0, '过重'),
                  (40.0, '肥胖'), (float('inf'), '非常肥胖')]

    for top, status in top_status:
        if bmi_value <= top:
            return bmi_value, status
      
# Pie plot
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.charts import Gauge

def draw_chart_gauge(bmi):
    c = (
        Gauge()
        .add(
            '',
            [("your BMI is ", bmi)],start_angle=180,end_angle=0,
            min_=0,max_= 50 ,
            split_number=10,
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(
                    color = [(0.149 / ( 50 / 100) , "#0000CD"),
                             (0.185 / ( 50 / 100) , "#4169E1"),
                             (0.250 / ( 50 / 100) , '#7CFC00'),
                             (0.300 / ( 50 / 100) , '#fd666d'),
                             (0.400  / ( 50 / 100) , '#EE82EE'), 
                             (1 , "#FF1493")] , 
                    width=15
                )          
            ),
            detail_label_opts=opts.LabelOpts(formatter="{value}")
        )
        .set_global_opts(
            #title_opts=opts.TitleOpts(title="BMI"),
            legend_opts=opts.LegendOpts(is_show=False)
            )
    )
    return c
    
#df_bak = pd.DataFrame(columns = ["Name", "Date", "Height (cm)", "Weight (kg)", "BMI"])
#df_bak.to_csv("./data/df_bak.csv",index=False)

# 标题制作 #
t1, t2 = st.columns((2,1)) 
t1.title("KEEP YOUR HEALTHLY")
t2.image('./images/images.jpg', width = 120)

# input #
with st.container():
    st.header("INPUT")
    name = st.text_input("Name","hanl")
    current_time = datetime.now()
    current_time = current_time.strftime("%Y-%m-%d %H:%M")
    date = st.text_input("Date",current_time)
    import datetime as dt
    date = dt.datetime.strptime(date, "%Y-%m-%d %H:%M")
#    st.write(type(date))
    l1c3, l1c4  = st.columns((1,1))
    with l1c3: 
        height = st.text_input("Height (cm)","167")
  
    with l1c4:
        weight = st.text_input("Weight (kg)","50")

# 数据保存 # 
if st.button("Submit"):

    BMI = float(bmi(height, weight)[0])
    new_row = [name, date, height, float(weight), float(BMI)]
    df_bak_add = pd.read_csv("./data/df_bak.csv")
    df_bak_add.loc[len(df_bak_add.index)] = new_row
    df_bak_add = df_bak_add.drop_duplicates()

    df_bak_add.to_csv("./data/df_bak.csv",index=False)
 
    st.header("\nBMI calulation")
    from pyecharts.render import make_snapshot
    from snapshot_selenium import snapshot as driver
    bmi_chart = draw_chart_gauge(BMI)
    bmi_chart.render("bmi_chart.html")
    with open("bmi_chart.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    st.components.v1.html(html_content, width=700, height=380)

    # BMI table
    df_bmi_ref = pd.read_csv("./data/BMI_REF.csv", encoding="gbk")
    df_bmi_ref.reset_index(drop=True, inplace=True)
    #st.dataframe(df_bmi_ref)
    fig = go.Figure(
                data = [go.Table (columnorder = [0,1], columnwidth = [10,10],
                    header = dict(
                     values = list(df_bmi_ref.columns),
                     font=dict(size=16, color = 'white'),
                     fill_color = '#264653',
                     line_color = '#264653', #'rgba(255,255,255,0.2)',
                     align = ['left','center'],
                     #text wrapping
                     height=30
                     )
                  , cells = dict(
                      values = [df_bmi_ref[K].tolist() for K in df_bmi_ref.columns], 
                      font=dict(size=16),
                      align = ['left','center'], 
                      line_color = '#264653', #'rgba(255,255,255,0.2)',
                      height=30))])
    #st.subheader("BMI释义")
    fig.update_layout(title_text="BMI释义",title_font_color = '#264653',font=dict(size=40),margin= dict(l=0,r=10,b=10,t=30), height=350)
    st.plotly_chart(fig, use_container_width=True)

    # line plot #
    st.header("\nLine chart")
    tmp_df = df_bak_add[df_bak_add["Name"]==name]
#    tmp_df = tmp_df.sort_values(["Date"])
#    tmp_df['Date'] = pd.to_datetime(tmp_df['Date'], format='%Y-%m-%d %H:%M')

    df_ = tmp_df[["Name","Date","Weight (kg)"]].copy()
    df_.columns = ["Name","Date_One_Month_Ago","Weight_One_Month_Ago"]

    df_stat = tmp_df
    df_stat['Weight_Diff_lastrecord'] = df_stat.groupby('Name')['Weight (kg)'].diff()

 #   df_stat['Date_One_Month_Ago'] = df_stat['Date'] - pd.DateOffset(months=1)
 #   df_stat = pd.merge(df_stat,df_,how="left",on = ["Name","Date_One_Month_Ago"])
 #   df_stat["Weight_Diff_lastmonth"] = df_stat["Weight (kg)"] - df_stat["Weight_One_Month_Ago"]
 #   df_stat = df_stat[['Name', 'Date', 'Weight (kg)', 'Weight_Diff_lastrecord','Weight_Diff_lastmonth']]

    m1, m2, m3, m4, m5 = st.columns((1,1,5,1,1))
    m1.write('')
    m3.metric(label ='当前体重：',value = str(df_stat['Weight (kg)'].iloc[-1]) + " kg", delta = str(df_stat['Weight_Diff_lastrecord'].iloc[-1])+' 相较于上次记录', delta_color = 'inverse')
#    m4.metric(label ='相较于上个月：',value = str(df_stat['Weight_Diff_lastmonth'])+" kg", delta = str(df_stat['Weight_Diff_lastmonth']), delta_color = 'inverse')
    m1.write('')

    with st.container():
        l2c1, l2c2 = st.columns((2,2))
        with l2c1:
            fig = px.line(tmp_df, x = 'Date', y='Weight (kg)', template = 'seaborn', line_shape='spline', markers=True)
       #     fig.update_traces(marker_color='#7A9E9F')
            fig.update_layout(title_text="Weight (kg)",title_x=0,margin= dict(l=0,r=10,b=10,t=30), yaxis_title=None, xaxis_title=None)
            l2c1.plotly_chart(fig, use_container_width=True)
        with l2c2:
            fig = px.line(tmp_df, x = 'Date', y='BMI',template = 'seaborn', line_shape='spline',markers=True)
          #  fig.update_traces(marker_color='#7A9E9F')
            fig.update_layout(title_text="BMI",title_x=0,margin= dict(l=0,r=10,b=10,t=30), yaxis_title=None, xaxis_title=None)
            l2c2.plotly_chart(fig, use_container_width=True)

    # dataframe
    st.header("\nTable")
    with st.expander("Table"):
        name_df = st.multiselect("Name：",df_bak_add.Name.unique().tolist(),df_bak_add.Name.unique().tolist())
        tmp_df = df_bak_add[df_bak_add["Name"]==name]
#        tmp_df = tmp_df.sort_values(["Date"],ascending=False)
           
        fig = go.Figure(
                    data = [go.Table (columnorder = [0,1,2,3,4], columnwidth = [10,10,10,10,10],
                        header = dict(
                         values = list(tmp_df.columns),
                     font=dict(size=15, color = 'white'),
                     fill_color = '#264653',
                     line_color = 'rgba(255,255,255,0.2)',
                     align = ['left','center'],
                     height=30
                     )
                  , cells = dict(
                      values = [tmp_df[K].tolist() for K in tmp_df.columns], 
                      font=dict(size=15),
                      align = ['left','center'],
                      line_color = 'rgba(255,255,255,0.2)',
                      height=30))]) 
        fig.update_layout(title_text="",title_font_color = '#264653',title_x=0,margin= dict(l=0,r=10,b=10,t=30), height=280) 
        st.plotly_chart(fig, use_container_width=True)

# contact us
st.header("\nContact us")
with st.expander("Contact us"):
    with st.form(key='contact', clear_on_submit=True):
        email = st.text_input('Contact Email')
        st.text_area("Query","Please fill in all the information or we may not be able to process your request")   
        submit_button = st.form_submit_button(label='Send Information')	
