---
title: "<유니티 C#> 심화 Day 2: 코루틴으로 시간차 동작 만들기 (IEnumerator, yield, WaitForSeconds)"
date: 2026-10-14 15:04:00 +0900
description: "3초 뒤에 폭발, 0.1초 간격으로 깜빡이기, 2초 쿨타임. Update만으로는 번거로운 시간차 동작을 코루틴으로 만든다. while 반복문과 코루틴 멈추기까지."
series: 유니티 C# 일주일
series_title: "심화 Day 2: 코루틴"
categories: [게임 제작 공부, 유니티]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

[Day 1](/posts/csharp-week-adv-day1/)에서 함정이 플레이어 체력을 깎게 만들었다. 그런데 지금은 함정 두 개를 연달아 밟으면 체력이 순식간에 두 번 깎인다. 보통 게임은 맞으면 캐릭터가 잠깐 깜빡이면서 그동안은 안 맞는다. 이걸 만들려면 "0.1초 동안 안 보이고, 0.1초 동안 보이고, 이걸 다섯 번, 끝나면 무적 해제"처럼 **시간차가 있는 동작**이 필요하다.

Update는 매 프레임 처음부터 다시 실행된다. "0.1초 기다렸다가 다음 줄"을 할 수가 없다. 그래서 타이머 변수를 여러 개 만들어 매 프레임 시간을 재야 하는데, 금방 복잡해진다. 오늘 배우는 **코루틴**은 함수 안에서 "여기서 잠깐 쉬었다가 이어서"를 할 수 있게 해 준다.

**오늘의 목표**

- 코루틴을 만들고 `StartCoroutine`으로 시작할 수 있다
- `WaitForSeconds`와 `yield return null`로 기다리는 시간을 정할 수 있다
- `while` 반복문을 읽고 쓸 수 있다
- 쿨타임과 무적 시간을 만들 수 있다

## 1. 기다렸다가 실행하기
{:.briefing-heading}

3초 뒤에 터지는 폭탄이다.

```csharp
using System.Collections;
using UnityEngine;

public class Bomb : MonoBehaviour
{
    void Start()
    {
        StartCoroutine(Explode());
    }

    IEnumerator Explode()
    {
        Debug.Log("째깍째깍...");
        yield return new WaitForSeconds(3f);
        Debug.Log("펑!");
        Destroy(gameObject);
    }
}
```

새로운 게 세 개다.

| 코드 | 뜻 |
|---|---|
| `IEnumerator` | "이 함수는 코루틴이다"라는 표시. void 자리에 쓴다 |
| `yield return new WaitForSeconds(3f);` | 여기서 3초 쉰다 |
| `StartCoroutine(Explode());` | 코루틴을 시작한다 |

보통 함수는 불리면 끝까지 한 번에 실행된다. 코루틴은 `yield return`을 만나면 **그 자리에 책갈피를 꽂고 잠깐 멈춘다.** 3초가 지나면 유니티가 책갈피 자리부터 이어서 실행해 준다. 그래서 "째깍째깍..."이 찍히고 3초 뒤에 "펑!"이 찍힌다.

중요한 건, 코루틴이 쉬는 3초 동안 **게임은 멈추지 않는다**는 점이다. 다른 오브젝트의 Update도, 이 오브젝트의 Update도 평소처럼 돈다. 쉬는 건 이 코루틴 하나뿐이다.

> **`using System.Collections;`를 꼭 넣는다.** `IEnumerator`는 이 묶음 안에 들어 있다. Unity 6의 새 스크립트에는 `using UnityEngine;` 한 줄만 있어서, 이 줄을 안 넣으면 IEnumerator에 빨간 줄이 생긴다. 기초 Day 3에서 List를 쓰려고 `using System.Collections.Generic;`을 넣었던 것과 같다. 이름이 비슷하지만 다른 줄이다.
{: .prompt-warning }

### Explode()만 쓰면 아무 일도 없다

```csharp
Explode();                   // 아무 일도 안 일어남 (에러도 없음)
StartCoroutine(Explode());   // 이렇게 시작해야 한다
```

코루틴을 보통 함수처럼 부르면, 에러도 안 나고 아무것도 실행되지 않는다. 콘솔이 조용하니 원인 찾기가 어렵다. 코루틴은 **반드시 StartCoroutine으로 감싸서** 시작한다.

