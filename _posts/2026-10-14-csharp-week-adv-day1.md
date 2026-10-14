---
title: "<유니티 C#> 심화 Day 1: 클래스와 객체 (class, new, 생성자, 메서드)"
date: 2026-10-14 15:00:00 +0900
description: "클래스는 설계도, 객체는 찍어낸 실물. new와 생성자, 메서드, 그리고 Player player가 무슨 뜻인지까지. 함정 스크립트가 플레이어 스크립트를 불러 체력을 깎게 만든다."
series: 유니티 C# 일주일
series_title: "심화 Day 1: 클래스와 객체"
categories: [게임 제작 공부, 유니티]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

[기초 코스](/posts/csharp-week-basic-day0/)에서는 이동, 점프, 코인 줍기, 스태미나까지 `PlayerController` 스크립트 하나에 모두 넣었다. 작은 게임은 이걸로 충분하지만, 함정과 적과 UI가 생기면 스크립트 하나로는 감당이 안 된다. 심화 코스의 주제는 **스크립트끼리 협업하는 구조**다.

그 첫걸음이 클래스다. 기초 Day 0부터 매번 써 온 `public class Player : MonoBehaviour`의 `class`가 무엇인지, 다른 스크립트에서 보이는 `Player player` 같은 줄이 무슨 뜻인지가 오늘 풀린다.

**오늘의 목표**

- 클래스(설계도)와 객체(실물)의 차이를 안다
- `new`와 생성자로 객체를 만들고, 메서드로 객체에게 일을 시킬 수 있다
- 한 스크립트에서 다른 스크립트의 함수를 부를 수 있다

## 1. 클래스는 설계도, 객체는 실물
{:.briefing-heading}

게임에 몬스터가 나온다고 하자. 몬스터마다 이름과 체력이 있다. 슬라임 하나만 있으면 변수 두 개로 끝나지만, 슬라임, 고블린, 오크가 나오면 변수가 금방 여섯 개, 아홉 개로 늘어난다.

그래서 "몬스터는 이름과 체력을 가진다"는 **설계도**를 한 번 그려 두고, 그 설계도로 몬스터를 필요한 만큼 찍어낸다. 이 설계도가 **클래스**, 찍어낸 실물이 **객체**다.

```csharp
public class Monster
{
    public string name;
    public int hp;
}
```

설계도만 있으면 아직 몬스터는 한 마리도 없다. 붕어빵 틀만 있고 붕어빵은 없는 상태다. 실물은 `new`로 만든다.

```csharp
Monster a = new Monster();
a.name = "슬라임";
a.hp = 30;

Monster b = new Monster();
b.name = "고블린";
b.hp = 50;
```

`new Monster()`는 "Monster 설계도로 하나 새로 만들어 줘"라는 뜻이다. 같은 틀로 찍었어도 슬라임과 고블린은 **각자 자기 값을 따로** 가진다. 그래서 `a.hp -= 10;`을 해도 b의 체력은 50 그대로다.

가운데 점(`.`)은 "~의"라고 읽으면 된다. `a.hp`는 "a의 hp", `a.name`은 "a의 name"이다. 기초에서 쓴 `transform.position`도 "transform의 position"이었다.

### `Monster a`는 `int coin`과 같은 모양이다

```csharp
int coin = 0;
Monster a = new Monster();
```

두 줄을 나란히 놓으면 모양이 똑같다. **자료형, 이름, =, 넣을 값.** 클래스를 만든다는 건 `int`, `float` 같은 **자료형을 내가 새로 만든다**는 뜻이다. `Monster`라는 자료형이 생겼으니 `Monster` 상자를 만들 수 있다.

그래서 다른 스크립트에서 자주 보는 `Player player`는 "**Player 자료형**의 상자, 이름은 **player**"다. 앞의 대문자는 클래스 이름(자료형), 뒤의 소문자는 내가 붙인 변수 이름이다. 이름은 아무거나 붙여도 되지만, 자료형 이름을 소문자로 바꿔 붙이는 게 관례라 이런 모양이 많이 보인다.

## 2. 생성자: 만들자마자 값 채우기
{:.briefing-heading}

