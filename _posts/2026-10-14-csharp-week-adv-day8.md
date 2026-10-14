---
title: "<유니티 C#> 심화 Day 8: 값 형식과 참조 형식 (복사와 주소, position.x 함정)"
date: 2026-10-14 15:28:00 +0900
description: "int와 Vector3는 통째로 복사되고, 클래스와 List는 주소만 복사된다. 왜 바꿨는데 안 바뀌는지, 왜 안 건드렸는데 바뀌는지, 왜 transform.position.x = 5가 에러인지 한 번에 정리하며 심화 코스를 마친다."
series: 유니티 C# 일주일
series_title: "심화 Day 8: 값 형식과 참조 형식"
categories: [게임 제작 공부, 유니티]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

심화 코스의 마지막 날은 새 기능 대신, 지금까지 몇 번이나 "나중에 정리한다"고 미뤄 둔 원리를 정리한다.

- 기초 Day 8: 함수에 int를 넘기면 **복사돼서** 원본은 그대로였다
- [Day 1](/posts/csharp-week-adv-day1/): 함정의 Player 칸에는 복사본이 아니라 진짜 플레이어를 **가리키는 표지판**이 들어 있다고 했다
- [Day 4](/posts/csharp-week-adv-day4/): `target.y`를 바꿔도 플레이어는 꿈쩍하지 않았다
- [Day 6](/posts/csharp-week-adv-day6/): 슬라임 에셋을 고치면 그걸 쓰는 슬라임이 **전부** 바뀌었다

어떤 건 복사되고, 어떤 건 같은 것을 가리킨다. 이 차이가 **값 형식과 참조 형식**이다. 이걸 알면 "왜 바꿨는데 안 바뀌지?"와 "왜 안 건드렸는데 바뀌지?" 버그의 절반이 풀린다.

**오늘의 목표**

- 값 형식은 `=` 할 때 내용이 통째로 복사된다는 걸 안다
- 참조 형식은 `=` 할 때 주소만 복사돼서 같은 실물을 함께 가리킨다는 걸 안다
- `transform.position.x = 5f;`가 왜 에러인지 알고, 꺼내서 고치고 다시 넣을 수 있다

## 1. 두 종류의 상자
{:.briefing-heading}

C#의 자료형은 크게 두 종류다.

| | 상자 안에 든 것 | 예 |
|---|---|---|
| **값 형식** | 내용물 **자체** | int, float, bool, Vector3, Quaternion, Color, enum |
| **참조 형식** | 내용물이 있는 곳의 **주소** | string, 배열, List, GameObject, 모든 컴포넌트, 내가 만든 클래스(Monster), ScriptableObject |

값 형식 상자에는 숫자 10이 그대로 들어 있다. 참조 형식 상자에는 몬스터가 들어 있는 게 아니라, **몬스터가 사는 집 주소를 적은 쪽지**가 들어 있다. 몬스터 실물은 따로 어딘가에 살고 있다.

이 차이는 `=`로 옮겨 담을 때와 함수에 넘길 때 드러난다.

## 2. 값 형식: 통째로 복사
{:.briefing-heading}

```csharp
int a = 10;
int b = a;     // a의 내용 10을 복사
b = 99;
Debug.Log(a);  // 10

Vector3 p1 = new Vector3(1f, 0f, 0f);
Vector3 p2 = p1;   // 세 숫자를 통째로 복사
p2.x = 5f;
Debug.Log(p1.x);   // 1
```

`b = a`는 a 상자의 내용물 10을 **복사해서** b 상자에 넣는다. 그다음 b를 99로 바꿔도 a는 10 그대로다. 시험지를 복사해서 친구에게 주면, 친구가 복사본에 낙서해도 내 원본은 깨끗한 것과 같다.

기초 Day 8의 `AddTen(myHp)`도 같은 원리였다. myHp의 값 50이 복사돼서 x로 들어갔으니, 함수 안에서 x를 바꿔도 myHp는 그대로였다.