## 2. 반복 연출 만들기
{:.briefing-heading}

### for 안에 yield를 넣으면 시간차 반복

피격 시 깜빡이기다.

```csharp
IEnumerator Blink()
{
    Renderer r = GetComponent<Renderer>();

    for (int i = 0; i < 5; i++)
    {
        r.enabled = false;                      // 안 보이게
        yield return new WaitForSeconds(0.1f);
        r.enabled = true;                       // 보이게
        yield return new WaitForSeconds(0.1f);
    }
}
```

`Renderer`는 오브젝트를 화면에 그리는 컴포넌트다. `enabled`를 false로 하면 그리지 않아서 사라져 보인다. 오브젝트가 없어진 게 아니라 안 그리는 것뿐이라 충돌은 그대로 한다.

for 한 바퀴에 0.1 + 0.1 = 0.2초, 다섯 바퀴면 1초 동안 깜빡인다. 기초 Day 3의 for는 한 프레임 안에 순식간에 다 돌았지만, 안에 yield가 있으면 바퀴마다 쉬어 가면서 돈다. 코루틴 + for는 연출에 정말 자주 쓰인다.

### while: 조건이 참인 동안 반복

```csharp
int hp = 3;
while (hp > 0)
{
    Debug.Log("남은 체력: " + hp);
    hp--;
}
// 3, 2, 1을 찍고 끝
```

기초 Day 3에서 예고한 `while`이다. `while (조건)`은 **조건이 참인 동안** 중괄호 안을 계속 반복한다. for는 "10번"처럼 횟수를 정해 두지만, while은 "체력이 남아 있는 동안", "적이 살아 있는 동안"처럼 **몇 번일지 모르는 반복**에 어울린다.

순서는 이렇다. 조건 검사 → 참이면 중괄호 안 실행 → 다시 조건 검사 → … → 거짓이면 빠져나간다. 위 코드는 hp가 3, 2, 1일 때 실행되고, 0이 되는 순간 `hp > 0`이 거짓이라 끝난다.

> 중괄호 안에서 조건을 바꾸는 줄(`hp--`)을 빼먹으면 hp는 영원히 3이라 끝나지 않는다. 기초 Day 3에서 본 **무한 루프**다. 유니티 에디터가 통째로 멈춰서 작업 관리자로 강제 종료해야 한다. 저장 안 한 씬은 날아간다.
{: .prompt-danger }

### yield return null: 한 프레임만 쉬기

```csharp
IEnumerator FadeOut()
{
    float t = 1f;
    while (t > 0f)
    {
        t -= Time.deltaTime;
        // t를 투명도로 쓴다 (1 → 0)
        yield return null;   // 다음 프레임까지 대기
    }
}
```

`yield return null`은 "**다음 프레임에** 이어서"라는 뜻이다. 매 프레임 t가 조금씩 줄어들고, 1초 뒤 0이 되면 while이 끝난다. 서서히 변하는 연출을 Update 없이 만들 수 있다.

### 코루틴 안의 while(true)에는 반드시 yield

```csharp
IEnumerator Loop()
{
    while (true)
    {
        Debug.Log("돈다");
        yield return null;   // 이 줄이 없으면 유니티가 멈춘다
    }
}
```

`while (true)`는 조건이 늘 참이라 끝나지 않는다. 일반 함수에서는 무조건 무한 루프지만, 코루틴에서는 안에 yield가 있으면 **한 바퀴 돌 때마다 쉬어 가니까** 안전하다. "게임 내내 2초마다 적 생성" 같은 일에 쓴다(심화 Day 3). 대신 yield를 빼먹으면 쉬지 않고 영원히 돌아서 에디터가 굳는다.

## 3. 쿨타임 만들기
{:.briefing-heading}

### 방법 1: bool 깃발 + 코루틴

```csharp
bool canDash = true;

void Update()
{
    if (Input.GetKeyDown(KeyCode.LeftShift) && canDash)
    {
        Dash();
        StartCoroutine(DashCooldown());
    }
}

IEnumerator DashCooldown()
{
    canDash = false;
    yield return new WaitForSeconds(2f);
    canDash = true;
}
```

기초 Day 7의 `isCleared` 같은 bool 깃발에 코루틴을 합쳤다. 대시하면 깃발을 내리고, 2초 뒤 다시 올린다. 깃발이 내려가 있는 동안에는 `&& canDash`가 거짓이라 Shift를 눌러도 대시가 안 된다.

