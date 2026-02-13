from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sklearn.preprocessing import LabelEncoder
import pickle
import joblib
from typing import Optional

from pydantic import BaseModel
app = FastAPI()


cat_feats=['NAME_CONTRACT_TYPE', 'CODE_GENDER', 'FLAG_OWN_CAR', 'FLAG_OWN_REALTY',
       'NAME_TYPE_SUITE', 'NAME_INCOME_TYPE', 'NAME_EDUCATION_TYPE',
       'NAME_FAMILY_STATUS', 'NAME_HOUSING_TYPE', 'OCCUPATION_TYPE',
       'WEEKDAY_APPR_PROCESS_START', 'ORGANIZATION_TYPE', 'FONDKAPREMONT_MODE',
       'HOUSETYPE_MODE', 'WALLSMATERIAL_MODE', 'EMERGENCYSTATE_MODE']

def label_encoder(input_df,categorical_feats):
    # categorical_feats = input_df.select_dtypes('object').columns
    for feat in categorical_feats:
        encoder = LabelEncoder()
        input_df[feat] = encoder.fit_transform(input_df[feat].fillna('NULL'))

    return input_df

model=joblib.load('credit_model.pkl')

 
class LoadInput(BaseModel):

    # ID
    SK_ID_CURR: int

    # Categorical basic
    NAME_CONTRACT_TYPE: str
    CODE_GENDER: str
    FLAG_OWN_CAR: str
    FLAG_OWN_REALTY: str

    # Family
    CNT_CHILDREN: int
    CNT_FAM_MEMBERS: Optional[float] = None

    # Financial
    AMT_INCOME_TOTAL: float
    AMT_CREDIT: float
    AMT_ANNUITY: Optional[float] = None
    AMT_GOODS_PRICE: Optional[float] = None

    # Demographics
    NAME_TYPE_SUITE: Optional[str] = None
    NAME_INCOME_TYPE: str
    NAME_EDUCATION_TYPE: str
    NAME_FAMILY_STATUS: str
    NAME_HOUSING_TYPE: str

    REGION_POPULATION_RELATIVE: float

    DAYS_BIRTH: int
    DAYS_EMPLOYED: int
    DAYS_REGISTRATION: Optional[float] = None
    DAYS_ID_PUBLISH: int

    OWN_CAR_AGE: Optional[float] = None

    # Flags
    FLAG_MOBIL: int
    FLAG_EMP_PHONE: int
    FLAG_WORK_PHONE: int
    FLAG_CONT_MOBILE: int
    FLAG_PHONE: int
    FLAG_EMAIL: int

    OCCUPATION_TYPE: Optional[str] = None

    REGION_RATING_CLIENT: int
    REGION_RATING_CLIENT_W_CITY: int

    WEEKDAY_APPR_PROCESS_START: str
    HOUR_APPR_PROCESS_START: int

    REG_REGION_NOT_LIVE_REGION: int
    REG_REGION_NOT_WORK_REGION: int
    LIVE_REGION_NOT_WORK_REGION: int
    REG_CITY_NOT_LIVE_CITY: int
    REG_CITY_NOT_WORK_CITY: int
    LIVE_CITY_NOT_WORK_CITY: int

    ORGANIZATION_TYPE: str

    # External scores
    EXT_SOURCE_1: Optional[float] = None
    EXT_SOURCE_2: Optional[float] = None
    EXT_SOURCE_3: Optional[float] = None

    # Social circle
    OBS_30_CNT_SOCIAL_CIRCLE: Optional[float] = None
    DEF_30_CNT_SOCIAL_CIRCLE: Optional[float] = None
    OBS_60_CNT_SOCIAL_CIRCLE: Optional[float] = None
    DEF_60_CNT_SOCIAL_CIRCLE: Optional[float] = None

    DAYS_LAST_PHONE_CHANGE: Optional[float] = None

    # Credit bureau requests
    AMT_REQ_CREDIT_BUREAU_HOUR: Optional[float] = None
    AMT_REQ_CREDIT_BUREAU_DAY: Optional[float] = None
    AMT_REQ_CREDIT_BUREAU_WEEK: Optional[float] = None
    AMT_REQ_CREDIT_BUREAU_MON: Optional[float] = None
    AMT_REQ_CREDIT_BUREAU_QRT: Optional[float] = None
    AMT_REQ_CREDIT_BUREAU_YEAR: Optional[float] = None

import pandas as pd 
@app.post('/predict')
def predict(data:LoadInput):

    data_dict = data.model_dump()
    df = pd.DataFrame([data_dict])
    df=label_encoder(df,categorical_feats=cat_feats)
    result=model.predict(df)
    return {'prediction':result.tolist()}



