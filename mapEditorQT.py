# -*- coding: utf-8 -*-
import json
import os
import sys
from enum import Enum
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QComboBox, QCheckBox, QScrollArea,
    QFrame, QGridLayout, QFileDialog, QMessageBox, QStatusBar
)
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont, QKeySequence
)
from PyQt6.QtCore import Qt, QRect, QPoint, QSize


class EditMode(Enum):
    """编辑模式"""
    TILE = 1
    ENTITY = 2
    SPAWN = 3
    ENEMY = 4


class MapCanvas(QWidget):
    """地图绘制区域"""
    
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        
        if self.editor.map_data is None:
            return
        
        # 绘制地图
        self.draw_map(painter)
        
        # 绘制其他元素
        if self.editor.show_spawn:
            self.draw_spawn(painter)
        if self.editor.show_entities:
            self.draw_entities(painter)
        if self.editor.show_enemies:
            self.draw_enemies(painter)
    
    def draw_map(self, painter):
        """绘制地图网格"""
        map_grid = self.editor.map_data.get('map', [])
        tile_size = int(40 * self.editor.zoom)
        
        for row in range(len(map_grid)):
            for col in range(len(map_grid[row])):
                tile = map_grid[row][col]
                x = col * tile_size + self.editor.offset_x
                y = row * tile_size + self.editor.offset_y
                
                if isinstance(tile, dict):
                    tile_code = tile.get('code', 1)
                else:
                    tile_code = tile
                
                if tile_code == 1:
                    color = QColor(80, 80, 80)
                elif tile_code == 2:
                    color = QColor(150, 150, 150)
                else:
                    color = QColor(120, 120, 120)
                
                painter.fillRect(int(x), int(y), int(tile_size), int(tile_size), color)
                
                if self.editor.show_grid:
                    painter.drawRect(int(x), int(y), int(tile_size), int(tile_size))
    
    def draw_entities(self, painter):
        """绘制实体"""
        entities = self.editor.map_data.get('entity', [])
        for entity in entities:
            x, y = entity['position']
            screen_x = x * self.editor.zoom + self.editor.offset_x
            screen_y = y * self.editor.zoom + self.editor.offset_y
            
            color = QColor(0, 255, 0) if entity == self.editor.selected_entity else QColor(0, 200, 0)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(screen_x) - 15, int(screen_y) - 15, 30, 30)
            
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawEllipse(int(screen_x) - 15, int(screen_y) - 15, 30, 30)
    
    def draw_enemies(self, painter):
        """绘制敌人"""
        enemies = self.editor.map_data.get('enemy', [])
        for enemy in enemies:
            x, y = enemy['spawn']
            screen_x = x * self.editor.zoom + self.editor.offset_x
            screen_y = y * self.editor.zoom + self.editor.offset_y
            
            color = QColor(255, 0, 0) if enemy == self.editor.selected_enemy else QColor(200, 0, 0)
            points = [
                QPoint(int(screen_x), int(screen_y) - 15),
                QPoint(int(screen_x) + 15, int(screen_y) + 15),
                QPoint(int(screen_x) - 15, int(screen_y) + 15)
            ]
            painter.setBrush(QBrush(color))
            painter.drawPolygon(points)
            
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawPolygon(points)
    
    def draw_spawn(self, painter):
        """绘制玩家生成点"""
        spawn = self.editor.map_data.get('playerSpawn', {})
        x, y = spawn.get('x', 0), spawn.get('y', 0)
        screen_x = x * self.editor.zoom + self.editor.offset_x
        screen_y = y * self.editor.zoom + self.editor.offset_y
        
        painter.fillRect(int(screen_x) - 15, int(screen_y) - 15, 30, 30, QColor(0, 0, 255))
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawRect(int(screen_x) - 15, int(screen_y) - 15, 30, 30)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if self.editor.map_data is None:
            return
        
        x = event.pos().x()
        y = event.pos().y()
        
        world_x = (x - self.editor.offset_x) / (40 * self.editor.zoom)
        world_y = (y - self.editor.offset_y) / (40 * self.editor.zoom)
        
        if event.button() == Qt.MouseButton.LeftButton:
            if self.editor.edit_mode == EditMode.TILE:
                grid_x = int(world_x)
                grid_y = int(world_y)
                self.editor.set_tile_at(grid_y, grid_x, self.editor.selected_tile_id)
            elif self.editor.edit_mode == EditMode.ENTITY:
                self.editor.add_or_select_entity(world_x * 40, world_y * 40)
            elif self.editor.edit_mode == EditMode.SPAWN:
                self.editor.set_player_spawn(world_x * 40, world_y * 40)
            elif self.editor.edit_mode == EditMode.ENEMY:
                self.editor.add_or_select_enemy(world_x * 40, world_y * 40)
            self.update()
        
        elif event.button() == Qt.MouseButton.RightButton:
            grid_x = int(world_x)
            grid_y = int(world_y)
            self.editor.set_tile_at(grid_y, grid_x, 1)
            self.update()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.MouseButton.MiddleButton:
            if hasattr(self, 'last_pos'):
                delta = event.pos() - self.last_pos
                self.editor.offset_x += delta.x()
                self.editor.offset_y += delta.y()
                self.update()
                self.editor.save_last_state()
            self.last_pos = event.pos()
    
    def wheelEvent(self, event):
        """鼠标滚轮事件"""
        delta = event.angleDelta().y()
        steps = delta / 120.0 if delta != 0 else 0.0

        old_zoom = self.editor.zoom
        cfg = self.editor.config or {}
        zcfg = cfg.get('zoom', {})

        factor = float(zcfg.get('wheel_factor', 1.05))
        zmin = float(zcfg.get('min', 0.5))
        zmax = float(zcfg.get('max', 3.0))

        target_zoom = old_zoom * (factor ** steps)
        new_zoom = max(zmin, min(zmax, target_zoom))

    # 鼠标位置（屏幕坐标）
        px = event.position().x()
        py = event.position().y()

        tile_size = 40.0

    # 世界坐标（以鼠标当前对应的点为锚点）
        world_x = (px - self.editor.offset_x) / (tile_size * old_zoom)
        world_y = (py - self.editor.offset_y) / (tile_size * old_zoom)

    # 应用新 zoom
        self.editor.zoom = new_zoom

    # 保持世界坐标不变 → 反向推 offset
        self.editor.offset_x = px - world_x * tile_size * new_zoom
        self.editor.offset_y = py - world_y * tile_size * new_zoom

        self.editor.zoom_spin.setValue(int(new_zoom * 100))
        self.update()
        self.editor.update_status()
        self.editor.save_last_state()


