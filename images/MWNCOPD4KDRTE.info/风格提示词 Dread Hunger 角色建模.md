# Dread Hunger 角色建模风格提示词

> 调研日期：2026-11-19
> 来源：Unreal Engine 官方开发者访谈（2021-12）、Steam 商店页、IGN、GamingCypher、KeenGamer、虎扑玩家评测等

---

## 一、调研结论：风格到底由什么构成

**最有价值的一条（官方原话）**：开发者 Alex Quick 在 Unreal Engine 访谈中说——

> "Artistically, we were heavily inspired by the aesthetic of the Dishonored games. The grim, painterly style of those games is a great fit for the story we are trying to tell. A number of our characters were actually created by a character artist who also made characters for Dishonored 1 and 2!"

即：**《耻辱》（Dishonored）的阴郁绘画感 + 维多利亚时代美学**，并且部分角色就是《耻辱1/2》的美术师做的。这是理解这套风格的钥匙。

其他交叉验证的风格事实：

| 维度 | 结论 | 来源线索 |
|---|---|---|
| 风格定位 | 风格化写实（stylized realism），介于纯写实与卡通之间；比 TF2 沉稳，比《The Horror》柔和 | GamingCypher、KeenGamer |
| 角色面部 | 五官夸张、性格化到"刻板印象"程度；鼻型精雕（鹰钩鼻等），一眼读出职业与善恶 | 虎扑评测 |
| 建模精度 | 中等面数、轮廓略硬朗；不是次世代照片级，而是手工雕刻般的块面感 | Steam 中文评测（"建模僵硬、多边形捉急"） |
| 服装 | 19 世纪北极探险装束：厚重毛皮、羊毛、油布、皮革、实用层叠；职业用制服色编码 | 职业设定表、Steam |
| 配色 | 冷调雪蓝 / 灰白 / 骨白为主，职业标志性色为辅，火光与提灯作暖色点缀 | 多篇评测 |
| 氛围 | 暴风雪、白雾、幽暗洞穴天光、骨图腾与血魔法，克苏鲁式疯狂与背叛 | 官方访谈、IGN |
| 叙事底色 | 富兰克林探险队 + 《极地恶灵》(The Terror) + Lovecraft 式未知恐惧 | 官方访谈 |

---

## 二、主提示词（英文，可直接投喂）

这是通用风格前缀，后面接具体角色描述即可：

```
Character concept art in the grim painterly style of Dread Hunger and Dishonored —
stylized realism, semi-realistic 3D game character, medium-poly hand-sculpted look
with slightly angular planes and deliberate hard edges, exaggerated story-driven
facial features (prominent hooked or blunt nose, deep-set eyes, strong jawline),
expressive silhouette that reads profession and moral alignment at a single glance.
19th-century Victorian Arctic expedition clothing: heavy wool, oilcloth, worn leather,
fur trim, practical layered workwear with visible stitching and honest wear.
Muted desaturated palette of cold slate blue, frost grey and bone white, one signature
uniform color per character, warm amber accent from lantern or firelight.
Cinematic low-key lighting, biting fog and drifting snow, matte surfaces,
painterly brushwork texture, grounded in historical grime, Unreal Engine real-time
character render. Full body, neutral dark background, no text.
```

**中文对照**：阴郁绘画感、风格化半写实、中等面数手工雕刻感与刻意硬边、夸张且性格化的五官、一眼可读职业的剪影、19 世纪维多利亚北极探险装束（厚羊毛／油布／旧皮革／毛边／层叠工装／可见缝线与真实磨损）、低饱和冷色调（石板蓝／霜灰／骨白）+ 职业标志色 + 灯火暖色点缀、电影感低调照明、刺骨浓雾与飘雪、哑光材质、绘画笔触质感、历史污垢感、虚幻引擎实时渲染。

---

## 三、分项提示词模块

按需取用，拼在主提示词后面。

### 3.1 面部与体态

```
exaggerated caricature-like facial structure: sharp aquiline nose or blunt boxer's nose,
heavy brow ridge, deep-set eyes, hollowed cheeks, weathered skin with visible pores
and windburn, asymmetry and imperfection, distinct silhouette and posture that
telegraphs personality — anxious, stern, sly, or brutal
```

要点：鼻型是这套风格的灵魂。给每个角色一种可辨识的鼻形与下颌，不要"好看的通用脸"。体态比五官更能传递性格——佝偻、紧绷、外八字、叉腰，都可以写进去。

### 3.2 服装与材质

```
layered Victorian polar workwear: oilcloth parka, thick wool sweater, fur-lined hood,
canvas trousers, leather harness and tool belt, worn leather gloves or bare hands,
brass buckles, hand-stitched repairs, frost and soot stains, matte fabric with
visible weave, no glossy surfaces
```

