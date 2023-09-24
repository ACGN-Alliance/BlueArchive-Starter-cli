![img](https://socialify.git.ci/ACGN-Alliance/BlueArchive-Starter-cli/image?description=1&font=Jost&forks=1&issues=1&language=1&logo=https%3A%2F%2Fcdnimg.gamekee.com%2Fimages%2Fwww%2F1596521281115_38919084.png&name=1&owner=1&pattern=Floating%20Cogs&pulls=1&stargazers=1&theme=Light)

# BlueArchive-Starter-cli

<!-- <tr>
<td>

![Static Badge](https://img.shields.io/badge/769521861-brightgreen?label=QQ%20Group)
</td>
<td>

![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FACGN-Alliance%2FBlueArchive-Starter-cli%2Ffeature-2%2Fpyproject.toml)
</td>

![Static Badge](https://img.shields.io/badge/1.0.3-green?label=latest)
</tr> -->

碧蓝档案初始号工具CLI版本(原[BlueArchive-Starter](https://github.com/ACGN-Alliance/BlueArchive-Starter)项目)  

众所周知, 碧蓝档案国际服初始号封号现象特别严重, 因此要想有个好一点的box必须在建号的时候不停的重置帐号来刷取.
看了下网上并没有特别好用的初始号刷号工具, 基本都是使用宏脚本配合一些屏幕操作软件做的, 或者使用模拟器自带的操作记录, 
但是这样做比较麻烦, 并且不能判断刷出来的号有哪些学生从而决定是否需要重刷, 于是就想写一个自动刷号工具来进行辅助.

## 支持平台
操作端: Windows/Linux  
被控端: Android 手机/Android 模拟器以及其他支持 Adb(安卓调试桥) 的 Android 平台
> 不保证较低版本平台兼容性, 具体兼容性有待测试

### 推荐配置
蓝叠5国际版 64bit或蓝叠 Pie 64bit，分辨率`1280*720`(DPI: 240)或`1920*1080`(DPI: 240)，界面缩放`100%`，经测试可以顺利运行。  
其他模拟器与配置不保证可正常运行，如果有问题请在[discussion | 模拟器识图问题收集区](https://github.com/ACGN-Alliance/BlueArchive-Starter-cli/issues/13)反馈，如果可以的话之后会进行适配，谢谢~

## 下载
[Release](https://github.com/ACGN-Alliance/BlueArchive-Starter-cli/releases)

> 因为Windows下使用`--onefile`打包有概率报毒，因此将dll与pyd文件拆开了

## 使用
### 视频版(推荐)
[Bilibili](https://www.bilibili.com/video/BV1ku4y1z71F/)

### 文字版
1. 在可执行文件目录下打开命令行(Windows为`main.exe`, Linux为`bas-for-linux.bin`), 执行程序。

2. 输入`1`查看`注意事项`。
   
3. 使用 USB 连接上你要操作的设备或者打开安卓模拟器。
> 注: 如果是实体安卓设备, 则需要把 `设置`>`开发者选项`>`USB调试` 开关打开, 连接上数据线后选择`传输文件`(若选择`仅充电`则需要在开发者选项当中把`仅充电下允许USB调试`打开)

1. 输入`2`来扫描已连接设备, 扫描出来后选取对应设备。
> 注: 如果是安卓手机, 执行此步时会提示需要验证 RSA 密钥(后面的步骤也会需要), 一律点击`允许`.

> 如果扫描不到模拟器请打开模拟器设置查看是否打开`USB调试`选项，如果找不到请上网搜索该模拟器是否支持USB调试(MuMu模拟器的某个版本就不支持)

5. 输入`4`打开配置菜单, 配置用户名以及其他选项。 

6. 打开`BlueArchive`, 进入大厅界面。

7. 选择`5`来开始执行脚本。

## 注意事项
- 确保网络通畅, 中途尽量不要出现连接失败以及掉线的状况
- 请关闭手机休眠
- 游戏设置中的`Quality`调整为`Very high`
- 语言请使用`English`
- 游戏宽高比设置为`16:9`
- 如果加入了社团请先退出, 否则会导致操作失败

## 常见问题解答
#### 1.模拟器开了但没扫描到是为什么？  
请检查你所用模拟器的adb调试设置是否打开，比如蓝叠的默认为关闭状态。但是有群友反馈开了也扫描不到，目前尚不清楚原因，可使用`指定地址`模式连接

#### 2.报错`图片尺寸不一致!如果此提示一直出现(>=25条)请向开发者反馈。`怎么解决？
少量此提示为正常现象，如果一直出现说明识别出现问题，请向开发者反馈

#### 3.报错`No such file or directory: 'temp_full_screenshot.png'`
请查看自己adb是否正确连接，确认自己连接设备时没有任何报错

## 感谢
[well404](https://github.com/Well2333) 帮助编写部分核心代码

[QTeaMix](https://tusiart.com/models/616971961895099597) 本程序图标基于此模型生成

## 参与开发
你可以通过 fork 本仓库并提出 [pr](https://github.com/ACGN-Alliance/BlueArchive-Starter/pulls) 来贡献代码, 另外如果你觉得你有能力的话欢迎加入我们的组织 [ACGN-Alliance](https://github.com/ACGN-Alliance), 随时欢迎加入(摸鱼也行的啦)