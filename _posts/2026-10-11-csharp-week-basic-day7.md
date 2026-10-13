---
title: "<유니티 C#> 기초 Day 7: 미니 프로젝트, 코인 줍기 (OnTriggerEnter, CompareTag, Destroy)"
date: 2026-10-11 22:36:00 +0900
description: "OnTriggerEnter와 CompareTag, Destroy로 만드는 코인 줍기 미니 게임. Trigger가 안 될 때 확인할 것과 완성 스크립트 읽기까지."
series: 유니티 C# 일주일
series_title: "기초 Day 7: 미니 프로젝트 코인 줍기"
categories: [게임 제작 공부, 유니티]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

일주일 동안 배운 걸 모아서 작은 게임을 하나 만든다. 방향키로 움직이고 스페이스로 점프하는 캐릭터가 바닥에 흩어진 코인을 모두 주우면 클리어. [Day 6](/posts/csharp-week-basic-day6/)의 `PlayerController`에 "닿았다"를 감지하는 기능만 더하면 된다.

**오늘의 목표**

- Trigger와 `OnTriggerEnter`로 "닿았다"를 감지할 수 있다
- 태그와 `CompareTag`로 닿은 게 무엇인지 확인할 수 있다
- `Destroy`로 오브젝트를 없앨 수 있다
- 완성된 스크립트를 위에서부터 읽고 설명할 수 있다

## 1. 닿았다는 걸 어떻게 알까: Trigger
{:.briefing-heading}

Collider는 원래 **부딪혀서 막는** 역할을 한다. 그런데 코인은 막히면 안 되고, 지나가면서 주워져야 한다. 이럴 때 Collider의 **Is Trigger**를 체크한다. 그러면 부딪혀 막지 않고 통과하면서 "닿았다"는 신호만 보낸다.

신호가 오면 유니티가 이 함수를 불러 준다.

```csharp
void OnTriggerEnter(Collider other)
{
    Debug.Log(other.name + "에 닿음");
}
```

`Start`, `Update`처럼 유니티가 대신 불러 주는 함수라서 **이름이 정확해야** 한다. `ontriggerenter`나 `OnTriggerenter`로 쓰면 에러도 안 나고 그냥 아무 일도 안 일어난다. 찾기 어려운 버그 1순위다.

괄호 안의 `other`는 **내가 닿은 상대의 Collider**다.

### Trigger가 작동하는 조건

Trigger 신호가 오려면 세 가지가 모두 맞아야 한다.

1. 두 오브젝트 모두 **Collider**가 있다
2. 둘 중 하나는 **Is Trigger**가 켜져 있다
3. 둘 중 하나는 **Rigidbody**가 있다

플레이어 큐브에는 Day 6에서 붙인 Rigidbody가 있으니, 코인에는 Collider(Is Trigger 켬)만 있으면 된다.

## 2. 닿은 게 코인일 때만: 태그와 CompareTag
{:.briefing-heading}

플레이어는 코인 말고도 바닥, 벽, 적에 닿는다. 코인일 때만 반응하려면 코인에 **태그**를 달아 둔다.

- 코인을 선택하고 Inspector 맨 위의 **Tag** 드롭다운 → **Add Tag...** → +로 `Coin`을 만든다
- 다시 코인을 선택하고 Tag를 `Coin`으로 고른다

```csharp
void OnTriggerEnter(Collider other)
{
    if (other.CompareTag("Coin"))
    {
        Destroy(other.gameObject);
    }
}
```

`other.CompareTag("Coin")`은 "닿은 상대의 태그가 Coin인가?"를 묻고 true/false를 돌려준다. 맞으면 `Destroy`로 없앤다.

### Destroy(other)와 Destroy(other.gameObject)

`other`는 **Collider 컴포넌트**다. 그래서 `Destroy(other)`는 코인의 Collider 컴포넌트만 지운다. 코인은 화면에 그대로 남는다. 오브젝트를 통째로 없애려면 그 컴포넌트가 붙은 **게임 오브젝트**를 가리키는 `other.gameObject`를 넘긴다.

## 3. 점수 세고 클리어하기
{:.briefing-heading}

```csharp
int coin = 0;
[SerializeField] int goal = 5;

void OnTriggerEnter(Collider other)
{
    if (other.CompareTag("Coin"))
    {
        Destroy(other.gameObject);
        coin++;
        Debug.Log("코인: " + coin + " / " + goal);

        if (coin >= goal)
        {
            Debug.Log("스테이지 클리어!");
        }
    }
}
```

변수, `++`, 글자 더하기, if, `[SerializeField]`. Day 1~2에 배운 것이 그대로 쓰인다.

- 목표 개수 `goal`을 `[SerializeField]`로 꺼내 두면 스테이지마다 Inspector에서 다르게 정할 수 있다
- 클리어 조건을 `coin == goal`이 아니라 `coin >= goal`로 쓴 건, 혹시 목표보다 많이 주워도 클리어를 놓치지 않게 하려는 것이다

