![BlueArchive-Starter-cli](https://socialify.git.ci/ACGN-Alliance/BlueArchive-Starter-cli/image?description=1&descriptionEditable=%E7%A2%A7%E8%93%9D%E6%A1%A3%E6%A1%88%E5%88%9D%E5%A7%8B%E5%8F%B7%E5%B7%A5%E5%85%B7&font=Jost&forks=1&issues=1&logo=https%3A%2F%2Fi.imgur.com%2FGWyoWJN.png&name=1&owner=1&pattern=Floating%20Cogs&pulls=1&stargazers=1&theme=Light)

# BlueArchive-Starter-cli

BlueArchive initial account tool(Cli version)

As we known, BlueArchive Global banned initial account frequently, so we need to reset the account to get a good start account. When I found tools to do these things, I cant find a satisfied tools, they are basically made using macro scripts in conjunction with some screen operation software, or use the built-in operation record of the android simulator, but I think it's troublesome and cant know if the account has students we want to determine if we need to reset the account, so I made this tool.

## Support Platforms
Operation: Windows or Linux
Controlled: Android simulator or other android platform that supports `adb`(Android Debug Bridge)
> Compatibility with lower version platforms is not guaranteed, specific compatibility needs to be further tested

### Recommend Configuration
BlueStack 5 global or BlueStack Pie 64bit, resolution ratio `1280*720`(DPI: 240) or `1920*1080`(DPI: 240), scale is `100%`，these tested to run normally。  
We cant ensure the stability of other platforms，if you have problems when using this tool, please post issues in [discussion | 模拟器识图问题收集区](https://github.com/ACGN-Alliance/BlueArchive-Starter-cli/issues/13).

### Download
[Release](https://github.com/ACGN-Alliance/BlueArchive-Starter-cli/releases)

## How to use
### Video
[Bilibili](https://www.bilibili.com/video/BV1ku4y1z71F/)

### Documention
[BAS使用文档](https://acgn-alliance.github.io/BAS-doc/)

### Simple Version
1. Run the executable program(Windows is `.exe`, Linux is `.bin`).

2. Input `1` to read `注意事项`.
   
3. Connect to the device you want to operate using USB or open the Android emulator.
> tips: If it is a physical Android device, you need to open the settings followed: `settings`>`Develop Settings`>`USB debug`, then choose `Transport files`.

4. Input `2` to scan connected devices, then choose the device you need.
> tips: If it is a physical Android device, when you do this, it will tell you to verify rsa key, choose `yes`(The following steps will also require).

> If you cant scan the device, please check if you open `USB debug` option，if you cant find these please search if the simulator has `adb`.

5. Input `4` to enter settings menu, set user name and other settings. 

6. Start `BlueArchive`, and enter main interface.

7. Choose `7` to start the script.

## Important Notice
- Ensure that the network is stable and try not to experience connection failures or drops during the process.
- Please turn off phone hibernation.
- Adjust `Quality` in game settings to `Very high`.
- Use `English` as game language.
- Ensure the aspect ratio is `16:9`.
- Please leave group if you join it, otherwise it will lead to some problems.

## Thanks
[well404](https://github.com/Well2333) Contribute to the core code

[QTeaMix](https://tusiart.com/models/616971961895099597) The program icon was generated from this model

## How to contribute
You can fork this repository and post a [pr](https://github.com/ACGN-Alliance/BlueArchive-Starter/pulls) to contribute, or you can apply for our organzation [ACGN-Alliance](https://github.com/ACGN-Alliance), we welcome all of you.