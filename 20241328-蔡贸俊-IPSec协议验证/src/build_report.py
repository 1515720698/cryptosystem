"""依据实际日志生成提交报告，不在此脚本中生成实验结果。"""
from pathlib import Path
import json,textwrap,hashlib,platform
R=Path(__file__).resolve().parents[1]
V=json.loads((R/'data/vectors.json').read_text(encoding='utf8'))
J=json.loads((R/'logs/openssl-results.json').read_text(encoding='utf8'))
O=J['results']; G=json.loads((R/'logs/attachment-tool-results.json').read_text(encoding='utf8'))
assert len(G)==20 and all(x['pass'] for x in G)
assert O['check_count']==26 and O['pass_count']==26
def code(s,lang='text'):return '\n```'+lang+'\n'+s.strip()+'\n```\n'
def hexs(s):return code('\n'.join(textwrap.wrap(s,64)))
def val(k):return hexs(O[k])
def fig(name,caption):return f'\n![{caption}](images/{name}.png)\n\n*{caption}（本次附件工具窗口原始截图）*\n'
report=f'''# IPSec协议验证实验报告

**课程：信息安全系统设计**  
**学号：20241328　姓名：蔡贸俊　班级：2413**

## 一、实验任务与验证思路

本次作业包括两部分：第一部分使用课程附件中的密码协议验证工具复核 IPSec 协议数据；第二部分使用 OpenSSL 命令独立完成同一组数据的验证。我按“解密关键数据 → 验证双方签名 → 派生工作密钥 → 校验主模式 HASH → 解密快速模式并验证完整性”的顺序进行实验。

### 1.1 材料检查

- 附件为 `密码协议验证工具-rocedu (1).zip`，解压后包含 `Fdog-Base.exe` 及其运行库，界面显示版本 **V1.0.5**。
- 题目给出的在线链接实际显示《（美化）ch03 密码技术-10--密码协议验证IPSec-2.pptx》，共 **61 页**。我逐页读取了其中的文字和关键页面，依据第 9—59 页给出的样例值开展运算复核。
- 本地附件未包含课件提到的 `left.pcapng`、`left_enc.key` 和 `right_enc.key`。因此本报告的密文、签名、公钥及私钥数值来自课件；没有将课件里的 Wireshark 截图作为自己的抓包结果。
- 课件已提供双方签名原文、签名值、公钥、派生公式及快速模式前两包密文，可以完成本报告的密码运算验证。视频未读取，不作为本报告的事实依据。

### 1.2 任务与证据对应

| 作业内容 | 本次操作 | 实际证据 |
|---|---|---|
| 使用附件工具验证（79 分项） | SM2 解密及双方验签，SM3/HMAC 派生，SM4-CBC 解密和 HASH 复核 | 20 项工具运算记录、20 张对应窗口截图 |
| 使用 OpenSSL 验证（20 分加分项） | 用 `pkeyutl`、`dgst`、`enc` 独立重算，并执行篡改对照 | 26 项检查通过，完整命令、退出码、二进制输入输出 |
| 提交验证过程 | 记录输入来源、步骤、结果、对比与结论 | 本 Markdown 及由其转换的 PDF |

## 二、实验环境与基本原理

### 2.1 实际环境

| 项目 | 配置 |
|---|---|
| 操作系统 | Windows 10，10.0.19045，AMD64 |
| 附件工具 | Fdog-Base / Fdog-Kit-Zookeeper，V1.0.5（同一运行窗口可能显示不同标题） |
| 命令行密码工具 | {O['openssl_version']} |
| OpenSSL 程序路径 | `C:\\Program Files\\Git\\usr\\bin\\openssl.exe` |
| 辅助脚本 | Python 3.12.10，用于十六进制转字节、ASN.1 编码、调用命令及整理输出 |
| 密码算法 | SM2、SM3、HMAC-SM3、SM4-CBC |

OpenSSL 部分没有调用附件工具或其 DLL；密码运算均由独立的 OpenSSL 可执行程序完成。Python 没有重新实现 SM2、SM3、HMAC 或 SM4。

### 2.2 两个阶段及符号

课件采用国密 IPSec VPN 的两阶段协商示例：第一阶段主模式用于身份鉴别与工作密钥协商，建立 ISAKMP SA；第二阶段快速模式在第一阶段密钥保护下协商 IPSec SA。它与通用 IKEv2 的消息流程不同，本次按课件给定公式验证。

- `i` 表示发起方，`r` 表示响应方；`Ni`、`Nr` 是第一阶段 Nonce。
- `SKi`、`SKr` 是课件样例中的密钥材料，不能和最终 ESP 会话密钥混同。
- `CKY-I`、`CKY-R` 分别为 8 字节 Cookie；`MsgID` 为 4 字节消息标识。
- `X || Y` 表示**字节串拼接**，不是把十六进制文本当 ASCII 字符计算。
- `载荷_b` 表示去掉 4 字节 ISAKMP 通用载荷头后的主体。ID 主体中身份类型、协议和端口字段仍需保留。
- 本例 `HASH = SM3`，`PRF(K,M) = HMAC-SM3(K,M)`。附件工具应使用“杂凑计算 → SM3-HMAC”，不能将另一个面向 `P_hash` 的“PRF计算”页面直接套用到本例。

## 三、使用附件工具完成验证

### 3.1 准备输入与 SM2 密文格式

我解压附件并启动 `Fdog-Base.exe`。工具主要提供密码运算页面，因此把课件中的载荷数据按其对应算法逐项输入。

第一阶段发起方私钥（课件第 9 页）：
{hexs(V['prv_i'])}
课件第 12 页的 SKi 密文由 ASN.1 的 `X、Y、Hash、C` 四部分组成。工具的 C1C3C2 输入采用 `X || Y || C3 || C2`，先去掉 ASN.1 标签和长度；坐标按 32 字节表示，ASN.1 INTEGER 的符号补零不属于坐标。原始拼接值为：
{hexs(V['ski_cipher_raw'])}

### 3.2 解密 SKi

1. 进入“SM2算法 → SM2加密解密”。
2. KEY 输入上面的 32 字节私钥。
3. 数据输入上面的密文，选择 **C1C3C2**，点击“解密”。

工具输出：
{val('ski_decrypted')}
结果与课件第 13 页的 `SKi` 一致，长度为 16 字节。
{fig('ski_decrypted','图1　SM2 解密得到 SKi')}

### 3.3 解密 Ni 与 IDi

进入“SM4算法 → SM4加密解密”，输入编码选 Hex，模式选 CBC，填充选 **NO_PADDING**，先保留所有解密字节，再依据协议字段长度区分主体和尾部填充。

**（1）Ni：**密钥为 `SKi`，IV 为 16 字节零，密文来自第 14 页：
{hexs(V['ni_cipher'])}
完整解密结果：
{val('ni_decrypted')}
按课件取前 16 字节作为 Ni：`{V['ni']}`；后 16 字节为 `00 × 15 || 0f`，保留在原始记录中。不能把该尾部当成 PKCS7 的 16 个 `10`。

**（2）IDi：**仍使用 `SKi`，IV 改为 **Ni 密文的最后一个分组**：`{V['ni_cipher'][-32:]}`。输入第 16 页的 96 字节密文：
{hexs(V['idi_cipher'])}
解密后取前 80 字节作为 IDi 主体：
{hexs(V['idi'])}
前四字节 `09000000` 仍属于 ID 主体；后续为身份标识内容，末尾可读字符串为 `client sign`。余下 16 字节为 `00 × 15 || 0f`，不参加签名原文拼接。

### 3.4 验证双方 SM2 签名

发起方的签名原文为：
{code('Mi = SKi || Ni || IDi_b || CERT_enc_i')}
其中证书载荷主体 `CERT_enc_i` 为 **1 字节证书编码 05 + DER 证书**，保留 `05`，不加入其 4 字节通用载荷头。Mi 总长 **610 字节**。响应方按同样方法拼接 `Mr = SKr || Nr || IDr_b || CERT_enc_r`，总长 **608 字节**。

操作如下：

1. 打开“SM2签名验签”，公钥输入 `04 || X || Y`，不是证书的完整编码。
2. 输入对应的完整签名原文，编码选 Hex。
3. 签名的原始值是 `r || s`，各 32 字节；转换为 `SEQUENCE(INTEGER r, INTEGER s)` 后输入签名框。工具也提供“RS→ASN1”转换按钮。
4. 勾选 UserID，使用十六进制 `31323334353637383132333435363738`，对应字符串 `1234567812345678`。
5. 不勾选“基于 e 值验签”，点击“验签”。

| 项目 | 发起方 | 响应方 |
|---|---|---|
| 签名公钥长度 | 65 字节（含 04） | 65 字节（含 04） |
| 原始签名长度 | 64 字节 | 64 字节 |
| 签名原文长度 | 610 字节 | 608 字节 |
| 工具实际结果 | 验签成功！ | 验签成功！ |

完整公钥、原始签名及 Mi、Mr 见附录 A，所有字节也保存在 `data/vectors.json` 中。
{fig('signature_i','图2　发起方签名验证成功')}
{fig('signature_r','图3　响应方签名验证成功')}
这表明课件给出的两条签名与相应公钥、UserID 及消息内容相匹配。本步骤没有验证 CA 信任链和证书撤销状态。

### 3.5 派生第一阶段工作密钥

我在“杂凑计算”中选择 Hex。普通摘要选择 SM3；PRF 选择 **SM3-HMAC**，KEY 填密钥，输入框填消息。

基础输入为：
{code('Ni = '+V['ni']+'\nNr = '+V['nr']+'\nCKY-I = '+V['cookies'][:16]+'\nCKY-R = '+V['cookies'][16:])}
按课件第 28 页顺序计算：
{code('H = SM3(Ni || Nr)\nSKEYID   = HMAC-SM3(H, CKY-I || CKY-R)\nSKEYID_d = HMAC-SM3(SKEYID, CKY-I || CKY-R || 00)\nSKEYID_a = HMAC-SM3(SKEYID, SKEYID_d || CKY-I || CKY-R || 01)\nE_full   = HMAC-SM3(SKEYID, SKEYID_a || CKY-I || CKY-R || 02)')}
末尾 `00、01、02` 各是**一个字节**，不是字符“0”“1”“2”。本次输出如下：
'''
for label,k in [('H','nonce_hash'),('SKEYID','skeyid'),('SKEYID_d','skeyid_d'),('SKEYID_a','skeyid_a'),('E_full','skeyid_e_full')]:report+=f'\n**{label}：**\n'+val(k)
report+=f'''
SM4 密钥只取 E_full 的前 16 字节：`{O['skeyid_e_full'][:32]}`。虽然课件第 34 页还展示了派生结果后半段，但消息 5、6 的实际 IV 按第 36 页的 `SM3(SKi || SKr)` 另算，不能直接用 E_full 的后 16 字节代替。
{fig('skeyid_e_full','图4　使用 SM3-HMAC 计算 E_full')}

### 3.6 解密并独立重算 HASHi、HASHr

先计算 `SM3(SKi || SKr)`，结果为：
{val('main_iv_hash')}
取前 16 字节 `de788aa1e41303baf97136e86f82f2fc` 作为 HASHi 加密载荷的 IV；解密 HASHr 时，IV 为 HASHi 密文的最后 16 字节 `b958be5fa74277fc91b3bfd3d1cbf7e0`。均使用 SM4-CBC、前述 16 字节密钥、NO_PADDING。

解密后，两条载荷均为 **4 字节通用头 + 32 字节 HASH + 12 字节零填充**：
{code('HASHi 载荷头：00 00 00 24\nHASHr 载荷头：00 00 00 24\n0x0024 = 36 = 4 + 32')}
因此不能直接把完整 48 字节明文与 32 字节 HMAC 输出比较。

再按下式独立重算：
{code('HASHi = HMAC-SM3(SKEYID, CKY-I || CKY-R || SAi_b || IDi_b)\nHASHr = HMAC-SM3(SKEYID, CKY-R || CKY-I || SAr_b || IDr_b)')}
本例 SAi_b 与 SAr_b 相同，都是 48 字节：
{hexs(V['sa'])}
得到：

**HASHi：**
{val('hashi')}
**HASHr：**
{val('hashr')}
两者分别与解密载荷的 32 字节 HASH 主体完全一致，也与课件第 44、48 页一致。这一步把前面的密钥派生、Cookie 顺序、SA 和身份载荷联系起来，而不只是“成功解出一段数据”。

### 3.7 第二阶段快速模式解密

第一包 IV 按课件第 49—51 页计算：
{code('MsgID = cc2d2221\n第一阶段最后密文分组 = d92048953a172891b194012f8db5f7b0\nIV1 = SM3(第一阶段最后密文分组 || MsgID) 的前16字节')}
完整摘要为：
{val('quick_iv_hash')}
因此 `IV1 = 56e6dfc945499ae8aca47a6ca9cf2ada`。以同一个 SKEYID_e 的前 16 字节为密钥，解密快速模式第一包；第二包 IV 改为**第一包密文最后一组**：`359b204f92800504072e2994af771b88`。

两包密文均为 160 字节，解密结果均含 148 字节有效载荷和 12 字节零填充。第一包完整明文如下：
{val('qm1')}
{fig('qm1','图5　快速模式第一包 SM4-CBC 解密')}
我按 Next Payload 与 Length 逐个拆分，而不是仅根据可读字符串判断解密是否正确：

| 偏移（字节） | 当前载荷 | 长度（含通用头） | 下一载荷 |
|---|---|---|---|
| 0 | HASH | 36 | SA（1） |
| 36 | SA | 60 | Nonce（10） |
| 96 | Nonce | 20 | ID（5） |
| 116 | IDi | 16 | IDr（5） |
| 132 | IDr | 16 | 无（0） |
| 148 | 零填充 | 12 | — |

从两包明文可解析到：

| 字段 | 第一包 | 第二包 |
|---|---|---|
| 协议号 | 3，ESP | 3，ESP |
| SPI | `c515ecd5` | `c713ad06` |
| 变换标识 | `0x7f`，课件样例对应 SM4 | 同左 |
| 鉴别属性 | `80050014`，课件对应 HMAC-SM3 | 同左 |
| 封装模式 | `80040001`，隧道模式 | 同左 |
| 秒生存期 | `0x1734 = 5940` 秒 | 同左 |
| KB 生存期 | `0x00086470 = 550000` KB | 同左 |
| Nonce | `4fdbbce1785046b21f1eb00afbec31c4` | `106bcaa925dc5b6d994efc88369d6059` |
| IDi 子网 | `172.16.29.0/24` | 同左 |
| IDr 子网 | `172.16.28.0/24` | 同左 |

变换编号按课件历史样例解析，不将样例中的 `0x7f` 直接当成所有版本的标准编号。

### 3.8 快速模式完整性复核

进一步计算前两包 HASH，作为对“解密后结构合理”的补充验证：
{code('HASH(1) = HMAC-SM3(SKEYID_a, MsgID || M1_after_HASH)\nHASH(2) = HMAC-SM3(SKEYID_a, MsgID || Ni2_b || M2_after_HASH)')}
这里 `Ni2_b` 是第二阶段第一包中 16 字节的 Nonce，不能误用第一阶段 Ni；`M_after_HASH` 包含后续载荷各自的通用头，排除 HASH 载荷及尾部填充，本例为明文偏移 `[36,148)`。

**HASH(1)：**
{val('quick_hash1')}
**HASH(2)：**
{val('quick_hash2')}
两项均与解密包内的 HASH 一致。附件工具共完成 **20 项**运算，逐项输出与独立 OpenSSL 结果一致；完整输入、输出和判定保存在 `logs/attachment-tool-verification.txt`。

## 四、加分项目：使用 OpenSSL 命令独立验证

### 4.1 数据准备及复现入口

我另用 OpenSSL 对**同一组课件输入**进行验证。脚本 `src/verify_openssl.py` 只调用独立 OpenSSL 程序；即使附件工具未启动，仍可完成全部命令行检查。

本节命令均在实验目录运行。Windows PowerShell 可先指定程序位置：
{code('$ossl = "C:\\Program Files\\Git\\usr\\bin\\openssl.exe"\n& $ossl version','powershell')}
实际版本输出：
{code(O['openssl_version'])}
十六进制输入先转换成二进制文件，不能直接把十六进制文本文件传给 `dgst`。完整复现命令为：
{code('$env:OPENSSL_EXE = "C:\\Program Files\\Git\\usr\\bin\\openssl.exe"\npython .\\src\\verify_openssl.py','powershell')}
其中 `python` 指可用的 Python 3；本机实际用隔离的 Python 3.12.10 解释器执行。此脚本使用 Python 标准库，不依赖 GUI 自动化库或密码库。

### 4.2 转换格式并用 SM2 解密

OpenSSL 的 SM2 解密输入需要 ASN.1 DER，而附件工具接受裸 C1C3C2。因此脚本将同一份密文包装为：
{code('SEQUENCE {\n  INTEGER xCoordinate,\n  INTEGER yCoordinate,\n  OCTET STRING C3,\n  OCTET STRING C2\n}')}
脚本还将课件私钥标量包装为带 SM2 曲线 OID `1.2.156.10197.1.301` 的 ECPrivateKey，再由 `pkey` 转成 PEM。这里是**编码重建**，没有声称读取了缺失的原始 `.key` 文件。

手动复现命令：
{code('& $ossl pkey -inform DER -in data/enc_i.der -out data/enc_i.pem\n& $ossl pkeyutl -decrypt -inkey data/enc_i.pem -in data/ski.der -out data/ski.bin','powershell')}
本次输出字节的十六进制表示为 `{O['ski_decrypted']}`，与附件工具、课件均一致。

### 4.3 使用 SM4-CBC 解密

以 Ni 解密为例，手动等效命令为：
{code('& $ossl enc -d -sm4-cbc -K '+V['ski']+' `\n  -iv 00000000000000000000000000000000 -nopad `\n  -in data/ni_decrypted.enc -out data/ni-manual.bin','powershell')}
`-K` 和 `-iv` 接收十六进制参数，`-nopad` 禁止默认 PKCS7 去填充；它不是“不产生明文尾部”，而是让协议填充原样保留。结果与第三节的完整 Ni 明文逐字节一致。

IDi、HASHi、HASHr 和快速模式两包使用相同的 `enc -d -sm4-cbc -nopad` 方式，只按第三节替换输入、密钥和 IV。完整命令及输出见 `logs/openssl-verification.txt`。

### 4.4 使用 SM2 验证双方签名

脚本将 `04 || X || Y` 包装成 SubjectPublicKeyInfo DER，将 `r || s` 包装成 DER 签名。若 INTEGER 的最高位为 1，DER 编码需添加符号用 `00`；不能简单地把 64 字节原始签名直接交给 OpenSSL。

发起方命令：
{code('& $ossl pkeyutl -verify -pubin -keyform DER `\n  -inkey data/sig_i_pub.der -rawin -digest sm3 `\n  -pkeyopt distid:1234567812345678 `\n  -in data/signed_i.bin -sigfile data/sig_i.der','powershell')}
响应方命令：
{code('& $ossl pkeyutl -verify -pubin -keyform DER `\n  -inkey data/sig_r_pub.der -rawin -digest sm3 `\n  -pkeyopt distid:1234567812345678 `\n  -in data/signed_r.bin -sigfile data/sig_r.der','powershell')}
本次两条命令的实际输出均为：
{code('Signature Verified Successfully\nexit=0')}
其中 `-rawin -digest sm3` 表示输入的是待签消息原文；OpenSSL 按 SM2 规则结合 UserID 计算相关摘要。不能先对原文普通 SM3 一次，再把摘要当“原文”重复哈希。

### 4.5 使用 SM3 与 HMAC-SM3 派生密钥

普通 SM3：
{code('& $ossl dgst -sm3 -binary data/nonce_hash.bin','powershell')}
其二进制输出在日志中显示为：
{val('nonce_hash')}
计算 SKEYID 的命令：
{code('& $ossl dgst -sm3 -mac HMAC `\n  -macopt hexkey:'+O['nonce_hash']+' `\n  -binary data/skeyid.bin','powershell')}
此处 `data/skeyid.bin` 是 **Cookie 拼接的输入文件**，不是已经派生出的 SKEYID。计算结果保存为 `data/skeyid.sm3`。后续密钥和 HASH 使用同样命令形式：KEY 换成相应密钥值，输入文件换成按公式拼好的字节文件。

| 运算 | KEY | 输入文件（文件内容） | 与附件工具对比 |
|---|---|---|---|
| SKEYID | SM3(Ni\\|\\|Nr) | `skeyid.bin`（两 Cookie） | 相同 |
| SKEYID_d | SKEYID | `skeyid_d.bin`（两 Cookie\\|\\|00） | 相同 |
| SKEYID_a | SKEYID | `skeyid_a.bin`（d\\|\\|两 Cookie\\|\\|01） | 相同 |
| E_full | SKEYID | `skeyid_e_full.bin`（a\\|\\|两 Cookie\\|\\|02） | 相同 |
| HASHi、HASHr | SKEYID | `hashi.bin`、`hashr.bin` | 相同，且等于包内 HASH |
| HASH(1)、HASH(2) | SKEYID_a | `quick_hash1.bin`、`quick_hash2.bin` | 相同，且等于包内 HASH |

表内文件均位于 `data/`；输出在同名 `.sm3` 文件中。带 `-binary` 的命令输出是二进制，脚本将其以 HEX 记录，不通过 PowerShell 文本重定向保存二进制。

### 4.6 篡改对照验证

为检查验签是否真正依赖输入内容，我分别把 Mi、Mr 的**第一个字节异或 01**，其余输入保持不变，再执行原来的验签命令：

| 检查 | 原始数据 | 修改一字节后 |
|---|---|---|
| 发起方 SM2 验签 | 成功，退出码 0 | 失败，退出码 1 |
| 响应方 SM2 验签 | 成功，退出码 0 | 失败，退出码 1 |
| 快速模式 HASH(1) | 等于第一包 HASH | 修改覆盖内容最后一字节后不相等 |

篡改后的 SM2 实际输出为 `Signature Verification Failure`。快速模式篡改后重算 HASH(1) 为：
{val('quick_hash1_tampered')}
它与原始 `{O['quick_hash1']}` 不同。因此篡改会被签名或带密钥的摘要检出；单纯 CBC 解密本身不等同于完整性验证。

## 五、验证结果汇总

| 验证对象 | 附件工具 | OpenSSL / 解析结果 | 判断 |
|---|---|---|---|
| SKi | 解密为课件给定值 | 同值 | 一致 |
| Ni、IDi | 解密成功，保留尾部 | 逐字节一致 | 一致 |
| 发起方、响应方签名 | 均“验签成功！” | 两次退出码均为 0 | 一致 |
| SKEYID、d、a、e | 按 HMAC-SM3 顺序得到 | 独立命令重算同值 | 一致 |
| HASHi、HASHr | 解密值等于重算值 | 同时与课件值比较通过 | 一致 |
| 快速模式 IV | SM3 取前 16 字节 | 同值 | 一致 |
| 快速模式两包 | 解密得到载荷链 | 长度、Next Payload、零填充均正确 | 通过 |
| HASH(1)、HASH(2) | 与包内值相同 | 独立 HMAC 重算一致 | 通过 |
| 篡改消息 | — | 两次签名拒绝、一次 MAC 不匹配 | 符合预期 |

附件工具的 **20 项实际运算全部一致**；OpenSSL 脚本的 **26 项检查全部通过**。20 与 26 是各自脚本定义的运算项/检查项数量，不是额外的报文数量或评分承诺。

## 六、实验中遇到的问题与处理

### 6.1 默认 PKCS7 导致解密结果为空

最初附件工具使用默认填充时，SM4 解密没有得到预期结果。检查课件明文尾部后发现：Ni、IDi 尾部为 `00 × 15 || 0f`，主模式 HASH 和快速模式报文则包含零填充，不符合工具默认 PKCS7 的检查要求。我改为 **NO_PADDING**，并在 OpenSSL 中使用 `-nopad`，再次运行后六项 SM4 解密全部与独立结果一致。

处理原则是先保留原始解密字节，再按字段长度解释填充；不能为了让工具“去填充成功”而修改课件密文。

### 6.2 把裸 SM2 数据与 ASN.1 编码区分开

同样的密文和签名在两种工具中的输入格式不同。附件解密使用 C1C3C2，OpenSSL 解密使用 DER；签名的 `r||s` 需转换为两个 INTEGER 的 SEQUENCE。转换只改变外层编码，不改变密码学数值。

### 6.3 IV 和 HASH 输入范围不能混用

本次 IV 随阶段变化：Ni 用全零；IDi 用 Ni 的密文尾块；HASHi 用 `SM3(SKi||SKr)` 前 16 字节；HASHr 用 HASHi 密文尾块；快速模式第一包用“上一阶段密文尾块与 MsgID”的摘要，第二包用第一包密文尾块。只有按课件关系串联，才能同时满足解密和 MAC 校验。

第一阶段 `SA_b、ID_b` 去掉通用头；快速模式 `M_after_HASH` 保留后续载荷的通用头。两者的拼接范围不同，是本次复核中需要特别核对的地方。

## 七、实验结论

本次通过附件工具与 OpenSSL 两条路线，对课件样例完成了 SM2 解密、双方 SM2 签名、第一阶段工作密钥派生、HASHi/HASHr 以及第二阶段前两包的解密和完整性验证。不同工具的结果一致，篡改对照也能检出一字节修改，说明这组样例的密钥、消息与鉴别值之间具有一致的密码学关系。

本报告验证的是课件样例的密码运算和报文载荷关系。材料未提供原始 pcap、快速模式第三包和 ESP 业务数据，因此未宣称完成现场抓包、HASH(3) 核验、ESP 数据面测试或实际 VPN 隧道建立；证书链也未做完整信任验证。

## 八、参考资料

1. 娄嘉鹏，《信息安全系统设计：密码技术—密码协议验证IPSec》，云班课在线课件，共 61 页。重点使用第 9—59 页。题目提供的访问地址：[云班课课件](https://viewer.mosoteach.cn/viewer?token=620d79be4742bb6b4b30176fcd02010e&app_id=MTWEB&app_version=6.0.0&screenx=null&location=null)。
2. 课程附件 `密码协议验证工具-rocedu (1).zip`，本次实际运行 Fdog-Base V1.0.5。
3. OpenSSL 3.5 官方文档：[openssl-pkeyutl](https://docs.openssl.org/3.5/man1/openssl-pkeyutl/)，用于核对 SM2、`distid`、`rawin` 等参数。
4. OpenSSL 3.5 官方文档：[EVP_PKEY-SM2](https://docs.openssl.org/3.5/man7/EVP_PKEY-SM2/)，用于核对 SM2 UserID 与摘要机制。

## 附录 A：关键输入数据

以下数据均为课件样例的十六进制字节表示；换行仅用于排版，使用时拼接。完整密文和输出另见 `data/vectors.json`、`logs/openssl-results.json`。
'''
for title,key in [('发起方签名公钥（不含04）','pub_sig_i'),('发起方签名 r||s','sig_i'),('响应方签名公钥（不含04）','pub_sig_r'),('响应方签名 r||s','sig_r'),('发起方完整签名原文 Mi（610字节）','signed_i'),('响应方完整签名原文 Mr（608字节）','signed_r'),('HASHi 密文（48字节）','hashi_cipher'),('HASHr 密文（48字节）','hashr_cipher'),('快速模式第一包密文（160字节）','qm1_cipher'),('快速模式第二包密文（160字节）','qm2_cipher')]:report+=f'\n### {title}\n'+hexs(V[key])
report+='''
## 附录 B：实验文件与复现说明

| 文件或目录 | 用途 |
|---|---|
| `data/vectors.json` | 课件输入的原始十六进制数值 |
| `data/` 中 DER、PEM、BIN、ENC、PLAIN、SM3 文件 | OpenSSL 实际输入、输出和重编码数据 |
| `src/verify_openssl.py` | 独立执行所有命令行检查，只依赖 Python 标准库与 OpenSSL |
| `src/verify_attachment_gui.py` | 在已经打开的附件工具上填入数据、读取输出并保存截图 |
| `logs/openssl-verification.txt` | OpenSSL 完整命令、退出码、输出 |
| `logs/openssl-results.json` | 26 项检查及计算结果 |
| `logs/attachment-tool-verification.txt` | 20 项附件工具运算输入和输出 |
| `images/` | 每项工具运算对应的原始窗口截图 |
| `references/` | 在线课件读取记录及关键页面留存 |

复现 OpenSSL 部分时保留 `src/` 和 `data/` 的相对位置，设置 `OPENSSL_EXE` 后运行 `python src/verify_openssl.py`。复现 GUI 部分还需安装 pywinauto、Pillow，手动启动附件工具，展开杂凑算法、SM2算法、SM4算法菜单，再运行 `python src/verify_attachment_gui.py`。GUI 复核对照文件为本次独立 OpenSSL 结果。

'''
(R/'20241328-蔡贸俊-IPSec协议验证.md').write_text(report,encoding='utf8')
(R/'INDEX_提交清单.md').write_text('''# 提交清单

主要提交文件：

- `20241328-蔡贸俊-IPSec协议验证.md`
- `20241328-蔡贸俊-IPSec协议验证.pdf`

报告同时覆盖 79 分必做项与 20 分 OpenSSL 加分项；评分以教师评阅为准。

辅助材料保留在 `src/`、`data/`、`logs/`、`images/`、`references/`。直接阅读 PDF 即可查看正文及原始窗口截图。上传 Markdown 时保留其相对图片目录。

## 实际验证范围

已完成附件工具 20 项运算、OpenSSL 26 项检查。输入来自题目链接实际显示的 61 页 PPT。未获取原始抓包和原始私钥文件；未读取视频；未实施实际 VPN 网络隧道与 ESP 数据面验证。报告已准确说明这些边界。

## 最短复现

设置 OPENSSL_EXE 后，用可用 Python 3 执行：

```powershell
python src/verify_openssl.py
```
''',encoding='utf8')
print('Report generated',len(report),'characters')
