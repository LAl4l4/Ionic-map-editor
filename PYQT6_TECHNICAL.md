# PyQt6 地图编辑器技术文档

## 架构概述

```
MapEditorQT (主窗口 - QMainWindow)
├── MapCanvas (绘制区域 - QWidget)
│   ├── draw_map() - 绘制地砖网格
│   ├── draw_entities() - 绘制实体
│   ├── draw_enemies() - 绘制敌人
│   ├── draw_spawn() - 绘制生成点
│   ├── mousePressEvent() - 处理点击
│   ├── mouseMoveEvent() - 处理拖动
│   └── wheelEvent() - 处理滚轮
│
├── 右侧工具栏 (create_right_panel)
│   ├── 文件操作区
│   ├── 编辑模式选择
│   ├── 地砖选择
│   ├── 显示选项
│   ├── 缩放控制
│   └── 状态显示
│
├── 状态栏 (QStatusBar)
└── 菜单栏 (未来扩展)
```

## 核心类说明

### 1. MapCanvas

继承自 `QWidget`，负责所有的地图绘制和用户交互。

#### 主要方法

```python
def paintEvent(self, event):
    """Qt 绘制事件，自动触发重绘"""
    # 绘制地图及所有对象
    
def mousePressEvent(self, event):
    """鼠标按下事件
    - 左键：放置地砖或添加对象
    - 右键：删除地砖
    """
    
def mouseMoveEvent(self, event):
    """鼠标移动事件
    - 中键拖动：移动地图
    """
    
def wheelEvent(self, event):
    """鼠标滚轮事件
    - 上滚：放大地图
    - 下滚：缩小地图
    """
```

#### 绘制管道

```python
def paintEvent(self, event):
    painter = QPainter(self)
    
    # 1. 填充背景
    painter.fillRect(self.rect(), QColor(30, 30, 30))
    
    # 2. 绘制地砖（栅栏）
    self.draw_map(painter)
    
    # 3. 绘制游戏对象（三层）
    self.draw_spawn(painter)      # 生成点（底层）
    self.draw_entities(painter)   # 实体（中层）
    self.draw_enemies(painter)    # 敌人（顶层）
```

### 2. MapEditorQt

继承自 `QMainWindow`，是主应用窗口。

#### 主要方法

```python
def __init__(self):
    """初始化编辑器状态"""
    
def init_ui(self):
    """初始化用户界面"""
    
def create_right_panel(self):
    """创建右侧工具栏"""
    
def load_map(map_name):
    """加载地图 JSON 文件"""
    
def save_map():
    """保存当前地图"""
    
def update_ui():
    """更新 UI 元素状态"""
    
def keyPressEvent(event):
    """处理键盘快捷键"""
```

## 坐标系统

### 世界坐标 vs 屏幕坐标

```
世界坐标系：
- 原点在地图左上角 (0, 0)
- 每个地砖 40 × 40 像素
- 用于存储地图数据

屏幕坐标系：
- 原点在窗口左上角 (0, 0)
- 会随缩放和偏移变化
- 用于绘制和输入

转换公式：
screen_x = world_x * zoom + offset_x
screen_y = world_y * zoom + offset_y

反向转换：
world_x = (screen_x - offset_x) / zoom
world_y = (screen_y - offset_y) / zoom
```

## 数据流向

### 地砖编辑流程

```
用户左键点击
    ↓
mousePressEvent()
    ↓
screen → world 坐标转换
    ↓
set_tile_at(row, col, tile_id)
    ↓
修改 self.map_data['map'][row][col]
    ↓
canvas.update()
    ↓
paintEvent() (Qt 自动调用)
    ↓
draw_map() 重新绘制
```

### 文件加载流程

```
用户点击"打开地图"
    ↓
load_map_dialog()
    ↓
选择 JSON 文件
    ↓
load_map(map_name)
    ↓
读取 JSON 文件
    ↓
加载到 self.map_data
    ↓
update_ui() 更新界面
    ↓
canvas.update() 重新绘制
```

## 事件处理

### 鼠标事件优先级

```
1. mousePressEvent() - 点击
2. mouseMoveEvent() - 移动
3. wheelEvent() - 滚轮
4. mouseReleaseEvent() - 释放（未实现）
```

### 键盘事件

```python
def keyPressEvent(self, event):
    if event.key() == Qt.Key.Key_1:      # 模式切换
    if event.key() == Qt.Key.Key_S:      # 保存（+Ctrl）
    if event.key() == Qt.Key.Key_R:      # 重置视图
    if event.key() == Qt.Key.Key_Delete: # 删除对象
```

## 缩放实现

### 缩放倍数管理

```python
self.zoom = 1.0  # 默认 100%

# 缩放范围：50% ~ 300%
min_zoom = 0.5
max_zoom = 3.0

# 滚轮缩放
if delta > 0:
    self.zoom = min(self.zoom + 0.2, max_zoom)
else:
    self.zoom = max(self.zoom - 0.2, min_zoom)
```

### 缩放对渲染的影响

```python
# 地砖大小随缩放变化
tile_size_screen = int(40 * self.zoom)

# 绘制坐标受缩放影响
x_screen = x_world * tile_size_screen + offset_x
y_screen = y_world * tile_size_screen + offset_y
```

## UI 组件树

