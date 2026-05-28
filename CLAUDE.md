# CLAUDE.md — My Care Lab: 나만의 솔루션 만들기 (PoC B)

## 프로젝트 개요

My Care Lab의 PoC B.
사용자가 에이전트와 대화형으로 건강 솔루션(시나리오 예제: 체중감량)을 co-creation하고,
생성된 플랜 기반으로 넛징과 보상이 작동하는 루프를 시연한다.
보상은 Three.js 기반 3D 갤러리(Slow Museum / Bloom Planet / Wellness Marble)에 직접 반영된다.

깃허브: https://github.com/jaewonize/My-Care-Lab
GitHub Pages: https://jaewonize.github.io/My-Care-Lab/

---

## 기술 스택

- 단일 HTML 파일 (순수 HTML/CSS/JS) — 부모 **`app.html`** (PWA start_url; `index.html`은 랜딩/리다이렉트)
- 3개 테마는 iframe으로 임베드, 각자 Three.js 씬 (CDN r128)
- 모바일 프레임: 360px × 780px (갤럭시 S25 스타일) → 모바일 단독 실행 시 상하 크롭 후 화면 가득
- PWA: `manifest.webmanifest` (display: standalone, theme_color 동적, icon.svg)
- Canvas API: 체형 슬라이더 Warp 변형 (per-scanline)
- localStorage 키 (현재 데모는 메모리 전용, 키만 정의): `mycarelab_plan`, `mycarelab_rewards`

---

## 디렉토리 구조

```
[Demo] PoC B/
├── app.html                ← 부모 (My Care Lab, PWA start_url)
├── index.html              ← 랜딩(또는 리다이렉트)
├── manifest.webmanifest    ← PWA 매니페스트 (display:standalone)
├── icon.svg                ← 앱 아이콘 (그라데이션 sprout)
├── CLAUDE.md               ← 이 파일
├── .gitignore
├── .claude/launch.json     ← 로컬 프리뷰 (npx http-server, 포트 4173)
├── Slow Museum/            ← iframe 테마 1 — 3D 갤러리 (조각상 + 그림)
│   ├── index.html
│   └── asset/{sculpture,portrait,landscape,abstract}
├── Slow-Planet/            ← iframe 테마 2 — 3D 지구 + 동물 (Bloom Planet)
│   ├── index.html
│   └── assets/{maps,models}
└── Wellness Marble/        ← iframe 테마 3 — 아이소메트릭 보드게임판
    ├── index.html
    ├── lib/
    └── asset/{activity,restoration,appearance,mind,bike}
```

각 테마 폴더는 원래 별도 GitHub repo였지만 My-Care-Lab으로 통합 시 .git 제거됨
(원본 repo: jaewonize/Slow-Museum, jaewonize/Bloom-Planet, jaewonize/Wellness-Marble).

---

## 화면 구조 & 라우팅

화면 전환은 CSS translateX 슬라이드 애니메이션.
`.screen.active` 클래스로 제어. statusbar/tabbar는 absolute 오버레이라 전환 시 레이아웃 시프트 없음.

```
screen-dashboard  대시보드 — Slow Museum 갤러리 (iframe) + 솔루션 카드 오버레이 4개
                  → 첫 진입 시 활성 탭 (시작 화면)
screen-home       솔루션 탭 — 기존 솔루션 카드 2개 + 넛징 카드 + "나만의 솔루션 만들기"
screen-chat       에이전트 대화 — co-creation 플로우 (인트로 + 4단계)
```

**하단 탭바**: [🏛 대시보드] / [✨ 솔루션] — 대시보드 활성 시 탭바 배경 투명.
**보상 페이지(screen-reward) 제거됨**: 미션 완료 → 갤러리 직접 업데이트.

---

## Co-creation 플로우 (screen-chat)

State machine 기반 단계 (외부 루프 + 스냅샷 기반 뒤로가기 지원).

