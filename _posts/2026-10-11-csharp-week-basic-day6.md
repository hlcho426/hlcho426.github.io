---
title: "<유니티 C#> 기초 Day 6: 키 입력으로 캐릭터 움직이기 (GetKey, GetAxis, AddForce 점프)"
date: 2026-10-11 22:32:00 +0900
description: "GetKeyDown과 GetKey의 차이, GetAxis로 방향키 이동, Rigidbody.AddForce로 점프하고 무한 점프 막기. Unity 6 입력 설정 주의점도 정리했다."
series: 유니티 C# 일주일
series_title: "기초 Day 6: 입력과 이동, 점프"
categories: [게임 제작 공부, 유니티]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
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

그런데 이렇게 바꾸면 유니티가 싫어함...<br>
일단 샘플 프로젝트니까 그냥 공부를 위해 both로 유지한다.
![인풋both유니티가싫어함](/assets/img/unitystudy/csharp_basic_day6_01.png){: w="1036" h="172" }


## 1. 키 입력 세 가지
{:.briefing-heading}

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

입력은 **Update 안에서** 검사한다. 키는 언제 눌릴지 모르니 매 프레임 확인해야 한다. Start에 넣으면 큐브가 처음 나타나는 순간에 딱 한 번만 확인하고 끝난다. 그 순간 키를 누르고 있지 않았다면 그걸로 끝이다.

점프를 `GetKey`로 만들면 스페이스를 누르고 있는 동안 매 프레임 점프해서 로켓처럼 날아간다. "한 번"은 `GetKeyDown`이다.

## 2. 방향키로 이동: GetAxis
{:.briefing-heading}

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
{:.briefing-heading}

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

Day 2의 `&&`가 여기서 나온다. "스페이스를 눌렀고 **그리고** 땅에 있으면". `OnCollisionEnter`는 무언가와 부딪힌 순간 유니티가 불러 주는 함수다.

### isGrounded가 바뀌는 세 순간

`isGrounded`는 "지금 땅에 있나?"를 기억하는 깃발이다. 딱 세 순간에만 바뀐다.

| 순간 | isGrounded | 바꾸는 줄 |
|---|---|---|
| 처음 | true | 함수 밖의 `bool isGrounded = true;` (처음 값, 한 번만) |
| 점프하는 순간 | false | Update의 `isGrounded = false;` |
| 착지하는 순간 | true | OnCollisionEnter의 `isGrounded = true;` |

그래서 땅에서 뛰어 공중에 떴다가 착지하면 true → false → true 순서로 바뀐다. 이 세 곳 말고 다른 데서 바꾸면 깃발이 거짓말을 하게 된다.

흔한 실수가 Update 안에 `isGrounded = true;`를 넣는 것이다. 맨 위의 `bool isGrounded = true;`는 처음 값을 정하는 줄이라 한 번만 실행되지만, Update 안에 쓰면 **매 프레임** "땅에 있음"이 된다. 점프해서 false로 바꿔도 다음 프레임에 바로 true가 되니, 공중에서도 계속 점프할 수 있다. true는 착지할 때만 넣는다.

그럼 "땅"은 어떻게 판단할까? 지금 코드는 **무엇에 부딪혔든 땅으로 친다.** 부딪힌 상대가 바닥인지는 따지지 않는다. 이 씬에서 큐브가 부딪힐 수 있는 게 바닥(Plane) 하나뿐이라, 지금은 "부딪힘 = 착지"가 맞아떨어진다.

그리고 유니티가 "부딪혔다"를 알려면 조건이 있다.

