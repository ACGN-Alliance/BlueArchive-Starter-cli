![img](https://socialify.git.ci/ACGN-Alliance/BlueArchive-Starter/image?description=1&font=Jost&forks=1&issues=1&language=1&logo=https%3A%2F%2Fcdnimg.gamekee.com%2Fimages%2Fwww%2F1596521281115_38919084.png&name=1&owner=1&pattern=Floating%20Cogs&pulls=1&stargazers=1&theme=Light)

# BlueArchive-Starter-cli
碧蓝档案初始号工具CLI版本(原[BlueArchive-Starter](https://github.com/ACGN-Alliance/BlueArchive-Starter)项目)

## 项目正在开发, 快了快了

众所周知, 碧蓝档案国际服初始号封号现象特别严重, 因此要想有个好一点的box必须在建号的时候不停的重置帐号来刷取.
看了下网上并没有特别好用的初始号刷号工具, 基本都是使用宏脚本配合一些屏幕操作软件做的, 或者使用模拟器自带的操作记录, 
但是这样做比较麻烦, 并且不能判断刷出来的号有哪些学生从而决定是否需要重刷, 于是就想写一个自动刷号工具来进行辅助.

## 支持平台
操作端: Windows/Linux(?)  
被控端: Android 手机/Android 模拟器以及其他支持 Adb(安卓调试桥) 的 Android 平台
> 不保证较低版本平台兼容性, 具体兼容性有待测试

## 下载
目前本工具尚在开发初期, 功能未完善, 并无 release 版本

## 使用
1. 进入[Android SDK Platform-Tools](https://developer.android.google.cn/studio/releases/platform-tools?hl=zh-cn)下载对应于自己系统的最新版 platform 工具  
> 提供的软件中不包含 platform-tools

2. 将下载好的压缩包解压, 将名为 `platform-tools` 的文件夹当中的`adb`文件放入下载好的 `ba-starter` 可执行文件同级目录下

3. 打开命令行(Windows: 按住Win+R键, 输入`cmd`然后回车, linux不用我教了吧), 切换到`ba-starter`可执行文件目录下, 执行程序

4. 使用 USB 连接上你要操作的设备或者打开安卓模拟器
> 注: 如果是实体安卓设备, 则需要把 `设置`>`开发者选项`>`USB调试` 开关打开, 连接上数据线后选择`传输文件`(若选择`仅充电`则需要在开发者选项当中把`仅充电下允许USB调试`打开)

5. 输入`1`查看`注意事项`

6. 输入`2`来扫描已连接设备, 扫描出来后选取对应设备
> 注: 如果是安卓手机, 执行此步时会提示需要验证 RSA 密钥(后面的步骤也会需要), 一律点击`允许`.

7. 打开`BlueArchive`, 进入大厅界面

8. 选择`5`来开始执行脚本

## 注意事项
- 确保网络通畅, 中途尽量不要出现连接失败的状况
- 请关闭手机休眠
- 游戏设置中的`Quality`调整为`high`
- 游戏宽高比设置为`16:9`

## 计划

- [ ] 软件打包可执行文件
- [ ] box内容判断
- [ ] 断点续运&异常中断
- [ ] 多种设备支持
- [ ] adb可执行文件扫描

## 参与开发
你可以通过 fork 本仓库并提出 [pr](https://github.com/ACGN-Alliance/BlueArchive-Starter/pulls) 来贡献代码, 另外如果你觉得你有能力的话欢迎加入我们的组织 [ACGN-Alliance](https://github.com/ACGN-Alliance), 随时欢迎加入(摸鱼也行的啦)