이 코드에는 문제가 하나 있다. 5개를 넘게 주우면 6개째, 7개째에도 "스테이지 클리어!"가 또 찍힌다. "이미 했는지"를 기억하는 bool 깃발로 막는다.

```csharp
bool isCleared = false;

// ...
if (coin >= goal && !isCleared)
{
    isCleared = true;
    Debug.Log("스테이지 클리어!");
}
```

## 4. 땅에 닿았을 때만 착지
{:.briefing-heading}

Day 6에서는 "아무거나 부딪히면 착지"였다. 코인은 Trigger라 부딪힘에 안 걸리지만, 나중에 벽이 생기면 벽에 닿아도 점프가 다시 충전된다. 바닥에 `Ground` 태그를 달고 바닥에 부딪혔을 때만 착지로 친다.

```csharp
void OnCollisionEnter(Collision col)
{
    if (col.gameObject.CompareTag("Ground"))
        isGrounded = true;
}
```

`OnCollisionEnter`는 Trigger가 아닌 **진짜 부딪힘**을 감지하는 짝꿍 함수다. 받는 값이 `Collision`이라서, 상대 오브젝트는 `col.gameObject`로 꺼낸다.

`Ground`도 Coin처럼 유니티에 기본으로 있는 태그가 아니라서, 직접 만들어 바닥에 달아야 한다(아래 "직접 해 보기" 1번). 태그를 만들지 않고 `CompareTag("Ground")`를 쓰면 "그런 태그는 없다"는 에러가 나고, 만들었는데 바닥에 안 붙이면 에러 없이 점프가 한 번만 된다.

> 현업에서는: 태그도 완벽하지는 않다. 태그는 **무엇에** 부딪혔는지만 보고 **어디에** 닿았는지는 안 본다. 그래서 Ground 태그가 붙은 상자의 옆면에 공중에서 부딪혀도 착지로 처리된다. 그래서 실무에서는 발밑으로 짧은 광선을 쏴서(**Raycast**) 바로 아래에 땅이 있는지 확인하는 방법을 많이 쓴다.
>
> ```csharp
> bool IsGrounded()
> {
>     // 큐브 중심에서 아래로 0.6m 광선을 쏴서 무언가 맞으면 땅 위다
>     // (높이 1인 큐브라 중심에서 바닥까지 0.5m + 여유 0.1m)
>     return Physics.Raycast(transform.position, Vector3.down, 0.6f);
> }
> ```
>
> 지금은 태그 방식으로 충분하고, 캐릭터 조작을 다듬을 때 이 방식으로 바꾸면 된다.
{: .prompt-tip }

## 직접 해 보기
{:.briefing-heading}

1. Day 6의 Plane을 선택하고 Tag에 `Ground`를 새로 만들어 단다.
2. **3D Object → Sphere**를 만들고 Scale을 0.5로 줄인다. Sphere Collider의 **Is Trigger**를 체크하고 Tag를 `Coin`으로 단다.
3. 코인을 선택하고 **Ctrl + D**로 4개 더 복제해서 바닥 여기저기에 흩어 놓는다. 높이는 Y = 0.5 정도.
4. 큐브의 `PlayerController`를 완성본으로 바꾼다.

```csharp
using UnityEngine;

public class PlayerController : MonoBehaviour
{
    [SerializeField] float speed = 5f;
    [SerializeField] float jumpPower = 6f;
    [SerializeField] int goal = 5;

    Rigidbody rb;
    int coin = 0;
    bool isGrounded = true;
    bool isCleared = false;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
    }

    void Update()
    {
        float h = Input.GetAxis("Horizontal");
        float v = Input.GetAxis("Vertical");
        Vector3 dir = new Vector3(h, 0f, v);
        transform.position += dir * speed * Time.deltaTime;

        if (Input.GetKeyDown(KeyCode.Space) && isGrounded)
        {
            rb.AddForce(Vector3.up * jumpPower, ForceMode.Impulse);
            isGrounded = false;
        }
    }

    void OnCollisionEnter(Collision col)
    {
        if (col.gameObject.CompareTag("Ground"))
            isGrounded = true;
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Coin"))
        {
            Destroy(other.gameObject);
            coin++;
            Debug.Log("코인: " + coin + " / " + goal);

            if (coin >= goal && !isCleared)
            {
                isCleared = true;
                Debug.Log("스테이지 클리어!");
            }
        }
    }
}
```

플레이해서 코인을 다 주워 보자. 콘솔에 "코인: 1 / 5"부터 "스테이지 클리어!"까지 찍히면 성공이다.

### 위에서부터 읽기

이 스크립트는 거의 모든 유니티 스크립트의 뼈대를 그대로 보여 준다.