몬스터를 만들 때마다 `a.name = ...`, `a.hp = ...`를 줄줄이 쓰는 건 번거롭고, 한 줄 빼먹기도 쉽다. 만드는 순간 값을 넣게 하는 게 **생성자**다.

```csharp
public class Monster
{
    public string name;
    public int hp;

    public Monster(string name, int hp)
    {
        this.name = name;
        this.hp = hp;
    }
}

Monster slime = new Monster("슬라임", 30);
```

생성자는 생김새가 특이하다.

- 이름이 **클래스 이름과 똑같다** (`Monster`)
- 앞에 `void`도, `int` 같은 자료형도 **쓰지 않는다**
- `new` 할 때 **자동으로 한 번** 실행된다

`new Monster("슬라임", 30)`의 괄호 안 값들이 생성자의 매개변수 `name`, `hp`로 들어간다. 기초 Day 4에서 함수에 값을 넘기던 것과 같다.

### this는 "이 객체의"

생성자 안에 `name`이 두 개 있다. 클래스의 칸 `name`과, 괄호로 받은 매개변수 `name`. 이름이 같으면 C#은 가까운 쪽, 즉 매개변수를 가리킨다. 그래서 클래스의 칸을 가리킬 때는 앞에 `this.`를 붙인다.

```csharp
this.name = name;
// 이 객체의 name 칸에 = 괄호로 받은 name을 넣는다
```

매개변수 이름을 `n`처럼 다르게 지으면 `this` 없이 `name = n;`으로 써도 된다. 다만 같은 이름을 쓰고 `this`로 구분하는 모양이 훨씬 흔해서, 남의 코드를 읽으려면 알아 둬야 한다.

## 3. 메서드: 자기 일은 자기가
{:.briefing-heading}

클래스 안에는 값뿐 아니라 함수도 넣을 수 있다. 클래스 안의 함수를 **메서드**라고 부른다.

```csharp
public class Monster
{
    public string name;
    public int hp;

    // 생성자는 앞과 같다

    public void TakeDamage(int amount)
    {
        hp -= amount;
        if (hp < 0) hp = 0;
    }

    public bool IsDead()
    {
        return hp <= 0;
    }
}
```

```csharp
Monster m = new Monster("슬라임", 20);
m.TakeDamage(50);
Debug.Log(m.hp);        // 0
Debug.Log(m.IsDead());  // True
```

20에서 50을 빼면 -30이지만, `TakeDamage` 안의 if가 0으로 막아 준다. 체력이 음수가 되는 버그를 **몬스터 스스로** 막는 것이다. 바깥에서 `m.hp -= 50;`으로 직접 깎았다면, 깎는 곳마다 "음수면 0으로" 코드를 붙여야 했을 것이다.

메서드를 부를 때는 **객체.메서드()** 모양이다. `m.IsDead()`에서 괄호를 빼먹고 `m.IsDead`라고 쓰면 함수를 "부른" 게 아니라서 에러가 난다.

클래스 안에 들어가는 세 가지를 정리하면 이렇다.

| 이름 | 무엇 | 예 |
|---|---|---|
| 필드 | 객체가 가진 값 | `name`, `hp` |
| 생성자 | 만들 때 한 번 실행 | `Monster(string name, int hp)` |
| 메서드 | 객체가 하는 일 | `TakeDamage`, `IsDead` |

## 4. 지금까지 쓴 스크립트도 클래스였다
{:.briefing-heading}

```csharp
public class Player : MonoBehaviour { }  // 오브젝트에 붙이는 컴포넌트
public class Monster { }                 // 순수 데이터용 클래스
```

기초 코스에서 만든 스크립트도 전부 클래스였다. 차이는 뒤에 붙은 `: MonoBehaviour` 하나다. 이건 "MonoBehaviour의 기능을 물려받는다"는 표시다(물려받기, 즉 상속은 실전 Day 1에서 자세히 배운다). 물려받은 덕분에 게임 오브젝트에 붙을 수 있고, 유니티가 `Start`, `Update`, `OnTriggerEnter`를 알아서 불러 준다.

