---
title: "<유니티 C#> 기초 Day 4: 함수와 void, 매개변수, return (void는 왜 쓸까?)"
date: 2026-10-11 22:24:00 +0900
description: "void는 왜 쓸까? 함수를 만들고 부르는 법, 매개변수로 값 넘기기, return으로 결과 돌려받기까지 유니티 C# 함수를 비전공자 눈높이로 정리했다."
series: 유니티 C# 일주일
series_title: "기초 Day 4: 함수와 void"
categories: [유니티 공부]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

처음 스크립트를 열었을 때부터 `void Start()`, `void Update()`가 있었다. 그런데 `void`가 뭔지는 아무도 말해 주지 않았다. 나도 공부하면서 void가 왜 붙는지 따로 물어봤다. 오늘은 그 답인 **함수**를 배운다.

**오늘의 목표**

- 함수를 만들고 부를 수 있다
- 매개변수로 함수에 값을 넘길 수 있다
- `return`으로 결과를 돌려받을 수 있다
- `void`가 무슨 뜻인지, 언제 쓰는지 설명할 수 있다

## 1. 함수: 코드 묶음에 이름 붙이기
{:.briefing-heading}

자주 하는 동작에 이름을 붙여 두고, 필요할 때 이름만 부르는 것이 **함수**다.

```csharp
void Start()
{
    SayHello();
    SayHello();
}

void SayHello()
{
    Debug.Log("안녕!");
}
```

- **만들기**: `void SayHello() { ... }`. 이름을 정하고 중괄호 안에 할 일을 쓴다
- **부르기**: `SayHello();`. 이름 뒤에 괄호와 세미콜론

위 코드는 "안녕!"을 두 번 찍는다. `SayHello()`를 부르는 순간 SayHello 안으로 들어가 코드를 실행하고, 끝나면 부른 자리로 돌아와 다음 줄을 이어서 실행한다.

```csharp
void Start()
{
    Debug.Log("A");
    Hit();
    Debug.Log("C");
}

void Hit()
{
    Debug.Log("B");
}
```

출력은 A, B, C 순서다.

만들기만 하고 부르지 않은 함수는 **실행되지 않는다.** 그럼 `Start`와 `Update`는 누가 불렀을까? **유니티가 대신 불러 준다.** 유니티는 정해진 이름(`Start`, `Update`, 나중에 배울 `OnTriggerEnter` 등)의 함수를 찾아서 정해진 때에 부른다. 그래서 이 이름들은 철자와 대소문자가 정확해야 한다.

함수를 쓰는 가장 큰 이유는 **같은 코드를 여러 번 쓰지 않으려고**다. 한 곳에 만들어 두면 여러 곳에서 부를 수 있고, 고칠 때도 한 곳만 고치면 된다.

## 2. 매개변수: 함수에 값 넘기기
{:.briefing-heading}

데미지는 매번 다르다. 10일 때도 있고 25일 때도 있다. 그때마다 함수를 새로 만들 수는 없으니, 함수가 **값을 받게** 만든다.

```csharp
int hp = 100;

void Start()
{
    TakeDamage(10);
    TakeDamage(25);
}

void TakeDamage(int amount)
{
    hp -= amount;
    Debug.Log("남은 체력: " + hp);
}
```

괄호 안의 `int amount`가 **매개변수**다. 함수가 받을 값의 자료형과 이름이다. 부를 때 넣은 10, 25가 amount에 담겨서 들어간다. 그래서 "남은 체력: 90", "남은 체력: 65"가 찍힌다.

- 만들 때: `void Heal(int amount)`처럼 **자료형과 이름**을 쓴다
- 부를 때: `Heal(30);`처럼 **값만** 넣는다. `Heal(int 30);`은 에러다
- 여러 개는 쉼표로: `void Move(float x, float y)`, 부를 때 `Move(1f, 2f);`

