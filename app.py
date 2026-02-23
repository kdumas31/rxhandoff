import streamlit as st
import json
from datetime import datetime, date
import uuid

st.set_page_config(
    page_title="RxHandoff | Pharmacy Shift Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# — Inject custom CSS ————————————————————————————————————————

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,600;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}
h1, h2, h3, h4 {
    font-family: 'IBM Plex Mono', monospace !important;
}
.stApp {
    background-color: #0d1117;
    color: #e6edf3;
}
.block-container {
    padding-top: 1.5rem;
}
div[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}
.rx-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.rx-card.urgent {
    border-left: 4px solid #f85149;
}
.rx-card.watch {
    border-left: 4px solid #d29922;
}
.rx-card.stable {
    border-left: 4px solid #3fb950;
}
.tag {
    display: inline-block;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.72rem;
    font-family: 'IBM Plex Mono', monospace;
    margin-right: 4px;
    color: #8b949e;
}
.shift-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: #8b949e;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}
</style>
""", unsafe_allow_html=True)

# — Session State Init ————————————————————————————————————————

def init_state():
    if "issues" not in st.session_state:
        st.session_state.issues = [
            {
                "id": str(uuid.uuid4()),
                "mrn": "MRN-004821",
                "name": "J. Whitfield",
                "unit": "MICU",
                "bed": "12B",
                "category": "Anticoagulation",
                "priority": "Urgent",
                "summary": "Heparin drip — anti-Xa level 0.18 (subtherapeutic). MD notified, awaiting order to uptitrate.",
                "status": "Awaiting MD",
                "flag_callback": True,
                "flag_level_pending": True,
                "ts": "06:42",
            },
            {
                "id": str(uuid.uuid4()),
                "mrn": "MRN-009137",
                "name": "R. Okonkwo",
                "unit": "5 West",
                "bed": "518",
                "category": "Drug Interaction",
                "priority": "Urgent",
                "summary": "Warfarin + fluconazole started today. INR 2.1 — expect significant elevation. Recommend warfarin hold x2 doses and recheck INR tomorrow.",
                "status": "Pending",
                "flag_callback": False,
                "flag_level_pending": False,
                "ts": "07:05",
            },
            {
                "id": str(uuid.uuid4()),
                "mrn": "MRN-002255",
                "name": "T. Nguyen",
                "unit": "6 East",
                "bed": "604",
                "category": "Renal Dosing",
                "priority": "Watch",
                "summary": "Vancomycin AUC/MIC monitoring — trough 22.4 (high). Dose held. Renal dosing per pharmacy protocol. Next level at 1400.",
                "status": "Monitoring",
                "flag_callback": False,
                "flag_level_pending": True,
                "ts": "05:30",
            },
            {
                "id": str(uuid.uuid4()),
                "mrn": "MRN-007744",
                "name": "M. Delgado",
                "unit": "CVICU",
                "bed": "3A",
                "category": "IV Shortage",
                "priority": "Watch",
                "summary": "NS 0.9% bags on allocation — switched to LR per shortage protocol. Attending aware. Watch for any CI to LR.",
                "status": "Monitoring",
                "flag_callback": False,
                "flag_level_pending": False,
                "ts": "06:15",
            },
            {
                "id": str(uuid.uuid4()),
                "mrn": "MRN-001190",
                "name": "S. Patel",
                "unit": "7 North",
                "bed": "714",
                "category": "High-Alert Med",
                "priority": "Stable",
                "summary": "Insulin infusion transitioning to SQ regimen. Endocrine consulted. Basal dose confirmed. No further pharmacy action needed.",
                "status": "Resolved",
                "flag_callback": False,
                "flag_level_pending": False,
                "ts": "04:50",
            },
        ]
    if "shift_notes" not in st.session_state:
        st.session_state.shift_notes = [
            {
                "id": str(uuid.uuid4()),
                "ts": "06:00",
                "author": "Night RPh",
                "note": "NS 0.9% 1L bags limited to 2 per patient per shift. Use LR as substitute per shortage memo. PYXIS cabinet B3 restocked.",
            },
            {
                "id": str(uuid.uuid4()),
                "ts": "05:15",
                "author": "Night RPh",
                "note": "IV room down 1 tech until 0900. Stat IV requests may have 20-min delay. Notify charge nurse on 5W and 6E.",
            },
        ]
    if "shift_start" not in st.session_state:
        st.session_state.shift_start = datetime.now().strftime("%Y-%m-%d %H:%M")

init_state()

# — Sidebar ————————————————————————————————————————————————

with st.sidebar:
    st.markdown('<div class="shift-header">RxHandoff</div>', unsafe_allow_html=True)
    st.markdown("## 💊 Pharmacy")
    st.markdown("**Shift started:** " + st.session_state.shift_start)
    st.divider()

    page = st.radio(
        "Navigate",
        ["Handoff Board", "Log Issue", "Shift Notes", "Shift Summary"],
        label_visibility="collapsed",
    )
    st.divider()

    units = sorted(set(i["unit"] for i in st.session_state.issues))
    unit_filter = st.multiselect("Filter by Unit", units, default=units)

    priorities = ["Urgent", "Watch", "Stable"]
    priority_filter = st.multiselect("Filter by Priority", priorities, default=priorities)

    st.divider()
    open_count = sum(1 for i in st.session_state.issues if i["status"] != "Resolved")
    urgent_count = sum(1 for i in st.session_state.issues if i["priority"] == "Urgent" and i["status"] != "Resolved")
    st.metric("Open Issues", open_count)
    st.metric("Urgent", urgent_count)

# — Helper ————————————————————————————————————————————————————

PRIORITY_COLOR = {"Urgent": "urgent", "Watch": "watch", "Stable": "stable"}
STATUS_OPTIONS = ["Pending", "Awaiting MD", "Monitoring", "Resolved"]
CATEGORIES = [
    "Renal Dosing", "Drug Interaction", "High-Alert Med",
    "Anticoagulation", "IV Shortage", "TPN/Nutrition",
    "Antimicrobial Stewardship", "Pain/Sedation", "Other",
]

def filtered_issues():
    return [
        i for i in st.session_state.issues
        if i["unit"] in unit_filter and i["priority"] in priority_filter
    ]

# — Page: Handoff Board ———————————————————————————————————————

if page == "Handoff Board":
    st.markdown("## 📋 Handoff Board")
    col_a, col_b = st.columns([3, 1])
    with col_b:
        show_resolved = st.toggle("Show Resolved", value=False)

    issues = filtered_issues()
    if not show_resolved:
        issues = [i for i in issues if i["status"] != "Resolved"]

    # Sort: Urgent → Watch → Stable
    priority_order = {"Urgent": 0, "Watch": 1, "Stable": 2}
    issues = sorted(issues, key=lambda x: priority_order.get(x["priority"], 3))

    if not issues:
        st.info("No open issues matching current filters.")
    else:
        for issue in issues:
            css_class = PRIORITY_COLOR.get(issue["priority"], "stable")
            flags = ""
            if issue.get("flag_callback"):
                flags += '<span class="tag">📞 Callback</span>'
            if issue.get("flag_level_pending"):
                flags += '<span class="tag">🧪 Level Pending</span>'

            st.markdown(f"""
