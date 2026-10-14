---
title: "<유니티 C#> 심화 Day 5: 이벤트로 알아서 반응하게 (event Action, Invoke, UnityEvent)"
date: 2026-10-14 15:16:00 +0900
description: "플레이어는 \"나 쓰러졌어\"라고 방송만 하고, 적과 UI는 알아서 듣고 반응한다. event Action으로 방송하고 +=로 구독하고, OnEnable과 OnDisable로 해지까지. 인스펙터에서 연결하는 UnityEvent도 쓴다."
series: 유니티 C# 일주일
series_title: "심화 Day 5: 이벤트"
categories: [게임 제작 공부, 유니티]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

[Day 4](/posts/csharp-week-adv-day4/)의 적은 플레이어가 쓰러져도 계속 빨간색으로 때린다. 체력은 더 안 깎이지만, 적이 "플레이어가 쓰러졌다"는 걸 모르기 때문이다.

그럼 PlayerHealth가 쓰러질 때 `enemy.Stop()`을 부르면 될까? 적이 하나면 그렇다. 그런데 실제 게임에서는 플레이어가 쓰러지면 게임 오버 화면도 떠야 하고, 효과음도 나야 하고, 카메라도 흔들려야 하고, 스포너도 멈춰야 한다. PlayerHealth가 이 모든 걸 직접 불러야 할까? 오늘은 **방송만 하고, 듣는 쪽이 알아서 반응하는** 구조인 이벤트를 배운다.

**오늘의 목표**

- `event Action`으로 방송 채널을 만들고 `Invoke`로 방송할 수 있다
- `+=`로 구독하고 `-=`로 해지할 수 있다. 구독은 OnEnable, 해지는 OnDisable
- `Action<int>`로 값을 실어 보낼 수 있다
- 인스펙터에서 연결하는 `UnityEvent`를 쓸 수 있다

## 1. 직접 부르면 생기는 일
{:.briefing-heading}

```csharp
void Die()
{
    ui.ShowGameOver();
    sound.PlayDeathSound();
    cameraShake.Shake();
    enemySpawner.Stop();
    // 기능이 생길 때마다 계속 늘어난다...
}
```

Day 1에서 배운 대로 다른 스크립트를 직접 부르면 이렇게 된다. 문제가 세 가지 있다.

- 플레이어가 UI, 사운드, 카메라, 스포너를 **전부 알아야 한다.** 칸도 네 개 연결해야 한다.
- 하나라도 연결이 빠지면 NullReferenceException이 난다. 사운드 매니저가 없는 테스트 씬에서는 플레이어가 죽는 순간 에러다.
- "죽으면 업적 달성"을 넣으려면 **플레이어 코드를 또 고쳐야** 한다. 플레이어와 상관없는 기능인데도.

이렇게 스크립트끼리 서로를 많이 알고 얽혀 있는 걸 **결합도가 높다**고 한다. 하나를 고치면 줄줄이 고쳐야 한다.

## 2. 방송만 하고, 듣는 쪽이 알아서
{:.briefing-heading}

```csharp
using System;
using UnityEngine;

public class Player : MonoBehaviour
{
    public event Action OnDied;

    void Die()
    {
        OnDied?.Invoke();
    }
}
```

- `public event Action OnDied;`: **방송 채널**을 하나 만든다. 이름은 OnDied.
- `OnDied?.Invoke();`: 그 채널로 **방송한다.** "나 쓰러졌어!"

학교 방송실을 떠올리면 된다. 방송실은 "3반 학생들 운동장으로 모이세요"라고 말할 뿐, 누가 스피커 앞에 있는지 모른다. 듣는 학생들이 알아서 움직인다. 플레이어도 "나 쓰러졌어"라고 방송만 하고, 누가 듣는지 몰라도 된다.

`Action`은 C#에 들어 있는 기능이라 파일 맨 위에 `using System;`이 필요하다. List를 쓰려고 `using System.Collections.Generic;`을 넣었던 것과 같다.

### ?.는 "듣는 사람이 없으면 넘어가"

