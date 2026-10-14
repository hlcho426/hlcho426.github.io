---
title: "<유니티 C#> 심화 Day 3: 프리팹과 생성 (Instantiate, Destroy, Random.Range)"
date: 2026-10-14 15:08:00 +0900
description: "자주 쓰는 오브젝트를 프리팹으로 만들고 Instantiate로 찍어낸다. Destroy로 시간 뒤 치우기, Random.Range의 끝값 함정, 코인 스포너와 오브젝트 풀링까지."
series: 유니티 C# 일주일
series_title: "심화 Day 3: 프리팹과 생성"
categories: [게임 제작 공부, 유니티]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

기초 Day 7에서 코인을 Ctrl + D로 다섯 개 복사해 바닥에 흩어 놓았다. 그리고 코인이 빙글빙글 도는 `Coin` 스크립트를 붙이려다 보니 다섯 개에 일일이 붙여야 했다. 코인이 50개라면? 디자인을 바꿀 때마다 50개를 다 고쳐야 한다.

오늘은 오브젝트를 **원본 하나**로 관리하는 **프리팹**과, 그 원본을 게임 중에 코드로 찍어내는 **Instantiate**를 배운다. 총알, 적, 이펙트, 떨어지는 아이템처럼 "게임 중에 생겼다 사라지는 것"은 전부 이 방식으로 만든다. [Day 2](/posts/csharp-week-adv-day2/)의 코루틴과 합치면 "1초마다 하나씩 나타나기"도 금방이다.

**오늘의 목표**

- 프리팹을 만들고, 원본과 복사본의 관계를 안다
- `Instantiate`로 오브젝트를 만들고, 돌려받은 오브젝트를 다룰 수 있다
- `Destroy(대상, 초)`로 시간 뒤에 치울 수 있다
- `Random.Range`의 정수와 소수 규칙 차이를 안다

## 1. 프리팹: 재사용하는 원본
{:.briefing-heading}

Hierarchy의 오브젝트를 **Project 창으로 끌어다 놓으면** 프리팹이 된다. 프리팹은 씬이 아니라 프로젝트에 파일(`.prefab`)로 저장되는 **오브젝트 원본**이다. 붙어 있던 컴포넌트, 값, 태그, 자식 오브젝트까지 통째로 저장된다.

이때 Hierarchy에 남아 있는 오브젝트는 이름이 **파란색**으로 바뀐다. "이건 프리팹의 복사본이다"라는 표시다. 이 상태에서 Project 창의 원본을 다시 Hierarchy로 끌어다 놓으면 복사본이 하나 더 생긴다.

| 하는 일 | 결과 |
|---|---|
| 원본 프리팹의 값을 고친다 | 씬에 놓인 **모든 복사본**에 한 번에 반영된다 |
| 씬의 복사본 하나만 값을 고친다 | 그 하나만 바뀐다. Inspector에서 그 값이 **굵은 글씨**로 표시된다 |
| 굵은 글씨가 된 복사본의 원본을 고친다 | 따로 바꾼 그 값은 원본을 따라가지 않고 그대로 남는다 |

원본 프리팹은 Project 창에서 더블클릭하면 **프리팹 편집 모드**로 열린다. 배경이 바뀌고 그 프리팹만 보인다. 여기서 고치면 원본이 바뀐다. Hierarchy 위쪽의 화살표(`<`)를 누르면 원래 씬으로 돌아온다.

적 100마리를 프리팹 하나로 관리할 수 있는 이유가 이것이다. 체력을 바꾸고 싶으면 원본만 고치면 된다.

## 2. Instantiate로 찍어내기
{:.briefing-heading}

이제 코드에서 프리팹을 복제해 씬에 만든다. 스페이스를 누르면 총알이 생기는 예다.

```csharp
[SerializeField] GameObject bulletPrefab;

void Update()
{
    if (Input.GetKeyDown(KeyCode.Space))
    {
        Instantiate(bulletPrefab, transform.position, Quaternion.identity);
    }
}
```

`Instantiate(원본, 위치, 회전)`. 원본을 복제해서 그 위치에 그 회전으로 놓는다. 원본은 Day 1처럼 Inspector의 칸에 **Project 창의 프리팹을** 끌어다 놓아 연결한다.

