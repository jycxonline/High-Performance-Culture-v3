"""Streamlit pages for the PACE gamification layer (single-department)."""
from __future__ import annotations
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from .engine import (
    ACTIVATION_THRESHOLD, load_lookup, save_lookup, compute_stage, advance_stage,
    badges_earned, checkpoint_challenges, assign_random_destination, log_admin_action,
    save_action_plan, load_action_plan, save_checkpoint_update, load_checkpoints,
)
from .pace_track import render_pace_journey
from ..config_loader import BRAND

NAVY = "#1F3864"; GOLD = "#BF9000"


def _hero(title, subtitle):
    st.markdown(f"""<div style="background:linear-gradient(135deg,{NAVY} 0%,#2A4A7F 100%);
    color:white;padding:1.6rem 2rem;border-radius:8px;margin-bottom:1.5rem;border-bottom:3px solid {GOLD};">
    <h1 style="color:white;margin:0;font-size:1.7rem">{title}</h1>
    <p style="color:#D9E2F3;margin:0.4rem 0 0 0;font-size:0.95rem">{subtitle}</p></div>""", unsafe_allow_html=True)


def _dept_picker(depts, key="dept_picker"):
    if not depts:
        st.info("No departments found in the Department Lookup file."); return None
    labels = [f"{d.dept_code} — {d.dept_name}" for d in depts]
    options = ["— Select a department to view its PACE journey —"] + labels
    choice = st.selectbox("Choose a department", options, key=key, label_visibility="collapsed")
    if choice == options[0]: return None
    code = choice.split(" — ")[0]
    return next(d for d in depts if d.dept_code == code)


def page_pace(lookup_path, action_plan_dir):
    _hero("PACE", f"Select a department to view its PACE journey. {BRAND}.")
    if not Path(lookup_path).exists():
        st.error("Department Lookup file not found. Upload one via PACE Admin."); return
    depts = load_lookup(lookup_path)
    for d in depts: d.stage = compute_stage(d)
    dept = _dept_picker(depts, key="pace_picker")
    if dept is None:
        st.markdown("### Overall PACE progress")
        total = len(depts)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total departments", total)
        c2.metric("In Training (>=70%)", sum(1 for d in depts if d.completion_pct >= ACTIVATION_THRESHOLD))
        c3.metric("Implementing change", sum(1 for d in depts if d.action_plan_submitted))
        c4.metric("Finished", sum(1 for d in depts if d.destination_assigned))
        st.info("👆 Select a department above to see its individual PACE journey.")
        rows = [{"Code": d.dept_code, "Department": d.dept_name, "Completion %": f"{d.completion_pct:.0%}",
                  "Current stage": d.stage_display, "Badges": f"{len(badges_earned(d))} / 9"} for d in depts]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        return

    st.markdown("### PACE journey")
    st.pyplot(render_pace_journey(dept), use_container_width=True)
    c1, c2 = st.columns([2, 3])
    with c1:
        st.markdown("#### Department profile")
        rows = [("Code", dept.dept_code), ("Runner colour", dept.runner_colour),
                ("Responses", f"{dept.actual} of {dept.expected} ({dept.completion_pct:.0%})"),
                ("Current stage", dept.stage_display),
                ("Status", "In Training (>=70%)" if dept.is_activated else "Warming up (<70%)")]
        if dept.destination_assigned and dept.destination:
            rows.append(("Medal", dept.destination))
        for k, v in rows: st.markdown(f"**{k}:** {v}")
    with c2:
        st.markdown("#### Progression")
        cc1, cc2 = st.columns(2)
        flags = [("Report Reviewed", dept.report_reviewed), ("Action Plan Submitted", dept.action_plan_submitted),
                 ("Checkpoint 1", dept.checkpoint_1), ("Checkpoint 2", dept.checkpoint_2),
                 ("Checkpoint 3", dept.checkpoint_3), ("Finish Line", dept.destination_assigned)]
        for i, (name, val) in enumerate(flags):
            with (cc1 if i < 3 else cc2): st.markdown(f"{'✅' if val else '⬜'} {name}")
        st.markdown("#### Badges earned")
        earned = badges_earned(dept)
        if not earned: st.caption("No badges yet.")
        else:
            st.markdown(" ".join(f'<span style="display:inline-block;padding:4px 10px;margin:3px;'
                f'border-radius:12px;font-size:0.8rem;background:{GOLD};color:white;font-weight:600">🏅 {b}</span>'
                for b in earned), unsafe_allow_html=True)