| | `: MonoBehaviour` 있음 | 없음 |
|---|---|---|
| 만드는 법 | 오브젝트에 **컴포넌트로 붙인다** | `new`로 만든다 |
| Start, Update | 유니티가 불러 준다 | 없다 |
| 쓰임 | 플레이어, 적, 함정처럼 씬에 있는 것 | 몬스터 정보, 카드 한 장 같은 데이터 묶음 |

MonoBehaviour를 `new Player()`로 만들면 안 된다. 유니티가 "MonoBehaviour는 new로 만들 수 없다"는 경고를 띄우고, 만들어진 것도 오브젝트에 붙어 있지 않아 제대로 동작하지 않는다. 컴포넌트는 Inspector의 **Add Component**나 코드의 `AddComponent<Player>()`로 붙인다.

## 5. 다른 스크립트와 대화하기
{:.briefing-heading}

이제 오늘의 진짜 목적이다. 바닥에 함정이 있고, 플레이어가 밟으면 체력이 깎인다고 하자. 체력은 플레이어 스크립트에, 밟았는지 감지는 함정 스크립트에 있다. 함정이 플레이어에게 "10 깎아"라고 말하려면 어떻게 할까?

```csharp
// Player.cs
public class Player : MonoBehaviour
{
    int hp = 100;

    public void TakeDamage(int amount)
    {
        hp -= amount;
    }
}

// Trap.cs
public class Trap : MonoBehaviour
{
    [SerializeField] Player player;

    void OnTriggerEnter(Collider other)
    {
        player.TakeDamage(10);
    }
}
```

Trap에 `Player` 자료형의 칸 `player`를 만든다. `[SerializeField]`가 붙어 있으니 Inspector에 **Player** 칸이 생긴다. 여기에 Hierarchy의 플레이어 오브젝트를 **끌어다 놓으면** 연결된다. 그다음부터 `player.TakeDamage(10)`으로 플레이어의 메서드를 부를 수 있다.

> **이 칸에 들어 있는 건 플레이어의 복사본이 아니다.** 씬에 있는 바로 그 플레이어를 **가리키는 표지판**이다. 그래서 TakeDamage를 부르면 진짜 플레이어의 체력이 줄어든다. 왜 복사가 아니라 가리키기인지는 심화 Day 8 "값 형식과 참조 형식"에서 정리한다.
{: .prompt-info }

### public이어야 밖에서 부를 수 있다

`TakeDamage` 앞의 `public`을 지우면 Trap에서 빨간 에러가 난다. 기초 Day 5에서 봤듯이 아무것도 안 쓰면 `private`, 즉 **그 클래스 안에서만** 쓸 수 있기 때문이다. 다른 스크립트가 불러야 하는 메서드만 `public`으로 연다.

### 연결을 빼먹으면 NullReferenceException

Inspector에서 Player 칸에 아무것도 안 끌어다 놓고 함정을 밟으면 `NullReferenceException`이 뜬다. 칸이 비어 있으면(null) 가리키는 플레이어가 없는데 TakeDamage를 부르려고 했기 때문이다. 유니티에서 가장 많이 만나는 에러이고, 열에 아홉은 "칸 연결을 안 했다"가 원인이다.

### 더 좋은 방법: 닿은 상대에게서 꺼내기

함정이 10개면 10개마다 플레이어를 끌어다 놓아야 한다. 귀찮고 빼먹기 쉽다. 그런데 함정은 이미 "누가 밟았는지"를 안다. `OnTriggerEnter`의 `other`다.

```csharp
void OnTriggerEnter(Collider other)
{
    Player p = other.GetComponent<Player>();
    if (p != null)
    {
        p.TakeDamage(10);
    }
}
```

닿은 상대의 오브젝트에서 `Player` 컴포넌트를 꺼낸다. 기초 Day 5의 `GetComponent<Rigidbody>()`와 같은 함수인데, 앞에 `other.`를 붙여서 **내 오브젝트가 아니라 상대 오브젝트에서** 찾는다. 내가 만든 스크립트도 컴포넌트라서 이렇게 꺼낼 수 있다.

