---
title: Mituhashi Glass Crafts, 유리를 깎는 체험을 작품 저장과 전시로 잇는다
description: 가상 공간에서 만든 물건을 그 공간 밖에서도 간직할 수 있다면 제작 경험은 어떻게 달라질까? 10월 20일 소개된 Mituhashi
  Glass Crafts는 VRChat의 유리 공예 체험을 작품 저장과 전시로 연결한다.
date: 2026-10-22 12:16:41 +0900
categories:
- 레퍼런스 조사
- 업계 뉴스
tags:
- 업계 뉴스
briefing_type: game
briefing_event: mituhashi-glass-crafts-vrchat-making-sharing-20261020
briefing_sources:
- https://80.lv/articles/taking-a-real-life-hobby-into-digital-spaces-mituhashi-made-a-vrchat-glass-cutting-experience
---

*이 글은 공개 원문을 바탕으로 Codex가 조사하고 정리했습니다.*

가상 공간에서 만든 물건을 그 공간 밖에서도 간직할 수 있다면 제작 경험은 어떻게 달라질까? 10월 20일 소개된 Mituhashi Glass Crafts는 VRChat의 유리 공예 체험을 작품 저장과 전시로 연결한다.

## 무슨 일이 있었나
{:.briefing-heading}

### 깎은 자리가 문양으로 드러나는 조작

80 Level은 Mituhashi Glass Crafts를 일본의 유리 공예인 에도 기리코를 체험하는 VRChat 월드로 소개했다. 회전하는 절삭 도구로 판유리뿐 아니라 꽃병이나 와인잔 같은 입체 형태를 깎고, 색유리를 깎은 부분은 투명해진다고 설명한다. 이는 공개 소개의 설명이며 실제 절삭감이나 표현의 정확성을 직접 확인한 결과는 아니다.

### 형태 선택과 보조 기능을 함께 제공한다

소개 글에 따르면 이용자는 유리 형태를 고르고 절삭 각도와 깊이를 조정하며, 절삭 보조와 가이드를 켤 수 있다. 결과물의 모양을 고르는 일과 손으로 깎는 일을 연결하되, 정밀한 작업을 돕는 기능도 둔 구성이다. 보조 기능이 실제로 초보자의 실패를 얼마나 줄이는지는 공개 글에 측정 결과가 없다.

### 체험이 끝나도 작품을 가져갈 수 있다

완성한 작품은 코드로 저장하고 공유할 수 있으며, Unity용 기리코 생성기로 가져와 3D 오브젝트로 내보낸 뒤 자신의 월드에 전시할 수 있다고 소개한다. 제작자가 배포하는 BOOTH 설명에서도 작품 코드를 붙여 문양과 색을 복원하고 배치용 Prefab을 만드는 흐름을 확인했다. 여기서 Prefab은 장면에 다시 배치할 수 있게 묶은 오브젝트다. 실제 복원과 내보내기는 실행하지 않았다.

## 왜 중요한가
{:.briefing-heading}

**분석:** 편집자의 해석으로는 이 사례의 핵심은 공예 조작의 재현뿐 아니라 만든 것을 남기는 흐름에 있다. 절삭 보조가 작업의 진입을 돕고 저장·전시가 결과물을 다시 보거나 다른 사람에게 보여 줄 이유를 제공할 수 있다. 다만 보조 기능의 학습 효과나 작품 보존이 재방문에 미치는 영향은 이번 자료로 입증되지 않는다. 다음 항목은 비슷한 제작 체험을 설계할 때 비교해 볼 실험 제안이며 실제로 수행하지 않았다.

## 개발에 적용할 점
{:.briefing-heading}

- 같은 짧은 문양 과제를 보조 기능을 켠 조건과 끈 조건으로 나눠 본다. 완료 여부뿐 아니라 이용자가 도구와 유리의 접촉 위치를 설명하는지 관찰해 조작 이해와 보조 의존을 구분한다.

- 체험 종료 화면에 작품만 보여 주는 안과 저장 코드를 함께 제공하는 안을 비교한다. 처음 온 이용자가 설명 없이 저장하고 다시 불러올 수 있는지 확인하고 실패한 단계를 기록한다.

- 작품을 전시할 때 제작 당시의 색과 형태를 알아볼 수 있는지 확인한다. 다른 조명에서 결과가 달라 보이면 저장 실패로 오해하는지 관찰하고 미리보기와 안내를 조정한다.

## 원문과 확인 자료
{:.briefing-heading}

- [Taking a Real-Life Hobby into Digital Spaces: Mituhashi Made a VRChat Glass Cutting Experience](<https://80.lv/articles/taking-a-real-life-hobby-into-digital-spaces-mituhashi-made-a-vrchat-glass-cutting-experience>) — **2026-10-20**, 원문 본문 확인.

**확인 범위:** 2026-10-22 원문을 수집했다. 80 Level의 2026년 10월 20일 소개 본문 전체와 제작자의 BOOTH 상품 번호 9005992 배포 설명을 웹으로 읽었다. 정확한 월드 최초 공개일은 확인하지 못해 10월 20일을 소개 글의 발행일로만 사용했다. BOOTH는 Unity 2022.3과 PC판 VRChat 조건, Quest·URP·HDRP 미지원, 생성 작품 판매 금지와 코드 공유 가능을 안내한다. 다운로드·설치·VRChat 접속·절삭·저장 복원·성능 측정은 하지 않았다. CLI 수집은 DNS 오류로 실패해 실제 읽은 발췌만 보존했으며 원본 해시는 없다. VRChat 월드 상세 본문은 접근하지 못했다. 관련 공식 YouTube 영상을 확인하지 못해 임베드를 생략했고 이미지도 생략했다.
