---
title: "<유니티 C#> 기초 Day 8: 변수의 범위와 함수의 흐름 (지역 변수, 매개변수 복사, return)"
date: 2026-10-11 22:40:00 +0900
description: "Update 안 변수가 매번 초기화되는 이유, Start에서 넣은 값이 사라지는 함정, 매개변수 복사와 조기 반환까지. 변수의 범위로 기초 코스를 마무리한다."
series: 유니티 C# 일주일
series_title: "기초 Day 8: 변수의 범위와 함수의 흐름"
categories: [게임 제작 공부, 유니티]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

[Day 7](/posts/csharp-week-basic-day7/)에서 코인 줍기 게임을 완성했다. 기초 코스의 마지막 날은 새 기능 대신, 지금까지 써 온 변수와 함수가 **실제로 어떻게 동작하는지** 다진다. "분명 더했는데 왜 계속 1이지?", "Start에서 넣었는데 왜 Update에서 없다고 하지?" 같은, 초보 때 반드시 한 번은 만나는 버그들이 여기서 풀린다.

**오늘의 목표**

- 변수가 어디서 태어나고 언제 사라지는지(범위) 안다
- 함수에 값을 넘기면 복사된다는 걸 안다
- `return`으로 함수를 중간에 끝내는 "조기 반환"을 쓸 수 있다

## 1. 중괄호는 변수의 집
{:.briefing-heading}

```csharp
public class Player : MonoBehaviour
{
    int coin = 0;          // ① 클래스의 집: 스크립트가 살아 있는 동안

    void Update()
    {
        int temp = 5;      // ② Update의 집: 이번 프레임 동안만

        if (coin > 10)
        {
            int bonus = 2; // ③ if의 집: 이 중괄호 안에서만
        }
        // 여기서 bonus는 없다
    }
}
```

변수는 **자기가 태어난 중괄호 안에서만** 산다. 중괄호가 닫히면 사라진다. 이걸 **범위(scope)**라고 한다.

| 어디서 태어났나 | 이름 | 언제까지 사나 |
|---|---|---|
| 클래스 바로 아래 | **필드** | 스크립트(컴포넌트)가 있는 동안 계속 |
| 함수 안 | **지역 변수** | 함수가 끝나면 사라짐 |
| if, for의 중괄호 안 | 블록 변수 | 그 블록이 끝나면 사라짐 |

### 초보 단골 버그 1: 매번 1이 나와요

```csharp
void Update()
{
    int count = 0;

    if (Input.GetKeyDown(KeyCode.Space))
    {
        count++;
        Debug.Log(count);   // 항상 1
    }
}
```

스페이스를 누를 때마다 1, 2, 3… 이 되길 바랐는데 항상 1이 나온다. count가 Update 안에서 태어났기 때문이다. Update는 매 프레임 새로 실행되니까, count도 **매 프레임 0으로 새로 태어난다.**

계속 기억해야 하는 값은 함수 밖, 클래스의 칸(필드)에 둔다.

```csharp
int count = 0;   // 필드

void Update()
{
    if (Input.GetKeyDown(KeyCode.Space))
    {
        count++;
        Debug.Log(count);   // 1, 2, 3 ...
    }
}
```

### 초보 단골 버그 2: Start에서 넣었는데 Update에서 없어요

```csharp
void Start()
{
    Rigidbody rb = GetComponent<Rigidbody>();
}

void Update()
{
    rb.AddForce(Vector3.up);   // 에러: rb가 없다
}
```

rb가 Start 안에서 태어나서 Start가 끝날 때 사라졌다. 그래서 Update에서는 "rb라는 건 없다"는 빨간 에러가 뜬다.

고치려면 클래스의 칸에 `Rigidbody rb;`를 만들고, Start에서는 **자료형 없이** `rb = ...`만 쓴다.

```csharp
Rigidbody rb;            // 필드

void Start()
{
    rb = GetComponent<Rigidbody>();   // 자료형 없이!
}
```

