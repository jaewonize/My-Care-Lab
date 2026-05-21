# CLAUDE.md — Slow Museum

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
  - 트리거 버튼들 (점수 급락, 할로윈 특별 보상, 100회 방문 달성 등)
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
- **Slow Terrarium** (지구 꾸미기)
- **Slow Museum** (갤러리) ← 이 폴더
- **Wellness Marble** (보드게임판)

---

## 프로젝트 개요
슬로우 테라리움의 베리에이션. 한 층 갤러리 공간에 4개 카테고리를 4개 전시 존으로 매핑.
점수가 오를수록 해당 존에 명화/조각 보상이 추가되고, 점수에 따라 조명이 변화함.

## 기술 스택
- Three.js 기반 3D 그래픽 (갤러리 공간 + 내부 오브젝트 모두 3D로 구성)
- 순수 HTML/CSS/JS
- 단일 HTML 파일

## 파일 구조
```
slow-museum/
├── CLAUDE.md
├── index.html             # 메인 파일 (단일 HTML). slow_planet.html은 삭제됨
├── .claude/launch.json    # dev 서버 (python3 + .claude/serve.py, 포트 8766)
├── .claude/serve.py       # 멀티스레드 정적 서버 (preview_start가 Desktop TCC로 막힘)
└── asset/
    ├── lion.glb           # 최적화 기준 참고 모델 (미사용, 향후 사용 예정 → 보존)
    ├── sculpture/*.glb    # 조각 다수 (gltf-transform 최적화 완료, 원본 삭제됨).
    │                      #   현재 5종만 PED_LAYOUT 사용, 나머지는 향후 사용 → 보존
    ├── portrait/          # 초상화: 사용 4종 = <이름>.jpg(최적화). 그 외 신규 원본 .jpg 보존
    ├── abstract/          # 추상화: HK1.jpg · HK2.jpg (최적화, 원본명)
    └── landscape/         # 풍경화: <이름>.jpg (cypresses·water_lilies·inwang, 최적화)
```
- **에셋 명명 원칙**: 최적화 끝난 파일은 **원본 파일명으로 치환**해 폴더 용량 절감
  (`.crop`·`.matted` 등 부수 구분자 미사용). 아직 최적화 안 한 소스 파일은 **삭제 금지**.
- 깃 원격: `https://github.com/jaewonize/Slow-Museum` (origin/main). asset 포함 커밋됨.
- 프리뷰: `preview_start`는 macOS Desktop TCC로 차단됨 → Bash 백그라운드로
  `python3 .claude/serve.py` 실행 → `http://localhost:8766/index.html`.
  `serve.py`가 **no-store 헤더** 전송 → 턴마다 **일반 새로고침(Cmd+R)** 만으로 최신 씬.
  서버 죽었으면 재기동: `lsof -ti tcp:8766|xargs kill -9; nohup python3
  .claude/serve.py >.claude/serve.log 2>&1 &`
- 검증 팁: 프리뷰 스크린샷 툴이 간헐 불안정 → 단일 `preview_eval`로 씬그래프/수치 확인이 안정적.

### 베이스 셸 재사용 원칙 (slow_planet.html 기준 — 파일은 삭제됨, 레이아웃 원칙만 계승)
- 좌측 폰 프레임(`#canvas-wrap` 360×780) · 제목(`#phone-title`) · 하단 점수카드(`#cards`)
  · 우측 컨트롤 패널(`#sliders`: 슬라이더 4개 + 입력 버튼 + 트리거) — **레이아웃 그대로 유지**
- 슬라이더 draft → `입력` 버튼 → `applyScores()` → `scores{}`/카드 반영 흐름 유지
- **교체 대상**: 좌측 3D 영역만. `THREE.SphereGeometry` 지구 + 대기권 + 지구 텍스처
  + 구면 보상 배치 → 3D 갤러리 실내 공간으로 교체
- 참고 셸엔 점수→그래픽 반응 로직이 거의 없음(카드 텍스트만 갱신, 트리거 리스너 없음)
  → Slow Museum에서 점수 연동·트리거 반응을 **새로 설계·구현**
- 향후: 컨트롤 패널 1개 + 좌측에 2개 이상 테마 화면 병렬 비교
  → 좌측 영역은 독립 모듈처럼 교체·다중 인스턴스화 가능한 구조로 설계

