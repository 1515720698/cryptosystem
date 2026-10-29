# 实验二1—3学时提交清单

姓名：蔡贸俊　学号：20241328　班级：2413

## 主要文件

- [实践记录（Markdown）](20241328_蔡贸俊_实验二_1-3学时_实践记录.md)
- [实践记录（PDF）](20241328_蔡贸俊_实验二_1-3学时_实践记录.pdf)
- [本阶段要求](materials/本阶段要求.md)
- [完整运行日志](logs/verification.log)、[本次编译日志](logs/build.log)、[结构化验证结果](logs/results.json)
- [实际终端截图](images/实际终端验证截图.png)
- [源码来源与适配说明](src/SOURCES.md)
- [本次Git提交记录](logs/git_log.txt)、[课程仓库与归档提交信息](logs/repository_metadata.json)
- `src/`：SM2、SM3、SM4的C实现、实验入口、Makefile及MIRACL所需源码。
- `data/`：测试原文、参考密文、二进制摘要及本次实测输出；含公开的测试密钥夹具。
- `materials/`：检测中心原始源码包/PDF、原指导书、真实标准查询记录及标准文本。

## 运行方法

现有Windows电脑已安装openEuler、GCC、make、Python3和GmSSL。在本文件夹打开PowerShell，运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\运行实验.ps1
```

在openEuler终端进入本目录，也可执行：

```bash
python3 tools/verify_linux.py
```

脚本编译参考代码，生成测试数据，并调用GmSSL逐字节比对，预期最后显示 `ALL 36 CHECKS PASSED`。手动编译入口为 `make -C src -j4`。程序文件是Linux ELF，需要在openEuler运行。

## 本次技术内容

1. 检测中心SM2公钥加解密、SM3、SM4原自检。
2. SM3的11组输入边界及GmSSL比较。
3. SM4的标准向量、8组加密比对和反向解密、非法分组长度拒绝。
4. SM2与GmSSL双向互操作、随机加密3次、C3篡改和过短密文拒绝。
5. 密标委SM2、SM3、SM4标准检索与函数对应分析。

源码从最终交付目录实际构建与验证；验证日期以 `logs/results.json` 为准。重新运行会更新随机密文与计时；报告引用本次结果。

## 提交手续及选做项

- **课程仓库**：https://github.com/1515720698/cryptosystem ，分支 `master`，本次材料放在同名实验目录下。
- **本次Git记录**：已按SM3、SM4、SM2与验证工具分组创建三个真实归档提交，并另行提交实践文档；原始输出见 `logs/git_log.txt`。这些是已有实验完成后的本次归档记录，没有回填早期开发日期。最终文档提交可在仓库提交历史中查看。
- **Rust三算法：选做，未实施。**
- 实践记录的个人心得为AI代拟，提交前请本人核对。

本目录提供本阶段实践所需Markdown和PDF。压缩包为 `20241328_蔡贸俊_实验二_1-3学时_提交材料.zip`，放在本目录内，打包时排除压缩包本身和编译中间件。

公开包不含运行时生成的测试私钥PEM；`test_key.c`会在复现时生成公开d=1的实验夹具。认证凭据不属于提交材料。
