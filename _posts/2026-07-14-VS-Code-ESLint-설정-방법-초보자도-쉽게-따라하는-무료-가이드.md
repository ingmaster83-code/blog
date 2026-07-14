---
layout: post
title: "VS Code ESLint 설정 방법, 초보자도 쉽게 따라하는 무료 가이드"
date: 2026-07-14
description: "VS Code ESLint 설정 방법을 자주 발생하는 오류와 함께 알려드립니다. 설치부터 적용까지 30초면 해결. WooaVS로 최신 버전을 무료로 시작하세요."
categories:
  - "vs"
tags:
  - "VS Code ESLint 설정 방법"
  - "ESLint 설치 오류"
  - "VS Code 확장팩 추천"
  - "WooaVS"
  - "코드 정리 자동화"
  - "린터 설정 노하우"
  - "ESLint Prettier 충돌 해결"
kit: "vs"
faq:
  - q: "ESLint 설치 후 VS Code에서 빨간 줄이 사라지지 않아요. 어떻게 해야 하나요?"
    a: "VS Code를 재시작한 후 명령 팔레트(Ctrl+Shift+P)에서 'ESLint: Restart ESLint Server'를 실행해보세요. 그래도 안 되면 `.eslintrc` 파일이 프로젝트 루트에 있는지 확인합니다."
  - q: "ESLint와 Prettier 규칙이 충돌할 때는 어떻게 해결하나요?"
    a: "`eslint-config-prettier` 패키지를 설치하고 ESLint 설정의 extends 배열 마지막에 'prettier'를 추가하면 Prettier와 충돌하는 규칙이 비활성화됩니다."
  - q: "링크가 공식 배포처로 연결되나요?"
    a: "네. 모든 다운로드 링크는 각 프로그램의 공식 홈페이지로 연결되며, 항상 최신 버전을 안전하게 받을 수 있도록 주기적으로 점검합니다."
---

VS Code에서 ESLint를 설정하려다 빨간 줄이 멈추지 않거나, Prettier와 충돌이 나서 코드가 엉망이 된 경험, 한 번쯤 있으시죠? 저도 처음에는 공식 문서만 보고 따라 했다가 오히려 더 헤맸습니다. 오늘은 제가 실제로 겪었던 **VS Code ESLint 설정 방법**을, 자주 발생하는 실수와 해결법 중심으로 정리해드리겠습니다. 초보자도 10분 안에 완벽하게 세팅할 수 있습니다.

---

## 왜 ESLint 설정이 자주 꼬일까?

ESLint는 자바스크립트와 타입스크립트 코드에서 문법 오류나 잠재적 버그를 잡아주는 강력한 도구입니다. 하지만 VS Code에서 제대로 작동하려면 세 가지가 정확히 맞아야 합니다. 확장 프로그램 설치, 프로젝트 내 패키지 설치, 그리고 설정 파일의 위치.

가장 흔한 실수는 VS Code 확장팩만 설치하고 프로젝트에 `eslint` 패키지를 설치하지 않는 것입니다. 확장팩은 단순히 VS Code와 ESLint를 연결해주는 다리 역할만 합니다. 실제 린트 규칙을 적용하려면 프로젝트에 `eslint`가 설치되어 있어야 합니다.

---

## WooaVS로 VS Code 확장팩과 도구를 한 번에 관리하기

