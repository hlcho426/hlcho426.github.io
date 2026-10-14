---
title: "<유니티 C#> 심화 Day 6: ScriptableObject로 데이터 에셋 만들기 (CreateAssetMenu, 데이터와 상태 나누기)"
date: 2026-10-14 15:20:00 +0900
description: "아이템, 몬스터, 스킬 같은 기획 데이터를 코드 밖 에셋 파일로 뺀다. CreateAssetMenu로 데이터 파일을 만들고, 플레이 중에 바꾼 값이 남는 함정과 원본 데이터와 실행 중 상태를 나누는 법까지."
series: 유니티 C# 일주일
series_title: "심화 Day 6: ScriptableObject"
categories: [게임 제작 공부, 유니티]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

[Day 4](/posts/csharp-week-adv-day4/)에서 만든 적은 속도, 추격 거리, 공격력을 Inspector에서 정한다. 그런데 느리고 약한 슬라임과 빠르고 센 고블린을 만들고 싶다면? 적 오브젝트마다 숫자를 따로 입력해야 한다. 슬라임이 열 마리면 속도를 바꿀 때 열 번 고친다. 그리고 그 숫자들은 씬 안의 오브젝트에 묶여 있어서, 다른 씬에서 같은 슬라임을 쓰려면 또 입력해야 한다.

기획서에는 보통 이런 표가 있다.

| 이름 | 이동 속도 | 추격 거리 | 공격력 | 공격 간격 |
|---|---|---|---|---|
| 슬라임 | 1.5 | 5 | 10 | 1.5초 |
| 고블린 | 3.5 | 7 | 20 | 0.8초 |

오늘은 이 표의 한 줄 한 줄을 **프로젝트의 파일**로 만든다. 그게 **ScriptableObject**다. 슬라임 데이터 파일 하나를 고치면 모든 슬라임이 바뀌고, 고블린 강화판은 파일을 복제해서 숫자만 바꾸면 끝이다. 코드는 안 고친다.

**오늘의 목표**

- ScriptableObject로 데이터 에셋을 만들 수 있다
- 오브젝트가 데이터 에셋을 읽어 쓰게 할 수 있다
- 원본 데이터(에셋)와 실행 중에 변하는 값(오브젝트)을 나눌 수 있다

## 1. 데이터를 에셋으로 만들기
{:.briefing-heading}

상점 아이템 데이터를 예로 든다.

```csharp
using UnityEngine;

[CreateAssetMenu(menuName = "Game/Item")]
public class ItemData : ScriptableObject
{
    public string itemName;
    public int price;
    public Sprite icon;
    [TextArea] public string description;
}
```

`: MonoBehaviour` 대신 `: ScriptableObject`를 붙였다. 이러면 게임 오브젝트에 붙이는 컴포넌트가 아니라, **프로젝트 창의 파일(에셋)**로 존재하는 데이터가 된다.

위의 `[CreateAssetMenu(menuName = "Game/Item")]`는 Project 창 메뉴에 이 데이터를 만드는 항목을 추가한다. 이제 Project 창에서 우클릭 → **Create → Game → Item**을 고르면 `포션.asset`, `열쇠.asset` 같은 파일이 생기고, 선택하면 Inspector에서 값을 채울 수 있다. 머티리얼이나 프리팹처럼 그냥 파일이다.

Day 1에서 본 클래스 종류에 하나가 더 늘었다.

| | MonoBehaviour | ScriptableObject | 순수 클래스 |
|---|---|---|---|
| 어디에 있나 | 씬의 오브젝트에 붙어서 | 프로젝트 창의 **파일**로 | 코드 안에서 `new`로 |
| Start, Update | 있다 | 없다 | 없다 |
| 쓰임 | 움직이고 반응하는 것 | 아이템, 몬스터, 스킬 같은 **기획 데이터** | 세이브 데이터, 계산용 묶음 |

씬과 상관없이 파일로 있으니 여러 씬에서 같은 에셋을 같이 쓸 수 있다.