아무도 구독하지 않은 이벤트는 **비어 있다(null).** 이 상태에서 `OnDied.Invoke()`를 부르면 NullReferenceException이 난다. `?.`를 붙이면 "비어 있으면 그냥 넘어가고, 누가 있으면 방송해"가 된다. 그래서 이벤트를 방송할 때는 거의 항상 `?.Invoke()`로 쓴다.

## 3. 구독하고 해지하기
{:.briefing-heading}

듣는 쪽은 이렇게 쓴다.

```csharp
public class GameOverUI : MonoBehaviour
{
    [SerializeField] Player player;

    void OnEnable()
    {
        player.OnDied += ShowGameOver;    // 구독
    }

    void OnDisable()
    {
        player.OnDied -= ShowGameOver;    // 해지
    }

    void ShowGameOver()
    {
        Debug.Log("GAME OVER");
    }
}
```

`player.OnDied += ShowGameOver;`는 "OnDied 방송이 오면 ShowGameOver를 불러 줘"라고 **등록**하는 것이다. 이걸 **구독**이라고 한다. 유튜브 채널 구독과 같다. 구독해 두면 새 영상이 올라올 때 알림이 온다.

여기서 **함수 이름 뒤에 괄호를 안 붙인다**는 점이 중요하다. `ShowGameOver()`처럼 괄호를 붙이면 "지금 당장 실행해"가 된다. 지금은 실행하는 게 아니라 "나중에 방송 오면 불러 달라"고 **맡기는** 것이라 이름만 넘긴다.

이제 사운드 매니저도 반응하게 하려면? 사운드 쪽에서 `player.OnDied += PlayDeathSound;`로 구독만 하면 된다. **플레이어 코드는 한 줄도 안 고친다.** 이게 이벤트의 힘이다.

### OnEnable과 OnDisable

`Start`, `Update`처럼 유니티가 불러 주는 함수다.

| 함수 | 언제 불리나 |
|---|---|
| `OnEnable()` | 오브젝트나 스크립트가 **켜질 때**. 처음 시작할 때도 Start보다 먼저 불린다 |
| `OnDisable()` | 오브젝트나 스크립트가 **꺼질 때**. 오브젝트가 Destroy될 때도 먼저 불린다 |

켜질 때 구독하고 꺼질 때 해지하는 게 기본 짝이다.

### 구독했으면 해지까지 한 세트

구독 목록은 **방송하는 쪽(플레이어)에** 적혀 있다. GameOverUI 오브젝트가 Destroy돼도, 플레이어 쪽 목록에서 저절로 지워지지 않는다. 그래서 해지 없이 UI를 없애면, 나중에 플레이어가 방송할 때 **이미 사라진 UI의 함수를 부르려다** 에러가 날 수 있다.

OnEnable에서 `+=`, OnDisable에서 `-=`. 이 둘을 늘 같이 쓴다. 오브젝트가 Destroy될 때도 OnDisable이 먼저 불리니, 이 짝만 지키면 해지는 알아서 된다.

## 4. 값을 실어 보내기
{:.briefing-heading}

"체력이 바뀌었어"만 방송하면 UI가 몇으로 바뀌었는지 모른다. 숫자도 같이 보낸다.

```csharp
// Player
public event Action<int> OnHpChanged;

public void TakeDamage(int amount)
{
    hp -= amount;
    OnHpChanged?.Invoke(hp);
}

// HpUI
void OnEnable()  { player.OnHpChanged += UpdateHp; }
void OnDisable() { player.OnHpChanged -= UpdateHp; }

void UpdateHp(int current)
{
    Debug.Log("HP: " + current);
}
```

`Action<int>`는 **int 하나를 실어 보내는** 채널이다. `Invoke(hp)`의 hp가 받는 쪽 `UpdateHp(int current)`의 current로 들어간다. 그래서 체력 100에서 30을 맞으면 "HP: 70"이 찍힌다. hp를 깎은 **뒤에** Invoke 했으니까.

받는 함수는 보내는 것과 **모양이 맞아야** 한다. `Action<int>`에는 int 하나를 받는 void 함수만 구독할 수 있다. `void UpdateHp()`처럼 받는 칸이 없거나 `void UpdateHp(string s)`처럼 자료형이 다르면 `+=`에서 에러가 난다.

값이 두 개면 `Action<int, int>`처럼 늘리면 된다. 지금 체력과 최대 체력을 같이 보내면 체력바를 그리기 좋다.

