---
title: "<유니티 C#> 기초 Day 5: Transform과 컴포넌트 (Vector3, Time.deltaTime, GetComponent)"
date: 2026-10-11 22:28:00 +0900
description: "Transform과 Vector3로 오브젝트를 옮기고, Time.deltaTime으로 컴퓨터 성능과 상관없이 같은 속도로 움직이기. GetComponent와 SerializeField까지."
series: 유니티 C# 일주일
series_title: "기초 Day 5: Transform과 컴포넌트"
categories: [게임 제작 공부, 유니티]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

Day 4까지는 콘솔에 글자만 찍었다. 오늘부터 드디어 화면 속 물체를 움직인다. 유니티 오브젝트의 위치·회전·크기를 맡는 **Transform**, 숫자 세 개 묶음인 **Vector3**, 컴퓨터 성능과 상관없이 같은 속도로 움직이게 해 주는 **Time.deltaTime**, 그리고 다른 컴포넌트를 가져오는 **GetComponent**를 배운다.

**오늘의 목표**

- `transform.position`으로 오브젝트를 옮길 수 있다
- `Vector3`를 만들고 읽을 수 있다
- 이동 속도에 `Time.deltaTime`을 곱하는 이유를 설명할 수 있다
- `GetComponent`로 다른 컴포넌트를 가져오고, `[SerializeField]`를 쓸 수 있다

## 1. Transform: 모든 오브젝트가 가진 컴포넌트
{:.briefing-heading}

Hierarchy에서 아무 오브젝트나 골라 보면 Inspector 맨 위에 항상 **Transform**이 있다. 위치(Position), 회전(Rotation), 크기(Scale)를 담당하고, 지울 수도 없다.

스크립트 안에서는 소문자 `transform`으로 **이 스크립트가 붙은 오브젝트의 Transform**에 바로 접근할 수 있다.

```csharp
void Start()
{
    Debug.Log(transform.position);                   // 지금 위치
    transform.position = new Vector3(0f, 2f, 0f);    // 위로 2만큼 떨어진 곳으로
    transform.localScale = new Vector3(2f, 2f, 2f);  // 크기 두 배
}
```

- `transform.position`: 위치
- `transform.rotation`: 회전
- `transform.localScale`: 크기

## 2. Vector3: 숫자 세 개 묶음
{:.briefing-heading}

위치는 x, y, z 세 숫자로 정해진다. 이 세 숫자를 한 덩어리로 다루는 자료형이 **Vector3**다.

```csharp
Vector3 pos = new Vector3(1f, 2f, 3f);
Debug.Log(pos.x);   // 1
Debug.Log(pos.y);   // 2
Debug.Log(pos.z);   // 3
```

유니티에서 **x는 좌우, y는 위아래, z는 앞뒤**다. 위쪽이 y라는 게 중요하다. 점프는 y를 키우는 것이다.

x, y, z는 모두 `float`다. 그래서 `2`처럼 소수점이 없는 숫자도 `2f`로 쓰는 습관이 있다. 위치·회전·크기·속도·힘처럼 유니티가 공간을 다루는 숫자는 거의 다 `float`라서, 속도나 점프 힘 같은 수치도 `float`로 만든다.

자주 쓰는 방향은 이름이 붙어 있다.

| 이름 | 값 | 뜻 |
|---|---|---|
| `Vector3.zero` | (0, 0, 0) | 원점 |
| `Vector3.up` | (0, 1, 0) | 위 |
| `Vector3.right` | (1, 0, 0) | 오른쪽 |
| `Vector3.forward` | (0, 0, 1) | 앞 |

이 방향들은 **길이가 1**이다. 여기에 숫자를 곱하면 방향은 그대로 두고 길이만 늘어난다. `Vector3.right * 5f`는 (5, 0, 0), 오른쪽으로 5다. `Vector3.up * 2f`는 (0, 2, 0), 위로 2다. 그래서 움직이거나 힘을 주는 코드는 거의 늘 `방향 * 크기` 모양이 된다.

`position`에는 Vector3를 통째로 넣어야 한다. `transform.position = 0;`처럼 숫자 하나는 넣을 수 없다. 원점으로 보내려면 `transform.position = Vector3.zero;`다.

## 3. 움직이기와 Time.deltaTime
{:.briefing-heading}

Update는 매 프레임 실행되니까, 매번 위치를 조금씩 더하면 움직인다.

