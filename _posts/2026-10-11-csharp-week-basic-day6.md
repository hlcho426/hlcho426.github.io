---
title: "유니티 C# 기초 Day 6: 키 입력으로 캐릭터 움직이기 (GetKey, GetAxis, AddForce 점프)"
date: 2026-10-11 22:32:00 +0900
description: "GetKeyDown과 GetKey의 차이, GetAxis로 방향키 이동, Rigidbody.AddForce로 점프하고 무한 점프 막기. Unity 6 입력 설정 주의점도 정리했다."
series: 유니티 C# 일주일
series_title: "기초 Day 6: 입력과 이동, 점프"
categories: [유니티 공부]
tags: [유니티, C#, Input, GetKeyDown, GetAxis, Rigidbody, AddForce, 유니티 C# 일주일]
---

{% include series.html %}

[Day 5](/posts/csharp-week-basic-day5/)에서 큐브를 코드로 움직였다. 오늘은 그 움직임을 **키보드로 조종**한다. 방향키로 걷고, 스페이스로 점프한다. 지금까지 배운 변수, if, 함수, Transform이 전부 한 스크립트에 모인다.

**오늘의 목표**

- `GetKeyDown`, `GetKey`, `GetKeyUp`의 차이를 안다
- `Input.GetAxis`로 방향키 입력을 받아 캐릭터를 움직일 수 있다
- Rigidbody에 `AddForce`로 힘을 줘서 점프시킬 수 있다
- 공중에서 계속 점프하는 버그를 막을 수 있다

> 이 글의 코드는 유니티의 기존 입력 방식(`Input` 클래스)을 쓴다. Unity 6의 새 프로젝트에서 `InvalidOperationException` 에러가 나면, [Day 0](/posts/csharp-week-basic-day0/)에서 설명한 대로 **Active Input Handling**을 **Both**로 바꾼다. 새 Input System은 실전 Day 6에서 배운다.
{: .prompt-warning }

## 1. 키 입력 세 가지

```csharp
void Update()
{
    if (Input.GetKeyDown(KeyCode.Space))
        Debug.Log("눌렀다!");

    if (Input.GetKey(KeyCode.Space))
        Debug.Log("누르는 중...");

    if (Input.GetKeyUp(KeyCode.Space))
        Debug.Log("뗐다!");
}
```

| 함수 | 언제 true? | 어디에 쓰나 |
|---|---|---|
| `GetKeyDown` | 누른 **순간** 한 프레임 | 점프, 공격, 상호작용 |
| `GetKey` | 누르고 **있는 동안** 매 프레임 | 달리기, 계속 쏘기 |
| `GetKeyUp` | 뗀 **순간** 한 프레임 | 차지 공격 발사 |

키 이름은 `KeyCode.Space`, `KeyCode.E`, `KeyCode.LeftShift`처럼 쓴다. `Input.GetKeyDown("E")`처럼 글자로 넣는 방식보다 `KeyCode`를 쓰는 게 오타가 없다.

입력은 **Update 안에서** 검사한다. 키는 언제 눌릴지 모르니 매 프레임 확인해야 한다. Start에 넣으면 게임 시작 순간에 딱 한 번만 확인하고 끝난다.

점프를 `GetKey`로 만들면 스페이스를 누르고 있는 동안 매 프레임 점프해서 로켓처럼 날아간다. "한 번"은 `GetKeyDown`이다.

## 2. 방향키로 이동: GetAxis

방향키 네 개를 하나씩 `GetKey`로 검사하지 않아도 된다.

```csharp
float h = Input.GetAxis("Horizontal");   // ←: -1, →: 1
float v = Input.GetAxis("Vertical");     // ↓: -1, ↑: 1
```

`GetAxis`는 방향키, WASD, 게임패드 스틱 입력을 **-1에서 1 사이 숫자**로 알려 준다. 아무것도 안 누르면 0이다.

이 숫자를 방향으로 만들어 Day 5의 이동 공식에 넣으면 끝이다.

```csharp
public class PlayerMove : MonoBehaviour
{
    [SerializeField] float speed = 5f;

    void Update()
    {
        float h = Input.GetAxis("Horizontal");
        float v = Input.GetAxis("Vertical");

        Vector3 dir = new Vector3(h, 0f, v);
        transform.position += dir * speed * Time.deltaTime;
    }
}
```

h는 x(좌우)에, v는 z(앞뒤)에 넣었다. y는 0이다. 땅 위를 걷는 거니까. 만약 v를 y에 넣으면 위 키를 누를 때 하늘로 날아간다. 2D 게임이라면 그게 맞을 수도 있다.

아무 키도 안 누르면 h, v가 0이라 dir도 (0, 0, 0)이고, 0에 무엇을 곱해도 0이라 제자리다.

## 3. 점프: Rigidbody에 힘 주기

점프는 위로 올라갔다가 중력으로 떨어져야 한다. 이걸 직접 계산하는 대신 유니티의 물리 엔진에 맡긴다. **Rigidbody** 컴포넌트를 붙이면 그 오브젝트에 중력과 물리가 적용된다.

```csharp
[SerializeField] float jumpPower = 6f;
Rigidbody rb;

void Start()
{
    rb = GetComponent<Rigidbody>();
}

void Update()
{
    if (Input.GetKeyDown(KeyCode.Space))
    {
        rb.AddForce(Vector3.up * jumpPower, ForceMode.Impulse);
    }
}
```

`AddForce(방향 * 힘, ForceMode.Impulse)`는 "이 방향으로 이만큼 힘을 줘라"다. `ForceMode.Impulse`는 힘을 **한 번에 팍** 주는 방식이라 점프에 딱 맞는다.

Rigidbody는 Day 5에서 배운 대로 Start에서 한 번 가져와 저장해 둔다.

### 무한 점프 막기

위 코드는 공중에서도 스페이스를 누를 때마다 또 점프한다. 땅에 있을 때만 점프하게 하려면 "땅에 있나?"를 기억하는 bool이 필요하다.

```csharp
bool isGrounded = true;

void Update()
{
    if (Input.GetKeyDown(KeyCode.Space) && isGrounded)
    {
        rb.AddForce(Vector3.up * jumpPower, ForceMode.Impulse);
        isGrounded = false;   // 점프하면 공중
    }
}

void OnCollisionEnter(Collision collision)
{
    isGrounded = true;        // 무언가에 부딪히면(착지하면) 다시 땅
}
```

Day 2의 `&&`가 여기서 나온다. "스페이스를 눌렀고 **그리고** 땅에 있으면". `OnCollisionEnter`는 무언가와 부딪힌 순간 유니티가 불러 주는 함수다. 지금은 "아무거나 부딪히면 착지"로 간단히 했다. 바닥에만 반응하게 만드는 방법은 Day 7에서 배운다.

## 직접 해 보기

1. Hierarchy에서 **3D Object → Plane**을 만든다. 바닥이 된다.
2. 큐브를 바닥보다 조금 위(Position Y = 1)에 둔다.
3. 큐브의 Inspector에서 **Add Component → Rigidbody**를 붙인다. 플레이하면 큐브가 바닥으로 떨어지는지 확인한다.
4. Rigidbody의 **Constraints → Freeze Rotation**에서 X, Z를 체크한다. 이동하다 큐브가 데굴데굴 넘어지는 걸 막는다.
5. 큐브에 `PlayerController` 스크립트를 만들어 붙인다. 이전에 붙인 `Mover`는 꺼 둔다(Inspector에서 이름 옆 체크 해제).

```csharp
using UnityEngine;

public class PlayerController : MonoBehaviour
{
    [SerializeField] float speed = 5f;
    [SerializeField] float jumpPower = 6f;

    Rigidbody rb;
    bool isGrounded = true;

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

    void OnCollisionEnter(Collision collision)
    {
        isGrounded = true;
    }
}
```

플레이하고 Game 창을 한 번 클릭한 뒤 방향키(또는 WASD)와 스페이스를 눌러 보자. 해 볼 것.

- Jump Power를 3, 10으로 바꿔 보기
- `GetKeyDown`을 `GetKey`로 바꾸면? (로켓)
- `isGrounded = false;` 줄을 지우면? (공중 연속 점프)
- 왼쪽 Shift를 누르는 동안 두 배로 빨라지게 만들어 보기. 힌트: `GetKey(KeyCode.LeftShift)`와 if

## 자주 헷갈리는 것

**Q. 대각선으로 가면 더 빨라.**<br>
맞다. →와 ↑를 같이 누르면 dir이 (1, 0, 1)이 되는데, 이 방향의 길이는 1이 아니라 약 1.41이다. 그래서 대각선이 41% 빠르다. `dir = Vector3.ClampMagnitude(dir, 1f);`를 이동 전에 한 줄 넣으면 길이가 1을 넘지 않게 잘라 준다.

**Q. 키를 떼도 캐릭터가 살짝 미끄러지다 멈춰.**<br>
`GetAxis`는 0에서 1로 바로 뛰지 않고 부드럽게 올라갔다 내려간다. 미끄러짐 없이 딱딱 끊기는 조작을 원하면 `Input.GetAxisRaw`를 쓴다. -1, 0, 1 중 하나만 나온다.

**Q. 키를 눌러도 반응이 없어.**<br>
Game 창을 클릭해서 게임 화면에 포커스가 가 있는지 확인한다. 그래도 안 되면 콘솔에 빨간 에러가 있는지 본다. `InvalidOperationException`이면 위의 Active Input Handling 설정 문제다.

**Q. 점프가 안 되고 `MissingComponentException` 에러가 나.**<br>
큐브에 Rigidbody를 안 붙였다. `GetComponent<Rigidbody>()`가 아무것도 못 찾아서 rb가 비어 있는 상태로 AddForce를 부른 것이다.

## 현업에서는

- **입력은 Update, 물리는 FixedUpdate.** 물리 계산은 FixedUpdate라는 다른 함수에서 일정한 간격으로 하는 게 정석이다. 다만 `GetKeyDown`은 FixedUpdate에서 검사하면 가끔 놓쳐서, 입력은 Update에서 bool로 기억해 두고 FixedUpdate에서 처리한다. 한 번 팍 주는 점프는 Update에서 해도 대부분 괜찮다. 자세한 건 다지기 Day 4 "유니티 실행 순서"에서 다룬다.
- **Rigidbody가 있으면 속도로 움직인다.** 위 코드는 배우기 쉽게 Transform으로 옮겼지만, 물리가 붙은 캐릭터는 보통 Rigidbody의 속도를 바꿔서 움직인다. 벽에 박혔을 때 덜덜 떨리거나 뚫고 지나가는 문제가 줄어든다.

  ```csharp
  // Unity 6 기준. 이전 버전은 linearVelocity 대신 velocity
  Vector3 move = dir * speed;
  rb.linearVelocity = new Vector3(move.x, rb.linearVelocity.y, move.z);
  ```

- **새 프로젝트라면 새 Input System을 쓴다.** 키 대신 "점프", "이동" 같은 행동으로 입력을 받고, 키보드·게임패드·키 바꾸기를 한 번에 처리한다. 기존 `Input`으로 원리를 익히고 실전 Day 6에서 옮겨 간다.

## 앱에서 연습하기

이 글은 앱의 **기초 Day 6**과 같은 내용이다.

- [키 입력 받기](https://hlcho426.github.io/unity-csharp-week/#d6l1): GetKey, GetKeyDown, GetKeyUp
- [방향키로 이동하기](https://hlcho426.github.io/unity-csharp-week/#d6l2): Input.GetAxis
- [점프: 물리에 힘 주기](https://hlcho426.github.io/unity-csharp-week/#d6l3): Rigidbody.AddForce

## 정리

- `GetKeyDown` 누른 순간 한 번, `GetKey` 누르고 있는 동안 계속, `GetKeyUp` 뗀 순간 한 번
- 입력 검사는 Update 안에서
- `GetAxis("Horizontal")`, `GetAxis("Vertical")`는 -1 ~ 1. `방향 * speed * Time.deltaTime`으로 이동
- Rigidbody가 있으면 중력과 물리가 적용된다. `AddForce(방향 * 힘, ForceMode.Impulse)`로 순간적인 힘
- 점프는 `GetKeyDown && isGrounded`. 점프하면 false, 착지하면 true

다음 글은 기초 Day 7, 코인 줍기 미니 프로젝트.
