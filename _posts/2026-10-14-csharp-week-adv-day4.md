---
title: "<유니티 C#> 심화 Day 4: 상태 머신으로 적 AI 만들기 (enum, switch, ChangeState)"
date: 2026-10-14 15:12:00 +0900
description: "bool 깃발이 늘어날수록 생기는 모순을 enum 하나로 없애고, switch로 상태마다 할 일을 나눈다. 대기, 추격, 공격을 오가는 적을 만든다."
series: 유니티 C# 일주일
series_title: "심화 Day 4: 상태 머신"
categories: [게임 제작 공부, 유니티]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

[Day 3](/posts/csharp-week-adv-day3/)까지 함정과 코인이 생겼다. 오늘은 적이다. 가만히 있다가, 플레이어가 다가오면 쫓아오고, 가까워지면 공격한다. 기획서로 치면 이런 표다.

| 상태 | 하는 일 | 다음 상태로 가는 조건 |
|---|---|---|
| 대기 | 가만히 있는다 | 플레이어가 5m 안 → 추격 |
| 추격 | 플레이어 쪽으로 걷는다 | 1.5m 안 → 공격, 7m 밖 → 대기 |
| 공격 | 1초마다 때린다 | 2m 밖 → 추격 |

캐릭터는 늘 이 중 **딱 하나의 상태**에 있다. 이렇게 "지금 어느 상태인지"와 "언제 다른 상태로 넘어가는지"로 동작을 짜는 구조를 **상태 머신**이라고 부른다. 적 AI, 플레이어 조작, 보스 패턴, 게임 흐름(타이틀 → 플레이 → 결과)까지 게임 곳곳에서 쓴다. 오늘은 이걸 코드로 옮긴다.

**오늘의 목표**

- `enum`으로 상태 목록을 만들 수 있다
- `switch`로 상태마다 다른 일을 시킬 수 있다
- 상태 전환을 한 함수(`ChangeState`)로 모을 수 있다

## 1. bool이 너무 많아지면
{:.briefing-heading}

지금까지 배운 것으로 상태를 표현하면 bool 깃발 여러 개가 된다.

```csharp
bool isIdle;
bool isMoving;
bool isAttacking;
bool isHit;
```

문제는 이 넷이 **동시에 true가 될 수 있다**는 것이다. 공격을 시작할 때 `isAttacking = true`는 했는데 `isMoving = false`를 깜빡하면, "걸으면서 공격하는 중"이라는 말이 안 되는 상태가 생긴다. 깃발이 넷이면 조합이 16가지인데 말이 되는 건 네 가지뿐이다. 나머지 12가지가 전부 버그 후보다.

## 2. enum: 이름 붙은 선택지
{:.briefing-heading}

```csharp
public enum State
{
    Idle,
    Move,
    Attack,
    Hit
}

State state = State.Idle;   // 지금 상태

state = State.Attack;              // 바꾸기
if (state == State.Attack) { }     // 확인하기
```

`enum`은 **정해진 선택지 목록에 이름을 붙인 자료형**이다. `State`라는 자료형을 새로 만들었고, 이 자료형의 변수에는 Idle, Move, Attack, Hit 중 **딱 하나**만 들어갈 수 있다. 공격으로 바꾸는 순간 대기는 저절로 아니게 된다. 모순이 구조적으로 불가능해진다.

값을 쓸 때는 **enum이름.값** 모양이다. `State.Move`처럼. 그냥 `Move`라고 쓰면 무엇의 Move인지 몰라서 에러가 난다.

### string으로 하면 안 될까?

`string state = "Attack";`으로도 비슷하게 할 수 있다. 하지만 어딘가에서 `"attack"`이나 `"Atack"`으로 쓰면 컴파일러는 그냥 다른 글자로 보고 넘어간다. 에러 없이 조용히 틀리는 버그다. enum은 `State.Atack`이라고 쓰는 순간 빨간 에러가 난다. 그래서 요일, 무기 종류, 아이템 등급처럼 **정해진 목록**은 enum으로 만든다.

