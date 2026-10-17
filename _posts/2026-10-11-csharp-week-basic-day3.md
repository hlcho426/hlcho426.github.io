---
title: "<유니티 C#> 기초 Day 3: 반복문과 배열 (for, 배열, foreach, List)"
date: 2026-10-11 22:20:00 +0900
description: "for 반복문, 0부터 세는 배열, foreach, 늘었다 줄었다 하는 List까지. 무한 루프와 IndexOutOfRangeException을 피하는 법도 함께 정리했다."
series: 유니티 C# 일주일
series_title: "기초 Day 3: 반복문과 배열"
categories: [게임 제작 공부, 유니티]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

적을 5마리 만들고, 아이템 10개를 확인하고, 파티원 모두에게 회복을 걸어야 한다. 그러나 같은 코드를 다섯 번, 열 번 복사할 수는 없다.<br> 오늘은 같은 일을 여러 번 시키는 **반복문**과, 여러 값을 한 줄에 담는 **배열**, 그리고 늘었다 줄었다 하는 **List**를 배운다.

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

### for 줄 끝에는 ;를 찍지 않는다

```csharp
for (int i = 0; i < 3; i++);   // 줄 끝에 ; 를 찍었다
{
    Debug.Log("적 생성");
}
```

"적 생성"이 세 번이 아니라 **한 번** 찍힌다. for 줄 끝의 `;`가 "반복할 일은 아무것도 없음"이라는 빈 문장이 되어, for는 아무 일도 안 하고 세 바퀴를 돈 뒤 끝난다. 아래 중괄호는 for와 상관없는 그냥 덩어리라서 그다음에 한 번 실행된다.

[Day 1](/posts/csharp-week-basic-day1/)에서 본 "자리를 여닫는 줄에는 `;`를 찍지 않는다"가 바로 이 경우다. 빨간 에러도 안 나고 콘솔에 노란 경고(`Possible mistaken empty statement`, "빈 문장을 실수로 쓴 것 같다")만 뜨니, 반복이 이상하면 for 줄 끝부터 본다. `if (hp <= 0);`처럼 if 줄 끝에 찍어도 똑같이, 조건과 상관없이 아래 중괄호가 늘 실행된다.

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

**Q. `for (int i = 0; ...)`의 i는 꼭 int여야 해?**<br>
꼭 그렇지는 않다. 괄호의 첫 칸 `int i = 0`은 Day 1의 `int hp = 100;`과 같은 그냥 변수 만들기라서, 다른 자료형도 된다.

```csharp
for (float t = 0f; t < 1f; t += 0.25f)
    Debug.Log(t);   // 0, 0.25, 0.5, 0.75
```

그래도 거의 항상 int를 쓰는 이유가 두 가지 있다. 첫째, for는 대부분 `scores[i]`처럼 번호로 칸을 꺼내는 데 쓰는데, 번호는 int만 된다. `scores[1.5f]` 같은 칸은 없다. 둘째, float는 오차가 쌓인다. 0.1 같은 소수는 컴퓨터가 정확히 담지 못해서, 0.1f를 열 번 더하면 1이 아니라 1.0000001쯤이 된다. 그래서 `for (float t = 0f; t <= 1f; t += 0.1f)`는 11번 돌 것 같지만 10번만 돈다. "정확히 N번"에는 오차가 없는 int가 안전하다.

횟수가 정해지지 않은 반복("적이 다 죽을 때까지")에는 for보다 `while`이 어울린다. [심화 Day 2](/posts/csharp-week-adv-day2/)에서 나온다.

**Q. for는 배열이랑만 같이 써? List는?**<br>
List도 배열처럼 `bag[0]`, `bag[1]` 번호로 꺼낼 수 있어서 for로 똑같이 돈다. 개수 자리에 `Length` 대신 `Count`를 쓰는 것만 다르다.

```csharp
for (int i = 0; i < bag.Count; i++)
    Debug.Log(i + "번 칸: " + bag[i]);
```

배열이나 List 없이 횟수만 필요할 때도 쓴다. `for (int i = 0; i < 5; i++)` 안에 `Debug.Log("적 생성");`을 넣으면 다섯 번 찍힌다.

**Q. 배열은 크기를 못 늘린다면서, Inspector에서는 +로 늘어나던데?**<br>
Inspector의 +는 배열을 늘리는 게 아니라 **더 큰 새 배열로 바꿔치기**한다. 칸이 4개인 새 배열을 만들고, 10, 20, 30을 옮겨 담은 뒤, `scores`가 새 배열을 가리키게 바꾼다. 3칸짜리 사물함을 늘린 게 아니라 4칸짜리를 새로 사서 짐을 옮긴 셈이다. 코드에서 같은 일을 하려면 이 바꿔치기를 직접 해야 한다.

