# GitHub 정기 브리핑 운영

## 현재 상태

최소 버전은 GitHub Actions에서 실행한다. 기존 ChatGPT 정기 브리핑 세 개와 연결하지 않으며 변경하지 않는다. 예약 트리거는 있지만 `BRIEFING_SCHEDULE_ENABLED`와 `BRIEFING_PAID_ENABLED`가 모두 정확히 `true`일 때만 유료 예약 작업을 수행한다. 기본은 둘 다 미설정으로 비활성이다. main 직접 push와 자동 병합은 구현하지 않았다.

초기 구현 PR을 검토·병합해야 기본 브랜치의 예약 및 workflow_dispatch 메뉴에 등록된다. 병합은 예약 활성화나 유료 API 사용 승인이 아니다. 초기 PR에서 무료 합성 자료 수동 시험을 먼저 진행한다. 합성 게시물은 Actions 작업 공간과 artifact에만 있으며 운영 글로 커밋할 수 없다.

## 아키텍처

1. 공개 게시물과 모든 열린 PR의 출처 URL·사건 식별자를 읽는다. 같은 유형의 미병합 PR이 있으면 API 사용 전에 종료한다. 같은 날짜의 닫힌/병합된 PR도 재생성하지 않는다.
2. OpenAI Responses API `web_search`로 유형별 공개 원문 후보를 찾는다. 일간은 최근 48시간 우선, 최대 7일 이내 자료만 허용한다. 주간은 1년 이내 연구를 대상으로 2~3편을 권장한다. 적격 자료가 적으면 줄이고 0편이면 PR을 만들지 않는다.
3. Python이 후보 URL을 직접 GET한다. HTML 본문은 trafilatura, PDF는 pypdf로 추출한다. 사설 주소·접근 인증·캡차·짧은 본문·미지원 형식·3MB 초과 파일은 제외한다. 리디렉션도 공개 주소인지 검사한다. 유료 원문·JS 전용 페이지를 우회하지 않는다.
4. 공개 편집 지침과 기존 공개 글을 입력하여 JSON Schema로 한 편씩 작성한다. 날짜와 원문 근거 구절을 기계 검사하고 별도 모델 검토로 근거 없는 주장·발표와 실증의 혼동·기존 사건 재보도를 걸러낸다. 검색 결과의 문장만으로 글을 완성하지 않는다.
5. 날짜·영문 slug·현재 README 카테고리·KST·필수 구성·템플릿 삽입·비공개 경로 표식을 검사한다. 제목 유형과 확인 범위를 넣고 기존 `briefing-heading` 스타일을 사용한다. 최소 버전은 이미지의 이용 허가를 자동 검증하지 않으므로 이미지를 생략한다.
6. 직접 출처 링크를 다시 GET하고 Jekyll·Chirpy 빌드, htmlproofer 내부 링크 및 생성 페이지를 검사한다. 통과한 파일만 `codex/briefing-{kind}-{KST 날짜}` 브랜치에 커밋하고 유형별 PR 한 개를 만든다. 사용자 병합 후 기존 Pages 배포가 실행된다.
7. 기존 PR Preview가 실제 Chirpy 렌더링과 생성 글 경로를 검사하여 약 45분짜리 임시 공개 주소를 댓글로 제공한다. artifact는 7일 보관한다. 미리보기는 공개 주소이므로 검토 중인 글도 외부에서 접근 가능하다.

URL 중복은 추적 파라미터·www·fragment 및 arXiv PDF/초록/버전을 정규화한다. `briefing_sources`, `briefing_event`는 병합된 글의 지속 기록이다. 과거 다섯 글도 본문의 URL로 검색하고 제목을 모델 검토에 제공한다. 사건 이름이 다르게 생성되는 의미상 중복은 모델 검토와 최종 사용자 리뷰가 필요하다. 근거 구절 포함과 모델 재검토는 진실성·이미지 권리·실험 재현을 보장하지 않는다. 원문을 직접 사용하는 품질 시험은 유료 API 사용 승인 후 진행해야 한다.

## 필요한 API와 대안

선택한 MVP는 **OpenAI API 키 한 개**로 검색과 작성·검토를 수행한다. ChatGPT 구독과 API 요금은 별개이며 키를 채팅·코드·PR에 붙이지 않는다. 별도 검색 서비스 키는 필요 없다. HTML/PDF 수집과 Jekyll 검사는 별도 유료 API 없이 실행한다.