def page_submit_action_plan(lookup_path, action_plan_dir, get_analysis_for_dept):
    _hero("Implement Change — Action Plan", "Translate your PACE diagnostic report into an action plan.")
    if not Path(lookup_path).exists():
        st.error("Lookup file not found."); return
    depts = load_lookup(lookup_path)
    for d in depts: d.stage = compute_stage(d)
    dept = _dept_picker(depts, key="ap_picker")
    if dept is None: st.info("👆 Select your department above."); return
    weakest = None
    try:
        a = get_analysis_for_dept(dept.dept_name)
        if a is not None: weakest = min(a.focus.pillar_means, key=a.focus.pillar_means.get)
    except Exception: pass
    st.markdown(f"""<div style="background:#D9E2F3;padding:1rem 1.2rem;border-left:4px solid {NAVY};
    border-radius:4px;margin:0.8rem 0"><b>Department:</b> {dept.dept_name} ({dept.dept_code})<br>
    <b>Current stage:</b> {dept.stage_display}<br><b>Completion:</b> {dept.actual}/{dept.expected} ({dept.completion_pct:.0%})
    {'<br><b>Priority element:</b> ' + weakest if weakest else ''}</div>""", unsafe_allow_html=True)
    existing = load_action_plan(action_plan_dir, dept.dept_id) or {}
    with st.form(f"ap_{dept.dept_id}"):
        st.markdown("### Action Plan")
        insight = st.text_area("1. Key insight from the report", value=existing.get("insight", ""), height=80)
        pillars = ["Purpose", "Alliance", "Coordination", "Excellence"]
        default_p = existing.get("priority_pillar") or (weakest or "Purpose")
        pillar = st.selectbox("2. Priority element", pillars, index=pillars.index(default_p) if default_p in pillars else 0)
        commitment = st.text_area("3. Commitment statement", value=existing.get("commitment", ""), height=100)
        st.markdown("**4. Actions**")
        existing_actions = existing.get("actions", [])
        while len(existing_actions) < 3:
            existing_actions.append({"action": "", "owner": "", "timeline": "", "success_measure": ""})
        new_actions = []
        for i in range(3):
            st.markdown(f"**Action {i+1}**")
            a_ = st.text_input(f"Description ({i+1})", value=existing_actions[i].get("action", ""), key=f"act_{dept.dept_id}_{i}")
            cc1, cc2 = st.columns(2)
            with cc1: o = st.text_input(f"Owner ({i+1})", value=existing_actions[i].get("owner", ""), key=f"own_{dept.dept_id}_{i}")
            with cc2: t = st.text_input(f"Timeline ({i+1})", value=existing_actions[i].get("timeline", ""), key=f"tim_{dept.dept_id}_{i}")
            m = st.text_input(f"Success measure ({i+1})", value=existing_actions[i].get("success_measure", ""), key=f"suc_{dept.dept_id}_{i}")
            new_actions.append({"action": a_, "owner": o, "timeline": t, "success_measure": m})
        support = st.text_area("5. Support required", value=existing.get("support_required", ""), height=80)
        if st.form_submit_button("📨 Submit action plan", type="primary"):
            plan = {"dept_id": dept.dept_id, "dept_name": dept.dept_name, "insight": insight.strip(),
                    "priority_pillar": pillar, "commitment": commitment.strip(),
                    "actions": [a for a in new_actions if a.get("action", "").strip()],
                    "support_required": support.strip(), "status": "Submitted — awaiting admin approval"}
            if not insight or not commitment or not plan["actions"]:
                st.error("Please fill in insight, commitment, and at least one action.")
            else:
                save_action_plan(action_plan_dir, dept.dept_id, plan); st.success("✅ Action plan submitted."); st.balloons()


def page_checkpoint_update(lookup_path, action_plan_dir, get_analysis_for_dept):
    _hero("Checkpoint Update", "Submit a progress update at each PACE checkpoint.")
    if not Path(lookup_path).exists():
        st.error("Lookup file not found."); return
    depts = load_lookup(lookup_path)
    for d in depts: d.stage = compute_stage(d)
    eligible = [d for d in depts if d.action_plan_submitted]
    if not eligible: st.info("No departments have started implementing change yet."); return
    dept = _dept_picker(eligible, key="cp_picker")
    if dept is None: st.info("👆 Select your department."); return
    weakest = None
    try:
        a = get_analysis_for_dept(dept.dept_name)
        if a is not None: weakest = min(a.focus.pillar_means, key=a.focus.pillar_means.get)
    except Exception: pass
    challenges = checkpoint_challenges(weakest)
    existing = load_checkpoints(action_plan_dir, dept.dept_id)
    if not dept.checkpoint_1: next_cp = 1
    elif not dept.checkpoint_2: next_cp = 2
    elif not dept.checkpoint_3: next_cp = 3
    else: st.success("🎉 All three checkpoints complete — ready for the finish line."); return
    cp_name = list(challenges.keys())[next_cp - 1]; cp = challenges[cp_name]
    st.markdown(f"### 📍 {cp_name}")
    st.markdown(f"**Focus:** {cp['focus']}")
    st.markdown(f"""<div style="background:#FFF3D9;padding:1rem;border-left:4px solid {GOLD};
    border-radius:4px;margin:0.8rem 0"><b>⚠️ Challenge:</b> {cp['challenge']}</div>""", unsafe_allow_html=True)
    if cp.get("priority_hint"):
        st.markdown(f"""<div style="background:#D9E2F3;padding:0.8rem;border-left:4px solid {NAVY};
        border-radius:4px;margin:0.8rem 0;font-size:0.9rem">💡 <b>Priority insight:</b> {cp['priority_hint']}</div>""", unsafe_allow_html=True)
    st.markdown(f"**Prompt:** {cp['prompt']}")
    with st.form(f"cp_{dept.dept_id}_{next_cp}"):
        prior = existing.get(f"checkpoint_{next_cp}", {}).get("update_text", "")
        text = st.text_area("Your progress update", value=prior, height=180)
        st.file_uploader("Optional evidence", type=["png", "jpg", "jpeg", "pdf", "docx"])
        if st.form_submit_button(f"📨 Submit Checkpoint {next_cp}", type="primary"):
            if not text.strip(): st.error("Please write your update.")
            else:
                save_checkpoint_update(action_plan_dir, dept.dept_id, next_cp, text.strip())
                st.success(f"✅ Checkpoint {next_cp} submitted."); st.balloons()


