# Codex 로컬 정기 브리핑 운영

## 비용과 실행 조건

GitHub Actions의 OpenAI API 생성 경로를 제거했다. 별도 모델 API 호출, `OPENAI_API_KEY`, `BRIEFING_GITHUB_TOKEN`, 유료 검색 키가 필요 없다. 이전 월 $40~80 API 예산은 이 설계에 적용되지 않는다. ChatGPT로 로그인한 Codex가 구독 사용량 안에서 조사·작성하고 이미 연결한 GitHub 도구로 PR을 제출한다. 사용량 한도에 도달하면 작업이 지연·중단될 수 있다. 추가 크레딧을 구매하거나 API 키 인증으로 전환하지 않는다.

PC 전원·인터넷·Codex 앱 실행·ChatGPT 로그인이 필요하다. 실행 시간에는 절전·최대 절전에 들어가지 않게 한다. 놓친 실행의 자동 보충을 보장하지 않는다. [OpenAI 공식 안내](https://learn.chatgpt.com/docs/automations?surface=app)를 참고한다. GitHub Actions 빌드와 45분 미리보기의 러너 사용량은 별개이며 GitHub 요금제·Billing에서 확인한다.

기존 ChatGPT 정기 브리핑 세 개는 변경하거나 GitHub에 자동 연결하지 않는다. 저장소별 Codex 예약 세 개를 새로 등록한다. 원래 요청한 수동 시험·활성화 승인 조건에 따라 초기 상태는 **일시정지**다. 구현 PR을 검토·병합하고 수동 실행을 확인한 뒤 사용자 승인으로 활성화한다. 모델 API Secrets를 등록할 필요가 없다.

## 아키텍처

1. Codex 예약이 현재 원격 main의 README·AGENTS·편집 지침·작업 절차와 공개 기준 글을 읽는다. 같은 유형의 미병합 PR 또는 같은 날짜의 기존 PR이 있으면 새 작업을 건너뛴다.
2. 내장 웹 검색으로 원문을 찾고 본문을 확인한다. 일간은 최근 48시간 우선/7일 이내, 연구는 1년 이내 공개 전문을 중심으로 2~3편을 권장한다. 적격 자료가 적으면 줄인다.
3. `collect.py`가 공개 HTML/PDF 본문·해시·날짜를 `output/briefing/{kind}/{date}/sources/`에 수집한다. 사설 주소·접근 차단·초록만의 연구·미확인 날짜는 제외한다. 원문 전체를 공개 저장소에 커밋하지 않는다.
4. Codex가 원문을 읽어 ARTICLE_SCHEMA에 맞는 JSON을 작성하고 사실·분석을 다시 대조한다. `run.py --mode codex --input ...`는 모델을 호출하지 않고 근거·날짜·중복·구조를 검사하여 Markdown을 생성한다.
5. 게시물 제목에는 내용만 쓰고 카테고리 접두어를 붙이지 않는다. `briefing_sources`, `briefing_event`는 중복 검사 기록이다. 이미지 권리 검증 자동화가 없으므로 이미지를 생략한다.
6. 연결된 GitHub 도구로 최신 main에서 전용 브랜치를 만들고 `_posts` 파일만 커밋한다. 로컬 브랜치·사용자 파일·인덱스를 변경하지 않는다. 유형별 draft PR 하나를 생성해 기존 Actions 빌드·검사·미리보기를 실행한다. 검사 통과 후 ready for review로 전환한다. main 직접 push와 자동 병합은 하지 않는다.
7. 결과에 PR·검사·미리보기·확인 한계를 남기고 현재 예약 실행에 PR artifact를 연결한다. 사용자 병합 후 기존 Pages가 배포한다.

유형별 시작을 분산하고 원격 파일만 변경해 로컬 경쟁을 줄인다. 제출 직전 모든 열린 PR을 다시 검사한다. 출처가 다른 같은 사건은 제목·본문도 비교한다. 구절 포함 검사나 Codex 재검토는 진실성·실험 재현을 보장하지 않으므로 사용자 검토가 필요하다.

## 일정 (KST)

| 종류 | 시작 | 결과 |
|---|---|---|
| 게임 개발 데일리 | 매일 07:55 | 최대 5편, 하루 PR 1개 |
| AI 툴 데일리 | 매일 08:05 | 최대 5편, 하루 PR 1개 |
| 주간 게임 연구 | 금요일 07:45 | 권장 2~3편, 금요일 PR 1개 |

작성·검사에는 시간이 필요하므로 제출은 시작보다 늦다. Codex 앱의 Scheduled/자동화 메뉴에서 상태와 일정을 관리한다. 각 예약은 지정 유형으로 `CODEX_RUNBOOK.md`를 실행하도록 한다.

## 무료 수동 시험

```sh
python -m pip install -r tools/briefing/requirements.txt
python -m unittest discover -s tools/briefing -p 'test_*.py' -v
python tools/briefing/run.py --kind game --mode fixture --output output/briefing/test-game
python tools/briefing/run.py --kind ai --mode fixture --output output/briefing/test-ai
python tools/briefing/run.py --kind research --mode fixture --output output/briefing/test-research
python tools/briefing/check.py
```

fixture는 합성 자료이며 운영 글로 제출하지 않는다. CI에서 세 유형의 Chirpy 페이지와 내부 링크를 검사한다. codex 모드 입력은 `[{"source_file":"sources/article.json","article":{...ARTICLE_SCHEMA 필드...}}]`이다. source_file은 해당 output 안에 있어야 한다. 연결된 GitHub 도구의 원격 중복 검사는 항상 필요하며, CLI 권한이 있으면 `--repo hlcho426/hlcho426.github.io`도 쓴다.

구현 PR에서 회귀·합성 통합 시험과 실제 원문 수집·Codex 렌더링을 확인한다. 병합 후 일시정지 예약의 **Run now/지금 실행**으로 실제 조사→draft PR→CI→검토 경로를 먼저 시험한다. 이 시험도 구독 사용량을 소비하지만 모델 API는 호출하지 않는다. 이후 사용자 승인으로 예약을 활성화한다.

## 권한과 실패 확인

연결된 GitHub 도구가 저장소·파일·브랜치·PR을 읽고 생성할 수 있어야 한다. gh 로그인도 확인했으나 CLI 네트워크·Git 쓰기는 샌드박스 권한에 따라 무인 실행에서 차단될 수 있어 연결 도구를 우선한다. 직접 GET·Python 설치가 막히면 허용된 웹·브라우저 도구로 본문을 실제 확인한다. 확인할 수 없으면 제출하지 않는다. 추가 권한·연결이 필요하면 구체적인 조치를 실행 결과에 남긴다. 샌드박스 우회나 무제한 권한 부여는 하지 않는다.

Scheduled에서 완료·실패·필수 사용자 조치를 확인한다. 로컬 report.json은 생성·제외·오류와 모델 API 호출 0건을 기록한다. 원문·초안 캐시는 공개 PR에 포함하지 않는다. GitHub 검사 실패는 PR Checks와 Actions 로그에서 확인한다. 미리보기 댓글의 공개 주소는 약 45분 유지되며 Actions 재실행으로 갱신된다.

원문 접근·중복 검사 불가, 전 후보 거절, CI 실패를 성공으로 보고하지 않는다. 후보 0개이면 PR을 만들지 않는다. 같은 미병합 PR 때문에 건너뛴 경우 실행 기록에만 남기고 반복 알림을 하지 않는다. 새 PR·새 실패·필수 사용자 조치가 있을 때 알린다.
