# 게임 개발 브리핑 두 번째 테스트

기준 샘플: `_posts/2026-10-11-machinarium-2-briefing.md`. 제목, 리드, 초록색 섹션 제목, 구체적 소제목, 분석, 실행 제안, 출처와 확인 범위를 따른다. 새 글에는 개인 프로젝트나 사적 정보가 없다.

## 기사 검증 (2026-10-11)

| 유형 | 채택 자료 | 날짜와 확인 상태 | 사용하지 않은 내용 |
| --- | --- | --- | --- |
| 장기 개발 회고 | [Nocturne 개발자 인터뷰, 80 Level](https://80.lv/articles/this-rhythm-rpg-was-rebuilt-three-times-during-its-10-year-development) | 게시 2026-10-09. 당사자의 10년·세 차례 재제작·도구 설명. [개발사 블로그](https://pracystudios.com/blog)의 2026-09-22 출시 발표와 개발 기간 교차 확인 | 리뷰 비율, 분량, 입력 주파수 등 미측정 수치 |
| 개발 도구 | [RizomUV 공식 기능 발표](https://www.rizomuv.com/feature/rizomuv-2027-release-features/) | 제공 시작 2026-10-08. 페이지 게시일은 별도 표시되지 않음. 기능은 제조사 설명 | 성능 향상 배율, 가격, 실사용 효과 |
| 소규모 팀 아트 | [Silver Pines 개발자 인터뷰, 80 Level](https://80.lv/articles/how-silver-pines-used-rotoscoping-to-create-its-unsettling-horror) | 게시 2026-10-08. 레벨 제작 2명과 주인공 1,800장 초과는 당사자 설명. 스튜디오 전체 인원과 구분 | 출시·매출·공포감에 대한 단정 |
| 업계 이슈 | [Heart Machine 공식 CWA 발표](https://cwa-union.org/news/releases/video-game-developers-heart-machine-secure-voluntary-union-recognition-cwa) | 게시 2026-03-09. 2월 요청, 자발적 인정. 인정 일자·정확한 찬성률·인원은 미제시 | 계약 체결·개선 성과·최신 계약 상태 |

Double Fine 후보는 교체했다. [NLRB 사건 20-RC-386546](https://www.nlrb.gov/case/20-RC-386546)에는 2026-05-07 접수, 42명, 2026-05-20 신청 철회 및 승인, 현재 Closed가 표시된다. 원래 제안한 ‘노조 결성’을 현재 완료 사실로 사용할 수 없으므로 동일 유형의 공식 인정 발표를 선택했다. 이 기록만으로 철회 이유나 이후 모든 활동을 추정하지 않는다.

## 이미지

네 글 모두 대표 이미지와 대체 텍스트·출처 캡션을 추가했다. 처음에는 이미지를 생략했으나 공식 보도 자료와 별도 브랜드 지침을 확인해 보완했다.

- Silver Pines: [Team17 Press Kit Archive](https://www.team17.com/press-kit-archive)가 보도용으로 제공하는 [2026 프레스킷](https://www.team17.com/hubfs/Press%20Kits/Silver%20Pines%20Press%20Kit%202026.zip)의 `Screenshots/Screen 7.jpg`. 원본 그대로 사용. 권리자는 Wych Elm / Team17 등 해당 권리자이며 블로그의 일반 본문 라이선스가 이 이미지까지 확장되지 않는다.
- RizomUV: [공식 브랜드 지침](https://www.rizomuv.com/writing-and-branding-guidelines/)이 정지 이미지의 로고 사용을 허용. 제공된 `RizomUV-Rectangle-Dark-2.png`를 변경 없이 사용하고 제휴·후원을 암시하지 않는다. 로고 권리는 Rizom-Lab에 남는다.
- Nocturne: 공식 프레스킷의 이미지 폴더에 현재 파일이 표시되지 않아 자체 제작 설명도를 사용. 게임 스크린샷·공식 아트가 아님을 명시.
- Heart Machine: 인정과 첫 계약의 단계를 구분하는 자체 제작 설명도. 실제 직원 사진·공식 홍보물이 아님을 명시하고 계약 상태는 미확인으로 표시.

[80 Level 정책](https://80.lv/republishing-policy)의 이미지 허가 제한과 개발사·배급사 자료의 이용 조건은 별개로 평가했다. 네 대표 자산은 저장소의 `assets/img/briefing/`에 저장해 외부 이미지 링크에 의존하지 않는다.

## PR 미리보기

`.github/workflows/pr-preview.yml`은 실제 Jekyll/Chirpy 구성을 production 모드로 빌드하고 htmlproofer로 내부 링크를 확인한다. 미리보기에서만 URL을 상대 경로로 만들고 PWA·댓글을 끈다. 운영 구성, 기존 Pages 워크플로 및 정기 자동화는 수정하지 않는다.

동일 저장소 PR에만 빌드 산출물을 임시 HTTP 서버로 제공하고 Cloudflare Quick Tunnel로 공개한다. 서버의 루트는 `_site` 산출물뿐이다. 저장소 원본·Git 정보·토큰을 제공하지 않는다. 외부 접근 가능한 공개 주소이며 접근 인증은 없다. [Cloudflare 공식 설명](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)처럼 프로세스 종료 시 URL이 만료된다.

홈·네 글·CSS의 외부 HTTP 확인을 통과한 뒤 PR 댓글에 주소를 쓴다. 이후 약 45분간 유지한다. 빌드 작업은 먼저 성공 완료하고, 미리보기 작업은 공개 서버를 유지하는 동안 실행 중으로 보인다. **Re-run all jobs** 또는 PR 새 커밋으로 재시작하면 새 주소를 댓글에 갱신한다. 동시 실행은 PR마다 하나이며 이전 주소는 종료된다. PR 종료만으로 즉시 종료되는 것은 아니고 남은 유지 시간까지 살아 있을 수 있다. 실패한 실행에서는 댓글의 이전 주소가 유효하다고 가정하지 말고 현재 실행 결과를 확인한다.

산출물은 Actions artifact로 7일간 보관된다. 만료 후 다운로드해 로컬 HTTP 서버로 볼 수 있다. 외부 링크 검사와 시각 검토는 빌드 성공과 별도로 기록한다. 이 구성은 운영 Pages 배포 권한을 요청하지 않는다.
