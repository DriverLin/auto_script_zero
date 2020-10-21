# auto_script_zero
# 使用树莓派执行键盘脚本

## 安装   

首先配置树莓派zero的HID

[pi-as-keyboard](https://github.com/c4software/pi-as-keyboard)
    
下载脚本

[./src/keybord_controller.py](https://github.com/DriverLin/auto_script_zero/blob/master/src/keybord_controller.py)

安装依赖 
sudo pip3 install bottle

## 使用 

```
sudo python3 ./keybord_controller.py    
```

手机或电脑访问 \[raspberryip\]:/8003

输入脚本 

上传脚本

开始执行

## 脚本格式说明
loop == true 则重复执行

insertRandom == true 则每步操作之间插入0~100ms随机延迟

press key 按下按键

release key 释放按键

sleep a b 区间(a,b)随机延迟 单位为ms

最多同时按下6个普通按键和一个功能键(ctrl||shift)

再按下更多时不再响应

部分按键没实现，有需求可自行添加