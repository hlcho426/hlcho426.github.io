"""Synthetic offline input: never news, never eligible for publication."""
def fixture(kind, today):
    evidence = "This synthetic test document describes an offline pipeline validation."
    paragraph = "이 문단은 자동화 기능을 시험하기 위한 합성 자료의 설명이다. 실제 제품 발표나 연구 결과가 아니다. 원문 수집 이후 근거 구절을 검사하고 독립 게시물을 만드는 경로를 확인한다. 수동 테스트에서는 유료 API와 공개 게시물 발행을 실행하지 않는다."
    headers = ["시험 자료의 질문", "시험 자료의 방법", "시험 자료의 발견", "시험 자료의 한계"]
    article = {"publishable": True, "reason": "Synthetic offline test only",
               "title": "합성 자료로 확인하는 브리핑 생성 경로의 수동 테스트",
               "slug": "synthetic-pipeline-test", "event_key": "synthetic-" + kind,
               "lead": paragraph, "paragraphs": [{"heading": h, "text": paragraph, "evidence": evidence}
                                                  for h in headers],
               "importance": "합성 자료를 이용한 기능 검사는 실제 기사 품질과 구분해야 한다. " + paragraph * 2,
               "applications": ["시험 출력의 카테고리와 시간대를 읽어 보고 파일 이름과 구조가 규칙에 맞는지 확인한다.",
                                "근거 구절을 바꾼 실패 자료를 입력하고 게시물 생성이 차단되는지 확인한다."],
               "scope": paragraph, "source_date": today.isoformat(), "date_evidence": today.isoformat(),
               "research_full_text": True, "ai_conditions": paragraph, "ai_limits": paragraph}
    source = {"url": f"https://example.org/synthetic-{kind}", "title": "합성 시험 원문 (실제 기사 아님)",
              "text": today.isoformat() + "\n" + (evidence + "\n") * 100,
              "document_date": today.isoformat(), "truncated": False, "sha256": "synthetic"}
    return {"url": source["url"], "title": source["title"], "event_key": article["event_key"],
            "source": source, "article": article}