```csharp
scores[3] = 40;        // 3칸짜리 배열이면 에러: 3번 칸이 없다
scores = new int[4];   // 교체는 되지만 값이 0, 0, 0, 0으로 전부 사라진다
```

`scores[3] = 40`이 에러인지는 코드만 봐서는 정해지지 않는다. 배열이 몇 칸일지는 실행해 봐야 알기 때문에, 이 에러는 저장할 때 뜨는 빨간 컴파일 에러가 아니라 **실행 중에 그 줄을 지나는 순간** 난다. 그리고 배열은 오브젝트마다 따로 있다. Player가 붙은 오브젝트가 둘이고 그중 하나만 Inspector에서 4칸으로 늘렸다면, 4칸짜리는 3번 칸에 40이 잘 들어가고 3칸짜리만 `IndexOutOfRangeException`이 난다.

List는 이 이사를 알아서 해 준다. `Add`만 하면 칸이 모자랄 때 안에서 더 큰 배열을 만들어 옮겨 담는다. 그래서 게임 중에 개수가 계속 바뀌는 인벤토리 같은 건 List로 만든다.

**Q. 그럼 코드에는 3개인데 Inspector에는 4개면, 코드만 봐서는 모르잖아?**<br>
맞다. Day 1의 그 규칙(코드의 값은 처음 붙일 때의 기본값일 뿐, 그다음부터는 Inspector에 저장된 값이 쓰인다)이 배열에도 똑같이 적용된다. 유니티에서는 원래 이렇다. 수치와 목록은 Inspector(나중에 배울 ScriptableObject)에서 기획자가 채우고, 코드는 몇 개가 들어오든 동작하게 짠다. 그래서 이렇게 한다.

- 개수를 `3`처럼 숫자로 박지 않고 `scores.Length`로 쓴다. 위 for문도 Length를 써서, Inspector에서 4개로 늘리면 4번 돈다.
- 실제 값이 궁금하면 Inspector를 보거나 `Debug.Log(scores.Length)`로 찍어 본다.
- 코드의 값으로 되돌리고 싶으면 컴포넌트 ⋮ 메뉴의 **Reset**을 누른다.

**Q. List도 번호를 쓸 때 칸이 있는지 확인해야 해?**<br>
그렇다. 오히려 더 조심해야 한다. 게임 중에 `Remove`로 개수가 계속 바뀌기 때문이다. 없는 번호를 쓰면 배열처럼 에러가 난다(이름만 `ArgumentOutOfRangeException`으로 조금 다르다).

```csharp
List<string> bag = new List<string>();
bag.Add("포션");       // 지금 1개, 0번 칸만 있다

Debug.Log(bag[1]);     // 에러: 1번 칸이 없다
bag[1] = "검";         // 이것도 에러
```

List는 늘어나는 목록인데도 `bag[1] = "검"`으로는 안 늘어난다. 번호로는 **이미 있는 칸**만 읽고 바꿀 수 있고, 칸을 늘리는 건 `Add`와 `Insert`뿐이다. 그래서 이렇게 쓴다.

- 번호를 직접 쓸 때는 `if (i < bag.Count)`로 칸이 있는지 먼저 확인한다.
- 첫 번째 것을 꺼낼 때는 `if (bag.Count > 0)`으로 비어 있지 않은지 본다. 빈 List의 `bag[0]`도 에러다.
- 전부 돌 때는 `for (int i = 0; i < bag.Count; i++)`나 `foreach`를 쓴다. 범위가 알아서 맞춰져서 따로 확인할 필요가 없다.
- 몇 번 칸에 있는지 모를 때는 번호를 짐작하지 말고 `bag.Contains("포션")`(있나?)이나 `bag.IndexOf("포션")`(몇 번 칸? 없으면 -1)으로 찾는다. 다지기 Day 1에서 자세히 다룬다.

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
- 없는 번호를 쓰면 `IndexOutOfRangeException`(List는 `ArgumentOutOfRangeException`). 번호를 직접 쓸 때는 `Length`·`Count`로 칸이 있는지 먼저 확인
- `foreach (자료형 x in 목록)`: 하나씩 꺼내 반복
- List는 크기가 변하는 배열. `Add`, `Remove`, `Count`

다음 글은 기초 Day 4, 함수와 void.