```
QMainWindow (mapEditorQt)
├── QWidget (main_widget)
│   └── QHBoxLayout
│       ├── MapCanvas (canvas, stretch=1)
│       └── QFrame (right_panel, stretch=0)
│           └── QVBoxLayout
│               ├── QPushButton (load_btn)
│               ├── QPushButton (save_btn)
│               ├── QComboBox (mode_combo)
│               ├── QComboBox (tile_combo)
│               ├── QCheckBox (grid_check)
│               ├── QCheckBox (entity_check)
│               ├── QCheckBox (enemy_check)
│               ├── QCheckBox (spawn_check)
│               ├── QSpinBox (zoom_spin)
│               ├── QLabel (shortcuts_label)
│               └── QLabel (status_label)
│
└── QStatusBar (statusBar)
```

## 颜色方案

```python
# 背景色
background = QColor(30, 30, 30)    # 深灰

# 地砖色
tile_1 = QColor(80, 80, 80)        # 暗地砖
tile_2 = QColor(150, 150, 150)     # 亮地砖

# 对象色
entity_normal = QColor(0, 200, 0)  # 绿色 - 未选中
entity_selected = QColor(0, 255, 0)  # 亮绿 - 选中

enemy_normal = QColor(200, 0, 0)   # 暗红 - 未选中
enemy_selected = QColor(255, 0, 0) # 亮红 - 选中

spawn = QColor(0, 0, 255)          # 蓝色 - 生成点

grid = QColor(40, 40, 40)          # 很深的灰 - 网格
```

## 性能优化

### 1. 局部重绘

```python
# 只重绘必要区域（而不是整个窗口）
self.canvas.update()  # 触发 paintEvent()
```

### 2. 绘制优化

```python
# 在 paintEvent 中只绘制可见范围的地砖
for row in range(len(map_grid)):
    for col in range(len(map_grid[row])):
        # 可以添加裁剪逻辑，只绘制可见部分
        if is_visible(row, col):
            draw_tile()
```

### 3. 事件节流

```python
# mouseMoveEvent 中避免频繁重绘
# 只在必要时调用 update()
```

## 扩展指南

### 添加新的编辑模式

1. 在 `EditMode` 枚举中添加新模式：
```python
class EditMode(Enum):
    TILE = 1
    ENTITY = 2
    SPAWN = 3
    ENEMY = 4
    YOUR_MODE = 5  # 新增
```

2. 在 `mode_combo` 中添加选项：
```python
self.mode_combo.addItems([..., "你的模式"])
```

3. 在 `on_mode_changed` 中处理：
```python
def on_mode_changed(self, index):
    modes = [EditMode.TILE, ..., EditMode.YOUR_MODE]
    self.edit_mode = modes[index]
```

4. 在 `mousePressEvent` 中实现逻辑：
```python
elif self.edit_mode == EditMode.YOUR_MODE:
    # 你的编辑逻辑
```

### 添加新的显示选项

1. 添加成员变量：
```python
self.show_your_option = True
```

2. 添加 UI 复选框：
```python
self.your_check = QCheckBox(u"显示选项")
self.your_check.setChecked(True)
self.your_check.stateChanged.connect(...)
layout.addWidget(self.your_check)
```

3. 在 `paintEvent` 中添加条件绘制：
```python
if self.show_your_option:
    self.draw_your_objects(painter)
```

### 添加新的绘制层

```python
def draw_your_objects(self, painter):
    """绘制自定义对象"""
    objects = self.map_data.get('your_objects', [])
    for obj in objects:
        # 绘制逻辑
        painter.fillRect(...)
```

## 调试技巧

### 1. 启用调试输出

```python
# 在 load_map 中
print(f"地图大小: {len(map_grid)} × {len(map_grid[0])}")

# 在 set_tile_at 中
print(f"放置地砖: ({row}, {col}) = {tile_id}")
```

### 2. 可视化调试

```python
# 在 paintEvent 中绘制调试信息
debug_text = f"Zoom: {self.editor.zoom:.1f}x, Offset: ({self.editor.offset_x}, {self.editor.offset_y})"
# 绘制到屏幕
```

### 3. 检查数据完整性

```python
def validate_map_data(self):
    """验证地图数据"""
    if self.map_data is None:
        return False
    if 'map' not in self.map_data:
        return False
    # ... 更多检查
    return True
```

## 常见问题和解决方案

### 问题：绘制不更新

**原因：** 没有调用 `update()`  
**解决：** 在修改数据后调用 `self.canvas.update()`

### 问题：坐标偏移

**原因：** 没有正确转换坐标系  
**解决：** 检查 world ↔ screen 的转换

### 问题：性能下降

**原因：** 频繁重绘或数据过大  
**解决：**
1. 减少 update() 调用频率
2. 优化绘制算法
3. 使用图形缓存

## 版本历史

### v2.0 (当前)
- ✅ 基于 PyQt6 重构
- ✅ 完美的中文支持
- ✅ 原生系统界面
- ✅ 更好的性能

### v1.0
- 基于 Pygame
- 基础编辑功能

## 参考资源

- [PyQt6 官方文档](https://doc.qt.io/qt-6/)
- [Qt 绘制系统](https://doc.qt.io/qt-6/paintsystem.html)
- [Qt 事件系统](https://doc.qt.io/qt-6/eventsandmousepicking.html)
