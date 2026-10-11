---
title: "유니티 C# 기초 Day 0: 유니티 설치하고 첫 스크립트 붙이기"
date: 2026-10-11 22:08:00 +0900
description: "Unity Hub로 Unity 6를 설치하고 프로젝트를 만든 뒤, 큐브에 첫 C# 스크립트를 붙여 콘솔에 글자를 띄우기까지. 비전공자를 위한 유니티 첫걸음."
series: 유니티 C# 일주일
series_title: "기초 Day 0: 유니티 설치와 첫 스크립트"
categories: [유니티 공부]
tags: [유니티, C#, 유니티 설치, 유니티 입문, 유니티 C# 일주일]
---

{% include series.html %}

앱의 기초 코스는 바로 코드 읽기부터 시작한다. 그런데 그 코드를 어디에 쓰고, 어떻게 실행하는지는 앱에 없다. 그래서 Day 0을 따로 만들었다.

이번 글의 목표는 하나다. **유니티 콘솔 창에 내가 쓴 글자 한 줄 띄우기.** 여기까지 되면 앞으로 나오는 모든 예제를 직접 돌려 볼 수 있다.

## 1. Unity Hub와 에디터 설치

유니티는 두 단계로 설치한다.

- **Unity Hub**: 유니티 버전과 프로젝트를 관리하는 런처. [unity.com/download](https://unity.com/download)에서 받는다.
- **Unity Editor**: 실제로 게임을 만드는 프로그램. Hub 안에서 설치한다.

순서는 이렇다.

1. Unity Hub를 설치하고 실행한 뒤 Unity 계정으로 로그인한다. 처음이면 계정을 만든다.
2. 라이선스를 고르라고 하면 개인용 무료 라이선스(Personal)를 받는다.
3. 왼쪽 **Installs** → **Install Editor**에서 **LTS** 표시가 붙은 Unity 6 버전을 고른다. LTS(Long Term Support)는 오래 지원하는 안정 버전이라는 뜻이다. 처음 배울 때는 LTS가 제일 무난하다.
4. 모듈 선택 화면에서 Windows라면 **Microsoft Visual Studio Community**를 체크한다. C# 코드를 쓰는 편집기다. 이미 Visual Studio나 다른 편집기가 있으면 건너뛰어도 된다. 빌드 모듈(Android, iOS 등)은 나중에 추가해도 된다.

> 이 시리즈의 코드는 **Unity 6** 기준이다. 옛 버전과 달라지는 부분은 그때그때 따로 적는다.
{: .prompt-info }

## 2. 새 프로젝트 만들기

Hub의 **Projects** → **New project**에서 템플릿을 고른다. 3D 템플릿이면 아무거나 괜찮다. 여기서는 **Universal 3D**를 쓴다. 프로젝트 이름과 저장 위치를 정하고 **Create project**를 누르면 몇 분 뒤 에디터가 열린다.

## 3. 에디터 화면 읽기

처음 열면 창이 여러 개라 복잡해 보이지만, 지금 알아야 할 건 여섯 개다.

| 창 | 하는 일 |
|---|---|
| **Hierarchy** | 지금 씬에 있는 오브젝트 목록 |
| **Scene** | 오브젝트를 배치하는 작업 화면 |
| **Game** | 플레이어가 실제로 보게 될 화면 |
| **Inspector** | 고른 오브젝트의 정보와 컴포넌트 |
| **Project** | 프로젝트 파일(에셋) 목록. 스크립트도 여기 있다 |
| **Console** | 로그와 에러가 뜨는 곳 |

Console 창이 안 보이면 메뉴 **Window → General → Console**로 연다. 앞으로 제일 자주 볼 창이다.

## 4. 큐브 하나 만들기

Hierarchy 빈 곳을 우클릭하고 **3D Object → Cube**를 고른다. Scene 화면에 큐브가 생기고, Inspector에 `Transform`, `Mesh Filter`, `Mesh Renderer`, `Box Collider` 같은 칸이 보인다.

이 칸 하나하나가 **컴포넌트**다. 유니티의 오브젝트는 컴포넌트를 조립해서 만든다. 위치는 Transform이, 모양은 Mesh Filter가, 충돌은 Collider가 맡는다. 우리가 만드는 스크립트도 이렇게 붙는 컴포넌트 중 하나가 된다.

## 5. 스크립트 만들기

Project 창의 **Assets** 폴더를 우클릭하고 **Create → Scripting → MonoBehaviour Script**를 고른다. 유니티 버전에 따라 메뉴 이름이 **C# Script**로 보이기도 한다.

파일 이름을 `Player`로 바꾸고 엔터를 친다. 이 이름이 중요하다. 유니티는 **파일 이름과 스크립트 안의 클래스 이름이 같아야** 스크립트를 오브젝트에 붙일 수 있다. 파일을 만들 때 정한 이름이 클래스 이름으로 들어가니까, 처음에 제대로 지어 두는 게 편하다.

> 나중에 파일 이름만 바꾸면 클래스 이름은 그대로라서 둘이 어긋난다. 이름을 바꿀 때는 파일과 코드 속 `class` 이름을 같이 바꾼다.
{: .prompt-warning }

## 6. 큐브에 붙이기

Project 창의 `Player` 스크립트를 Hierarchy의 Cube 위로 끌어다 놓는다. Cube를 클릭해 보면 Inspector 맨 아래에 **Player (Script)** 칸이 생겨 있다. 이제 이 스크립트는 큐브의 컴포넌트다.

Inspector의 **Add Component** 버튼을 누르고 `Player`를 검색해서 붙여도 된다.

## 7. 코드 한 줄 쓰기

`Player` 스크립트를 더블클릭하면 코드 편집기(Visual Studio 등)가 열린다. 이런 코드가 들어 있다. 버전에 따라 주석 몇 줄이 더 있을 수 있다.

```csharp
using UnityEngine;

public class Player : MonoBehaviour
{
    void Start()
    {

    }

    void Update()
    {

    }
}
```

`Start` 안에 한 줄을 넣는다.

```csharp
void Start()
{
    Debug.Log("안녕, 유니티!");
}
```

**Ctrl + S**(맥은 Cmd + S)로 저장하고 유니티로 돌아온다. 오른쪽 아래에서 잠깐 무언가 돌아가는데, 유니티가 코드를 읽어 들이는(컴파일하는) 중이다.

> 더블클릭해도 편집기가 안 열리면 **Edit → Preferences → External Tools**의 External Script Editor에서 설치한 편집기를 고른다.
{: .prompt-tip }

## 8. 실행

에디터 위쪽 가운데의 ▶ 버튼을 누른다. Console 창에 이 줄이 뜨면 성공이다.

```
안녕, 유니티!
```

한 번 더 ▶을 누르면 플레이가 멈춘다.

이번엔 같은 줄을 `Start`가 아니라 `Update` 안에 넣고 실행해 보자. Console이 순식간에 같은 글자로 가득 찬다. `Start`는 시작할 때 한 번, `Update`는 매 프레임 실행되기 때문이다. 이 차이가 [기초 Day 1](/posts/csharp-week-basic-day1/)의 첫 내용이다. Console 위쪽의 **Collapse**를 켜면 같은 줄을 하나로 묶고 몇 번 찍혔는지 숫자로 보여 준다.

> **플레이 중에 Inspector에서 바꾼 값은 플레이를 멈추면 원래대로 돌아간다.** 실험하기엔 좋지만, 마음에 드는 값을 찾았다면 멈추기 전에 적어 두자.
{: .prompt-warning }

## 에러가 났다면

Console에 빨간 줄이 뜨면 코드에 문제가 있다는 뜻이다. 빨간 줄을 더블클릭하면 편집기에서 그 줄로 바로 간다. 처음에 자주 만나는 건 이 세 가지다.

- `; expected`: 문장 끝에 세미콜론 `;`이 빠졌다.
- 스크립트를 붙이려는데 "script class cannot be found" 비슷한 경고: 파일 이름과 클래스 이름이 다르거나, 코드에 에러가 있어서 아직 컴파일이 안 됐다.
- 아무 일도 안 일어남: 스크립트를 오브젝트에 안 붙였거나, 붙인 오브젝트가 씬에 없다.

빨간 에러가 하나라도 있으면 ▶ 버튼을 눌러도 플레이가 시작되지 않는다. 에러부터 고친다.

## 미리 해 두면 좋은 설정: 입력 방식

기초 Day 6에서 키보드 입력을 받을 때 `Input.GetKeyDown` 같은 코드를 쓴다. 그런데 Unity 6의 새 프로젝트는 **새 Input System만 켜져 있는 경우**가 있다. 그러면 이 코드를 실행할 때 `InvalidOperationException` 에러가 난다.

미리 둘 다 쓸 수 있게 바꿔 두자.

1. **Edit → Project Settings → Player**를 연다.
2. **Other Settings → Configuration**의 **Active Input Handling**을 **Both**로 바꾼다.
3. 에디터를 다시 시작하라고 하면 다시 시작한다.

새 Input System은 실전 Day 6에서 따로 배운다. 그 전까지는 배우기 쉬운 기존 방식으로 연습한다.

## 현업에서는

- **유니티 버전을 함부로 바꾸지 않는다.** 프로젝트는 만들 때의 버전으로 연다. 같이 작업하는 사람이 있으면 모두 같은 버전을 쓴다. Hub에 버전을 여러 개 깔아 두고 프로젝트마다 고를 수 있다.
- **스크립트는 폴더를 정해서 모은다.** `Assets/Scripts`처럼 폴더를 만들어 두면 나중에 찾기 쉽다.
- **처음부터 Git 같은 버전 관리를 쓴다.** 실수로 망가뜨려도 어제 상태로 되돌릴 수 있다. 유니티 프로젝트용 `.gitignore`를 같이 쓰면 `Library` 폴더 같은 큰 임시 파일은 빼고 저장한다.

## 정리

- Unity Hub로 에디터(Unity 6 LTS)를 설치하고 프로젝트를 만든다.
- 스크립트는 오브젝트에 **컴포넌트로 붙여야** 실행된다.
- 파일 이름 = 클래스 이름.
- `Debug.Log("...")`로 Console에 글자를 찍어서 코드가 도는지 확인한다.
- 플레이 중에 바꾼 값은 멈추면 사라진다.

다음 글 [기초 Day 1](/posts/csharp-week-basic-day1/)에서는 방금 본 스크립트를 한 줄씩 읽고, 변수를 배운다.