```
Stage A    인사 + 역할 소개 → 시작 방식 선택
           [추천 받고 싶어요] / [원하는 솔루션이 있어요]
              (specific 분기는 안내 후 추천 흐름으로 합류 — sleep fallback 패턴)
Stage B    발견된 신호 카드(운동복 찜 / 다이어트 캡처) → 솔루션 방향 선택
           [🏃 내 몸 가꾸기 루틴] / [🥗 건강 식단 리셋]
              (두 선택 모두 체중감량 데모로 수렴, 플랜 카드 eyebrow만 동적)
step 1    신체 데이터 + 라이프스타일 입력
          (체중/체지방률/근육량/키/나이/성별 + 평균 걸음수/수면h/수면점수/스트레스)
step 2    Canvas Warp 슬라이더 — 목표 체형 설정
step 3    타겟 날짜 선택 (메모리 이벤트: My Wedding 2026-08-15, Trip to Hawaii 2026-10-03 + 직접 입력)
step 4    플랜 견적 카드 — 개인화 역산 + 수락/강화/순화 + 이전 단계로
```

뒤로가기: 챗 헤더의 백 버튼(`#backBtn`) → `screen-home` 복귀.
각 위젯의 `[data-step-back]` 버튼 → snapshot 복원으로 이전 단계 재진입.

### 챗 로딩 애니메이션 (실시간감 — 에이전트가 일하고 있다는 무대 효과)

3개 패턴이 결합되어 데이터 발견의 호흡을 만듦:

**A. 타이핑 인디케이터** (`appendTyping` / `withTyping`)
주요 에이전트 발화 직전 0.7s 동안 ••• 펄스 표시 → 발화로 교체.
모든 큰 비트(인트로/Step 1·2·3·4 전환)에 적용.

**B. 작업 상태 라벨** (`appendStatus` / `withStatus`)
스피너 + 텍스트 1.2~1.6s 표시 → 결과 카드로 교체. 4비트에 적용:
- "일상 데이터 탐색 중…" (인트로 신호 카드 직전)
- "갤러리·웨어러블 데이터 분석 중…" (Step 1 카드 직전)
- "캘린더 메모리 조회 중…" (Step 3 카드 직전)
- "플랜 설계 중…" (Step 4 카드 직전, 1.6s)

**C. 스켈레톤 → 실데이터 채워짐** (`.is-skeleton` + `.skel-bar` + `.reveal`)
카드 외곽이 먼저 등장하고, 내부는 shimmer 바로 표시 → 0.9~1.2s 후 실데이터로 fade-in 교체.
적용: 인트로 신호 카드, Step 1 데이터 연동, Step 3 메모리 이벤트, Step 4 플랜 hero+cats.
- 공통 클래스: `.sk-ico / .sk-meta / .sk-line(.w50/.w70) / .sk-tag`
- 채워질 때 stagger 애니메이션 (rows 0.1s 간격, plan hero→cats→timeline→actions 0.1s 간격)

**동기화 룰**: 다음 발화가 스켈레톤 fill 전에 뜨면 안 됨 → 인트로 흐름은 fill 완료(0.9s) + 호흡(0.4s) 후 다음 typing.

### Step 4 — 개인화 역산 로직 (구현됨)

```
필요 총 칼로리 적자 = 목표 감량(kg) × 7700kcal
일일 적자 = 총 적자 ÷ 기간(일)

잘 태우기:
- 좌식(avgSteps<6000) → 분담률 60% / 활동적 → 40%
- daily_kcal_extra = 일일 적자 × 분담률
- step_target = max(6000, avgSteps + extra_kcal/0.04/2)
- is_bottleneck = sedentary

잘 자기:
- sleepH<6 → 시간 목표 7h (is_bottleneck=true)
- sleepH<7 → +0.5h
- sleepScore<65 → 점수 75↑ (is_bottleneck=true)

잘 빠지기:
- weekly_loss_kg = totalLoss ÷ weeks

잘 버티기:
- avgStress>70 → stress_max=60 (is_bottleneck=true)
- 65<stress<=70 → stress_max=65 (is_bottleneck=true)
- 기타 → 60
```