### 방법 2: 시각 비교

```csharp
float nextDashTime = 0f;

void Update()
{
    if (Input.GetKeyDown(KeyCode.LeftShift) && Time.time >= nextDashTime)
    {
        Dash();
        nextDashTime = Time.time + 2f;
    }
}
```

`Time.time`은 게임이 시작되고 흐른 시간(초)이다. 대시할 때 "다음에 쓸 수 있는 시각"을 적어 둔다. Time.time이 10.5일 때 대시했다면 nextDashTime은 12.5이고, 그 시각이 지나야 다시 쓸 수 있다. 코루틴 없이 숫자 하나로 끝나서 가볍다.

| | 깃발 + 코루틴 | 시각 비교 |
|---|---|---|
| 변수 | bool 하나 + 코루틴 함수 | float 하나 |
| 좋은 점 | 쿨타임이 끝나는 순간 할 일(소리, 아이콘 반짝)을 넣기 쉽다 | 가볍고 짧다. 남은 시간 계산도 쉽다 (`nextDashTime - Time.time`) |

둘 다 실무에서 쓴다. 스킬이 수십 개라면 시각 비교가 관리하기 편하다.

## 4. 코루틴 멈추기
{:.briefing-heading}

```csharp
Coroutine blink;

blink = StartCoroutine(Blink());
StopCoroutine(blink);   // 이것 하나만 멈춤

StopAllCoroutines();    // 이 스크립트의 코루틴 전부 멈춤
```

`StartCoroutine`은 시작한 코루틴을 `Coroutine` 자료형으로 돌려준다. 받아 두었다가 `StopCoroutine`에 넣으면 그것 하나만 멈춘다. 이 스크립트에서 돌고 있는 코루틴을 한꺼번에 멈추려면 `StopAllCoroutines()`를 쓴다. 맞아서 하던 연출을 끊고 새 연출을 시작할 때 자주 쓴다.

코루틴은 이럴 때도 저절로 멈춘다.

| 하는 일 | 코루틴 |
|---|---|
| `Destroy(gameObject)` | 멈춘다 |
| `gameObject.SetActive(false)` (오브젝트 끄기) | 멈춘다. 다시 켜도 이어서 돌지 않는다 |
| `enabled = false` (스크립트만 끄기) | **안 멈춘다** |

마지막 줄이 함정이다. 스크립트 체크박스를 꺼서 Update는 멈췄는데, 코루틴은 계속 돌고 있을 수 있다.

## 직접 해 보기
{:.briefing-heading}

Day 1의 함정 씬에서 이어서 한다.

### A. 맞으면 깜빡이며 1초 무적

`PlayerHealth`를 아래처럼 바꾼다. 맨 위 using 줄도 확인한다.

```csharp
using System.Collections;
using UnityEngine;

public class PlayerHealth : MonoBehaviour
{
    [SerializeField] int maxHp = 100;

    int hp;
    bool isInvincible = false;
    Renderer rend;

    void Start()
    {
        hp = maxHp;
        rend = GetComponent<Renderer>();
    }

    public void TakeDamage(int amount)
    {
        if (hp <= 0) return;
        if (isInvincible) return;   // 무적 중이면 무시

        hp -= amount;
        if (hp < 0) hp = 0;
        Debug.Log("아야! 남은 체력 " + hp);

        if (hp == 0)
        {
            Debug.Log("게임 오버");
            return;
        }

        StartCoroutine(Invincible());
    }

    IEnumerator Invincible()
    {
        isInvincible = true;

        for (int i = 0; i < 5; i++)
        {
            rend.enabled = false;
            yield return new WaitForSeconds(0.1f);
            rend.enabled = true;
            yield return new WaitForSeconds(0.1f);
        }

        isInvincible = false;
    }
}
```

`Invincible` 코루틴 하나가 두 가지를 같이 한다. 시작할 때 무적 깃발을 올리고, 1초 동안 깜빡인 뒤, 깃발을 내린다. TakeDamage 맨 위의 `if (isInvincible) return;`이 무적 동안 들어오는 데미지를 걸러낸다.