이런 번거로움을 줄이기 위해 저는 **WooaVS**를 사용하고 있습니다. [WooaVS 무료로 시작하기](https://vskit.wooahouse.com)에서는 VS Code에 필요한 각종 확장팩과 개발 도구를 최신 버전으로 모아서 제공합니다. ESLint뿐만 아니라 Prettier, Live Server, GitLens 등 필수 확장팩을 한 번에 확인하고 설치할 수 있어서 설정 시간을 획기적으로 줄일 수 있습니다.

---

## VS Code ESLint 설정 방법: 단계별 가이드

### 1. 필수 패키지 설치하기

터미널을 열고 프로젝트 폴더에서 아래 명령어를 실행하세요.

```bash
npm install eslint --save-dev
```

만약 타입스크립트를 사용한다면 추가 패키지도 필요합니다.

```bash
npm install @typescript-eslint/parser @typescript-eslint/eslint-plugin --save-dev
```

**실수 포인트**: `--global` 옵션으로 전역 설치하면 안 됩니다. 프로젝트마다 다른 ESLint 버전과 규칙을 사용해야 하므로 반드시 `--save-dev`로 로컬 설치해야 합니다.

### 2. 설정 파일 생성하기

```bash
npx eslint --init
```

이 명령어를 실행하면 인터랙티브 모드가 시작됩니다. 여기서 자주 하는 실수는 "What type of modules does your project use?"에서 잘못 선택하는 것입니다. JavaScript 파일에서 `import`/`export`를 사용한다면 "ES modules"를, `require()`를 사용한다면 "CommonJS"를 선택하세요.

### 3. VS Code 확장팩 설치 및 설정

VS Code 좌측 확장 탭에서 "ESLint"를 검색해 Microsoft 공식 확장팩을 설치합니다. 설치 후 `settings.json`에 아래 설정을 추가하면 저장할 때 자동으로 코드를 정리해줍니다.

```json
{
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "eslint.validate": ["javascript", "javascriptreact", "typescript", "typescriptreact"]
}
```

---

## 자주 발생하는 오류와 해결법

### 오류 1: "ESLint is not running"

VS Code 하단 상태 표시줄에 ESLint 아이콘이 빨간색 X로 표시된다면, 명령 팔레트(Ctrl+Shift+P)에서 "ESLint: Restart ESLint Server"를 실행하세요. 그래도 안 되면 `node_modules` 폴더를 삭제 후 `npm install`을 다시 실행합니다.

### 오류 2: Prettier와 규칙 충돌

ESLint와 Prettier가 동시에 들여쓰기나 따옴표 규칙을 적용하려다 충돌하는 경우입니다. 해결 방법은 간단합니다.

```bash
npm install eslint-config-prettier --save-dev
```

그리고 `.eslintrc` 파일의 `extends` 배열 가장 마지막에 `"prettier"`를 추가하세요. 그러면 Prettier와 충돌하는 모든 ESLint 규칙이 자동으로 비활성화됩니다.

### 오류 3: 설정 파일을 찾지 못함

VS Code가 프로젝트 루트에서 `.eslintrc` (또는 `.eslintrc.json`, `.eslintrc.js`) 파일을 찾지 못하면 오류가 발생합니다. 이때는 VS Code 상단 메뉴에서 **파일 > 기본 설정 > 설정**으로 이동해 `eslint.workingDirectories`를 검색한 후, 프로젝트 폴더 경로를 추가하면 해결됩니다.

---

## 실전 활용 팁: 팀 협업을 위한 ESLint 최적화

팀 프로젝트에서는 ESLint 규칙을 팀원 모두가 동일하게 적용해야 합니다. 이때 유용한 팁은 `eslint-plugin-import`를 추가하는 것입니다. 이 플러그인은 import 문의 순서를 강제하고, 사용하지 않는 import를 자동으로 제거해줍니다.

설치는 간단합니다.

```bash
npm install eslint-plugin-import --save-dev
```

`.eslintrc`에 아래 규칙을 추가하세요.

```json
{
  "plugins": ["import"],
  "rules": {
    "import/order": ["error", { "alphabetize": { "order": "asc" } }]
  }
}
```

이제 팀원이 코드를 저장할 때마다 import 문이 알파벳 순서로 자동 정렬됩니다. 코드 리뷰 시간을 대폭 줄일 수 있는 꿀팁입니다.

또한, CI/CD 파이프라인에 ESLint 검사를 포함시키는 것도 좋은 방법입니다. `package.json`의 `scripts`에 아래 명령어를 추가하면 됩니다.

```json
"scripts": {
  "lint": "eslint src/"
}
```

GitHub Actions나 GitLab CI에서 `npm run lint`를 실행하면, 린트 오류가 있는 코드는 병합 자체가 거부되도록 설정할 수 있습니다.

---

## 마무리하며

**VS Code ESLint 설정 방법**은 한 번 제대로 익혀두면 개발 생산성이 확연히 달라집니다. 오늘 소개해드린 실수와 해결법을 기억하시면 더 이상 빨간 줄 때문에 스트레스받지 않으실 거예요.

혹시 어떤 확장팩을 설치해야 할지, 어떤 버전이 최신인지 헷갈리신다면 [WooaVS에서 필요한 도구를 한 번에 확인해보세요](https://vskit.wooahouse.com). 모든 링크는 공식 배포처로 연결되어 있어 안전하게 최신 버전을 받을 수 있습니다. 지금 바로 깔끔한 코드 정리의 세계로 들어와 보세요.