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

- 단일 HTML 파일 (순수 HTML/CSS/JS) — 부모 `index.html`
- 3개 테마는 iframe으로 임베드, 각자 Three.js 씬 (CDN r128)
- 모바일 프레임: 360px × 780px (갤럭시 S25 스타일)
- Canvas API: 체형 슬라이더 Warp 변형 (per-scanline)
- localStorage 키 (현재 데모는 메모리 전용, 키만 정의): `mycarelab_plan`, `mycarelab_rewards`

---

## 디렉토리 구조

```
[Demo] PoC B/
├── index.html              ← 부모 (My Care Lab)
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
인트로     에이전트 환영 메시지 + 의도 빠른 응답
step 1    신체 데이터 + 라이프스타일 입력
          (체중/체지방률/근육량/키/나이/성별 + 평균 걸음수/수면h/수면점수/스트레스)
step 2    Canvas Warp 슬라이더 — 목표 체형 설정
step 3    타겟 날짜 선택 (메모리 이벤트 + 프리셋)
step 4    플랜 견적 카드 — 개인화 역산 + 수락/강화/순화 + 이전 단계로
```

뒤로가기: 각 위젯의 `[data-step-back]` 버튼 → snapshot 복원으로 이전 단계 재진입.

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

`onNudgeDone(cat)` — 보상 페이지 거치지 않고 바로 갤러리 반영:

```
STATE.missionsDone += 1
N = STATE.missionsDone

N=1 → window.gallery.addSculpture(1, 'thrower')   # 슬롯 #2 (앞줄 가운데)
N=2 → window.gallery.addSculpture(0, 'nike')      # 슬롯 #1 (앞줄 왼쪽)
N≥3 → window.gallery.addPainting()                # groom 우선, 그 다음 random

→ 대시보드 탭으로 자동 전환 (테마가 다른 곳이었으면 Slow Museum으로 복귀)
```

mission 1: 5번째 조각 = thrower @ 슬롯 #2 (h=0.3 매칭)
mission 2: 6번째 조각 = nike @ 슬롯 #1 (h=0.3 매칭)
mission 3+: 그림 슬롯 채움. 각 벽의 EXHIBIT 시퀀스(턴 5 기준)에서 미사용 항목 무작위.

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

`NUDGE_SCENARIOS` 배열에 4종 (카테고리별 1개). 홈 화면 넛징 헤더에 `맥락 바꾸기 ↻` 알약 →
시연 시 시나리오 순환 (시각화용, 실제 데이터 트리거 아님).

### 트리거 정의 (개념)

- 잘 태우기: 3일 연속 소모 칼로리 목표 대비 70% 미달
- 잘 자기: 수면 점수/시간이 개인 목표치 이하 2일 연속
- 잘 빠지기: 주간 감량 페이스 목표의 50% 미달
- 잘 버티기: 스트레스 지수가 개인 목표 상한 초과 2일 연속

### 카드 형태

```
⚠ {카테고리} 위협 감지         [시간]
{title}
{body}

[✅ 했어요]  [나중에]
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

---

## 구현 우선순위 / 작업 이력

### 완료
- [x] 모바일 Shell + 기존 솔루션 카드 더미
- [x] "나만의 솔루션 만들기" 진입 카드
- [x] 에이전트 대화 UI + state machine 기반 4단계 플로우
- [x] 사진 업로드 + Canvas Warp 슬라이더 (per-scanline)
- [x] 타겟 날짜 선택 UI (메모리 이벤트 + 프리셋)
- [x] 플랜 견적 카드 + 개인화 역산 + 안전장치
- [x] 넛징 카드 + 맥락 바꾸기 (4 시나리오 순환)
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
| `index.html` | My Care Lab 부모 (대시보드 + 솔루션 + 챗) |
| `Slow Museum/index.html` | 3D 갤러리 iframe + window.gallery API |
| `Slow-Planet/index.html` | 3D 지구 iframe (Bloom Planet 테마) |
| `Wellness Marble/index.html` | 3D 보드게임판 iframe |
| `CLAUDE.md` | 이 파일 |
| `.claude/launch.json` | 로컬 프리뷰 서버 설정 |