<div class="rx-card {css_class}">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.8rem;color:#8b949e;">{issue['ts']} · {issue['mrn']} · {issue['unit']} {issue['bed']}</span>
    <span class="tag">{issue['priority']}</span>
  </div>
  <div style="font-weight:600;margin:6px 0 4px;">{issue['name']}</div>
  <div style="font-size:0.88rem;color:#c9d1d9;margin-bottom:8px;">{issue['summary']}</div>
  <span class="tag">{issue['category']}</span>
  {flags}
</div>
""", unsafe_allow_html=True)

            with st.expander("Update status", expanded=False):
                new_status = st.selectbox(
                    "Status",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(issue["status"]),
                    key="status_" + issue["id"],
                )
                if st.button("Save", key="save_" + issue["id"]):
                    for i in st.session_state.issues:
                        if i["id"] == issue["id"]:
                            i["status"] = new_status
                    st.rerun()

# — Page: Log Issue ———————————————————————————————————————————

elif page == "Log Issue":
    st.markdown("## ➕ Log New Issue")
    with st.form("log_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        mrn = c1.text_input("MRN", placeholder="MRN-XXXXXX")
        name = c2.text_input("Patient Name", placeholder="Last, First")
        unit = c3.text_input("Unit", placeholder="e.g. MICU")

        c4, c5, c6 = st.columns(3)
        bed = c4.text_input("Bed", placeholder="e.g. 12B")
        category = c5.selectbox("Category", CATEGORIES)
        priority = c6.selectbox("Priority", ["Urgent", "Watch", "Stable"])

        summary = st.text_area("Clinical Summary", placeholder="Describe the issue, relevant labs, actions taken, and what the oncoming pharmacist needs to do.", height=120)

        c7, c8 = st.columns(2)
        flag_callback = c7.checkbox("MD Callback Needed")
        flag_level_pending = c8.checkbox("Lab Level Pending")

        submitted = st.form_submit_button("Log Issue", use_container_width=True)
        if submitted:
            if mrn and name and summary:
                new_issue = {
                    "id": str(uuid.uuid4()),
                    "mrn": mrn,
                    "name": name,
                    "unit": unit,
                    "bed": bed,
                    "category": category,
                    "priority": priority,
                    "summary": summary,
                    "status": "Pending",
                    "flag_callback": flag_callback,
                    "flag_level_pending": flag_level_pending,
                    "ts": datetime.now().strftime("%H:%M"),
                }
                st.session_state.issues.insert(0, new_issue)
                st.success("Issue logged successfully.")
            else:
                st.error("MRN, patient name, and summary are required.")

# — Page: Shift Notes ————————————————————————————————————————

elif page == "Shift Notes":
    st.markdown("## 📝 Shift Notes")
    st.caption("Department-wide notes: shortages, staffing, equipment — not tied to a specific patient.")

    with st.form("note_form", clear_on_submit=True):
        author = st.text_input("Your Name / Role", placeholder="e.g. Night RPh")
        note_text = st.text_area("Note", placeholder="Enter shift note...", height=100)
        if st.form_submit_button("Add Note", use_container_width=True):
            if note_text:
                st.session_state.shift_notes.insert(0, {
                    "id": str(uuid.uuid4()),
                    "ts": datetime.now().strftime("%H:%M"),
                    "author": author or "Anon",
                    "note": note_text,
                })
                st.success("Note added.")

    st.divider()
    for n in st.session_state.shift_notes:
        st.markdown(f"""
