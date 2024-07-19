import streamlit as st
from utils import PreProcesor, columns

import numpy as np
import pandas as pd
import joblib

model = joblib.load('model.joblib')
st.title('Electricity Theft Detection')

columnNumbs: list[int] = [1,2,3,4,5,6,7,8] # list of your features
columnNames: list[str] = ['2']

def show_prediction():
    row = np.array(columnNumbs)
    X = pd.DataFrame([row],columns=columnNames)
    y = model.predict(X)[0]

st.button('Predict',on_click=show_prediction)