- **양쪽 모두 Collider(충돌 모양)가 있어야 한다.** Hierarchy에서 3D Object로 만든 Cube에는 Box Collider, Plane에는 Mesh Collider가 처음부터 붙어 있다. Collider를 지우면 큐브가 바닥을 그냥 뚫고 떨어지고, OnCollisionEnter도 불리지 않는다.
- **둘 중 적어도 하나에는 Rigidbody가 있어야 한다.** 여기서는 큐브에 붙였다. 물리 엔진이 움직이는 쪽이 있어야 충돌을 계산한다.
- **Collider의 Is Trigger가 꺼져 있어야 한다.** 켜면 막히지 않고 통과하면서 OnCollisionEnter 대신 OnTriggerEnter가 불린다. Day 7에서 코인에 쓰는 방식이다.

다만 "아무거나 부딪히면 착지"라서, 나중에 벽이 생기면 공중에서 벽에 닿기만 해도 점프가 다시 충전되는 버그가 생긴다. 바닥에만 반응하게 만드는 방법(바닥에 `Ground` 태그를 달아 확인하기)은 Day 7에서 배운다.

## 직접 해 보기
{:.briefing-heading}

1. Hierarchy에서 **3D Object → Plane**을 만든다. 바닥이 된다.

   > Plane을 선택하면 Inspector의 Mesh Collider에 노란 경고(`Mesh 'Plane' used by the Mesh Collider is missing pre-baked triangle collision...`)가 뜰 수 있다. 에러가 아니라 예고라서 그대로 진행해도 된다. Mesh Collider는 모델의 삼각형 모양 그대로 충돌을 계산하는데, 그 계산용 데이터를 지금은 빌드할 때 유니티가 자동으로 만들어 주지만 앞으로는 미리 만들어 두라는 뜻이다. 직접 가져온 모델이라면 Import 설정의 **Pre-bake Triangle Collision Mesh**를 켜면 되지만, Plane은 유니티 내장 도형이라 이 설정을 바꿀 수 없다.
   >
   > 평평한 바닥에는 삼각형 단위로 계산하는 Mesh Collider가 과하다. 경고를 없애고 싶으면 Mesh Collider를 지우고(⋮ → Remove Component) **Box Collider**를 붙인다. Size Y가 0이면 두께가 없어서 빠른 물체가 뚫을 수 있으니 Size Y 0.1, Center Y -0.05 정도로 두께를 준다. 또는 Cube를 Scale (10, 1, 10)으로 납작하게 늘려 바닥으로 써도 된다. 울퉁불퉁한 지형처럼 모양 그대로 부딪혀야 하는 움직이지 않는 물체에만 Mesh Collider를 쓴다.
   {: .prompt-warning }

   ![Mesh Collider 경고](/assets/img/unitystudy/csharp_basic_day6_02.png){: w="595" h="295" }

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
- `GetKeyDown`을 `GetKey`로 바꾸면? 스페이스를 누르고 있는 동안 착지하자마자 또 뛴다(토끼뜀). `&& isGrounded`가 "땅에 있을 때만"을 막아 주고 있어서 로켓까지는 안 된다. 조건에서 `&& isGrounded`까지 지우면 공중에서도 매 프레임 힘을 받아 로켓처럼 날아간다. 손을 떼도 한참 더 올라가고, 떨어질 때는 바닥을 뚫고 끝없이 떨어지기도 한다. 이유는 아래 "자주 헷갈리는 것"에 있다
- `isGrounded = false;` 줄을 지우면? (공중 연속 점프)
- 왼쪽 Shift를 누르는 동안 **이동 속도**가 두 배가 되게(달리기) 만들어 보기. 힌트: `GetKey(KeyCode.LeftShift)`와 if. 함정 주의: `speed *= 2f;`처럼 speed 자체를 바꾸면 Update가 매 프레임 돌면서 2배, 4배, 8배로 계속 불어나 순식간에 날아간다. 원래 speed는 그대로 두고, 이번 프레임에 쓸 속도를 `currentSpeed` 같은 변수에 따로 담아 쓴다