### Vector3는 new를 쓰는데 값 형식이야?

헷갈리는 부분이다. Vector3는 `new Vector3(...)`로 만들지만 클래스가 아니라 **struct(구조체)**라는 종류다. struct는 값 형식이라 통째로 복사된다. Quaternion, Color도 struct다. 유니티 문서에서 자료형을 찾았을 때 제목 옆에 struct라고 적혀 있으면 값 형식, class라고 적혀 있으면 참조 형식이다.

## 3. 참조 형식: 주소를 나눠 갖는다
{:.briefing-heading}

Day 1의 Monster 클래스로 해 보자.

```csharp
Monster a = new Monster("슬라임", 30);

Monster b = a;   // 주소만 복사
b.hp = 0;

Debug.Log(a.hp); // 0 !
```

`b = a`는 몬스터를 복제하는 게 아니라 **주소 쪽지를 복사**하는 것이다. 같은 집을 가리키는 쪽지가 두 장이 됐을 뿐, 몬스터는 여전히 **한 마리**다. 그래서 b 쪽지를 들고 찾아가 체력을 0으로 만들면, a 쪽지를 들고 찾아가도 체력 0인 그 몬스터를 만난다.

List도 클래스라서 같다.

```csharp
List<string> party = new List<string>();
List<string> copy = party;   // 같은 List를 가리킨다
copy.Add("전사");
Debug.Log(party.Count);      // 1
```

copy에 넣었는데 party에도 들어 있다. 이름만 두 개일 뿐 List는 하나다. 진짜 복사본이 필요하면 `new List<string>(party)`처럼 **새로 만들면서** 내용을 옮겨 담는다.

### 함수에 넘길 때도 주소가 복사된다

```csharp
void Kill(Monster m)
{
    m.hp = 0;
}

Monster slime = new Monster("슬라임", 30);
Kill(slime);
Debug.Log(slime.hp);   // 0
```

기초 Day 8의 AddTen과 결과가 반대다. 함수에 넘길 때도 `=`와 똑같이 복사가 일어나는데, 참조 형식은 **주소가** 복사된다. 함수 안의 m과 바깥의 slime이 같은 몬스터를 가리키니, 함수 안에서 바꾼 게 원본에 보인다.

| | 넘기는 것 | 함수 안에서 바꾸면 |
|---|---|---|
| `AddTen(int x)` | 값 50의 복사본 | 원본 그대로 |
| `Kill(Monster m)` | 주소의 복사본 | **원본이 바뀐다** |

### 그래서 Trap이 Player를 "가리킨다"고 했다

```csharp
[SerializeField] PlayerHealth player;

player.TakeDamage(10);
```

Day 1의 함정 칸에 들어 있는 건 플레이어의 복사본이 아니라 **씬에 있는 그 플레이어의 주소**다. 그래서 TakeDamage를 부르면 진짜 플레이어의 체력이 줄어든다. 만약 복사본이었다면 함정은 가짜 플레이어를 때리고 있었을 것이다.

그리고 **주소 칸이 비어 있는 상태가 바로 null**이다. 쪽지에 아무 주소도 안 적혀 있으니 찾아갈 수가 없다. NullReferenceException은 "빈 쪽지를 들고 찾아가려 했다"는 에러다. 값 형식인 int에는 주소 칸이 없으니 null이 될 수 없고, 아무것도 안 넣으면 0이다.

Day 6도 같은 원리다. 슬라임 세 마리의 Data 칸에는 `Slime` 에셋의 **주소**가 들어 있다. 세 마리 모두 같은 파일을 가리키니, 파일 하나를 고치면 셋 다 바뀐다.

## 4. 유니티 함정: position.x 직접 바꾸기
{:.briefing-heading}

```csharp
transform.position.x = 5f;   // 에러 CS1612
```

x만 바꾸고 싶은 자연스러운 코드인데 컴파일 에러가 난다. 이유는 앞의 두 원리에 다 있다.

