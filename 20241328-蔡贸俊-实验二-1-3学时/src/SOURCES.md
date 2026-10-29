# 源码来源与改动说明

- SM2_ENC.c/h：商用密码检测中心SM2加解密PDF，SM2_ENC_V1.1，2016-09-27。
- SM3.c/h：商用密码检测中心SM3 PDF，SM3_V1.1，2016-09-18。
- SM4.c/h：商用密码检测中心SM4 PDF，SM4_V1.0，2016-09-13。
- 上述参考代码作者：Mao Yingying、Huo Lili。原包、原PDF、免责声明、原始提取文本均在materials，保留其使用声明。本实验用于课程学习。
- kdf.h：保留官方SM3_KDF函数主体，移除其重复的unsigned long SM3，改用独立官方32位SM3。
- miracl/：来自https://github.com/miracl/MIRACL，提交b9b8fd471de253cfd6313446cb490741edb069a7。版权/许可见随附README.md和各源文件，构建采用amd64 LP64配置。
- main.c、test_key.c、Makefile及tools脚本：本次实验辅助入口，由OpenCode协助编写。

恢复脚本为了去除PDF换行影响，整理了原注释；算法作者、版本和完整注释以materials原件为准。额外改动包括：十六进制断行恢复、compare改mr_compare、SM4字节移位前无符号转换、头文件防重复包含。未将GmSSL算法调用包装成检测中心代码。