![Shift 달리기 코드](/assets/img/unitystudy/csharp_basic_day6_03.png){: w="515" h="259" }

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. 대각선으로 가면 더 빨라.**<br>
맞다. →와 ↑를 같이 누르면 dir이 (1, 0, 1)이 되는데, 이 방향의 길이는 1이 아니라 약 1.41이다. 그래서 대각선이 41% 빠르다. `dir = Vector3.ClampMagnitude(dir, 1f);`를 이동 전에 한 줄 넣으면 길이가 1을 넘지 않게 잘라 준다.

비주얼 스튜디오 자동완성은 `new Vector3(h, 0f, v).normalized`처럼 `.normalized`를 붙여 주기도 한다. 이것도 대각선 문제를 고치지만 방식이 다르다. `.normalized`는 방향은 그대로 두고 길이를 **항상 1**로 만들고, `ClampMagnitude`는 길이가 1을 **넘을 때만** 1로 줄인다. `GetAxis`는 키를 누르면 0에서 1로 부드럽게 올라가고, 게임패드 스틱을 반만 기울이면 0.5쯤이 나오는데, 여기서 차이가 생긴다.

| 입력 | `.normalized` | `ClampMagnitude(dir, 1f)` |
|---|---|---|
| 대각선 (1, 0, 1) | 길이 1 | 길이 1 |
| 키를 막 누른 순간 (0.3, 0, 0) | 길이 1로 키움, 바로 최고 속도 | 0.3 그대로, 서서히 빨라짐 |
| 스틱을 반만 기울임 (0.5, 0, 0) | 길이 1, 천천히 걷기가 안 됨 | 0.5 그대로, 천천히 걷는다 |
| 아무것도 안 누름 (0, 0, 0) | 0 그대로 (에러 없음) | 0 그대로 |

`.normalized`를 쓰면 대각선 문제는 고쳐지지만, GetAxis의 부드러운 출발과 정지, 스틱으로 살살 걷기가 사라져서 딱딱 끊기는 느낌이 된다. 그래서 값이 부드럽게 변하는 `GetAxis`나 게임패드 입력에는 `ClampMagnitude`를 쓰고, -1·0·1만 나오는 `GetAxisRaw`라면 `.normalized`를 써도 된다. 둘 다 넣어 실행해 보고 키를 뗄 때의 느낌을 비교해 보면 차이가 바로 보인다.

**Q. 키를 떼도 캐릭터가 살짝 미끄러지다 멈춰.**<br>
`GetAxis`는 0에서 1로 바로 뛰지 않고 부드럽게 올라갔다 내려간다. 미끄러짐 없이 딱딱 끊기는 조작을 원하면 `Input.GetAxisRaw`를 쓴다. -1, 0, 1 중 하나만 나온다.

**Q. 키를 눌러도 반응이 없어.**<br>
Game 창을 클릭해서 게임 화면에 포커스가 가 있는지 확인한다. 그래도 안 되면 콘솔에 빨간 에러가 있는지 본다. `InvalidOperationException`이면 위의 Active Input Handling 설정 문제다.

**Q. 점프가 안 되고 `MissingComponentException` 에러가 나.**<br>
큐브에 Rigidbody를 안 붙였다. `GetComponent<Rigidbody>()`가 아무것도 못 찾아서 rb가 비어 있는 상태로 AddForce를 부른 것이다.

**Q. 로켓으로 날아가면 손을 떼도 끝없이 올라가고, 떨어질 땐 바닥을 뚫고 계속 떨어져.**<br>
**올라가는 이유는 이미 붙은 속도 때문이다.** 물체는 누가 멈추지 않으면 계속 움직이려고 한다(관성). 손을 떼면 힘을 더 주는 것만 멈출 뿐, 지금까지 쌓인 속도를 없애 주지는 않는다. 숫자로 보면 이렇다.

- `ForceMode.Impulse`로 6을 한 번 주면, 질량 1인 큐브는 위로 초속 6m씩 빨라진다.
- GetKey는 그걸 **매 프레임** 준다. 60fps에서 0.5초만 누르고 있어도 30번, 초속 약 180m(시속 650km쯤)가 된다.
- 손을 떼면 중력이 속도를 1초에 9.8m/s씩만 깎는다. 초속 180m가 0이 되려면 약 18초가 걸리고, 그동안 1.6km쯤 더 올라간다.

