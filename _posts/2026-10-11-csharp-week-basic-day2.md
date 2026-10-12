---
title: "<유니티 C#> 기초 Day 2: 조건문 if, else와 논리 연산자 (조건에 따라 다르게 움직이기)"
date: 2026-10-11 22:16:00 +0900
description: "if, else, else if와 비교 연산자, &&와 ||로 조건을 묶는 법, =와 ==의 차이까지. 유니티 예제로 배우는 C# 조건문."
series: 유니티 C# 일주일
series_title: "기초 Day 2: 조건문 if"
categories: [유니티 공부]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

[Day 1](/posts/csharp-week-basic-day1/)에서 변수에 값을 담았다.<br>
게임은 그 값을 보고 계속 판단한다.<br>
체력이 0 이하면 게임 오버<br>
코인이 100개 이상이면 구매 성공<br>
땅에 있고 스태미나가 남아 있으면 점프<br>
오늘은 이 "판단"을 코드로 쓰는 **조건문**을 배운다.

**오늘의 목표**

- `if`로 조건이 맞을 때만 코드를 실행할 수 있다
- `=`와 `==`의 차이를 안다
- `else`, `else if`로 갈래를 나눌 수 있다
- `&&`, `||`, `!`로 조건을 묶을 수 있다

## 1. if: 조건이 참일 때만
{:.briefing-heading}

```csharp
int hp = 0;

if (hp <= 0)
{
    Debug.Log("게임 오버");
}
```

`if` 뒤 괄호 안의 조건이 **참(true)**이면 중괄호 안의 코드를 실행하고, **거짓(false)**이면 중괄호를 통째로 건너뛴다.

중괄호 밖의 코드는 조건과 상관없이 항상 실행된다.

```csharp
int hp = 30;
if (hp < 50)
{
    Debug.Log("위험!");
}
Debug.Log("끝");
```

hp가 30이면 "위험!"과 "끝"이 둘 다 찍힌다. hp가 80이면 조건이 거짓이라 "끝"만 찍힌다.

### 비교 기호 여섯 개

| 기호 | 뜻 | 예 |
|---|---|---|
| `==` | 같다 | `coin == 10` |
| `!=` | 다르다 | `state != 0` |
| `>` | 크다 | `score > 90` |
| `<` | 작다 | `hp < 50` |
| `>=` | 크거나 같다 (이상) | `coin >= 100` |
| `<=` | 작거나 같다 (이하) | `hp <= 0` |

"이상", "이하"를 코드로 옮길 때는 `=`가 붙는지 꼭 확인한다. "체력이 0 이하면 죽음"을 `hp < 0`으로 쓰면 체력이 딱 0일 때 안 죽는 버그가 생긴다.

### 비교 결과는 bool이다

`hp <= 0` 같은 비교식은 계산하면 `true` 아니면 `false`가 된다. 그래서 비교 결과를 bool 변수에 바로 담을 수 있다.

```csharp
int hp = 0;
bool isDead = hp <= 0;   // true
```

`if`의 괄호 안에는 **반드시 bool**(true 아니면 false)이 들어가야 한다. 비교식이든 bool 변수든 bool을 돌려주는 함수든, 계산한 결과가 bool이기만 하면 된다. 그래서 bool 변수는 그대로 조건에 넣을 수 있다.

```csharp
if (isDead)          // isDead == true 와 같은 뜻
{
    Debug.Log("게임 오버");
}
```

## 2. `=`와 `==`
{:.briefing-heading}

가장 많이 헷갈리는 부분이다.

- `=`는 **넣기**: `coin = 10;` → coin에 10을 넣어라
- `==`는 **묻기**: `coin == 10` → coin이 10과 같은가?

조건에는 묻는 쪽인 `==`를 쓴다.

```csharp
if (coin == 10)   // O
if (coin = 10)    // X (에러)
```

C#은 친절해서 `if (coin = 10)`처럼 숫자에 `=`를 쓰면 "int를 bool로 바꿀 수 없다"는 에러를 내서 바로 알려 준다. 다만 bool 변수에 `if (isDead = true)`라고 쓰면 에러 없이 경고만 뜨고, isDead에 true를 넣어 버린다. bool은 `== true`를 붙이지 말고 `if (isDead)`처럼 그대로 쓰는 습관을 들이면 이 실수를 아예 피할 수 있다.

## 3. else와 else if: 아니면, 그것도 아니면
{:.briefing-heading}

### else: 아니면

```csharp
if (coin >= 100)
{
    Debug.Log("구매 성공");
}
else
{
    Debug.Log("코인이 부족해요");
}
```