class MapEditorQt(QMainWindow):
    """基于 PyQt6 的地图编辑器"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(u"mapEditor - Qt6")
        self.setGeometry(100, 100, 1600, 1000)
        
        # 地图数据
        self.map_data = None
        self.current_map_name = None
        self.basepath = os.path.dirname(os.path.abspath(__file__))
        
        # 编辑器状态
        self.edit_mode = EditMode.TILE
        self.selected_tile_id = 1
        self.zoom = 1
        self.offset_x = 0
        self.offset_y = 0

        # 配置与持久化
        self.config = None
        self.config_path = os.path.join(self.basepath, "map_editor_config.json")
        self.load_config()
        
        # UI 状态
        self.show_grid = True
        self.show_entities = True
        self.show_enemies = True
        self.show_spawn = True
        
        # 选中的对象
        self.selected_entity = None
        self.selected_enemy = None
        
        # 初始化 UI
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        # 主窗口
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        
        # 左侧：地图编辑区
        self.canvas = MapCanvas(self)
        main_layout.addWidget(self.canvas, 1)
        
        # 右侧：工具栏
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 0)
        
        # 状态栏
        self.statusBar().showMessage(u"准备就绪")
    
    def create_right_panel(self):
        """创建右侧工具栏"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # 地图文件操作
        layout.addWidget(QLabel(u"<b>地图文件</b>"))
        
        load_btn = QPushButton(u"打开地图")
        load_btn.clicked.connect(self.load_map_dialog)
        layout.addWidget(load_btn)
        
        save_btn = QPushButton(u"保存地图")
        save_btn.clicked.connect(self.save_map)
        layout.addWidget(save_btn)
        
        layout.addSpacing(20)
        
        # 编辑模式选择
        layout.addWidget(QLabel(u"<b>编辑模式</b>"))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([u"地砖编辑", u"实体编辑", u"生成点编辑", u"敌人编辑"])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        layout.addWidget(self.mode_combo)
        
        layout.addSpacing(20)
        
        # 地砖选择
        layout.addWidget(QLabel(u"<b>地砖选择</b>"))
        
        self.tile_combo = QComboBox()
        self.tile_combo.currentIndexChanged.connect(self.on_tile_changed)
        layout.addWidget(self.tile_combo)
        
        layout.addSpacing(20)
        
        # 显示选项
        layout.addWidget(QLabel(u"<b>显示选项</b>"))
        
        self.grid_check = QCheckBox(u"显示网格")
        self.grid_check.setChecked(True)
        self.grid_check.stateChanged.connect(lambda: setattr(self, 'show_grid', self.grid_check.isChecked()) or self.canvas.update())
        layout.addWidget(self.grid_check)
        
        self.entity_check = QCheckBox(u"显示实体")
        self.entity_check.setChecked(True)
        self.entity_check.stateChanged.connect(lambda: setattr(self, 'show_entities', self.entity_check.isChecked()) or self.canvas.update())
        layout.addWidget(self.entity_check)
        
        self.enemy_check = QCheckBox(u"显示敌人")
        self.enemy_check.setChecked(True)
        self.enemy_check.stateChanged.connect(lambda: setattr(self, 'show_enemies', self.enemy_check.isChecked()) or self.canvas.update())
        layout.addWidget(self.enemy_check)
        
        self.spawn_check = QCheckBox(u"显示生成点")
        self.spawn_check.setChecked(True)
        self.spawn_check.stateChanged.connect(lambda: setattr(self, 'show_spawn', self.spawn_check.isChecked()) or self.canvas.update())
        layout.addWidget(self.spawn_check)
        
        layout.addSpacing(20)
        
        # 缩放控制
        layout.addWidget(QLabel(u"<b>缩放</b>"))
        
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel(u"缩放倍数:")
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setMinimum(50)
        self.zoom_spin.setMaximum(300)
        self.zoom_spin.setValue(100)
        self.zoom_spin.setSuffix("%")
        self.zoom_spin.valueChanged.connect(self.on_zoom_changed)
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.zoom_spin)
        layout.addLayout(zoom_layout)

        # 视图重置按钮
        reset_btn = QPushButton(u"重置视图（居中）")
        reset_btn.clicked.connect(self.reset_to_center)
        layout.addWidget(reset_btn)
        
        layout.addSpacing(20)
        
        # 快捷键提示
        layout.addWidget(QLabel(u"<b>快捷键</b>"))
        
        shortcuts_text = u"""
左键：放置地砖/添加对象
右键：删除地砖
中键拖动：移动视图
滚轮：缩放
Delete/Backspace：删除选中对象
R：重置视图
        """
        
        shortcuts_label = QLabel(shortcuts_text)
        shortcuts_label.setFont(QFont("Monaco", 9))
        layout.addWidget(shortcuts_label)
        
        layout.addStretch()
        
        # 信息面板
        layout.addWidget(QLabel(u"<b>当前状态</b>"))
        
        self.status_label = QLabel()
        self.status_label.setFont(QFont("Monaco", 10))
        layout.addWidget(self.status_label)
        
        return panel
    
    def load_map(self, map_name=None):
        """加载地图文件"""
        if not map_name:
            map_name = self.config.get('last_map')
        if map_name is None:
            return False  
        
        filepath = os.path.join(self.basepath, u"{}.json".format(map_name))
        if not os.path.exists(filepath):
            QMessageBox.warning(self, u"错误", u"地图文件不存在: {}".format(filepath))
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.map_data = json.load(f)
                self.current_map_name = map_name
                self.update_ui()
                # 视图定位：优先恢复上次视图，否则居中
                if self.config.get('persist', {}).get('remember_last_view') and self.config.get('last_state'):
                    self.apply_last_view()
                else:
                    self.center_view()
                self.canvas.update()
                self.statusBar().showMessage(u"地图已加载: {}".format(map_name))
                return True
        except Exception as e:
            QMessageBox.critical(self, u"错误", u"加载地图失败: {}".format(e))
            return False
    
    def save_map(self):
        """保存地图文件"""
        if self.map_data is None:
            QMessageBox.warning(self, u"警告", u"没有打开任何地图")
            return False
        
        filepath = os.path.join(self.basepath, u"{}.json".format(self.current_map_name))
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.map_data, f, ensure_ascii=False, indent=2)
                self.statusBar().showMessage(u"地图已保存: {}".format(self.current_map_name))
                return True
        except Exception as e:
            QMessageBox.critical(self, u"错误", u"保存地图失败: {}".format(e))
            return False
    
    def load_map_dialog(self):
        """打开文件对话框选择地图"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            u"打开地图文件",
            self.basepath,
            u"JSON 文件 (*.json)"
        )
        
        if filename:
            map_name = os.path.splitext(os.path.basename(filename))[0]
            self.load_map(map_name)
    
    def update_ui(self):
        """更新 UI 元素"""
        if self.map_data is None:
            return
        
        # 更新地砖选择下拉列表
        self.tile_combo.clear()
        tile_info = self.map_data.get('tile_info', {})
        tile_ids = sorted([int(k) for k in tile_info.keys()])
        
        for tile_id in tile_ids:
            tile_name = tile_info[str(tile_id)].get('name', 'Unknown')
            self.tile_combo.addItem(u"ID {}: {}".format(tile_id, tile_name), tile_id)
        
        self.update_status()
    
    def update_status(self):
        """更新状态信息"""
        if self.map_data is None:
            return
        
        mode_names = {
            EditMode.TILE: u"地砖编辑",
            EditMode.ENTITY: u"实体编辑",
            EditMode.SPAWN: u"生成点编辑",
            EditMode.ENEMY: u"敌人编辑"
        }
        
        status_text = u"""地图: {}
