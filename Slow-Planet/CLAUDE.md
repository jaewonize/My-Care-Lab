# CLAUDE.md — Bloom Planet

## 상위 컨텍스트

### 서비스 개요
저속노화(Slow Aging) 지표를 관리하는 헬스케어 앱.
4개 카테고리(잘 움직이기/잘 쉬기/잘 가꾸기/잘 다스리기) 점수를
시각적으로 보여주는 그래픽 대시보드.

### 데이터 수집 방식
- 엔드 프로덕트: 시스템이 자동 수집/분석 (웨어러블, 셀피 분석)
- 유저가 직접 입력하지 않음
- PoC: 수동 입력으로 점수 변화에 따른 그래픽 반응을 시연

### PoC A 목적
점수 변화에 따라 그래픽이 반응하는 걸 보여주기 위한 시뮬레이터.
엔드유저용 앱 화면이 아닌, 디자이너/기획자가 실시간으로 화면 느낌을 확인하는 용도.

### PoC A 레이아웃 원칙
- **좌측 (모바일 화면)**: 엔드유저가 실제로 보게 될 화면. 컨트롤 UI 없음.
- **우측 여백 (컨트롤 패널)**: 시연자/디자이너용. 모바일 화면 밖 브라우저 여백에 배치.
  - 4개 카테고리 슬라이더
  - 트리거 버튼들 (점수 급락, 이벤트, 100회 방문 달성 등)
- 슬라이더/버튼 조작 → 좌측 모바일 화면 그래픽이 동적으로 반응

```
[브라우저 창]
┌─────────────────┬──────────────────┐
│                 │  🎛 Control Panel │
│  📱 모바일 화면  │  ── 잘 움직이기  │
│  (유저가 보는   │  ── 잘 쉬기      │
│   실제 화면)    │  ── 잘 가꾸기    │
│                 │  ── 잘 다스리기  │
│                 │                  │
│                 │  [트리거 버튼들]  │
└─────────────────┴──────────────────┘
```

### 전체 테마 목록 (PoC A)
- **Bloom Planet** (지구 꾸미기) ← 이 폴더
- **Slow Museum** (갤러리)
- **Wellness Marble** (보드게임판)

---

## 프로젝트 개요
저속노화 지표 4개 카테고리 점수를 3D 지구 꾸미기로 시각화하는 PoC A.
점수가 오를수록 지구 위에 보상 아이템(동식물/사물)이 배치되고, 합산 점수가 지구 자전 속도에 반영됨.

## 기술 스택
- Three.js r128 (CDN) + meshopt_decoder (CDN, EXT_meshopt_compression 디코딩)
- 순수 HTML/CSS/JS (프레임워크 없음)
- 단일 HTML 파일

## 개발 환경 (이 맥 PC에 설치됨)
- `gltf-transform` CLI v4.3.0 — `npm install -g @gltf-transform/cli` (에셋 최적화용)
- `gh` CLI — GitHub 인증 완료 (jaewonize 계정, HTTPS 토큰)
- Node v26, python3 (`python` 아님 — launch.json은 python3 사용)
- git remote는 새 이름으로 설정됨: `https://github.com/jaewonize/Bloom-Planet.git`

## 파일 구조
```
Slow-Planet/                    # 로컬 폴더명 (~/Desktop/Slow-Planet, GitHub repo = Bloom-Planet)
├── CLAUDE.md
├── index.html                  # 메인 파일 (단일 HTML; 지구 텍스처는 인라인 base64)
├── .claude/launch.json         # 로컬 프리뷰 서버 (python http.server 8765)
└── assets/
    ├── maps/                   # earth_color_map.png (바다 단일색본) 등
    └── models/
        ├── glb_activity/       # 동물 (lion·turtle·panda …)
        ├── glb_restoration/    # 식물·휴식처 (rainbow·banana·bald_cypress …)
        ├── glb_appearance/     # 바다 (manta·diver·shipwreck …)
        └── glb_mind/           # 건축물 (stonhenge·pisa …)
```
> 로컬 전용(커밋 안 됨, 다른 PC엔 안 옴 — 무시 가능): `_mapfix.py`, `assets/maps/*.bak`, `assets/maps/*.src`

