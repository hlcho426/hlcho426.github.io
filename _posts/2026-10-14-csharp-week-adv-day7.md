---
title: "<유니티 C#> 심화 Day 7: 세이브와 로드 (PlayerPrefs, JsonUtility, 파일 저장)"
date: 2026-10-14 15:24:00 +0900
description: "볼륨이나 최고 기록 같은 값 하나는 PlayerPrefs로, 코인과 위치처럼 여러 값은 클래스로 묶어 JSON 파일로 저장한다. 세이브 파일이 어디에 생기는지와 직접 열어 고치는 법까지."
series: 유니티 C# 일주일
series_title: "심화 Day 7: 세이브와 로드"
categories: [게임 제작 공부, 유니티]
tags: [유니티, C#, 학습앱, Claude, 유니티 C# 공부]
image:
  path: /assets/img/unitystudy/csharp_image.png
  width: 1200
  height: 675
---

{% include series.html %}

지금 게임은 플레이를 멈추면 모든 게 처음으로 돌아간다. 몇 초 만에 클리어했는지도, 코인을 몇 개 모았는지도 남지 않는다. 변수는 게임이 켜져 있는 동안 메모리에만 있다가, 게임이 꺼지면 사라지기 때문이다. 남기려면 **게임 밖 어딘가에 적어 둬야** 한다.

저장할 것은 크게 세 종류다.

| 종류 | 예 | 오늘 쓰는 도구 |
|---|---|---|
| 설정 | 소리 크기, 그래픽 옵션 | PlayerPrefs |
| 기록 | 최고 점수, 최단 클리어 시간 | PlayerPrefs |
| 진행 | 코인, 위치, 인벤토리, 퀘스트 | 클래스로 묶어서 JSON 파일로 |

[Day 6](/posts/csharp-week-adv-day6/)의 ScriptableObject는 "게임에 원래 들어 있는 데이터"였다. 오늘은 "플레이하면서 생긴 데이터"를 남기는 법이다.

**오늘의 목표**

- PlayerPrefs로 값 하나를 저장하고 불러올 수 있다
- 저장할 값들을 클래스로 묶어 JSON 글자로 바꿀 수 있다
- JSON을 파일로 쓰고 읽어서 세이브와 로드를 만들 수 있다

## 1. PlayerPrefs: 가장 간단한 저장소
{:.briefing-heading}

```csharp
// 저장
PlayerPrefs.SetFloat("volume", 0.8f);
PlayerPrefs.SetInt("bestScore", 1200);
PlayerPrefs.Save();

// 불러오기
float vol = PlayerPrefs.GetFloat("volume", 1f);
int best = PlayerPrefs.GetInt("bestScore", 0);
```

**이름(키)을 붙여 값 하나씩** 저장한다. 사물함에 이름표를 붙이고 물건 하나를 넣어 두는 것과 같다. `"volume"` 사물함에 0.8을 넣고, 나중에 `"volume"` 사물함을 열어 꺼낸다.

| 저장 | 불러오기 | 자료형 |
|---|---|---|
| `SetInt(키, 값)` | `GetInt(키, 기본값)` | int |
| `SetFloat(키, 값)` | `GetFloat(키, 기본값)` | float |
| `SetString(키, 값)` | `GetString(키, 기본값)` | string |

Get의 **두 번째 값은 저장된 적이 없을 때 돌려줄 기본값**이다. 게임을 처음 켰을 때는 "volume" 사물함이 비어 있으니 `GetFloat("volume", 1f)`는 1을 돌려준다. 첫 실행에 소리가 최대로 나오게 하는 것이다.

`PlayerPrefs.Save()`는 지금까지 Set 한 것을 바로 디스크에 쓴다. 게임이 정상적으로 종료될 때도 저장되지만, 갑자기 꺼지면 날아갈 수 있어서 중요한 값을 저장한 직후에는 불러 둔다.

그 밖에 자주 쓰는 것:

- `PlayerPrefs.HasKey("volume")`: 그 키로 저장된 게 있는지 true/false
- `PlayerPrefs.DeleteKey("volume")`: 그 키 하나 지우기

### 키는 대소문자까지 똑같아야 한다

저장할 때 `"Volume"`, 불러올 때 `"volume"`으로 쓰면 **다른 사물함**이다. 에러도 안 나고 그냥 기본값이 나온다. "분명 저장했는데 왜 안 불러와지지?" 버그의 단골 원인이다.

> **💡 꿀팁: 키 이름은 한 곳에 상수로**
>
> ```csharp
> const string VolumeKey = "volume";
>
> PlayerPrefs.SetFloat(VolumeKey, 0.8f);       // 저장
> float v = PlayerPrefs.GetFloat(VolumeKey, 1f);  // 불러오기
> ```
>
> `const`는 "절대 안 바뀌는 값"이라는 표시다. 키 이름을 한 번만 적어 두고 그 이름으로 쓰면, `VolumeKye`처럼 오타가 나면 컴파일러가 빨간 에러로 잡아 준다. `"volume"`을 여기저기 직접 쓰면 `"Volume"` 같은 오타가 조용한 버그가 된다.
>
> 애니메이터 파라미터 이름, 태그 이름처럼 **글자로 된 이름**은 모두 같은 방법을 쓴다. Day 4에서 상태 이름을 string 대신 enum으로 만든 것과 같은 이유다.
{: .prompt-tip }

### PlayerPrefs가 안 맞는 것

PlayerPrefs는 값 하나하나를 따로 저장하는 구조다. 인벤토리 아이템 30개, 퀘스트 10개, 맵의 상자 50개를 열었는지를 전부 키 하나씩 만들어 저장하면 금방 감당이 안 된다. 그리고 Windows에서는 파일이 아니라 레지스트리라는 시스템 저장소에 들어가서, 직접 열어 보기도 어렵다. 그래서 PlayerPrefs는 **설정과 간단한 기록**에만 쓰고, 게임 진행 데이터는 다음 방법을 쓴다.

## 2. JSON으로 묶어서 저장
{:.briefing-heading}

### 세이브 데이터 상자 만들기

```csharp
using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public class SaveData
{
    public int coin;
    public Vector3 position;
    public List<string> items = new List<string>();
}
```

저장할 것들을 **클래스 하나로** 묶는다. Day 1에서 배운 순수 클래스다. 맨 위의 `[System.Serializable]`은 "이 클래스는 글자로 바꿔서 저장할 수 있다"는 표시다. 이 표시가 있어야 유니티의 저장 도구가 안을 들여다본다.

### 객체 ↔ 글자 바꾸기

```csharp
SaveData data = new SaveData();
data.coin = 30;
data.position = transform.position;

string json = JsonUtility.ToJson(data);
// {"coin":30,"position":{"x":1.0,"y":0.0,"z":5.0},"items":[]}

SaveData loaded = JsonUtility.FromJson<SaveData>(json);
Debug.Log(loaded.coin);   // 30
```

**JSON**은 데이터를 글자로 적는 형식이다. `{"이름":값}` 모양이라 사람이 읽어도 대충 알아볼 수 있다. 웹, 앱, 게임 어디서나 쓰는 표준 형식이다.

- `JsonUtility.ToJson(객체)`: 객체 → 글자. To는 "~로 바꾸기"
- `JsonUtility.FromJson<자료형>(글자)`: 글자 → 객체. From은 "~에서 되돌리기". 꺾쇠 안에 어떤 클래스로 되돌릴지 적는다. `GetComponent<Rigidbody>()`의 꺾쇠와 같은 모양이다

Vector3는 x, y, z 세 칸짜리 묶음으로, List는 `[ ]` 목록으로 적힌 게 보인다.

### JsonUtility가 저장할 수 있는 것

JsonUtility는 유니티에 들어 있는 가벼운 도구라서, 저장할 수 있는 게 정해져 있다.

| 저장된다 | 저장 안 된다 |
|---|---|
| int, float, bool, string | **Dictionary** |
| Vector3, Color 같은 유니티 기본 묶음 | 프로퍼티 (`int Coin { get; set; }` 모양) |
| 배열, List | private 변수 (`[SerializeField]`를 안 붙였으면) |
| `[System.Serializable]`을 붙인 내 클래스 | `[System.Serializable]`을 안 붙인 내 클래스 |

오른쪽 것들은 **에러 없이 조용히 빠진다.** 저장은 됐다는데 불러오면 그 칸만 비어 있다. 특히 SaveData 안에 다른 클래스(예: `QuestData`)를 넣고 그 클래스에 `[System.Serializable]`을 빼먹으면, 퀘스트 진행만 통째로 사라진다. 찾기 정말 어려운 버그다.

Dictionary(이름표로 찾는 목록, 다지기 Day 2)를 저장하고 싶으면 "키와 값" 클래스의 List로 바꿔서 저장하거나, 더 많은 걸 지원하는 다른 JSON 도구를 쓴다(시스템 코스 Day 5의 Newtonsoft Json).

## 3. 파일로 쓰고 읽기
{:.briefing-heading}

JSON 글자를 만들었으니 이제 파일로 쓰면 된다.

```csharp
using System.IO;
using UnityEngine;

public class SaveSystem : MonoBehaviour
{
    string path => Application.persistentDataPath + "/save.json";

    public void Save(SaveData data)
    {
        string json = JsonUtility.ToJson(data);
        File.WriteAllText(path, json);
    }

    public SaveData Load()
    {
        if (!File.Exists(path))
            return new SaveData();   // 첫 플레이: 빈 데이터

        string json = File.ReadAllText(path);
        return JsonUtility.FromJson<SaveData>(json);
    }
}
```

| 코드 | 하는 일 |
|---|---|
| `Application.persistentDataPath` | 게임이 안전하게 파일을 쓸 수 있는 폴더. PC, 모바일 어디서나 알맞은 곳을 알려 준다 |
| `File.WriteAllText(경로, 글자)` | 파일에 글자를 쓴다. 이미 있으면 덮어쓴다 |
| `File.ReadAllText(경로)` | 파일의 글자를 전부 읽어 온다 |
| `File.Exists(경로)` | 그 파일이 있는지 true/false |

`File`은 C#의 파일 도구라서 맨 위에 `using System.IO;`가 필요하다.

**Save는 void, Load는 SaveData**인 이유는 기초 Day 4의 기준 그대로다. Save는 저장이라는 일만 하고 돌려줄 게 없다. Load는 꺼낸 데이터를 부른 쪽에 돌려줘야 한다. 그래서 부르는 쪽에서 이렇게 바로 이어 쓸 수 있다.

```csharp
transform.position = saveSystem.Load().position;
```

Load 맨 위의 `if (!File.Exists(path))`는 기초 Day 8의 가드다. 처음 플레이할 때는 세이브 파일이 없으니, 읽으려다 에러가 나기 전에 빈 SaveData를 돌려주고 끝낸다.

`string path => ...`는 "**부를 때마다** 이 값을 계산해서 줘"라는 짧은 표현이다. path를 쓸 때마다 화살표 오른쪽이 실행된다. 왜 그냥 변수로 안 만들었는지는 아래 "자주 헷갈리는 것"에 있다.

## 직접 해 보기
{:.briefing-heading}

코인 줍기에 두 가지를 넣는다. 최단 클리어 시간은 PlayerPrefs로, 코인 수와 위치는 JSON 파일로.

### A. 최단 기록 저장 (PlayerPrefs)

`PlayerController`에 상수와 함수를 추가한다.

```csharp
const string BestTimeKey = "bestTime";

void SaveBestTime()
{
    float time = Time.timeSinceLevelLoad;   // 씬이 시작되고 흐른 시간
    float best = PlayerPrefs.GetFloat(BestTimeKey, 9999f);

    if (time < best)
    {
        PlayerPrefs.SetFloat(BestTimeKey, time);
        PlayerPrefs.Save();
        Debug.Log("신기록! " + time.ToString("F1") + "초");
    }
    else
    {
        Debug.Log("기록 " + time.ToString("F1") + "초 (최고 " + best.ToString("F1") + "초)");
    }
}
```

클리어하는 곳에서 부른다.

```csharp
if (coin >= goal && !isCleared)
{
    isCleared = true;
    Debug.Log("스테이지 클리어!");
    SaveBestTime();
    onCleared.Invoke();
}
```

그리고 Start에 한 줄을 넣어 시작할 때 최고 기록을 보여 준다.

```csharp
if (PlayerPrefs.HasKey(BestTimeKey))
    Debug.Log("최고 기록: " + PlayerPrefs.GetFloat(BestTimeKey).ToString("F1") + "초");
```

`GetFloat(BestTimeKey, 9999f)`의 9999가 핵심이다. 처음엔 기록이 없으니 9999초가 최고 기록인 셈이고, 어떤 기록이든 그보다 빠르니 첫 클리어는 무조건 신기록이 된다. 기본값을 0으로 했다면 "0초보다 빨라야 신기록"이라 영원히 신기록이 안 나온다.

플레이해서 클리어하고, 플레이를 껐다가 다시 켜 보자. 콘솔 첫 줄에 최고 기록이 나온다. 플레이를 멈춰도 남아 있다. 한 번 더 클리어하면 기록과 비교해 준다.

### B. K로 저장, L로 불러오기 (JSON 파일)

1. `SaveData` 스크립트를 만들고 내용을 바꾼다.

```csharp
using UnityEngine;

[System.Serializable]
public class SaveData
{
    public int coin;
    public Vector3 position;
}
```

2. `PlayerController` 맨 위에 `using System.IO;`를 넣고, 아래를 추가한다.

```csharp
string SavePath => Path.Combine(Application.persistentDataPath, "save.json");

void SaveGame()
{
    SaveData data = new SaveData();
    data.coin = coin;
    data.position = transform.position;

    string json = JsonUtility.ToJson(data, true);
    File.WriteAllText(SavePath, json);
    Debug.Log("저장했다: " + SavePath);
}

void LoadGame()
{
    if (!File.Exists(SavePath))
    {
        Debug.Log("세이브 파일이 없다");
        return;
    }

    string json = File.ReadAllText(SavePath);
    SaveData data = JsonUtility.FromJson<SaveData>(json);

    coin = data.coin;
    transform.position = data.position;
    rb.linearVelocity = Vector3.zero;   // 떨어지던 중이었다면 멈추기
    Debug.Log("불러왔다: 코인 " + coin);
}
```

3. Update에 키 두 개를 연결한다.

```csharp
if (Input.GetKeyDown(KeyCode.K)) SaveGame();
if (Input.GetKeyDown(KeyCode.L)) LoadGame();
```

달라진 점 두 가지:

- `Path.Combine(폴더, 파일 이름)`: 폴더와 파일 이름 사이에 `/`를 알맞게 넣어 준다. 위 예제처럼 `+ "/save.json"`으로 붙여도 되지만, 슬래시를 빼먹거나 두 번 넣는 실수가 없다.
- `JsonUtility.ToJson(data, true)`: 두 번째 값 true는 "보기 좋게 줄 바꿔서"라는 뜻이다. 파일을 직접 열어 볼 거라서 켰다.

코인을 두 개 줍고 아무 데나 가서 **K**를 누른다. 플레이를 끄고 다시 켠 다음 **L**을 누르면, 저장한 자리로 순간이동하고 "불러왔다: 코인 2"가 찍힌다.

### C. 세이브 파일 열어 보기

> **💡 꿀팁: 세이브 파일은 어디에 있을까?**
>
> K를 누를 때 콘솔에 찍힌 경로가 세이브 파일 위치다. Windows라면 보통 이런 모양이다.
>
> `C:/Users/내이름/AppData/LocalLow/DefaultCompany/프로젝트이름/save.json`
>
> AppData는 숨김 폴더라서 탐색기에서 안 보일 수 있다. 탐색기 주소창에 `%userprofile%\AppData\LocalLow`를 붙여 넣으면 바로 간다. DefaultCompany는 **Edit → Project Settings → Player**의 Company Name이다.
>
> JSON은 글자 파일이라 메모장으로 열 수 있다.
>
> ```json
> {
>     "coin": 2,
>     "position": {
>         "x": 1.5,
>         "y": 0.5,
>         "z": -2.0
>     }
> }
> ```
>
> 여기서 coin을 4로 고치고 저장한 뒤, 게임에서 L을 누르고 코인 하나만 주워 보자. 바로 클리어된다. 후반부를 테스트할 때 처음부터 다시 하지 않아도 되는 이유다. 처음부터 다시 하고 싶으면 save.json을 지우면 된다.
{: .prompt-tip }

L로 불러와도 바닥의 코인은 다시 다섯 개 나타난다는 걸 눈치챘을 수도 있다. 지금은 "몇 개 주웠는지"만 저장하고 "**어떤** 코인을 주웠는지"는 저장하지 않았기 때문이다. 진짜 세이브라면 코인마다 번호를 붙여 주운 번호 목록(`List<int>`)까지 저장하고, 불러올 때 그 코인은 만들지 않아야 한다. 세이브 시스템이 어려운 이유가 이것이다. 무엇을 저장해야 "그 순간"이 되살아나는지 하나하나 정해야 한다.

## 자주 헷갈리는 것
{:.briefing-heading}

**Q. path를 `string path = Application.persistentDataPath + "/save.json";`처럼 변수로 만들면 안 돼?**<br>
MonoBehaviour의 필드에 처음 값을 넣는 자리에서는 `Application.persistentDataPath` 같은 유니티 기능을 부를 수 없다. 스크립트가 만들어지는 순간이라 유니티가 아직 준비가 안 됐기 때문이다. 플레이하면 "이 자리에서 부를 수 없다"는 에러가 난다. `=>`로 만들면 path를 **쓸 때** 계산하니까 괜찮다. 아니면 필드는 비워 두고 Start에서 `path = ...;`로 넣어도 된다.

**Q. ToJson이 `{}`만 돌려줘.**<br>
세 가지를 본다. 클래스 위에 `[System.Serializable]`이 있는지, 변수들이 `public`인지, `{ get; set; }`이 붙은 프로퍼티는 아닌지. 셋 다 JsonUtility가 조용히 건너뛰는 경우다.

**Q. PlayerPrefs를 지우고 처음부터 테스트하고 싶어.**<br>
에디터 메뉴 **Edit → Clear All PlayerPrefs**를 누르면 이 프로젝트의 PlayerPrefs가 전부 지워진다. 코드로는 `PlayerPrefs.DeleteAll()`이다. 실제 게임에 넣을 때는 설정까지 다 날아가니 조심한다.

**Q. 불러왔는데 코인 수는 맞고 위치만 이상해.**<br>
Rigidbody가 있는 오브젝트를 순간이동시키면, 물리가 바로 다음 순간에 위치를 다시 계산한다. 떨어지던 속도가 남아 있으면 불러온 자리에서 그대로 떨어진다. 위 코드에서 `rb.linearVelocity = Vector3.zero;`로 속도를 없앤 이유다. (Unity 6 이전 버전은 `rb.velocity`)

**Q. 세이브 파일을 플레이어가 메모장으로 고치면 치트 아니야?**<br>
맞다. 혼자 하는 게임이라면 보통 크게 신경 쓰지 않는다. 순위표나 유료 재화처럼 다른 사람과 얽힌 값은 기기에 저장하지 않고 서버에서 관리한다. 파일을 암호화하는 방법도 있지만, 기기 안에 있는 이상 완벽히 막을 수는 없다.

## 현업에서는
{:.briefing-heading}

- **세이브 데이터에 버전 번호를 넣는다.** `public int version = 1;` 한 칸을 넣어 두면, 업데이트로 SaveData 구조가 바뀌었을 때 "옛 버전 세이브구나" 하고 변환해 줄 수 있다. 출시 뒤에 이걸 안 넣었던 걸 후회하는 경우가 많다.
- **처음과 달라진 것만 저장한다.** 맵의 상자 500개를 전부 저장하는 게 아니라 "열린 상자 번호 목록"만 저장한다. 파일이 작고, 데이터(Day 6의 에셋)를 고쳐도 세이브가 덜 깨진다.
- **덮어쓰다 꺼지는 사고에 대비한다.** 저장하는 도중에 게임이 꺼지면 파일이 반만 쓰여 깨질 수 있다. 그래서 임시 파일에 먼저 다 쓴 다음 원래 파일과 바꾸거나, 세이브 슬롯을 두 개 두고 번갈아 쓴다.
- **저장 도구는 한 곳에 모은다.** 오늘은 PlayerController 안에 넣었지만, 보통은 SaveManager 같은 스크립트 하나가 저장과 불러오기를 맡고, 각 스크립트는 "내 저장할 값은 이거"만 넘긴다. 이런 "하나뿐인 관리자"를 만드는 법은 실전 Day 4에서 배운다.

## 앱에서 연습하기
{:.briefing-heading}

이 글은 앱의 **심화 Day 7**과 같은 내용이다.

- [PlayerPrefs: 간단 저장](https://hlcho426.github.io/unity-csharp-week/#a7l1): Set, Get, 기본값, 키 상수
- [JSON으로 묶어서 저장](https://hlcho426.github.io/unity-csharp-week/#a7l2): Serializable, JsonUtility
- [파일로 쓰고 읽기](https://hlcho426.github.io/unity-csharp-week/#a7l3): persistentDataPath, File

## 정리
{:.briefing-heading}

- 변수는 게임이 꺼지면 사라진다. 남기려면 게임 밖에 적어 둔다
- `PlayerPrefs.SetInt/SetFloat/SetString`으로 저장, `Get`으로 불러온다. Get의 두 번째 값은 저장된 게 없을 때의 기본값. 설정과 간단한 기록에 쓴다
- 키 이름은 대소문자까지 같아야 한다. `const` 상수로 한 곳에 적어 둔다
- 진행 데이터는 `[System.Serializable]` 클래스로 묶고, `JsonUtility.ToJson`으로 글자로, `FromJson<자료형>`으로 다시 객체로 바꾼다. Dictionary는 저장 못 한다
- `Application.persistentDataPath` 폴더에 `File.WriteAllText`로 쓰고 `File.ReadAllText`로 읽는다. 읽기 전에 `File.Exists`로 확인한다

다음 글은 심화 Day 8, 값 형식과 참조 형식. 심화 코스의 마지막 날이다. Day 1의 "가리키는 표지판", Day 4의 "복사해 온 값", Day 6의 "같은 파일을 가리킨다"가 모두 한 가지 원리로 풀린다.