模式: {}
选中地砖: {}
缩放: {:.1f}x
网格: {}
实体: {}
敌人: {}
生成点: {}""".format(
            self.current_map_name,
            mode_names.get(self.edit_mode, u"未知"),
            self.selected_tile_id,
            self.zoom,
            u"✓" if self.show_grid else u"✗",
            u"✓" if self.show_entities else u"✗",
            u"✓" if self.show_enemies else u"✗",
            u"✓" if self.show_spawn else u"✗"
        )
        
        self.status_label.setText(status_text)
    
    def on_mode_changed(self, index):
        """编辑模式变更"""
        modes = [EditMode.TILE, EditMode.ENTITY, EditMode.SPAWN, EditMode.ENEMY]
        self.edit_mode = modes[index]
        self.update_status()
    
    def on_tile_changed(self, index):
        """地砖选择变更"""
        if self.map_data and index >= 0:
            self.selected_tile_id = self.tile_combo.currentData()
            self.update_status()
    
    def on_zoom_changed(self, value):
        """缩放变更"""
        old_zoom = self.zoom
        self.zoom = value / 100.0
        # 以画布中心为锚点，尽量减少跳动
        cx = self.canvas.width() / 2.0
        cy = self.canvas.height() / 2.0
        world_x = (cx - self.offset_x) / (40 * old_zoom)
        world_y = (cy - self.offset_y) / (40 * old_zoom)
        self.offset_x = int(cx - world_x * 40 * self.zoom)
        self.offset_y = int(cy - world_y * 40 * self.zoom)
        self.canvas.update()
        self.update_status()
        self.save_last_state()
    
    def set_tile_at(self, row, col, tile_id):
        """设置指定位置的地砖"""
        if self.map_data is None:
            return False
        
        map_grid = self.map_data.get('map', [])
        if 0 <= row < len(map_grid) and 0 <= col < len(map_grid[0]):
            tile_info = self.map_data['tile_info'].get(str(tile_id))
            if tile_info:
                map_grid[row][col] = tile_info
                return True
        return False
    
    def add_or_select_entity(self, world_x, world_y):
        """添加或选择实体"""
        entities = self.map_data.get('entity', [])
        
        for entity in entities:
            ex, ey = entity['position']
            if abs(ex - world_x) < 30 and abs(ey - world_y) < 30:
                self.selected_entity = entity
                return
        
        new_entity = {
            "id": len(entities) + 1,
            "position": [world_x, world_y]
        }
        entities.append(new_entity)
        self.selected_entity = new_entity
    
    def add_or_select_enemy(self, world_x, world_y):
        """添加或选择敌人"""
        enemies = self.map_data.get('enemy', [])
        
        for enemy in enemies:
            ex, ey = enemy['spawn']
            if abs(ex - world_x) < 30 and abs(ey - world_y) < 30:
                self.selected_enemy = enemy
                return
        
        new_enemy = {
            "id": 1,
            "spawn": [world_x, world_y],
            "delay": 0
        }
        enemies.append(new_enemy)
        self.selected_enemy = new_enemy
    
    def set_player_spawn(self, world_x, world_y):
        """设置玩家生成点"""
        spawn = self.map_data.get('playerSpawn', {})
        spawn['x'] = world_x
        spawn['y'] = world_y
    
    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            if self.selected_entity:
                entities = self.map_data.get('entity', [])
                if self.selected_entity in entities:
                    entities.remove(self.selected_entity)
                    self.selected_entity = None
            if self.selected_enemy:
                enemies = self.map_data.get('enemy', [])
                if self.selected_enemy in enemies:
                    enemies.remove(self.selected_enemy)
                    self.selected_enemy = None
            self.canvas.update()
        
        elif event.key() == Qt.Key.Key_R:
            self.reset_to_center()
        
        elif event.key() == Qt.Key.Key_1:
            self.mode_combo.setCurrentIndex(0)
        elif event.key() == Qt.Key.Key_2:
            self.mode_combo.setCurrentIndex(1)
        elif event.key() == Qt.Key.Key_3:
            self.mode_combo.setCurrentIndex(2)
        elif event.key() == Qt.Key.Key_4:
            self.mode_combo.setCurrentIndex(3)
        
        elif event.key() == Qt.Key.Key_S and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.save_map()
        
        else:
            super().keyPressEvent(event)

    def center_view(self):
        """将地图居中到画布"""
        if not self.map_data:
            return
        map_grid = self.map_data.get('map', [])
        if not map_grid or not map_grid[0]:
            return
        rows = len(map_grid)
        cols = len(map_grid[0])
        tile_size = int(40 * self.zoom)
        map_w = cols * tile_size
        map_h = rows * tile_size
        cx = self.canvas.width() // 2
        cy = self.canvas.height() // 2
        self.offset_x = int(cx - map_w / 2)
        self.offset_y = int(cy - map_h / 2)
        self.zoom_spin.setValue(int(self.zoom * 100))

    def reset_to_center(self):
        """重置视图到居中"""
        self.center_view()
        self.canvas.update()
        self.save_last_state()

    def load_config(self):
        """读取配置文件，若不存在则使用默认配置"""
        defaults = {
            "zoom": {"min": 0.5, "max": 3.0, "wheel_factor": 1.05},
            "view": {"center_on_load": True},
            "persist": {"remember_last_view": True},
            "last_state": None
        }
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 合并默认值
                    def merge(d, s):
                        for k, v in s.items():
                            if k not in d:
                                d[k] = v
                            elif isinstance(v, dict) and isinstance(d[k], dict):
                                merge(d[k], v)
                        return d
                    self.config = merge(data, defaults)
            else:
                self.config = defaults
                # 写入默认配置文件，便于用户自定义
                self.save_config()
        except Exception:
            self.config = defaults

    def save_config(self):
        """写入配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def apply_last_view(self):
        """应用上次保存的视图状态"""
        state = self.config.get('last_state')
        if not state:
            return
        self.zoom = float(state.get('zoom', self.zoom))
        self.offset_x = int(state.get('offset_x', self.offset_x))
        self.offset_y = int(state.get('offset_y', self.offset_y))
        self.zoom_spin.setValue(int(self.zoom * 100))

    def save_last_state(self):
        """保存当前视图位置与缩放"""
        if not self.config.get('persist', {}).get('remember_last_view'):
            return
        self.config['last_state'] = {
            'zoom': self.zoom,
            'offset_x': self.offset_x,
            'offset_y': self.offset_y
        }
        # 保存当前打开的地图名字
        if self.current_map_name:
            self.config['last_map'] = self.current_map_name
        
        self.save_config()

    def closeEvent(self, event):
        """窗口关闭时保存状态"""
        self.save_last_state()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    editor = MapEditorQt()
    editor.show()
    
    # 尝试加载默认地图
    editor.load_map()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