여기서 함정이 하나 더 있다. 필드를 만들어 놓고도 Start에서 `Rigidbody rb = GetComponent<Rigidbody>();`라고 **자료형을 다시 쓰면**, 같은 이름의 지역 변수가 새로 생긴다. 값은 그 지역 변수에 들어가고 Start가 끝나면 사라진다. 필드 rb는 여전히 비어 있어서, 에러는 Update에서 터진다. 에러 난 줄만 봐서는 원인을 찾기 어려운 버그다.

## 2. 함수에 값을 넘기면 복사된다
{:.briefing-heading}

용어부터 정리한다.

```csharp
void Heal(int amount)   // amount = 매개변수 (받는 칸)
{
    hp += amount;
}

Heal(30);               // 30 = 인자 (넣는 값)
```

둘을 섞어 부르는 사람도 많아서 엄격하게 구분할 필요는 없다. "받는 칸"과 "넣는 값"이 다르다는 것만 기억하면 된다.

그럼 변수를 넘기면 무슨 일이 일어날까?

```csharp
int myHp = 50;

void AddTen(int x)
{
    x += 10;
    Debug.Log(x);    // 60
}

void Start()
{
    AddTen(myHp);
    Debug.Log(myHp); // 50 !
}
```

> **코드는 위에서 아래가 아니라, 실행되는 순서대로 읽는다.** `void AddTen(int x) { ... }`는 "이렇게 하면 된다"고 적어 둔 레시피일 뿐이라, 위에 적혀 있어도 누가 부르기 전까지는 한 줄도 실행되지 않는다. 레시피만 먼저 읽으면 "x가 뭔데?"가 안 보이는 게 당연하다. 재료는 부르는 쪽이 넣어 주기 때문이다. 그래서 유니티가 불러 주는 함수(`Start`, `Update`, `OnTriggerEnter` 등)에서 출발해 한 줄씩 따라가다가, 함수를 부르는 줄을 만나면 그 함수로 들어가 읽고, 끝나면 부른 자리로 돌아와 다음 줄을 읽는다.
{: .prompt-tip }

이 순서로 따라가 보면 이렇다. Start의 `AddTen(myHp);`가 실행되면, 괄호 안의 myHp가 지금 50이니 50을 들고 AddTen으로 들어간다. 들어가는 순간 받는 칸 `int x`에 그 50이 담긴다. 함수 맨 위에 `int x = 50;`이 숨어 있는 것과 같다. 그래서 `x += 10`으로 x가 60이 된다. Day 4의 `TakeDamage(10)`에서 amount가 10이 된 것과 같은 원리이고, 숫자 대신 변수를 넣었으니 그 안에 든 값이 들어간 것이다.

함수 안에서 x는 60이 됐는데 myHp는 50 그대로다. `AddTen(myHp)`를 부를 때 myHp **자체**가 아니라 **myHp의 값 50을 복사해서** x라는 새 상자에 넣어 주기 때문이다. 시험지를 복사해서 친구에게 주면, 친구가 복사본에 낙서해도 내 원본은 깨끗한 것과 같다.

`int`, `float`, `bool`, `Vector3` 같은 값은 이렇게 복사된다.

### 바뀐 값이 필요하면 돌려받는다

```csharp
int AddTen(int x)
{
    return x + 10;
}

void Start()
{
    myHp = AddTen(myHp);
    Debug.Log(myHp);   // 60
}
```

void 대신 int를 돌려주게 하고, 돌려받은 값을 다시 myHp에 넣는다. Day 4에서 배운 "부른 쪽이 결과를 받아 써야 하면 그 자료형"이 바로 이 경우다.

같은 클래스 안이라면 더 간단한 방법도 있다. 굳이 넘기지 말고 필드를 직접 바꾸면 된다. `hp`를 매개변수로 넘겨 함수 안에서 깎으면 복사본만 깎인다. `hp -= 10;`처럼 필드를 직접 쓰자.