- `GameObject`: 게임 오브젝트 통째를 담는 자료형이다. 프리팹도 GameObject라서 이 칸에 들어간다.
- `Quaternion`: 유니티가 **회전**을 다루는 자료형이다. 속은 복잡한 수학이지만, 지금은 "회전 값"이라고만 알면 충분하다.
- `Quaternion.identity`: "회전 없음". 프리팹이 원래 놓인 방향 그대로다.

플레이어가 바라보는 방향으로 총알을 돌려서 만들고 싶으면 세 번째 칸에 내 회전을 넣는다.

```csharp
Instantiate(bulletPrefab, transform.position, transform.rotation);
```

순서는 **원본, 위치, 회전**이다. 위치 자리에 회전을 넣으면 자료형이 맞지 않아 에러가 난다.

> 원본 칸을 비워 두고 스페이스를 누르면 "복제할 원본이 없다"는 에러가 난다. Day 1의 NullReferenceException처럼 Inspector 연결부터 확인한다.
{: .prompt-tip }

## 3. 만든 것 다루고 치우기
{:.briefing-heading}

### Instantiate도 값을 돌려준다

```csharp
GameObject b = Instantiate(bulletPrefab, transform.position, transform.rotation);
b.GetComponent<Bullet>().damage = 20;
```

Instantiate는 void가 아니다. **방금 만든 복사본**을 돌려준다. 받아 두면 그 총알 하나에만 데미지를 따로 정하는 식으로 손댈 수 있다. 기초 Day 4에서 배운 "부른 쪽이 결과를 받아 써야 하면 자료형을 쓴다"가 바로 이 경우다. GameObject를 복제했으니 돌아오는 것도 GameObject다.

### 총알이 영원히 남지 않게

```csharp
public class Bullet : MonoBehaviour
{
    public int damage = 10;
    [SerializeField] float speed = 20f;

    void Start()
    {
        Destroy(gameObject, 3f);   // 3초 뒤 스스로 삭제
    }

    void Update()
    {
        transform.Translate(Vector3.forward * speed * Time.deltaTime);
    }
}
```

`Destroy`에 두 번째 값으로 초를 넣으면 **그 시간 뒤에** 지운다. 이 줄이 없으면 화면 밖으로 날아간 총알이 사라지지 않고 계속 쌓인다. 쏠 때마다 오브젝트가 늘어나서 게임이 점점 무거워진다. 플레이 중에 Hierarchy를 보면 `Bullet(Clone)`이 줄줄이 쌓이는 게 보인다. 복제된 오브젝트에는 이름 뒤에 `(Clone)`이 붙는다.

`transform.Translate`는 "지금 위치에서 이만큼 옮겨"라는 함수다. 기초 Day 5의 `transform.position += ...`와 비슷한데, 기본으로 **내가 바라보는 방향 기준**으로 움직인다. 그래서 `Vector3.forward`가 "월드의 앞"이 아니라 "총알의 앞"이 된다. 돌려서 만든 총알이 제 방향으로 날아가는 이유다.

### gameObject와 this

```csharp
Destroy(gameObject);   // 이 스크립트가 붙은 오브젝트째 삭제
Destroy(this);         // 이 스크립트 컴포넌트만 삭제
```

스크립트 안에서 소문자 `gameObject`는 **이 스크립트가 붙어 있는 오브젝트**다. 소문자 `transform`이 내 Transform이었던 것처럼 바로 쓸 수 있다. `this`는 **이 스크립트 자신**, 오브젝트에 붙은 여러 컴포넌트 중 하나다.

기초 Day 7에서 `Destroy(other)`는 Collider만 지우고, `Destroy(other.gameObject)`가 코인을 통째로 지웠던 것과 같은 관계다. 오브젝트째 없애려면 늘 gameObject를 넘긴다.

## 4. 스포너 만들기
{:.briefing-heading}

### 코루틴 + Instantiate

2초마다 랜덤 위치에 적을 만든다.

```csharp
[SerializeField] GameObject enemyPrefab;
[SerializeField] float interval = 2f;

void Start()
{
    StartCoroutine(SpawnLoop());
}

IEnumerator SpawnLoop()
{
    while (true)
    {
        float x = Random.Range(-5f, 5f);
        Vector3 pos = new Vector3(x, 0f, 10f);
        Instantiate(enemyPrefab, pos, Quaternion.identity);

        yield return new WaitForSeconds(interval);
    }
}
```