1. **변수**: 조절할 수치는 `[SerializeField]`로, 내부 상태는 그냥 변수로
2. **Start**: 필요한 컴포넌트를 찾아 준비
3. **Update**: 매 프레임 입력을 확인하고 움직이기
4. **이벤트 함수**: 부딪히거나 닿았을 때 반응하기

모르는 줄이 하나도 없다면 일주일 코스는 성공이다. 읽을 수 있으면 고칠 수 있고, 고칠 수 있으면 만들 수 있다.

### 더 해 보기

코인이 제자리에서 빙글빙글 돌면 훨씬 코인 같다. `Coin` 스크립트를 만들어 코인 하나에 붙여 보자.

```csharp
using UnityEngine;

public class Coin : MonoBehaviour
{
    [SerializeField] float turnSpeed = 180f;

    void Update()
    {
        transform.Rotate(Vector3.up * turnSpeed * Time.deltaTime);
    }
}
```

나머지 4개에도 일일이 붙이기 귀찮다면, 그게 바로 **프리팹**이 필요한 순간이다. 심화 Day 3에서 배운다.

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. 코인을 지나가도 아무 반응이 없어.**<br>
이 순서로 확인한다.

1. 코인 Collider의 **Is Trigger**가 켜져 있나
2. 플레이어에 **Rigidbody**가 있나
3. 함수 이름이 정확히 `OnTriggerEnter(Collider other)`인가
4. 코인의 Tag가 정확히 `Coin`인가 (대소문자까지)
5. 2D 게임이라면 Collider 2D와 `OnTriggerEnter2D(Collider2D other)`를 써야 한다. 3D용과 2D용은 서로 신호를 주고받지 않는다

함수 첫 줄에 `Debug.Log("닿음");`을 넣어 보면 함수 자체가 불리는지부터 알 수 있다.

**Q. `other.tag == "Coin"`으로 써도 되지 않아?**<br>
동작은 하지만 `CompareTag`를 쓰는 게 좋다. 조금 더 빠르고, 프로젝트에 없는 태그 이름을 쓰면 에러로 알려 줘서 오타를 잡기 쉽다.

**Q. Destroy한 다음 줄에서 그 코인을 써도 돼?**<br>
`Destroy`는 그 자리에서 바로 지우지 않고 이번 프레임이 끝날 때 지운다. 그래서 같은 함수의 바로 다음 줄에서는 아직 남아 있다. 하지만 다음 프레임부터는 지워진 오브젝트라 건드리면 `MissingReferenceException`이 난다. 코인의 정보가 필요하면 Destroy 전에 읽어 두는 습관이 안전하다.

## 현업에서는
{:.briefing-heading}

- **같은 오브젝트는 프리팹으로 만든다.** 코인 50개를 복사해 두면 디자인을 바꿀 때 50개를 다 고쳐야 한다. 프리팹으로 만들면 원본 하나만 고치면 된다.
- **Debug.Log 대신 UI에 표시한다.** 실제 게임에서는 콘솔이 아니라 화면에 "코인: 3 / 5"를 띄운다. 실전 Day 5에서 텍스트와 체력바를 연결한다.
- **주운 뒤의 일은 나눠 둔다.** 코인을 주우면 소리, 이펙트, 점수 UI, 업적이 동시에 반응해야 한다. 플레이어 스크립트가 이걸 다 직접 부르면 금방 엉킨다. 심화 Day 5의 이벤트로 깔끔하게 나눈다.

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **기초 Day 7**과 같은 내용이다.

- [충돌 감지: OnTriggerEnter](https://hlcho426.github.io/unity-csharp-week/#d7l1): Is Trigger, CompareTag, Destroy
- [점수 세고 클리어하기](https://hlcho426.github.io/unity-csharp-week/#d7l2): 카운트, 조건, UI 문자열
- [완성 코드 읽기](https://hlcho426.github.io/unity-csharp-week/#d7l3): 일주일 배운 걸 한 스크립트로

## 정리
{:.briefing-heading}

- Collider의 Is Trigger를 켜면 통과하면서 감지만 한다. 감지되면 `OnTriggerEnter(Collider other)`가 불린다
- Trigger는 양쪽 Collider + 한쪽 Is Trigger + 한쪽 Rigidbody가 있어야 작동한다
- `other.CompareTag("Coin")`으로 무엇인지 확인한다
- 오브젝트째 없애려면 `Destroy(other.gameObject)`
- "한 번만"은 bool 깃발로. 진짜 부딪힘은 `OnCollisionEnter(Collision col)`
- 변수 → Start에서 준비 → Update에서 입력·이동 → 이벤트 함수에서 반응. 이게 유니티 스크립트의 뼈대다

다음 글은 기초 Day 8, 변수의 범위와 함수의 흐름. 기초 코스의 마지막 날이다.