```csharp
public enum Rarity { Common, Rare, Epic, Legendary }
```

### enum은 Inspector에서 드롭다운이 된다

```csharp
[SerializeField] Rarity rarity = Rarity.Common;
```

이렇게 꺼내 두면 Inspector에 목록에서 고르는 드롭다운이 생긴다. 숫자나 글자를 손으로 치는 것보다 실수가 없다. `Debug.Log(rarity);`로 찍으면 `Common`처럼 이름이 그대로 나온다.

## 3. switch: 상태마다 할 일 나누기
{:.briefing-heading}

상태가 정해졌으면, 상태마다 다른 일을 시킨다. if / else if로도 되지만 값에 따라 갈래를 나눌 때는 `switch`가 깔끔하다.

```csharp
void Update()
{
    switch (state)
    {
        case State.Idle:
            UpdateIdle();
            break;
        case State.Move:
            UpdateMove();
            break;
        case State.Attack:
            UpdateAttack();
            break;
    }
}
```

`switch (값)`의 값과 같은 `case`를 찾아서 그 아래를 실행하고, `break`에서 switch 밖으로 나간다. state가 Move면 `UpdateMove()` 하나만 실행된다.

같은 일을 if로 쓰면 이렇다.

```csharp
if (state == State.Idle)
    UpdateIdle();
else if (state == State.Move)
    UpdateMove();
else if (state == State.Attack)
    UpdateAttack();
```

하는 일은 같다. 상태가 많아질수록 switch 쪽이 "갈래 목록"처럼 한눈에 들어온다. 그리고 공격 버그면 `UpdateAttack`만 열어 보면 된다. 상태별 코드가 서로 섞이지 않는 게 이 구조의 진짜 장점이다.

### break는 꼭, 나머지는 default

```csharp
switch (state)
{
    case State.Idle:
        UpdateIdle();
        break;      // 꼭 필요

    default:        // 어느 case에도 안 맞으면
        Debug.Log("모르는 상태: " + state);
        break;
}
```

C#에서는 case마다 `break`가 꼭 있어야 한다. 빼먹으면 **컴파일 에러**다. 다른 언어 중에는 break를 빼먹으면 조용히 다음 case까지 실행해 버려서 버그를 만드는 언어도 있는데, C#은 그 실수를 아예 막아 준다.

`default:`는 어느 case에도 맞지 않을 때 실행된다. 나중에 State에 `Stun`을 추가하고 case를 깜빡했을 때, default의 로그가 알려 준다.

## 4. 상태 전환 규칙
{:.briefing-heading}

### 상태를 바꾸는 문은 하나로

공격 상태에 들어갈 때는 공격 애니메이션을 틀고, 피격 상태에 들어갈 때는 깜빡여야 한다고 하자. 코드 여기저기서 `state = State.Attack;`을 직접 쓰면, 그중 한 곳에서 애니메이션 재생을 빼먹기 쉽다. 그래서 **모든 전환을 함수 하나로** 모은다.

```csharp
void ChangeState(State next)
{
    if (state == next) return;   // 이미 그 상태면 무시

    state = next;

    // 들어갈 때 할 일
    if (next == State.Attack)
        anim.SetTrigger("Attack");
    else if (next == State.Hit)
        StartCoroutine(Blink());
}
```

이제 상태를 바꿀 때는 늘 `ChangeState(State.Attack)`을 부른다. "들어갈 때 할 일"은 이 함수에만 있으니 빠질 수가 없다. (`anim.SetTrigger`는 애니메이션에 신호를 보내는 코드로, 실전 Day 5에서 배운다.)

맨 위의 `if (state == next) return;`은 기초 Day 8의 가드다. 공격 상태에서 매 프레임 `ChangeState(State.Attack)`이 불려도, 이미 공격 중이면 바로 빠져나간다. 이 줄이 없으면 공격 애니메이션이 매 프레임 처음부터 다시 시작돼서 영원히 첫 동작만 반복한다.

### 전환 조건은 각 상태 안에서