> `List`나 내가 만든 클래스처럼 **값이 아닌 것**을 넘기면 결과가 다르다. 함수 안에서 바꾼 게 원본에도 보인다. 이 차이는 심화 Day 8 "값 형식과 참조 형식"에서 다룬다.
{: .prompt-info }

## 3. return과 조기 탈출
{:.briefing-heading}

`return`을 만나면 함수는 그 자리에서 끝난다. 값을 돌려주지 않는 void 함수도 `return;`으로 중간에 끝낼 수 있다.

```csharp
void TryJump()
{
    if (!isGrounded)
        return;          // 공중이면 여기서 끝

    if (stamina < 10)
        return;          // 스태미나가 부족해도 끝

    rb.AddForce(Vector3.up * 6f, ForceMode.Impulse);
    stamina -= 10;
}
```

이렇게 **안 되는 조건을 먼저 걸러내고 빠져나가는** 방식을 "조기 반환" 또는 "가드"라고 한다. 놀이기구 입구에서 키 재고, 표 확인하고, 통과한 사람만 태우는 것과 같다.

같은 일을 if 안에 if로 쓸 수도 있다.

```csharp
void TryJump()
{
    if (isGrounded)
    {
        if (stamina >= 10)
        {
            rb.AddForce(Vector3.up * 6f, ForceMode.Impulse);
            stamina -= 10;
        }
    }
}
```

하는 일은 똑같지만, 조건이 늘어날수록 중괄호가 계속 깊어진다. 조건이 다섯 개면 다섯 겹이다. 그래서 실무에서는 앞의 조기 반환 모양을 더 많이 쓴다. 함수 맨 위에 `if (isDead) return;` 한 줄을 두는 것도 아주 흔한 패턴이다.

값을 돌려주는 함수에서도 마찬가지다.

```csharp
int Clamp(int v)
{
    if (v < 0) return 0;
    if (v > 100) return 100;
    return v;
}
```

`Clamp(150)`은 두 번째 if에서 100을 돌려주며 끝난다. 참고로 유니티에는 같은 일을 하는 `Mathf.Clamp(값, 최소, 최대)`가 이미 있다.

## 직접 해 보기
{:.briefing-heading}

Day 7의 `PlayerController`에 스태미나를 넣어 보자. 점프할 때마다 스태미나 10을 쓰고, 땅에 있으면 초당 5씩 회복한다.

```csharp
[SerializeField] float maxStamina = 30f;
float stamina;   // 필드: 계속 기억해야 하니까

void Start()
{
    rb = GetComponent<Rigidbody>();
    stamina = maxStamina;
}

void Update()
{
    // ... 이동 코드는 그대로 ...

    if (Input.GetKeyDown(KeyCode.Space))   // 스페이스를 누른 프레임에만
    {
        TryJump();                         // 쓰기: 점프하면 -10
    }

    if (isGrounded)                        // 위 if와 별개: 매 프레임 검사
    {
        // 충전: 땅에 있으면 초당 5씩, 최대치는 넘지 않게
        stamina = Mathf.Min(stamina + 5f * Time.deltaTime, maxStamina);
    }
}

void TryJump()
{
    if (!isGrounded) return;
    if (stamina < 10f)
    {
        Debug.Log("스태미나 부족: " + stamina);
        return;
    }

    rb.AddForce(Vector3.up * jumpPower, ForceMode.Impulse);
    isGrounded = false;
    stamina -= 10f;
    Debug.Log("점프! 남은 스태미나 " + stamina);
}
```

기존 Update의 점프 if문은 `TryJump()` 호출로 바꾼다.

충전과 사용은 따로 일어난다. **충전은 Update에서 매 프레임** 한다. 스페이스를 안 눌러도 땅에 있으면 계속 찬다. **TryJump는 스페이스를 누른 순간에만** 불려서, 공중이거나 스태미나가 부족하면 그냥 빠져나가고, 아니면 점프하면서 10을 쓴다. 두 if를 중괄호로 나눠 둔 건 이게 서로 상관없는 별개의 if라는 걸 보이려고다. 중괄호 없이 한 줄로 쓰면 들여쓰기 때문에 한 덩어리처럼 보여 헷갈리기 쉽다.