## 공간 구조 (3D 실내)
한 층 갤러리 실내를 3D로 구성. 중앙홀 + 3면 벽체.
```
[중앙홀]       — 잘 움직이기 — 입체 조각 전시대 3~5개
[왼쪽 벽체]    — 잘 쉬기     — 풍경화 3~5점
[중앙 벽체]    — 잘 가꾸기   — 초상화/인물화 3~5점
[오른쪽 벽체]  — 잘 다스리기 — 추상화 3~5점
```

## 조명 / 점수 연동
- **자연광 연출**: 태양이 왼쪽에서 떠서 오른쪽으로 지듯 광원이 좌→우 이동하며
  갤러리 내부를 비춤 (slow_planet의 Directional `sun` 활용/확장)
- 점수 높을수록 해당 존 밝아짐 → 작품이 선명하게 빛남 / 낮을수록 어두워짐(패널티)
- 광원 이동속도로 노화속도를 표현하려는 구상은 있으나 **구현은 나중**
- **노화속도 시각화 오브제는 당분간 보류** (모래시계/아틀라스 검토 보류)

## 평면 작품 표현 방식
- 3D 공간 내 벽면에 액자(plane + texture)로 배치
- 클레이 스타일 불가 (조소처럼 보이는 문제)
- 재질 변환 방식: 유화→페이퍼크래프트, 수채화→파스텔화 등
- AI로 스타일 재해석하여 생성 (방식 미확정)

## 보상 테이블

### 중앙홀 — 잘 움직이기 / 조각 (20개)
| # | 작품 | 작가/시대 |
|---|------|---------|
| 1 | 원반 던지는 사람 | 미론 (고대 그리스) |
| 2 | 밀로의 비너스 | 작자미상 (고대 그리스) |
| 3 | 사모트라케의 니케 | 작자미상 (고대 그리스) |
| 4 | 생각하는 사람 | 로댕 |
| 5 | 론다니니 피에타 | 미켈란젤로 |
| 6 | 다비드상 | 미켈란젤로 |
| 7 | 발레리나 | 드가 |
| 8 | 벌룬독 | 제프 쿤스 |
| 9 | 튤립 | 제프 쿤스 |
| 10 | 스파이더 | 루이스 부르주아 |
| 11 | 클라우드 게이트 | 아니쉬 카푸어 |
| 12 | 간다라 불상 | 고대 간다라 |
| 13 | 누워있는 형상 | 헨리 무어 |
| 14 | TV 로봇 | 백남준 |
| 15 | 공간 속의 독특한 형태의 연속성 | 움베르토 보치오니 |
| 16 | 해머링 맨 | 조나단 보롭스키 |
| 17 | 라마수 | 메소포타미아 |
| 18 | 람세스 2세 입상 | 고대 이집트 |
| 19 | 병마용 | 고대 중국 |
| 20 | 작품 미정 | 자비에르 베이앙 |

### 왼쪽 벽체 — 잘 쉬기 / 풍경화 (20개)
| # | 작품 | 작가 |
|---|------|------|
| 1 | 전함 테메레르 | 윌리엄 터너 |
| 2 | 눈보라 | 윌리엄 터너 |
| 3 | 인상, 일출 | 클로드 모네 |
| 4 | 수련 | 클로드 모네 |
| 5 | 건초더미 | 클로드 모네 |
| 6 | 루앙 대성당 | 클로드 모네 |
| 7 | 그랑드 자트 섬의 일요일 오후 | 조르주 쇠라 |
| 8 | 별이 빛나는 밤 | 반 고흐 |
| 9 | 삼나무가 있는 밀밭 | 반 고흐 |
| 10 | 아몬드 꽃 | 반 고흐 |
| 11 | 열대 폭풍우 | 앙리 루소 |
| 12 | 잠자는 집시 | 앙리 루소 |
| 13 | 생트 빅투아르 산 | 폴 세잔 |
| 14 | 타히티의 해변 | 폴 고갱 |
| 15 | 봄 | 피사로 |
| 16 | 개양귀비 밭 | 클로드 모네 |
| 17 | 더 큰 첨벙 | 데이비드 호크니 |
| 18 | 그라운드 스웰 | 에드워드 호퍼 |
| 19 | 나이트호크스 | 에드워드 호퍼 |
| 20 | 피레네의 성 | 르네 마그리트 |