```csharp
[SerializeField] Transform player;   // 플레이어를 끌어다 놓은 칸

void UpdateIdle()
{
    float dist = Vector3.Distance(transform.position, player.position);
    if (dist < 5f)
        ChangeState(State.Move);
}

void UpdateMove()
{
    // 플레이어 쪽으로 이동...
    float dist = Vector3.Distance(transform.position, player.position);
    if (dist < 1.5f)
        ChangeState(State.Attack);
}
```

`Vector3.Distance(a, b)`는 두 위치 사이의 거리를 float 하나로 돌려준다.

대기 상태에서는 "5m 안에 왔나"만, 이동 상태에서는 "1.5m 안에 왔나"만 검사한다. 그래서 대기 중인 적에게 플레이어가 3m까지 다가오면, 공격이 아니라 **추격**이 먼저 시작된다. 공격 검사는 이동 상태 안에 있으니까. 글 맨 위의 기획 표가 그대로 코드가 됐다. 표의 "다음 상태로 가는 조건" 칸이 각 Update 함수의 if다.

### 어느 상태에서든 넘어가는 전환

"맞으면 어떤 상태든 피격으로"처럼 상태와 상관없는 규칙도 있다. 이걸 모든 case에 복사해 넣으면 안 된다. 그 일이 일어나는 **순간**에 전환한다.

```csharp
public void TakeDamage(int amount)
{
    hp -= amount;
    ChangeState(State.Hit);
}
```

## 직접 해 보기
{:.briefing-heading}

대기, 추격, 공격을 오가는 적을 만든다. 상태가 눈에 보이게 색도 바꾼다. 대기는 흰색, 추격은 노란색, 공격은 빨간색.

1. **3D Object → Capsule**을 만들고 이름을 `Enemy`로 한다. 플레이어에서 8m쯤 떨어진 곳(예: X = 0, Y = 1, Z = 8)에 둔다. Capsule은 높이가 2라서 Y = 1이면 바닥에 선다.
2. `Enemy` 스크립트를 만들어 붙인다.

```csharp
using UnityEngine;

public class Enemy : MonoBehaviour
{
    public enum State
    {
        Idle,
        Chase,
        Attack
    }

    [SerializeField] PlayerHealth player;
    [SerializeField] float moveSpeed = 2f;
    [SerializeField] float chaseRange = 5f;
    [SerializeField] float attackRange = 1.5f;
    [SerializeField] int attackDamage = 10;
    [SerializeField] float attackCooldown = 1f;

    // 지금 상태 (Inspector에서 보기용)
    [SerializeField] State state = State.Idle;

    float nextAttackTime = 0f;
    Renderer rend;

    void Start()
    {
        rend = GetComponent<Renderer>();
    }

    void Update()
    {
        float dist = Vector3.Distance(transform.position, player.transform.position);

        switch (state)
        {
            case State.Idle:
                UpdateIdle(dist);
                break;
            case State.Chase:
                UpdateChase(dist);
                break;
            case State.Attack:
                UpdateAttack(dist);
                break;
        }
    }

    void UpdateIdle(float dist)
    {
        if (dist < chaseRange)
            ChangeState(State.Chase);
    }

    void UpdateChase(float dist)
    {
        Vector3 target = player.transform.position;
        target.y = transform.position.y;   // 높이는 내 높이 그대로
        transform.position = Vector3.MoveTowards(transform.position, target, moveSpeed * Time.deltaTime);

        if (dist < attackRange)
            ChangeState(State.Attack);
        else if (dist > chaseRange + 2f)
            ChangeState(State.Idle);       // 충분히 멀어지면 포기
    }

    void UpdateAttack(float dist)
    {
        if (dist > attackRange + 0.5f)
        {
            ChangeState(State.Chase);
            return;
        }

        if (Time.time >= nextAttackTime)
        {
            player.TakeDamage(attackDamage);
            nextAttackTime = Time.time + attackCooldown;
        }
    }

    void ChangeState(State next)
    {
        if (state == next) return;

        Debug.Log(name + ": " + state + " → " + next);
        state = next;

        switch (next)
        {
            case State.Idle:
                rend.material.color = Color.white;
                break;
            case State.Chase:
                rend.material.color = Color.yellow;
                break;
            case State.Attack:
                rend.material.color = Color.red;
                break;
        }
    }
}
```