## 점수 체계

### 4개 카테고리
| 카테고리 | 데이터 소스 |
|---------|-----------|
| 잘 움직이기 (move) | 웨어러블 (걸음수, 운동량) |
| 잘 쉬기 (rest) | 웨어러블 (수면 데이터) |
| 잘 가꾸기 (groom) | 셀피 분석 |
| 잘 다스리기 (manage) | 웨어러블 (HRV, 스트레스) |

### LED 상태
- delta ≥ +2 → green (상승)
- delta ≤ -2 → red (하락)
- 그 외 → off

### 보상 지급 로직
- 누적 상승폭 기준
- 하락해도 누적 유지, 소급 없음
- 2점 간격으로 보상 지급

### 저속노화 속도 (자전 속도 7단계)
- 합산 점수 기준
- 점수 높을수록 → 느린 자전 (저속노화)
- 점수 낮을수록 → 빠른 자전

## 그래픽 스펙 (현재 구현)
- 캔버스(폰 화면) 크기 **360×780**. CSS `#canvas-wrap`/`#sliders`, `<canvas id="globe">` 속성, JS `const W,H` 네 곳이 함께 움직여야 함.
- Three.js 3D 지구 구체 + 인라인 base64 색맵(`colorData`)/displacement.
- 지구맵: 원본 2912×1440을 바다 단일색 `(150,208,230)`으로 통일. 육지 판정 `isLandUV`: `g > b + 15`(초록 우세=육지). `index.html` 인라인 `colorData`와 `assets/maps/earth_color_map.png`가 동일본.
- 보상 = GLB 모델을 지구 표면에 법선 방향으로 세워 배치 (구버전 "오렌지 디스크/20슬롯"은 폐기). 발이 표면에 닿게 `PLACEMENT_R=1.005`.
- 분포 `pickSpacedDir`: Mitchell best-candidate(후보 16개 중 기존 배치와 최근접거리 최대인 것 선택) → 안 몰림. 리셋 시 `_placedDirs`를 사자만 남기고 비움(반복해도 골고루). **이 골고루 분포는 추후 실제 보상테이블 연동 시에도 유지할 것.**
- 모델별 법선축 기준 랜덤 yaw (사자 제외 — 사자는 아프리카 고정 LAT 28 / LON 1, facing 180° 회전).
- 카메라: 망원 셋업 `FOV 25`, `CAM_Z 12`, `CAM_Y -0.72` (외곽 perspective 왜곡 최소화). 줌 `Z_MIN 3 ~ Z_MAX 10`.
- 자전: `_earthQ.multiply(_spinQ)` — **local Y(지구 남북축) 기준** (premultiply 아님; 기울여도 자전축 안 흔들림). 잡고 있는 동안만 정지, 놓으면 즉시 재개.
- 스와이프 관성: 드래그 속도 EMA 추적 → 놓으면 `FRICTION 0.94`로 감속, `VEL_STOP 0.001` 이하 정지. 자전과 합산됨.
- 초기 회전 `_earthQInitial`: 사자(아프리카)가 화면 좌측 가장자리, 정면엔 아시아·호주. 빈 공간 탭 → 이 회전으로 리셋 + 자전 재개. (드래그 후 놓기는 리셋 아님 — 현재 위치 유지)
- 조명: 지구는 layer 0 (ambient 0.55 / hemi 0.7 / sun 0.25 + VSM 소프트섀도우). 보상 모델은 `o.layers.enable(1)`로 layer 0+1 **둘 다** 받음 → modelSun/modelAmbient가 지구 조명에 **중첩**되니 과노출 주의. 현재 `modelSun 0.4 / modelAmbient 0`로 낮춰둠 (지구 ambient가 이미 fill 역할). 더 분리하려면 layer 격리 필요(섀도우 영향 검토).

## 보상 테이블

