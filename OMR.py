import streamlit as st
import pandas as pd
import time

# ---------------------------------------------------------
# 1. 정답 데이터베이스 (진도별 + 동형)
# ---------------------------------------------------------
EXAM_DB = {
    "진도별 모의고사": {
        1: [1, 1, 2, 1, 4, 3, 2, 2, 3, 3, 2, 4, 4, 3, 3, 3, 2, 3, 3, 2],
        2: [3, 1, 3, 2, 4, 1, 2, 4, 3, 2, 4, 2, 3, 1, 4, 2, 4, 3, 2, 2],
        3: [2, 2, 1, 3, 2, 2, 3, 2, 3, 4, 1, 3, 4, 2, 2, 4, 3, 2, 2, 4],
        4: [4, 2, 4, 1, 2, 1, 2, 3, 3, 3, 2, 3, 2, 1, 1, 4, 3, 4, 1, 2],
        5: [1, 2, 2, 2, 2, 4, 2, 3, 3, 2, 1, 4, 3, 2, 4, 4, 3, 2, 3, 3],
        6: [3, 1, 4, 3, 1, 1, 1, 4, 4, 4, 2, 1, 4, 4, 4, 2, 2, 3, 2, 3],
        7: [3, 4, 1, 3, 3, 3, 3, 3, 4, 1, 4, 3, 3, 1, 2, 3, 2, 4, 1, 2],
        8: [1, 3, 3, 1, 3, 3, 3, 2, 4, 2, 2, 3, 2, 2, 1, 4, 3, 1, 3, 4],
        9: [2, 2, 4, 4, 3, 2, 4, 4, 3, 3, 4, 2, 2, 3, 2, 3, 3, 1, 2, 2],
        10: [2, 3, 3, 4, 3, 2, 2, 3, 2, 4, 2, 2, 3, 2, 1, 4, 3, 1, 1, 3],
        11: [1, 2, 3, 4, 1, 2, 1, 4, 4, 3, 3, 2, 4, 4, 4, 4, 3, 4, 3, 3],
        12: [3, 1, 4, 3, 2, 4, 1, 1, 4, 1, 2, 4, 2, 3, 2, 2, 4, 4, 1, 4],
    },
    "동형 모의고사": {
        1: [2, 3, 4, 4, 3, 1, 2, 3, 4, 2, 2, 3, 2, 3, 1, 4, 4, 4, 1, 3],
        2: [2, 2, 4, 3, 3, 4, 3, 3, 2, 1, 1, 1, 3, 4, 4, 2, 3, 1, 1, 3],
        3: [2, 2, 3, 4, 3, 4, 1, 2, 3, 2, 2, 1, 4, 4, 1, 2, 4, 3, 1, 2],
        4: [4, 1, 2, 2, 2, 4, 2, 3, 4, 2, 3, 4, 4, 1, 1, 4, 4, 4, 4, 1],
        5: [2, 4, 2, 2, 4, 4, 3, 4, 4, 4, 4, 3, 4, 4, 2, 2, 4, 3, 1, 1],
        6: [2, 3, 4, 2, 2, 3, 3, 4, 4, 1, 4, 2, 1, 2, 1, 2, 3, 3, 4, 1],
        7: [1, 2, 3, 4, 3, 3, 2, 2, 3, 4, 2, 1, 3, 3, 4, 4, 3, 2, 2, 2],
        8: [2, 2, 3, 3, 3, 4, 3, 4, 3, 3, 2, 3, 1, 1, 2, 4, 1, 3, 4, 3],
        9: [2, 4, 3, 1, 1, 4, 3, 3, 4, 3, 1, 3, 2, 1, 1, 1, 2, 1, 4, 1],
        10: [1, 1, 3, 3, 4, 4, 4, 3, 2, 3, 1, 3, 3, 4, 2, 1, 3, 1, 2, 1],
        11: [1, 3, 3, 4, 3, 3, 3, 4, 2, 3, 4, 2, 4, 2, 4, 2, 3, 3, 2, 3],
        12: [2, 2, 3, 2, 4, 3, 4, 2, 4, 3, 3, 1, 1, 2, 2, 2, 4, 3, 2, 4],
    }
}