> **💡 꿀팁: Inspector를 보기 좋게 꾸미기**
>
> ```csharp
> [Header("기본 정보")]
> public string itemName;
>
> [Range(0, 9999)]
> public int price;
>
> [Tooltip("상점에 보이는 설명")]
> [TextArea] public string description;
> ```
>
> 변수 위에 붙이는 `[ ]` 표시를 **어트리뷰트**라고 한다. 늘 쓰던 `[SerializeField]`도 어트리뷰트다. 코드 동작은 그대로 두고 Inspector 모양만 바꿔 준다.
>
> - `[Header("제목")]`: 위에 굵은 소제목을 단다
> - `[Range(최소, 최대)]`: 숫자 칸이 슬라이더가 되고, 범위 밖 값은 못 넣는다
> - `[Tooltip("설명")]`: 칸 이름에 마우스를 올리면 설명이 뜬다
> - `[TextArea]`: 한 줄 칸이 여러 줄 입력 칸이 된다
>
> 데이터를 채우는 사람이 칸마다 뜻을 묻지 않아도 되게 해 준다. 기획자가 직접 데이터를 넣는 팀이라면 정말 고마운 기능이다.
{: .prompt-tip }

## 2. 데이터 에셋 사용하기
{:.briefing-heading}

```csharp
public class ShopSlot : MonoBehaviour
{
    [SerializeField] ItemData item;

    void Start()
    {
        Debug.Log(item.itemName + " : " + item.price + "G");
    }
}
```

ShopSlot에 `ItemData` 자료형의 칸을 만들고, Inspector에서 Project 창의 `포션.asset`을 끌어다 놓는다. Day 1에서 플레이어를 끌어다 놓던 것과 같다. 그다음엔 `item.price`처럼 점으로 꺼내 읽는다.

슬롯 10개가 모두 같은 `포션.asset`을 가리킨다면, 포션 가격을 50에서 80으로 바꿀 때 **에셋 하나만** 고치면 슬롯 10개가 모두 바뀐다. 슬롯마다 가격이 복사돼 들어간 게 아니라, 모두 같은 파일 하나를 **가리키고** 있기 때문이다. 밸런스 조정이 정말 편해진다.

## 3. 주의: 플레이가 끝나도 바뀐 채 남는다
{:.briefing-heading}

```csharp
void Start()
{
    item.itemName = "테스트";
    // 에디터에서 플레이를 끝내도
    // 포션.asset의 이름은 '테스트'로 남는다
}
```

플레이 중에 씬 오브젝트의 값을 바꾸면, 플레이를 끝낼 때 원래대로 돌아온다. 기초 코스 내내 겪은 일이다. 그런데 ScriptableObject는 씬이 아니라 **프로젝트의 파일**이라서, 에디터에서 플레이 중에 바꾼 값이 플레이를 끝내도 **바뀐 채로 남는다.** 코드로 바꾸든 Inspector에서 바꾸든 마찬가지다.

빌드한 게임에서는 반대로, 실행 중에 바꾼 값이 파일에 저장되지 않는다. 게임을 다시 켜면 원래 값이다. 에디터와 빌드에서 결과가 다르니 더 헷갈린다.

그래서 규칙을 하나 정한다. **ScriptableObject는 읽기만 하는 원본 데이터로 쓴다.** 게임 중에 변하는 값은 각 오브젝트의 변수에 따로 둔다.

### 몬스터의 현재 체력은 어디에?

슬라임 세 마리가 모두 `슬라임.asset`을 쓴다고 하자. 맞을 때 에셋의 hp를 깎으면? 세 마리가 같은 파일을 가리키니 **세 마리가 같이 깎인다.** 그리고 에디터에서는 플레이가 끝나도 깎인 채로 남는다.

```csharp
public class Monster : MonoBehaviour
{
    [SerializeField] MonsterData data;   // 원본: 최대 체력, 속도...
    int currentHp;                       // 상태: 이 몬스터의 지금 체력

    void Start()
    {
        currentHp = data.maxHp;          // 시작할 때 원본에서 복사
    }

    public void TakeDamage(int amount)
    {
        currentHp -= amount;             // 내 것만 깎인다
    }
}
```

최대 체력은 원본(에셋)에서 **읽기만** 하고, 지금 체력은 각 몬스터가 **자기 변수**에 복사해서 쓴다. 한 마리가 맞으면 그 한 마리의 currentHp만 줄어든다.

| | 어디에 | 예 |
|---|---|---|
| 원본 데이터 | ScriptableObject 에셋 | 최대 체력, 이동 속도, 드랍 목록 |
| 실행 중 상태 | 각 오브젝트의 변수 | 지금 체력, 지금 상태, 다음 공격 시각 |

## 4. 데이터 구조 설계하기
{:.briefing-heading}

데이터 에셋이 다른 데이터 에셋을 품을 수도 있다. 몬스터가 죽으면 떨어뜨리는 아이템 목록이다.

