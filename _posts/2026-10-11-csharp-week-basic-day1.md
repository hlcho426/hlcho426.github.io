---
title: "유니티 C# 기초 Day 1: 스크립트와 변수 (Start, Update, int, float, public)"
date: 2026-10-11 22:12:00 +0900
series: 유니티 C# 일주일
series_title: "기초 Day 1: 스크립트와 변수"
categories: [유니티 공부]
tags: [유니티, C#, 변수, 자료형, Start, Update, 유니티 C# 일주일]
---

{% include series.html %}

[Day 0](/posts/csharp-week-basic-day0/)에서 큐브에 스크립트를 붙이고 콘솔에 글자를 띄웠다. 오늘은 그 스크립트를 한 줄씩 읽고, 게임에 필요한 숫자를 담는 **변수**를 배운다.

**오늘의 목표**

- 유니티 스크립트의 뼈대를 읽을 수 있다
- `Start`와 `Update`가 언제 실행되는지 안다
- `int`, `float`, `bool`, `string` 변수를 만들고 계산할 수 있다
- `public`을 붙여 인스펙터에서 값을 바꿀 수 있다

## 1. 스크립트의 뼈대 읽기

새 스크립트를 만들면 늘 이 모양이다.

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

처음엔 외계어 같지만 줄마다 하는 일은 단순하다.

| 코드 | 뜻 |
|---|---|
| `using UnityEngine;` | 유니티가 준비해 둔 도구 상자를 쓰겠다는 선언. `Debug`, `Transform` 같은 걸 쓰려면 필요하다 |
| `public class Player` | `Player`라는 이름의 스크립트(클래스). **파일 이름 Player.cs와 같아야 한다** |
| `: MonoBehaviour` | "유니티 오브젝트에 붙일 수 있는 스크립트"라는 표시. 이게 있어야 컴포넌트로 붙는다 |
| `{ }` | 중괄호. 여기서부터 여기까지가 한 덩어리라는 표시 |
| `void Start()` | 게임이 시작될 때 **딱 한 번** 실행되는 곳 |
| `void Update()` | **매 프레임** 계속 실행되는 곳 |

`class`가 정확히 무엇인지, `void`가 왜 붙는지는 뒤에서 제대로 다룬다. 지금은 "유니티가 정해 둔 자리"라고만 알아 두면 된다. 함수와 `void`는 기초 Day 4, 클래스는 심화 Day 1에서 배운다.

### Start와 Update는 내가 부르지 않는다

`Start`와 `Update`는 내가 직접 실행하라고 하지 않아도 **유니티가 알아서 불러 준다.** 게임이 시작되면 `Start`를 한 번, 그다음부터는 화면을 한 번 그릴 때마다(한 프레임마다) `Update`를 부른다.

게임이 1초에 60프레임으로 돌면 `Update`는 1초에 약 60번 실행된다. 그래서 이 코드는 콘솔을 순식간에 도배한다.

```csharp
void Update()
{
    Debug.Log("안녕");
}
```

그래서 역할을 나눈다.

- **Start**: 처음 한 번 준비할 것. 체력 채우기, 필요한 컴포넌트 찾아 두기
- **Update**: 계속 확인하거나 바꿔야 할 것. 키 입력 확인, 이동

### 세미콜론과 중괄호

```csharp
void Start()
{
    Debug.Log("안녕, 선라이트!");
}
```

`Debug.Log(...)`는 괄호 안의 내용을 콘솔에 찍는다. 코드가 내 생각대로 도는지 확인할 때 개발자가 제일 많이 쓰는 도구다.

문장 끝의 `;`(세미콜론)은 "이 명령 끝"이라는 마침표다. 하나라도 빠지면 빨간 에러가 뜨고 게임이 실행되지 않는다. 초보 에러 1순위다.

## 2. 변수: 값을 담는 상자

게임에는 기억해야 할 값이 많다. 체력, 속도, 점수, 닉네임. 이런 값을 담아 두는 이름 붙은 상자가 **변수**다.

```csharp
int hp = 100;
```

| 조각 | 뜻 |
|---|---|
| `int` | 상자의 종류(**자료형**). 정수를 담는다 |
| `hp` | 상자 이름. 내가 정한다 |
| `= 100` | 처음 넣을 값 |
| `;` | 끝 |

### 자주 쓰는 상자 네 종류

```csharp
int    coin     = 30;      // 정수
float  speed    = 3.5f;    // 소수 (뒤에 f!)
bool   isAlive  = true;    // 참/거짓
string nickname = "Sun";   // 글자 (큰따옴표)
```

`//` 뒤는 **주석**이다. 컴퓨터는 무시하고 사람이 읽으라고 남기는 메모다.

- **int**: 개수, 점수처럼 소수점이 필요 없는 숫자
- **float**: 속도, 시간처럼 소수점이 필요한 숫자. 숫자 뒤에 `f`를 붙인다
- **bool**: 예/아니오 두 가지뿐인 정보. "땅에 닿아 있나?", "죽었나?" 같은 것. 이름을 `isGrounded`, `isDead`처럼 `is`로 시작하면 읽기 좋다
- **string**: 글자. 큰따옴표로 감싼다

### `=`는 "같다"가 아니다

```csharp
int hp = 100;
hp = hp - 30;
```

수학 시간에 `hp = hp - 30`을 보면 말이 안 된다. 하지만 코드에서 `=`는 **오른쪽을 계산해서 왼쪽 상자에 넣어라**라는 뜻이다. 그래서 두 번째 줄은 "지금 hp에서 30을 뺀 값을 다시 hp에 넣어라"이고, hp는 70이 된다. "같은가?"를 묻는 건 `==`이다. 이건 기초 Day 2의 if에서 나온다.

## 3. 계산하기

게임 코드에서 정말 자주 쓰는 줄임 표현이 있다.

```csharp
int score = 0;
score = score + 10;  // 기본
score += 10;         // 같은 뜻, 짧게
score++;             // 1 더하기
```

`-=`(빼서 넣기), `*=`(곱해서 넣기)도 같은 방식이다. 코인을 먹을 때 `coin++`, 데미지를 받을 때 `hp -= damage`처럼 쓴다.

### 함정: 정수끼리 나누면 소수점이 사라진다

```csharp
int a = 7;
int b = 2;
Debug.Log(a / b);   // 3
```

3.5가 아니라 **3**이 나온다. `int`끼리 나누면 결과도 `int`라서 소수점 아래를 버린다. 하나라도 소수로 만들면 3.5가 나온다.

```csharp
Debug.Log(7f / 2);          // 3.5
Debug.Log((float)a / b);    // 3.5  (a를 float로 바꿔서 나누기)
```

이 함정은 나중에 체력바를 만들 때 다시 나온다. 체력 70 / 최대 체력 100을 `int`끼리 나누면 0이 돼서 체력바가 텅 빈다.

### 글자 + 숫자 = 이어 붙인 글자

```csharp
int hp = 70;
Debug.Log("HP: " + hp);   // HP: 70
```

글자에 `+`로 숫자를 붙이면 숫자가 글자로 바뀌어 이어 붙는다. UI에 체력을 표시할 때 이렇게 쓴다.

## 4. public: 인스펙터에서 값 바꾸기

```csharp
public class Player : MonoBehaviour
{
    public float speed = 5f;
    int coin = 0;
}
```

변수 앞에 `public`을 붙이고 저장하면, 유니티 Inspector의 Player 칸에 **Speed** 입력칸이 생긴다. 코드를 고치지 않고 숫자만 바꿔 가며 테스트할 수 있다. 아무것도 안 붙인 `coin`은 Inspector에 안 보인다.

순서는 꼭 `public → 자료형 → 이름 → 값`이다. `public jumpPower = 7f;`처럼 자료형을 빼거나 `float public jumpPower`처럼 순서를 바꾸면 에러다.

> 실무에서는 `public` 대신 `[SerializeField]`를 더 많이 쓴다. Inspector에는 보이지만 다른 스크립트가 함부로 바꾸지는 못하게 하는 방법이다. 기초 Day 5에서 배운다.
{: .prompt-tip }

## 직접 해 보기

Day 0에서 만든 `Player` 스크립트를 이렇게 바꾸고 실행해 보자.

```csharp
using UnityEngine;

public class Player : MonoBehaviour
{
    public int hp = 100;
    public float speed = 3.5f;
    public string nickname = "Sun";

    void Start()
    {
        Debug.Log(nickname + "의 체력: " + hp);

        hp -= 30;
        Debug.Log("함정을 밟았다! 남은 체력: " + hp);

        Debug.Log("7 / 2 = " + (7 / 2));
        Debug.Log("7f / 2 = " + (7f / 2));
    }
}
```

콘솔에 이렇게 찍힌다.

```
Sun의 체력: 100
함정을 밟았다! 남은 체력: 70
7 / 2 = 3
7f / 2 = 3.5
```

이제 Inspector에서 Hp를 50으로, Nickname을 내 이름으로 바꾸고 다시 실행해 보자. 코드는 그대로인데 결과가 바뀐다.

## 자주 헷갈리는 것

**Q. float에는 왜 f를 붙여야 해?**<br>
C#은 `3.5`처럼 쓴 소수를 기본으로 `double`이라는 더 큰 소수 자료형으로 본다. 큰 상자에 든 값을 작은 `float` 상자에 그냥 넣을 수는 없어서 에러가 난다. 뒤에 `f`를 붙이면 "처음부터 float 값이야"라는 뜻이 된다. `float speed = 3.5;`는 에러, `float speed = 3.5f;`는 정상이다.

**Q. 코드에서 `speed = 5f`를 `10f`로 바꿨는데 게임에선 여전히 5야.**<br>
`public` 변수의 값은 **Inspector에 저장된 값이 이긴다.** 코드에 쓴 값은 스크립트를 처음 붙일 때의 기본값일 뿐이고, 그다음부터는 씬에 저장된 Inspector 값이 쓰인다. Inspector에서 직접 바꾸거나, 컴포넌트 오른쪽 위 ⋮ 메뉴의 **Reset**을 누르면 코드의 값으로 돌아간다. 초보 때 정말 많이 헤매는 부분이다.

**Q. 변수 이름은 아무렇게나 지어도 돼?**<br>
규칙만 지키면 된다. 숫자로 시작할 수 없고, 띄어쓰기를 넣을 수 없다. 그리고 C#은 **대소문자를 구분해서** `hp`와 `Hp`는 다른 변수다. 관례상 변수는 `moveSpeed`처럼 소문자로 시작해서 단어마다 대문자로 쓰고(camelCase), 클래스는 `PlayerMove`처럼 대문자로 시작한다(PascalCase).

## 현업에서는

- **숫자를 코드에 박지 않는다.** `transform.position += ... * 5f`처럼 숫자를 코드 한가운데 쓰면 나중에 찾기도 바꾸기도 어렵다. 의미 있는 이름의 변수로 빼서 Inspector에 꺼내 두면, 기획자도 코드를 안 열고 수치를 조정할 수 있다.
- **글자를 이어 붙일 때는 문자열 보간을 많이 쓴다.** `$"HP: {hp} / {maxHp}"`처럼 따옴표 앞에 `$`를 붙이고 중괄호 안에 변수를 넣는다. `+`를 여러 번 쓰는 것보다 읽기 쉽다.
- **`Update` 안의 `Debug.Log`는 확인이 끝나면 지운다.** 매 프레임 로그를 찍으면 콘솔도 보기 어렵고 게임도 느려진다.

## 앱에서 연습하기

이 글은 앱의 **기초 Day 1**과 같은 내용이다. 레슨마다 바로 열린다.

- [유니티 스크립트의 생김새](https://hlcho426.github.io/unity-csharp-week/#d1l1): Start, Update, Debug.Log
- [변수: 값을 담는 상자](https://hlcho426.github.io/unity-csharp-week/#d1l2): int, float, bool, string
- [계산하고, 인스펙터에 꺼내기](https://hlcho426.github.io/unity-csharp-week/#d1l3): 연산자와 public

## 정리

- 스크립트 = 게임 오브젝트에 붙이는 C# 클래스. 파일 이름과 클래스 이름이 같아야 한다
- `Start`는 시작할 때 한 번, `Update`는 매 프레임
- 변수 만들기: `자료형 이름 = 값;`
- `int` 정수 / `float` 소수(뒤에 f) / `bool` 참·거짓 / `string` 글자
- `=`는 "오른쪽 값을 왼쪽에 넣기". `int`끼리 나누면 소수점이 버려진다
- `public`을 붙이면 Inspector에서 값을 조절할 수 있다. 이미 붙은 컴포넌트는 Inspector 값이 우선이다

다음 글은 기초 Day 2, if로 판단하기.
