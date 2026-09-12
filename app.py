import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Chemical Storage Spill-Risk Planner",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp{background:linear-gradient(135deg,#f7fbff 0%,#eef8f4 48%,#fff8ef 100%);color:#172033}
.block-container{max-width:1480px;padding-top:1.1rem}
.hero{background:linear-gradient(120deg,#ffffff,#eaf7f3);border:1px solid #d5e8e3;border-radius:26px;padding:28px 32px;box-shadow:0 12px 32px rgba(31,76,75,.10);margin-bottom:20px}
.hero h1{margin:0;color:#174f4b;font-size:2.25rem}.hero p{color:#5d6f79;margin:.55rem 0 0;font-size:1rem}
.card{background:#fff;border:1px solid #dfe9e7;border-radius:18px;padding:17px;box-shadow:0 7px 22px rgba(31,76,75,.08);height:100%}
.metric{font-size:1.85rem;font-weight:800;color:#174f4b}.label{font-size:.79rem;color:#6b7b84;text-transform:uppercase;letter-spacing:.07em}
.section{font-size:1.28rem;font-weight:800;color:#194c49;margin:23px 0 10px}
.alert{padding:12px 15px;border-radius:13px;background:#fff7e7;border:1px solid #efd28a;color:#624b12;margin:6px 0}
.note{background:#edf8ff;border:1px solid #cfe6f5;border-radius:14px;padding:13px;color:#31536a}
.small{color:#687982;font-size:.88rem}
div[data-testid="stSidebar"]{background:#f0f8f6;border-right:1px solid #d7e8e4}
</style>
""", unsafe_allow_html=True)

REQUIRED = [
    "inventory_volume_tons","storage_condition_score","containment_score",
    "weather_exposure_index","inspection_score","nearby_population",
    "transfer_frequency_30d","days_since_inspection","container_age_years",
    "leak_history_24m","chemical_hazard_index","temperature_excursion_count"
]

@st.cache_data
def load_data(uploaded=None):
    return pd.read_csv(uploaded) if uploaded is not None else pd.read_csv(
        "data/sample_chemical_storage_records.csv"
    )

def screening_score(row):
    value = (
        np.clip(row.inventory_volume_tons / 50 * 16, 0, 16)
        + np.clip((100-row.storage_condition_score)*0.20, 0, 20)
        + np.clip((100-row.containment_score)*0.18, 0, 18)
        + np.clip(row.weather_exposure_index*0.12, 0, 12)
        + np.clip((100-row.inspection_score)*0.18, 0, 18)
        + np.clip(row.transfer_frequency_30d*1.2, 0, 12)
        + np.clip(row.days_since_inspection/20, 0, 12)
        + np.clip(row.container_age_years, 0, 10)
        + np.clip(row.leak_history_24m*4, 0, 12)
        + np.clip(row.chemical_hazard_index*0.10, 0, 10)
        + np.clip(row.temperature_excursion_count*1.5, 0, 9)
    )
    return round(float(np.clip(value, 0, 100)), 1)

def risk_class(score):
    if score < 25: return "Low"
    if score < 50: return "Moderate"
    if score < 75: return "High"
    return "Critical"

st.markdown("""
<div class="hero">
<h1>🧪 Chemical Storage Spill-Risk Planner</h1>
<p>Local-first facility intelligence for spill-risk screening, storage-condition review,
inspection prioritization and operational planning.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🧭 Operations Console")
    uploaded = st.file_uploader("Upload local facility CSV", type=["csv"])
    st.caption("100% local processing • No external APIs")
    st.markdown("---")
    sample = pd.read_csv("data/sample_chemical_storage_records.csv")
    regions = st.multiselect(
        "Facility region", sorted(sample.region.unique()),
        default=sorted(sample.region.unique())
    )
    risks = st.multiselect(
        "Risk class", ["Low","Moderate","High","Critical"],
        default=["Low","Moderate","High","Critical"]
    )
    population = st.slider("Minimum nearby population", 0, 100000, 0, 1000)
    st.markdown("---")
    st.markdown("### 🧩 Dashboard Modules")
    st.caption("Risk Map • Storage • Weather • Inspection • Population • Priority • Scenarios • Alerts")

df = load_data(uploaded)
missing = [c for c in REQUIRED if c not in df.columns]
if missing:
    st.error("CSV missing required columns: " + ", ".join(missing))
    st.stop()

df["risk_score"] = df.apply(screening_score, axis=1)
df["risk_class"] = df["risk_score"].map(risk_class)
df = df[
    df.region.isin(regions)
    & df.risk_class.isin(risks)
    & (df.nearby_population >= population)
].copy()

if df.empty:
    st.warning("No facilities match the current filters.")
    st.stop()

metrics = st.columns(5)
values = [
    ("🏭","Facilities screened",len(df)),
    ("⚠️","High + critical",int((df.risk_score >= 50).sum())),
    ("🧯","Average risk",f"{df.risk_score.mean():.1f}"),
    ("🔍","Review signals",int((df.inspection_score < 60).sum() + df.leak_history_24m.gt(0).sum())),
    ("👥","Population nearby",f"{int(df.nearby_population.sum()):,}")
]
for col,(icon,label,value) in zip(metrics,values):
    col.markdown(
        f'<div class="card"><div class="label">{icon} {label}</div>'
        f'<div class="metric">{value}</div></div>',
        unsafe_allow_html=True
    )

st.markdown('<div class="section">🗺️ Facility Risk Intelligence</div>', unsafe_allow_html=True)
left,right = st.columns([1.5,1])
with left:
    fig = px.scatter(
        df, x="longitude", y="latitude", size="risk_score", color="risk_class",
        hover_name="facility_id",
        hover_data=["region","chemical_category","inventory_volume_tons","nearby_population"],
        title="Local Facility Risk Map",
        labels={"longitude":"Longitude","latitude":"Latitude"}
    )
    fig.update_layout(template="plotly_white",height=410)
    st.plotly_chart(fig,use_container_width=True)
with right:
    dist = df.risk_class.value_counts().reindex(["Low","Moderate","High","Critical"]).fillna(0).reset_index()
    dist.columns = ["risk_class","count"]
    fig = px.pie(dist,names="risk_class",values="count",hole=.58,title="Risk Distribution")
    fig.update_layout(template="plotly_white",height=410)
    st.plotly_chart(fig,use_container_width=True)

st.markdown('<div class="section">🧪 Storage Condition & Containment</div>', unsafe_allow_html=True)
left,right = st.columns(2)
with left:
    fig = px.scatter(
        df,x="storage_condition_score",y="containment_score",
        size="inventory_volume_tons",color="risk_class",hover_name="facility_id",
        title="Storage Condition vs Containment",
        labels={"storage_condition_score":"Storage condition score",
                "containment_score":"Containment score"}
    )
    fig.update_layout(template="plotly_white",height=350)
    st.plotly_chart(fig,use_container_width=True)
with right:
    cat = df.groupby("chemical_category",as_index=False).agg(
        avg_risk=("risk_score","mean"),
        inventory=("inventory_volume_tons","sum")
    ).sort_values("avg_risk",ascending=False)
    fig = px.bar(cat,x="chemical_category",y="avg_risk",color="avg_risk",
                 text_auto=".1f",title="Risk by Chemical Category")
    fig.update_layout(template="plotly_white",height=350,showlegend=False)
    st.plotly_chart(fig,use_container_width=True)

st.markdown('<div class="section">🌦️ Weather, Inspection & Operations</div>', unsafe_allow_html=True)
c1,c2,c3 = st.columns(3)
with c1:
    fig = px.scatter(df,x="weather_exposure_index",y="risk_score",color="risk_class",
                     size="nearby_population",hover_name="facility_id",
                     title="Weather Exposure vs Risk")
    fig.update_layout(template="plotly_white",height=320)
    st.plotly_chart(fig,use_container_width=True)
with c2:
    fig = px.scatter(df,x="days_since_inspection",y="inspection_score",
                     color="risk_class",size="risk_score",hover_name="facility_id",
                     title="Inspection Recency")
    fig.update_layout(template="plotly_white",height=320)
    st.plotly_chart(fig,use_container_width=True)
with c3:
    fig = px.scatter(df,x="transfer_frequency_30d",y="risk_score",color="risk_class",
                     size="inventory_volume_tons",hover_name="facility_id",
                     title="Transfer Activity vs Risk")
    fig.update_layout(template="plotly_white",height=320)
    st.plotly_chart(fig,use_container_width=True)

st.markdown('<div class="section">📊 Population Exposure & Regional Benchmarking</div>', unsafe_allow_html=True)
c1,c2 = st.columns(2)
with c1:
    fig = px.scatter(df,x="nearby_population",y="risk_score",color="risk_class",
                     size="inventory_volume_tons",hover_name="facility_id",
                     title="Nearby Population Exposure")
    fig.update_layout(template="plotly_white",height=340)
    st.plotly_chart(fig,use_container_width=True)
with c2:
    regional = df.groupby("region",as_index=False).agg(
        facilities=("facility_id","count"),
        avg_risk=("risk_score","mean"),
        population=("nearby_population","sum")
    ).sort_values("avg_risk",ascending=False)
    fig = px.bar(regional,x="region",y="avg_risk",color="avg_risk",
                 text_auto=".1f",title="Regional Risk Benchmark")
    fig.update_layout(template="plotly_white",height=340,showlegend=False)
    st.plotly_chart(fig,use_container_width=True)

st.markdown('<div class="section">🚨 Spill-Risk Priority Queue</div>', unsafe_allow_html=True)
priority = df[
    ["facility_id","region","chemical_category","risk_score","risk_class",
     "inventory_volume_tons","storage_condition_score","containment_score",
     "inspection_score","days_since_inspection","leak_history_24m","nearby_population"]
].sort_values("risk_score",ascending=False)
st.dataframe(priority.head(20),use_container_width=True,hide_index=True)

st.markdown('<div class="section">🧪 What-if Scenario Studio</div>', unsafe_allow_html=True)
a,b,c,d = st.columns(4)
with a: inventory_change = st.slider("Inventory change %",-40,50,0)
with b: storage_change = st.slider("Storage score change",-30,20,0)
with c: containment_change = st.slider("Containment score change",-30,20,0)
with d: inspection_change = st.slider("Inspection score change",-30,20,0)

scenario = df.copy()
scenario["inventory_volume_tons"] = np.clip(
    scenario["inventory_volume_tons"]*(1+inventory_change/100),0,None
)
scenario["storage_condition_score"] = np.clip(
    scenario["storage_condition_score"]+storage_change,0,100
)
scenario["containment_score"] = np.clip(
    scenario["containment_score"]+containment_change,0,100
)
scenario["inspection_score"] = np.clip(
    scenario["inspection_score"]+inspection_change,0,100
)
scenario["scenario_score"] = scenario.apply(screening_score,axis=1)

a,b,c = st.columns(3)
a.metric("Current average",f"{df.risk_score.mean():.1f}")
b.metric("Scenario average",f"{scenario.scenario_score.mean():.1f}",
         f"{scenario.scenario_score.mean()-df.risk_score.mean():+.1f}")
c.metric("High / Critical",int((scenario.scenario_score>=50).sum()))

st.markdown('<div class="section">🔔 Rule-based Operational Alerts</div>', unsafe_allow_html=True)
alerts=[]
for _,r in df.iterrows():
    if r.risk_score >= 75:
        alerts.append(f"🔴 {r.facility_id}: critical screening priority ({r.risk_score:.1f})")
    elif r.risk_score >= 50:
        alerts.append(f"🟠 {r.facility_id}: high screening priority ({r.risk_score:.1f})")
    if r.containment_score < 60:
        alerts.append(f"🟡 {r.facility_id}: containment score below 60")
    if r.storage_condition_score < 60:
        alerts.append(f"🟡 {r.facility_id}: storage condition score below 60")
    if r.days_since_inspection >= 180:
        alerts.append(f"🟡 {r.facility_id}: inspection older than 180 days")
    if r.leak_history_24m >= 2:
        alerts.append(f"🟡 {r.facility_id}: repeated historical leak signal")
if alerts:
    for item in alerts[:18]:
        st.markdown(f'<div class="alert">{item}</div>',unsafe_allow_html=True)
else:
    st.success("No rule-based alerts triggered.")

st.markdown('<div class="section">📈 Historical Risk Trend</div>', unsafe_allow_html=True)
if "record_date" in df.columns:
    trend = df.groupby("record_date",as_index=False).agg(avg_risk=("risk_score","mean"))
    trend["record_date"] = pd.to_datetime(trend["record_date"])
    trend = trend.sort_values("record_date")
    fig = px.line(trend,x="record_date",y="avg_risk",markers=True,
                  title="Average Screening Risk Over Time")
    fig.update_layout(template="plotly_white",height=330)
    st.plotly_chart(fig,use_container_width=True)

st.markdown("""
<div class="note"><b>Responsible-use note</b><br>
<span class="small">This application provides local screening and decision-support analytics only.
It does not predict an actual spill, certify chemical-storage safety, or replace qualified
hazardous-material professionals, engineers, inspectors, emergency authorities, or applicable
laws and safety standards. Sample data is synthetic.</span></div>
""",unsafe_allow_html=True)