```csharp
using System.Collections.Generic;
using UnityEngine;

[CreateAssetMenu(menuName = "Game/Monster")]
public class MonsterData : ScriptableObject
{
    public string monsterName;
    public int maxHp;
    public float moveSpeed;
    public List<ItemData> drops;
}
```

Inspector의 Drops 목록에 `포션.asset`, `열쇠.asset`을 끌어다 넣을 수 있다. 몬스터 데이터 → 아이템 데이터로 이어지는 구조다. 기획서에서 "몬스터 표의 드랍 칸에 아이템 ID를 적는" 것과 같다.

죽을 때 하나를 랜덤으로 고르려면 Day 3의 배열 뽑기를 그대로 쓴다.

```csharp
ItemData drop = data.drops[Random.Range(0, data.drops.Count)];
```

List니까 `Length`가 아니라 `Count`다(기초 Day 3). int 버전 `Random.Range`는 끝값을 빼니 0부터 Count - 1까지 딱 맞게 나온다.

### 고블린 강화판은 복제해서 숫자만

"고블린보다 세고 빠른 엘리트 고블린"이 필요하면? `고블린.asset`을 선택하고 **Ctrl + D**로 복제해서 이름과 숫자만 바꾼다. 새 스크립트도, if문도 필요 없다. **코드 수정 없이 콘텐츠를 늘리는 구조**라서, 혼자 만드는 게임에서 특히 강력하다.

## 직접 해 보기
{:.briefing-heading}

Day 4~5의 적이 숫자를 데이터 에셋에서 읽게 바꾸고, 슬라임과 고블린을 만든다.

### A. 적 데이터 만들기

1. `EnemyData` 스크립트를 만들고 내용을 바꾼다.

```csharp
using UnityEngine;

[CreateAssetMenu(menuName = "Game/Enemy Data")]
public class EnemyData : ScriptableObject
{
    [Header("기본 정보")]
    public string enemyName = "슬라임";
    public Color idleColor = Color.white;

    [Header("움직임")]
    [Range(0.5f, 10f)] public float moveSpeed = 2f;
    [Tooltip("이 거리 안에 들어오면 쫓아온다")]
    public float chaseRange = 5f;
    [Tooltip("이 거리 안이면 공격한다")]
    public float attackRange = 1.5f;

    [Header("공격")]
    public int attackDamage = 10;
    public float attackCooldown = 1f;
}
```

2. Project 창에 `Data` 폴더를 만들고, 그 안에서 우클릭 → **Create → Game → Enemy Data**. 이름을 `Slime`으로 한다.
3. Slime을 선택하고 Inspector에서 값을 채운다. 이름 슬라임, Idle Color 초록, Move Speed 1.5, Chase Range 5, Attack Range 1.5, Attack Damage 10, Attack Cooldown 1.5. Header가 소제목으로, Range가 슬라이더로 보이고, Chase Range 칸에 마우스를 올리면 Tooltip 설명이 뜬다.
4. Slime을 선택한 채 **Ctrl + D**로 복제하고 이름을 `Goblin`으로 바꾼다. 이름 고블린, Idle Color 파랑, Move Speed 3.5, Chase Range 7, Attack Damage 20, Attack Cooldown 0.8.

### B. 적이 데이터를 읽게