**안전장치**: `dailyDeficit > 1000kcal` → `plan.isUnsafe = true`
→ ⬆ 목표 올리기 비활성, .warning-strip 표시.

---

## 대시보드 화면 (screen-dashboard)

### 갤러리 — Three.js iframe

3개 테마 iframe을 미리 mount(`data-src`)하되 활성 1개만 `src` 설정 → **lazy 로드**.
테마 전환(`#theme-switch` 우상단 알약) 시 다음 iframe에 src 주입 + 로딩 스피너 표시.
첫 진입은 Slow Museum.

**Three.js RAF 일시정지**: 각 테마에 `window.__pauseRender()` / `__resumeRender()` 노출.
부모의 goScreen 오버라이드가 대시보드 떠날 때 활성 iframe 일시정지 → 솔루션 챗/Canvas Warp의
lag 해소. 복귀 시 재개.

**FRAME_INJECT_CSS**: iframe 로드 완료 시점에 부모가 CSS 주입 (이전엔 컨트롤 패널 숨김용이었으나,
3개 테마에서 슬라이더 패널은 소스 자체에서 제거됨. 현재는 background:transparent / canvas-wrap
border-radius 제거 등 최소 정리만).

### Slow Museum 초기 상태 (My Care Lab 적용)

- 전시대 PED_ASSIGN: `{ 2: 'milo', 3: 'thinker', 4: 'brancusi' }`
- 슬롯 #1·#2 빈 전시대 (h=0.3), `_loadSculptureToPed()` 함수로 런타임 추가 가능
- 그림: groom(중앙벽) 4슬롯 모두 채움, rest/manage 벽은 slot 1·3 빈 액자
- BokehPass DoF 강화 (aperture 0.004 / maxblur 0.022) — 앞줄 조각 선명, 뒤로 갈수록 아웃포커스
- **렌즈 시프트** `VIEW_SHIFT_Y = 120` — 점수카드 위 보상 공간 확보(이전 80에서 +40px 위로)
- **빈 전시대/액자 캡션 분기** (showArtLabel): name 없으면 제목 '작품 없음', 메타 '마지막 전시일 YYYY-MM-DD HH:MM' (랜덤 30일~3년 전, 그룹별 1회 캐시), 사유 없음. 채워진 작품은 기존 '획득일 + 사유' 유지.

### Bloom Planet (Slow-Planet) 카메라 구도

- 시작 줌 `CAM_Z = 11` (이전 10에서 살짝 줌아웃)
- 시작 렌즈 시프트 `INIT_VIEW_OY = 40` (40px 위로) — 점수카드 위 공간 확보
- 풀샷 렌즈 시프트 `FULL_VIEW_OY = 20` (20px 위로)
- 풀샷 카메라 `FULL_Z = 13`, `FULL_Y = -0.5`

### Wellness Marble 카메라 구도

- 시작 줌 `camera.zoom = 1.70` (이전 1.8221에서 살짝 줌아웃)
- 렌즈 시프트 `VIEW_SHIFT_X = -10` (보드 우측으로 10px), `VIEW_SHIFT_Y = 125` (위로 125px)

### window.gallery API (Slow Museum 내 노출)

부모가 미션 완료 시 호출:
- `addSculpture(slotIdx, name)` — 빈 전시대에 조각 추가
- `addPainting()` — groom 우선, 그 다음 random에서 빈 액자 채움 (해당 벽 시퀀스 중 미사용)
- `getCounts()` — `{ sculptures, paintings }`

### 솔루션 카드 오버레이 (부모가 그림)

iframe 위에 absolute 위치 (bottom 60px). 원본 Slow Museum `.card` 디자인 동일
(`#f5efe8` 배경, name 13px, score 26px).

