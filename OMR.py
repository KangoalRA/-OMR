import streamlit as st
import pandas as pd
import time

# ---------------------------------------------------------
# 1. 정답 데이터베이스
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
# 2. 세션 상태 및 초기화 로직
# ---------------------------------------------------------
st.set_page_config(page_title="사회 OMR 채점기", layout="centered", initial_sidebar_state="auto")

# CSS 설정
st.markdown("""
<style>
    div[role="radiogroup"] > label { margin-right: 15px !important; font-size: 1.1rem !important; }
    .question-text { font-size: 1.2rem; font-weight: bold; padding-top: 5px; }
    .timer-text { font-size: 1.5rem; font-weight: bold; color: #ff4b4b; text-align: center; border: 2px solid #ff4b4b; border-radius: 10px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# 변수 초기화 함수
def reset_exam_state():
    st.session_state.started = False
    st.session_state.start_time = None
    st.session_state.current_score = None
    # radio 버튼들을 초기화하기 위해 key를 변경함
    st.session_state.form_key = time.time() 

if 'started' not in st.session_state:
    reset_exam_state()

# ---------------------------------------------------------
# 3. 사이드바 설정
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 시험 설정")
    exam_type = st.radio("시험 종류", ["진도별 모의고사", "동형 모의고사"])
    available_rounds = list(EXAM_DB[exam_type].keys())
    round_num = st.selectbox("회차 선택", available_rounds, format_func=lambda x: f"제 {x}회")
    
    # 회차가 바뀌면 모든 데이터 리셋
    current_round_id = f"{exam_type}_{round_num}"
    if 'last_round_id' not in st.session_state or st.session_state.last_round_id != current_round_id:
        st.session_state.last_round_id = current_round_id
        reset_exam_state()
        st.rerun()

    st.markdown("---")
    if st.button("🔄 전체 초기화 (재시험)", use_container_width=True):
        reset_exam_state()
        st.rerun()

# ---------------------------------------------------------
# 4. 메인 화면 및 타이머 로직
# ---------------------------------------------------------
st.title(f"📝 {exam_type} 제 {round_num}회")

if not st.session_state.started:
    st.info("아래 버튼을 누르면 타이머가 작동하며 OMR 카드가 나타납니다.")
    if st.button("🚀 풀이 시작", use_container_width=True, type="primary"):
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.rerun()
else:
    # 타이머 표시 영역
    timer_placeholder = st.empty()
    elapsed = int(time.time() - st.session_state.start_time)
    mins, secs = divmod(elapsed, 60)
    timer_placeholder.markdown(f'<div class="timer-text">⏱️ 경과 시간: {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)

    # OMR 폼 시작
    with st.form(key=f"omr_form_{st.session_state.form_key}"):
        user_answers = {}
        for i in range(1, 21):
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f'<div class="question-text">{i}번</div>', unsafe_allow_html=True)
            with col2:
                user_answers[i] = st.radio(f"Q{i}", [1, 2, 3, 4], horizontal=True, index=None, label_visibility="collapsed", key=f"ans_{i}_{st.session_state.form_key}")
            if i % 5 == 0 and i != 20:
                st.divider()

        st.markdown("---")
        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            submitted = st.form_submit_button("💯 채점하기", use_container_width=True, type="primary")
        with col_sub2:
            retest = st.form_submit_button("🔄 다시 풀기", use_container_width=True)

    if retest:
        reset_exam_state()
        st.rerun()

    # ---------------------------------------------------------
    # 5. 채점 결과
    # ---------------------------------------------------------
    if submitted:
        finish_time = int(time.time() - st.session_state.start_time)
        f_mins, f_secs = divmod(finish_time, 60)
        
        correct_answers = EXAM_DB[exam_type][round_num]
        score = 0
        wrong_list = []
        
        for i in range(1, 21):
            if user_answers.get(i) == correct_answers[i-1]:
                score += 5
            else:
                wrong_list.append((i, user_answers.get(i), correct_answers[i-1]))
        
        st.divider()
        st.balloons()
        st.markdown(f"### 📊 결과: **{score}점**")
        st.markdown(f"⏱️ **총 소요 시간:** {f_mins}분 {f_secs}초")
        
        if wrong_list:
            st.markdown("#### ❌ 오답 확인")
            res_df = pd.DataFrame([{"번호": f"{q}번", "내 답": u if u else "미입력", "정답": c} for q, u, c in wrong_list])
            st.table(res_df)
        else:
            st.success("와우! 만점입니다! 대단해요! 🏆")

# 타이머 실시간 업데이트를 위한 스크립트 (사용자가 아무것도 안 해도 1초마다 갱신되길 원할 경우)
# 단, Streamlit의 특성상 입력 중 갱신되면 불편할 수 있어 자동 갱신은 빼고 입력 시마다 갱신되게 두었습니다.