`Enemy`를 아래처럼 바꾼다. 숫자 칸 다섯 개가 `data` 칸 하나로 바뀌었고, 쓰는 곳마다 `data.`가 붙었다. Day 5에서 넣은 OnEnable, OnDisable, StopAttack도 들어 있다.

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
    [SerializeField] EnemyData data;

    // 지금 상태 (Inspector에서 보기용)
    [SerializeField] State state = State.Idle;

    float nextAttackTime = 0f;
    Renderer rend;

    void Start()
    {
        rend = GetComponent<Renderer>();
        rend.material.color = data.idleColor;
    }

    void OnEnable()
    {
        player.OnDied += StopAttack;
    }

    void OnDisable()
    {
        player.OnDied -= StopAttack;
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
        if (dist < data.chaseRange)
            ChangeState(State.Chase);
    }

    void UpdateChase(float dist)
    {
        Vector3 target = player.transform.position;
        target.y = transform.position.y;
        transform.position = Vector3.MoveTowards(transform.position, target, data.moveSpeed * Time.deltaTime);

        if (dist < data.attackRange)
            ChangeState(State.Attack);
        else if (dist > data.chaseRange + 2f)
            ChangeState(State.Idle);
    }

    void UpdateAttack(float dist)
    {
        if (dist > data.attackRange + 0.5f)
        {
            ChangeState(State.Chase);
            return;
        }

        if (Time.time >= nextAttackTime)
        {
            player.TakeDamage(data.attackDamage);
            nextAttackTime = Time.time + data.attackCooldown;
        }
    }

    void StopAttack()
    {
        ChangeState(State.Idle);
        enabled = false;
    }

    void ChangeState(State next)
    {
        if (state == next) return;

        Debug.Log(data.enemyName + ": " + state + " → " + next);
        state = next;

        switch (next)
        {
            case State.Idle:
                rend.material.color = data.idleColor;
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

`nextAttackTime`과 `state`는 data로 옮기지 않았다. 적마다 지금 상태, 다음 공격 시각이 다르니까. 위에서 본 "원본 데이터와 실행 중 상태 나누기"가 그대로 적용됐다.

### C. 슬라임과 고블린

1. Enemy를 선택하고 **Data** 칸에 `Slime`을 끌어다 놓는다. 이름도 `Slime`으로 바꾼다.
2. **Ctrl + D**로 복제해서 이름을 `Goblin`으로 바꾸고, 다른 곳(예: X = 6, Z = 6)에 둔다. Data 칸에 `Goblin`을 끌어다 놓는다.
3. 플레이한다. 초록 슬라임은 천천히 쫓아오고, 파란 고블린은 멀리서도 알아채고 빠르게 달려와 세게 때린다. 콘솔에 "슬라임: Idle → Chase", "고블린: Idle → Chase"처럼 누가 바뀌었는지 찍힌다. **Enemy 스크립트는 하나**인데 데이터만 달라서 다르게 움직인다.

Day 5에서 클리어하면 적을 멈추게 한 **On Cleared ()** 칸에는 처음 Enemy(지금의 Slime)만 들어 있다. 고블린도 같이 멈추게 하려면 +를 눌러 Goblin을 추가한다.

### D. 함정 체험: 플레이 중에 에셋 바꾸기

1. 슬라임을 Ctrl + D로 하나 더 복제한다. 이제 Slime 데이터를 쓰는 적이 둘이다.
2. 플레이 중에 Project 창의 `Slime` 에셋을 선택하고 Move Speed를 6으로 올린다. **슬라임 두 마리가 동시에** 빨라진다. 둘 다 같은 파일을 가리키고 있다는 증거다.
3. 플레이를 끈다. Slime 에셋의 Move Speed를 다시 보자. **6 그대로**다. 씬 오브젝트의 값이었다면 원래대로 돌아왔을 것이다.
4. 1.5로 되돌려 둔다.

플레이 중에 데이터를 만지며 밸런스를 맞출 때는 오히려 편한 성질이다. 마음에 드는 값을 찾으면 그대로 남으니까. 대신 **코드로** 에셋 값을 바꾸는 실수를 하면 몰래 데이터가 망가진다는 걸 기억하자.

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. Create 메뉴에 Game이 안 보여.**<br>
세 가지를 본다. 콘솔에 빨간 컴파일 에러가 있으면 새 코드가 반영되지 않는다. `[CreateAssetMenu]` 줄이 클래스 바로 위에 있는지 본다. 그리고 파일 이름과 클래스 이름(`EnemyData`)이 같은지 본다. ScriptableObject도 MonoBehaviour처럼 이름이 같아야 한다.

**Q. 적을 프리팹으로 만들었더니 Player 칸이 비어 있어.**<br>
심화 Day 3에서 말한 그 문제다. 프리팹 원본은 씬 안의 플레이어를 가리킬 수 없다. 스포너로 적을 찍어낸다면, Instantiate가 돌려준 적에게 플레이어를 넣어 준다.

```csharp
// Enemy에 추가
public void SetTarget(PlayerHealth target)
{
    player = target;
}

// 스포너에서
Enemy e = Instantiate(enemyPrefab, pos, Quaternion.identity);
e.SetTarget(player);
```

다만 Enemy의 OnEnable은 Instantiate 하는 **그 순간** 불린다. SetTarget보다 먼저라서, 그때는 player가 아직 비어 있어 `player.OnDied += ...`에서 에러가 난다. 이렇게 찍어내는 적은 구독을 OnEnable 대신 SetTarget 안에서 하는 식으로 순서를 맞춰야 한다. 실행 순서는 다지기 Day 4에서 자세히 다룬다.

**Q. ScriptableObject에서는 Start, Update를 못 써?**<br>
못 쓴다. 씬에 있는 게 아니라서 유니티가 매 프레임 불러 주지 않는다. 데이터를 담고, 계산 함수(예: 레벨에 따른 공격력 계산)를 넣는 정도로 쓴다.

**Q. 데이터 에셋의 칸 이름을 바꿨더니 값이 다 날아갔어.**<br>
유니티는 변수 **이름**으로 값을 저장한다. `moveSpeed`를 `speed`로 바꾸면 유니티 입장에서는 새 칸이라 비어 있다. 에셋을 많이 만든 뒤에는 변수 이름을 함부로 바꾸지 않는다. 꼭 바꿔야 하면 `[FormerlySerializedAs("moveSpeed")]`라는 어트리뷰트로 옛 이름을 알려 주면 값이 이어진다. 파일 맨 위에 `using UnityEngine.Serialization;`이 필요하다.

**Q. 엑셀로 정리한 데이터가 수백 줄인데, 에셋을 하나씩 만들어야 해?**<br>
손으로 하면 그렇다. 그래서 실무에서는 엑셀이나 구글 시트를 CSV로 내보내고, 에디터 도구로 에셋을 자동으로 만든다. 시스템 코스 Day 6 "CSV → ScriptableObject 변환기"에서 다룬다.

## 현업에서는
{:.briefing-heading}

- **데이터 주도 설계.** 숫자와 목록은 코드 밖(에셋, 테이블)에 두고, 코드는 "데이터를 읽어서 동작하는 틀"만 갖는다. 기획자가 프로그래머를 기다리지 않고 밸런스를 바꿀 수 있고, 새 몬스터를 넣을 때 코드 리뷰가 필요 없다.
- **원본과 상태를 섞지 않는다.** 오늘의 "현재 체력은 오브젝트에" 규칙은 실무에서 아주 엄격하게 지킨다. 에셋 값을 코드로 바꾸는 줄이 있으면 리뷰에서 바로 질문받는다.
- **에셋 이름 규칙을 정한다.** `Enemy_Slime`, `Enemy_Goblin`, `Item_Potion`처럼 종류를 앞에 붙이면 Project 창 검색과 정렬이 편하다. 데이터가 수백 개가 되면 차이가 크다.
- **이벤트 채널로도 쓴다.** ScriptableObject 안에 `event Action`을 넣어 두고, 방송하는 쪽과 듣는 쪽이 같은 에셋을 끌어다 놓아 연결하는 방식도 있다. Day 5에서 HpLogger가 플레이어를 직접 알아야 했던 것까지 없앨 수 있다. 구조가 커지면 찾아볼 만한 패턴이다.

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **심화 Day 6**과 같은 내용이다.

- [데이터를 에셋으로 만들기](https://hlcho426.github.io/unity-csharp-week/#a6l1): CreateAssetMenu, Inspector 꾸미기
- [데이터 에셋 사용하기](https://hlcho426.github.io/unity-csharp-week/#a6l2): 참조, 공유, 플레이 중 변경 주의
- [데이터 구조 설계하기](https://hlcho426.github.io/unity-csharp-week/#a6l3): SO 안에 SO, 리스트, 원본과 상태 나누기

## 정리
{:.briefing-heading}

- `: ScriptableObject`를 붙이면 오브젝트에 안 붙는 **데이터 파일(에셋)**이 된다
- `[CreateAssetMenu(menuName = "Game/Item")]`로 Create 메뉴에 추가해서 에셋을 만든다
- `[SerializeField] ItemData item;` 칸에 에셋을 끌어다 놓고 `item.price`처럼 읽는다. 여러 오브젝트가 같은 에셋을 가리키니 하나만 고치면 모두 바뀐다
- 에디터에서 플레이 중에 에셋 값을 바꾸면 끝나도 남는다. 에셋은 읽기만 하는 원본으로 쓴다
- 원본 데이터는 에셋에, 지금 체력 같은 실행 중 상태는 각 오브젝트의 변수에
- `[Header]`, `[Range]`, `[Tooltip]`, `[TextArea]`로 Inspector를 보기 좋게 꾸민다

다음 글은 심화 Day 7, 세이브와 로드. 최고 기록을 PlayerPrefs로 저장하고, 코인 수와 위치를 JSON 파일로 저장했다가 불러온다.
