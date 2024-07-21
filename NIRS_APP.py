import streamlit as st

from io import StringIO
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from scipy.ndimage import gaussian_filter1d

#st.title('Hello and welcome to ')
#st.title("Hannah's NIRS app")
 



with st.sidebar:
    #st.image('NU_logo.jpg')
    st.title('NIRS APP')
    st.write('This is a small webapp designed to analyse NIRS data from portamon.')
    st.write('This can be done in the following steps.')
    st.write('1. First upload your data file.')
    st.write('2. Choose which data field you are interested in.')
    st.write('3. Analyse.')
    st.write('##')
    st.write('##')
    st.write('##')
    st.write('Designed by Hannah Wilson and developed by Ben Wilson.')

#Read in the file
uploaded_file = st.file_uploader("Choose a NIRS file")
if uploaded_file is not None:
    #Decode the file from binary to a string
    file = StringIO(uploaded_file.getvalue().decode("utf-8"))
    
    #Process the data and extract the data fields from the legend
    #Set up some variables
    headers = []
    rows = []
    Take_legend = False
    Rows_of_legend = 0
    #Run through the file
    for i, v in enumerate(file.readlines()):
        #Find the legend
        if 'Legend:' in v:
            Take_legend = True
        #Stop when at the bottom of the legend
        if Take_legend == True and Rows_of_legend > 2:
            if len(v.split('\t'))<2:
                break
        #Take the headers from the legend
        if Take_legend == True and Rows_of_legend == 1:
            headers.extend(v.split('\t'))
            headers = [i.replace('\n','') for i in headers][:2]
        #Take the rows from the legend
        elif Take_legend == True and Rows_of_legend > 1:
            temp_row = v.split('\t')
            rows.append([i.replace('\n','').replace('Rx1 - ','') for i in temp_row][:2])
        if Take_legend == True:
            Rows_of_legend += 1
            
    #st.write(headers)
    #st.write(rows)

    #Find where the data starts
    file = StringIO(uploaded_file.getvalue().decode("utf-8"))
    for i, v in enumerate(file.readlines()):
        if '1\t2\t3\t4' in v:
            Data_start = i
            break

    #Extract the data
    file = StringIO(uploaded_file.getvalue().decode("utf-8"))
    data = np.array(np.char.split(file.readlines()[Data_start+1:]))
    
    
    #Process the data removed the events
    data_removed_event = [i[:len(rows)-1] for i in data]
    new_data = np.concatenate(data_removed_event)
    #Reshape in the correct columns
    new_data = new_data.reshape(int(len(new_data)/(len(rows)-1)),len(rows)-1)
    
    #Change the headers
    df = pd.DataFrame(new_data)
    df.columns = [i[1] for i in rows][:-1]
    df = df.set_index(rows[0][1])
    
    length_raw_data = len([i[1] for i in rows])
    
    #Add the events back in
    data_event = [True if len(i) > length_raw_data-1 else False for i in data]
    df['event'] = data_event
    
    #Give an option on which data field you want to show
    data_fields = tuple(list(df.columns.values))
    option = st.selectbox("Which data field would you like to work with?",data_fields,index=len(data_fields)-3)
    
    
    #Extract and smooth the data
    x = np.arange(len(df)-2)
    y = df[option].to_numpy().astype(float)[2:]
    y = gaussian_filter1d(y, 5)
    
    #Extract events
    events = df[df['event']].index.values.tolist()
    baseline = np.median(y[:int(events[0])])
    minimum = np.min(y[int(events[-1]):])
    maximum = np.max(y[int(events[-1]):])
    #maximum = np.max(df[events[2]:]['Tx1,Tx2,Tx3 TSI% (New Measurement 4)'].to_numpy().astype(float))
    data_range = maximum-minimum
    
    #Normalise the data
    y_new = 100*(y-minimum)/data_range
    baseline = 100*(baseline-minimum)/data_range
    
    #Make the figure
    fig = px.scatter(x=np.arange(len(df)-2),y=y_new)
    for event in events:
        fig.add_vline(x=event, line_width=3, line_dash="dash", line_color="red")
    fig.add_trace(
        go.Scatter(
            x=[0,events[0]],
            y=[baseline,baseline],
            mode="lines",
            line=go.scatter.Line(color="red",width=3),
            showlegend=False))
    
    #Show the figure
    st.plotly_chart(fig, use_container_width=True)



















    
    
    