```
┌─────────────┬─────────────┐
│ 1x1: NEW +  │ 1x2: 아침 5분 │
│  (또는 사용자│  정원 / 78  │
│  솔루션 8kg │             │
│  D-86)      │             │
├─────────────┼─────────────┤
│ 2x1: 밤 11시│ 2x2: 완료    │
│  잠들기 / 65│  14일 새벽   │
│             │  루틴 / 92  │
└─────────────┴─────────────┘
```

NEW 카드 클릭 → 챗 진입. `STATE.plan` 존재 시 1x1은 사용자 솔루션 카드로 교체.

---

## 미션 완료 → 갤러리 업데이트 (핵심 플로우)

`onNudgeDone(catIdx)` — 보상 페이지 거치지 않고 바로 갤러리 반영:

```
missionsDone += 1; N = missionsDone
bumpExecScore()                         # 수행 점수 +2

(테마가 다른 곳이면 museum으로 복귀)
showScreen('screen-dashboard')          # 먼저 대시보드 전환(갤러리 노출)
setTimeout(600ms) 후 보상 추가:          # 전환 끝난 뒤 등장 → fade-in 일관
  N=1 → gallery.addSculpture(1, 'thrower')   # 슬롯 #2 (앞줄 가운데)
  N=2 → gallery.addSculpture(0, 'nike')      # 슬롯 #1 (앞줄 왼쪽)
  N=3 → gallery.addPainting('groom')         # 전면 초상화 (왼쪽 2번째)
  N=4 → gallery.addPainting('rest')          # 왼쪽 안쪽 풍경화
  N=5 → gallery.addPainting('manage')        # 오른쪽 안쪽 추상화
  N>5 → gallery.addPainting()                # 빈 슬롯 random

nudgeIdx = (nudgeIdx + 1) % NUDGES.length    # 다음 미션으로 교체
renderNudge()
mCard.hidden = false; mSec.classList.add('open')   # 카드 펼친 채 유지
```

**미션 교체 UX**: 완료 후 다음 미션으로 바꾸되 카드를 **펼친 상태로 유지** →
대시보드에서 보상 확인 후 실험실 복귀 시 헤더 클릭 없이 새 미션이 바로 보임.

mission 1: 5번째 조각 = thrower @ 슬롯 #2 (h=0.3 매칭)
mission 2: 6번째 조각 = nike @ 슬롯 #1 (h=0.3 매칭)
mission 3·4·5: groom / rest / manage 빈 액자 지정 채움 (텍스처 프리로드 → 즉시 fade-in)

---

## 4개 카테고리

| 카테고리 | 핵심 질문 | 목표치 결정 |
|---------|---------|------------|
| 🔥 잘 태우기 (burn)       | 오늘 충분히 움직였나?   | 칼로리 적자 역산 + 현재 활동량 |
| 😴 잘 자기 (sleep)        | 회복이 됐나?            | 현재 수면 상태 진단 후 병목 차등 |
| 📉 잘 빠지기 (progress)   | 실제로 변하고 있나?     | 목표 감량 ÷ 기간 |
| 🧘 잘 버티기 (resilience) | 무너지지 않고 있나?     | 현재 스트레스/HRV 진단 후 병목 차등 |

---

## 넛징 시스템

`NUDGES` 배열에 5종. '지금 할 일'(`#missionSec`) 헤더를 누르면 카드(`#missionNudge`)가
펼쳐짐. 솔루션 생성 전엔 배지 `0`(zero, 무채색)이라 펼침 비활성, 생성 후 `1`(활성 glow)로 전환.
'했어요'(`onNudgeDone`) → 갤러리 보상 + 다음 미션 교체, '나중에'(`in-skip`) → 다음 미션으로 순환.
*(우상단 '맥락 바꾸기' 알약은 제거됨 — '나중에'로 어차피 다음 맥락/미션으로 넘어가므로.)*