# ---------------------------------------------------------
# 2. UI 설정 및 CSS
# ---------------------------------------------------------
st.set_page_config(page_title="사회 OMR 채점기", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    div[role="radiogroup"] > label { margin-right: 20px !important; font-size: 1.2rem !important; }
    .question-text { font-size: 1.3rem; font-weight: bold; padding-top: 5px; color: #333; }
    .timer-container { 
        position: sticky; top: 0; z-index: 1000; background-color: white; 
        padding: 10px 0; border-bottom: 2px solid #eee; margin-bottom: 20px;
    }
    .timer-text { 
        font-size: 1.8rem; font-weight: bold; color: #E74C3C; text-align: center; 
        background: #FDEDEC; border: 2px solid #E74C3C; border-radius: 12px; padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 세션 상태 관리
# ---------------------------------------------------------
if 'started' not in st.session_state: st.session_state.started = False
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'form_id' not in st.session_state: st.session_state.form_id = 0
if 'submitted' not in st.session_state: st.session_state.submitted = False
if 'final_time' not in st.session_state: st.session_state.final_time = 0

def reset_exam():
    st.session_state.started = False
    st.session_state.start_time = None
    st.session_state.submitted = False
    st.session_state.form_id += 1 # 폼 ID 변경으로 라디오 버튼 초기화

# ---------------------------------------------------------
# 4. 사이드바 설정
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 시험 설정")
    exam_type = st.radio("시험 종류", ["진도별 모의고사", "동형 모의고사"])
    round_num = st.selectbox("회차 선택", list(EXAM_DB[exam_type].keys()), format_func=lambda x: f"제 {x}회")
    
    # 회차 변경 감지
    current_key = f"{exam_type}_{round_num}"
    if 'last_key' not in st.session_state or st.session_state.last_key != current_key:
        st.session_state.last_key = current_key
        reset_exam()

    st.divider()
    if st.button("🔄 재시험 (리셋)", use_container_width=True):
        reset_exam()
        st.rerun()

# ---------------------------------------------------------
# 5. 실시간 타이머 프래그먼트 (이 부분이 1초마다 실행됨)
# ---------------------------------------------------------
@st.fragment(run_every="1s")
def render_timer():
    if st.session_state.started and not st.session_state.submitted:
        elapsed = int(time.time() - st.session_state.start_time)
        mins, secs = divmod(elapsed, 60)
        st.markdown(f'<div class="timer-text">⏱️ {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
    elif st.session_state.submitted:
        mins, secs = divmod(st.session_state.final_time, 60)
        st.markdown(f'<div class="timer-text" style="color:#27AE60; border-color:#27AE60; background:#EAFAF1;">✅ 종료 {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. 메인 화면 로직
# ---------------------------------------------------------
st.title(f"✍️ {exam_type} {round_num}회")

if not st.session_state.started:
    st.info("준비가 되면 아래 버튼을 눌러주세요. 시계가 시작됩니다.")
    if st.button("🚀 풀이 시작", use_container_width=True, type="primary"):
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.session_state.submitted = False
        st.rerun()
else:
    # 1초마다 업데이트되는 타이머 노출
    st.markdown('<div class="timer-container">', unsafe_allow_html=True)
    render_timer()
    st.markdown('</div>', unsafe_allow_html=True)

    # OMR 카드 폼
    with st.form(key=f"omr_{st.session_state.form_id}"):
        user_ans = {}
        for i in range(1, 21):
            c1, c2 = st.columns([1, 4])
            with c1: st.markdown(f'<div class="question-text">{i}번</div>', unsafe_allow_html=True)
            with c2: user_ans[i] = st.radio(f"Q{i}", [1, 2, 3, 4], horizontal=True, index=None, label_visibility="collapsed", key=f"q_{i}_{st.session_state.form_id}")
            if i % 5 == 0 and i != 20: st.divider()

        st.markdown("---")
        submit_btn = st.form_submit_button("💯 채점 및 제출", use_container_width=True, type="primary")

    if submit_btn:
        st.session_state.submitted = True
        st.session_state.final_time = int(time.time() - st.session_state.start_time)
        
        # 채점 계산
        ans_list = EXAM_DB[exam_type][round_num]
        score = sum(5 for i in range(1, 21) if user_ans.get(i) == ans_list[i-1])
        wrongs = [{"번호": f"{i}번", "내 답": user_ans.get(i) if user_ans.get(i) else "미입력", "정답": ans_list[i-1]} 
                  for i in range(1, 21) if user_ans.get(i) != ans_list[i-1]]

        st.divider()
        st.markdown(f"### 📊 결과: **{score}점**")
        if wrongs:
            st.markdown("#### ❌ 오답 노트")
            st.table(pd.DataFrame(wrongs))
        else:
            st.balloons()
            st.success("만점입니다! 축하드려요! 🏆")