`transform.position`을 읽으면, Transform이 위치를 **복사해서** 건네준다. Vector3는 값 형식이니까. 그 복사본의 x를 바꿔 봤자 진짜 위치는 안 바뀐다. 복사본은 그 줄이 끝나면 버려진다. 그래서 C#이 "이건 아무 효과 없는 코드야"라고 미리 막아 주는 것이다.

### 해결: 꺼내서, 고치고, 다시 넣기

```csharp
Vector3 p = transform.position;   // 1. 복사본 꺼내기
p.x = 5f;                         // 2. 복사본 고치기
transform.position = p;           // 3. 통째로 다시 넣기
```

복사본을 받아서 고친 다음, 통째로 다시 넣는다. 세 번째 줄의 `=`는 "위치를 이걸로 바꿔 줘"라고 Transform에 전달하는 것이라 실제로 반영된다.

Day 4의 적 코드가 이 모양이었다.

```csharp
Vector3 target = player.transform.position;   // 플레이어 위치 복사
target.y = transform.position.y;              // 복사본의 높이만 바꿈
```

target은 복사본이니까 높이를 바꿔도 플레이어는 꿈쩍하지 않았다. 원하는 게 바로 그거였다. 플레이어를 옮기려던 게 아니라 "플레이어 위치인데 높이만 내 높이인 점"이 필요했으니까.

같은 원리가 적용되는 곳:

| 바꾸고 싶은 것 | 에러 나는 코드 | 3단계로 |
|---|---|---|
| 위치 | `transform.position.y = 2f;` | 꺼내서 y만 바꾸고 다시 넣기 |
| 크기 | `transform.localScale.x = 2f;` | 같은 방법 |
| 물리 속도 | `rb.linearVelocity.y = 0f;` | 같은 방법 |

## 직접 해 보기
{:.briefing-heading}

### A. 복사와 주소를 눈으로 보기

빈 오브젝트에 `ValueRefTest` 스크립트를 만들어 붙이고 플레이한다. Day 1의 Monster 클래스를 그대로 쓴다.

```csharp
using System.Collections.Generic;
using UnityEngine;

public class ValueRefTest : MonoBehaviour
{
    void Start()
    {
        // 값 형식
        Vector3 start = new Vector3(0f, 0f, 0f);
        Vector3 cur = start;
        cur.y = 3f;
        Debug.Log("값 형식: start.y = " + start.y);       // 0

        // 참조 형식: 내 클래스
        Monster a = new Monster("슬라임", 30);
        Monster b = a;
        b.hp = 0;
        Debug.Log("참조 형식: a.hp = " + a.hp);           // 0

        // 참조 형식: List
        List<string> party = new List<string>();
        List<string> copy = party;
        copy.Add("전사");
        Debug.Log("List: party.Count = " + party.Count);  // 1

        // 진짜 복사본
        List<string> clone = new List<string>(party);
        clone.Add("마법사");
        Debug.Log("새로 만든 복사본: party.Count = " + party.Count + ", clone.Count = " + clone.Count);  // 1, 2
    }
}
```

주석의 숫자를 가리고, 출력을 먼저 맞혀 본 다음 플레이해서 확인해 보자. 다 맞혔으면 오늘 내용은 거의 끝이다.

### B. 에러를 일부러 만들어 보기

ValueRefTest의 Start 맨 아래에 이 줄을 넣는다.

```csharp
transform.position.x = 5f;
```

저장하면 콘솔에 `CS1612` 에러가 뜬다.

```text
error CS1612: Cannot modify the return value of 'Transform.position' because it is not a variable
```

"Transform.position은 변수가 아니라서, 돌려받은 값을 고칠 수 없다"는 말이다. 풀어 쓰면 "position이 준 건 진짜 위치가 아니라 복사본이라 고쳐 봐야 소용없다"는 뜻이다. 컴파일 에러가 있으면 플레이가 안 되니, 확인했으면 3단계로 바꿔서 에러를 없앤다.