### 중앙 벽체 — 잘 가꾸기 / 초상화·인물화 (20개)
| # | 작품 | 작가 |
|---|------|------|
| 1 | 진주 귀걸이를 한 소녀 | 페르메이르 |
| 2 | 모나리자 | 레오나르도 다빈치 |
| 3 | 비트루비우스적 인간 | 레오나르도 다빈치 |
| 4 | 자화상 | 렘브란트 |
| 5 | 우유 따르는 여인 | 페르메이르 |
| 6 | 꿈 | 피카소 |
| 7 | 자화상 | 반 고흐 |
| 8 | 자화상 | 프리다 칼로 |
| 9 | 그랑드 오달리스크 | 앵그르 |
| 10 | 마담 X | 존 싱어 사전트 |
| 11 | 샤넬 초상화 | 마리 로랑생 |
| 12 | 물랭 루주 | 툴루즈 로트렉 |
| 13 | 댄서들 | 드가 |
| 14 | 헨리 8세 초상 | 한스 홀바인 |
| 15 | 휘파람 부는 소년 | 호머 |
| 16 | 마릴린 먼로 | 앤디 워홀 |
| 17 | 거울 앞의 여인 | 로이 리히텐슈타인 |
| 18 | 유디트 | 구스타프 클림트 |
| 19 | 잔 에뷔테른 | 모딜리아니 |
| 20 | 작품 미정 | 보테로 |

### 오른쪽 벽체 — 잘 다스리기 / 추상화 (20개)
| # | 작품 | 작가 |
|---|------|------|
| 1 | 빨강 파랑 노랑의 구성 | 몬드리안 |
| 2 | 구성 8번 | 칸딘스키 |
| 3 | 노란색 빨간색 파란색 | 칸딘스키 |
| 4 | 화려한 날개의 미소 | 호안 미로 |
| 5 | 여인, 새, 별 | 호안 미로 |
| 6 | 나와 마을 | 샤갈 |
| 7 | 에펠탑 | 샤갈 |
| 8 | 화이트 센터 | 마크 로스코 |
| 9 | No. 14 | 마크 로스코 |
| 10 | 검정 사각형 | 말레비치 |
| 11 | 검정 원 | 말레비치 |
| 12 | 검정 십자가 | 말레비치 |
| 13 | 호박 | 쿠사마 야요이 |
| 14 | 푸른 말 | 프란츠 마르크 |
| 15 | 달팽이 | 마티스 |
| 16 | 이카루스 | 마티스 |
| 17 | 미래주의를 위한 구성 | 알렉산드라 엑스테르 |
| 18 | 어디서 무엇이 되어 다시 만나랴 | 김환기 |
| 19 | 저녁노을 | 김환기 |
| 20 | 작품 미정 | 올라퍼 엘리아슨 |

## 작업 이력

### 완료
- [x] index.html 골격 (slow_planet 셸 재사용, 좌측만 갤러리로 교체) + 파일명 index.html
- [x] 갤러리 3D 실내 (바닥/천장/중앙·좌·우 벽), 카메라 수평 고정(수직선 평행)
      + 렌즈 시프트(카드 위 정렬) + FOV(`CAM_FOV` 계산, 360×780에서 ≈70.3°로 옛 가로시야 보존) + 회전한계
- [x] 입력: 1포인터 드래그 좌우회전(수직패닝 없음) · 휠/핀치 줌 · 클릭 ·
      빈곳/천장 클릭 복귀. 모드: `free`/`transition`/`focus`/`overview`
- [x] 단독 감상(focus): 깨끗한 배경벽 격리 + 카드 위 정렬 + **카메라 궤도 턴테이블
      (작품 transform 불변 → 리셋 시 잔존 없음)** + 빈곳 클릭 시 숨은 작품 픽 제외
- [x] 아이소메트릭 전경 오버뷰(휠 줌아웃 한계→전환, 드래그 방위회전, 근접 벽 작품 숨김)
- [x] 조명: 환경/반구/약한 sun + 존 스포트(점수 연동) + 정면벽 밝게(코너 대비) +
      왼쪽벽 전용 재질, 배경색. **조각별 개별 스포트라이트**(레이어 아님 — `distance`로
      전시대 밑동까지만, 바닥 컷오프), thinker는 emissive로 밝힘
