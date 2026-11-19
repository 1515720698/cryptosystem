# 实验三（1–3 学时）提交清单

- [实践记录 Markdown](20241328_蔡贸俊_实验三_1-3学时_实践记录.md) · [实践记录 PDF](20241328_蔡贸俊_实验三_1-3学时_实践记录.pdf)
- [SKF 新增查询](skf/device_state.cpp) · [SDF 新增实现](sdf/src/device_info.c)
- [基线运行](logs/01-baseline.txt) · [SKF 验证](logs/02-skf-state.txt) · [SDF 验证](logs/03-sdf-info.txt) · [功能提交日志](logs/git-log.txt)
- [Windows 实体 SKF 补测](logs/04-skf-hardware.txt) · [补测脚本](tests/check-skf-windows.py)
- [openEuler 实体 SKF 验证](logs/08-skf-openeuler-hardware.txt) · [验证脚本](tests/check-skf-linux-usb.sh)
- [厂商库获取说明](vendor/README.md)：本地交付已含 x64 运行库，克隆 Git 时需按说明单独提取。

在 openEuler x86_64 中进入本目录，运行：

```bash
make
bash tests/check-skf.sh
make build/test-sdf
./build/sdf-info
./build/test-sdf
```

SKF 实体 UKey 已在 openEuler 验证通过。复现时确保 openEuler 正在运行，Windows 管理员终端用 `usbipd list` 找到 `055c:db08` 的 BUSID，执行 `usbipd bind --busid <BUSID>`、`usbipd attach --wsl --busid <BUSID>`。在 openEuler 以有权访问设备的账户运行 `modprobe usb_storage` 和 `bash tests/check-skf-linux-usb.sh`。测试完可用 `usbipd unbind --hardware-id 055c:db08` 归还设备并停止共享。

`bash tests/baseline.sh` 保留了初始诊断入口；无 USB 总线时原 SKF 示例可能崩溃。个人课程项目的 Gitee/GitHub 链接待补，未向参考仓库推送。按本阶段要求交付实践 Markdown 与 PDF，不包含另行评分的完整实验三 `.doc` 报告。