```csharp
Vector3 p = transform.position;
p.x = 5f;
transform.position = p;
```

플레이하고 이 오브젝트를 선택해 보면 Inspector의 Position X가 5로 바뀌어 있다. 이번엔 세 번째 줄만 지워 보자. 에러는 안 나지만 Position X는 그대로다. 복사본만 고치고 버린 것이다.

### C. 짧게 누르면 낮게 점프

3단계 패턴을 실제 게임 조작에 써 본다. 플랫포머 게임에서 흔한 "스페이스를 짧게 누르면 낮게, 길게 누르면 높이" 점프다. `PlayerController`의 Update에 추가한다.

```csharp
// 올라가는 중에 스페이스를 떼면 상승 속도를 절반으로
if (Input.GetKeyUp(KeyCode.Space) && rb.linearVelocity.y > 0f)
{
    Vector3 vel = rb.linearVelocity;   // 1. 꺼내고
    vel.y *= 0.5f;                     // 2. 고치고
    rb.linearVelocity = vel;           // 3. 다시 넣기
}
```

`GetKeyUp`은 기초 Day 6의 GetKeyDown과 짝으로, 키를 **뗀** 프레임에만 true다. `rb.linearVelocity`는 Rigidbody의 지금 속도(Vector3)이고, y가 0보다 크면 올라가는 중이다. 올라가는 도중에 키를 떼면 위로 가는 속도만 절반으로 깎는다. x와 z는 그대로다.

스페이스를 톡 쳐 보고, 꾹 눌러 보자. 점프 높이가 달라진다. `0.5f`를 0.3으로 줄이면 차이가 더 커진다.

> Unity 6 이전 버전에서는 `linearVelocity` 대신 `velocity`다. 앱의 문제도 `rb.velocity`로 나오는데 방법은 똑같다.
{: .prompt-info }

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. string도 참조 형식이라며? 그런데 왜 복사처럼 동작해?**<br>

```csharp
string a = "슬라임";
string b = a;
b = "고블린";
Debug.Log(a);   // 슬라임
```

`b = "고블린"`은 b가 가리키던 글자를 **고치는 게 아니라**, b 쪽지에 새 글자 "고블린"의 주소를 **새로 적는** 것이다. a 쪽지는 여전히 "슬라임"을 가리킨다. string은 한 번 만들어지면 내용을 바꿀 수 없게 만들어져 있어서, 바꾸는 것처럼 보이는 모든 일이 사실은 새 글자를 만드는 일이다. 그래서 결과적으로 값 형식처럼 쓰면 된다.

**Q. 참조 형식에 `b = new Monster(...)`를 하면 a도 바뀌어?**<br>
안 바뀐다. 이건 b 쪽지에 **다른 집 주소**를 새로 적는 것이다. a는 원래 몬스터를 계속 가리킨다. 가리키는 실물 안의 값을 바꾸는 `b.hp = 0`과, 쪽지 자체를 바꾸는 `b = 다른 것`은 다르다.

**Q. 함수 안에서 `m = null;` 하면 원본도 null이 돼?**<br>
안 된다. 함수에 넘어온 건 주소 쪽지의 **복사본**이다. 복사본 쪽지를 지워도 바깥 쪽지는 그대로다. 함수 안에서 바꿀 수 있는 건 "쪽지가 가리키는 실물의 내용"뿐이다.

**Q. Destroy한 오브젝트를 가리키는 변수는 어떻게 돼?**<br>
변수에는 여전히 주소가 남아 있지만, 유니티는 그 오브젝트가 사라졌다는 걸 알고 `== null` 비교에서 true를 돌려준다. 그래서 `if (enemy != null)`로 확인할 수 있다. 확인 없이 쓰면 `MissingReferenceException`이 난다. null 이야기는 다지기 Day 3에서 자세히 다룬다.