```csharp
void Update()
{
    transform.position += new Vector3(0.1f, 0f, 0f);
}
```

오른쪽으로 계속 움직인다. 그런데 문제가 있다. 1초에 120프레임 도는 컴퓨터는 60프레임 도는 컴퓨터보다 Update가 두 배 많이 불려서 **두 배 빨리** 움직인다. 게임 속도가 컴퓨터 성능에 따라 달라지면 안 된다.

1초에 그리는 프레임 수를 **fps**(frames per second)라고 한다. 1초에 60프레임이면 60fps, 120프레임이면 120fps다. 같은 게임도 컴퓨터 성능이나 화면 설정에 따라 fps가 다르고, 한 컴퓨터 안에서도 순간순간 조금씩 오르내린다.

해결책이 `Time.deltaTime`이다.

```csharp
public float speed = 5f;

void Update()
{
    transform.position += Vector3.right * speed * Time.deltaTime;
}
```

`Time.deltaTime`은 **지난 프레임부터 지금까지 흐른 시간(초)**이다. 60fps면 약 0.0167초, 120fps면 약 0.0083초다. 여기에 속도를 곱하면 "1프레임마다 5"가 아니라 **"1초마다 5"**가 된다. 프레임이 많은 컴퓨터는 조금씩 자주, 적은 컴퓨터는 많이씩 가끔 더해서 1초 동안 움직인 거리는 똑같다.

`방향 * 속도 * Time.deltaTime` 모양은 앞으로 계속 쓴다. 앞쪽으로 초당 3씩이면 `Vector3.forward * 3f * Time.deltaTime`이다.

### Translate

같은 일을 하는 함수도 있다.

```csharp
transform.Translate(Vector3.right * speed * Time.deltaTime);
```

`Translate`는 "이만큼 옮겨라"라는 함수다. 다만 Translate는 기본으로 **오브젝트 자신이 바라보는 방향**을 기준으로 옮긴다. 오브젝트가 회전해 있으면 `Vector3.right`가 월드의 오른쪽이 아니라 자기 오른쪽이 된다. 월드 기준으로 똑같이 하려면 `transform.Translate(..., Space.World)`처럼 끝에 `Space.World`를 붙인다.

## 4. GetComponent: 다른 컴포넌트 가져오기
{:.briefing-heading}

오브젝트는 컴포넌트 조립품이다. Transform 말고도 물리를 맡는 **Rigidbody**, 충돌을 맡는 **Collider**, 애니메이션을 맡는 **Animator**, 그리고 내가 만든 스크립트가 붙는다. 같은 오브젝트에 붙은 다른 컴포넌트를 쓰려면 `GetComponent`로 가져온다.

```csharp
Rigidbody rb;

void Start()
{
    rb = GetComponent<Rigidbody>();
}
```

꺾쇠 `< >` 안에 가져올 컴포넌트의 종류를 쓰고, 뒤에 빈 괄호 `()`를 붙인다. `GetComponent<Animator>()`, `GetComponent<Collider>()`처럼.

찾는 데는 비용이 들어서, 매 프레임 찾지 않고 **Start에서 한 번 찾아 변수에 저장**해 두는 게 기본 패턴이다.

없는 컴포넌트를 찾으면 `null`(없음)이 돌아온다. 그 상태로 `rb.AddForce(...)`처럼 쓰려고 하면 에러가 난다. 에디터에서는 "Rigidbody가 붙어 있지 않다"는 `MissingComponentException`이, 빌드한 게임에서는 `NullReferenceException`이 뜬다. 어느 쪽이든 "뭔가 안 붙어 있구나"부터 의심하면 된다.

## 5. public 대신 [SerializeField]
{:.briefing-heading}

```csharp
public float speed = 5f;               // Inspector O, 다른 스크립트 O
[SerializeField] float jumpPower = 7f; // Inspector O, 다른 스크립트 X
float timer = 0f;                      // Inspector X, 다른 스크립트 X
```

`public`은 Inspector에 보이지만, **다른 스크립트가 마음대로 바꿀 수도** 있다. Inspector에서 조절만 하고 싶다면 `[SerializeField]`를 붙인다. Inspector에는 보이지만 다른 스크립트는 못 건드린다. 실무에서는 이쪽을 훨씬 많이 쓴다.

## 직접 해 보기
{:.briefing-heading}

큐브에 새 스크립트 `Mover`를 만들어 붙인다.