def page_pace_admin(lookup_path, action_plan_dir, data_dir):
    _hero("PACE Admin", "Manage the PACE journey.")
    admin_user = st.text_input("Admin identity", value=st.session_state.get("admin_user", "OD"))
    st.session_state["admin_user"] = admin_user
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Lookup File", "🏃 Departments", "🎛️ Action Plans", "🏆 Progress"])

    with tab1:
        st.markdown("### Department Lookup File")
        c1, c2 = st.columns(2)
        with c1:
            if Path(lookup_path).exists():
                with open(lookup_path, "rb") as f:
                    st.download_button("⬇️ Download current lookup", f.read(), file_name="PACE_Department_Lookup.xlsx")
            else: st.warning("No lookup file loaded.")
        with c2:
            up = st.file_uploader("Upload new lookup", type=["xlsx"])
            if up is not None:
                tmp = Path(data_dir) / f"_incoming_lookup_{up.name}"; tmp.write_bytes(up.getvalue())
                try:
                    incoming = load_lookup(str(tmp)); st.success(f"✅ Valid. {len(incoming)} depts.")
                    if st.button("Apply ✓", type="primary"):
                        backup = Path(data_dir) / f"PACE_Department_Lookup.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
                        if Path(lookup_path).exists(): shutil.copy(lookup_path, backup)
                        shutil.copy(tmp, lookup_path); tmp.unlink(missing_ok=True)
                        log_admin_action(lookup_path, admin_user, "Uploaded lookup", "All", f"{len(incoming)} depts")
                        st.success(f"✅ Updated. Backup: {backup.name}"); st.rerun()
                except Exception as e:
                    st.error(f"❌ Rejected: {e}"); tmp.unlink(missing_ok=True)

    with tab2:
        if not Path(lookup_path).exists(): st.warning("Upload a lookup file first.")
        else:
            depts = load_lookup(lookup_path)
            for d in depts: d.stage = compute_stage(d)
            dept = _dept_picker(depts, key="admin_picker")
            if dept is None: st.info("👆 Select a department.")
            else:
                st.markdown(f"### {dept.dept_name} · {dept.stage_display}")
                c1, c2, c3 = st.columns([3, 2, 2])
                with c1:
                    st.markdown(f"**Completion:** {dept.actual}/{dept.expected} ({dept.completion_pct:.0%})")
                    new_actual = st.number_input("Update responses", min_value=0, value=dept.actual, key=f"act_{dept.dept_id}")
                    if new_actual != dept.actual and st.button("Save", key=f"save_{dept.dept_id}"):
                        dept.actual = int(new_actual)
                        dept.completion_pct = (dept.actual / dept.expected) if dept.expected else 0
                        dept.stage = compute_stage(dept); save_lookup(lookup_path, [dept])
                        log_admin_action(lookup_path, admin_user, "Updated responses", dept.dept_name, f"→ {dept.actual}"); st.rerun()
                with c2:
                    st.markdown("**Progression**")
                    for lbl, val in [("Report Reviewed", dept.report_reviewed), ("Action Plan", dept.action_plan_submitted),
                                     ("Checkpoint 1", dept.checkpoint_1), ("Checkpoint 2", dept.checkpoint_2),
                                     ("Checkpoint 3", dept.checkpoint_3), ("Finish Line", dept.destination_assigned)]:
                        st.markdown(f"{'✅' if val else '⬜'} {lbl}")
                with c3:
                    st.markdown("**Next admin action**")
                    if not dept.report_reviewed:
                        if st.button("✅ Mark Report Reviewed", key=f"rep_{dept.dept_id}"):
                            dept = advance_stage(dept, "mark_report_reviewed"); save_lookup(lookup_path, [dept])
                            log_admin_action(lookup_path, admin_user, "Report reviewed", dept.dept_name, ""); st.rerun()
                    elif not dept.action_plan_submitted:
                        plan = load_action_plan(action_plan_dir, dept.dept_id)
                        if plan:
                            st.caption(f"📄 Plan ({len(plan.get('actions', []))} actions)")
                            if st.button("🏃 Approve → Implement", key=f"apr_{dept.dept_id}", type="primary"):
                                dept = advance_stage(dept, "approve_action_plan"); save_lookup(lookup_path, [dept])
                                log_admin_action(lookup_path, admin_user, "Approved plan", dept.dept_name, ""); st.rerun()
                        else: st.caption("Awaiting plan submission.")
                    elif not dept.checkpoint_1:
                        if st.button("✅ Sign off CP1", key=f"cp1_{dept.dept_id}"):
                            dept = advance_stage(dept, "mark_checkpoint_1"); save_lookup(lookup_path, [dept]); st.rerun()
                    elif not dept.checkpoint_2:
                        if st.button("✅ Sign off CP2", key=f"cp2_{dept.dept_id}"):
                            dept = advance_stage(dept, "mark_checkpoint_2"); save_lookup(lookup_path, [dept]); st.rerun()
                    elif not dept.checkpoint_3:
                        if st.button("✅ Sign off CP3", key=f"cp3_{dept.dept_id}"):
                            dept = advance_stage(dept, "mark_checkpoint_3"); save_lookup(lookup_path, [dept]); st.rerun()
                    elif not dept.destination_assigned:
                        medal = assign_random_destination(seed=dept.dept_id)
                        if st.button(f"🏁 Finish Line → {medal}", key=f"dst_{dept.dept_id}", type="primary"):
                            dept.destination = medal; dept = advance_stage(dept, "assign_destination"); save_lookup(lookup_path, [dept])
                            log_admin_action(lookup_path, admin_user, "Finish line", dept.dept_name, medal); st.rerun()
                    else: st.success("🏆 PACE Setter — finished!")
                st.markdown("---"); st.markdown("### PACE journey preview")
                st.pyplot(render_pace_journey(dept), use_container_width=True)

    with tab3:
        st.markdown("### Submitted action plans")
        depts_all = load_lookup(lookup_path) if Path(lookup_path).exists() else []
        found = 0
        for d in depts_all:
            plan = load_action_plan(action_plan_dir, d.dept_id)
            if plan:
                found += 1
                approved = "✅ Approved" if d.action_plan_submitted else "⏳ Awaiting"
                with st.expander(f"{d.dept_code} — {d.dept_name} · {approved}"):
                    st.markdown(f"**Priority element:** {plan.get('priority_pillar','')}")
                    st.markdown(f"**Insight:** {plan.get('insight','')}")
                    st.markdown(f"**Commitment:** {plan.get('commitment','')}")
                    for i, a in enumerate(plan.get("actions", []), start=1):
                        st.markdown(f"{i}. **{a.get('action','')}** — Owner: {a.get('owner','—')} · Timeline: {a.get('timeline','—')}")
        if not found: st.info("No plans submitted yet.")

    with tab4:
        if not Path(lookup_path).exists(): st.warning("Upload lookup first.")
        else:
            depts = load_lookup(lookup_path)
            for d in depts: d.stage = compute_stage(d)
            total = len(depts)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("In Training", sum(1 for d in depts if d.completion_pct >= ACTIVATION_THRESHOLD), f"of {total}")
            c2.metric("Implementing", sum(1 for d in depts if d.action_plan_submitted), f"of {total}")
            c3.metric("Race ready", sum(1 for d in depts if d.checkpoint_3), f"of {total}")
            c4.metric("Finished", sum(1 for d in depts if d.destination_assigned), f"of {total}")
            funnel = pd.DataFrame({
                "PACE Stage": ["Warm-up", "Training", "Reflect", "Implement Change", "Reflect (2)", "Training-Tempo", "Race up PACE", "Finish Line"],
                "Departments": [total, sum(1 for d in depts if d.completion_pct >= ACTIVATION_THRESHOLD),
                    sum(1 for d in depts if d.report_reviewed), sum(1 for d in depts if d.action_plan_submitted),
                    sum(1 for d in depts if d.checkpoint_1), sum(1 for d in depts if d.checkpoint_2),
                    sum(1 for d in depts if d.checkpoint_3), sum(1 for d in depts if d.destination_assigned)]})
            st.dataframe(funnel, use_container_width=True, hide_index=True)