적이나 돌멩이가 밟았다면 Player 컴포넌트가 없으니 null이 돌아온다. 그래서 `if (p != null)`로 확인하고 부른다. 이러면 함정마다 연결할 필요가 없다.

### hp를 public으로 열면 안 될까?

`hp`를 public으로 열고 Trap에서 `player.hp -= 10;`이라고 써도 동작은 한다. 그런데 나중에 "맞으면 1초 무적", "방어력만큼 덜 깎임" 같은 규칙이 생기면? hp를 직접 깎는 곳이 함정, 적, 총알, 독 장판에 흩어져 있으면 그곳을 전부 고쳐야 한다. `TakeDamage` 하나로 모아 두면 그 안만 고치면 된다. **자기 값은 자기 메서드로**. 앞의 Monster에서 본 것과 같은 원리다.

## 직접 해 보기
{:.briefing-heading}

기초 코스의 코인 줍기 씬에서 이어서 한다.

### A. 순수 클래스 만들어 보기

1. Project 창에서 스크립트를 하나 만들고 이름을 `Monster`로 한다. 메뉴는 기초 Day 0과 같은 **Create → Scripting → MonoBehaviour Script**를 써도 된다. 어차피 내용을 통째로 바꾼다.
2. 내용을 지우고 아래로 바꾼다. `: MonoBehaviour`가 없다는 점에 주의한다.

```csharp
public class Monster
{
    public string name;
    public int hp;

    public Monster(string name, int hp)
    {
        this.name = name;
        this.hp = hp;
    }

    public void TakeDamage(int amount)
    {
        hp -= amount;
        if (hp < 0) hp = 0;
    }

    public bool IsDead()
    {
        return hp <= 0;
    }
}
```

3. 이 클래스는 오브젝트에 붙일 수 없으니, 시험할 스크립트를 따로 만든다. `MonsterTest` 스크립트를 만들고 Hierarchy에 **Create Empty**로 빈 오브젝트를 하나 만들어 붙인다.

```csharp
using UnityEngine;

public class MonsterTest : MonoBehaviour
{
    void Start()
    {
        Monster slime = new Monster("슬라임", 30);
        Monster goblin = new Monster("고블린", 50);

        slime.TakeDamage(50);

        Debug.Log(slime.name + " 체력 " + slime.hp + ", 쓰러졌나? " + slime.IsDead());
        Debug.Log(goblin.name + " 체력 " + goblin.hp);
    }
}
```

플레이하면 콘솔에 이렇게 찍힌다.

```text
슬라임 체력 0, 쓰러졌나? True
고블린 체력 50
```

슬라임만 맞았고 고블린은 그대로다. 객체마다 값이 따로라는 게 눈으로 보인다. bool을 글자와 더하면 `True`/`False`로 찍힌다.

해 볼 것: MonsterTest의 Start에 `Monster orc = new Monster();`처럼 괄호 안을 비운 줄을 하나 넣어 보자. 빨간 에러가 난다. 이유는 아래 "자주 헷갈리는 것"에 있다. 확인했으면 MonsterTest 오브젝트는 지우거나 꺼 둔다.

### B. 함정이 플레이어 체력 깎기

이번엔 MonoBehaviour끼리 대화한다. 체력은 이동과 다른 역할이니 `PlayerController`에 넣지 않고 새 스크립트로 나눈다.

1. `PlayerHealth` 스크립트를 만들어 플레이어 큐브에 붙인다.

```csharp
using UnityEngine;

public class PlayerHealth : MonoBehaviour
{
    [SerializeField] int maxHp = 100;
    int hp;

    void Start()
    {
        hp = maxHp;
    }

    public void TakeDamage(int amount)
    {
        if (hp <= 0) return;   // 이미 쓰러졌으면 무시

        hp -= amount;
        if (hp < 0) hp = 0;
        Debug.Log("아야! 남은 체력 " + hp);

        if (hp == 0)
        {
            Debug.Log("게임 오버");
        }
    }
}
```

맨 위의 `if (hp <= 0) return;`은 기초 Day 8의 조기 반환이다. 이미 쓰러졌는데 또 맞아서 "게임 오버"가 여러 번 찍히는 걸 막는다.

