# 教材代码来源与适配范围

教材压缩包：用户提供的 `Win加密解密-code(1).rar`，SHA-256 为 `B92049BEA16ECC99E636823F70C6A7BEF590B8848AB0BEEC13D552686F6C618A`。

- SM4：`ch03/3.6/test/test/sm4.cpp`、`sm4.h`。
- SM3：`ch04/4.2/test/test/sm3.cpp`、`sm3.h`。
- SM2：`ch14/14.2/test/test/SM2_ENC.c`、`SM2_ENC.h`、`kdf.c`、`kdf.h`。

上述原文件的必要子集保存在 `materials/textbook_selected/`；完整解压目录和原始 RAR 仍保留在本机 materials 内。`prepare_textbook_sources.py` 每次从子集生成 UTF-8 的 `src/textbook/`，不从前半段检测中心实验替换教材算法。

适配仅包括移除空预编译头引用、GB18030/UTF-8 编码读取、将 Windows 32位 unsigned long 假设显式改为 uint32_t、使循环移位计数按32取模，以及 SM4 字节左移前转换为无符号32位值。逐文件 SHA-256 与完整差异见 `logs/textbook_source_provenance.json`、`logs/textbook_portability.patch`。

SM2 大数/椭圆曲线依赖采用前半段已保存的 MIRACL 官方源代码，提交 `b9b8fd471de253cfd6313446cb490741edb069a7`，保留其原始版权与来源说明。Windows 教材的 mymiracl.lib 不参与 Linux 链接。教材头文件内的全局变量暂采用 `-fcommon` 兼容；KDF 内原有字节缓冲区重解释使用 `-fno-strict-aliasing`，不将参考实现描述为经安全审计的生产实现。

`test_key.c` 只用 GmSSL 库将公开 d=1 夹具序列化为 GmSSL 命令可读取的文件，不参与教材三算法的实现。

GM3000 SDK 来源：`https://gitee.com/rocedu/bestidiocs4stu` 的 `ch06/longmaiskf0016-stu.zip`，检出提交 `048ec69e7998c9d13eb4624541acbe6b1e089589`。随交付保留 x64 SKF 库、头文件和对应使用手册；完整 SDK 留在本地 `materials/GM3000_SDK_reference/`。
