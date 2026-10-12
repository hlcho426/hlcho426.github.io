---
title: "<유니티 C#> 기초 Day 3: 반복문과 배열 (for, 배열, foreach, List)"
date: 2026-10-11 22:20:00 +0900
description: "for 반복문, 0부터 세는 배열, foreach, 늘었다 줄었다 하는 List까지. 무한 루프와 IndexOutOfRangeException을 피하는 법도 함께 정리했다."
series: 유니티 C# 일주일
series_title: "기초 Day 3: 반복문과 배열"
categories: [유니티 공부]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

적을 5마리 만들고, 아이템 10개를 확인하고, 파티원 모두에게 회복을 걸어야 한다. 같은 코드를 다섯 번, 열 번 복사할 수는 없다. 오늘은 같은 일을 여러 번 시키는 **반복문**과, 여러 값을 한 줄에 담는 **배열**, 그리고 늘었다 줄었다 하는 **List**를 배운다.

**오늘의 목표**

- `for`로 정해진 횟수만큼 반복할 수 있다
- 배열을 만들고 번호(인덱스)로 꺼낼 수 있다. 번호는 0부터다
- `foreach`로 목록을 하나씩 꺼내 쓸 수 있다
- 크기가 변하는 목록에는 `List`를 쓴다는 걸 안다

## 1. for: 정해진 횟수만큼
{:.briefing-heading}

```csharp
for (int i = 0; i < 3; i++)
{
    Debug.Log(i);
}
```

출력은 `0`, `1`, `2`다. 괄호 안은 세미콜론으로 나뉜 세 칸이다.

| 칸 | 뜻 |
|---|---|
| `int i = 0` | 시작: 숫자 상자 i를 0으로 만든다 |
| `i < 3` | 이 조건이 참인 동안 계속 돈다 |
| `i++` | 한 바퀴 돌 때마다 i에 1을 더한다 |

순서대로 따라가 보면 이렇다. i가 0 → 조건 참 → 실행 → i가 1 → 조건 참 → 실행 → i가 2 → 조건 참 → 실행 → i가 3 → 조건 거짓 → 끝. 그래서 세 번 돈다.

**0부터 시작해서 `i < n`**이면 정확히 n번 돈다. 이 모양이 가장 흔하다. "적 생성"을 5번 찍고 싶으면 `i < 5`다.

반복하면서 값을 모을 수도 있다.

```csharp
int total = 0;
for (int i = 1; i <= 3; i++)
{
    total += i;
}
// total = 1 + 2 + 3 = 6
```

### 무한 루프 조심

```csharp
for (int i = 0; i < 10; i--)   // i++ 대신 i--
{
    Debug.Log(i);
}
```

i가 0, -1, -2… 로 작아지기만 해서 `i < 10`이 계속 참이다. 사실상 끝나지 않는 반복은 유니티 에디터를 통째로 멈춰 버린다. 이렇게 되면 작업 관리자로 유니티를 강제로 꺼야 하고, 저장하지 않은 씬 작업이 날아간다.

> 반복문을 고친 뒤 처음 실행할 때는 **씬을 먼저 저장(Ctrl + S)**하고 ▶을 누르자.
{: .prompt-warning }

## 2. 배열: 번호가 붙은 상자들
{:.briefing-heading}

```csharp
int[] scores = { 10, 20, 30 };

Debug.Log(scores[0]);      // 10
Debug.Log(scores[2]);      // 30
Debug.Log(scores.Length);  // 3
```

자료형 뒤에 `[]`를 붙이면 같은 종류의 값을 여러 개 담는 **배열**이 된다. 사물함처럼 칸마다 번호가 붙어 있고, 꺼낼 때는 `배열이름[번호]`로 꺼낸다.

가장 중요한 규칙은 하나다. **번호는 0부터 센다.** 칸이 3개면 번호는 0, 1, 2다. 개수는 `Length`로 알 수 있고, 마지막 번호는 항상 `Length - 1`이다.

```csharp
string[] items = { "검", "방패", "포션" };
Debug.Log(items[1]);   // 방패 (0번이 검)
```

없는 번호를 꺼내면 에러가 난다.

```csharp
int[] arr = { 1, 2, 3 };
Debug.Log(arr[3]);   // IndexOutOfRangeException
```

`IndexOutOfRangeException`은 "번호가 범위를 벗어났다"는 뜻이다. 앞으로 정말 자주 보게 될 에러라, 보면 "0부터 셌나? Length를 넘었나?"부터 확인하면 된다.

배열 칸도 변수처럼 값을 바꿀 수 있다.

```csharp
int[] hp = { 100, 80 };
hp[1] = 50;   // 두 번째 칸을 50으로
```

### for와 배열은 단짝

배열의 모든 칸을 돌 때는 for를 이렇게 쓴다.

```csharp
for (int i = 0; i < scores.Length; i++)
{
    Debug.Log(scores[i]);
}
```

i가 0부터 `Length - 1`까지 딱 맞게 돈다. 배열 크기가 바뀌어도 코드를 고칠 필요가 없다.

## 3. foreach: 번호 없이 하나씩
{:.briefing-heading}

번호가 필요 없으면 `foreach`가 더 편하다.

```csharp
string[] party = { "전사", "마법사", "궁수" };

foreach (string member in party)
{
    Debug.Log(member);
}
```