Rigidbody의 공기 저항(**Linear Damping**) 기본값이 0이라 중력 말고는 속도를 줄여 주는 게 없다. 플레이 중에 Rigidbody의 **Info**를 펼치면 **Linear Velocity**가 실시간으로 보이는데, 누르는 동안 y가 쭉쭉 오르고 떼면 천천히 줄어드는 게 숫자로 보인다. Linear Damping을 5쯤으로 올리고 다시 해 보면 손을 떼자마자 금방 느려진다. 그리고 매 프레임 힘을 주니 프레임이 많은 컴퓨터일수록 더 높이 간다. Day 5에서 본 "Time.deltaTime 없이 매 프레임 더하면 컴퓨터마다 달라진다"와 같은 문제다. 그래서 계속 주는 힘은 FixedUpdate에서 준다(다지기 Day 4).

**바닥을 뚫는 이유는 너무 빨라서다.** 유니티 물리는 1초에 50번(0.02초마다) 위치를 계산한다. 1.6km 위에서 떨어지면 바닥에 닿을 때 초속 180m쯤이라, 한 번 계산할 때마다 3.6m씩 움직인다. 그런데 Plane은 두께가 없는 판이라, 한 번은 바닥 위에 있다가 다음 계산 때는 이미 바닥 아래에 있게 된다. 둘이 겹친 순간이 한 번도 없으니 유니티는 부딪혔다는 걸 모르고, 큐브는 아무것도 없는 아래로 끝없이 떨어진다. 이걸 **터널링**이라고 한다. 빠른 물체가 뚫으면 안 될 때는 그 물체의 Rigidbody에서 **Collision Detection**을 **Continuous Dynamic**으로 바꾼다. 계산 사이에 지나간 길까지 확인해서 뚫리지 않는다(대신 계산이 조금 무거워진다). 총알처럼 빠른 물체에 주로 쓴다.

**Q. 점프는 무조건 물리야? Rigidbody가 꼭 있어야 해?**<br>
아니다. 점프를 만드는 방법은 크게 세 가지다.

**1. Rigidbody로 (이 글의 방식)**: 위로 팍 밀어 주기만 하면, 올라갔다가 중력으로 떨어지고 바닥에 부딪히는 건 물리 엔진이 다 해 준다. 코드가 짧고, 상자를 밀거나 폭발에 날아가는 것처럼 다른 물체와의 반응이 자연스럽다. 대신 물리 엔진이 계산하니 "정확히 이 높이까지" 같은 미세한 조절이 어렵고, 미끄러지거나 튕기는 의도치 않은 움직임이 생기기도 한다. 이 글에서 Rigidbody를 쓴 건 가장 적은 코드로 점프와 착지를 배울 수 있어서다.

**2. CharacterController로**: 유니티에는 캐릭터 이동 전용 컴포넌트인 CharacterController가 있다. 물리 엔진이 밀지 않고, 중력과 점프를 내가 직접 계산한다. 3D 액션·3인칭 게임에서 아주 흔하게 쓴다.

```csharp
CharacterController cc;
float yVelocity;                              // 위아래 속도
[SerializeField] float jumpHeight = 1.5f;     // 점프 높이(m)
[SerializeField] float gravity = -20f;        // 내가 정하는 중력

void Awake() { cc = GetComponent<CharacterController>(); }

void Update()
{
    if (cc.isGrounded && yVelocity < 0f)
        yVelocity = -2f;                      // 땅에 붙어 있게

    if (cc.isGrounded && Input.GetKeyDown(KeyCode.Space))
        yVelocity = Mathf.Sqrt(jumpHeight * -2f * gravity);  // 딱 jumpHeight만큼 오르는 속도

    yVelocity += gravity * Time.deltaTime;    // 중력도 직접 더한다
    cc.Move(Vector3.up * yVelocity * Time.deltaTime);
}
```