3. Enemy의 **Player** 칸에 Hierarchy의 플레이어 큐브를 끌어다 놓는다. 칸의 자료형이 PlayerHealth라서, PlayerHealth가 붙은 오브젝트만 들어간다.
4. 플레이한다. 적에게 다가가면 노랗게 변하며 쫓아오고, 붙으면 빨갛게 변해 1초마다 체력을 깎는다. 맞을 때마다 Day 2의 깜빡임도 나온다. 대시(E)로 멀리 도망치면 다시 노란색, 더 멀어지면 흰색으로 돌아가 멈춘다. 콘솔에는 `Enemy: Idle → Chase`처럼 전환이 찍힌다.

플레이 중에 Inspector의 **State** 칸을 보자. 상태가 바뀔 때마다 드롭다운 값이 같이 바뀐다. 상태 머신을 만들 때 이렇게 지금 상태를 보이게 해 두면 디버깅이 훨씬 쉽다.

### 코드 읽기

- **`player.transform.position`**: player 칸의 자료형은 PlayerHealth다. 그런데 컴포넌트라면 어떤 것이든 `.transform`, `.gameObject`로 **자기가 붙은 오브젝트의** Transform과 오브젝트에 갈 수 있다. 그래서 칸 하나로 체력(TakeDamage)과 위치를 둘 다 쓴다.
- **dist를 Update에서 한 번만 구한다**: 세 상태가 모두 거리를 쓰니 Update 맨 위에서 한 번 구해 매개변수로 넘긴다.
- **`Vector3.MoveTowards(현재, 목표, 최대 거리)`**: 현재 위치에서 목표 쪽으로 최대 거리만큼 다가간 위치를 돌려준다. 목표를 지나치지 않는다. 최대 거리에 `moveSpeed * Time.deltaTime`을 넣었으니 1초에 2m씩 다가간다.
- **`target.y = transform.position.y;`**: 플레이어가 점프해도 적이 따라 떠오르지 않게, 목표 위치의 높이만 내 높이로 바꿨다. target은 플레이어 위치를 **복사해 온 값**이라서, 이걸 바꿔도 플레이어는 꿈쩍하지 않는다. 왜 그런지는 심화 Day 8에서 정리한다.
- **쿨타임은 시각 비교**: 공격은 Day 2의 `Time.time` 방식을 썼다.

### 왜 들어갈 때와 나올 때 거리가 다를까

추격 시작은 5m 안인데, 포기는 7m 밖이다. 공격 시작은 1.5m 안인데, 공격 해제는 2m 밖이다. 같은 숫자로 하면 어떻게 될까?

포기 거리를 5m로 하면, 플레이어가 딱 5m 근처에 서 있을 때 거리가 4.99, 5.01, 4.99…로 미세하게 흔들리면서 **추격과 대기를 매 프레임 오간다.** 색이 노랑-흰색으로 번쩍거리고 콘솔이 전환 로그로 도배된다. 들어가는 문턱과 나오는 문턱 사이에 여유를 두면 이런 떨림이 없어진다. 해 볼 것: `chaseRange + 2f`를 `chaseRange`로 바꾸고 5m 경계에서 서성여 보자. 확인했으면 되돌린다.

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. enum을 클래스 안에 써? 밖에 써?**<br>
둘 다 된다. 위처럼 **안에** 쓰면 Enemy 전용 State가 되고, 밖에서는 `Enemy.State.Chase`로 부른다. 플레이어에도 State를 만들 때 이름이 안 부딪힌다. 여러 스크립트가 같이 쓰는 목록(아이템 등급 같은)은 클래스 **밖**에 쓴다.

**Q. case 여러 개에서 같은 일을 하고 싶어.**<br>
case를 내용 없이 연달아 쓰면 묶인다. 이건 break를 빼먹은 게 아니라 "이 두 경우 모두"라는 뜻이라 에러가 아니다.