### 잘 움직이기 (20종)
| 순서 | 아이템 | GLB 파일명 | 이미지 파일명 |
|------|--------|-----------|-------------|
| 1 | 사슴 | deer_pbr.glb | assets/move/deer.png |
| 2 | 닭 | chicken_pbr.glb | assets/move/chicken.png |
| 3 | 양 | sheep_pbr.glb | assets/move/sheep.png |
| 4 | 앵무새 | parrot_pbr.glb | assets/move/parrot.png |
| 5 | 거북이 | turtle_pbr.glb | assets/move/turtle.png |
| 6 | 홍학 | flamingo_pbr.glb | assets/move/flamingo.png |
| 7 | 기린 | giraffe_pbr.glb | assets/move/giraffe.png |
| 8 | 공작 | peacock_pbr.glb | assets/move/peacock.png |
| 9 | 얼룩말 | zebra_pbr.glb | assets/move/zebra.png |
| 10 | 캥거루 | kangaroo_pbr.glb | assets/move/kangaroo.png |
| 11 | 곰 | bear_pbr.glb | assets/move/bear.png |
| 12 | 황소 | bull_pbr.glb | assets/move/bull.png |
| 13 | 산양 | ram_pbr.glb | assets/move/ram.png |
| 14 | 코끼리 | elephant_pbr.glb | assets/move/elephant.png |
| 15 | 치타 | cheetah_pbr.glb | assets/move/cheetah.png |
| 16 | 레드판다 | red_panda_pbr.glb | assets/move/red_panda.png |
| 17 | 흰여우 | arctic_fox_pbr.glb | assets/move/arctic_fox.png |
| 18 | 사자 | lion_pbr.glb | assets/move/lion.png |
| 19 | 팬더 | panda_pbr.glb | assets/move/panda.png |
| 20 | 블랙팬서 | panther_pbr.glb | assets/move/panther.png |

### 잘 쉬기 — 나무 (10종)
| 순서 | 아이템 | GLB 파일명 | 이미지 파일명 |
|------|--------|-----------|-------------|
| 1 | 갈대 | cattail_pbr.glb | assets/rest_tree/cattail.png |
| 2 | 대나무 | bamboo_pbr.glb | assets/rest_tree/bamboo.png |
| 3 | 바나나 나무 | banana_pbr.glb | assets/rest_tree/banana_tree.png |
| 4 | 파파야 나무 | papaya_pbr.glb | assets/rest_tree/papaya_tree.png |
| 5 | 야자수 | palm_pbr.glb | assets/rest_tree/palm_tree.png |
| 6 | 버드나무 | willow_pbr.glb | assets/rest_tree/willow.png |
| 7 | 낙우송 | bald_cypress_pbr.glb | assets/rest_tree/bald_cypress.png |
| 8 | 전나무 | tanenbaum_pbr.glb | assets/rest_tree/fir.png |
| 9 | 도토리 나무 | acorn_pbr.glb | assets/rest_tree/oak.png |
| 10 | 아카시아 | acacia_pbr.glb | assets/rest_tree/acacia.png |

### 잘 쉬기 — 휴식처 (10종)
| 순서 | 아이템 | GLB 파일명 | 이미지 파일명 |
|------|--------|-----------|-------------|
| 1 | 열기구 | balloon_pbr.glb | assets/rest_shelter/balloon.png |
| 2 | 파라솔 | parasol_pbr.glb | assets/rest_shelter/parasol.png |
| 3 | 캠프파이어 | campfire_pbr.glb | assets/rest_shelter/campfire.png |
| 4 | 무지개 | rainbow_pbr.glb | assets/rest_shelter/rainbow.png |
| 5 | 티피텐트 | teepee_pbr.glb | assets/rest_shelter/teepee.png |
| 6 | 오아시스 | oasis_pbr.glb | assets/rest_shelter/oasis.png |
| 7 | 온천 | spring_pbr.glb | assets/rest_shelter/hot_spring.png |
| 8 | 오두막 | cabin_pbr.glb | assets/rest_shelter/cabin.png |
| 9 | 폭포 | waterfall_pbr.glb | assets/rest_shelter/waterfall.png |
| 10 | 게르 | hut_pbr.glb | assets/rest_shelter/ger.png |

