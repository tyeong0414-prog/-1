import os
import io
import textwrap
from datetime import date

import pandas as pd
import requests
import qrcode
import streamlit as st

st.set_page_config(
    page_title="MY CAREER | 진로탐구",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# 기본 데이터: 고등학생 진로 탐색용 예시 데이터
# -----------------------------
CAREERS = [
    {
        "name": "AI 엔지니어", "field": "IT·컴퓨터", "subfield": "인공지능·데이터",
        "summary": "인공지능 모델과 서비스를 설계·개발하고 실제 문제에 적용합니다.",
        "tasks": "데이터 분석, 머신러닝 모델 개발, AI 서비스 구현 및 성능 평가",
        "skills": ["수학·통계", "프로그래밍", "논리적 사고", "문제 해결", "협업"],
        "majors": ["컴퓨터공학과", "인공지능학과", "데이터사이언스학과", "소프트웨어학과"],
        "subjects": ["수학", "정보", "확률과 통계", "미적분"],
        "activities": ["Python으로 간단한 데이터 분석하기", "AI 윤리 사례 조사하기", "공개 데이터로 분류 모델 탐구하기"],
        "tags": ["탐구형", "현실형", "진취형"],
        "outlook": "AI 기술이 다양한 산업에 적용되며 관련 직무가 확장되고 있습니다. 세부 직무와 채용 수요는 기술·산업 변화에 따라 달라집니다.",
    },
    {
        "name": "소프트웨어 개발자", "field": "IT·컴퓨터", "subfield": "소프트웨어·앱",
        "summary": "사용자와 조직의 요구를 분석해 웹·앱·시스템을 설계하고 구현합니다.",
        "tasks": "요구사항 분석, 프로그램 작성, 테스트, 유지보수 및 협업",
        "skills": ["프로그래밍", "논리적 사고", "문제 해결", "의사소통", "꾸준한 학습"],
        "majors": ["컴퓨터공학과", "소프트웨어학과", "정보통신공학과"],
        "subjects": ["정보", "수학", "영어", "물리학"],
        "activities": ["학교생활에 필요한 작은 앱 기획하기", "GitHub에 프로젝트 기록하기", "사용자 의견을 반영해 프로그램 개선하기"],
        "tags": ["현실형", "탐구형"],
        "outlook": "산업 전반에서 소프트웨어 활용이 이어지고 있습니다. 개발 분야별 기술 변화와 포트폴리오가 중요합니다.",
    },
    {
        "name": "데이터 분석가", "field": "IT·컴퓨터", "subfield": "인공지능·데이터",
        "summary": "데이터를 수집·정리·분석해 의사결정에 필요한 근거를 제공합니다.",
        "tasks": "데이터 정제, 통계 분석, 시각화, 분석 결과 전달",
        "skills": ["통계", "데이터 해석", "시각화", "비판적 사고", "글쓰기"],
        "majors": ["통계학과", "데이터사이언스학과", "산업공학과", "컴퓨터공학과"],
        "subjects": ["확률과 통계", "수학", "정보", "사회·문화"],
        "activities": ["공공데이터포털 자료 분석하기", "설문조사 결과를 그래프로 표현하기", "분석 결과를 한 페이지로 요약하기"],
        "tags": ["탐구형", "관습형"],
        "outlook": "데이터 기반 의사결정이 여러 분야에서 활용됩니다. 분석 도구뿐 아니라 분야별 맥락을 이해하는 역량도 필요합니다.",
    },
    {
        "name": "의사", "field": "의료·생명", "subfield": "의료·보건",
        "summary": "환자의 건강 상태를 진단하고 치료·예방 및 건강 관리에 참여합니다.",
        "tasks": "문진과 진찰, 검사 결과 해석, 치료 계획 수립, 환자와 소통",
        "skills": ["과학적 탐구", "의사소통", "공감", "책임감", "협업"],
        "majors": ["의예과·의학과"],
        "subjects": ["생명과학", "화학", "수학", "영어"],
        "activities": ["질병 예방 캠페인 기획하기", "의료 윤리 쟁점 조사하기", "인체 기관과 항상성 탐구하기"],
        "tags": ["탐구형", "사회형"],
        "outlook": "의료 수요와 보건의료 제도, 전문 분야에 따라 진로 경로가 다양합니다. 교육·수련 과정과 자격 요건을 확인해야 합니다.",
    },
    {
        "name": "생명과학 연구원", "field": "의료·생명", "subfield": "생명과학·바이오",
        "summary": "생명 현상을 연구하고 의약·농업·환경 등 다양한 분야의 지식과 기술을 발전시킵니다.",
        "tasks": "연구 질문 설정, 실험 설계, 자료 분석, 연구 결과 발표",
        "skills": ["생명과학 지식", "실험 설계", "통계", "관찰력", "협업"],
        "majors": ["생명과학과", "생명공학과", "분자생물학과", "바이오융합학과"],
        "subjects": ["생명과학", "화학", "수학", "정보"],
        "activities": ["생명과학 논문 초록 읽기", "생태계 또는 세포 관련 탐구 설계하기", "실험 결과를 표와 그래프로 정리하기"],
        "tags": ["탐구형", "현실형"],
        "outlook": "바이오·의약·농생명·환경 등 다양한 연구 분야가 있습니다. 연구 분야에 따라 대학원 과정이 요구될 수 있습니다.",
    },
    {
        "name": "간호사", "field": "의료·생명", "subfield": "의료·보건",
        "summary": "환자 곁에서 건강 회복과 질병 예방을 돕고 의료팀과 협력합니다.",
        "tasks": "환자 상태 관찰, 간호 수행, 건강 교육, 의료진과 협력",
        "skills": ["공감", "의사소통", "관찰력", "책임감", "협업"],
        "majors": ["간호학과"],
        "subjects": ["생명과학", "화학", "보건", "윤리"],
        "activities": ["응급처치·건강교육 자료 조사하기", "지역사회 건강 문제 탐구하기", "환자 안전 사례 분석하기"],
        "tags": ["사회형", "현실형"],
        "outlook": "병원·지역사회·산업체·공공기관 등 진출 분야가 다양합니다. 면허와 관련 교육과정을 확인해야 합니다.",
    },
    {
        "name": "시각디자이너", "field": "예술·디자인", "subfield": "시각·콘텐츠",
        "summary": "정보와 메시지를 시각적으로 구성해 사람들이 쉽게 이해하고 경험하도록 돕습니다.",
        "tasks": "디자인 기획, 시각 자료 제작, 사용자 피드백 반영, 결과물 개선",
        "skills": ["창의력", "시각적 표현", "관찰력", "소통", "디지털 도구 활용"],
        "majors": ["시각디자인학과", "커뮤니케이션디자인학과", "디지털미디어학과"],
        "subjects": ["미술", "정보", "국어", "사회"],
        "activities": ["공공 캠페인 포스터 제작하기", "앱 화면을 관찰하고 사용성 개선안 만들기", "디자인 의도와 과정을 포트폴리오로 기록하기"],
        "tags": ["예술형", "진취형"],
        "outlook": "브랜드·디지털 제품·콘텐츠 등 활동 분야가 넓습니다. 도구 활용과 함께 기획력·포트폴리오가 중요합니다.",
    },
    {
        "name": "건축가", "field": "과학·공학", "subfield": "건축·도시",
        "summary": "사람과 환경을 고려해 건축물과 공간을 계획하고 설계합니다.",
        "tasks": "공간 기획, 설계 도면 작성, 법규·안전 검토, 관계자 협의",
        "skills": ["공간지각", "수학", "창의력", "소통", "문제 해결"],
        "majors": ["건축학과", "건축공학과", "도시공학과"],
        "subjects": ["수학", "물리학", "미술", "지리"],
        "activities": ["학교 공간의 동선 개선안 제시하기", "친환경 건축 사례 조사하기", "축척을 활용해 모형 또는 도면 만들기"],
        "tags": ["현실형", "예술형", "탐구형"],
        "outlook": "건축 설계·시공·도시·친환경 분야 등으로 진출할 수 있습니다. 학과별 교육과 자격 경로가 다르므로 확인이 필요합니다.",
    },
    {
        "name": "환경공학자", "field": "과학·공학", "subfield": "환경·에너지",
        "summary": "물·대기·폐기물·에너지 등 환경 문제를 과학과 공학으로 해결합니다.",
        "tasks": "환경 데이터 분석, 오염 저감 기술 검토, 시설·정책 개선 연구",
        "skills": ["과학적 탐구", "수학", "데이터 분석", "문제 해결", "협업"],
        "majors": ["환경공학과", "에너지공학과", "화학공학과", "토목환경공학과"],
        "subjects": ["화학", "생명과학", "수학", "지구과학"],
        "activities": ["학교 주변 미세먼지·수질 자료 조사하기", "플라스틱 저감 아이디어 실험하기", "지역 환경 정책 비교하기"],
        "tags": ["탐구형", "현실형"],
        "outlook": "탄소중립·환경 규제·자원순환 등과 연관된 분야입니다. 세부 업무는 공공·민간·연구기관에 따라 다릅니다.",
    },
    {
        "name": "교사", "field": "교육·사회", "subfield": "교육",
        "summary": "학생의 배움과 성장을 돕고 교과 지식과 학습 경험을 설계합니다.",
        "tasks": "수업 설계와 진행, 평가, 학생 상담, 교육 활동 운영",
        "skills": ["설명력", "공감", "의사소통", "전문성", "책임감"],
        "majors": ["교육학과", "사범대학 교과교육과", "초등교육과"],
        "subjects": ["희망 교과", "국어", "사회", "윤리"],
        "activities": ["친구에게 개념 설명 자료 만들기", "수업 활동을 직접 설계해 보기", "교육 격차 사례와 해결 방안 조사하기"],
        "tags": ["사회형", "진취형"],
        "outlook": "학교급·교과·교원 자격 경로에 따라 진출 과정이 다릅니다. 교원 양성 및 임용 관련 최신 안내를 확인해야 합니다.",
    },
    {
        "name": "변호사", "field": "법률·사회", "subfield": "법·공공",
        "summary": "법률 지식을 바탕으로 의뢰인의 권리를 보호하고 법적 문제 해결을 지원합니다.",
        "tasks": "법률 검토, 상담, 서면 작성, 소송·분쟁 대응",
        "skills": ["논리적 사고", "읽기·쓰기", "논증", "윤리의식", "의사소통"],
        "majors": ["법학과", "정치외교학과", "행정학과 등 관련 전공"],
        "subjects": ["정치와 법", "사회·문화", "국어", "윤리"],
        "activities": ["사회 쟁점을 법적 관점에서 분석하기", "모의재판 활동 참여하기", "판결문 요약과 근거 비교하기"],
        "tags": ["탐구형", "진취형", "사회형"],
        "outlook": "법률·기업·공공·국제 분야 등 활동 영역이 있습니다. 국내 변호사 자격 취득 경로와 요건을 별도로 확인해야 합니다.",
    },
    {
        "name": "마케팅 기획자", "field": "경영·경제", "subfield": "경영·콘텐츠",
        "summary": "고객과 시장을 분석해 제품·서비스의 가치를 알리는 전략을 기획합니다.",
        "tasks": "시장 조사, 고객 분석, 캠페인 기획, 성과 측정",
        "skills": ["창의력", "데이터 해석", "소통", "기획력", "협업"],
        "majors": ["경영학과", "광고홍보학과", "미디어커뮤니케이션학과"],
        "subjects": ["경제", "수학", "사회·문화", "국어"],
        "activities": ["브랜드 캠페인 분석하기", "설문으로 소비자 선호 조사하기", "작은 캠페인을 기획하고 결과 측정하기"],
        "tags": ["진취형", "예술형", "사회형"],
        "outlook": "디지털 채널과 데이터 활용이 확대되고 있습니다. 업종과 조직에 따라 필요한 전문성이 다릅니다.",
    },
]

FIELDS = {
    "IT·컴퓨터": ["인공지능·데이터", "소프트웨어·앱"],
    "의료·생명": ["의료·보건", "생명과학·바이오"],
    "예술·디자인": ["시각·콘텐츠"],
    "과학·공학": ["건축·도시", "환경·에너지"],
    "교육·사회": ["교육"],
    "법률·사회": ["법·공공"],
    "경영·경제": ["경영·콘텐츠"],
}
RIASEC = {
    "현실형(R)": "도구·기계·실제적인 활동을 선호하는 경향",
    "탐구형(I)": "관찰·분석·원리 탐구를 선호하는 경향",
    "예술형(A)": "창의적 표현과 새로운 아이디어를 선호하는 경향",
    "사회형(S)": "사람을 돕고 가르치며 협력하는 활동을 선호하는 경향",
    "진취형(E)": "목표를 세우고 설득·기획·주도하는 활동을 선호하는 경향",
    "관습형(C)": "자료를 체계적으로 정리하고 정확하게 처리하는 활동을 선호하는 경향",
}
QUESTION_BANK = [
    ("새로운 앱이나 기계가 어떻게 작동하는지 직접 시험해 보는 편이다.", "현실형(R)"),
    ("복잡한 현상을 관찰하고 원인을 분석하는 것이 흥미롭다.", "탐구형(I)"),
    ("글·그림·영상 등으로 나만의 아이디어를 표현하는 것을 좋아한다.", "예술형(A)"),
    ("친구의 고민을 듣거나 다른 사람의 학습을 돕는 일이 보람 있다.", "사회형(S)"),
    ("팀 활동에서 목표를 정하고 사람들을 설득하거나 이끄는 편이다.", "진취형(E)"),
    ("자료를 분류하고 일정과 절차를 꼼꼼하게 정리하는 것을 좋아한다.", "관습형(C)"),
    ("직접 만들고 고치면서 결과를 확인하는 활동을 즐긴다.", "현실형(R)"),
    ("자료와 근거를 비교해 규칙이나 패턴을 찾는 것이 재미있다.", "탐구형(I)"),
    ("정답이 하나가 아닌 과제에서 독창적인 해결책을 생각한다.", "예술형(A)"),
    ("여러 사람의 의견을 조율하고 함께 해결하는 활동을 선호한다.", "사회형(S)"),
    ("아이디어를 실행 계획으로 만들고 성과를 내는 데 관심이 있다.", "진취형(E)"),
    ("숫자나 기록을 정확하게 확인하고 체계적으로 관리하는 편이다.", "관습형(C)"),
]

# -----------------------------
# 스타일
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family:'Noto Sans KR', sans-serif;}
.block-container {padding-top:1.2rem; padding-bottom:1.4rem; max-width:1200px;}
.hero {background:linear-gradient(115deg,#142b49 0%,#245b91 58%,#4878bd 100%);
 color:white; padding:1.35rem 1.5rem; border-radius:20px; margin-bottom:1rem;}
.hero h1 {font-size:2rem; margin:0 0 .35rem 0; font-weight:800;}
.hero p {color:#e4eefb; margin:0;}
.small-muted {color:#64748b; font-size:.88rem;}
.info-card {background:#f4f7fb; border:1px solid #e3eaf3; border-radius:15px; padding:1rem; min-height:115px;}
.step {font-size:.78rem; color:#2563a6; font-weight:700; letter-spacing:.04em;}
div.stButton > button {border-radius:12px; min-height:2.7rem; font-weight:600;}
div[data-testid="stMetric"] {background:#f4f7fb; border:1px solid #e3eaf3; padding:12px; border-radius:12px;}
@media (max-width: 700px) {
 .block-container {padding-left:.8rem; padding-right:.8rem;}
 .hero h1 {font-size:1.5rem;}
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 상태 및 데이터 함수
# -----------------------------
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "compare" not in st.session_state:
    st.session_state.compare = []
if "field_choice" not in st.session_state:
    st.session_state.field_choice = "IT·컴퓨터"
if "sub_choice" not in st.session_state:
    st.session_state.sub_choice = FIELDS["IT·컴퓨터"][0]
if "report_name" not in st.session_state:
    st.session_state.report_name = ""

def career_api_key():
    try:
        return st.secrets.get("CAREERNET_API_KEY", os.getenv("CAREERNET_API_KEY", ""))
    except Exception:
        return os.getenv("CAREERNET_API_KEY", "")

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_careernet_jobs(api_key, keyword=""):
    if not api_key:
        return []
    try:
        url = "https://www.career.go.kr/cnet/front/openapi/jobs.json"
        response = requests.get(url, params={"apiKey": api_key, "pageIndex": 1, "searchJobNm": keyword}, timeout=8)
        response.raise_for_status()
        payload = response.json()
        rows = payload.get("list", payload.get("jobs", []))
        if isinstance(rows, dict):
            rows = [rows]
        return rows if isinstance(rows, list) else []
    except Exception:
        return []

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_careernet_majors(api_key, keyword):
    if not api_key:
        return {}
    try:
        url = "https://www.career.go.kr/cnet/openapi/getOpenApi"
        params = {
            "apiKey": api_key, "svcType": "api", "svcCode": "MAJOR",
            "contentType": "json", "gubun": "대학교", "thisPage": "1",
            "perPage": "10", "searchTitle": keyword,
        }
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        return response.json()
    except Exception:
        return {}

def find_career(name):
    return next((c for c in CAREERS if c["name"] == name), None)

def toggle_favorite(name):
    if name in st.session_state.favorites:
        st.session_state.favorites.remove(name)
    else:
        st.session_state.favorites.append(name)

def career_card(career, show_actions=True, prefix=""):
    st.markdown(f"**{career['name']}**")
    st.caption(f"{career['field']}  ·  {career['subfield']}")
    st.write(career["summary"])
    c1, c2 = st.columns(2)
    c1.caption("주요 역량")
    c1.write(" · ".join(career["skills"][:3]))
    c2.caption("관련 전공")
    c2.write(" · ".join(career["majors"][:2]))
    if show_actions:
        a, b = st.columns(2)
        fav_label = "★ 저장됨" if career["name"] in st.session_state.favorites else "☆ 관심 직업 저장"
        if a.button(fav_label, key=f"{prefix}fav_{career['name']}", use_container_width=True):
            toggle_favorite(career["name"])
            st.rerun()
        if b.button("비교 목록에 추가", key=f"{prefix}cmp_{career['name']}", use_container_width=True):
            if career["name"] not in st.session_state.compare:
                if len(st.session_state.compare) >= 2:
                    st.warning("직업 비교는 한 번에 최대 2개까지 가능합니다.")
                else:
                    st.session_state.compare.append(career["name"])
                    st.success("비교 목록에 추가했습니다.")
                    st.rerun()
            else:
                st.info("이미 비교 목록에 있습니다.")

def make_report(career, student_name, motivation, question):
    lines = [
        "# 진로 탐구 보고서",
        f"- 작성자: {student_name or '미기재'}",
        f"- 작성일: {date.today().isoformat()}",
        f"- 탐구 직업: {career['name']}",
        "",
        "## 1. 직업을 선택한 이유",
        motivation or "관심 분야와 연결해 선택 이유를 작성해 보세요.",
        "",
        "## 2. 직업의 주요 업무",
        career["tasks"],
        "",
        "## 3. 필요한 역량",
        ", ".join(career["skills"]),
        "",
        "## 4. 관련 학과 및 교과목",
        "- 관련 학과: " + ", ".join(career["majors"]),
        "- 관련 교과목: " + ", ".join(career["subjects"]),
        "",
        "## 5. 나의 탐구 질문",
        question or "이 직업에서 가장 중요한 역량은 무엇이며, 어떻게 기를 수 있을까?",
        "",
        "## 6. 후속 탐구 및 실천 계획",
        "\n".join(f"- {x}" for x in career["activities"]),
        "",
        "## 7. 참고 및 유의사항",
        "본 보고서는 진로 탐색을 위한 초안입니다. 학과 개설 여부, 입시 전형, 자격 요건 및 직업 전망은 대학·공공기관의 최신 공식 자료로 추가 확인하세요.",
    ]
    return "\n".join(lines)

# -----------------------------
# 상단 헤더 및 메뉴
# -----------------------------
st.markdown("""
<div class="hero">
  <div class="step">HIGH SCHOOL CAREER EXPLORER</div>
  <h1>🧭 MY CAREER</h1>
  <p>관심사를 발견하고, 직업을 탐색하고, 나만의 진로 계획을 만들어 보세요.</p>
</div>
""", unsafe_allow_html=True)

pages = ["홈", "관심 분야 탐색", "흥미 유형 분석", "직업 상세", "직업 비교", "나의 보관함", "탐구 보고서", "QR·설정"]
page = st.radio("메뉴", pages, horizontal=True, label_visibility="collapsed")
st.divider()

# -----------------------------
# 홈
# -----------------------------
if page == "홈":
    st.subheader("나에게 맞는 진로, 작은 관심에서 시작해요.")
    st.write("관심 분야를 고르고 세부 분야를 탐색하면 관련 직업과 학과를 확인할 수 있습니다.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="info-card"><div class="step">STEP 01</div><h3>🔎 분야 발견</h3><p>관심 있는 큰 영역에서 출발해요.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="info-card"><div class="step">STEP 02</div><h3>🧩 직업 탐색</h3><p>세부 분야와 직업의 특징을 살펴봐요.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="info-card"><div class="step">STEP 03</div><h3>📝 진로 설계</h3><p>역량과 학과를 알아보고 보고서를 만들어요.</p></div>', unsafe_allow_html=True)
    st.markdown("### 빠른 시작")
    quick1, quick2 = st.columns(2)
    with quick1:
        st.info(f"⭐ 저장한 관심 직업: **{len(st.session_state.favorites)}개**")
        st.write("보관함에서 저장한 직업을 다시 확인할 수 있어요.")
    with quick2:
        st.info(f"⚖️ 비교 목록: **{len(st.session_state.compare)} / 2개**")
        st.write("관심 있는 두 직업의 업무와 역량을 비교해 보세요.")
    st.markdown("### 인기 탐색 예시")
    featured = ["AI 엔지니어", "생명과학 연구원", "시각디자이너"]
    cols = st.columns(3)
    for col, name in zip(cols, featured):
        with col:
            c = find_career(name)
            with st.container(border=True):
                st.markdown(f"**{c['name']}**")
                st.caption(c["field"])
                st.write(c["summary"])
                if st.button("직업 살펴보기", key=f"home_{name}", use_container_width=True):
                    st.session_state.selected_career = name
                    st.session_state.detail_from_home = True
                    st.rerun()
    if st.session_state.get("detail_from_home"):
        st.info("상단 메뉴에서 '직업 상세'를 선택하면 선택한 직업 정보를 볼 수 있습니다.")

# -----------------------------
# 관심 분야 탐색: 영역 -> 세부 분야 -> 직업
# -----------------------------
elif page == "관심 분야 탐색":
    st.subheader("관심 분야를 단계별로 좁혀 보세요.")
    st.markdown('<div class="step">STEP 1 · 관심 영역</div>', unsafe_allow_html=True)
    field = st.selectbox("가장 관심 있는 영역을 선택하세요.", list(FIELDS.keys()), key="field_select")
    st.session_state.field_choice = field
    st.markdown('<div class="step">STEP 2 · 세부 분야</div>', unsafe_allow_html=True)
    subfield = st.selectbox("더 알아보고 싶은 세부 분야를 선택하세요.", FIELDS[field], key="sub_select")
    st.session_state.sub_choice = subfield
    matches = [c for c in CAREERS if c["field"] == field and c["subfield"] == subfield]
    st.markdown('<div class="step">STEP 3 · 관련 직업</div>', unsafe_allow_html=True)
    if matches:
        st.caption(f"'{field} / {subfield}'에서 탐색할 수 있는 직업")
        for c in matches:
            with st.container(border=True):
                career_card(c, prefix="explore_")
    else:
        st.info("이 세부 분야의 기본 직업 데이터는 준비 중입니다. 다른 세부 분야를 선택해 보세요.")
    st.caption("※ 직업 목록은 진로 탐색용 대표 예시이며 모든 관련 직업을 포함하지 않습니다.")

# -----------------------------
# 흥미 유형 분석: 간단한 자기탐색 도구
# -----------------------------
elif page == "흥미 유형 분석":
    st.subheader("나의 흥미 유형 살펴보기")
    st.write("각 문항을 읽고 나와 가까운 정도를 선택하세요. 이 결과는 진단이나 적성 판정이 아닌 자기이해를 위한 참고 자료입니다.")
    scores = {k: 0 for k in RIASEC}
    with st.form("interest_form"):
        for i, (question, kind) in enumerate(QUESTION_BANK):
            val = st.slider(f"{i+1}. {question}", 1, 5, 3, key=f"interest_{i}", help="1 전혀 아니다 · 5 매우 그렇다")
            scores[kind] += val
        submitted = st.form_submit_button("흥미 유형 결과 보기", use_container_width=True)
    if submitted:
        st.session_state.interest_scores = scores
    if "interest_scores" in st.session_state:
        result = st.session_state.interest_scores
        ranked = sorted(result.items(), key=lambda x: x[1], reverse=True)
        st.markdown("### 나의 흥미 경향")
        topcols = st.columns(3)
        for col, (kind, score) in zip(topcols, ranked[:3]):
            col.metric(kind, f"{score}점")
        df = pd.DataFrame({"유형": list(result.keys()), "점수": list(result.values())})
        st.bar_chart(df.set_index("유형"))
        st.markdown("### 유형 설명")
        for kind, score in ranked[:3]:
            st.write(f"**{kind}** — {RIASEC[kind]}")
        st.info("점수가 높은 유형은 현재 응답에서 상대적으로 두드러진 흥미 경향입니다. 상황과 경험에 따라 달라질 수 있으며, 특정 직업에 적합하다는 판정은 아닙니다.")
        if st.button("결과 초기화"):
            del st.session_state.interest_scores
            st.rerun()

# -----------------------------
# 직업 상세
# -----------------------------
elif page == "직업 상세":
    st.subheader("직업 정보 자세히 보기")
    names = [c["name"] for c in CAREERS]
    default_name = st.session_state.get("selected_career", names[0])
    idx = names.index(default_name) if default_name in names else 0
    chosen = st.selectbox("탐색할 직업", names, index=idx)
    c = find_career(chosen)
    with st.container(border=True):
        st.markdown(f"## {c['name']}")
        st.caption(f"{c['field']}  /  {c['subfield']}")
        st.write(c["summary"])
        st.markdown("#### 주요 업무")
        st.write(c["tasks"])
        st.markdown("#### 필요한 역량")
        st.write("  ·  ".join(c["skills"]))
        st.markdown("#### 관련 학과 및 대학 탐색")
        st.write("관련 학과 예시: " + " · ".join(c["majors"]))
        st.caption("대학별 학과 명칭과 개설 여부는 달라질 수 있습니다. 아래 공식 진로 사이트에서 최신 정보를 검색하세요.")
        st.markdown("[커리어넷 학과정보 열기](https://www.career.go.kr/)  ·  [대학알리미 열기](https://www.academyinfo.go.kr/)")
        st.markdown("#### 관련 교과목")
        st.write(" · ".join(c["subjects"]))
        st.markdown("#### 고등학생 탐구·체험 아이디어")
        for activity in c["activities"]:
            st.write("• " + activity)
        st.markdown("#### 직업 전망 참고")
        st.write(c["outlook"])
        a, b = st.columns(2)
        if a.button("☆ 관심 직업 저장" if chosen not in st.session_state.favorites else "★ 저장 해제", use_container_width=True):
            toggle_favorite(chosen)
            st.rerun()
        if b.button("직업 비교에 추가", use_container_width=True):
            if chosen not in st.session_state.compare and len(st.session_state.compare) < 2:
                st.session_state.compare.append(chosen)
                st.success("비교 목록에 추가했습니다.")
                st.rerun()
            elif chosen in st.session_state.compare:
                st.info("이미 비교 목록에 있습니다.")
            else:
                st.warning("비교는 최대 2개까지 가능합니다.")
    api_key = career_api_key()
    if api_key:
        with st.expander("커리어넷 API 검색 결과(선택 기능)"):
            rows = fetch_careernet_jobs(api_key, chosen)
            if rows:
                st.write("커리어넷 API에서 받은 직업 검색 결과")
                st.json(rows[:5])
            else:
                st.caption("API 응답이 없거나 검색 결과가 없습니다. 기본 제공 정보를 계속 이용할 수 있습니다.")
    else:
        st.caption("커리어넷 API 인증키를 등록하면 직업정보 연동을 시도합니다. 인증키 없이도 기본 탐색 기능은 이용할 수 있습니다.")

# -----------------------------
# 직업 비교
# -----------------------------
elif page == "직업 비교":
    st.subheader("두 직업을 나란히 비교해 보세요.")
    st.caption("직업 비교 목록은 최대 2개입니다. 아래에서 비교할 직업을 직접 선택할 수도 있습니다.")
    all_names = [c["name"] for c in CAREERS]
    current = st.session_state.compare[:]
    left_default = current[0] if current else all_names[0]
    right_default = current[1] if len(current) > 1 else all_names[1]
    left = st.selectbox("직업 A", all_names, index=all_names.index(left_default), key="compare_a")
    right_options = [n for n in all_names if n != left]
    right = st.selectbox("직업 B", right_options, index=right_options.index(right_default) if right_default in right_options else 0, key="compare_b")
    if st.button("선택한 두 직업 비교하기", use_container_width=True):
        st.session_state.compare = [left, right]
    if len(st.session_state.compare) == 2:
        a, b = [find_career(n) for n in st.session_state.compare]
        lcol, rcol = st.columns(2)
        for col, career in [(lcol, a), (rcol, b)]:
            with col:
                with st.container(border=True):
                    st.markdown(f"### {career['name']}")
                    st.caption(career["field"] + " · " + career["subfield"])
                    st.markdown("**주요 업무**")
                    st.write(career["tasks"])
                    st.markdown("**필요 역량**")
                    st.write(" · ".join(career["skills"]))
                    st.markdown("**관련 학과**")
                    st.write(" · ".join(career["majors"]))
                    st.markdown("**관련 교과목**")
                    st.write(" · ".join(career["subjects"]))
        if st.button("비교 목록 비우기"):
            st.session_state.compare = []
            st.rerun()
    else:
        st.info("위에서 두 직업을 선택하고 비교하기를 눌러주세요.")

# -----------------------------
# 나의 보관함
# -----------------------------
elif page == "나의 보관함":
    st.subheader("내가 저장한 관심 직업")
    if not st.session_state.favorites:
        st.info("아직 저장한 직업이 없습니다. '관심 분야 탐색' 또는 '직업 상세'에서 ☆ 버튼을 눌러 저장해 보세요.")
    else:
        st.write(f"총 {len(st.session_state.favorites)}개 저장됨")
        for name in st.session_state.favorites:
            c = find_career(name)
            if c:
                with st.container(border=True):
                    st.markdown(f"**{c['name']}** · {c['field']}")
                    st.write(c["summary"])
                    x, y = st.columns(2)
                    if x.button("비교 목록에 추가", key=f"vault_cmp_{name}", use_container_width=True):
                        if name not in st.session_state.compare and len(st.session_state.compare) < 2:
                            st.session_state.compare.append(name)
                            st.rerun()
                        else:
                            st.warning("비교 목록은 최대 2개이며 중복 저장할 수 없습니다.")
                    if y.button("저장 해제", key=f"vault_del_{name}", use_container_width=True):
                        toggle_favorite(name)
                        st.rerun()

# -----------------------------
# 보고서 생성
# -----------------------------
elif page == "탐구 보고서":
    st.subheader("진로 탐구 보고서 초안 만들기")
    st.write("직업 정보를 바탕으로 보고서 초안을 생성합니다. 제출 전에는 직접 조사한 자료와 생각을 추가해 완성하세요.")
    selected = st.selectbox("탐구할 직업", [c["name"] for c in CAREERS])
    career = find_career(selected)
    student = st.text_input("작성자(선택)", placeholder="이름 또는 별칭")
    motivation = st.text_area("이 직업을 선택한 이유", placeholder="관심을 갖게 된 계기와 궁금한 점을 적어보세요.", height=95)
    question = st.text_input("나의 탐구 질문(선택)", placeholder="예: 이 직업에서 데이터 분석 역량은 어떻게 활용될까?")
    report = make_report(career, student, motivation, question)
    st.markdown("#### 보고서 미리보기")
    st.markdown(report)
    st.download_button(
        "보고서 Markdown 파일 다운로드",
        data=report.encode("utf-8"),
        file_name=f"진로탐구보고서_{selected.replace(' ', '_')}.md",
        mime="text/markdown",
        use_container_width=True,
    )

# -----------------------------
# QR / 설정 / API
# -----------------------------
elif page == "QR·설정":
    st.subheader("QR 코드 및 데이터 연결")
    st.write("앱을 GitHub에 올리고 Streamlit Community Cloud에 배포한 뒤, 배포 주소로 QR 코드를 만들 수 있습니다.")
    app_url = st.text_input("배포된 앱 주소", placeholder="https://your-app-name.streamlit.app")
    if app_url.strip().startswith(("https://", "http://")):
        qr = qrcode.QRCode(box_size=8, border=3)
        qr.add_data(app_url.strip())
        qr.make(fit=True)
        image = qr.make_image(fill_color="#142b49", back_color="white")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        st.image(buffer.getvalue(), caption="휴대전화 카메라로 스캔해 앱에 접속하세요.", width=230)
        st.download_button("QR 코드 PNG 다운로드", buffer.getvalue(), "my_career_qr.png", "image/png")
    else:
        st.info("배포 주소를 입력하면 QR 코드가 표시됩니다. 로컬 실행 주소가 아닌 공개 배포 주소를 입력하세요.")
    st.divider()
    st.markdown("#### 커리어넷 Open API 연결")
    st.write("커리어넷 Open API는 인증키 발급과 승인이 필요합니다. 발급 후 Streamlit 앱의 Secrets에 `CAREERNET_API_KEY`를 등록하세요.")
    st.code('CAREERNET_API_KEY = "발급받은_인증키"', language="toml")
    st.markdown("[커리어넷 Open API 신청 및 안내](https://www.career.go.kr/cnet/front/openapi/openApiMainCenter.do)")
    st.markdown("[커리어넷 직업백과 API 문서](https://m.career.go.kr/cnet/front/openapi/jobCenter.do)")
    st.markdown("[커리어넷 학과정보 API 문서](https://www.career.go.kr/cnet/front/openapi/openApiMajorCenter.do)")
    api_key = career_api_key()
    if api_key:
        st.success("CAREERNET_API_KEY가 설정되어 있습니다.")
        with st.expander("학과 API 연결 테스트"):
            keyword = st.text_input("학과 검색어", value="컴퓨터공학")
            if st.button("커리어넷 학과 검색"):
                data = fetch_careernet_majors(api_key, keyword)
                if data:
                    st.json(data)
                else:
                    st.warning("응답을 받지 못했습니다. 인증키, 승인 상태 및 API 요청 조건을 확인하세요.")
    else:
        st.warning("현재 API 인증키가 없습니다. 기본 내장 직업 데이터로 앱을 사용할 수 있습니다.")
    st.divider()
    st.markdown("#### 데이터 출처 및 이용 안내")
    st.markdown("""
- [커리어넷](https://www.career.go.kr/) — 직업·학과·진로 정보 및 Open API
- [고용24](https://www.work24.go.kr/) — 직업정보와 고용 관련 정보
- [대학알리미](https://www.academyinfo.go.kr/) — 대학 및 학과 관련 공시정보

직업·학과 예시는 탐색을 돕기 위한 기초 데이터입니다. 입시 전형, 학과 개설 여부, 자격 요건, 임금 및 전망은 매년 달라질 수 있으므로 반드시 해당 대학과 공공기관의 최신 공식 자료를 확인하세요.
""")

st.divider()
st.caption("MY CAREER · 고등학생 진로탐구 프로젝트 | 즐겨찾기와 흥미 결과는 현재 세션에 임시 저장됩니다.")