```csharp
switch (state)
{
    case State.Idle:
    case State.Chase:
        canTalk = true;
        break;
    case State.Attack:
        canTalk = false;
        break;
}
```

**Q. 적이 플레이어를 밀고 들어와.**<br>
공격 거리(1.5m)가 너무 짧으면 붙을 때까지 걸어온다. 캡슐과 큐브가 닿는 거리는 대략 1m다. attackRange를 그보다 넉넉하게 잡는다.

**Q. 적이 공중으로 떠올라.**<br>
`target.y = transform.position.y;` 줄을 빼먹었는지 본다. 이 줄이 없으면 플레이어가 점프할 때 목표도 위로 올라가서, 적이 하늘로 걸어간다.

**Q. 플레이어가 쓰러져도 적이 계속 빨간색으로 때려.**<br>
PlayerHealth의 `if (hp <= 0) return;` 가드 덕분에 체력은 더 안 깎이지만, 적은 플레이어가 쓰러진 걸 모른다. 적이 "플레이어가 쓰러졌다"는 소식을 듣게 하는 방법이 다음 글의 이벤트다.

## 현업에서는
{:.briefing-heading}

- **코드보다 표와 그림을 먼저.** 상태 이름, 상태마다 하는 일, 전환 조건을 글 맨 위 같은 표나 동그라미-화살표 그림으로 먼저 그린다. 기획자와 프로그래머가 같은 그림을 보며 이야기할 수 있고, 빠진 전환("공격 중에 맞으면?")이 그림에서 먼저 보인다.
- **Animator도 상태 머신이다.** 유니티의 애니메이션 도구인 Animator Controller는 상태(박스)와 전환(화살표)을 그림으로 그리는 상태 머신 편집기다. 오늘 배운 구조를 알면 Animator 창이 바로 읽힌다. 실전 Day 5에서 코드와 연결한다.
- **상태가 많아지면 상태마다 클래스로 나눈다.** 보스처럼 상태가 열 개, 스무 개가 되면 switch 하나가 너무 길어진다. 그때는 상태 하나를 클래스 하나로 만들고 "들어갈 때, 매 프레임, 나올 때" 함수를 각자 갖게 하는 방식(State 패턴)으로 키운다. 출발점은 오늘의 enum + switch다.
- **전환 로그를 남긴다.** `Idle → Chase`처럼 전환을 찍어 두면 "왜 갑자기 공격했지?" 같은 버그를 로그만 보고 추적할 수 있다. 다 만든 뒤에는 지우거나 개발용 설정에서만 켜지게 한다.

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **심화 Day 4**와 같은 내용이다. 앱은 추격 상태 이름을 Move로 쓴다.

- [enum: 이름 붙은 선택지](https://hlcho426.github.io/unity-csharp-week/#a4l1): 상태를 하나로 표현
- [switch로 상태별 동작](https://hlcho426.github.io/unity-csharp-week/#a4l2): case, break, default
- [상태 전환 규칙](https://hlcho426.github.io/unity-csharp-week/#a4l3): ChangeState, 들어갈 때 할 일

## 정리
{:.briefing-heading}

- bool 깃발 여러 개로 상태를 표현하면 말이 안 되는 조합이 생긴다
- `enum`은 정해진 선택지에 이름을 붙인 자료형. 변수에는 늘 딱 하나만 들어간다. `State.Attack`처럼 쓴다
- `switch (값) { case A: ... break; }`로 값에 따라 갈래를 나눈다. C#은 break를 빼먹으면 컴파일 에러, 나머지는 `default`
- 상태 변경은 `ChangeState` 한 곳에서만. 들어갈 때 할 일도 거기서. `if (state == next) return;`으로 같은 상태 재진입을 막는다
- 전환 조건은 각 상태의 Update 안에서 검사한다. 들어가는 문턱과 나오는 문턱에 여유를 둔다

다음 글은 심화 Day 5, 이벤트. 플레이어가 "나 쓰러졌어"라고 방송하면, 적과 UI가 알아서 반응하게 만든다. 플레이어 코드는 적이 있는지조차 몰라도 된다.
