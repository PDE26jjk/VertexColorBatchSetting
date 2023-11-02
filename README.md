# VertexColorBatchSetting
A blender Add-on.

Set Vertex Color on selected elements.

批量设置顶点色的blender插件。

学关卡设计的时候，讲师用的Maya，可以选择面然后设置顶点色，可以方便地在Unity里面区分不同的东西。我用blender怎么也找不到这个功能，就自己写了个插件。顺便一提，可以用unity mesh sync插件同步Blender和Unity的东西。

可以选择点线面来设置顶点色，可以获取顶点色的平均值。palette是纹理绘制模式的brush的palette，想添加颜色就去Texture painting mode找palette设置。

如果开了gamma校正，设置顶点色的时候会取2.2乘方，获取顶点色的时候取1/2.2乘方。



## How to use:

![vct_show1](https://raw.githubusercontent.com/PDE26jjk/misc/main/img/vct_show1.gif)