- [x] 조각 GLB **gltf-transform 최적화**(meshopt+webp+quantize, ~280MB→8MB),
      원본 삭제·치환. 현재 5개만 전시대 배치(`SCULPT_ADJ`로 scale/ry/ox/bright 보정),
      나머지 모델은 향후 사용 → 보존
- [x] 전시대: 높이 개별값, 밝은 색(#ffffff), **접지(contact) 그림자** plane
- [x] 벽 작품 매핑 (소스 Pillow 여백 크롭 → **JPEG 최적화 후 `<이름>.jpg` 원본명 치환**;
      `.crop`/`.matted` 변형본·미사용 원본 삭제, 신규 추가 원본은 보존):
  - 가운데(초상화/groom): picasso·pearl_earing·matisse·andy_warhol, **면적 1.7 고정**
    (pearl_earing은 여백 안 자른 원본 비율)
  - 오른쪽(추상화/manage): 1·4=“Temporarily off view” 텍스트(작게 H1.3),
    2·3=HK1(여백 합성본)·HK2(원본 여백) — **세로길이 1.9·걸리는높이만 일치**, 가로는 비율대로
  - 왼쪽(풍경화/rest): cypresses·water_lilies·“Temporarily off view”·inwang, **면적 2.3 고정**
- [x] 로딩 최적화: 멀티스레드 dev 서버 + 회화 PNG→JPEG(원본명) → 초기 로드 대폭 단축
- [x] 조각 외곽선 안티알리아싱: `EffectComposer`에 WebGL2 멀티샘플 타깃 전달
      (후처리가 renderer MSAA를 우회하던 문제 해결)
- [x] 피사계 심도(DOF): `EffectComposer`+`BokehPass`+`GammaCorrection`.
      focus=양수 월드거리(앞줄 조각), 모드별 자동, `aperture 0.0016 / maxblur 0.012`
- [x] UI 키컬러 웜그레이 `#7d7169`, 제목 `#675d56`(키컬러 계열·약간 어둡게)
- [x] GitHub origin/main 푸시 (asset 포함)

### 미구현 / 다음
- [ ] 트리거 버튼 반응 로직 (현재 버튼만 있고 리스너 없음 — 신규 설계)
- [ ] 점수 슬라이더→존 밝기 외 다른 반응(보상 추가 등) 구체화
- [ ] 좌측 영역 모듈화 (향후 다중 테마 병렬 비교)
- [ ] 미정 작품 확정(자비에르 베이앙/보테로/올라퍼 엘리아슨), 나머지 보상 작품 채우기
- [ ] (보류) 노화속도 = 태양 좌→우 이동속도 연동 (`sun` 애니메이션)

## 코드 맵 (다른 기기에서 이어서 작업 시 — index.html 내 조절 지점)
- **벽↔존 매핑**: rest=왼쪽/풍경, groom=가운데/초상, manage=오른쪽/추상, move=중앙홀/조각.
  각 `zones.{key}.items[0..3]`이 프레임(생성 z순). 프레임=`makeFrame` 그룹
  (`userData.art`=그림 plane, `userData.frame`=테두리 box).
- **벽별 균일 간격**(`layoutWallUniform`): 4프레임 로드 완료 시 자동 호출.
  첫·마지막 프레임 센터(p0·p3) 유지 → 전체 폭 보존, 가운데 둘(p1·p2)을
  모서리 간격 G가 균일하도록 재배치. 벽마다 G 독립 계산. 프레임 외곽폭은
  `userData._outerW` (W+0.16, fitFrameBy*에서 설정).
- **벽 작품 배치/크기**: `GROOM_ART`(배열·순서), `GROOM_AREA`(면적) ·
  `MANAGE_ART_H`/`MANAGE_NOTICE_H`(세로길이) + `[['HK1.jpg',1],['HK2.jpg',2]]` ·
  `LANDSCAPE_AREA` + `[['cypresses',0],...]`. 사이즈 함수: `fitFrameByArea` / `fitFrameByHeight`.
  로더는 모두 `asset/<존>/<이름>.jpg` 단일 원본명 로드(`GROOM_SRC` 등 변형 매핑 없음).
  안내문구는 `makeNoticeTexture(['Temporarily','off view'])` (canvas, `NOTICE_ASPECT`).
- **조각**: `SCULPT_ADJ[name]={scale,ry,ox,oy,oz,bright}`(oy=Y −=아래, oz=Z +=앞/관람자쪽,
  월드단위. 앉은자세 등 전시대 걸침용. oy −1.0=전시대높이만큼 아래),
  `SCULPT_H`(균일 높이 기준), `PED_LAYOUT`(x,z,전시대높이,모델명). 조각별 스포트 = 로더 내
  `spot`(intensity 2.8, `spot.distance`=전시대 밑동까지). 접지그림자=`_contactShadowTex`.
- **카메라/뷰**: `camera`(fov=`CAM_FOV`, 옛 384×768·FOV66°의 가로시야를 현재 W/H에서 보존),
  `VIEW_SHIFT_Y`(렌즈시프트), `YAW_LIMIT`,
  `applyCam`, 트윈 `startTween`/`focusOn`/`returnToInit`, 오버뷰 `OVERVIEW`/`enterOverview`.
- **단독감상 프레이밍**(`computeSoloPose`): 그림=중심·`SOLO_FILL` 0.6(불변).
  조각=`SOLO_FILL_SCULPT` 0.85(더 크게)·`SOLO_SCULPT_VBIAS` 0.42(<0.5=바닥 고정·위로 키움)·
  `SOLO_SHIFT_SCULPT` 30(화면에서 위로 올리는 렌즈 시프트px). 그림 `SOLO_SHIFT_FRAME`=CARD_H/2−50(≈84).
  `vHalf`로 비대칭 조준 시 상/하 안 잘리게 d 산출.
- **단독감상 작품해설 라벨**(`#art-label`, `showArtLabel`/`updateArtLabelPos`/`hideArtLabel`):
  미술관 캡션. **작품 기준 배치**(화면 X): (작품+전시대) bbox 바닥중앙 = `_alAnchor`(월드,
  focus 동안 고정) → 매 프레임 `camera.project`로 투영, 그 **20px 아래**(조각·그림 동일).
  제목=현재 파일명(`userData._art`/`_sculpt`, 추후 재라벨), 획득일=`LOADED_AT`(갤러리 로딩시각),
  보상사유=`REWARD_MSG[zone]` 회화체 플레이스홀더(점수상승+근거 원시데이터). focus 시
  `#cards` 숨김→복귀 복원. 단독감상에선 점수카드 항상 숨김(의도 확정).
- **단독감상 조명**: 그림=`placeFrameFocus` 부드러운 정면광(`FOCUS_FRAME_INT`1.1·`DIST`3.0,
  원거리=핫스팟 없음·시선 추종·채움 0). 존 스포트는 측면벽을 비스듬히 훑어 그림 정면이
  어두워서 정면광 필요(과노출 났던 근접·고세기 1.5@1.2u 대신 원거리·저세기).
  조각=`placeSculptFocus()` 일관 배치(`focusOn`·회전 동일 함수 → 첫프레임 과노출/점프 제거):
  키=시선방향·`FOCUS_SCULPT_DIST`3.2·`FOCUS_SCULPT_INT`0.85·`KEYY`1.4 +
  위 채움 `focusFill`(`FOCUS_SCULPT_FILL`0.5·`FILLY`3.0, 회전해도 고정→뒷면 안 까맘).
  전부 조절 상수.
- **DOF**: `bokeh.uniforms.aperture/maxblur`(블러 세기), `dofFocusDistance()`(모드별 초점).
  `composer` 패스 체인: RenderPass→BokehPass(needsSwap=true)→GammaCorrection.
  `_composerTarget`=WebGL2 멀티샘플 타깃(`samples` 4) → 후처리에도 MSAA(조각 외곽선).
- **dev 훅**: `window.__debug = { camera, scene, zones, focusables, focusOn,
  returnToInit, composer, bokeh, state() }` — 검증/디버그용.
- **에셋 가공**: 조각 최적화 = `npx @gltf-transform/cli optimize <in> <out>
  --compress meshopt --texture-compress webp --texture-size 1024
  --simplify-ratio 0.1 --simplify-error 0.01`. 이미지: Pillow로 여백 크롭(소스) →
  **`sips -s format jpeg -s formatOptions 85`로 JPEG 최적화 → `<이름>.jpg` 원본명 치환**
  (변형 suffix 미사용, 미최적화 소스는 삭제 금지). HK1 여백합성 = 흰 캔버스 패딩.

## 전시 최적화 5턴 작업 (진행 중)

각 폴더 20개씩. **파일명 알파벳순**으로 4개씩 5턴. 그림=벽 4프레임(좌→우=알파벳순),
조각=회전 슬롯 #1·#3·#4·#5(알파벳 4개). **#2(앞열 중앙)=전 턴 고정 기준작 `thrower`**
(`PED_FIXED`, 검증값 scale.9·ryπ/4·h0.3 그대로). thrower는 회전 시퀀스에서 제외(중복방지)
→ thrower가 알파벳상 속한 T4는 회전이 3개(나머지 1슬롯 빔).

### 규칙
- 그림: mat(여백) 크롭(**Pillow** `.claude/matcrop.py`) → 종횡비 유지 →
  벽별 면적상수로 옆 작품과 면적 유사. portrait `GROOM_AREA 1.7`(area-fit),
  landscape `LANDSCAPE_AREA 2.3`(area-fit), abstract도 면적-fit으로 통일
  (기존 height-fit HK1/HK2 제외 — 아래 검증유지 규칙).
- **작업본 서픽스 규칙**: 원본 `<이름>.<ext>`는 **건드리지 않고** 크롭/최적화 결과를
  `<이름>.work.jpg`로 저장. 로더는 `*.work.jpg` 있으면 그걸, 없으면 원본 로드.
  최종 확정 시에만 `*.work.jpg`→원본명 치환(원본 삭제). 흰여백 추가 지정 그림은
  지정 시 반영.
- **검증유지 규칙**: 현재 씬에 이미 있던(=1차 검증된) 모델/그림이 알파벳 시퀀스에서
  등장할 때는 **지금 셋팅값 그대로** 사용(재크롭/재계산 안 함).
- 조각: 전시대 높이는 **사용자가 모델별로 지정** → 지정되면 per-sculpture로 기록.
  높이/스케일/ry/ox/bright는 모델 속성으로 취급(전시대 슬롯과 무관하게 따라다님).
- **모델↔전시대 페어링 불변식 (영구·전 턴 동일 적용)**:
  - 전시대 *크기*(h·`SCULPT_PED_WX`·`SCULPT_PED_WZ`)는 **모델에 고정 페어링**.
    전시 *슬롯/위치*는 턴마다 가변(`PED_ASSIGN`).
  - **좌우(X)**: 전시대는 항상 슬롯 기본 X에 **중심(center) 정렬** → 크기가 변해도
    중심 불변·좌우 대칭(예: balloon_dog 중심 = brancusi 중심의 대칭점).
    wx 변경 시 중심 기준 양옆 균등 확장, 기본 위치로 재정렬.
  - **앞뒤(Z)**: 전시대 **앞면(+Z) 라인 고정**, 깊이(wz) 증가는 **뒤(−Z)로만**.
    앞뒤 정렬은 절대 불변. (`makePedestal`의 `zc=0.4−D/2`가 이를 보장)
  - 검증값(T1): balloon_dog 전시대 Xc=−1.2 ↔ brancusi Xc=+1.2(대칭),
    앞면 둘 다 world z=−5.1.

### 검증된 베이스라인 (현재 셋팅값 — 등장 시 유지)
- 조각 `SCULPT_ADJ` / 전시대높이(h): milo `{}`·h0.3 · thrower `{scale:.9,ry:π/4}`·h0.3 ·
  nike `{scale:.9,ry:0}`·h0.3 · thinker `{scale:.88,ry:π/6,bright:.9,ox:0}`·h0.6 ·
  brancusi `{scale:.66,ry:0}`·h1.0 · balloon_dog `{scale:.81,ry:55°(π/4+π/18),ox:0.2}`·**전시대폭 ×1.8** ·
  ballerina `{scale:1,ry:0,bright:.9}` · abstract `{scale:1,ry:−45°(−90+45)}`. (`SCULPT_H` 1.7 정규화 기준)
  전시대 가로폭 `SCULPT_PED_WX[name]`·깊이 `SCULPT_PED_WZ[name]`(기본 1, **해당 모델 전용·턴 유지**)
  → `makePedestal(h,wx,wz)`: 가로=X 배율, 깊이=**앞면(+Z) 고정·뒤로만 확장**(조각 무왜곡).
  현재 balloon_dog: WX 1.8 · WZ 1.4.
- 그림: portrait area 1.7(pearl_earing은 **mat 크롭 안 함·원본 비율**),
  abstract HK1/HK2 height-fit 1.9, landscape area 2.3.

### 턴 배치표 (알파벳순)
- portrait: T1 andy_warhol·bbc_interview·coco·dancers / T2 fifer·girl_cat·gogh·green_line /
  T3 italian_woman·jeanne·lydia·milkmaid / T4 mona_lisa·pearl_earing·picasso·primavesi /
  T5 raffaelo·renaissance·rose_hair·tango  (검증유지: pearl_earing·picasso T4.
  andy_warhol는 가장자리 흰라인 제거 위해 `!` 해제 → 좌4·우10·하10px 크롭 work본 사용, 원본 보존)
- abstract: T1 HK1·HK2·YK_1·YK_2 / T2 joan_miro_1·joan_miro_2·jp_1·jp_2 /
  T3 malevichi_1·malevichi_2·malevichi_3·matisse_1 / T4 matisse_2·mondrian_1·mondrian_2·paul_klee_1 /
  T5 paul_klee_3·paul_klee_4·rothko_1·rothko_2  (검증유지: HK1·HK2 T1, height-fit 1.9)
- landscape: T1 No180·campo_vaccino·cite·cypresses / T2 early_morning·exotic_forest·garden·grande_jatte /
  T3 inwang·lady_on_a_beach·le_reve·little_house / T4 roadtoyork·rouen_athedral·schloss_kammer·suburb /
  T5 summer·tollgate·view_of_venice·water_lilies  (검증유지: cypresses T1, inwang T3, water_lilies T5)
- sculpture(슬롯 #1·#3·#4·#5): T1 abstract·ballerina·balloon_dog·brancusi /
  T2 bust·carol_gold·colossus·henry_moor / T3 ionia·listening·mauryan·milo /
  T4 nike·song·thinker·thrower / T5 tulip·walker·warrior·zeus
  (검증유지: brancusi T1, milo T3, nike·thinker·thrower T4)

### 진행 상황
- [x] T1  - [x] T2  - [x] T3  - [x] T4 (사용자 승인 완료)  - [~] T5 (씬 구성됨·검토중)
  - 코드: 그림/조각 로더 턴 구동화(`TURN`·`EXHIBIT`·`SCULPT_SEQ`·`PED_ASSIGN`),
    MANAGE_AREA=2.0, #2=고정 thrower(`PED_FIXED`), `PED_DEFAULT_H`=0.45
  - **T1 확정값**: 조각 보정 balloon_dog `{scale:.81,ry:55°,ox:0.2,WX1.8,WZ1.4}` ·
    ballerina `{bright:.9}` · abstract `{ry:−45°}`. 전시대높이=brancusi 1.0,
    나머지(abstract·ballerina·balloon_dog) 기본 0.45 수용(별도 지정 없었음).
    그림: 전부 `.work.jpg`(원본 보존), andy_warhol 좌4·우10·하10 크롭.
  - **T2 조각↔슬롯**: #1=bust · #3=henry_moor · #4=colossus · #5=carol_gold · #2=비움
    (SCULPT_SEQ T2 구간 **수동 배치** — 알파벳 턴멤버십은 불변).
    그림 12개 `.work.jpg` 생성(원본 보존, 일부 mat 크롭됨).
    girl_cat(구 gir_cat 오타수정): 수동 크롭 L22·R7·T4·B30(원본 675×1000).
    early_morning: 흰매트 제거 L94·R104·T54·B50(원본 1134×852).
    exotic_forest: 아트포스터(텍스트·키라인 포함)→원화만 크롭(622×827) 후
    깨끗한 흰 mat(짧은변 9%≈56px) 재합성. 원본 보존.
  - **T2 조각 보정**: bust `{scale:.792}`·전시대 h1.0(brancusi와 동일) ·
    carol_gold `{scale:1.17,ox:0.075}`·전시대 h0.15 · colossus `{scale:1.0935}`·전시대 h0.3 ·
    henry_moor `{scale:.72,ry:90°,ox:0.08}`·전시대 h0.6(thinker와 동일)·`WX 1.15`(룰대로 슬롯센터 대칭).
    (h0 → `makePedestal` base/그림자 생략, 조각 바닥에 직접)
  - **T3 조각↔슬롯**: #1=mauryan · #3=listening · #4=ionia · #5=milo · **#2=thrower(고정 기준작)**
    (SCULPT_SEQ T3 구간 수동 배치 — 알파벳 턴멤버십 불변).
    listening 전시대 h1.0(bust와 동일)·앉은자세 `{oy:-0.79, oz:0.4}`(전시대 걸침, 튜닝 중).
    h 0.936 → **전부 1.0으로 정리**(brancusi·bust·listening). `oy`·`oz` 보정 신설.
    milo는 **검증유지**(T1: h0.3·SCULPT_ADJ 무) → 기존값 그대로. listening 신규(기본).
    ionia `{scale:0.855}`·mauryan `{scale:1.1}` 둘 다 **전시대 없음(h0)·접지그림자만**
    (`makePedestal`: 접지 그림자를 `if(h>0)` 밖으로 빼 **항상 생성** → h0도 바닥 그림자.
    h>0 동작 동일). 그림: inwang **검증유지**(원본 직접·area2.3),
    나머지 11개 `.work.jpg` 생성(원본 보존, 일부 mat 크롭).
    milkmaid: 수동 크롭 L14·R30·T10·B34(원본 863×1000).
    little_house: 수동 크롭 R30·B30(원본 512×507).
  - **T3 검토 대기**: 조각 scale/높이/ry/ox/bright + 그림 mat·크기 피드백 → 기록 후 반영
  - **T4 조각↔슬롯**: #1=nike(검증유지) · **#2=thrower(고정 기준작)** · #3=song · #4=thinker(검증유지) ·
    **#5=tulip**(SCULPT_SEQ에서 thrower↔tulip 교환 → 빈 슬롯이 T4→T5로 이동).
    nike·thinker는 검증값 그대로(scale.9·ry0 / scale.88·ry π/6·bright.9·ox0).
    song `{}`·전시대 h0.3(최저, nike와 동일). tulip `{scale:0.8, ox:0.2}`·기본 전시대 h0.45.
    그림: pearl_earing·picasso **검증유지**(원본 직접), 나머지 10개 `.work.jpg` 생성(원본 보존,
    일부 mat 크롭. roadtoyork.png→jpg 등 최적화).
    primavesi: 아트포스터(GUSTAV KLIMT 텍스트·키라인)→원화만 크롭(1260×1596) 후
    깨끗한 흰 mat(짧은변 9%≈113px) 재합성. 원본 보존(1400×2000).
    paul_klee_1: 풀-블리드 원화에 흰 mat(짧은변 9%≈83px) 패딩만 추가(원본 922×1280→1088×1446).
    mondrian_1: 아트포스터(PIET MONDRIAN 텍스트)→원화만 사방 검출 크롭(901×1356), mat 미추가. 원본 1143×1600 보존.
  - **T4 검토 대기**: song·primavesi·mona_lisa 등 신규 조정 + 그림 mat·크기 피드백 → 반영
  - **T5 조각↔슬롯**: #1=thrower(검증) · **#2=carol_gold(고정 기준작)** · #3=zeus · #4=warrior · #5=walker
    (PED_FIXED가 thrower→carol_gold로 변경된 상태라 T5에서 thrower가 #1 회전으로 등장.
    T5 수동배치: walker↔zeus 교환).
    walker `{scale:0.88}`·전시대 h0.6 · zeus `{scale:0.72}`·전시대 h0.6 · warrior 신규(기본). 그림: water_lilies **검증유지**(원본 직접·area2.3),
    나머지 11개 `.work.jpg` 생성(원본 보존. rothko_1.png 2.9MB→152KB, tango 1.7MB→520KB 등 최적화).
    rothko_1: 사진 배경 제거→원화 크롭(1349×1418, 하단 +10px 더 트림)+흰mat 121px 재합성.
    원본 .png 1352×1454 보존. **height-fit 1.9 적용**(`MANAGE_HEIGHT_KEEP`에 추가) → mat 포함해도
    원화 자체 면적이 다른 작품과 유사하게 큼(HK1/HK2 사이즈).
    rothko_2: 풀-블리드 원화에 흰mat 68px(짧은변 9%) 패딩, **height-fit 1.9 적용**(rothko_1과 동일 방식).
    원본 770×759 보존, work 906×895.
  - **T5 검토 대기**: walker·warrior·zeus 신규 조정 + 그림 mat·크기 피드백 → 반영