### 잘 가꾸기 (미정)
### 잘 다스리기 (미정)

## 현재 데모 동작 (index.html — '입력' 버튼 시연)
실제 보상테이블/슬라이더 연동 전, "이렇게 작동할 것"을 보여주는 **시연용**.
- 페이지 로드: **사자만** (아프리카 고정).
- '입력'(`#submit-btn`) 누를 때마다 단계 진행:
  1. 거북이·무지개·만타레이·스톤헨지 (4)
  2. 팬더·바나나나무·다이버 (3)
  3. 낙우송·난파선·피사의 사탑 (3) → 사자+10
  4. 한 번 더 → 리셋(사자만) → 1번부터 반복(루프)
- 보상 시 지구 중앙 안내 팝업: "○○가/이 지구에 도착했어요" (받침 따라 이/가 자동, 우상단 X 닫기).
- idle 모션: 만타·다이버 = 법선축 ±10° sin 왕복 + 위아래 hop(raised-cosine ease, 진폭 0.03). 무지개 = 법선축(Y) 연속 360° 회전 + 같은 hop.
- idle 속도 상수(공용, sway 전체 적용): `IDLE_ROT_SPEED 1.0`(좌우), `IDLE_HOP_SPEED 2.5`(위아래), `IDLE_SPIN_SPEED 0.45`(무지개 회전).
- floatR(표면에서 띄움): 무지개 `0.03`, 만타레이 `0.02`, 다이버 `0.01`. 나머지는 0(표면 부착).
- 배치 데이터 = `REWARD_BATCHES`. 옵션: `ocean`·`scaleMul`·`tiltX`·`floatR`·`idle`('sway'|'spin').

## 에셋 최적화 워크플로우 (확립됨 — 재사용)
원본 GLB는 개당 25~50MB(텍스처 2K PBR + 고폴리). GitHub/런타임용으로 공격적 압축.

```bash
gltf-transform optimize <in.glb> <out.glb> \
  --texture-compress webp --texture-size 512 \
  --simplify-ratio 0.05 --simplify-error 0.01
```

- 결과: 평균 ~750KB (40~50배 감소). 보상 80개 총 2.4GB → 59MB. 단일 파일 2MB 미만 → LFS 불필요.
- 코드 측: `gltfLoader.setMeshoptDecoder(MeshoptDecoder)` + meshopt CDN 스크립트 필수 (EXT_meshopt_compression).
- 시각: 화면에서 작게 보이는 보상엔 이 정도면 충분(사자·venus 검증 완료). 갤러리처럼 크게 볼 거면 `--simplify-ratio 0.1 --texture-size 1024`로 완화.
- 배치 처리: 카테고리 폴더 순회 루프(이전 세션에서 80개 일괄 처리함). 원본은 `~/Desktop/WA Reward/...`, repo엔 최적화본만 커밋.
- Slow Museum 조각 19개도 동일 옵션으로 처리해둠(운반용, `~/Desktop/WA Reward/Slow Museum/sculpture_glb_small/`).

## 멀티 테마 통합 (다음 단계 — 별도 세션 권장)
3개 테마를 공용 컨트롤 패널 하나로 묶은 통합 HTML.
- 테마 / 로컬폴더 / GitHub repo / Pages (3개 다 Pages 200 OK):
  - Bloom Planet — `~/Desktop/Slow_Planet` — jaewonize/Bloom-Planet — jaewonize.github.io/Bloom-Planet/
  - Slow Museum — `~/Desktop/Slow_Museum` — jaewonize/Slow-Museum — jaewonize.github.io/Slow-Museum/
  - Wellness Marble — `~/Desktop/Wellness_Marble` — jaewonize/Wellness-Marble — jaewonize.github.io/Wellness-Marble/