```csharp
using UnityEngine;

public class Mover : MonoBehaviour
{
    [SerializeField] float speed = 2f;
    [SerializeField] float turnSpeed = 90f;   // 초당 회전 각도

    void Start()
    {
        transform.position = Vector3.zero;
    }

    void Update()
    {
        transform.position += Vector3.right * speed * Time.deltaTime;
        transform.Rotate(Vector3.up * turnSpeed * Time.deltaTime);
    }
}
```

실행하면 큐브가 원점에서 출발해 빙글빙글 돌면서 오른쪽으로 초당 2씩 간다. 해 볼 것.

- 플레이 중에 Inspector의 Speed, Turn Speed를 바꿔 보기
- `transform.position +=` 줄을 `transform.Translate(Vector3.right * speed * Time.deltaTime);`로 바꿔 보기. 큐브가 돌면서 오른쪽이 계속 바뀌니까 원을 그리며 움직인다. Translate가 "자기 기준"이라는 게 눈으로 보인다
- 끝에 `Space.World`를 붙이면 다시 직선으로 간다

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. `transform.position.x = 5f;`가 왜 에러야?**<br>
`transform.position`을 읽으면 위치 값의 **복사본**이 나온다. 복사본의 x만 바꿔 봤자 진짜 위치는 안 바뀌어서, C#이 아예 에러(CS1612)로 막는다. x만 바꾸고 싶으면 꺼내서, 고치고, 다시 넣는다.

```csharp
Vector3 p = transform.position;
p.x = 5f;
transform.position = p;
```

왜 복사본이 나오는지는 [심화 Day 8 "값 형식과 참조 형식"](/posts/csharp-week-adv-day8/)에서 다룬다.

**Q. `Transform`이랑 `transform`은 뭐가 달라?**<br>
대문자 `Transform`은 컴포넌트의 **종류(자료형)** 이름이고, 소문자 `transform`은 **이 오브젝트의** Transform을 가리키는 변수다. `Rigidbody`(종류)와 `rb`(내가 만든 변수)의 관계와 같다.

**Q. Rotation은 왜 x, y, z 세 숫자로 직접 안 넣어?**<br>
유니티는 회전을 `Quaternion`이라는 특별한 형식으로 다룬다. 지금은 회전시키고 싶으면 `transform.Rotate(...)`를 쓴다고 알아 두면 충분하다. [심화 Day 3](/posts/csharp-week-adv-day3/)에서 다시 나온다.

**Q. 비주얼 스튜디오 자동완성은 `[SerializeField] private float`처럼 private을 붙여 주던데?**<br>
둘은 완전히 같은 코드다. C#에서는 앞에 아무것도 안 쓰면 자동으로 `private`이다. private을 붙이든 안 붙이든 Inspector에는 보이고, 다른 스크립트에서는 못 쓴다. 다른 스크립트에서 쓰게 하려면 `public`을 붙여야 한다.

```csharp
[SerializeField] float speed = 5f;           // private이 생략된 것
[SerializeField] private float speed = 5f;   // private을 직접 쓴 것 (같은 뜻)
```

| 쓴 것 | Inspector | 다른 스크립트 |
|---|---|---|
| `public float speed` | 보인다 | 쓸 수 있다 |
| `[SerializeField] float speed` (= private) | 보인다 | 못 쓴다 |
| `float speed` (= private) | 안 보인다 | 못 쓴다 |

비주얼 스튜디오가 private을 붙여 주는 건 코드 스타일 때문이다. C#(.NET)의 표준 스타일은 생략할 수 있어도 private을 직접 쓰는 쪽이다. 반대로 유니티의 새 스크립트 템플릿(`void Start()`)이나 유니티 공식 문서 예제는 생략하는 경우가 많고, 이 시리즈도 짧게 보이려고 생략했다. 아래 "현업에서는"의 `[SerializeField] private`도 같은 코드를 private을 써서 적은 것이다. 동작은 같으니, 내 프로젝트 안에서 한 가지로 통일하기만 하면 된다.

**Q. Mover는 플레이 중에 Inspector에서 Speed를 바꾸면 바로 빨라지는데, Day 1의 Player hp는 바꿔도 아무 변화가 없었어. 왜 달라?**<br>
플레이 중에 Inspector에서 값을 바꾸면, 두 경우 모두 변수 값 자체는 그 순간 바로 바뀐다. 차이는 **코드가 그 값을 언제 다시 읽느냐**다.