材质关键词：`oilcloth / boiled wool / cracked leather / brass / canvas / fur ruff / frost blotches / soot stains / hand-stitched patches`

### 3.3 配色（职业色编码）

Dread Hunger 原版八职业的制服色，可直接借用这套编码逻辑：

| 职业 | 标志色 |
|---|---|
| 船长 Captain | 海军蓝 |
| 牧师 Chaplain | 黑 |
| 厨子 Cook | 白 |
| 医生 Doctor | 黄 |
| 工程师 Engineer | 蓝 + 黑手套 |
| 猎人 Hunter | 棕 |
| 皇家陆战队 Marine | 蓝 |
| 领航员 Navigator | 黑 + 黑手套 |

提示词写法：`muted [color] uniform as the character's signature color, desaturated and dirtied, against a cold slate-blue and bone-white arctic backdrop`

### 3.4 光照与氛围

```
overcast polar daylight or dim lantern-lit interior, cold blue ambient fill,
single warm amber key light from lantern or fire, volumetric fog, drifting snow
particles, hard-edged painterly shadows, muted highlights, no specular shine
```

### 3.5 3D 建模专项（给建模师 / AI 3D 的参数）

```
medium-poly game-ready character, 15k–40k triangles, clean quad topology,
hard-surface props kept low-poly, hand-sculpted stylized forms over subdivision
smoothing, PBR materials with high roughness (0.6–0.85), fabric anisotropy,
oxidized brass and worn leather, hand-painted texture overlays with grime and
edge wear, stylized normal maps, standard humanoid rig, extra care on thick
garment deformation, Unreal Engine 5 lit render, Lumen-style global illumination
```

---

## 四、负面提示词

```
photorealistic, hyperrealistic, glossy plastic skin, smooth anime features,
modern or sci-fi clothing, neon lighting, oversaturated colors, clean studio
product shot, chibi, cute, subdivision-smoothed blob, generic handsome face,
low detail, blurry, extra limbs, deformed hands, text, logo, watermark
```

---

## 五、参数建议

| 工具 | 建议 |
|---|---|
| Midjourney v6.1 | `--ar 3:2 --stylize 250 --style raw`（raw 抑制过度美化，保留粗粝感） |
| Stable Diffusion XL | Steps 30–40，CFG 6–8，DPM++ 2M Karras；配合 painterly / grimy 类 LoRA |
| 3D 流程 | ZBrush 手雕夸张体块 → Blender 减面（保留硬边）→ Substance 做旧材质 → UE5 冷光 + 暖点光渲染 |

---

## 六、套用示例：《孤岛余烬》五角色

把主提示词 + 下列角色片段拼接即可。

**沈泊舟（舰长）**
```
retired Chinese naval captain, mid-40s, stern weathered face, salt-and-pepper stubble,
short hooked nose, deep-set guilty eyes, tall rigid posture, dark navy oilcloth pea
coat with tarnished brass buttons, peaked captain's cap, leather cross-body strap,
six-shot revolver at hip, military dagger, worn leather gloves — signature color: navy blue
```

**顾栖梧（学者）**
```
female occult scholar, early 30s, intelligent wary expression, sharp straight nose,
thin lips, ink-stained fingers, slightly stooped, deep hood and damp-proof wool shawl,
layered dark teal and muted violet robes, rune staff with faintly glowing violet crystal,
leather satchel of notes — signature color: muted violet
```

**韩鸦（猎人）**
```
male bounty hunter, 30s, lean hard-bitten, predatory squint, scarred crooked nose,
five o'clock stubble, wide-brim battered leather hat, worn brown leather jacket,
double-barrel shotgun slung across back, coil of wire rope and hunting traps,
fingerless gloves — signature color: rust brown
```

**温砚（医师）**
```
male field physician, late 30s, calm exhausted eyes, straight blunt nose, tidy short
hair, practical stoop from years of triage, short white canvas cape, grey field uniform,
worn medical satchel, standard-issue pistol, hand-held glowing oil lantern —
signature color: bone white with olive grey
```

**邱铸（工程师）**
```
male demolition engineer, 40s, stocky and broad, soot-smudged face, broken flat nose,
one partly deaf ear with a small ear trumpet, blunt pragmatic stare, heavy canvas work
jacket, leather tool belt, welding mask pushed onto forehead, bulky breathing apparatus
backpack, nail gun at hip, crude round mine — signature color: industrial teal with rust orange
```

---

## 七、一句话速查

> **耻辱式阴郁绘画感 + 风格化半写实中等面数 + 夸张性格脸与可读剪影 + 维多利亚北极厚重装束 + 职业色编码 + 冷调雪原与暖灯火对比。**