**Q. 내가 만든 클래스를 값 형식으로 만들 수도 있어?**<br>
`class` 대신 `struct`로 만들면 값 형식이 된다. 위치, 색처럼 작고 자주 복사되는 묶음에 쓴다. 처음에는 class로 만들고, struct는 "Vector3가 struct라서 복사된다"는 걸 이해하는 정도면 충분하다.

## 현업에서는
{:.briefing-heading}

- **"공유하고 싶은가, 따로 갖고 싶은가"를 먼저 묻는다.** 같은 데이터를 여럿이 봐야 하면 참조(Day 6의 에셋), 각자 바꿔야 하면 복사(Day 6의 currentHp). 버그의 상당수가 공유하면 안 되는 걸 공유하거나, 공유해야 하는 걸 복사해서 생긴다.
- **List를 그대로 넘겨주지 않는다.** 인벤토리 List를 다른 스크립트에 그대로 넘기면, 그쪽에서 Add나 Clear를 해도 내 인벤토리가 바뀐다. 읽기만 해야 하는 곳에는 복사본을 주거나 읽기 전용으로 감싸서 준다. 다지기 Day 1의 List 함정이 이 이야기다.
- **3단계 패턴은 그냥 외운다.** 꺼내고, 고치고, 다시 넣기. 위치, 회전, 크기, 속도, 머티리얼 색까지 유니티에서 하루에도 몇 번씩 쓴다.

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **심화 Day 8**과 같은 내용이다. 마지막 레슨에는 3단계 패턴을 직접 조립하는 블록 문제가 있다.

- [값 형식: 복사되는 것들](https://hlcho426.github.io/unity-csharp-week/#c4l1): int, float, bool, Vector3
- [참조 형식: 주소를 나눠 갖는 것들](https://hlcho426.github.io/unity-csharp-week/#c4l2): 클래스, List, GameObject
- [유니티 함정: position.x 직접 바꾸기](https://hlcho426.github.io/unity-csharp-week/#c4l3): Vector3는 복사된다

## 정리
{:.briefing-heading}

- 값 형식(int, float, bool, Vector3, enum…)은 `=` 할 때 내용이 통째로 복사된다. 복사본을 바꿔도 원본은 그대로
- 참조 형식(클래스, List, 배열, GameObject, 컴포넌트, ScriptableObject…)은 주소만 복사된다. 같은 실물을 함께 가리켜서, 한쪽에서 바꾸면 다른 쪽에서도 보인다
- 함수에 넘길 때도 같다. int는 원본이 안 바뀌고, Monster는 원본이 바뀐다
- 주소 칸이 비어 있는 상태가 null
- `transform.position.x = 5f;`는 에러. position은 복사본을 돌려주니까. 꺼내서 → 고치고 → 다시 넣기

## 심화 코스를 마치며
{:.briefing-heading}

기초 코스가 스크립트 하나로 캐릭터를 움직이는 법이었다면, 심화 코스는 스크립트 여러 개가 **함께 일하는 법**이었다. 지금 씬에는 이런 것들이 있다.

- 이동과 대시를 맡는 `PlayerController`, 체력과 무적을 맡는 `PlayerHealth` (Day 1, 2)
- 프리팹으로 찍혀 나오는 코인과 스포너 (Day 3)
- 대기, 추격, 공격을 오가는 적 (Day 4)
- 플레이어가 쓰러지면 방송을 듣고 멈추는 적과 로그, 클리어하면 Inspector에서 연결한 대로 반응하는 오브젝트들 (Day 5)
- 데이터 에셋으로 성격이 정해지는 슬라임과 고블린 (Day 6)
- 최단 기록과 세이브 파일 (Day 7)

작지만 게임의 뼈대가 다 들어 있다. 다음 코스인 **실전**에서는 이 구조를 더 단단하게 만든다. 공통점을 물려받는 상속, "할 수 있다"는 약속인 인터페이스, 게임 전체를 관리하는 매니저, 화면의 체력바, 새 Input System, 그리고 버그를 찾는 법까지. 첫 글은 실전 Day 1, 상속이다.
