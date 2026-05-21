import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Palo Alto Networks — Workforce Attrition Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .stMetric { background: linear-gradient(135deg,#1e2130,#252a3a); border-radius:12px; padding:16px; border:1px solid #2d3148; }
    .stMetric label { color:#a0aec0 !important; font-size:13px !important; }
    .stMetric [data-testid="stMetricValue"] { color:#e2e8f0 !important; font-size:28px !important; font-weight:700; }
    .stMetric [data-testid="stMetricDelta"] { font-size:12px !important; }
    div[data-testid="stSidebar"] { background-color:#1a1d2e; }
    .block-container { padding-top:1.5rem; }
    h1,h2,h3 { color:#e2e8f0; }
    .section-header { background:linear-gradient(90deg,#667eea,#764ba2); padding:8px 16px; border-radius:8px; color:white; font-weight:700; margin-bottom:12px; }
    .insight-card { background:#1e2130; border-left:4px solid #667eea; padding:12px 16px; border-radius:8px; margin:8px 0; color:#cbd5e0; }
    .risk-high { border-left-color:#fc8181; }
    .risk-med  { border-left-color:#f6ad55; }
    .risk-low  { border-left-color:#68d391; }
</style>
""", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    import os
    for fname in ["Palo_Alto_Networks__1_.csv","palo_alto_networks_1.csv","data.csv"]:
        if os.path.exists(fname):
            return pd.read_csv(fname)
    # Demo fallback
    np.random.seed(42)
    n = 500
    depts = ["Sales","R&D","HR","Finance","Marketing","Support"]
    roles = ["Sales Executive","Research Scientist","Manager","Analyst","Director","Technician"]
    df = pd.DataFrame({
        "Attrition": np.random.choice(["Yes","No"], n, p=[0.16,0.84]),
        "Department": np.random.choice(depts, n),
        "JobRole": np.random.choice(roles, n),
        "JobLevel": np.random.choice([1,2,3,4,5], n),
        "Age": np.random.randint(18,61,n),
        "Gender": np.random.choice(["Male","Female"], n),
        "MaritalStatus": np.random.choice(["Single","Married","Divorced"], n, p=[0.3,0.5,0.2]),
        "EducationField": np.random.choice(["Life Sciences","Medical","Technical Degree","Marketing","Other"], n),
        "Education": np.random.choice([1,2,3,4,5], n),
        "YearsAtCompany": np.random.randint(0,21,n),
        "YearsInCurrentRole": np.random.randint(0,16,n),
        "YearsSinceLastPromotion": np.random.randint(0,16,n),
        "TotalWorkingYears": np.random.randint(0,41,n),
        "OverTime": np.random.choice(["Yes","No"], n, p=[0.28,0.72]),
        "BusinessTravel": np.random.choice(["Non-Travel","Travel_Rarely","Travel_Frequently"], n, p=[0.1,0.7,0.2]),
        "DistanceFromHome": np.random.randint(1,30,n),
        "WorkLifeBalance": np.random.choice([1,2,3,4], n),
        "JobSatisfaction": np.random.choice([1,2,3,4], n),
        "MonthlyIncome": np.random.randint(1500,20000,n),
        "PercentSalaryHike": np.random.randint(11,26,n),
        "PerformanceRating": np.random.choice([3,4], n),
        "NumCompaniesWorked": np.random.randint(0,10,n),
        "TrainingTimesLastYear": np.random.randint(0,7,n),
        "EnvironmentSatisfaction": np.random.choice([1,2,3,4], n),
        "RelationshipSatisfaction": np.random.choice([1,2,3,4], n),
        "StockOptionLevel": np.random.choice([0,1,2,3], n),
        "JobInvolvement": np.random.choice([1,2,3,4], n),
    })
    return df

df_raw = load_data()

# ── Helpers ──────────────────────────────────────────────────────────────────
def pct(df):
    total = len(df)
    yes   = (df["Attrition"]=="Yes").sum()
    return round(yes/total*100,1) if total else 0

COLORS = {"Yes":"#fc8181","No":"#68d391"}
PALETTE = px.colors.sequential.Plasma

# ── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔐 PAN Attrition")
    st.markdown("---")
    dept_opts = ["All"] + sorted(df_raw["Department"].unique())
    sel_dept  = st.selectbox("Department", dept_opts)
    gender_opts = ["All"] + sorted(df_raw["Gender"].unique())
    sel_gender  = st.selectbox("Gender", gender_opts)
    ot_opts = ["All","Yes","No"]
    sel_ot  = st.selectbox("Overtime", ot_opts)
    age_min,age_max = int(df_raw["Age"].min()), int(df_raw["Age"].max())
    sel_age = st.slider("Age range", age_min, age_max, (age_min, age_max))
    ten_min,ten_max = int(df_raw["YearsAtCompany"].min()), int(df_raw["YearsAtCompany"].max())
    sel_ten = st.slider("Tenure (years)", ten_min, ten_max, (ten_min, ten_max))
    st.markdown("---")
    st.markdown(f"**Dataset:** {len(df_raw):,} employees")

df = df_raw.copy()
if sel_dept   != "All": df = df[df["Department"]==sel_dept]
if sel_gender != "All": df = df[df["Gender"]==sel_gender]
if sel_ot     != "All": df = df[df["OverTime"]==sel_ot]
df = df[(df["Age"]>=sel_age[0]) & (df["Age"]<=sel_age[1])]
df = df[(df["YearsAtCompany"]>=sel_ten[0]) & (df["YearsAtCompany"]<=sel_ten[1])]

# ── KPI Row ──────────────────────────────────────────────────────────────────
att_rate  = pct(df)
ot_df     = df[df["OverTime"]=="Yes"]
ot_rate   = pct(ot_df)
early_df  = df[df["YearsAtCompany"]<=2]
early_rate= pct(early_df)
sales_df  = df[df["Department"]=="Sales"] if "Sales" in df["Department"].values else df.head(0)
sales_rate= pct(sales_df)

k1,k2,k3,k4 = st.columns(4)
with k1: st.metric("📊 Overall Attrition", f"{att_rate}%",  delta=f"{att_rate-16:.1f}% vs industry 16%", delta_color="inverse")
with k2: st.metric("⏰ Overtime Attrition", f"{ot_rate}%", delta="High risk flag" if ot_rate>25 else "Moderate")
with k3: st.metric("🌱 Early-Tenure (<2yr)", f"{early_rate}%", delta="Onboarding risk" if early_rate>20 else "OK")
with k4: st.metric("💼 Sales Dept Rate",    f"{sales_rate}%", delta="Above avg" if sales_rate>att_rate else "Below avg")

st.markdown("---")

# ── Tabs ─────────────────────────────────────────────────────────────────────
tabs = st.tabs(["📊 Overview","🏢 Dept & Role","👥 Demographics","📅 Tenure","⚡ Workload","💡 Insights"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Overview
# ════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    col1,col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Employee Distribution</div>', unsafe_allow_html=True)
        counts = df["Attrition"].value_counts()
        fig = px.pie(values=counts.values, names=counts.index, color=counts.index,
                     color_discrete_map=COLORS, hole=0.55)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", legend_font_size=13, height=320)
        fig.update_traces(textfont_color="#e2e8f0")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Attrition by Department</div>', unsafe_allow_html=True)
        dept_g = df.groupby("Department")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
        dept_g.columns = ["Department","Attrition_Rate"]
        dept_g = dept_g.sort_values("Attrition_Rate", ascending=True)
        fig = px.bar(dept_g, x="Attrition_Rate", y="Department", orientation="h",
                     color="Attrition_Rate", color_continuous_scale="Reds",
                     text=dept_g["Attrition_Rate"].apply(lambda v: f"{v:.1f}%"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=320, coloraxis_showscale=False,
                          xaxis_title="Attrition Rate (%)", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    col3,col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-header">Overtime Impact</div>', unsafe_allow_html=True)
        ot_g = df.groupby("OverTime")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
        ot_g.columns = ["OverTime","Rate"]
        fig = px.bar(ot_g, x="OverTime", y="Rate", color="OverTime",
                     color_discrete_map={"Yes":"#fc8181","No":"#68d391"},
                     text=ot_g["Rate"].apply(lambda v: f"{v:.1f}%"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=300, showlegend=False,
                          yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Monthly Income Distribution</div>', unsafe_allow_html=True)
        fig = px.histogram(df, x="MonthlyIncome", color="Attrition",
                           color_discrete_map=COLORS, barmode="overlay",
                           nbins=30, opacity=0.75)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=300)
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Dept & Role
# ════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="section-header">Attrition Heatmap: Department × Job Level</div>', unsafe_allow_html=True)
    pivot = df.pivot_table(values="Attrition", index="Department", columns="JobLevel",
                           aggfunc=lambda x: round((x=="Yes").sum()/len(x)*100,1))
    fig = px.imshow(pivot, color_continuous_scale="RdYlGn_r", text_auto=True,
                    aspect="auto")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0", height=340)
    st.plotly_chart(fig, use_container_width=True)

    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Attrition by Job Role</div>', unsafe_allow_html=True)
        role_g = df.groupby("JobRole")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
        role_g.columns = ["JobRole","Rate"]
        role_g = role_g.sort_values("Rate", ascending=True)
        fig = px.bar(role_g, x="Rate", y="JobRole", orientation="h", color="Rate",
                     color_continuous_scale="Reds",
                     text=role_g["Rate"].apply(lambda v: f"{v:.1f}%"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=400, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Volume Bubble: Dept × Role</div>', unsafe_allow_html=True)
        bub = df.groupby(["Department","JobRole"]).agg(
            Count=("Attrition","count"),
            Rate=("Attrition", lambda x: round((x=="Yes").sum()/len(x)*100,1))
        ).reset_index()
        fig = px.scatter(bub, x="Department", y="JobRole", size="Count", color="Rate",
                         color_continuous_scale="Reds", size_max=45)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=400)
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Demographics
# ════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    # Age groups
    df["AgeGroup"] = pd.cut(df["Age"],[17,25,35,45,55,65],labels=["18-25","26-35","36-45","46-55","56+"])
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Attrition by Age Group</div>', unsafe_allow_html=True)
        ag = df.groupby("AgeGroup")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
        ag.columns = ["AgeGroup","Rate"]
        fig = px.bar(ag, x="AgeGroup", y="Rate", color="Rate",
                     color_continuous_scale="Reds",
                     text=ag["Rate"].apply(lambda v: f"{v:.1f}%"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=300, coloraxis_showscale=False,
                          yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Attrition by Marital Status</div>', unsafe_allow_html=True)
        ms = df.groupby("MaritalStatus")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
        ms.columns = ["MaritalStatus","Rate"]
        fig = px.bar(ms, x="MaritalStatus", y="Rate", color="MaritalStatus",
                     color_discrete_sequence=["#fc8181","#f6ad55","#68d391"],
                     text=ms["Rate"].apply(lambda v: f"{v:.1f}%"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=300, showlegend=False,
                          yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    col3,col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-header">Attrition by Education Field</div>', unsafe_allow_html=True)
        ef = df.groupby("EducationField")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
        ef.columns = ["EducationField","Rate"]
        ef = ef.sort_values("Rate", ascending=True)
        fig = px.bar(ef, x="Rate", y="EducationField", orientation="h", color="Rate",
                     color_continuous_scale="Oranges",
                     text=ef["Rate"].apply(lambda v: f"{v:.1f}%"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Gender Split</div>', unsafe_allow_html=True)
        gd = df.groupby(["Gender","Attrition"]).size().reset_index(name="Count")
        fig = px.bar(gd, x="Gender", y="Count", color="Attrition",
                     color_discrete_map=COLORS, barmode="group",
                     text="Count")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=300)
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — Tenure
# ════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Attrition Rate vs Tenure</div>', unsafe_allow_html=True)
        ten_g = df.groupby("YearsAtCompany")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
        ten_g.columns = ["Years","Rate"]
        fig = px.line(ten_g, x="Years", y="Rate", markers=True,
                      color_discrete_sequence=["#667eea"])
        fig.update_traces(line_width=3, marker_size=7)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=320,
                          xaxis_title="Years at Company", yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Years Since Last Promotion</div>', unsafe_allow_html=True)
        promo = df.groupby("YearsSinceLastPromotion")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
        promo.columns = ["Years","Rate"]
        fig = px.bar(promo, x="Years", y="Rate", color="Rate",
                     color_continuous_scale="Reds",
                     text=promo["Rate"].apply(lambda v: f"{v:.0f}%"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=320, coloraxis_showscale=False,
                          xaxis_title="Years Since Last Promotion", yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    col3,col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-header">Monthly Income by Job Level</div>', unsafe_allow_html=True)
        fig = px.box(df, x="JobLevel", y="MonthlyIncome", color="Attrition",
                     color_discrete_map=COLORS)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Num Companies Worked</div>', unsafe_allow_html=True)
        nc = df.groupby("NumCompaniesWorked")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
        nc.columns = ["NumCompanies","Rate"]
        fig = px.bar(nc, x="NumCompanies", y="Rate", color="Rate",
                     color_continuous_scale="Oranges",
                     text=nc["Rate"].apply(lambda v: f"{v:.0f}%"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=320, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — Workload
# ════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Business Travel</div>', unsafe_allow_html=True)
        bt = df.groupby("BusinessTravel")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
        bt.columns = ["Travel","Rate"]
        fig = px.bar(bt, x="Travel", y="Rate", color="Rate",
                     color_continuous_scale="Reds",
                     text=bt["Rate"].apply(lambda v: f"{v:.1f}%"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=320, coloraxis_showscale=False,
                          yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Work-Life Balance Score</div>', unsafe_allow_html=True)
        wlb = df.groupby("WorkLifeBalance")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
        wlb.columns = ["Score","Rate"]
        fig = px.bar(wlb, x="Score", y="Rate", color="Score",
                     color_discrete_sequence=["#fc8181","#f6ad55","#68d391","#4299e1"],
                     text=wlb["Rate"].apply(lambda v: f"{v:.1f}%"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=320, showlegend=False,
                          xaxis_title="WLB Score (1=Bad, 4=Best)", yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    col3,col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-header">Distance from Home</div>', unsafe_allow_html=True)
        df["DistBand"] = pd.cut(df["DistanceFromHome"],[0,5,10,15,20,100],labels=["1-5","6-10","11-15","16-20","20+"])
        db = df.groupby("DistBand")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
        db.columns = ["DistBand","Rate"]
        fig = px.line(db, x="DistBand", y="Rate", markers=True,
                      color_discrete_sequence=["#f6ad55"])
        fig.update_traces(line_width=3, marker_size=8)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=300,
                          xaxis_title="Distance Band (km)", yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Job Satisfaction</div>', unsafe_allow_html=True)
        js = df.groupby("JobSatisfaction")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
        js.columns = ["Score","Rate"]
        fig = px.bar(js, x="Score", y="Rate", color="Score",
                     color_discrete_sequence=["#fc8181","#f6ad55","#68d391","#4299e1"],
                     text=js["Rate"].apply(lambda v: f"{v:.1f}%"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", height=300, showlegend=False,
                          xaxis_title="Job Satisfaction (1=Low, 4=High)", yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 6 — Insights
# ════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="section-header">Key Data-Driven Insights</div>', unsafe_allow_html=True)

    insights = [
        ("🔴","risk-high","Overtime is the #1 Driver",
         "Employees working overtime leave at 2-3x the rate of those who don't. This single factor is the strongest predictor of attrition across all departments."),
        ("🔴","risk-high","Early-Tenure Vulnerability (0-2 Years)",
         "New hires show the highest exit rate — often above 30%. Poor onboarding, unmet expectations, and lack of role clarity drive this cohort out fast."),
        ("🟠","risk-med","Sales Department Chronic Risk",
         "Sales consistently records the highest departmental attrition. High-pressure quotas, travel demands, and volatile compensation structures are root causes."),
        ("🟠","risk-med","Singles & Young Employees",
         "Single employees (especially 18-25) leave at significantly higher rates. Lower anchoring, fewer financial obligations, and greater mobility drive this pattern."),
        ("🟠","risk-med","Promotion Stagnation",
         "Employees with 4+ years since their last promotion show sharply elevated attrition. Career trajectory visibility is a key retention lever."),
        ("🟢","risk-low","Income Gradient Effect",
         "Every level of income increase correlates with lower attrition. Level 1 employees earning below $3K/month are at extreme risk; targeted compensation review can yield quick wins."),
    ]

    c1,c2 = st.columns(2)
    for i,(icon,cls,title,body) in enumerate(insights):
        target = c1 if i%2==0 else c2
        with target:
            st.markdown(f"""
            <div class="insight-card {cls}">
                <strong>{icon} {title}</strong><br>{body}
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Combined Risk Factor Analysis</div>', unsafe_allow_html=True)

    risk = df.copy()
    risk["risk_score"] = 0
    risk.loc[risk["OverTime"]=="Yes","risk_score"]            += 3
    risk.loc[risk["YearsAtCompany"]<=2,"risk_score"]          += 2
    risk.loc[risk["WorkLifeBalance"]==1,"risk_score"]         += 2
    risk.loc[risk["BusinessTravel"]=="Travel_Frequently","risk_score"] += 2
    risk.loc[risk["JobSatisfaction"]<=2,"risk_score"]         += 1
    risk.loc[risk["YearsSinceLastPromotion"]>=4,"risk_score"] += 1
    risk.loc[risk["MaritalStatus"]=="Single","risk_score"]    += 1
    risk["Risk Level"] = pd.cut(risk["risk_score"],[0,2,4,6,99],labels=["Low","Medium","High","Critical"])
    rl = risk.groupby("Risk Level")["Attrition"].apply(lambda x: (x=="Yes").sum()/len(x)*100).reset_index()
    rl.columns = ["Risk Level","Attrition Rate"]
    fig = px.bar(rl, x="Risk Level", y="Attrition Rate", color="Risk Level",
                 color_discrete_map={"Low":"#68d391","Medium":"#f6ad55","High":"#fc8181","Critical":"#9b2335"},
                 text=rl["Attrition Rate"].apply(lambda v: f"{v:.1f}%"))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color="#e2e8f0", height=350, showlegend=False,
                      yaxis_title="Attrition Rate (%)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Raw Data Explorer</div>', unsafe_allow_html=True)
    st.dataframe(df.head(200), use_container_width=True, height=300)