## 5. 인스펙터에서 연결하는 이벤트: UnityEvent
{:.briefing-heading}

```csharp
using UnityEngine;
using UnityEngine.Events;

public class Door : MonoBehaviour
{
    public UnityEvent onOpened;

    public void Open()
    {
        onOpened.Invoke();
    }
}
```

`event Action`은 코드에서 `+=`를 해야 구독된다. `UnityEvent`는 **Inspector에 칸이 생겨서** 마우스로 연결한다. + 버튼을 누르고, 오브젝트를 끌어다 놓고, 실행할 함수를 드롭다운에서 고르면 끝이다. 코드를 안 고치고도 "문이 열리면 불 켜기, 소리 내기"를 붙일 수 있다.

사실 이미 본 적이 있을 수도 있다. UI 버튼의 **On Click ()** 칸이 바로 UnityEvent다.

| | event Action | UnityEvent |
|---|---|---|
| 연결하는 곳 | 코드 (`+=`) | Inspector (마우스) |
| 좋은 점 | 연결이 코드에 다 보인다. 빠르다 | 코드 없이 연결. 기획자가 직접 만질 수 있다 |
| 아쉬운 점 | 프로그래머만 연결할 수 있다 | 연결이 Inspector 여기저기 흩어져서 "이거 어디서 연결했지?"를 찾기 어렵다 |

그래서 보통 **코드끼리의 연결에는 event Action**, 레벨 디자인이나 연출처럼 **씬마다 다르게 붙이는 반응에는 UnityEvent**를 쓴다.

## 직접 해 보기
{:.briefing-heading}

플레이어가 쓰러지면 적이 공격을 멈추고, 코인을 다 주우면 적과 함정이 사라지게 만든다. 플레이어 쪽은 누가 듣는지 모른다.

### A. PlayerHealth가 방송하게

`PlayerHealth`를 아래처럼 바꾼다. 맨 위에 `using System;`이 추가됐고, Debug.Log 대신 이벤트를 방송한다. 로그는 듣는 쪽이 찍는다.

```csharp
using System;
using System.Collections;
using UnityEngine;

public class PlayerHealth : MonoBehaviour
{
    public event Action<int> OnHpChanged;
    public event Action OnDied;

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
        if (isInvincible) return;

        hp -= amount;
        if (hp < 0) hp = 0;
        OnHpChanged?.Invoke(hp);   // 체력이 바뀌었어, 지금 hp야

        if (hp == 0)
        {
            OnDied?.Invoke();      // 나 쓰러졌어
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

이 상태로 플레이하면 콘솔이 조용하다. 방송은 하는데 듣는 사람이 아직 없다. `?.` 덕분에 에러도 안 난다.

### B. 체력 로그를 듣는 스크립트

1. **Create Empty**로 빈 오브젝트 `HpLogger`를 만들고, 같은 이름의 스크립트를 붙인다.

```csharp
using UnityEngine;

public class HpLogger : MonoBehaviour
{
    [SerializeField] PlayerHealth player;

    void OnEnable()
    {
        player.OnHpChanged += ShowHp;
        player.OnDied += ShowGameOver;
    }

    void OnDisable()
    {
        player.OnHpChanged -= ShowHp;
        player.OnDied -= ShowGameOver;
    }

    void ShowHp(int current)
    {
        Debug.Log("HP: " + current);
    }

    void ShowGameOver()
    {
        Debug.Log("GAME OVER");
    }
}
```

2. **Player** 칸에 플레이어 큐브를 끌어다 놓고 플레이한다. 함정이나 적에게 맞으면 "HP: 70"이 다시 찍힌다. 나중에 화면에 체력바를 만들 때(실전 Day 5)는 이 스크립트 자리에 UI 스크립트가 들어간다. PlayerHealth는 그때도 안 고친다.

해 볼 것: 플레이 중에 HpLogger 오브젝트의 체크박스를 꺼 보자. OnDisable에서 해지되니, 맞아도 로그가 안 찍힌다. 다시 켜면 OnEnable에서 구독해서 다시 찍힌다.

### C. 적이 플레이어의 쓰러짐을 듣게

`Enemy`에 아래 세 함수를 추가한다. 나머지는 Day 4 그대로다.

```csharp
void OnEnable()
{
    player.OnDied += StopAttack;
}