함정 두 개를 딱 붙여 놓고 한 번에 지나가 보자. 첫 함정에서 깜빡이기 시작하고, 두 번째 함정에서는 체력이 깎이지 않는다. 함정 사이를 벌려서 1초 넘게 걸리게 지나가면 둘 다 깎인다.

### B. 대시와 2초 쿨타임

`PlayerController`에 대시를 넣는다. 짧은 시간 동안 이동 속도를 확 올리는 방식이다. 기초 Day 6의 "더 해 보기"에서 Shift를 달리기로 썼다면 겹치지 않게, 대시는 **E** 키로 한다.

맨 위에 `using System.Collections;`를 넣고, 변수를 추가한다.

```csharp
[SerializeField] float dashSpeed = 15f;
[SerializeField] float dashTime = 0.2f;
[SerializeField] float dashCooldown = 2f;

bool canDash = true;
bool isDashing = false;
```

Update의 이동 부분을 이렇게 바꾼다. 원래 speed는 그대로 두고, 이번 프레임에 쓸 속도를 `currentSpeed`에 따로 담는다(기초 Day 6의 달리기와 같은 방법).

```csharp
float h = Input.GetAxis("Horizontal");
float v = Input.GetAxis("Vertical");
Vector3 dir = new Vector3(h, 0f, v);

float currentSpeed = speed;
if (isDashing) currentSpeed = dashSpeed;
transform.position += dir * currentSpeed * Time.deltaTime;

if (Input.GetKeyDown(KeyCode.E) && canDash)
{
    StartCoroutine(Dash());
}
```

그리고 코루틴을 추가한다.

```csharp
IEnumerator Dash()
{
    canDash = false;
    isDashing = true;
    Debug.Log("대시!");

    yield return new WaitForSeconds(dashTime);       // 0.2초 동안 빠르게
    isDashing = false;

    yield return new WaitForSeconds(dashCooldown);   // 2초 쿨타임
    canDash = true;
    Debug.Log("대시 준비 완료");
}
```

yield가 두 번 나온다. 코루틴은 위에서부터 차례로 쉬어 가며 내려가니까 "0.2초 대시 → 대시 끝 → 2초 쉼 → 다시 사용 가능"이 순서대로 일어난다. Update로 만들었다면 타이머 변수가 두 개 필요했을 일이다.

방향키를 누른 채 E를 눌러 보자. 휙 미끄러지듯 나갔다가, 2초 동안은 E를 눌러도 반응이 없다. 방향키 없이 E만 누르면 dir이 0이라 제자리에 있는다.

해 볼 것: 대시 중에는 함정에 안 맞게 해 보자. 대시 중인지는 PlayerController가 알고, 맞을지 말지는 PlayerHealth가 정한다. 예를 들어 PlayerHealth에 무적을 켜고 끄는 public 메서드 `SetInvincible(bool on)`을 만들고, Dash 코루틴에서 `GetComponent<PlayerHealth>()`로 꺼내 부를 수 있다(Day 1에서 함정이 한 것과 같다). 그런데 맞아서 무적인 도중에 대시가 끝나며 무적을 꺼 버리면? 정답이 하나가 아닌 문제라, 어떻게 나누면 깔끔할지 고민해 보는 것 자체가 연습이다.

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. StartCoroutine을 Update 안에서 불렀더니 이상해졌어.**<br>
Update는 매 프레임 불리니까, 조건 없이 StartCoroutine을 쓰면 **매 프레임 새 코루틴이 하나씩** 시작된다. 1초면 수십 개가 동시에 돈다. Update 안에서 시작할 때는 위 대시처럼 `GetKeyDown`이나 깃발로 "한 번만" 시작되게 한다. 게임 내내 도는 코루틴은 Start에서 한 번 시작한다.

**Q. 코루틴을 중간에 끝내고 싶어. return; 하면 돼?**<br>
코루틴 안에서는 `return;`이 에러다. 대신 `yield break;`를 쓴다. 기초 Day 8의 조기 반환과 같은 역할이다.

```csharp
IEnumerator Blink()
{
    if (rend == null) yield break;   // 그릴 게 없으면 바로 끝
    // ...
}
```

**Q. 게임을 일시정지했는데 WaitForSeconds가 계속 흘러가?**<br>
반대다. 보통 일시정지는 `Time.timeScale = 0`으로 만드는데, 이러면 WaitForSeconds도 같이 **멈춘다.** 게임 시간 기준으로 기다리기 때문이다. 일시정지 메뉴의 연출처럼 멈춘 동안에도 흘러가야 하는 건 `WaitForSecondsRealtime`을 쓴다.