2. **3D Object → Cube**로 함정을 만든다. 이름은 `Trap`, Scale은 (1.5, 0.1, 1.5), 위치는 바닥 위 Y = 0.05쯤에 둔다. Box Collider의 **Is Trigger**를 켠다. 눈에 띄게 빨간 머티리얼을 입혀도 좋다.
3. `Trap` 스크립트를 만들어 함정에 붙인다. 먼저 **끌어다 놓는 버전**이다.

```csharp
using UnityEngine;

public class Trap : MonoBehaviour
{
    [SerializeField] PlayerHealth player;
    [SerializeField] int damage = 30;

    void OnTriggerEnter(Collider other)
    {
        player.TakeDamage(damage);
    }
}
```

4. 함정을 선택하면 Inspector에 **Player** 칸이 보인다. Hierarchy의 플레이어 큐브를 그 칸에 끌어다 놓는다. 칸에 `Player (PlayerHealth)`처럼 표시되면 연결된 것이다.
5. 플레이해서 함정을 밟아 본다. "아야! 남은 체력 70"이 찍히면 성공이다. 네 번 밟으면 "게임 오버"가 나온다.

이제 **Ctrl + D**로 함정을 하나 복제해 보자. 복제하면 칸 연결까지 복사되지만, 함정을 새로 만들 때마다 매번 끌어다 놓아야 한다는 건 변함없다. 복제한 함정의 Player 칸을 비워 보자. 칸 오른쪽의 동그라미 버튼을 눌러 **None**을 고르면 된다. 그리고 그 함정을 밟으면 `NullReferenceException`이 뜬다. 칸 연결을 빼먹으면 이렇게 된다는 걸 한 번 겪어 두면, 나중에 이 에러를 봤을 때 가장 먼저 Inspector를 확인하게 된다.

6. 이제 **닿은 상대에게서 꺼내는 버전**으로 바꾼다.

```csharp
using UnityEngine;

public class Trap : MonoBehaviour
{
    [SerializeField] int damage = 30;

    void OnTriggerEnter(Collider other)
    {
        PlayerHealth health = other.GetComponent<PlayerHealth>();
        if (health != null)
        {
            health.TakeDamage(damage);
        }
    }
}
```

Player 칸이 사라졌다. 함정을 몇 개를 복제해도 연결할 게 없다.

> 함정 Collider가 Trigger인데 플레이어의 `OnTriggerEnter`(코인 줍기)도 같이 불린다. 플레이어 쪽은 `CompareTag("Coin")`으로 코인인지 확인하니 함정에는 반응하지 않는다. 한 번 닿으면 **양쪽 스크립트 모두** OnTriggerEnter가 불린다는 것도 알아 두자.
{: .prompt-tip }

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. 생성자를 만들었더니 `new Monster()`가 에러가 나.**<br>
생성자를 하나도 안 만들면 C#이 "괄호 안이 빈 생성자"를 몰래 하나 만들어 준다. 그래서 1번 예제의 `new Monster()`가 됐던 것이다. 그런데 `Monster(string name, int hp)`처럼 생성자를 직접 만드는 순간, 그 몰래 만든 빈 생성자는 사라진다. 이제 Monster를 만들려면 이름과 체력을 꼭 넣어야 한다. 둘 다 쓰고 싶으면 빈 생성자 `public Monster() { }`도 직접 하나 더 만든다.

**Q. MonoBehaviour에도 생성자를 써도 돼?**<br>
쓰지 않는다. MonoBehaviour는 유니티가 직접 만들기 때문에, 생성자가 언제 몇 번 불릴지 보장이 없다. 준비 작업은 생성자 대신 `Awake`나 `Start`에 쓴다. 둘의 차이는 다지기 Day 4에서 다룬다.

**Q. 객체랑 인스턴스는 다른 거야?**<br>
같은 말이다. "Monster 클래스의 인스턴스"는 "Monster 설계도로 찍어낸 객체"다. 유니티 문서에서는 인스턴스라는 말을 더 자주 쓴다. 심화 Day 3의 `Instantiate`도 "인스턴스로 만든다"는 뜻이다.