- Player의 hp는 `Start()`에서만 썼다. Start는 큐브가 처음 나타날 때 딱 한 번 실행되고 끝나서, 그 뒤에 hp를 바꿔도 다시 읽어서 찍는 코드가 없다. 그래서 변화가 없어 보인다.
- Mover의 speed, turnSpeed는 `Update()`에서 매 프레임 읽는다. 바꾼 바로 다음 프레임부터 새 값으로 계산해서 즉시 빨라지거나 느려진다.

그래서 "플레이하면서 수치 맞추기"는 Update처럼 계속 읽는 값에서만 효과가 보인다. Day 1의 "코드를 고쳐도 안 바뀌던 것"과는 다른 이야기다. 그건 코드 값과 Inspector 값 중 **무엇이 이기냐**(Inspector가 이긴다)였고, 이건 바뀐 값을 **코드가 다시 읽느냐**(Update는 매번, Start는 한 번)다.

그리고 플레이 중에 Inspector에서 바꾼 값은 **플레이를 멈추면 원래대로 돌아간다**(Day 0에서 본 그 주의사항). 딱 좋은 값을 찾았다면 멈추기 전에 적어 두거나, 컴포넌트 ⋮ 메뉴의 **Copy Component**로 복사해 두었다가 멈춘 뒤 **Paste Component Values**로 붙여 넣는다. 실무에서 수치를 맞출 때 자주 쓰는 방법이다.

## 현업에서는
{:.briefing-heading}

- **유니티의 1은 1미터로 생각한다.** 중력 기본값(9.81)도 이 기준에 맞춰져 있다. 기본 큐브는 한 변이 1, 기본 캡슐은 키가 2라서 사람 크기쯤이다. `speed = 5f`면 초당 5미터, 사람이 달리는 속도쯤이다. 캐릭터를 실제보다 10배 크게 만들면 떨어지는 게 달에서처럼 느릿하게 느껴지니, 크기는 실제 비율에 가깝게 맞춘다.
- **GetComponent는 미리 해 둔다.** Start(또는 Awake)에서 찾아 변수에 담아 두고 쓴다. Update에서 매번 찾는 코드는 리뷰에서 바로 지적받는다.
- **꼭 필요한 컴포넌트는 RequireComponent로 강제한다.** 스크립트 위에 `[RequireComponent(typeof(Rigidbody))]`를 붙이면, 이 스크립트를 붙일 때 Rigidbody가 자동으로 같이 붙는다. "안 붙여서 에러"를 원천 봉쇄한다.
- **수치는 `[SerializeField] private`로 꺼낸다.** 다른 스크립트가 값을 바꿔야 하면 public 변수를 열기보다 함수(`SetSpeed(...)`)를 만들어 그 함수로만 바꾸게 한다.
- **물리가 붙은 물체는 Transform으로 직접 옮기지 않는다.** Rigidbody가 붙은 물체를 `transform.position`으로 순간이동시키면 물리 계산과 어긋날 수 있다. 이 시리즈에서는 배우기 쉽게 Transform으로 옮기지만, 실무에서는 Rigidbody의 힘이나 속도로 움직인다. Day 6에서 다시 이야기한다.

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **기초 Day 5**와 같은 내용이다.

- [Transform과 Vector3](https://hlcho426.github.io/unity-csharp-week/#d5l1): 위치, 회전, 크기
- [움직이기와 Time.deltaTime](https://hlcho426.github.io/unity-csharp-week/#d5l2): 프레임과 상관없이 같은 속도로
- [다른 컴포넌트 가져오기](https://hlcho426.github.io/unity-csharp-week/#d5l3): GetComponent, SerializeField

## 정리
{:.briefing-heading}

- 모든 게임 오브젝트에는 Transform이 있다. 스크립트에서는 소문자 `transform`
- `transform.position`은 위치(Vector3). Vector3는 x, y, z 세 숫자이고 y가 위쪽이다
- 이동은 `방향 * 속도 * Time.deltaTime`. deltaTime을 곱하면 "초당" 속도가 된다
- `GetComponent<타입>()`으로 같은 오브젝트의 컴포넌트를 가져온다. 보통 Start에서 한 번
- `[SerializeField]`는 Inspector에는 보이지만 다른 스크립트는 못 건드린다

다음 글은 기초 Day 6, 키 입력으로 캐릭터 움직이기.
