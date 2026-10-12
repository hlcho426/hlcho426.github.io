---
title: Copilot for JetBrains, 진단에서 수정 요청까지의 단계를 줄인다
date: 2026-10-12 00:31:47 +0900
categories:
- 레퍼런스 조사
- 개발 도구
tags:
- Copilot
- JetBrains
- 개발 도구
briefing_type: ai
briefing_event: archive-copilot-jetbrains-diagnostic-fixes
briefing_sources:
- https://github.blog/changelog/2026-10-10-new-controls-and-chat-improvements-in-copilot-for-jetbrains/
briefing_archive: true
---

IDE가 표시한 오류를 다시 설명하고 AI 대화로 옮기는 과정도 반복 작업이다. Copilot for JetBrains는 진단 메뉴에서 수정 요청을 여는 흐름과 연결 도구의 시작 제어를 개선했다. 자동 수정의 성공과 요청 과정의 편의를 구분해 살펴본다.

## 무슨 일이 있었나
{:.briefing-heading}

### 변경 — 진단 메뉴에서 Fix를 선택한다

공식 글은 진단의 intention 메뉴에 Fix 동작이 추가돼 인라인 대화를 열고 수정을 요청한다고 설명한다. 사용할 수 있으면 agent 모드, 그렇지 않으면 ask 모드를 사용한다. 오류를 보여주는 곳에서 수정 요청으로 이동하는 단계를 줄이는 변화다.

### 연결 도구와 계정·세션 제어

Copilot과 Claude에 설정된 MCP 서버의 자동 시작을 끄는 설정도 소개된다. MCP 서버는 에이전트와 외부 기능을 연결하는 도구 제공자다. 자동 시작 제어가 모든 네트워크 사용과 권한을 차단한다는 의미는 아니다. 세션·worktree와 모델 전환 관련 안정성 개선도 함께 안내한다.

### 사용 조건 — 지원 IDE 버전을 확인한다

같은 변경 기록은 JetBrains IDE 2025.1 지원 종료와 2025.2 이상 필요 조건을 명시한다. 플러그인·계정과 실제 IDE의 지원 조합을 확인해야 한다. VS Code에 적용되는 기능으로 소개하지 않는다.

## 왜 중요한가
{:.briefing-heading}

**분석:** 오류에서 수정 요청까지의 경로가 짧아져도, 제안된 변경이 정확한지는 검사해야 한다. 한 오류를 고치는 과정에서 주변 동작이 달라지는지도 검토 범위에 넣는다.

### 구체적인 작업 예시 — 작은 컴파일 오류

**설명용 예시:** 가상 시험 코드에서 잘못된 변수 이름으로 생긴 오류를 준비한다. 오류 위치에서 수정을 요청하고 변경된 파일과 수정 범위를 읽는다. 기대 결과는 변수 이름의 일관성 회복과 컴파일 성공이며, 관련 없는 기능을 삭제하면 실패다.

이후 해당 함수의 작은 동작 검사도 실행한다. IDE에서 빨간 표시가 사라졌다는 사실만으로 런타임 동작까지 확인됐다고 기록하지 않는다. 연결 도구가 필요 없는 과제라면 어떤 서버가 시작되는지도 별도로 확인할 수 있다.

### 어떤 개발자에게 관련 있나 · 지금 도입할 만한가

**필자의 판단:** 지원되는 JetBrains IDE에서 Copilot을 이미 쓰는 작업자에게 관련 있다. 기존 환경의 진단 흐름을 시험할 만하며, 이 기능 하나 때문에 IDE나 유료 서비스를 바꿀 필요는 없다.

## 개발에 적용할 점
{:.briefing-heading}

- 현재 IDE·플러그인·계정의 지원 조합을 먼저 확인한다.

- 작은 오류에서 제안 diff와 컴파일·동작 검사를 순서대로 확인한다.

- MCP 자동 시작 제어와 각 도구의 접근 권한을 별도로 검토한다.

## 원문과 확인 자료
{:.briefing-heading}

- [GitHub의 JetBrains 플러그인 공식 변경 기록](https://github.blog/changelog/2026-10-10-new-controls-and-chat-improvements-in-copilot-for-jetbrains/) — 2026-10-10.

**확인 범위:** 2026-10-12 원문을 확인했다. 공식 변경 기록의 출시일·Fix 모드·MCP 제어·지원 IDE 조건을 확인했다. 플러그인 설치·진단 수정·컴파일·서버 설정 변경은 수행하지 않았다.