void OnDisable()
{
    player.OnDied -= StopAttack;
}

void StopAttack()
{
    ChangeState(State.Idle);
    enabled = false;   // 이 스크립트를 꺼서 Update를 멈춘다
}
```

적에게 계속 맞아서 쓰러져 보자. "GAME OVER"가 찍히는 순간 적이 흰색으로 돌아가 멈춘다. HpLogger와 Enemy, 두 곳이 같은 방송을 듣고 각자 반응했다.

`enabled = false`로 스크립트가 꺼지면 OnDisable이 불려서 구독도 알아서 해지된다. Day 2에서 본 것처럼 스크립트만 꺼도 코루틴은 안 멈추지만, 이 Enemy에는 코루틴이 없으니 괜찮다.

### D. 코인을 다 주우면: UnityEvent로 연결

1. `PlayerController` 맨 위에 `using UnityEngine.Events;`를 넣고, 변수를 하나 추가한다.

```csharp
public UnityEvent onCleared;
```

2. 클리어하는 곳에 한 줄을 넣는다.

```csharp
if (coin >= goal && !isCleared)
{
    isCleared = true;
    Debug.Log("스테이지 클리어!");
    onCleared.Invoke();
}
```

3. 플레이어 큐브의 PlayerController를 보면 **On Cleared ()**라는 칸이 생겼다. 오른쪽 아래 **+**를 누른다.
4. 새로 생긴 줄의 빈 칸(None (Object))에 Hierarchy의 **Enemy**를 끌어다 놓는다. 오른쪽 드롭다운(No Function)에서 **Enemy → bool enabled**를 고르고, 아래 체크박스는 **끈 채로** 둔다. "클리어하면 Enemy 스크립트의 enabled를 false로"라는 뜻이다.
5. **+**를 한 번 더 눌러 **Trap**을 끌어다 놓고, **GameObject → SetActive (bool)**을 골라 체크박스를 끈 채로 둔다. 함정 오브젝트를 끄라는 뜻이다.
6. 플레이해서 코인을 다 줍는다. 적이 멈추고 함정이 사라진다.

PlayerController의 코드에는 Enemy도 Trap도 나오지 않는다. "클리어했다"고 Invoke만 했고, 누가 무엇을 할지는 Inspector에서 정했다. 함정을 하나 더 끄고 싶으면 +를 눌러 추가하면 된다. 코드는 그대로다.

UnityEvent는 Inspector가 미리 만들어 두기 때문에 비어 있지 않다. 그래서 `?.` 없이 `onCleared.Invoke()`로 바로 부른다.

### 더 해 보기

쓰러지면 플레이어도 못 움직이게 해 보자. 단, **PlayerHealth는 한 줄도 고치지 않는다.** PlayerController가 같은 오브젝트의 PlayerHealth 방송을 구독하면 된다.

```csharp
void OnEnable()
{
    GetComponent<PlayerHealth>().OnDied += Stop;
}

void OnDisable()
{
    GetComponent<PlayerHealth>().OnDied -= Stop;
}