**Q. 파일 이름과 클래스 이름이 꼭 같아야 해?**<br>
MonoBehaviour는 **반드시** 같아야 한다. 다르면 오브젝트에 붙이려고 할 때 "스크립트 클래스를 찾을 수 없다"는 창이 뜨고 붙지 않는다. 순수 클래스는 달라도 동작하지만, 찾기 쉽도록 같게 맞추는 게 좋다.

**Q. `this`는 언제 꼭 써야 해?**<br>
필드와 매개변수 이름이 같아서 구분해야 할 때만 꼭 필요하다. 이름이 겹치지 않으면 `hp -= amount;`처럼 그냥 써도 이 객체의 hp를 가리킨다.

**Q. `other.GetComponent<PlayerHealth>()`가 null이 나와.**<br>
PlayerHealth가 Collider와 **같은 오브젝트**에 붙어 있는지 본다. GetComponent는 그 오브젝트만 뒤진다. 캐릭터 모델이 자식 오브젝트로 들어가 있고 Collider가 자식에 붙어 있으면, 부모의 스크립트를 못 찾는다. 이럴 땐 부모 쪽을 찾는 `GetComponentInParent`를 쓴다.

## 현업에서는
{:.briefing-heading}

- **스크립트 하나에 역할 하나.** 이동은 `PlayerController`, 체력은 `PlayerHealth`처럼 나눈다. 체력 버그면 PlayerHealth만 열면 된다. 한 파일이 수백 줄이 되면 나눌 때가 됐다는 신호다.
- **필드는 private, 일은 public 메서드로.** 다른 스크립트가 값을 직접 바꾸지 못하게 하고, `TakeDamage`, `Heal`처럼 정해진 문으로만 바꾸게 한다. 이렇게 안을 감추고 문만 열어 두는 걸 **캡슐화**라고 부른다.
- **연결 방법은 상황에 따라 고른다.** 씬에 하나뿐인 대상(카메라, 특정 문)은 Inspector에서 끌어다 놓고, 닿은 상대처럼 그때그때 달라지는 대상은 `GetComponent`로 꺼낸다. 실전 Day 2에서는 컴포넌트가 있는지 확인과 꺼내기를 한 번에 하는 `TryGetComponent`도 배운다.
- **순수 클래스는 데이터 묶음에 쓴다.** 인벤토리의 아이템 한 칸, 대화 한 줄, 퀘스트 하나처럼 씬에 붙을 필요가 없는 것들이다. 세이브 데이터도 순수 클래스로 만든다(심화 Day 7).

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **심화 Day 1**과 같은 내용이다.

- [클래스는 설계도](https://hlcho426.github.io/unity-csharp-week/#a1l1): class, new, 객체
- [생성자와 메서드](https://hlcho426.github.io/unity-csharp-week/#a1l2): 만들 때 값 넣기, 클래스 안의 함수
- [다른 스크립트와 대화하기](https://hlcho426.github.io/unity-csharp-week/#a1l3): 참조 연결, public 메서드

## 정리
{:.briefing-heading}

- 클래스 = 설계도, 객체 = `new`로 찍어낸 실물. 객체마다 값을 따로 가진다
- 클래스를 만들면 새 자료형이 생긴다. `Player player`는 "Player 자료형의 상자 player"
- 생성자는 클래스와 이름이 같고 void를 안 쓴다. `new` 할 때 한 번 실행된다. `this.name`은 이 객체의 name
- 클래스 안의 함수가 메서드. 자기 값은 자기 메서드로 다룬다
- `: MonoBehaviour`가 붙은 클래스는 new 대신 오브젝트에 붙인다
- 다른 스크립트를 부르려면 그 자료형의 칸을 만들어 연결하거나, `other.GetComponent<타입>()`으로 꺼낸다. 부를 메서드는 public

다음 글은 심화 Day 2, 코루틴. "3초 뒤에", "0.1초 간격으로 깜빡깜빡"처럼 시간차가 있는 동작을 만든다. 오늘 만든 PlayerHealth에 맞으면 깜빡이는 무적 시간을 붙인다.
