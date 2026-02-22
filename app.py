import streamlit as st
import json
from datetime import datetime, date
import uuid

st.set_page_config(
page_title=“RxHandoff | Pharmacy Shift Dashboard”,
page_icon=“💊”,
layout=“wide”,
initial_sidebar_state=“expanded”,
)

# ── Inject custom CSS ──────────────────────────────────────────────────────────

st.markdown(”””

<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:ital,wght@0,300;0,500;0,700;1,300&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}
h1, h2, h3, h4 {
    font-family: 'IBM Plex Mono', monospace !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0a0f1a !important;
    border-right: 1px solid #1e2d45;
}
section[data-testid="stSidebar"] * {
    color: #a8c4e0 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #a8c4e0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem;
}

/* Main background */
.main { background: #050b14 !important; }
.block-container { 
    padding-top: 1.5rem !important;
    background: #050b14;
}

/* Cards */
.rx-card {
    background: #0d1b2a;
    border: 1px solid #1e2d45;
    border-radius: 4px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    color: #c8dff0;
}
.rx-card.urgent {
    border-left: 3px solid #ff4d4d;
}
.rx-card.warning {
    border-left: 3px solid #ffb020;
}
.rx-card.stable {
    border-left: 3px solid #00c47d;
}
.rx-card.info {
    border-left: 3px solid #2d8cf0;
}

/* Tags */
.tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 2px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    margin-right: 4px;
    margin-bottom: 2px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.tag-red    { background: rgba(255,77,77,0.15);  color: #ff4d4d; border: 1px solid #ff4d4d40; }
.tag-amber  { background: rgba(255,176,32,0.15); color: #ffb020; border: 1px solid #ffb02040; }
.tag-green  { background: rgba(0,196,125,0.15);  color: #00c47d; border: 1px solid #00c47d40; }
.tag-blue   { background: rgba(45,140,240,0.15); color: #2d8cf0; border: 1px solid #2d8cf040; }
.tag-gray   { background: rgba(100,120,140,0.15);color: #6a8fad; border: 1px solid #6a8fad40; }

/* Header strip */
.shift-header {
    background: #0d1b2a;
    border: 1px solid #1e2d45;
    border-radius: 4px;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
}
.shift-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.3rem;
    font-weight: 600;
    color: #e8f4ff;
    margin: 0;
}
.shift-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: #4a7fa0;
}

/* Metric tiles */
.metric-tile {
    background: #0d1b2a;
    border: 1px solid #1e2d45;
    border-radius: 4px;
    padding: 1rem;
    text-align: center;
}
.metric-number {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: #e8f4ff;
    line-height: 1;
}
.metric-label {
    font-size: 0.72rem;
    color: #4a7fa0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
    font-family: 'IBM Plex Mono', monospace;
}
.metric-sub {
    font-size: 0.7rem;
    color: #ff4d4d;
    font-family: 'IBM Plex Mono', monospace;
    margin-top: 2px;
}

/* Section headers */
.section-head {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #2d8cf0;
    border-bottom: 1px solid #1e2d45;
    padding-bottom: 0.4rem;
    margin-bottom: 0.75rem;
    margin-top: 1.25rem;
}

/* Override streamlit default colors */
.stButton > button {
    background: #0d1b2a !important;
    color: #2d8cf0 !important;
    border: 1px solid #2d8cf0 !important;
    border-radius: 2px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.05em;
}
.stButton > button:hover {
    background: #2d8cf020 !important;
}
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: #0d1b2a !important;
    color: #c8dff0 !important;
    border: 1px solid #1e2d45 !important;
    border-radius: 2px !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
.stSelectbox > div > div {
    background: #0d1b2a !important;
    color: #c8dff0 !important;
    border: 1px solid #1e2d45 !important;
}
label {
    color: #6a8fad !important;
    font-size: 0.78rem !important;
    font-family: 'IBM Plex Mono', monospace !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.stCheckbox label { text-transform: none !important; }
</style>

“””, unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────────

def init_state():
if “issues” not in st.session_state:
st.session_state.issues = [
{
“id”: str(uuid.uuid4())[:8],
“mrn”: “MRN-00412”,
“patient”: “J. Hartwell”,
“unit”: “MICU”,
“bed”: “4B”,
“priority”: “Urgent”,
“category”: “Renal Dosing”,
“description”: “Vancomycin trough pending — levels ordered but not yet resulted. Dose due at 2100. Hold until AUC reviewed.”,
“pharmacist”: “Chen, M.”,
“status”: “Pending”,
“created”: “14:32”,
“tags”: [“Vancomycin”, “AKI”, “Hold”],
“followup_required”: True,
},
{
“id”: str(uuid.uuid4())[:8],
“mrn”: “MRN-00289”,
“patient”: “R. Okonkwo”,
“unit”: “CCU”,
“bed”: “2A”,
“priority”: “Urgent”,
“category”: “Drug Interaction”,
“description”: “Patient on warfarin (INR 3.1) — fluconazole ordered for oral thrush. Significant interaction. Recommend dose reduction + daily INR monitoring. Awaiting MD callback.”,
“pharmacist”: “Torres, L.”,
“status”: “Awaiting MD”,
“created”: “15:10”,
“tags”: [“Warfarin”, “DDI”, “Callback”],
“followup_required”: True,
},
{
“id”: str(uuid.uuid4())[:8],
“mrn”: “MRN-00551”,
“patient”: “M. Szabo”,
“unit”: “SICU”,
“bed”: “7C”,
“priority”: “Watch”,
“category”: “IV Shortage”,
“description”: “NS 1L bags on allocation. Patient requires 125 mL/hr maintenance. Switched to 500 mL bags Q4H per shortage protocol. Nursing aware.”,
“pharmacist”: “Patel, A.”,
“status”: “Monitoring”,
“created”: “13:45”,
“tags”: [“NS Shortage”, “IV Fluid”, “Protocol”],
“followup_required”: False,
},
{
“id”: str(uuid.uuid4())[:8],
“mrn”: “MRN-00374”,
“patient”: “D. Beaumont”,
“unit”: “Neuro ICU”,
“bed”: “1D”,
“priority”: “Stable”,
“category”: “Anticoagulation”,
“description”: “Heparin drip titrated to PTT 80–100. Last PTT 94 at 1600. Next check at 2200. Stable on current rate of 1150 units/hr.”,
“pharmacist”: “Williams, R.”,
“status”: “Resolved”,
“created”: “11:20”,
“tags”: [“Heparin”, “PTT”, “DVT-Tx”],
“followup_required”: False,
},
]
if “notes” not in st.session_state:
st.session_state.notes = [
{“time”: “15:55”, “author”: “Chen, M.”, “text”: “Pharmacy dept fridge #2 temp alarm resolved — biomedical confirmed. All refrigerated products verified stable.”},
{“time”: “14:00”, “author”: “Torres, L.”, “text”: “Aminoglycoside dosing service: two new consults in ED, both dosed and monitored. Levels scheduled.”},
{“time”: “13:30”, “author”: “Patel, A.”, “text”: “Oncology floor: 5-FU infusion completed without incident. Waste documented and disposed. Hazardous waste log updated.”},
]
if “current_pharmacist” not in st.session_state:
st.session_state.current_pharmacist = “Williams, R.”
if “shift” not in st.session_state:
st.session_state.shift = “Day (07:00–19:00)”

init_state()

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
st.markdown(”### 💊 RxHandoff”)
st.markdown(”—”)
st.markdown(”**Pharmacist on Duty**”)
pharmacist = st.text_input(“Name”, value=st.session_state.current_pharmacist, label_visibility=“collapsed”)
st.session_state.current_pharmacist = pharmacist

```
st.markdown("**Shift**")
shift = st.selectbox("Shift", ["Day (07:00–19:00)", "Night (19:00–07:00)", "Mid (11:00–23:00)"], 
                      index=0, label_visibility="collapsed")
st.session_state.shift = shift

st.markdown("---")
page = st.radio("Navigation", ["📋  Handoff Board", "➕  Log Issue", "📝  Shift Notes", "📊  Shift Summary"])
st.markdown("---")

# Quick stats in sidebar
issues = st.session_state.issues
urgent_count = sum(1 for i in issues if i["priority"] == "Urgent")
pending_count = sum(1 for i in issues if i["status"] in ["Pending", "Awaiting MD"])
st.markdown(f"""
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#4a7fa0;">
OPEN ISSUES<br>
<span style="font-size:1.5rem;color:#e8f4ff;font-weight:600;">{len(issues)}</span>
<br><br>
URGENT<br>
<span style="font-size:1.5rem;color:#ff4d4d;font-weight:600;">{urgent_count}</span>
<br><br>
PENDING FOLLOWUP<br>
<span style="font-size:1.5rem;color:#ffb020;font-weight:600;">{pending_count}</span>
</div>
""", unsafe_allow_html=True)
```

# ── Header ─────────────────────────────────────────────────────────────────────

now = datetime.now()
st.markdown(f”””

<div class="shift-header">
  <div>
    <p class="shift-title">RxHandoff Dashboard</p>
    <p class="shift-meta">Acute Care Pharmacy · {st.session_state.shift} · {now.strftime('%A, %B %d %Y')}</p>
  </div>
  <div style="text-align:right">
    <p style="font-family:'IBM Plex Mono',monospace;font-size:1.1rem;color:#e8f4ff;margin:0;">{now.strftime('%H:%M')}</p>
    <p class="shift-meta">{st.session_state.current_pharmacist}</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────

# PAGE: HANDOFF BOARD

# ─────────────────────────────────────────────────────────────────────────────

if “Handoff Board” in page:
# Metric row
issues = st.session_state.issues
total = len(issues)
urgent = sum(1 for i in issues if i[“priority”] == “Urgent”)
watch = sum(1 for i in issues if i[“priority”] == “Watch”)
resolved = sum(1 for i in issues if i[“status”] == “Resolved”)

```
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-tile">
        <div class="metric-number">{total}</div>
        <div class="metric-label">Total Issues</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-tile">
        <div class="metric-number" style="color:#ff4d4d">{urgent}</div>
        <div class="metric-label">Urgent</div>
        <div class="metric-sub">Require action now</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-tile">
        <div class="metric-number" style="color:#ffb020">{watch}</div>
        <div class="metric-label">Watch</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-tile">
        <div class="metric-number" style="color:#00c47d">{resolved}</div>
        <div class="metric-label">Resolved</div>
    </div>""", unsafe_allow_html=True)

# Filter bar
st.markdown('<p class="section-head">Active Issues</p>', unsafe_allow_html=True)
f1, f2, f3 = st.columns([2, 2, 2])
with f1:
    filter_priority = st.selectbox("Priority", ["All", "Urgent", "Watch", "Stable"])
with f2:
    filter_status = st.selectbox("Status", ["All", "Pending", "Awaiting MD", "Monitoring", "Resolved"])
with f3:
    filter_unit = st.selectbox("Unit", ["All"] + list(set(i["unit"] for i in issues)))

# Display issues
priority_map = {"Urgent": "urgent", "Watch": "warning", "Stable": "stable"}
tag_color_map = {
    "Vancomycin": "tag-red", "AKI": "tag-amber", "Hold": "tag-red",
    "Warfarin": "tag-amber", "DDI": "tag-red", "Callback": "tag-amber",
    "NS Shortage": "tag-amber", "IV Fluid": "tag-blue", "Protocol": "tag-blue",
    "Heparin": "tag-green", "PTT": "tag-green", "DVT-Tx": "tag-green",
}

shown = 0
for issue in issues:
    if filter_priority != "All" and issue["priority"] != filter_priority:
        continue
    if filter_status != "All" and issue["status"] != filter_status:
        continue
    if filter_unit != "All" and issue["unit"] != filter_unit:
        continue
    shown += 1

    card_class = priority_map.get(issue["priority"], "info")
    status_color = {"Pending": "#ffb020", "Awaiting MD": "#ff4d4d", 
                    "Monitoring": "#2d8cf0", "Resolved": "#00c47d"}.get(issue["status"], "#6a8fad")

    tags_html = "".join(
        f'<span class="tag {tag_color_map.get(t, "tag-gray")}">{t}</span>'
        for t in issue.get("tags", [])
    )

    col_card, col_actions = st.columns([5, 1])
    with col_card:
        st.markdown(f"""
        <div class="rx-card {card_class}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.4rem;">
            <div>
              <span style="font-family:'IBM Plex Mono',monospace;font-size:0.85rem;font-weight:600;color:#e8f4ff;">
                {issue['patient']}
              </span>
              <span style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#4a7fa0;margin-left:10px;">
                {issue['mrn']} · {issue['unit']} {issue['bed']}
              </span>
            </div>
            <div style="text-align:right;">
              <span style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:{status_color};border:1px solid {status_color}40;padding:1px 7px;border-radius:2px;">
                {issue['status']}
              </span>
            </div>
          </div>
          <div style="font-size:0.7rem;color:#4a7fa0;font-family:'IBM Plex Mono',monospace;margin-bottom:0.4rem;">
            {issue['category']} · Logged {issue['created']} by {issue['pharmacist']}
          </div>
          <div style="font-size:0.85rem;color:#a8c4e0;line-height:1.5;margin-bottom:0.5rem;">
            {issue['description']}
          </div>
          <div>{tags_html}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_actions:
        st.markdown("<div style='margin-top:0.6rem'/>", unsafe_allow_html=True)
        new_status = st.selectbox(
            f"Status##{issue['id']}",
            ["Pending", "Awaiting MD", "Monitoring", "Resolved"],
            index=["Pending", "Awaiting MD", "Monitoring", "Resolved"].index(issue["status"]),
            label_visibility="collapsed",
            key=f"sel_{issue['id']}"
        )
        if new_status != issue["status"]:
            issue["status"] = new_status
            st.rerun()
        if st.button("Remove", key=f"del_{issue['id']}"):
            st.session_state.issues = [i for i in st.session_state.issues if i["id"] != issue["id"]]
            st.rerun()

if shown == 0:
    st.markdown('<div class="rx-card info" style="text-align:center;color:#4a7fa0;">No issues match current filters.</div>', unsafe_allow_html=True)
```

# ─────────────────────────────────────────────────────────────────────────────

# PAGE: LOG ISSUE

# ─────────────────────────────────────────────────────────────────────────────

elif “Log Issue” in page:
st.markdown(’<p class="section-head">New Handoff Issue</p>’, unsafe_allow_html=True)

```
c1, c2 = st.columns(2)
with c1:
    mrn = st.text_input("MRN", placeholder="MRN-00000")
    patient = st.text_input("Patient Name", placeholder="Last, First")
    unit = st.selectbox("Unit", ["MICU", "CCU", "SICU", "Neuro ICU", "Step-Down", "ED", "Oncology", "Transplant", "General Med"])
    bed = st.text_input("Bed", placeholder="e.g. 4B")
with c2:
    priority = st.selectbox("Priority", ["Urgent", "Watch", "Stable"])
    category = st.selectbox("Category", [
        "Renal Dosing", "Drug Interaction", "IV Shortage", "Anticoagulation",
        "High-Alert Medication", "Pending Labs", "Formulary", "Allergy", "TPN/Nutrition", "Other"
    ])
    status = st.selectbox("Status", ["Pending", "Awaiting MD", "Monitoring"])
    tags_input = st.text_input("Tags (comma-separated)", placeholder="Vancomycin, AKI, Hold")

description = st.text_area("Issue Description / Action Required", height=120, 
                            placeholder="Describe the clinical situation, what has been done, and what the incoming pharmacist needs to do...")
followup = st.checkbox("Requires Follow-Up by Next Shift")

if st.button("→ Log Issue"):
    if not mrn or not patient or not description:
        st.error("MRN, patient name, and description are required.")
    else:
        new_issue = {
            "id": str(uuid.uuid4())[:8],
            "mrn": mrn,
            "patient": patient,
            "unit": unit,
            "bed": bed,
            "priority": priority,
            "category": category,
            "description": description,
            "pharmacist": st.session_state.current_pharmacist,
            "status": status,
            "created": datetime.now().strftime("%H:%M"),
            "tags": [t.strip() for t in tags_input.split(",") if t.strip()],
            "followup_required": followup,
        }
        st.session_state.issues.insert(0, new_issue)
        st.success(f"Issue logged for {patient} ({mrn})")
        st.balloons()
```

# ─────────────────────────────────────────────────────────────────────────────

# PAGE: SHIFT NOTES

# ─────────────────────────────────────────────────────────────────────────────

elif “Shift Notes” in page:
st.markdown(’<p class="section-head">General Shift Notes</p>’, unsafe_allow_html=True)
st.markdown(’<div style="font-size:0.78rem;color:#4a7fa0;font-family:IBM Plex Mono,monospace;margin-bottom:1rem;">Use for department-wide updates, shortage alerts, staffing notes, and information not tied to a specific patient.</div>’, unsafe_allow_html=True)

```
new_note = st.text_area("New note", height=80, placeholder="Type a shift note...")
if st.button("Post Note"):
    if new_note.strip():
        st.session_state.notes.insert(0, {
            "time": datetime.now().strftime("%H:%M"),
            "author": st.session_state.current_pharmacist,
            "text": new_note.strip()
        })
        st.success("Note posted.")
        st.rerun()

st.markdown('<p class="section-head">Note History</p>', unsafe_allow_html=True)
for note in st.session_state.notes:
    st.markdown(f"""
    <div class="rx-card info">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#2d8cf0;margin-bottom:0.3rem;">
        {note['time']} · {note['author']}
      </div>
      <div style="font-size:0.85rem;color:#a8c4e0;">{note['text']}</div>
    </div>
    """, unsafe_allow_html=True)
```

# ─────────────────────────────────────────────────────────────────────────────

# PAGE: SHIFT SUMMARY

# ─────────────────────────────────────────────────────────────────────────────

elif “Shift Summary” in page:
st.markdown(’<p class="section-head">End-of-Shift Summary</p>’, unsafe_allow_html=True)
st.markdown(’<div style="font-size:0.78rem;color:#4a7fa0;font-family:IBM Plex Mono,monospace;margin-bottom:1rem;">Auto-generated handoff report. Review, edit, and share with the incoming pharmacist.</div>’, unsafe_allow_html=True)

```
issues = st.session_state.issues
urgent_issues = [i for i in issues if i["priority"] == "Urgent"]
watch_issues = [i for i in issues if i["priority"] == "Watch"]
followup_issues = [i for i in issues if i.get("followup_required")]

summary_lines = [
    f"SHIFT HANDOFF REPORT — {st.session_state.shift}",
    f"Date: {date.today().strftime('%B %d, %Y')}",
    f"Prepared by: {st.session_state.current_pharmacist}",
    f"Generated: {datetime.now().strftime('%H:%M')}",
    "",
    "═══════════════════════════════════════",
    "URGENT ISSUES",
    "═══════════════════════════════════════",
]
for i in urgent_issues:
    summary_lines += [
        f"▶ {i['patient']} ({i['mrn']}) — {i['unit']} {i['bed']}",
        f"  Category: {i['category']} | Status: {i['status']}",
        f"  {i['description']}",
        f"  Tags: {', '.join(i.get('tags', []))}",
        "",
    ]
if not urgent_issues:
    summary_lines.append("  No urgent issues.\n")

summary_lines += [
    "═══════════════════════════════════════",
    "WATCH ITEMS",
    "═══════════════════════════════════════",
]
for i in watch_issues:
    summary_lines += [
        f"◈ {i['patient']} ({i['mrn']}) — {i['unit']} {i['bed']}",
        f"  {i['description']}",
        "",
    ]
if not watch_issues:
    summary_lines.append("  No watch items.\n")

summary_lines += [
    "═══════════════════════════════════════",
    "REQUIRES FOLLOWUP NEXT SHIFT",
    "═══════════════════════════════════════",
]
for i in followup_issues:
    summary_lines.append(f"  • {i['patient']} — {i['category']}")
if not followup_issues:
    summary_lines.append("  None flagged.")

summary_lines += [
    "",
    "═══════════════════════════════════════",
    "SHIFT NOTES",
    "═══════════════════════════════════════",
]
for note in st.session_state.notes:
    summary_lines.append(f"  [{note['time']}] {note['author']}: {note['text']}")

summary_text = "\n".join(summary_lines)

st.text_area("Handoff Report", value=summary_text, height=500, key="summary_display")

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        "⬇ Download Handoff (.txt)",
        data=summary_text,
        file_name=f"rxhandoff_{date.today().isoformat()}_{st.session_state.shift[:3].lower()}.txt",
        mime="text/plain"
    )
with col2:
    summary_json = json.dumps({
        "date": str(date.today()),
        "shift": st.session_state.shift,
        "prepared_by": st.session_state.current_pharmacist,
        "issues": issues,
        "notes": st.session_state.notes,
    }, indent=2)
    st.download_button(
        "⬇ Download JSON (EHR import)",
        data=summary_json,
        file_name=f"rxhandoff_{date.today().isoformat()}.json",
        mime="application/json"
    )
```
