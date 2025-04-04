import streamlit as st
import pandas as pd
import numpy as np
from pyDOE import lhs

st.set_page_config(page_title="LHS 슬러리 조성표", layout="wide")
st.title("LHS 기반 음극 슬러리 조성표 생성기")

st.markdown("**LHS를 이용해 Carbon Black, CMC, Solvent 조성을 샘플링하고, Graphite는 자동 계산됩니다.**")

# 샘플 수 입력 (직접 입력)
n_samples = st.number_input("샘플 수 입력", min_value=1, max_value=100, value=10, step=1)

st.sidebar.header("조성 범위 설정 (wt%)")

# Carbon Black
st.sidebar.markdown("**Carbon Black (wt%)**")
col1, col2 = st.sidebar.columns(2)
cb_min = col1.number_input("최소값", key="cb_min", value=1.0, step=0.1, label_visibility="collapsed")
cb_max = col2.number_input("최대값", key="cb_max", value=5.0, step=0.1, label_visibility="collapsed")

# CMC
st.sidebar.markdown("**CMC (wt%)**")
col3, col4 = st.sidebar.columns(2)
cmc_min = col3.number_input("최소값", key="cmc_min", value=0.2, step=0.1, label_visibility="collapsed")
cmc_max = col4.number_input("최대값", key="cmc_max", value=1.0, step=0.1, label_visibility="collapsed")

# Solvent
st.sidebar.markdown("**Solvent (wt%)**")
col5, col6 = st.sidebar.columns(2)
solvent_min = col5.number_input("최소값", key="solvent_min", value=5.0, step=0.1, label_visibility="collapsed")
solvent_max = col6.number_input("최대값", key="solvent_max", value=15.0, step=0.1, label_visibility="collapsed")


# 범위 정리
bounds = {
    'carbon_black': (cb_min, cb_max),
    'cmc': (cmc_min, cmc_max),
    'solvent': (solvent_min, solvent_max)
}

# LHS 샘플링
lhs_samples = lhs(len(bounds), samples=n_samples)
scaled_samples = []
keys = list(bounds.keys())

for i, key in enumerate(keys):
    min_val, max_val = bounds[key]
    scaled = lhs_samples[:, i] * (max_val - min_val) + min_val
    scaled_samples.append(scaled)

# DataFrame 구성
df = pd.DataFrame({key + "_wt%": scaled_samples[i] for i, key in enumerate(keys)})

# graphite 계산
df["graphite_wt%"] = 100 - df["carbon_black_wt%"] - df["cmc_wt%"] - df["solvent_wt%"]

# 음수 제거
df = df[df["graphite_wt%"] > 0].reset_index(drop=True)

df.index = np.arange(1, len(df) + 1)

# 출력
st.subheader("조성표")
st.dataframe(df.style.format(precision=2))