점프 높이를 "1.5m"처럼 정확히 정할 수 있고, 땅에 있는지(`isGrounded`)를 기본으로 알려 준다. 계단과 경사로도 알아서 올라간다. 유니티가 제공하는 3인칭 예제 캐릭터(Starter Assets)도 이 방식이다. 대신 다른 물체를 밀거나 날아가는 반응은 직접 만들어야 한다.

**3. 직접 계산하거나 애니메이션으로**: 물리도 CharacterController도 안 쓰고, 위치를 코드로 직접 계산하거나 애니메이션으로 점프 모양만 보여 준다. 손맛이 아주 중요한 2D 플랫포머, 정해진 칸을 뛰는 보드게임·리듬게임처럼 정확히 원하는 대로 움직여야 할 때 쓴다.

고르는 기준은 이렇다. 밀기·쓰러뜨리기·날아가기 같은 **물리 반응이 게임의 재미**면 Rigidbody, **플레이어가 조종하는 캐릭터의 손맛**이 중요하면 CharacterController나 직접 계산이다.

## 현업에서는
{:.briefing-heading}

- **입력은 Update, 물리는 FixedUpdate.** 물리 계산은 FixedUpdate라는 다른 함수에서 일정한 간격으로 하는 게 정석이다. 다만 `GetKeyDown`은 FixedUpdate에서 검사하면 가끔 놓쳐서, 입력은 Update에서 bool로 기억해 두고 FixedUpdate에서 처리한다. 한 번 팍 주는 점프는 Update에서 해도 대부분 괜찮다. 자세한 건 다지기 Day 4 "유니티 실행 순서"에서 다룬다.
- **Rigidbody가 있으면 속도로 움직인다.** 위 코드는 배우기 쉽게 Transform으로 옮겼지만, 물리가 붙은 캐릭터는 보통 Rigidbody의 속도를 바꿔서 움직인다. 벽에 박혔을 때 덜덜 떨리거나 뚫고 지나가는 문제가 줄어든다.

  ```csharp
  // Unity 6 기준. 이전 버전은 linearVelocity 대신 velocity
  Vector3 move = dir * speed;
  rb.linearVelocity = new Vector3(move.x, rb.linearVelocity.y, move.z);
  ```

- **새 프로젝트라면 새 Input System을 쓴다.** 키 대신 "점프", "이동" 같은 행동으로 입력을 받고, 키보드·게임패드·키 바꾸기를 한 번에 처리한다. 기존 `Input`으로 원리를 익히고 실전 Day 6에서 옮겨 간다.

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **기초 Day 6**과 같은 내용이다.

- [키 입력 받기](https://hlcho426.github.io/unity-csharp-week/#d6l1): GetKey, GetKeyDown, GetKeyUp
- [방향키로 이동하기](https://hlcho426.github.io/unity-csharp-week/#d6l2): Input.GetAxis
- [점프: 물리에 힘 주기](https://hlcho426.github.io/unity-csharp-week/#d6l3): Rigidbody.AddForce

## 정리
{:.briefing-heading}

- `GetKeyDown` 누른 순간 한 번, `GetKey` 누르고 있는 동안 계속, `GetKeyUp` 뗀 순간 한 번
- 입력 검사는 Update 안에서
- `GetAxis("Horizontal")`, `GetAxis("Vertical")`는 -1 ~ 1. `방향 * speed * Time.deltaTime`으로 이동
- Rigidbody가 있으면 중력과 물리가 적용된다. `AddForce(방향 * 힘, ForceMode.Impulse)`로 순간적인 힘
- 점프는 `GetKeyDown && isGrounded`. 점프하면 false, 착지하면 true

다음 글은 기초 Day 7, 코인 줍기 미니 프로젝트.
