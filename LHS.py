import streamlit as st
import pandas as pd
import numpy as np
from pyDOE import lhs

st.set_page_config(page_title="LHS 슬러리 조성표", layout="wide")
st.title("LHS 기반 음극 슬러리 조성표 생성기")

st.markdown("**LHS를 이용해 Carbon Black, CMC, Solvent 조성을 샘플링하고, Graphite는 자동 계산됩니다.**")

# 샘플 수 입력
n_samples = st.number_input("샘플 수 입력", min_value=1, max_value=100, value=10, step=1)

st.sidebar.header("조성 범위 설정 (wt%)")

# Carbon Black
st.sidebar.markdown("**Carbon Black (wt%)**")
col1, col2 = st.sidebar.columns(2)
cb_min = col1.number_input("Carbon Black 최소", key="cb_min", value=1.0, step=0.1, label_visibility="collapsed")
cb_max = col2.number_input("Carbon Black 최대", key="cb_max", value=10.0, step=0.1, label_visibility="collapsed")

# CMC
st.sidebar.markdown("**CMC (wt%)**")
col3, col4 = st.sidebar.columns(2)
cmc_min = col3.number_input("CMC 최소", key="cmc_min", value=2.0, step=0.1, label_visibility="collapsed")
cmc_max = col4.number_input("CMC 최대", key="cmc_max", value=10.0, step=0.1, label_visibility="collapsed")

# Solvent
st.sidebar.markdown("**Solvent (wt%)**")
col5, col6 = st.sidebar.columns(2)
solvent_min = col5.number_input("Solvent 최소", key="solvent_min", value=30.0, step=0.1, label_visibility="collapsed")
solvent_max = col6.number_input("Solvent 최대", key="solvent_max", value=60.0, step=0.1, label_visibility="collapsed")

# Graphite
st.sidebar.markdown("**Graphite (wt%)**")
col7, col8 = st.sidebar.columns(2)
graphite_min = col7.number_input("Graphite 최소", key="graphite_min", value=30.0, step=0.5, label_visibility="collapsed")
graphite_max = col8.number_input("Graphite 최대", key="graphite_max", value=65.0, step=0.5, label_visibility="collapsed")

# 범위 정리
bounds = {
    'carbon_black': (cb_min, cb_max),
    'cmc': (cmc_min, cmc_max),
    'solvent': (solvent_min, solvent_max)
}
keys = list(bounds.keys())

# 조건 만족하는 샘플 생성
valid_samples = []
max_trials = 1000
trial_count = 0

while len(valid_samples) < n_samples and trial_count < max_trials:
    trial_count += 1
    lhs_sample = lhs(len(bounds), samples=1)
    sample_dict = {}

    for i, key in enumerate(keys):
        min_val, max_val = bounds[key]
        val = lhs_sample[0, i] * (max_val - min_val) + min_val
        sample_dict[key + "_wt%"] = val

    # Graphite 계산
    graphite = 100 - sample_dict["carbon_black_wt%"] - sample_dict["cmc_wt%"] - sample_dict["solvent_wt%"]

    # 조건 만족하면 추가
    if 0 < graphite <= 100 and graphite_min <= graphite <= graphite_max:
        sample_dict["graphite_wt%"] = graphite
        valid_samples.append(sample_dict)

# 결과 출력
st.subheader("조성표")

if len(valid_samples) < n_samples:
    st.warning(f"조건을 만족하는 조성을 {n_samples}개 중 {len(valid_samples)}개만 생성했습니다. 범위를 완화해보세요.")
else:
    st.success(f"{n_samples}개의 조건 만족 조성을 성공적으로 생성했습니다.")

if valid_samples:
    df = pd.DataFrame(valid_samples)
    df.index = np.arange(1, len(df) + 1)
    st.dataframe(df.style.format(precision=2))
else:
    st.error("조건을 만족하는 조성을 하나도 생성하지 못했습니다.")