`else`는 바로 앞 `if`의 조건이 거짓일 때 실행된다. 둘 중 **하나는 반드시** 실행되고, 둘 다 실행되는 일은 없다. `else`는 "앞의 if가 거짓이면"이라는 뜻이라 혼자서는 쓸 수 없고 항상 `if` 뒤에 온다.

그리고 `else` 뒤에는 **조건을 쓰지 않는다.** 조건이 "위가 전부 거짓이면"으로 이미 정해져 있어서다. `else (coin < 100)`처럼 쓰면 뜻은 맞아 보여도 에러다. 조건을 꼭 쓰고 싶으면 `else if (coin < 100)`으로 쓰지만, 앞 조건의 정반대라면 그냥 `else`가 더 깔끔하다.

### else if: 여러 갈래

```csharp
if (score >= 90)
{
    Debug.Log("S랭크");
}
else if (score >= 70)
{
    Debug.Log("A랭크");
}
else
{
    Debug.Log("B랭크");
}
```

위에서부터 차례로 검사해서 **처음 맞는 하나만** 실행하고 나머지는 건너뛴다. score가 75면 첫 조건은 거짓, 두 번째 조건이 참이라 "A랭크"만 찍힌다.

그래서 순서가 중요하다.

```csharp
if (score >= 70)
    Debug.Log("A");
else if (score >= 90)
    Debug.Log("S");
```

이렇게 쓰면 95점도 첫 조건(70 이상)에 먼저 걸려서 "A"가 찍힌다. 범위가 겹치는 조건은 **좁은(큰) 조건을 먼저** 쓴다.

> 위 코드처럼 실행할 줄이 하나뿐이면 중괄호를 생략할 수 있다. 하지만 나중에 줄을 하나 더 넣으면 그 줄은 if와 상관없이 항상 실행돼서 버그가 생기기 쉽다. 처음에는 항상 중괄호를 쓰는 걸 추천한다.
{: .prompt-warning }

## 4. 그리고, 또는, 아니다: `&&`, `||`, `!`
{:.briefing-heading}

조건 여러 개를 묶을 때 쓴다.

| 기호 | 읽는 법 | 결과 |
|---|---|---|
| `a && b` | a **그리고** b | 둘 다 참이어야 참 |
| <code>a &#124;&#124; b</code> | a **또는** b | 하나만 참이어도 참 |
| `!a` | a가 **아니다** | 참↔거짓 뒤집기 |

```csharp
// 땅에 있고 AND 스태미나가 있으면 점프
if (isGrounded && stamina > 0) { }

// 체력이 0 이하이거나 OR 낙사했으면 사망
if (hp <= 0 || isFallen) { }

// 죽지 않았으면
if (!isDead) { }
```

기획서 문장을 그대로 옮기면 된다. "열쇠가 있고 문 앞에 있으면 문 열기"는 둘 다 만족해야 하니 `hasKey && nearDoor`다. 여기에 `||`를 쓰면 열쇠 없이 문 앞에만 가도 문이 열린다.

## 직접 해 보기
{:.briefing-heading}

[Day 0](/posts/csharp-week-basic-day0/)에서 만든 큐브의 `Player` 스크립트를 이렇게 바꾼다.

```csharp
using UnityEngine;

public class Player : MonoBehaviour
{
    public int hp = 30;
    public int coin = 120;
    public bool hasKey = false;

    void Start()
    {
        if (hp <= 0)
        {
            Debug.Log("게임 오버");
        }
        else if (hp < 50)
        {
            Debug.Log("위험! 체력 " + hp);
        }
        else
        {
            Debug.Log("체력 충분");
        }

        if (coin >= 100 && hasKey)
        {
            Debug.Log("보물 상자를 열었다");
        }
        else
        {
            Debug.Log("상자를 열 수 없다");
        }
    }
}
```

Day 1에서 Inspector의 Hp를 50으로 바꿔 뒀다면, 코드의 `hp = 30`은 무시되고 50이 그대로 쓰인다. Day 1의 주의 상자에서 본 바로 그 규칙이다. 그대로 실행하면 "위험!" 대신 "체력 충분"이 찍힌다. 실행하기 전에 Player 컴포넌트 오른쪽 위 ⋮ 메뉴에서 **Reset**을 눌러, Inspector 값을 코드에 적은 값(Hp 30, Coin 120)으로 되돌리자.
{: .prompt-warning }