"party 안의 각 member에 대해"라고 읽는다. 배열에 든 순서대로 하나씩 꺼내 `member`에 담고 중괄호 안을 실행한다.

## 4. List: 늘었다 줄었다 하는 목록
{:.briefing-heading}

배열은 만들 때 칸 수가 정해지고 바꿀 수 없다. 그런데 인벤토리나 살아 있는 적 목록은 계속 늘고 준다. 이럴 때 **List**를 쓴다.

```csharp
using System.Collections.Generic;   // 파일 맨 위에 추가

List<string> bag = new List<string>();
bag.Add("포션");
bag.Add("열쇠");
Debug.Log(bag.Count);   // 2
bag.Remove("포션");
Debug.Log(bag[0]);      // 열쇠
```

- `List<string>`: 글자를 담는 List. 꺾쇠 안이 담을 자료형이다
- `new List<string>()`: 실제 빈 목록을 만든다
- `Add`로 넣고, `Remove`로 빼고, `[번호]`로 꺼낸다
- 개수는 `Length`가 아니라 **`Count`**다

> List를 쓰려면 파일 맨 위에 `using System.Collections.Generic;`이 있어야 한다. 없으면 "List를 찾을 수 없다"는 빨간 에러가 뜬다.
{: .prompt-tip }

List는 다지기 Day 1에서 원리까지 자세히 다시 다룬다. 지금은 "크기가 변하면 List"만 기억하면 된다.

## 직접 해 보기
{:.briefing-heading}

배열과 List는 `public`으로 만들면 Inspector에서 값을 넣을 수 있다.

```csharp
using System.Collections.Generic;
using UnityEngine;

public class Player : MonoBehaviour
{
    public int[] scores = { 10, 20, 30 };
    public List<string> bag = new List<string>();

    void Start()
    {
        int total = 0;
        for (int i = 0; i < scores.Length; i++)
        {
            total += scores[i];
        }
        Debug.Log("점수 " + scores.Length + "개, 합계 " + total);

        bag.Add("포션");
        foreach (string item in bag)
        {
            Debug.Log("가방: " + item);
        }
        Debug.Log("가방 아이템 수: " + bag.Count);
    }
}
```

저장하고 Inspector를 보면 Scores와 Bag 칸이 목록으로 보인다. Scores의 숫자를 바꾸거나 +로 칸을 늘려 보자. Bag에도 아이템 이름을 몇 개 넣어 두면, 실행할 때 코드가 넣은 "포션"이 맨 뒤에 붙어서 같이 찍힌다.

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. 왜 번호가 1이 아니라 0부터야?**<br>
컴퓨터는 번호를 "맨 앞에서 몇 칸 떨어져 있나"로 센다. 첫 칸은 맨 앞에서 0칸 떨어져 있으니 0번이다. 익숙해지는 수밖에 없다. 대신 `for (int i = 0; i < 배열.Length; i++)` 모양을 통째로 외워 두면 헷갈릴 일이 거의 없다.

**Q. Length랑 Count를 자꾸 헷갈려.**<br>
배열은 `Length`, List는 `Count`다. 틀리게 쓰면 빨간 에러로 바로 알려 주니 걱정하지 않아도 된다.

**Q. for와 foreach 중 뭘 써?**<br>
번호(몇 번째인지)가 필요하면 `for`, 그냥 하나씩 다 보면 되면 `foreach`가 읽기 쉽다. 단, foreach로 도는 중에 그 목록에서 Add나 Remove를 하면 에러가 난다. 지우면서 돌아야 할 때는 다지기 Day 1에서 배우는 방법을 쓴다.

## 현업에서는
{:.briefing-heading}

- **배열 크기를 숫자로 박지 않는다.** `i < 3` 대신 `i < scores.Length`처럼 쓰면 데이터가 바뀌어도 코드는 그대로다.
- **Inspector에서 채우는 목록이 많다.** 스폰 위치, 드랍 아이템, 대사 같은 걸 `public` 배열이나 List로 빼 두고 기획자가 직접 채우게 한다.
- **목록을 매 프레임 새로 만들지 않는다.** `new List<...>()`를 Update 안에서 계속 하면 쓰레기 메모리가 쌓여 가끔 버벅인다. 한 번 만들어 두고 비우고(`Clear`) 다시 쓴다.

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **기초 Day 3**과 같은 내용이다.

- [for: 정해진 횟수 반복](https://hlcho426.github.io/unity-csharp-week/#d3l1)
- [배열: 여러 값을 한 줄로](https://hlcho426.github.io/unity-csharp-week/#d3l2): int[ ], [0], Length
- [foreach와 List](https://hlcho426.github.io/unity-csharp-week/#d3l3): 하나씩 꺼내기, 늘어나는 목록

## 정리
{:.briefing-heading}

- `for (시작; 계속할 조건; 매번 할 일)`. 0부터 `i < n`이면 n번
- 배열: `자료형[] 이름 = { 값, 값, 값 };`, 번호는 0부터, 마지막 번호는 `Length - 1`
- 없는 번호를 쓰면 `IndexOutOfRangeException`
- `foreach (자료형 x in 목록)`: 하나씩 꺼내 반복
- List는 크기가 변하는 배열. `Add`, `Remove`, `Count`

다음 글은 기초 Day 4, 함수와 void.