<div class="rx-card stable">
  <div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.75rem;color:#8b949e;">{n['ts']} · {n['author']}</div>
  <div style="margin-top:6px;font-size:0.9rem;">{n['note']}</div>
</div>
""", unsafe_allow_html=True)

# — Page: Shift Summary ——————————————————————————————————————

elif page == "Shift Summary":
    st.markdown("## 📊 Shift Summary")
    issues_all = st.session_state.issues
    total = len(issues_all)
    resolved = sum(1 for i in issues_all if i["status"] == "Resolved")
    open_issues = total - resolved

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Issues", total)
    col2.metric("Open", open_issues)
    col3.metric("Resolved", resolved)
    col4.metric("Urgent Open", sum(1 for i in issues_all if i["priority"] == "Urgent" and i["status"] != "Resolved"))

    st.divider()
    st.markdown("### Open Issues by Priority")
    for priority in ["Urgent", "Watch", "Stable"]:
        group = [i for i in issues_all if i["priority"] == priority and i["status"] != "Resolved"]
        if group:
            st.markdown(f"**{priority}** ({len(group)})")
            for i in group:
                st.markdown(f"- `{i['mrn']}` {i['name']} — {i['unit']} {i['bed']} — {i['category']} — *{i['status']}*")

    st.divider()
    st.markdown("### Shift Notes")
    for n in st.session_state.shift_notes:
        st.markdown(f"- `{n['ts']}` **{n['author']}**: {n['note']}")

    st.divider()
    summary_data = {
        "shift_start": st.session_state.shift_start,
        "generated_at": datetime.now().isoformat(),
        "open_issues": [i for i in issues_all if i["status"] != "Resolved"],
        "resolved_issues": [i for i in issues_all if i["status"] == "Resolved"],
        "shift_notes": st.session_state.shift_notes,
    }

    col_a, col_b = st.columns(2)
    with col_a:
        txt_lines = [
            "RXHANDOFF — SHIFT SUMMARY",
            "=" * 40,
            "Shift Start: " + st.session_state.shift_start,
            "Generated:   " + datetime.now().strftime("%Y-%m-%d %H:%M"),
            "",
            "OPEN ISSUES",
            "-" * 40,
        ]
        for i in [x for x in issues_all if x["status"] != "Resolved"]:
            txt_lines.append(f"[{i['priority'].upper()}] {i['mrn']} {i['name']} ({i['unit']} {i['bed']})")
            txt_lines.append(f"  Category: {i['category']}")
            txt_lines.append(f"  Status:   {i['status']}")
            txt_lines.append(f"  Summary:  {i['summary']}")
            txt_lines.append("")
        txt_lines += [
            "SHIFT NOTES",
            "-" * 40,
        ]
        for n in st.session_state.shift_notes:
            txt_lines.append(f"[{n['ts']}] {n['author']}: {n['note']}")

        txt_out = "\n".join(txt_lines)
        st.download_button(
            "Download .txt Handoff",
            data=txt_out,
            file_name="rxhandoff_" + date.today().isoformat() + ".txt",
            mime="text/plain",
            use_container_width=True,
        )
    with col_b:
        st.download_button(
            "Download .json (EHR Import)",
            data=json.dumps(summary_data, indent=2),
            file_name="rxhandoff_" + date.today().isoformat() + ".json",
            mime="application/json",
            use_container_width=True,
        )