충전 줄을 나눠 보면 이렇다.

- `if (isGrounded)`: 공중에서는 회복하지 않는다.
- `stamina + 5f * Time.deltaTime`: 이번 프레임에 채운 값. Day 5처럼 Time.deltaTime을 곱해서 "1프레임에 5"가 아니라 "1초에 5"다. 60fps면 한 프레임에 약 0.083씩 오른다.
- `Mathf.Min(a, b)`: 둘 중 **작은 값**을 돌려준다. "채운 값"과 "최대치 30" 중 작은 쪽이니, 30을 넘는 순간 30으로 잘린다.

| 상황 | 채운 값 (a) | 최대치 (b) | Min 결과 = 새 stamina |
|---|---|---|---|
| 점프 후 12 남음 | 12.083 | 30 | 12.083 (아직 작으니 그대로) |
| 약 3.6초 뒤 | 30.05 | 30 | 30 (넘었으니 잘림) |
| 그 뒤 계속 | 30.083 | 30 | 30 (계속 30에 멈춤) |

Min이 없으면 땅에 서 있는 동안 31, 32, … 1000까지 끝없이 찬다. 사실 Day 4의 Heal 함수에서 "최대 체력을 넘지 않게"로 이미 해 본 일이다. 그 모양으로 풀어 쓰면 이렇고, 이 세 줄을 한 줄로 줄인 게 `Mathf.Min`이다.

```csharp
stamina += 5f * Time.deltaTime;   // 채우고
if (stamina > maxStamina)          // 넘었으면
    stamina = maxStamina;          // 최대치로 자른다
```

최대치로 자르는데 이름이 **Min**이라 헷갈린다. "작은 쪽을 고른다 → 결과가 큰 값을 못 넘는다"라서다. 반대로 바닥을 막을 땐 Max를 쓴다. `hp = Mathf.Max(hp - 30, 0);`은 체력이 0 밑으로 안 내려가게 한다. 위아래를 한 번에 막는 `Mathf.Clamp(값, 최소, 최대)`도 있다.

해 볼 것: Update 맨 첫 줄에 `float stamina = 0f;`를 한 줄 추가하면 무슨 일이 생길까? 점프 몇 번이면 스태미나가 바닥나고, 그 뒤로는 땅에 오래 있어도 회복되지 않는다. Update 안의 회복 코드가 필드가 아니라 **새로 생긴 지역 변수**만 채우고 버리기 때문이다. TryJump는 여전히 필드를 보니 계속 "스태미나 부족"이 뜬다. 위에서 본 "자료형을 다시 쓰는 함정"을 직접 만들어 보는 것도 좋은 공부다. 확인했으면 그 줄은 지운다.

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. 같은 이름의 변수를 두 번 만들면?**<br>
같은 중괄호 안에서 두 번 만들면 에러다. 하지만 필드와 같은 이름의 지역 변수는 에러 없이 만들어진다(위의 rb 함정). 그래서 필드와 지역 변수는 이름을 다르게 짓는 게 안전하다.

**Q. for문의 `i`는 어디까지 살아?**<br>
`for (int i = 0; ...)`의 i는 for문 안에서만 산다. 그래서 for문을 두 개 연달아 쓰면서 둘 다 `i`를 써도 된다.

**Q. 함수 안에서 원본을 바꾸고 싶으면 매개변수로는 절대 안 돼?**<br>
`ref`라는 표시를 붙이면 복사 대신 원본을 넘길 수 있다. 다만 처음에는 "돌려받아서 다시 넣기"나 "필드를 직접 바꾸기"가 훨씬 읽기 쉽다. 비슷한 표시인 `out`은 실전 Day 2의 `TryGetComponent`에서 처음 만난다.

