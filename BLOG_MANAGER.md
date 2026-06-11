# WooaHouse 블로그 자동 포스팅 매니저

## 개요

`blog_manager.py` — DeepSeek API로 SEO 블로그 글을 자동 생성하고 GitHub Pages에 배포하는 GUI 프로그램.

- **블로그 URL:** https://blog.wooahouse.com
- **저장소:** `C:\개인\wooahouse\blog\`
- **실행:** `python blog_manager.py`
- **기술:** Python + customtkinter GUI + DeepSeek API + Jekyll (GitHub Pages)

---

## 실행 방법

```
cd C:\개인\wooahouse\blog
python blog_manager.py
```

---

## GUI 주요 기능

| 기능 | 설명 |
|------|------|
| Kit 필터 | 드롭다운으로 특정 사이트(pdf, 이미지, qr…) 키워드만 표시 |
| 키워드 목록 버튼 | 전체 키워드를 팝업으로 표시 (완료/대기 배지 포함) |
| 생성 개수 슬라이더 | 1~100개 설정 |
| 잔액 새로고침 버튼 (↻) | DeepSeek API 잔액 실시간 조회 |
| PC 종료 스위치 | 빨간 토글 ON → 생성 완료 후 60초 카운트다운 후 PC 자동 종료 |
| 실행 버튼 | 설정한 개수만큼 순서대로 글 생성 → Git 커밋 → GitHub Push |

---

## 파일 구조

```
blog/
├── blog_manager.py       ← GUI 실행 파일 (메인)
├── keywords.json         ← 키워드 목록 (done: true/false)
├── BLOG_MANAGER.md       ← 이 파일
├── _posts/               ← 생성된 마크다운 포스트 저장
├── _config.yml           ← Jekyll 설정
├── .github/workflows/    ← GitHub Actions 자동 배포
└── ...
```

---

## keywords.json 구조

```json
[
  {
    "keyword": "PDF 파일 합치기 무료 온라인",
    "kit": "pdf",
    "done": true
  },
  {
    "keyword": "이미지 용량 줄이기 무료 방법",
    "kit": "이미지",
    "done": false
  }
]
```

- `done: true` → 이미 글 생성됨, 스킵
- `done: false` → 생성 대상
- 실행 후 자동으로 `done: true` 처리됨

---

## Kit 목록 (kit 값 → 사이트)

| kit 값 | 사이트명 | URL |
|--------|---------|-----|
| `pdf` | WooaPDF | https://pdfkit.wooahouse.com |
| `이미지` | WooaImage | https://imagekit.wooahouse.com |
| `qr` | WooaQR | https://qrkit.wooahouse.com |
| `텍스트` | WooaText | https://textkit.wooahouse.com |
| `색상` | WooaColor | https://colorkit.wooahouse.com |
| `계산` | WooaCalc | https://calckit.wooahouse.com |
| `ocr` | WooaOCR | https://wooaocr.wooahouse.com |
| `오디오` | WooaAudio | https://wooaaudio.wooahouse.com |
| `동영상` | WooaVideo | https://wooavideo.wooahouse.com |
| `폰트` | FontKit | https://fontkit.wooahouse.com |
| `개발` | WooaDev | https://wooadev.wooahouse.com |
| `뷰어` | WooaViewer | https://wooaviewer.wooahouse.com |
| `시트` | WooaSheet | https://wooasheet.wooahouse.com |

---

## 글 생성 흐름

1. `keywords.json`에서 `done: false` 키워드 중 랜덤 1개 선택
2. DeepSeek API (`deepseek-chat` 모델)에 SEO 프롬프트 전송
3. 응답 파싱 → `[TITLE]`, `[DESC]`, `[TAGS]`, `[FAQ]`, `[BODY]` 추출
4. Jekyll 프론트매터 포함 `.md` 파일 생성 → `_posts/` 저장
5. 해당 키워드 `done: true` 처리
6. 전체 완료 시 Git 커밋 + Push

---

## API 키 경로

```
C:\개인\개인 프로젝트\blogwriter_new\blogger_seo_bot\config\deepseek_api_key.txt
```

---

## 키워드 추가 방법

### 방법 1: 스크립트 사용 (권장)
`C:\개인\wooahouse\add_keywords.py` 수정 후 실행:
```
python C:\개인\wooahouse\add_keywords.py
```

### 방법 2: keywords.json 직접 편집
`done: false`로 항목 추가. `kit` 값은 위 Kit 목록 참조.

### 키워드 작성 규칙
- **형식:** `{도구 기능} 무료 {방법/온라인/방법}` (한국어 검색 쿼리 형태)
- **길이:** 15~30자 권장
- **포함 권장 단어:** 무료, 방법, 온라인, 도구, 추천, 변환, 설치 없이
- 이미 생성된 키워드와 중복되지 않게 확인 후 추가

---

## 알려진 이슈 & 해결법

| 문제 | 원인 | 해결 |
|------|------|------|
| GitHub Actions 배포 실패 (401) | Workflow 권한 부족 | Settings → Actions → General → "Read and write permissions" 설정 |
| 콘솔 한글 깨짐 | Windows cp949 인코딩 | 동작에는 문제없음, 파일 저장은 UTF-8로 정상 처리됨 |
| API 잔액 부족 | DeepSeek 크레딧 소진 | platform.deepseek.com에서 충전 |
| 글 생성 중단 | 네트워크 타임아웃 (90초) | 재실행하면 done:false 키워드부터 이어서 진행 |