## 3. return: 결과 돌려받기
{:.briefing-heading}

지금까지의 함수는 일만 하고 끝났다. 이번에는 **계산해서 답을 돌려주는** 함수다.

```csharp
int Add(int a, int b)
{
    return a + b;
}

void Start()
{
    int result = Add(3, 4);
    Debug.Log(result);   // 7
}
```

함수 이름 앞, 늘 `void`가 있던 자리에 `int`가 들어갔다. "이 함수는 **int 값을 돌려준다**"는 뜻이다. 함수 안의 `return a + b;`가 계산한 값을 부른 자리로 돌려보낸다. 그래서 `Add(3, 4)`라고 쓴 자리가 통째로 7로 바뀐 것처럼 동작한다.

돌려주는 자료형은 무엇이든 될 수 있다.

```csharp
int hp = 0;

bool IsDead()
{
    return hp <= 0;
}

void Start()
{
    if (IsDead())
    {
        Debug.Log("게임 오버");
    }
}
```

`IsDead()`는 참·거짓을 돌려주니 `bool`이다. 이런 함수는 이름을 `Is`, `Has`, `Can`으로 시작하면 `if (IsDead())`처럼 문장처럼 읽힌다.

### return을 만나면 그 자리에서 끝

```csharp
string Check(int coin)
{
    if (coin >= 10)
        return "부자";
    return "가난";
}
```

`Check(15)`는 "부자"다. `return`을 만나는 순간 함수가 끝나서 아래의 `return "가난";`까지 가지 않는다.

## 4. 그래서 void는 왜 쓸까?
{:.briefing-heading}

이제 답할 수 있다. **`void`는 "돌려주는 값이 없다"는 표시**다.

C#은 함수를 만들 때 반드시 "이 함수가 무엇을 돌려주는지"를 함수 이름 앞에 적게 되어 있다. `int`를 돌려주면 `int`, `bool`을 돌려주면 `bool`. 그런데 `SayHello()`나 `TakeDamage()`처럼 일만 하고 돌려줄 게 없는 함수도 그 자리를 비워 둘 수는 없다. 그래서 "없음"이라는 뜻의 `void`를 쓴다.

심부름에 비유하면 이렇다.

| 심부름 | 돌려받는 것 | 함수로 쓰면 |
|---|---|---|
| "불 좀 꺼 줘" | 없음 | `void TurnOffLight()` |
| "지금 몇 시야?" | 시간(숫자) | `int GetHour()` |
| "문 잠겼어?" | 예/아니오 | `bool IsLocked()` |

고르는 기준은 하나다. **부른 쪽이 결과를 받아서 써야 하면 그 자료형, 아니면 void.**

이 기준은 앞으로 계속 나온다. 예를 들어 심화 코스의 세이브 기능을 만들 때, 저장하는 `Save`는 일만 하니 `void`, 불러오는 `Load`는 꺼낸 데이터를 돌려줘야 하니 `SaveData`를 돌려주는 함수가 된다.

## 직접 해 보기
{:.briefing-heading}

```csharp
using UnityEngine;

public class Player : MonoBehaviour
{
    public int hp = 100;
    public int maxHp = 100;

    void Start()
    {
        TakeDamage(30);
        TakeDamage(50);
        Heal(200);

        if (IsDead())
            Debug.Log("게임 오버");
        else
            Debug.Log("생존! 체력 " + hp + " / " + maxHp);
    }

    void TakeDamage(int amount)
    {
        hp -= amount;
        Debug.Log(amount + " 데미지, 남은 체력 " + hp);
    }

    void Heal(int amount)
    {
        hp += amount;
        if (hp > maxHp) hp = maxHp;   // 최대 체력을 넘지 않게
        Debug.Log(amount + " 회복, 체력 " + hp);
    }

    bool IsDead()
    {
        return hp <= 0;
    }
}
```