### 미션 카피 (현재 5종, 직접 행동 처방형)

실시간 live 넛징 강조: 카드 테두리 glow 펄스 애니메이션, '했어요' 버튼 shimmer.

```
1. 잘 태우기 · 오후 6:40  — "버스로 퇴근 중이시네요." / 세곡사거리에 내려서 1.2km 걸어가세요
2. 잘 빠지기 · 오전 7:02  — "일어나셨네요." / 5분 안에 체중을 측정하세요
3. 잘 빠지기 · 밤 11:48   — "쿠팡이츠를 켜셨네요." / 앱을 닫고 방울토마토를 드세요
4. 잘 태우기 · 오후 9:30  — "넷플릭스 보는 중이시네요." / 잠시 멈추고 스쿼트 20개 하세요
5. 잘 태우기 · 방금       — "식사를 마치셨군요." / 바로 율동공원 둘레길 한 바퀴 걸으세요
```

### 트리거 정의 (개념)

- 잘 태우기: 3일 연속 소모 칼로리 목표 대비 70% 미달
- 잘 자기: 수면 점수/시간이 개인 목표치 이하 2일 연속
- 잘 빠지기: 주간 감량 페이스 목표의 50% 미달
- 잘 버티기: 스트레스 지수가 개인 목표 상한 초과 2일 연속

### 카드 형태

```
● {카테고리} · 위협 감지        [시간]
{lead}              ← 상황 ("버스로 퇴근 중이시네요.")
{action}            ← 행동 처방 (크게)
{reason}            ← 근거

[했어요]  [나중에]
```

---

## STATE 구조

```javascript
STATE = {
  step: 0,
  body: {
    weight, fat, muscle, height, age, gender,
    avgSteps, avgSleepH, avgSleepScore, avgStress
  },
  goal: { weight, fat, muscle, slider },
  photoSrc, targetDate, targetEvent, targetDays,
  plan: null,           // 확정된 플랜 전체
  rewards: [],          // 누적 보상 (현재 데모 메모리 전용)
  tab: 'dashboard',     // 시작 탭
  theme: 'museum',      // 현재 활성 테마
  newReward: null,      // 최근 보상 (대시보드 하이라이트용)
  missionsDone: 0,      // 갤러리 추가 시퀀스 결정
}
```

---

## 성능 최적화

1. **Lazy iframe 로딩**: 3개 테마 중 활성 1개만 `src` 설정. 다른 테마는 사용자가 전환 클릭 시 로드.
2. **RAF 일시정지**: 솔루션 탭에 있을 땐 활성 iframe의 `animate()` 함수가 `_paused` 체크로 RAF 체인 끊음 →
   GPU/CPU 점유 0. 대시보드 복귀 시 재개.
3. **슬라이더 패널 소스 삭제**: 각 테마 HTML에서 `<div id="sliders">` 블록 및 관련 JS 제거 →
   iframe 초기화 비용 감소.
4. **Cache-busting meta**: 4개 HTML 모두에 no-cache 메타 → 푸시 후 브라우저가 항상 fresh fetch.

---

## 디자인 디테일

