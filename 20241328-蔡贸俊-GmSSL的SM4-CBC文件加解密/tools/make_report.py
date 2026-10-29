from pathlib import Path
import re

root = Path(__file__).resolve().parent.parent
name = root.name
log = (root / 'logs/practice.txt').read_text(encoding='utf-8')
key = re.search(r'^key = (\w+)', log, re.M)[1]
iv = re.search(r'^iv = (\w+)', log, re.M)[1]
source = (root / 'src/sm4_file.c').read_text(encoding='utf-8')
ids = (root / 'sn.txt').read_text(encoding='ascii')
cross = (root / 'logs/cross-check.txt').read_text(encoding='utf-8')
ai = '''# AI 问答过程（本次真实交流节录）

工具：OpenCode；模型：openai/gpt-6.1-sol。以下摘录真实用户要求与助手反馈，工具执行结果另见 practice.txt；没有将 AI 生成的提问冒充用户发言。

## 用户要求

> 帮我完成课堂测试，学习以前解决问题的方法

用户随后给出任务：在 Ubuntu 或 openEuler 中创建全班八位学号的 sn.txt，把本人学号放到最后；使用 GmSSL 编程生成随机密钥和 IV，以 CBC 模式对文件加解密，得到 sn2.txt；用 Linux diff 验证；记录实践与 AI 问答过程，提交按“学号-姓名-作业题目”命名的 Markdown 与 PDF。

## 助手第一次反馈（原文）

我会先查找以前的 GmSSL 实验和现有 Linux 环境，复用已验证的方法，再保存本次真实编译、运行和 `diff` 记录，生成 Markdown 与 PDF。全班学号会优先从已有材料中查找，避免自行假定名单。

## 助手查阅旧材料后的反馈（原文）

已找到以前的 openEuler 24.03 环境、GmSSL 库编程记录，以及上次使用的 29 人学号文件（20241301—20241329，20241328 已排在最后）。本次会沿用已验证的 `SM4_CBC_CTX` 接口和链接参数，将字符串加解密改为文件加解密，并分别随机生成密钥与 IV。

## 助手完成运行后的反馈（原文）

C 程序已在 openEuler 中编译运行成功：261 字节的学号文件加密为 272 字节，解密后恢复为 261 字节，Linux `diff` 返回 0。额外用 GmSSL 命令行交叉验证时，发现需要显式加上 `-pkcs7_padding` 才会去除填充；补上后也通过了比对。报告会记录这个实际排错过程。

## 用户补充要求（原文）

需要补充运行结果的截图

## 助手对补充要求的反馈（原文）

我会补充真实终端窗口截图，展示编译、运行和 `diff` 验证结果，并更新 Markdown 与 PDF。补充运行会使用单独目录，截图中也会注明这是一次新的运行。

## AI 参与范围

AI 查阅旧实验资料、编写本次 C 程序和辅助脚本、通过工具实际执行编译与验证，并依据日志整理报告。完整源码和运行文本均随作业附上；报告不将 AI 操作描述为学生独立操作经历。
'''
(root / 'logs/AI问答记录.md').write_text(ai, encoding='utf-8')
ai_summary = '''# AI 使用记录

工具：OpenCode（模型：openai/gpt-6.1-sol）。本记录按本次实际交流和执行过程整理，为内容摘要。

1. **提出任务**：提供课堂测试要求，请 AI 参考以前解决类似问题的方法，协助完成 GmSSL 文件加解密实验及提交材料。
2. **参考旧实验**：AI 检查已有 openEuler 环境，找到之前使用的 29 人学号文件和 GmSSL 库编程记录，建议沿用 SM4_CBC_CTX 的 init/update/finish 流程。
3. **实现与解释**：AI 协助编写 C 程序，解释两次 rand_bytes 调用、16 字节密钥与 IV、文件分块读写及 PKCS#7 填充，并通过工具执行编译和运行。
4. **验证与排错**：执行 Linux diff 和 SHA-256 比较。额外进行 CLI 解密时出现填充未去除的问题，AI 对照旧命令补充 -pkcs7_padding，重新验证通过。
5. **整理材料**：AI 根据实际日志整理报告。补充提出运行截图要求后，AI 通过工具再次运行相同源码、采集终端窗口截图，并更新 Markdown 与 PDF。

本次 AI 辅助范围包含代码编写与解释、工具执行、排错和文档整理；运行证据保存在随附日志与截图中。

说明：本 AI 使用记录由 AI 根据实际交流与运行记录生成。
'''
(root / 'logs/AI使用记录.md').write_text(ai_summary, encoding='utf-8')
report = f'''# GmSSL 的 SM4-CBC 文件加解密课堂测试

**姓名：蔡贸俊　学号：20241328　班级：2413**  
**实验日期：2026 年 10 月 26 日**

## 一、实验目的与完成情况

本次实验通过一个学号文本文件，练习 GmSSL 随机数接口和 SM4-CBC 加解密接口的使用。实验重点是把“随机生成密钥和 IV—加密文件—解密文件—比较结果”连成完整流程，并用实际命令验证文件是否恢复一致。

| 要求 | 本次实现与证据 | 结果 |
| --- | --- | --- |
| 在 Ubuntu 或 openEuler 中完成 | WSL2 中的 openEuler 24.03 LTS | 已完成 |
| 全班八位学号，本人排最后 | sn.txt，复用上次课堂文件，29 条无重复 | 已完成 |
| GmSSL 编程生成随机密钥与 IV（4 分） | 两次 rand_bytes，各生成 16 字节 | 已完成 |
| CBC 文件加密解密及代码、编译运行过程（8 分） | C 程序调用 SM4-CBC 流式接口，输出 sn.enc 和 sn2.txt | 已完成 |
| Linux diff 验证（2 分） | diff sn.txt sn2.txt，退出码 0 | 已通过 |
| 实践及 AI 问答文本、Markdown 与 PDF | 本报告、logs 中的文本与对话节录 | 已整理 |

## 二、实验思路与旧方法的应用

本次采用“先参考旧实验，再修改为文件处理，最后验证结果”的思路。以前的示例已经验证过 GmSSL 的基本调用方式，因此本次主要解决输入文件、随机 IV、分块读写和结果比较这几个问题。

1. **复用环境**：此前已安装 openEuler 和 GmSSL，不重复安装。
2. **准备学号文件**：将以前课堂使用的 `/root/hash_hw/sn.txt` 复制到本次目录。文件包含 20241301—20241329 共 29 个学号，本人学号 20241328 放到最后，再检查格式与重复情况。
3. **复用 API 方法**：查阅旧项目 `/root/roc-edu-student-exp_1/docs/hours4-6.md` 中“GmSSL 库编程实践”，沿用 `SM4_CBC_CTX` 与 `init/update/finish` 流程，将原来的字符串处理改成文件分块读写。
4. **复用链接经验**：显式设置头文件路径、库路径和运行时搜索路径，使用 `-lgmssl` 链接 GmSSL。
5. **先验证再总结**：保留命令、真实输出与退出码；遇到 CLI 填充参数差异时查明原因并重跑。

## 三、实验环境与输入

实际环境为 **openEuler 24.03 LTS（WSL2，x86_64）**，编译器为 **GCC 12.3.1**，密码库为 **GmSSL 3.3.0-dev.1183**。程序为 Linux ELF 64 位可执行文件。

`sn.txt` 每行一个八位学号，采用 LF 换行，无 BOM，最后一行也有换行。共 29 行，每行 8 个数字加 1 个换行，因此为 29 × 9 = **261 字节**。程序运行前已校验数量、格式、唯一性及最后一行。

```text
{ids.rstrip()}
```

名单来源与 SHA-256 记录见 [logs/input-source.txt](logs/input-source.txt)。

## 四、原理与程序设计

### 1. 随机密钥与 IV

SM4 密钥长度为 128 位，分组长度为 128 位，因此 key 与 CBC 的 IV 均为 **16 字节**。使用 GmSSL 的 `rand_bytes` 分别生成两组随机字节，检查返回值为 1，不采用固定常量或 C 标准库 `rand()`。

```c
uint8_t key[16], iv[16];
if (rand_bytes(key, sizeof(key)) != 1 ||
    rand_bytes(iv, sizeof(iv)) != 1) {{
    fprintf(stderr, "GmSSL rand_bytes failed\\n");
    return 1;
}}
```

本次最终运行生成的值如下（32 个十六进制字符对应 16 字节）：

```text
key = {key}
iv = {iv}
```

程序将这组实验值分别写入 `key.bin`、`iv.bin`，便于使用命令行交叉验证。重新运行会生成新的随机值并覆盖本次运行产物。

### 2. SM4-CBC 与填充

CBC 加密满足 `C_i = E_K(P_i XOR C_(i-1))`，首块以前一个分组为 IV；解密满足 `P_i = D_K(C_i) XOR C_(i-1)`。解密必须使用与加密相同的密钥和**初始 IV**，因此每次操作分别初始化新的上下文。

程序以二进制方式读写文件，用 `update` 分块处理，并调用 `finish` 完成 PKCS#7 填充或去填充。261 除以 16 余 5，需要补 11 个 `0x0b`，所以密文为 **272 字节**；解密去填充后恢复 261 字节。

文件流程为：`sn.txt → SM4-CBC 加密 → sn.enc → SM4-CBC 解密 → sn2.txt`。

### 3. 代码各部分的作用

- `main`：生成随机密钥和 IV，保存实验参数，依次调用加密与解密函数。
- `crypt_file`：打开输入输出文件，初始化 CBC 上下文，循环读写数据，最后处理填充并关闭文件。
- `save_bytes`：将本次生成的 key 和 IV 各保存为 16 字节二进制文件。
- `print_hex`：把随机值输出为十六进制，便于查看和使用命令行复核。

加密和解密使用同一个文件处理函数，通过 `encrypt` 参数选择对应接口。这样能够减少重复代码，也便于对照两种操作的共同点和差别。

## 五、编译与运行过程

以下为最终运行文本摘录。所有命令均在本次成果目录下的 openEuler 中执行，完整日志见 [logs/practice.txt](logs/practice.txt)。`[exit code: ...]` 为采集脚本记录的真实退出码。

```bash
gcc -std=c11 -Wall -Wextra -O2 -I/usr/local/include \\
    src/sm4_file.c -L/usr/local/lib -Wl,-rpath,/usr/local/lib \\
    -lgmssl -o sm4_file
./sm4_file
```

编译无警告、退出码为 0；运行输出：

```text
key = {key}
iv = {iv}
encrypt: sn.txt (261 bytes) -> sn.enc (272 bytes)
decrypt: sn.enc (272 bytes) -> sn2.txt (261 bytes)
[exit code: 0]
```

各参数含义：`-I` 指定头文件目录，`-L` 指定链接库目录，`-Wl,-rpath` 指定运行时库搜索路径，`-lgmssl` 链接 GmSSL 库。`-Wall -Wextra` 开启编译警告。

```text
$ wc -c sn.txt sn.enc sn2.txt key.bin iv.bin
261 sn.txt
272 sn.enc
261 sn2.txt
 16 key.bin
 16 iv.bin
826 total
[exit code: 0]
```

## 六、Linux diff 正确性验证

```text
$ diff sn.txt sn2.txt
[exit code: 0]

$ sha256sum sn.txt sn2.txt
3e6ae0ce6045401bc073e36c4442f0de3d44cb6f6414ef0d339a5bac386ac012  sn.txt
3e6ae0ce6045401bc073e36c4442f0de3d44cb6f6414ef0d339a5bac386ac012  sn2.txt
[exit code: 0]
```

`diff` 没有差异输出且返回 0，说明本次明文文件和解密文件完全相同；两个文件的 SHA-256 也一致。返回 1 表示内容有差异，返回 2 通常表示执行错误，不能只看是否有文字输出。

另外，使用 GmSSL CLI 对 C 程序产生的密文解密，再与原文比较：

```text
{cross.rstrip()}
```

### 运行结果截图

以下截图展示在 Windows Terminal 中调用 WSL/openEuler 完成的一次补充运行，展示版裁去了外围空白。该次运行使用相同源码，数据和日志保存在 `logs/screenshot-run/`。由于每次运行都会重新生成随机数，截图中的 key 和 IV 与前面的文本记录不同，但文件长度和 diff 验证结果相同。

**图 1　环境、编译、随机密钥与 IV，以及 CBC 加解密结果。** 编译与运行均返回 0，文件长度仍为 261→272→261 字节。完整文字见 [补充运行日志](logs/screenshot-run/phase1.txt)。

![图1：openEuler 中编译与 CBC 加解密真实窗口截图](images/01-编译与加解密-裁剪.png)

**图 2　Linux diff 与学号顺序验证。** `diff sn.txt sn2.txt` 无差异且返回 0，两个 SHA-256 一致，最后一行是本人学号 20241328。完整文字见 [补充验证日志](logs/screenshot-run/phase2.txt)。

![图2：Linux diff 与学号顺序真实窗口截图](images/02-diff正确性验证-裁剪.png)

## 七、实际问题与解决

程序内部加解密和 `diff` 首次即通过。额外进行 CLI 解密时，最初未指定 `-pkcs7_padding`，CLI 虽返回 0，但输出末尾多出 11 个 `0x0b`，`diff` 返回 1。这恰好与 261 字节明文所需的填充长度一致。

对照旧实验中使用的命令，补上 `-pkcs7_padding`，重新执行，CLI 解密结果与 `sn.txt` 一致，退出码为 0。首次失败的命令及控制字符可读表示保存在 [logs/initial-cross-check.txt](logs/initial-cross-check.txt)，最终交叉验证原始文本见 [logs/cross-check.txt](logs/cross-check.txt)。

本次经验是：库接口与命令行默认选项可能不同，要同时检查退出码与文件内容，并核对模式、填充、密钥和 IV。

## 八、AI 使用记录

本次使用 OpenCode（模型 `openai/gpt-6.1-sol`）辅助完成实验。最初提供课堂测试要求，并提出参考以前解决问题的方法；随后补充运行截图和报告修改要求。AI 的使用过程整理如下：

1. **查阅方法**：检查已有 openEuler 和 GmSSL 环境，参考之前的学号文件与库编程示例，确定使用 SM4-CBC 流式接口。
2. **编写和解释程序**：协助编写文件加解密代码，说明 `rand_bytes`、CBC 初始化、分块处理和填充的作用。
3. **运行与排错**：AI 通过工具执行编译、加解密和 `diff` 验证；根据 CLI 解密末尾多出的填充字节，补充 `-pkcs7_padding` 参数并复核结果。
4. **整理提交材料**：根据实际日志整理实践过程，通过工具采集补充运行截图，并生成 Markdown 和 PDF。

本节为实际交流和辅助过程的摘要，详细内容见 [AI 使用记录](logs/AI使用记录.md)，对话节录见 [AI 问答记录](logs/AI问答记录.md)。

## 九、实验总结

已在 openEuler 中完成 GmSSL 随机密钥与 IV 生成、SM4-CBC 文件加密和解密，并使用 Linux `diff` 确认 `sn.txt` 与 `sn2.txt` 一致。主目录数据对应首次交付时的最终运行日志；截图对应单独保存的补充运行，两次均验证通过。

从本次结果可以归纳出三点：第一，文件加解密不仅要选择正确的算法，还要保持密钥、初始 IV 和填充方式一致；第二，密文比明文长是分组填充的正常结果，本次增加的 11 字节与 PKCS#7 计算相符；第三，程序返回成功并不直接等于明文正确，仍需用 `diff` 检查实际内容。

本次实验验证的是文件加解密后的内容一致性；`diff` 和 SHA-256 在这里用于结果核对，并不意味着 CBC 本身提供了消息完整性校验。

## 十、提交附件与参考依据

- [完整 C 源码](src/sm4_file.c)：核心实验程序；下附全文，报告可独立阅读。
- [run.sh](run.sh)：在已安装 GmSSL 的 Linux 中执行 `bash run.sh`，完成编译、运行与 diff。
- [输入文件](sn.txt)、[密文文件](sn.enc)、[解密文件](sn2.txt)。
- [实践日志](logs/practice.txt)、[交叉验证日志](logs/cross-check.txt)、[AI 问答记录](logs/AI问答记录.md)。

参考依据：本次课堂题目；此前实际读取的 `hours4-6.md`；本机安装的 `gmssl/rand.h` 与 `gmssl/sm4.h`。旧材料用于借鉴方法，本次运行数值均来自新日志。

## 附录：完整 C 程序

```c
{source.rstrip()}
```

---

**AI 生成说明：本报告正文及 AI 使用记录由 AI 根据本次实际交流、源码、运行日志和截图生成；代码编写、工具执行、排错和文档整理均包含 AI 辅助。**
'''
(root / f'{name}.md').write_text(report, encoding='utf-8')
(root / 'INDEX_提交清单.md').write_text(f'''# 提交清单

姓名：蔡贸俊；学号：20241328。

## 必交

- `{name}.md`
- `{name}.pdf`：含运行截图的最新提交版。
- `src/sm4_file.c`：建议与两份报告一并提交；报告附录也包含全文。

## 运行证据与数据

- `sn.txt`：以前课堂文件的原样副本，29 个学号，本人最后。
- `sn.enc`：SM4-CBC / PKCS#7 密文，272 字节。
- `sn2.txt`：解密明文，261 字节，与 sn.txt 的 Linux diff 返回 0。
- `key.bin`、`iv.bin`：本次实验生成的各 16 字节随机值。
- `logs/practice.txt`：环境、编译、运行、diff、SHA-256 的真实记录。
- `logs/cross-check.txt`、`logs/sn_cli.txt`：CLI 交叉验证记录及输出。
- `logs/initial-cross-check.txt`：首次 CLI 填充选项问题记录（控制字符已注明可读表示）。
- `logs/AI问答记录.md`：本次真实对话节录。
- `logs/AI使用记录.md`：按实际辅助过程整理的 AI 使用摘要，文末注明由 AI 生成。
- `logs/input-source.txt`：学号文件来源及摘要。
- `images/`：两张原始终端窗口截图及用于报告的裁剪展示版。
- `logs/screenshot-run/`：截图对应的补充运行源码、数据、随机值及两份文本记录。

## 复现

在安装了相同 GmSSL 的 openEuler 中进入本目录，执行：

```bash
bash run.sh
```

重新运行会更换随机密钥、IV 和密文；报告中的数值对应交付时的那次运行。
`tools/execute.py` 用于采集原环境日志，依赖原环境的 `/root/hash_hw/sn.txt`；常规复现使用现有 sn.txt 和 run.sh。
`tools/make_report.py` 根据 logs 和源码生成 Markdown；PDF 使用本机 Markdown 转 PDF 工具生成。
''', encoding='utf-8')
print(root / f'{name}.md')
