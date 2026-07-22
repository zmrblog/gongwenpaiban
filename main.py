# -*- coding: utf-8 -*-
"""
公文排版工具 - GUI 主程序
参考 gongwen.html 布局重写，使用 PyQt5
符合 GB/T 9704 标准
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QLineEdit, QComboBox,
    QDoubleSpinBox, QCheckBox, QGridLayout, QGroupBox,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

import gongwen_core as core


VERSION = "v0.1.1"


# ============================================================
# 设置面板（平铺展开，无弹窗）
# ============================================================

class SettingsPanel(QWidget):
    """设置面板 - 所有设置项平铺展开在主页面"""

    configChanged = pyqtSignal()

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._widgets = {}
        self._build_ui()
        self._load_config()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(16)

        # 页面边距
        layout.addWidget(self._create_margins_section())
        # 标题设置
        layout.addWidget(self._create_title_section())
        # 正文设置
        layout.addWidget(self._create_body_section())
        # 高级设置
        layout.addWidget(self._create_advanced_section())
        # 特殊选项
        layout.addWidget(self._create_special_section())
        # 版头设置
        layout.addWidget(self._create_header_section())
        # 版记设置
        layout.addWidget(self._create_footer_section())
        # 页码设置
        layout.addWidget(self._create_page_number_section())

        layout.addStretch()

    def _create_section_title(self, text):
        label = QLabel(text)
        label.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #374151; "
            "border-bottom: 1px solid #f3f4f6; padding-bottom: 6px; "
            "margin-bottom: 10px;"
        )
        return label

    def _create_margins_section(self):
        group = self._create_group_box("页面边距")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 20, 16, 16)

        grid = QGridLayout()
        grid.setSpacing(10)

        margins = ['top', 'bottom', 'left', 'right', 'footer']
        labels = ['上边距', '下边距', '左边距', '右边距', '页脚距']
        for i, (key, label_text) in enumerate(zip(margins, labels)):
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 12px; color: #6b7280;")
            grid.addWidget(lbl, i // 3, i % 3 * 2)

            spin = QDoubleSpinBox()
            spin.setRange(0, 10)
            spin.setSingleStep(0.1)
            spin.setDecimals(2)
            spin.setStyleSheet(
                "QDoubleSpinBox { padding: 6px 8px; border: 1px solid #d1d5db; "
                "border-radius: 6px; font-size: 13px; }"
            )
            spin.valueChanged.connect(self._on_changed)
            grid.addWidget(spin, i // 3, i % 3 * 2 + 1)
            self._widgets[f'margin_{key}'] = spin

        layout.addLayout(grid)
        return group

    def _create_title_section(self):
        group = self._create_group_box("公文标题")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 20, 16, 16)

        grid = QGridLayout()
        grid.setSpacing(10)

        lbl = QLabel("中文字体")
        lbl.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl, 0, 0)
        combo = self._create_font_combo(core.CHINESE_FONTS)
        grid.addWidget(combo, 0, 1)
        self._widgets['title_font'] = combo

        lbl2 = QLabel("字号")
        lbl2.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl2, 1, 0)
        size_combo = QComboBox()
        for size in core.FONT_SIZES:
            name = core.FONT_SIZE_NAMES.get(size, str(size))
            size_combo.addItem(f"{size}（{name}）", size)
        size_combo.setStyleSheet(
            "QComboBox { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        size_combo.currentIndexChanged.connect(self._on_changed)
        grid.addWidget(size_combo, 1, 1)
        self._widgets['title_size'] = size_combo

        lbl3 = QLabel("行距")
        lbl3.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl3, 2, 0)
        spacing_combo = QComboBox()
        for sp in core.LINE_SPACINGS:
            spacing_combo.addItem(str(sp), sp)
        spacing_combo.setStyleSheet(
            "QComboBox { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        spacing_combo.currentIndexChanged.connect(self._on_changed)
        grid.addWidget(spacing_combo, 2, 1)
        self._widgets['title_spacing'] = spacing_combo

        layout.addLayout(grid)
        return group

    def _create_body_section(self):
        group = self._create_group_box("正文格式")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 20, 16, 16)

        grid = QGridLayout()
        grid.setSpacing(10)

        lbl = QLabel("中文字体")
        lbl.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl, 0, 0)
        combo = self._create_font_combo(core.CHINESE_FONTS)
        grid.addWidget(combo, 0, 1)
        self._widgets['body_font'] = combo

        lbl2 = QLabel("英数字体")
        lbl2.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl2, 1, 0)
        combo2 = self._create_font_combo(core.ASCII_FONTS)
        grid.addWidget(combo2, 1, 1)
        self._widgets['body_ascii_font'] = combo2

        lbl3 = QLabel("字号")
        lbl3.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl3, 2, 0)
        size_combo = QComboBox()
        for size in core.FONT_SIZES:
            name = core.FONT_SIZE_NAMES.get(size, str(size))
            size_combo.addItem(f"{size}（{name}）", size)
        size_combo.setStyleSheet(
            "QComboBox { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        size_combo.currentIndexChanged.connect(self._on_changed)
        grid.addWidget(size_combo, 2, 1)
        self._widgets['body_size'] = size_combo

        lbl4 = QLabel("行距")
        lbl4.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl4, 3, 0)
        spacing_combo = QComboBox()
        for sp in core.LINE_SPACINGS:
            spacing_combo.addItem(str(sp), sp)
        spacing_combo.setStyleSheet(
            "QComboBox { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        spacing_combo.currentIndexChanged.connect(self._on_changed)
        grid.addWidget(spacing_combo, 3, 1)
        self._widgets['body_spacing'] = spacing_combo

        lbl5 = QLabel("首行缩进")
        lbl5.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl5, 4, 0)
        indent_combo = QComboBox()
        for val, name in core.INDENTS:
            indent_combo.addItem(name, val)
        indent_combo.setStyleSheet(
            "QComboBox { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        indent_combo.currentIndexChanged.connect(self._on_changed)
        grid.addWidget(indent_combo, 4, 1)
        self._widgets['body_indent'] = indent_combo

        hint = QLabel("正文行距和首行缩进同时应用于三级标题、四级标题、附件说明和成文日期")
        hint.setStyleSheet("font-size: 12px; color: #9ca3af; margin-top: 6px;")
        hint.setWordWrap(True)
        layout.addLayout(grid)
        layout.addWidget(hint)
        return group

    def _create_advanced_section(self):
        group = self._create_group_box("高级设置（标题字体）")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 20, 16, 16)

        hint = QLabel("一级、二级、三级标题统一在此配置中文字体、英数字体和字号")
        hint.setStyleSheet("font-size: 12px; color: #9ca3af;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        for heading_key, heading_label in [('h1', '一级标题'), ('h2', '二级标题'), ('h3', '三级标题')]:
            sub_group = self._create_group_box(heading_label)
            sub_layout = QGridLayout(sub_group)
            sub_layout.setSpacing(8)
            sub_layout.setContentsMargins(12, 16, 12, 12)

            lbl = QLabel("中文字体")
            lbl.setStyleSheet("font-size: 12px; color: #6b7280;")
            sub_layout.addWidget(lbl, 0, 0)
            combo = self._create_font_combo(core.CHINESE_FONTS)
            sub_layout.addWidget(combo, 0, 1)
            self._widgets[f'{heading_key}_font'] = combo

            lbl2 = QLabel("英数字体")
            lbl2.setStyleSheet("font-size: 12px; color: #6b7280;")
            sub_layout.addWidget(lbl2, 1, 0)
            combo2 = self._create_font_combo(core.ASCII_FONTS)
            sub_layout.addWidget(combo2, 1, 1)
            self._widgets[f'{heading_key}_ascii_font'] = combo2

            lbl3 = QLabel("字号")
            lbl3.setStyleSheet("font-size: 12px; color: #6b7280;")
            sub_layout.addWidget(lbl3, 2, 0)
            size_combo = QComboBox()
            for size in core.FONT_SIZES:
                name = core.FONT_SIZE_NAMES.get(size, str(size))
                size_combo.addItem(f"{size}（{name}）", size)
            size_combo.setStyleSheet(
                "QComboBox { padding: 6px 8px; border: 1px solid #d1d5db; "
                "border-radius: 6px; font-size: 13px; }"
            )
            size_combo.currentIndexChanged.connect(self._on_changed)
            sub_layout.addWidget(size_combo, 2, 1)
            self._widgets[f'{heading_key}_size'] = size_combo

            layout.addWidget(sub_group)

        return group

    def _create_special_section(self):
        group = self._create_group_box("特殊选项")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 20, 16, 16)

        cb1 = QCheckBox("正文段落首句加粗")
        cb1.setStyleSheet("font-size: 13px; color: #374151;")
        cb1.stateChanged.connect(self._on_changed)
        layout.addWidget(cb1)
        self._widgets['bold_first_sentence'] = cb1

        cb2 = QCheckBox("三级小标题加粗")
        cb2.setStyleSheet("font-size: 13px; color: #374151;")
        cb2.stateChanged.connect(self._on_changed)
        layout.addWidget(cb2)
        self._widgets['bold_heading3'] = cb2

        cb3 = QCheckBox("加盖印章")
        cb3.setStyleSheet("font-size: 13px; color: #374151;")
        cb3.stateChanged.connect(self._on_changed)
        layout.addWidget(cb3)
        self._widgets['has_stamp'] = cb3

        return group

    def _create_header_section(self):
        group = self._create_group_box("版头与版记 - 版头")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 20, 16, 16)

        cb = QCheckBox("启用版头")
        cb.setStyleSheet("font-size: 13px; color: #374151;")
        cb.stateChanged.connect(self._on_changed)
        layout.addWidget(cb)
        self._widgets['header_enabled'] = cb

        grid = QGridLayout()
        grid.setSpacing(10)

        lbl1 = QLabel("发文机关标志")
        lbl1.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl1, 0, 0)
        le1 = QLineEdit()
        le1.setPlaceholderText("如：国务院办公厅")
        le1.setStyleSheet(
            "QLineEdit { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        le1.textChanged.connect(self._on_changed)
        grid.addWidget(le1, 0, 1)
        self._widgets['header_org_name'] = le1

        lbl2 = QLabel("发文字号")
        lbl2.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl2, 1, 0)
        le2 = QLineEdit()
        le2.setPlaceholderText("如：国办发〔2024〕1号")
        le2.setStyleSheet(
            "QLineEdit { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        le2.textChanged.connect(self._on_changed)
        grid.addWidget(le2, 1, 1)
        self._widgets['header_doc_number'] = le2

        lbl3 = QLabel("签发人")
        lbl3.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl3, 2, 0)
        le3 = QLineEdit()
        le3.setPlaceholderText("选填，上行文使用")
        le3.setStyleSheet(
            "QLineEdit { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        le3.textChanged.connect(self._on_changed)
        grid.addWidget(le3, 2, 1)
        self._widgets['header_signer'] = le3

        layout.addLayout(grid)
        return group

    def _create_footer_section(self):
        group = self._create_group_box("版头与版记 - 版记")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 20, 16, 16)

        cb = QCheckBox("启用版记")
        cb.setStyleSheet("font-size: 13px; color: #374151;")
        cb.stateChanged.connect(self._on_changed)
        layout.addWidget(cb)
        self._widgets['footer_enabled'] = cb

        grid = QGridLayout()
        grid.setSpacing(10)

        lbl1 = QLabel("抄送机关")
        lbl1.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl1, 0, 0)
        le1 = QLineEdit()
        le1.setStyleSheet(
            "QLineEdit { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        le1.textChanged.connect(self._on_changed)
        grid.addWidget(le1, 0, 1)
        self._widgets['footer_cc'] = le1

        lbl2 = QLabel("印发机关")
        lbl2.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl2, 1, 0)
        le2 = QLineEdit()
        le2.setStyleSheet(
            "QLineEdit { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        le2.textChanged.connect(self._on_changed)
        grid.addWidget(le2, 1, 1)
        self._widgets['footer_printer'] = le2

        lbl3 = QLabel("印发日期")
        lbl3.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl3, 2, 0)
        le3 = QLineEdit()
        le3.setPlaceholderText("如：2024年1月1日")
        le3.setStyleSheet(
            "QLineEdit { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        le3.textChanged.connect(self._on_changed)
        grid.addWidget(le3, 2, 1)
        self._widgets['footer_print_date'] = le3

        layout.addLayout(grid)
        return group

    def _create_page_number_section(self):
        group = self._create_group_box("页码")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 20, 16, 16)

        cb = QCheckBox("添加页码")
        cb.setStyleSheet("font-size: 13px; color: #374151;")
        cb.stateChanged.connect(self._on_changed)
        layout.addWidget(cb)
        self._widgets['show_page_number'] = cb

        grid = QGridLayout()
        grid.setSpacing(10)

        lbl1 = QLabel("页码字体")
        lbl1.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl1, 0, 0)
        combo1 = QComboBox()
        combo1.addItem("宋体", "宋体")
        combo1.addItem("Times New Roman", "Times New Roman")
        combo1.setStyleSheet(
            "QComboBox { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        combo1.currentIndexChanged.connect(self._on_changed)
        grid.addWidget(combo1, 0, 1)
        self._widgets['page_number_font'] = combo1

        lbl2 = QLabel("页码样式")
        lbl2.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl2, 1, 0)
        combo2 = QComboBox()
        for val, name in core.PAGE_NUMBER_STYLES:
            combo2.addItem(name, val)
        combo2.setStyleSheet(
            "QComboBox { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        combo2.currentIndexChanged.connect(self._on_changed)
        grid.addWidget(combo2, 1, 1)
        self._widgets['page_number_style'] = combo2

        layout.addLayout(grid)
        return group

    def _create_group_box(self, title):
        group = QGroupBox(title)
        group.setStyleSheet(
            "QGroupBox { background: #fff; border: 1px solid #e5e7eb; "
            "border-radius: 8px; margin-top: 14px; font-size: 14px; "
            "font-weight: 600; color: #374151; padding-top: 8px; }"
            "QGroupBox::title { subcontrol-origin: margin; "
            "subcontrol-position: top left; left: 16px; padding: 0 8px; "
            "background: #fff; }"
        )
        return group

    def _create_font_combo(self, fonts):
        combo = QComboBox()
        combo.setEditable(True)
        for label, value in fonts:
            combo.addItem(label, value)
        combo.setStyleSheet(
            "QComboBox { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        combo.currentIndexChanged.connect(self._on_changed)
        combo.editTextChanged.connect(self._on_changed)
        return combo

    def _on_changed(self):
        """设置变化时发出信号"""
        self.configChanged.emit()

    def _load_config(self):
        cfg = self.config

        # 边距
        self._widgets['margin_top'].setValue(cfg['margins']['top'])
        self._widgets['margin_bottom'].setValue(cfg['margins']['bottom'])
        self._widgets['margin_left'].setValue(cfg['margins']['left'])
        self._widgets['margin_right'].setValue(cfg['margins']['right'])
        self._widgets['margin_footer'].setValue(cfg['margins'].get('footer', 2.5))

        # 标题
        self._set_combo_by_value(self._widgets['title_font'], cfg['title']['fontFamily'])
        self._set_combo_by_data(self._widgets['title_size'], cfg['title']['fontSize'])
        self._set_combo_by_data(self._widgets['title_spacing'], cfg['title']['lineSpacing'])

        # 正文
        self._set_combo_by_value(self._widgets['body_font'], cfg['body']['fontFamily'])
        self._set_combo_by_value(self._widgets['body_ascii_font'], cfg['body']['asciiFontFamily'])
        self._set_combo_by_data(self._widgets['body_size'], cfg['body']['fontSize'])
        self._set_combo_by_data(self._widgets['body_spacing'], cfg['body']['lineSpacing'])
        self._set_combo_by_data(self._widgets['body_indent'], cfg['body']['firstLineIndent'])

        # 高级
        for hkey in ['h1', 'h2', 'h3']:
            h = cfg['advanced'][hkey]
            self._set_combo_by_value(self._widgets[f'{hkey}_font'], h['fontFamily'])
            self._set_combo_by_value(self._widgets[f'{hkey}_ascii_font'], h['asciiFontFamily'])
            self._set_combo_by_data(self._widgets[f'{hkey}_size'], h['fontSize'])

        # 特殊选项
        self._widgets['bold_first_sentence'].setChecked(cfg['specialOptions']['boldFirstSentence'])
        self._widgets['bold_heading3'].setChecked(cfg['specialOptions']['boldHeading3'])
        self._widgets['has_stamp'].setChecked(cfg['specialOptions']['hasStamp'])

        # 版头
        self._widgets['header_enabled'].setChecked(cfg['header']['enabled'])
        self._widgets['header_org_name'].setText(cfg['header']['orgName'])
        self._widgets['header_doc_number'].setText(cfg['header']['docNumber'])
        self._widgets['header_signer'].setText(cfg['header']['signer'])

        # 版记
        self._widgets['footer_enabled'].setChecked(cfg['footerNote']['enabled'])
        self._widgets['footer_cc'].setText(cfg['footerNote']['cc'])
        self._widgets['footer_printer'].setText(cfg['footerNote']['printer'])
        self._widgets['footer_print_date'].setText(cfg['footerNote']['printDate'])

        # 页码
        self._widgets['show_page_number'].setChecked(cfg['specialOptions']['showPageNumber'])
        self._set_combo_by_value(self._widgets['page_number_font'], cfg['specialOptions']['pageNumberFont'])
        self._set_combo_by_data(self._widgets['page_number_style'], cfg['specialOptions']['pageNumberStyle'])

    def _set_combo_by_value(self, combo, value):
        idx = combo.findData(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        else:
            combo.setEditText(value)

    def _set_combo_by_data(self, combo, data):
        idx = combo.findData(data)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def reset_to_default(self):
        self.config = core.normalize_config(core.get_default_config())
        self._load_config()

    def get_config(self):
        cfg = core.get_default_config()

        # 边距
        cfg['margins']['top'] = self._widgets['margin_top'].value()
        cfg['margins']['bottom'] = self._widgets['margin_bottom'].value()
        cfg['margins']['left'] = self._widgets['margin_left'].value()
        cfg['margins']['right'] = self._widgets['margin_right'].value()
        cfg['margins']['footer'] = self._widgets['margin_footer'].value()

        # 标题
        cfg['title']['fontFamily'] = self._widgets['title_font'].currentText()
        cfg['title']['fontSize'] = self._widgets['title_size'].currentData()
        cfg['title']['lineSpacing'] = self._widgets['title_spacing'].currentData()

        # 正文
        cfg['body']['fontFamily'] = self._widgets['body_font'].currentText()
        cfg['body']['asciiFontFamily'] = self._widgets['body_ascii_font'].currentText() or 'Times New Roman'
        cfg['body']['fontSize'] = self._widgets['body_size'].currentData()
        cfg['body']['lineSpacing'] = self._widgets['body_spacing'].currentData()
        cfg['body']['firstLineIndent'] = self._widgets['body_indent'].currentData()

        # 高级
        for hkey in ['h1', 'h2', 'h3']:
            cfg['advanced'][hkey]['fontFamily'] = self._widgets[f'{hkey}_font'].currentText()
            cfg['advanced'][hkey]['asciiFontFamily'] = self._widgets[f'{hkey}_ascii_font'].currentText() or 'Times New Roman'
            cfg['advanced'][hkey]['fontSize'] = self._widgets[f'{hkey}_size'].currentData()

        # 特殊选项
        cfg['specialOptions']['boldFirstSentence'] = self._widgets['bold_first_sentence'].isChecked()
        cfg['specialOptions']['boldHeading3'] = self._widgets['bold_heading3'].isChecked()
        cfg['specialOptions']['hasStamp'] = self._widgets['has_stamp'].isChecked()

        # 版头
        cfg['header']['enabled'] = self._widgets['header_enabled'].isChecked()
        cfg['header']['orgName'] = self._widgets['header_org_name'].text()
        cfg['header']['docNumber'] = self._widgets['header_doc_number'].text()
        cfg['header']['signer'] = self._widgets['header_signer'].text()

        # 版记
        cfg['footerNote']['enabled'] = self._widgets['footer_enabled'].isChecked()
        cfg['footerNote']['cc'] = self._widgets['footer_cc'].text()
        cfg['footerNote']['printer'] = self._widgets['footer_printer'].text()
        cfg['footerNote']['printDate'] = self._widgets['footer_print_date'].text()

        # 页码
        cfg['specialOptions']['showPageNumber'] = self._widgets['show_page_number'].isChecked()
        cfg['specialOptions']['pageNumberFont'] = self._widgets['page_number_font'].currentText()
        cfg['specialOptions']['pageNumberStyle'] = self._widgets['page_number_style'].currentData()

        return core.normalize_config(cfg)


# ============================================================
# 主窗口
# ============================================================

class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.config = core.load_config()
        self.imported_text = ''
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle(f"公文排版工具 {VERSION}")
        self.setMinimumSize(900, 700)

        # 设置图标
        self._set_window_icon()

        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部工具栏（导入/清空/导出）
        main_layout.addWidget(self._build_toolbar())

        # 导入状态提示
        self.status_label = QLabel("未导入文件")
        self.status_label.setStyleSheet(
            "font-size: 13px; color: #6b7280; padding: 8px 20px; "
            "background: #fafafa; border-bottom: 1px solid #e5e7eb;"
        )
        main_layout.addWidget(self.status_label)

        # 下方：设置面板（可滚动）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #f9fafb; }")

        self.settings_panel = SettingsPanel(self.config)
        self.settings_panel.configChanged.connect(self._on_config_changed)
        scroll.setWidget(self.settings_panel)

        main_layout.addWidget(scroll, 1)

        # 应用整体样式
        self.setStyleSheet("QMainWindow { background: #fff; }")

        self._update_buttons_state()

    def _set_window_icon(self):
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass

    def _build_toolbar(self):
        toolbar = QFrame()
        toolbar.setFixedHeight(56)
        toolbar.setStyleSheet(
            "QFrame { background: #fff; border-bottom: 1px solid #e5e7eb; }"
        )

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        # 左侧：标题
        left = QHBoxLayout()
        left.setSpacing(10)

        title = QLabel("公文排版工具")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #111827;")
        left.addWidget(title)

        version_label = QLabel(VERSION)
        version_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #64748b;")
        left.addWidget(version_label)

        layout.addLayout(left)
        layout.addStretch()

        # 右侧：按钮
        right = QHBoxLayout()
        right.setSpacing(12)

        # 恢复默认按钮
        btn_reset = QPushButton("恢复默认")
        btn_reset.setStyleSheet(
            "QPushButton { background: #f3f4f6; color: #374151; border: none; "
            "border-radius: 6px; padding: 8px 16px; font-size: 14px; "
            "font-weight: 500; }"
            "QPushButton:hover { background: #e5e7eb; }"
        )
        btn_reset.clicked.connect(self._reset_config)
        right.addWidget(btn_reset)

        # 导入按钮
        btn_import = QPushButton("导入文件")
        btn_import.setStyleSheet(
            "QPushButton { background: #eff6ff; color: #2563eb; border: none; "
            "border-radius: 6px; padding: 8px 16px; font-size: 14px; "
            "font-weight: 500; }"
            "QPushButton:hover { background: #dbeafe; }"
        )
        btn_import.clicked.connect(self._import_file_dialog)
        right.addWidget(btn_import)

        # 清空按钮
        self.btn_clear = QPushButton("清空")
        self.btn_clear.setStyleSheet(
            "QPushButton { background: #f3f4f6; color: #374151; border: none; "
            "border-radius: 6px; padding: 8px 16px; font-size: 14px; "
            "font-weight: 500; }"
            "QPushButton:hover { background: #e5e7eb; }"
            "QPushButton:disabled { background: #f3f4f6; color: #9ca3af; }"
        )
        self.btn_clear.clicked.connect(self._clear_content)
        right.addWidget(self.btn_clear)

        # 导出按钮
        self.btn_export = QPushButton("导出 Word")
        self.btn_export.setStyleSheet(
            "QPushButton { background: #2563eb; color: #fff; border: none; "
            "border-radius: 6px; padding: 8px 16px; font-size: 14px; "
            "font-weight: 500; }"
            "QPushButton:hover { background: #1d4ed8; }"
            "QPushButton:disabled { background: #93c5fd; color: #fff; }"
        )
        self.btn_export.clicked.connect(self._export_word)
        right.addWidget(self.btn_export)

        layout.addLayout(right)
        return toolbar

    def _update_buttons_state(self):
        has_text = bool(self.imported_text.strip())
        self.btn_clear.setEnabled(has_text)
        self.btn_export.setEnabled(has_text)

    def _on_config_changed(self):
        """设置变化时实时保存配置"""
        self.config = self.settings_panel.get_config()
        core.save_config(self.config)

    def _reset_config(self):
        reply = QMessageBox.question(
            self, "确认恢复默认",
            "确定要将所有设置恢复为默认值吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.settings_panel.reset_to_default()
            self.config = self.settings_panel.get_config()
            core.save_config(self.config)

    def _import_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入文件", "",
            "Word 文档 (*.docx);;文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            self.import_file(file_path)

    def import_file(self, file_path):
        try:
            text = core.import_file(file_path)
            self.imported_text = text
            filename = os.path.basename(file_path)
            self.status_label.setText(f"已导入：{filename}（{len([l for l in text.split(chr(10)) if l.strip()])} 段）")
            self.status_label.setStyleSheet(
                "font-size: 13px; color: #059669; padding: 8px 20px; "
                "background: #ecfdf5; border-bottom: 1px solid #e5e7eb;"
            )
            self._update_buttons_state()
        except Exception as e:
            QMessageBox.critical(self, "文件导入失败", str(e))

    def _clear_content(self):
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空已导入的内容吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.imported_text = ''
            self.status_label.setText("未导入文件")
            self.status_label.setStyleSheet(
                "font-size: 13px; color: #6b7280; padding: 8px 20px; "
                "background: #fafafa; border-bottom: 1px solid #e5e7eb;"
            )
            self._update_buttons_state()

    def _export_word(self):
        if not self.imported_text.strip():
            return

        text = self.imported_text

        # 默认文件名（从第一行获取标题 + 版本号）
        default_name = f"公文_{VERSION}.docx"
        first_line = text.strip().split('\n')[0].strip()
        if first_line:
            default_name = f"{first_line}_{VERSION}.docx"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出 Word", default_name,
            "Word 文档 (*.docx)"
        )
        if not file_path:
            return

        try:
            # 规范化文本
            normalized, count = core.normalize_text(text)

            # 解析文档
            ast = core.parse_document(normalized)

            # 导出
            core.export_to_docx(ast, self.config, file_path)
            QMessageBox.information(self, "导出成功", f"文件已保存到：\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出失败：\n{str(e)}")

    def closeEvent(self, event):
        self.config = self.settings_panel.get_config()
        core.save_config(self.config)
        event.accept()


# ============================================================
# 入口
# ============================================================

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("公文排版工具")
    app.setApplicationVersion(VERSION)

    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