- 폰 프레임 360×780, 다이내믹 아일랜드 노치 제거됨
- statusbar / tabbar는 항상 absolute (flex 흐름에 영향 X) → 화면 전환 시 점프 없음
- 대시보드 활성 시 statusbar opacity:0, 탭바 background:transparent
- 솔루션 카드: 원본 Slow Museum `.card` 디자인 정확히 매칭 (#f5efe8, 13px/26px/700, #666/#7d7169)
- NEW/완료는 작은 `tag-mini` (9px, rgba(125,113,105,.14))로만 구분, 카드 본체 색은 동일

### 모바일 단독 실행 — Standalone + 상하 크롭

- manifest: `display: "standalone"`, `display_override: ["standalone", "minimal-ui"]`
- iOS/Android의 OS 상태바·내비바를 **항상 표시** (몰입모드 X, 회의 결정)
- 360×780 디자인 중 **상단 36px(상태바 영역) + 하단 43px(내비바 영역)** 크롭 후 남는 영역(704px)을 OS가 제공하는 안전 영역에 꽉 채움
- 스케일 = `maxH / (780 - CROP_TOP - CROP_BOTTOM)`. `maxH`는 `window.innerHeight`의 최대값을 기억(시스템바 토글에도 안정)
- transform: `translate(tx, -CROP_TOP*s) scale(s)` + `position:fixed; overflow:hidden`으로 하단 잘림 처리
- 하단 UI(`.tabbar / .composer / .gallery-reset / .score-cards / .chat`)는 모두 `--nav-bar-h: 40px`만큼 위로 평행이동 → 내비바에 안 가림
- 화면별 statusbar/내비바 배경 색을 동적 매칭(`setBarColor` + 메타 theme-color): museum #c6c0b3 / planet #d9e9e6 / marble #fffbf7 / 일반 #eef5f1
- 더블탭 새로고침 히트존 — 상단 좌(64px) / 우(110px) 비워 backBtn·테마 도트 클릭 방해 안 함

### 챗 UI 추가 스타일

- `.msg.agent.typing` + `.typing-dots` — 3-dot 펄스(`@keyframes tdot`)
- `.agent-status` + `.spinner` — 스피너(`@keyframes spin`) + fade-in
- `.skel-bar` — shimmer(`@keyframes shimmer`)
- `.reveal` — 페이드인 + translateY(`@keyframes rowFadeIn`)

---

## 구현 우선순위 / 작업 이력

### 완료
- [x] 모바일 Shell + 기존 솔루션 카드 더미
- [x] "나만의 솔루션 만들기" 진입 카드
- [x] 에이전트 대화 UI + state machine 기반 4단계 플로우
- [x] 사진 업로드 + Canvas Warp 슬라이더 (per-scanline)
- [x] 타겟 날짜 선택 UI (메모리 이벤트 + 프리셋)
- [x] 플랜 견적 카드 + 개인화 역산 + 안전장치
- [x] 넛징 카드 (5종 직접 행동 처방) + glow 펄스 / 했어요 shimmer / 카드 펼침·접기 토글
- [x] 에이전트 능동형 챗 간소화 (데이터·사진 자동 발견 → 연동 승인 버튼)
- [x] 보상 등장 타이밍 일관화 (대시보드 도착 600ms 후 추가 + 텍스처/조각 프리로드)
- [x] 보상 fade-in (조각 1.2s / 그림 1.2s, 0.5s 지연)
- [x] 빈 슬롯 3종 지정 (groom slot1 / rest slot3 / manage slot3) → mission 3·4·5 채움
- [x] 갤러리 리셋 버튼 (↺, Slow Museum 전용 · 화면 내 점수 카드 위 우측)
- [x] 목표 체형 슬라이더 모델 (체중 65→48 / 체지방 32→12 / 근손실 구간 <50kg 경고)
- [x] Warp 여백 인접색(edge-extend) 채움
- [x] 미션 완료 후 다음 미션 펼친 채 유지 (실험실 복귀 시 즉시 노출)
- [x] 대시보드 탭: Slow Museum iframe 통합
- [x] Bloom Planet / Wellness Marble iframe 추가 + 테마 전환 알약
- [x] Slow Museum 초기 상태 조정 (#1·#2 빈, #3 milo, #4 thinker, #5 brancusi,
      groom 4필름 / rest·manage 2빈)
- [x] window.gallery API: addSculpture / addPainting
- [x] 미션 완료 → 보상 페이지 스킵 → 갤러리 직접 업데이트 + 대시보드 자동 전환
- [x] DoF 강화 (앞줄 조각 초점, 뒤로 점진적 블러)
- [x] 시작 화면 = 대시보드 탭
- [x] 노치 제거
- [x] Cache-busting meta
- [x] Lazy iframe 로딩
- [x] 비활성 iframe RAF 일시정지로 챗 lag 해소
- [x] 3개 테마 슬라이더 패널 소스 삭제
- [x] PWA 등록 (manifest.webmanifest, icon.svg) — 홈 화면 추가 시 standalone
- [x] 모바일 단독 실행 — display:standalone + 상하 크롭(36/43px) + maxH 기반 안정 스케일
- [x] 화면별 statusbar/내비바 색 동적 매칭 (setBarColor)
- [x] 하단 UI 일괄 리프트 (--nav-bar-h: 40px) — tabbar / composer / score-cards / chat
- [x] 더블탭 새로고침 히트존 (좌 64px·우 110px 제외 — backBtn·테마 도트 살림)
- [x] 챗 인트로 2단계화 — 인사 + [추천 받고 싶어요 / 원하는 솔루션이 있어요]
- [x] 발견된 신호 카드 (운동복 찜 + 다이어트 캡처) → 솔루션 2갈래 [내 몸 가꾸기 / 건강 식단 리셋]
- [x] 챗 로딩 애니메이션 — 타이핑(•••) + 작업 상태 라벨 + 스켈레톤→실데이터 fill
- [x] 시퀀스 동기화 — 스켈레톤 fill 전에 다음 발화 안 뜨게 타이밍 정렬
- [x] 갤러리 렌즈 시프트 80→120 (점수카드 위 공간)
- [x] Bloom Planet 시작 줌아웃 + 40px 위로, 풀샷 20px 위로
- [x] Wellness Marble 줌 1.8221→1.70, 좌우/상하 시프트
- [x] 빈 전시대/액자 캡션 분기 — '작품 없음' + 마지막 전시일(랜덤 과거)
- [x] 챗 백버튼 정상 작동 — 히트존 좌측 64px 제외

### 미구현 / 다음
- [ ] localStorage 영속화 활성화 (현재 데모는 새로고침마다 초기화)
- [ ] 실제 Claude API 연동 (현재 더미 플랜 폴백)
- [ ] 체중계 연동 유도 UI
- [ ] 중간점검 사진 업로드 (수치/시각 트랙 불일치 감지)
- [ ] meshopt 워커 빌드로 GLB 디코딩 비동기화

---

## 주의사항

- file:// 환경에서는 iframe 상대경로가 동작하나 일부 브라우저에서 보안 제약 가능 →
  로컬 서버 권장 (`.claude/launch.json`의 'static', 포트 4173).
- iframe 통신은 같은 origin이라 `contentWindow.gallery.addSculpture(...)` 직접 호출 가능.
- 캐시 이슈로 변경이 안 보일 때: URL에 `?v=N` 쿼리 추가하거나 시크릿 창 사용.
- 테마 폴더의 GLB 에셋은 원본 repo에서 최적화된 상태로 가져와 통합됨. 추가 작업 필요 시 원본 repo 참조.

---

## 파일 목록

| 파일 | 내용 |
|------|------|
| `app.html` | My Care Lab 부모 (대시보드 + 솔루션 + 챗) — **PWA start_url** |
| `index.html` | 랜딩(또는 app.html 리다이렉트) |
| `manifest.webmanifest` | PWA 매니페스트 (display:standalone, theme_color) |
| `icon.svg` | 앱 아이콘 (그라데이션 sprout) |
| `Slow Museum/index.html` | 3D 갤러리 iframe + window.gallery API |
| `Slow-Planet/index.html` | 3D 지구 iframe (Bloom Planet 테마) |
| `Wellness Marble/index.html` | 3D 보드게임판 iframe |
| `CLAUDE.md` | 이 파일 |
| `.claude/launch.json` | 로컬 프리뷰 서버 설정 |