앞의 Day에서 Inspector로 Hp를 바꿔 봤다면 그 값이 남아 있어서 결과가 아래와 다르게 나올 수 있다. 실행하기 전에 Player 컴포넌트의 ⋮ 메뉴에서 **Reset**을 눌러 코드에 적은 값(Hp 100, Max Hp 100)으로 맞추자.
{: .prompt-warning }

실행하면 체력이 70, 20으로 줄었다가 회복으로 100이 되고 "생존!"이 찍힌다. `Heal` 안의 `if` 덕분에 200을 회복해도 최대 체력 100을 넘지 않는다. 이렇게 **체력을 다루는 규칙을 함수 안에 모아 두면** 다른 곳에서 신경 쓸 필요가 없다.

Start의 `TakeDamage(50)`을 `TakeDamage(200)`으로 바꿔 보자. Heal이 불려서 체력이 다시 100으로 차니 여전히 "생존!"이다. 그럼 Heal 줄을 지우면?

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. 부를 때 `Jump;`라고 쓰면 안 돼?**<br>
안 된다. 이름 뒤에 괄호가 있어야 "지금 실행해"라는 뜻이 된다. `Jump;`는 빨간 에러다. 반대로 `void`는 만들 때만 붙인다. 부를 때 `void Jump();`라고 쓰면 그것도 에러다.

**Q. 매개변수 `amount`는 함수 밖에서 쓸 수 있어?**<br>
없다. 매개변수는 그 함수 안에서만 사는 변수다. 함수가 끝나면 사라진다. 이건 기초 Day 8에서 "변수의 범위"로 자세히 다룬다.

**Q. 만든 함수가 실행이 안 돼.**<br>
누군가 불렀는지 확인한다. 내가 만든 함수는 내가 불러야 실행된다. `Start`, `Update` 같은 유니티 함수인데 안 불린다면 이름의 대소문자를 확인한다. `update()`는 유니티가 모르는 이름이라 에러도 없이 그냥 무시된다.

## 현업에서는
{:.briefing-heading}

- **함수 이름은 동사로 시작한다.** `TakeDamage`, `Jump`, `SpawnEnemy`처럼 무슨 일을 하는지 바로 보이게 짓는다. bool을 돌려주면 `IsDead`, `HasKey`, `CanJump`.
- **함수 하나는 한 가지 일만 한다.** 함수가 길어지고 "그리고"가 여러 번 들어가면 나눌 때가 됐다는 신호다.
- **규칙은 함수 안에 가둔다.** 체력을 직접 `hp -= 10`으로 여기저기서 깎지 않고 `TakeDamage(10)`으로 부르면, 나중에 "방어력만큼 덜 깎기", "무적 시간" 같은 규칙을 이 함수 하나에만 넣으면 된다.

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **기초 Day 4**와 같은 내용이다.

- [함수 만들고 부르기](https://hlcho426.github.io/unity-csharp-week/#d4l1): void Jump() { }
- [매개변수: 함수에 값 넘기기](https://hlcho426.github.io/unity-csharp-week/#d4l2): TakeDamage(int amount)
- [return: 결과 돌려받기](https://hlcho426.github.io/unity-csharp-week/#d4l3): int, bool을 돌려주는 함수

## 정리
{:.briefing-heading}

- 함수 = 코드 묶음에 이름 붙이기. 만들기 `void 이름() { }`, 부르기 `이름();`
- 괄호 안에 받을 값을 선언한다: `(int amount)`. 부를 때는 값만 넣는다: `TakeDamage(10);`
- `int Add(...) { return 값; }`: 이름 앞의 자료형을 돌려준다. return을 만나면 바로 끝난다
- `void` = 돌려주는 값 없음. 부른 쪽이 결과를 받아 써야 하면 그 자료형, 아니면 void
- `Start`, `Update`도 함수다. 유니티가 대신 불러 줄 뿐이다

다음 글은 기초 Day 5, Transform과 컴포넌트.