void Stop()
{
    enabled = false;
}
```

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. `+= ShowGameOver()`로 썼더니 에러가 나.**<br>
괄호를 붙이면 ShowGameOver를 **지금 실행**하고, 그 결과(void라서 없음)를 등록하려는 게 된다. 구독할 때는 이름만 쓴다.

**Q. OnEnable에서 NullReferenceException이 나.**<br>
player 칸에 연결을 안 했다. OnEnable은 시작하자마자 불리니까 플레이 버튼을 누르는 순간 에러가 난다. Inspector부터 확인한다.

**Q. `using System;`을 넣었더니 Random에 빨간 줄이 생겼어.**<br>
심화 Day 3에서 본 그 문제다. C#에도 Random이 있어서 이름이 겹친다. 같은 파일에서 유니티 Random을 쓰려면 `UnityEngine.Random.Range(...)`처럼 앞에 붙인다.

**Q. event를 빼고 `public Action OnDied;`로 써도 동작하는데?**<br>
동작은 한다. 하지만 event를 빼면 **바깥 스크립트가** `player.OnDied = null;`로 구독 목록을 통째로 지우거나, `player.OnDied.Invoke();`로 플레이어 대신 방송해 버릴 수 있다. `event`를 붙이면 바깥에서는 `+=`와 `-=`만 할 수 있고, 방송은 주인만 할 수 있다. Day 1에서 hp를 private으로 막은 것과 같은 이유다.

**Q. 같은 함수를 두 번 구독하면?**<br>
두 번 불린다. 로그가 두 번씩 찍히면 `+=`가 두 군데 있는지, OnEnable 말고 Start에서도 구독했는지 본다. 해지(`-=`)는 한 번에 하나씩 빠진다.

**Q. 구독한 함수들은 어떤 순서로 불려?**<br>
보통 구독한 순서대로 불린다. 하지만 OnEnable이 어느 스크립트부터 불릴지는 정해져 있지 않아서, 순서에 기대는 코드는 만들지 않는 게 좋다. "UI가 먼저 바뀌고 나서 사운드가" 같은 순서가 꼭 필요하면 이벤트를 둘로 나눈다.

## 현업에서는
{:.briefing-heading}

- **이름은 On + 일어난 일.** `OnDied`, `OnHpChanged`, `OnCoinCollected`처럼 "~했을 때"로 짓는다. 방송하는 쪽은 "무슨 일이 일어났다"만 알리고, "UI를 갱신해라" 같은 명령조 이름은 피한다. 무엇을 할지는 듣는 쪽이 정한다.
- **결합도를 낮추면 테스트가 쉽다.** 플레이어가 UI를 모르니까, UI 없는 빈 씬에서도 플레이어만 꺼내서 테스트할 수 있다. 팀 작업에서는 UI 담당과 전투 담당이 서로의 코드를 안 건드리고 일할 수 있다.
- **이벤트도 너무 많으면 길을 잃는다.** 방송하는 쪽은 누가 듣는지 모르기 때문에, 이벤트가 꼬리에 꼬리를 물면 "이게 왜 실행됐지?"를 추적하기 어렵다. 같은 스크립트 안이나, 서로 꼭 알아야 하는 관계는 그냥 직접 부른다.
- **람다로 구독하는 코드도 자주 보인다.** `player.OnDied += () => Debug.Log("끝");`처럼 함수를 따로 안 만들고 그 자리에서 쓰는 방식이다. 실전 Day 3에서 배운다. 다만 이렇게 구독하면 `-=`로 해지하기가 어려워서, 해지가 필요한 곳은 오늘처럼 이름 있는 함수로 구독한다.

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **심화 Day 5**와 같은 내용이다.

- [서로 몰라도 되게](https://hlcho426.github.io/unity-csharp-week/#a5l1): event Action, Invoke
- [구독하고 해지하기](https://hlcho426.github.io/unity-csharp-week/#a5l2): +=, -=, OnEnable/OnDisable
- [값을 실어 보내기](https://hlcho426.github.io/unity-csharp-week/#a5l3): Action&lt;int&gt;, UnityEvent

## 정리
{:.briefing-heading}

- 직접 부르기가 많아지면 스크립트끼리 얽힌다(결합도가 높다)
- `public event Action OnDied;`로 방송 채널을 만들고, `OnDied?.Invoke();`로 방송한다. `?.`는 듣는 사람이 없으면 넘어가는 안전장치. `using System;` 필요
- `이벤트 += 함수이름;`으로 구독, `-=`로 해지. 함수 이름에 괄호를 안 붙인다
- OnEnable에서 구독, OnDisable에서 해지가 기본 짝. 해지를 안 하면 사라진 오브젝트를 부르다 에러가 날 수 있다
- `Action<int>`는 int 하나를 실어 보낸다. 받는 함수도 int 하나를 받는 모양이어야 한다
- `UnityEvent`는 Inspector에서 마우스로 연결하는 이벤트. 코드끼리는 event Action, 씬마다 다른 반응은 UnityEvent

다음 글은 심화 Day 6, ScriptableObject. 적의 속도, 공격력 같은 숫자를 코드 밖 데이터 파일로 빼서, 슬라임과 고블린을 코드 수정 없이 만든다.