Day 2에서 배운 코루틴, while, 오늘 배운 Instantiate에 Random이 하나 더해졌다. 이번 `while (true)`는 안에 yield가 있어서 안전하다. 게임 내내 2초에 한 번씩 돌고, 이 스포너 오브젝트가 꺼지거나 지워지면 같이 멈춘다.

### Random.Range: 정수는 끝값을 뺀다

`Random.Range(최소, 최대)`는 그 사이의 무작위 값을 준다. 그런데 넣는 값이 소수냐 정수냐에 따라 규칙이 다르다.

```csharp
Random.Range(0f, 1f);   // float: 0 ~ 1, 끝값 1도 나올 수 있다
Random.Range(0, 3);     // int: 0, 1, 2 중 하나. 3은 안 나온다
Random.Range(1, 7);     // 주사위 1~6
```

| 넣는 값 | 결과 | 끝값 |
|---|---|---|
| `0f`, `1f` (float) | 0.0 ~ 1.0 사이 소수 | **포함** |
| `0`, `3` (int) | 0, 1, 2 중 정수 | **제외** |

같은 함수인데 규칙이 달라서 헷갈리기 쉽다. 정수 버전이 끝값을 빼는 데는 이유가 있다. 배열에서 하나를 뽑을 때 딱 맞는다.

```csharp
string[] drops = { "포션", "열쇠", "코인" };
string pick = drops[Random.Range(0, drops.Length)];
```

drops.Length는 3이고, `Random.Range(0, 3)`은 0, 1, 2 중 하나다. 배열 번호가 정확히 0, 1, 2이니 모든 칸이 고르게 나온다. 여기에 `drops.Length - 1`을 쓰면 0, 1만 나와서 마지막 아이템 "코인"은 **절대** 안 나온다. 기초 Day 3에서 배운 "배열 번호는 0부터 Length - 1까지"와 짝을 이루는 규칙이다.

## 직접 해 보기
{:.briefing-heading}

기초 Day 7의 코인을 프리팹으로 바꾸고, 시작하면 코인이 1초 간격으로 하나씩 랜덤 위치에 나타나게 만든다.

### A. 코인 프리팹 만들기

1. Project 창에 `Prefabs` 폴더를 만든다(우클릭 → **Create → Folder**). 정리용이라 없어도 되지만 있으면 찾기 쉽다.
2. 씬의 코인 하나를 골라 `Coin`으로 이름을 바꾸고, Project 창의 `Prefabs` 폴더로 **끌어다 놓는다.** Hierarchy의 Coin 이름이 파란색이 되면 프리팹이 만들어진 것이다.
3. Project 창의 Coin 프리팹을 더블클릭해서 프리팹 편집 모드로 연다. 기초 Day 7의 "더 해 보기"에서 만든 `Coin` 회전 스크립트를 여기서 붙인다. 아직 안 만들었다면 지금 만든다.

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

4. Hierarchy 위의 `<`로 씬으로 돌아온다. 프리팹 복사본인 Coin이 같이 돌기 시작한다(플레이하면 보인다). 원본에 붙였더니 복사본에도 붙은 것이다.
5. 이제 씬에 있는 코인을 **전부 지운다.** 원본은 Project 창에 있으니 걱정 없다. 앞으로는 코드가 찍어낸다.

### B. 코인 스포너

1. Hierarchy에서 **Create Empty**로 빈 오브젝트를 만들고 이름을 `CoinSpawner`로 한다.
2. `CoinSpawner` 스크립트를 만들어 붙인다.

```csharp
using System.Collections;
using UnityEngine;

public class CoinSpawner : MonoBehaviour
{
    [SerializeField] GameObject coinPrefab;
    [SerializeField] int count = 5;
    [SerializeField] float interval = 1f;
    [SerializeField] float range = 4f;

    void Start()
    {
        StartCoroutine(SpawnCoins());
    }

    IEnumerator SpawnCoins()
    {
        for (int i = 0; i < count; i++)
        {
            float x = Random.Range(-range, range);
            float z = Random.Range(-range, range);
            Vector3 pos = new Vector3(x, 0.5f, z);

            Instantiate(coinPrefab, pos, Quaternion.identity);

            yield return new WaitForSeconds(interval);
        }
    }
}
```

