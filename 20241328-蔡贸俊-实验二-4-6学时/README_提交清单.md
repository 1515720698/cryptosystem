# 实验二4—6学时提交清单

## 主要文件

- [4—6学时实践记录（Markdown）](20241328_蔡贸俊_实验二_4-6学时_实践记录.md)
- [4—6学时实践记录（PDF）](20241328_蔡贸俊_实验二_4-6学时_实践记录.pdf)
- [实验二综合报告（老师模板DOC）](20241328_蔡贸俊_实验二_密码算法实现.doc)
- [实验二综合报告（可编辑DOCX）](20241328_蔡贸俊_实验二_密码算法实现.docx)
- [实验二综合报告（PDF）](20241328_蔡贸俊_实验二_密码算法实现.pdf)
- [验证结论JSON](logs/crosscheck_results.json)、[完整命令日志](logs/crosscheck.log)、[SKF实际调用记录](logs/ukey_results.json)
- [实际终端截图](images/GM3000三方交叉验证_实际终端.png)
- `20241328_蔡贸俊_实验二_4-6学时_提交材料.zip`：最终精简可复现材料包。
- `实验二_4-6学时_本地Git历史.bundle`、`logs/git_log_完整.txt`：真实本地归档历史。

## 已完成

教材SM2/SM3/SM4编译与GmSSL对照、标准函数映射、GM3000三算法交叉验证。最终59项断言通过（软件40、硬件交叉19）；硬件SM3共8组、SM4共4组、SM2外部公钥加密3次。SM2密文分别交教材和GmSSL解密，均恢复原文。

## 最短复现

插入已初始化GM3000，在本目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\运行实验.ps1
```

仅重跑软件并复核已保存硬件输出：

```powershell
powershell -ExecutionPolicy Bypass -File .\运行实验.ps1 -ReuseHardware
```

依赖：64位Windows Python，现有openEuler WSL、GCC/G++、Python3、GmSSL命令及开发库、libubsan。`materials/GM3000_runtime`附所用x64 SKF DLL；`materials/textbook_selected`附教材原始必要子集；`src/miracl`附构建所需第三方源码。运行会更新随机密文、日志和哈希，交付报告引用本次保存结果。

## 提交状态和边界

课程仓库：https://github.com/1515720698/cryptosystem 。第一阶段已发布；本次4—6学时仅做本地Git归档，未推送远端。归档时间不等于早期开发时间。

模板封面实际课节、预习程度需本人据实填写；个人心得标为AI代拟待核对。硬件操作限于SKF摘要、临时SM4测试密钥和外部SM2公钥加密，不涉及设备私钥、PIN或证书；本机测试私钥为公开d=1夹具，运行时生成且排除于提交包。

完整教材解压目录、原始RAR及完整SDK仍留在本机materials内；最终ZIP只附复现必需源码/运行库/手册/标准，排除重复完整SDK、VS缓存、构建产物和运行时私钥。第一阶段记录作为综合报告来源，保存在materials/第一阶段记录。