실행하면 "위험! 체력 30"과 "상자를 열 수 없다"가 찍힌다. 이제 Inspector에서 값을 바꿔 가며 다시 실행해 보자.

- Hp를 0, 30, 80으로 바꾸면 각각 무엇이 찍히는지
- Has Key를 체크하면 상자가 열리는지
- `&&`를 `||`로 바꾸면 Has Key 없이도 열리는지

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. `if (hp)`처럼 숫자를 그대로 넣으면 안 돼?**<br>
C#에서는 에러다. C나 자바스크립트 같은 다른 언어는 "0이 아니면 참"으로 봐 주지만, C#은 `if`의 괄호 안에 bool만 받는다. 숫자는 `hp > 0`이나 `hp != 0`처럼 비교해서 bool로 만들어 넣는다. 조건을 비워 둔 `if ()`도 에러다.

```csharp
if (hp)        // 에러: int를 bool로 바꿀 수 없음
if (hp > 0)    // OK
```

나중에 다른 사람 코드에서 `if (player)`처럼 컴포넌트를 그대로 넣은 걸 볼 수 있다. 유니티 오브젝트는 "있으면 true, 없으면 false"로 자동으로 바뀌게 만들어져 있어서 되는 것이고, 뜻은 `if (player != null)`과 같다(null은 기초 Day 5에서 나온다). 이것도 결국 bool로 바뀌어 들어가니 규칙이 깨진 건 아니다. 처음에는 `!= null`로 쓰는 게 읽기 쉽다.

**Q. `if (hasKey & nearDoor)`처럼 `&`를 하나만 써도 되던데?**<br>
bool끼리는 `&` 하나도 "그리고"로 동작한다. 차이는 `&&`는 왼쪽이 거짓이면 오른쪽을 아예 계산하지 않는다는 것이다. 이 성질 덕분에 `if (target != null && target.hp > 0)`처럼 "있는지 먼저 확인하고, 있을 때만 값을 본다"를 한 줄로 쓸 수 있다. 조건에는 `&&`와 `||`를 쓴다고 기억하면 된다.

**Q. 콘솔에 `True`가 대문자로 찍혀.**<br>
`Debug.Log(a && b)`처럼 bool을 그대로 찍으면 `True`, `False`로 나온다. 코드에서는 소문자 `true`, `false`로 쓰고, 글자로 바꿔 보여 줄 때만 대문자다.

**Q. 조건이 길어져서 읽기 어려워.**<br>
조건을 bool 변수로 먼저 빼 두면 읽기 쉬워진다.

```csharp
bool canJump = isGrounded && stamina > 0;
if (canJump) { }
```

## 현업에서는
{:.briefing-heading}

- **조건에 이름을 붙인다.** `if (hp <= 0 && !isInvincible && !hasRevive)`보다 `bool shouldDie = ...; if (shouldDie)`가 훨씬 읽기 쉽다. 기획 문서의 용어를 그대로 이름으로 쓰면 기획자와 이야기하기도 편하다.
- **"이미 했는지" 깃발을 둔다.** "보상은 한 번만", "클리어 메시지는 한 번만" 같은 규칙은 `bool isCleared`처럼 한 번 했는지 기억하는 bool로 막는다. Day 7에서 실제로 쓴다.
- **갈래가 많아지면 다른 도구를 쓴다.** 상태가 대기·이동·공격·피격처럼 여러 개면 `if`를 길게 늘어놓기보다 `enum`과 `switch`를 쓴다. 심화 Day 4에서 배운다.

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **기초 Day 2**와 같은 내용이다.

- [if와 비교하기](https://hlcho426.github.io/unity-csharp-week/#d2l1): ==, >, <=
- [else와 else if](https://hlcho426.github.io/unity-csharp-week/#d2l2): 아니면, 그것도 아니면
- [그리고, 또는, 아니다](https://hlcho426.github.io/unity-csharp-week/#d2l3): &&, ||, !

## 정리
{:.briefing-heading}

- `if (조건) { ... }`: 조건이 참일 때만 실행한다. 괄호 안에는 반드시 bool이 들어간다
- `=`는 넣기, `==`는 같은지 묻기. 비교 결과는 항상 bool이다
- `else`는 위 조건이 전부 거짓일 때, `else if`는 위가 거짓이면 다음 조건을 검사한다
- 위에서부터 처음 맞는 하나만 실행된다. 겹치는 범위는 좁은 조건부터
- `&&` 둘 다 참, `||` 하나만 참, `!` 뒤집기. bool 변수는 그대로 조건에 넣는다

다음 글은 기초 Day 3, 반복문과 배열.