3. CoinSpawner의 **Coin Prefab** 칸에 Project 창의 Coin 프리팹을 끌어다 놓는다. Hierarchy의 오브젝트가 아니라 **Project 창의 원본**을 넣는다.
4. 플레이한다. 코인이 1초에 하나씩 바닥 여기저기에 나타나고, 다섯 개를 다 주우면 "스테이지 클리어!"가 찍힌다. PlayerController의 goal(5)과 스포너의 count(5)가 같아야 한다.

`range`가 4인 이유: 기본 Plane은 가로세로 10이라 가운데에서 -5 ~ 5까지다. 가장자리에 붙지 않게 4로 잡았다. Plane의 Scale을 키웠다면 range도 같이 키운다.

이번엔 while 대신 for를 썼다. "5개만"처럼 횟수가 정해져 있으니까. for 안에 yield를 넣으면 시간차 반복이 된다는 Day 2의 깜빡이기와 같은 모양이다.

해 볼 것: Coin 프리팹 원본을 열어 Scale을 0.8로 바꿔 보자. 다음에 플레이하면 찍혀 나오는 코인이 전부 커져 있다. 코드는 한 줄도 안 고쳤다.

### 더 해 보기: 총알 쏘기

1. **3D Object → Sphere**를 만들고 Scale을 0.2로 줄인다. Sphere Collider는 지운다(플레이어를 밀어내지 않게). 이름은 `Bullet`.
2. 위 3번의 `Bullet` 스크립트를 붙이고, Project 창에 끌어다 프리팹으로 만든 뒤 씬의 것은 지운다.
3. PlayerController에 쏘는 코드를 넣는다. 스페이스는 점프라서 F 키를 쓴다.

```csharp
[SerializeField] GameObject bulletPrefab;

// Update 안에
if (Input.GetKeyDown(KeyCode.F))
{
    Vector3 pos = transform.position + transform.forward;   // 내 앞 1m
    Instantiate(bulletPrefab, pos, transform.rotation);
}
```

플레이 중에 F를 연타하면서 Hierarchy를 보자. `Bullet(Clone)`이 늘어났다가 3초 뒤에 하나씩 사라진다. Bullet의 `Destroy(gameObject, 3f)` 줄을 지우고 다시 해 보면 끝없이 쌓인다.

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. 스포너 칸에 Hierarchy의 코인을 넣었더니 이상해.**<br>
씬에 있는 코인을 넣으면 **그 코인을 복제**한다. 처음엔 되는 것 같지만, 그 코인을 주워서 지우면 원본이 사라져서 다음 Instantiate에서 에러가 난다. 찍어낼 원본은 늘 **Project 창의 프리팹**을 넣는다.

**Q. 프리팹 원본에 씬의 오브젝트를 끌어다 놓을 수가 없어.**<br>
정상이다. 프리팹은 어느 씬에서든 쓸 수 있는 파일이라서, 특정 씬 안의 오브젝트를 가리킬 수 없다. 씬에 놓인 복사본에는 넣을 수 있지만, Instantiate로 새로 찍어낸 것은 그 칸이 비어 있다. 이럴 때는 만든 직후에 돌려받은 오브젝트에 넣어 준다. 이 문제는 심화 Day 6에서 적을 복제할 때 다시 만난다.

**Q. 코인이 바닥에 파묻히거나 공중에 떠.**<br>
`new Vector3(x, 0.5f, z)`의 0.5가 높이다. 코인 크기가 바뀌었으면 이 값도 맞춘다. Y를 `[SerializeField]`로 꺼내 두면 Inspector에서 바로 맞출 수 있다.

**Q. `Random.Range`에 빨간 줄이 생겼어. "모호하다"는 에러야.**<br>
파일 맨 위에 `using System;`이 있으면 생긴다. C#에도 `Random`이라는 같은 이름이 있어서, 어느 쪽인지 모르겠다는 에러다. 심화 Day 5에서 `using System;`을 쓰게 되는데, 같은 파일에서 Random을 쓴다면 `UnityEngine.Random.Range(...)`처럼 앞에 붙여서 구분한다.