**Q. 충전 속도가 5라서 정수로 찰 줄 알았는데, 남은 스태미나가 4.538103처럼 소수로 나와.**<br>
`Time.deltaTime` 때문이다. `5f * Time.deltaTime`은 "1초에 5"를 프레임 수만큼 잘게 나눈 조각이다. 144fps면 한 프레임이 약 0.0069초라 한 번에 0.035쯤 차고, 1초가 모여야 5가 된다. 게다가 프레임 간격이 매번 조금씩 달라서 지저분한 소수가 나온다.

그래서 stamina는 **float여야 한다.** Day 1의 "소수점이 없는데 왜 float일까?"가 여기서 진짜로 필요해진다. stamina를 int로 만들면 한 프레임에 채울 0.035가 int로 바뀌면서 0이 되고, 매 프레임 0씩 차니 **영원히 안 찬다.** int끼리 나누면 소수점이 버려지던 그 함정과 같다.

화면에 보여 줄 때만 자리수를 줄이면 된다. 속은 소수로 부드럽게 채우고, 겉으로는 깔끔하게 보여 준다. 게임의 스태미나 바나 체력바가 뚝뚝 끊기지 않고 스르륵 차오르는 이유다.

```csharp
Debug.Log("남은 스태미나 " + stamina.ToString("F1"));   // 11.4 (소수 첫째 자리까지)
Debug.Log("남은 스태미나 " + stamina.ToString("F0"));   // 11 (정수처럼, 반올림)
Debug.Log("남은 스태미나 " + Mathf.FloorToInt(stamina)); // 11 (내림)
```

## 현업에서는
{:.briefing-heading}

- **필드는 꼭 필요한 것만.** 한 프레임 안에서만 쓰는 값은 지역 변수로 둔다. 필드가 많을수록 "이 값을 누가 언제 바꿨지?"를 추적하기 어려워진다.
- **필드 이름을 구분한다.** 팀에 따라 필드 앞에 `_`를 붙여 `_speed`처럼 쓰기도 한다. 위의 "자료형을 다시 써서 생기는 함정"을 눈으로 바로 알아챌 수 있다. 팀 규칙을 따르면 된다.
- **함수 맨 위에 가드.** "죽었으면 아무것도 안 함", "대상이 없으면 아무것도 안 함" 같은 검사를 함수 맨 위에 모아 두면 아래는 "정상인 경우"만 읽으면 된다.

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **기초 Day 8**과 같은 내용이다. 블록 조립 문제도 처음 나온다.

- [변수는 어디까지 살아있을까](https://hlcho426.github.io/unity-csharp-week/#c3l1): 중괄호 = 변수의 집
- [함수에 값을 넘기면 복사돼요](https://hlcho426.github.io/unity-csharp-week/#c3l2): 매개변수와 인자
- [return과 조기 탈출](https://hlcho426.github.io/unity-csharp-week/#c3l3): 함수의 흐름 읽기

## 정리
{:.briefing-heading}

- 변수는 만들어진 `{ }` 안에서만 산다. 함수 안 변수는 함수가 끝나면 사라진다
- Update 안에서 만든 변수는 매 프레임 새로 태어난다. 계속 기억할 값은 필드에
- 필드에 담으려면 자료형 없이 `rb = ...`. 자료형을 다시 쓰면 새 지역 변수가 생긴다
- `int`, `float`, `bool`, `Vector3`는 함수에 넘길 때 복사된다. 바뀐 값이 필요하면 return으로 돌려받는다
- `return`을 만나면 함수는 바로 끝난다. 안 되는 조건을 먼저 걸러내는 조기 반환이 읽기 쉽다

## 기초 코스를 마치며
{:.briefing-heading}

여기까지 왔으면 유니티 스크립트의 뼈대를 읽고, 변수·조건·반복·함수로 캐릭터를 움직이고, 코인을 줍는 작은 게임을 만들 수 있다. 다음 코스인 **심화**에서는 스크립트끼리 협업하는 구조를 배운다. 첫 글은 심화 Day 1, 클래스와 객체. `Player player`가 무슨 뜻인지, 클래스와 생성자와 메서드가 뭐가 다른지가 여기서 풀린다.