- 방식: 새 repo("통합 껍데기")에 공용 패널 + iframe 3개(각 테마 Pages 주소) → 어느 테마 push해도 통합 화면 자동 반영. 직접 합치면 ID/스크립트 충돌 → iframe 격리 필수.
- 각 테마에 "끼워진 모드" 추가: iframe 안에서 열리면 자기 패널 숨기고 부모(공용 패널) postMessage 값으로 반응.
- 3개 테마 트리거 버튼은 이미 동일 동기화됨("이벤트", "동일연령…낮음/높음" 한 줄).

## 주의사항
- **file:// 더블클릭 불가**: GLB를 별도 파일로 로드 → 더블클릭하면 모델·사자 안 뜸(브라우저 보안). 반드시 로컬 서버(`.claude/launch.json`) 또는 GitHub Pages로 열 것.
- 지구맵 변경은 손으로 다시 그린 PNG를 그대로 임베드(`colorData` 교체)만. **픽셀 dilation/외곽선 오프셋 금지(폐기됨).**
- **저장소 이름 변경됨**: `Slow-Planet` → `Bloom-Planet`. 새 PC에서 clone/pull 시 remote가 옛 이름이면 `git remote set-url origin https://github.com/jaewonize/Bloom-Planet.git`. (이 맥 PC·집 PC 둘 다 처리 완료)
- **로컬 프리뷰 서버**: preview_start MCP는 CWD(`/Users/ttt`) 기준이라 프로젝트 launch.json 못 찾음 → `cd ~/Desktop/Slow-Planet && python3 -m http.server 8765` 백그라운드로 직접 띄우는 게 확실. http://localhost:8765/
- **코드 수정 후 안 보이면 캐시**: 강제 새로고침(⌘+Shift+R) 또는 개발자도구 Network 탭 "Disable cache" 켜고 작업.
- **긴 세션은 새 세션으로**: 이 문서가 최신 상태를 담으므로, 세션이 길어져 느려지면 새 세션에서 이 CLAUDE.md 읽고 이어갈 것.

## 작업 이력
- [x] 3D 지구 + 인라인 텍스처, 바다 단일색본 적용
- [x] 테마명 Bloom Planet 통일 (제목·문서·GitHub repo Bloom-Planet)
- [x] GLB 모델 표면 배치 + 법선 정렬 + 랜덤 yaw (사자 제외)
- [x] 골고루 분포(best-candidate) + 리셋 시 분포메모리 정리
- [x] '입력' 단계별 보상 데모(4→3→3→리셋 루프) + 안내 팝업(이/가 자동)
- [x] idle 모션: 만타·다이버 sway / 무지개 spin + hop(ease)
- [x] 컨트롤 패널 트리거 버튼 정리(이벤트/높음) — 3개 테마 동기화
- [x] 보상 80개 GLB 최적화·커밋 (gltf-transform, 2.4GB→59MB)
- [x] 망원 카메라(FOV25) + 스와이프 관성 + local축 자전
- [x] 모델 조명 과노출 완화 (modelSun 0.4 / modelAmbient 0)
- [x] 무지개·만타 floatR·idle 속도 튜닝
- [x] GitHub repo Slow-Planet→Bloom-Planet, remote URL 갱신
- [x] WA_integration용 embed 모드 (`?embed=1` 시 자체 패널 숨김 + `#canvas-wrap` 라운딩/배경/그림자 제거 + 1.012 overscan으로 부모 `.phone` 마스크 hairline 제거. 부모는 postMessage `{source:'wa-integration', type:'slider'|'submit'|'trigger', …}`로 슬라이더/입력/트리거 주입)
- [ ] 실제 보상테이블·슬라이더 점수 연동 (현재는 시연 단계 진행만)
- [ ] 모바일 반응형 (PC 완성 후 — 단일 파일 미디어쿼리 + 패널 토글, CSS 미디어쿼리·캔버스 동적크기)
- [ ] LED 상태 / 자전 속도 7단계 점수 연동
- [ ] 잘 가꾸기·잘 다스리기 보상 테이블 확정
- [ ] 멀티 테마 통합 HTML (위 계획)
