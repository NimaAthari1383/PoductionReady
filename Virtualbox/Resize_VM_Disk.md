# Some VirtualBox Commands

## Check Remaining VM Disk Space

```bash
VBoxManage showmediuminfo "/home/nima/VirtualBox/Ubuntu_SRV_2604-AWX SRV/Ubuntu_SRV_2604-AWX SRV.vdi"
```

## Resizing A VM Disk Space

```bash
sudo VBoxManage modifymedium disk `/path/to/disk.vdi` --resize `new_disk_size`
```

***Important NOTE:*** Must know that:  `new_disk_size` = previuos_disk_space + new_added_disk_space. For instance:

```bash
previuos_disk_space = 25G
new_added_disk_space = 10G
new_disk_size = 35G
```