다른 방법은 무료 RSS/arXiv 검색으로 후보를 수집하고 LLM만 유료 호출하는 것이다. 검색 요금은 줄지만 출처 목록 관리와 새 도구 포착에 제약이 있다. Tavily 같은 별도 검색 API도 도입할 수 있으나 키와 별도 요금제가 필요하여 이 버전에서는 사용하지 않는다. 모델 변경은 `BRIEFING_MODEL` 변수로 가능하나 Responses·web_search·Structured Outputs 지원을 먼저 확인하고 수동 테스트한다.

2026-10-11 확인한 [공식 가격표](https://developers.openai.com/api/docs/pricing)에서 기본 `gpt-6.1-sol`의 표준 짧은 문맥 가격은 입력 $2/백만 토큰, 출력 $10/백만 토큰이며 web_search는 $10/1,000회 + 검색 내용 토큰이다. [검색 API](https://developers.openai.com/api/docs/guides/tools-web-search)와 [구조화 출력](https://developers.openai.com/api/docs/guides/structured-outputs)을 사용한다. 가격은 이후 변경될 수 있다.

월 30일, 일간 총 10편/일과 주간 3편×4회를 모두 생성한다고 가정하면 약 312편이다. 글당 작성+검토 합계 입력 30,000토큰/출력 5,000토큰이면 약 $0.11/편 = $34.32다. 여기에 유형별 검색·후보 정리 약 64회×(입력 8,000/출력 2,000토큰)=$2.30, 검색 1~3회/실행=$0.64~1.92, 검색 내용 및 탈락 후보의 토큰 비용이 더해진다. **초기 예산 제안은 월 $40~80**이며 실제 청구 추정이나 상한이 아니다. 연구 전문이 길거나 탈락 후보가 많으면 초과할 수 있다. 검색 호출은 실행당 최대 3회, 후보 최대 8개, 응답 출력 최대 7,000토큰이고 유료 자동 재시도는 하지 않는다. 출력 상한에는 추론 토큰도 포함되므로 부족하면 응답을 거절한다. 매 실행 `report.json`의 모델·입출력·추론 토큰·검색 호출 수를 확인해 예산을 조정한다. OpenAI 프로젝트 사용량/예산 알림도 별도로 설정한다.

GitHub Actions와 45분 미리보기는 별도 러너 사용량이다. 저장소 공개 여부·러너·계정 요금제에 따라 비용이 달라지므로 GitHub Billing에서 확인한다. 모든 PR의 임시 미리보기 대기까지 포함하면 일간 2개+주간 1개가 월 약 64회, 대기 시간만 약 2,880분이다. 이 비용·사용량도 승인 전 검토한다.

## 사용자 설정과 승인 순서

1. 구현 PR의 무료 테스트와 미리보기를 확인하고 원하는 시점에 직접 병합한다.
2. GitHub 저장소 → **Settings → Secrets and variables → Actions → Secrets → New repository secret**에서 `OPENAI_API_KEY`를 등록한다. 코드나 `.env`를 push하지 않는다.
3. **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests**를 허용한다. 워크플로는 contents/pull-requests 쓰기 권한을 PR 제출에만 사용한다.
4. 자동 생성 PR의 미리보기까지 무인 실행하려면 선택적으로 `BRIEFING_GITHUB_TOKEN` secret에 이 저장소만 접근하는 fine-grained PAT를 등록한다. Repository permissions는 Contents: Read and write, Pull requests: Read and write이다. Issues: Read and write는 기존 미리보기의 댓글 쓰기에 사용될 수 있으나 해당 workflow는 자체 GITHUB_TOKEN 권한을 사용한다. Workflow 파일을 수정하는 토큰이 아니므로 Workflows 권한은 필요 없다. 장기 운영에는 GitHub App installation token을 권장한다.
5. PAT 없이 내장 GITHUB_TOKEN도 사용 가능하다. 현재 [GitHub 공식 문서](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)에 따르면 GITHUB_TOKEN으로 생성·갱신한 PR의 `pull_request` 검사에는 **Approve workflows to run** 승인이 필요할 수 있다. 사용자 리뷰 과정에서 승인하면 기존 미리보기·회귀 검사가 시작한다. PAT를 등록하면 PR 생성 이벤트가 승인 대기 없이 검사를 시작할 수 있다. 권한과 조직 정책을 확인한다.
6. **유료 API 사용을 승인한 뒤** Variables 탭에서 `BRIEFING_PAID_ENABLED=true`를 설정한다. `BRIEFING_SCHEDULE_ENABLED`는 아직 설정하지 않는다. Actions → **Briefing generation (manual first) → Run workflow**에서 mode=`live`, kind=`game`/`ai`/`research`를 차례로 시험한다. 테스트 PR의 사실·깊이·링크·미리보기·비용을 검토한다. 같은 유형의 미병합 PR이 남으면 다음 실행은 건너뛴다.
7. **실제 예약 실행을 승인한 뒤에만** `BRIEFING_SCHEDULE_ENABLED=true`를 설정한다. 끄려면 이 변수를 `false`로 변경한다. 유료 호출 전체를 끄려면 `BRIEFING_PAID_ENABLED=false`로 변경한다. 두 변수는 이 구현에서 자동 설정하지 않는다.

## 실행 일정 (KST)

| 종류 | 시작 목표 | 제출 |
|---|---|---|
| 게임 개발 데일리 | 매일 07:55 | 최대 5편, 하루 PR 1개 |
| AI 툴 데일리 | 매일 07:55, 게임 유형과 직렬 처리 | 최대 5편, 하루 PR 1개 |
| 주간 게임 연구 | 금요일 07:50 | 권장 2~3편, 금요일 PR 1개 |

예약식은 UTC 일간 `55 22 * * *`, 주간 `50 22 * * 4`이다. 검색·작성·검사 시간과 직렬 처리 때문에 PR 제출은 08:00 이후일 수 있다. [GitHub 예약 실행](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)은 부하로 지연·누락될 수 있고 기본 브랜치에 있는 workflow만 실행된다. 정각 전달을 보장하지 않는다. 동시 실행은 저장소 단위로 직렬화하여 유형 사이 중복과 동일 PR 생성 경쟁을 줄인다. 공용 저장소의 장기 비활동에 따른 예약 비활성화도 Actions에서 확인한다.

## 수동 검증과 실패 확인

로컬 설치 및 무료 검사:

```sh
python -m pip install -r tools/briefing/requirements.txt
python -m unittest discover -s tools/briefing -p 'test_*.py' -v
python tools/briefing/run.py --kind game --mode fixture --output output/briefing/game
python tools/briefing/run.py --kind ai --mode fixture --output output/briefing/ai
python tools/briefing/run.py --kind research --mode fixture --output output/briefing/research
python tools/briefing/check.py
```

Actions의 `fixture/all` 수동 실행은 세 유형별 합성 게시물 생성, 오프라인 회귀 검사, 메타데이터와 실제 Chirpy 빌드·내부 링크 검사를 한다. 합성 출처의 외부 링크는 실재 기사가 아니므로 검사 대상이 아니다. 별도 `Briefing regression checks`는 구현 PR과 이후 PR에서 실행한다.

각 실행의 Summary와 `briefing-{kind}-{run_id}` artifact(14일)의 `report.json`에 생성 목록, 제외 이유, API 사용량, 오류를 남긴다. 글 원문 전체와 API 키는 저장하지 않는다. 적격 후보를 모두 거절하면 실패로 표시하며 PR은 제출하지 않는다. 검색 결과 자체가 0개이면 정상 종료하고 PR을 만들지 않는다. 네트워크·API·빌드·링크 오류는 Actions 로그에서 확인한다. GitHub 프로필 **Settings → Notifications → System → Actions**에서 실패한 workflow 알림을 켠다. 별도 이메일·Slack 전송은 구현하지 않는다.

branch push 후 PR 생성만 실패하면 같은 날짜 브랜치를 덮어쓰지 않고 오류로 종료한다. Actions의 브랜치와 로그를 확인해 그 브랜치에서 PR을 수동 생성한다. 닫힌 PR의 같은 날짜 재실행도 자동 재제출하지 않는다. 새 기사를 원하면 다음 날짜 실행을 사용하고, 오류 수정은 기존 PR에서 처리한다.

무료 시험의 통과는 실제 API 접근·검색 품질·기사 편집 품질의 검증이 아니다. 사용자 승인 후 세 종류의 live 수동 시험을 완료한 뒤 예약을 활성화해야 한다.