**Q. 코루틴이 값을 돌려줄 수는 없어?**<br>
코루틴의 반환 자료형 자리는 IEnumerator로 정해져 있어서, `int`처럼 값을 돌려받을 수 없다. 결과가 필요하면 코루틴이 필드 값을 바꾸게 하거나, 심화 Day 5의 이벤트로 "끝났다"고 알리게 한다.

**Q. 같은 코루틴을 두 번 시작하면?**<br>
두 개가 동시에 돈다. 무적 중에는 TakeDamage가 걸러내니 지금 코드는 괜찮지만, 무적 없이 맞을 때마다 Blink를 시작하면 깜빡임이 겹쳐서 엉망이 된다. 받아 둔 Coroutine으로 이전 것을 멈추고 새로 시작한다.

```csharp
Coroutine blinkRoutine;

void StartBlink()
{
    if (blinkRoutine != null) StopCoroutine(blinkRoutine);
    blinkRoutine = StartCoroutine(Blink());
}
```

## 현업에서는
{:.briefing-heading}

- **연출은 코루틴, 쿨타임은 시각 비교.** 깜빡임, 페이드, 카메라 흔들림처럼 순서대로 흘러가는 연출은 코루틴이 읽기 쉽다. 스킬 쿨타임처럼 숫자만 재면 되는 건 `Time.time` 비교로 가볍게 만드는 경우가 많다.
- **코루틴 핸들을 챙긴다.** 실무 코드에서 `Coroutine xxxRoutine;` 필드를 자주 보는 이유가 위의 "두 번 시작" 문제다. 다시 시작할 수 있는 코루틴은 받아 두고, 시작 전에 이전 것을 멈춘다.
- **같은 대기 시간은 만들어 두고 쓴다.** `new WaitForSeconds(0.1f)`는 부를 때마다 메모리에 새로 만들어진다. 아주 자주 도는 코루틴이라면 `WaitForSeconds wait = new WaitForSeconds(0.1f);`를 필드로 한 번 만들어 두고 `yield return wait;`로 재사용한다. 처음에는 신경 쓰지 않아도 된다.
- **Unity 6에는 Awaitable도 있다.** `async`, `await`라는 C# 문법으로 코루틴과 비슷한 일을 하는 방식이다. 최근 코드에서 보이기 시작했는데, "기다렸다가 이어서"라는 원리는 코루틴과 같아서 코루틴을 이해하면 금방 읽힌다.

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **심화 Day 2**와 같은 내용이다. 앱의 예제는 대시 키로 Shift를 쓴다.

- [기다렸다가 실행하기](https://hlcho426.github.io/unity-csharp-week/#a2l1): IEnumerator, yield, StartCoroutine
- [반복 연출 만들기](https://hlcho426.github.io/unity-csharp-week/#a2l2): 깜빡임, while, 매 프레임 대기
- [쿨타임 만들기](https://hlcho426.github.io/unity-csharp-week/#a2l3): bool 깃발 + 코루틴, 시각 비교, 멈추기

## 정리
{:.briefing-heading}

- 코루틴 = 중간에 쉬었다가 이어서 실행하는 함수. `IEnumerator`로 만들고 `StartCoroutine(이름())`으로 시작한다
- `using System.Collections;`가 있어야 IEnumerator를 쓸 수 있다
- `yield return new WaitForSeconds(초);`는 그만큼 쉬기, `yield return null;`은 한 프레임 쉬기
- 코루틴이 쉬는 동안에도 게임은 계속 돈다
- `while (조건)`은 조건이 참인 동안 반복. 코루틴 안의 `while (true)`에는 반드시 yield
- 쿨타임은 bool 깃발 + 코루틴, 또는 `Time.time` 시각 비교
- `StopCoroutine(받아 둔 코루틴)`, `StopAllCoroutines()`로 멈춘다. 오브젝트를 끄거나 지우면 같이 멈추지만, 스크립트만 끄면 안 멈춘다

다음 글은 심화 Day 3, 프리팹과 생성. 기초 Day 7에서 코인 다섯 개를 일일이 복사했던 걸 프리팹 하나로 바꾸고, 코인이 시간차로 하나씩 나타나게 만든다.