**Q. Instantiate를 Update 안에서 조건 없이 부르면?**<br>
1초에 수십~수백 개가 생긴다. Day 2의 StartCoroutine과 같은 실수다. 키를 누른 순간(`GetKeyDown`), 코루틴의 시간차, 쿨타임으로 제한한다.

## 현업에서는
{:.briefing-heading}

- **반복해서 나오는 건 무조건 프리팹.** 코인, 적, 총알, 이펙트, UI 한 줄까지 프리팹으로 만든다. 씬에 직접 놓는 것도 프리팹 복사본으로 놓아야 나중에 한 번에 고칠 수 있다.
- **프리팹 칸은 쓸 자료형으로 받는다.** `[SerializeField] Bullet bulletPrefab;`처럼 GameObject 대신 스크립트 자료형으로 받으면, `Instantiate`가 바로 `Bullet`을 돌려준다. `GetComponent` 없이 `b.damage = 20;`으로 쓸 수 있고, Bullet 스크립트가 없는 엉뚱한 프리팹은 칸에 들어가지도 않는다.

```csharp
[SerializeField] Bullet bulletPrefab;

Bullet b = Instantiate(bulletPrefab, pos, transform.rotation);
b.damage = 20;
```

- **많이 만들고 지우는 건 풀링한다.** 아래 꿀팁 참고.

> **💡 꿀팁: 오브젝트 풀링**
>
> Instantiate와 Destroy는 생각보다 무거운 작업이다. 총알이나 이펙트처럼 1초에 수십 개씩 만들고 지우면, 버려진 메모리를 청소하는 일(가비지 컬렉션) 때문에 게임이 순간순간 뚝 끊긴다.
>
> 그래서 미리 여러 개 만들어 두고, 다 쓴 건 지우지 않고 `SetActive(false)`로 **꺼 둔다.** 다시 필요하면 꺼 둔 것을 위치만 옮겨서 `SetActive(true)`로 켜서 재사용한다. 이걸 **오브젝트 풀링**이라고 한다. 수영장(pool)에 물을 받아 두고 퍼 쓰는 느낌이다.
>
> ```csharp
> bullet.SetActive(false);              // 다 쓴 총알은 끄기
>
> bullet.transform.position = pos;      // 쏠 때는 꺼 둔 걸
> bullet.SetActive(true);               // 다시 켜서 쓰기
> ```
>
> 유니티에는 `ObjectPool`이라는 기본 도구(`UnityEngine.Pool`)도 있다. 처음에는 Instantiate/Destroy로 만들고, 버벅임이 느껴질 때 풀링으로 바꿔도 늦지 않다.
{: .prompt-tip }

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **심화 Day 3**과 같은 내용이다.

- [Instantiate로 찍어내기](https://hlcho426.github.io/unity-csharp-week/#a3l1): 프리팹, 위치, 회전
- [만든 것 다루고 치우기](https://hlcho426.github.io/unity-csharp-week/#a3l2): 반환값 받기, 시간 뒤 Destroy, gameObject와 this
- [스포너 만들기](https://hlcho426.github.io/unity-csharp-week/#a3l3): Random.Range, 반복 생성, 풀링

## 정리
{:.briefing-heading}

- 프리팹 = Project 창에 저장한 오브젝트 원본. 원본을 고치면 복사본 전부에 반영된다
- `Instantiate(원본, 위치, 회전)`으로 복제한다. `Quaternion.identity`는 회전 없음
- Instantiate는 만든 복사본을 돌려준다. 받아서 그 하나만 설정할 수 있다
- `Destroy(gameObject, 3f)`로 시간 뒤에 스스로 지운다. 안 지우면 계속 쌓인다
- `gameObject`는 이 스크립트가 붙은 오브젝트, `this`는 이 스크립트
- `Random.Range`: float는 끝값 포함, int는 끝값 제외. 배열 뽑기는 `arr[Random.Range(0, arr.Length)]`
- 많이 만들고 지우는 건 껐다 켜서 재사용(풀링)

다음 글은 심화 Day 4, 상태 머신. 플레이어가 다가오면 쫓아오고, 가까우면 공격하는 적을 만든다. "대기, 추격, 공격"이라는 상태를 코드로 나누는 방법이다.
