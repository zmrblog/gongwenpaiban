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
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox,
    QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QTabWidget, QGridLayout, QGroupBox,
    QScrollArea, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor, QDragEnterEvent, QDropEvent

import gongwen_core as core


VERSION = "v0.1.4"


# ============================================================
# 设置对话框
# ============================================================

class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._widgets = {}
        self.setWindowTitle("设置")
        self.setModal(True)
        self.setMinimumWidth(640)
        self.setMinimumHeight(560)
        self._build_ui()
        self._load_config()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # 标题栏
        header = QHBoxLayout()
        title = QLabel("设置")
        title.setStyleSheet("font-size: 17px; font-weight: 600; color: #111827;")
        header.addWidget(title)
        header.addStretch()
        btn_close = QPushButton("×")
        btn_close.setFixedSize(32, 32)
        btn_close.setStyleSheet(
            "QPushButton { border: none; border-radius: 6px; "
            "font-size: 16px; color: #6b7280; }"
            "QPushButton:hover { background: #f3f4f6; color: #111827; }"
        )
        btn_close.clicked.connect(self.accept)
        header.addWidget(btn_close)
        layout.addLayout(header)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # 页面边距
        scroll_layout.addWidget(self._create_margins_section())
        # 标题设置
        scroll_layout.addWidget(self._create_title_section())
        # 正文设置
        scroll_layout.addWidget(self._create_body_section())
        # 高级设置
        scroll_layout.addWidget(self._create_advanced_section())
        # 特殊选项
        scroll_layout.addWidget(self._create_special_section())
        # 版头设置
        scroll_layout.addWidget(self._create_header_section())
        # 版记设置
        scroll_layout.addWidget(self._create_footer_section())
        # 页码设置
        scroll_layout.addWidget(self._create_page_number_section())

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # 底部按钮
        footer = QHBoxLayout()
        btn_reset = QPushButton("恢复默认")
        btn_reset.setStyleSheet(
            "QPushButton { background: #fef2f2; color: #dc2626; "
            "border: none; border-radius: 6px; padding: 7px 16px; "
            "font-size: 13px; font-weight: 500; }"
            "QPushButton:hover { background: #fee2e2; }"
        )
        btn_reset.clicked.connect(self._reset_to_default)
        footer.addWidget(btn_reset)
        footer.addStretch()
        btn_close2 = QPushButton("关闭")
        btn_close2.setStyleSheet(
            "QPushButton { background: #f3f4f6; color: #374151; "
            "border: none; border-radius: 6px; padding: 7px 16px; "
            "font-size: 13px; font-weight: 500; }"
            "QPushButton:hover { background: #e5e7eb; }"
        )
        btn_close2.clicked.connect(self.accept)
        footer.addWidget(btn_close2)
        layout.addLayout(footer)

    def _create_section_title(self, text):
        label = QLabel(text)
        label.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #374151; "
            "border-bottom: 1px solid #f3f4f6; padding-bottom: 6px; "
            "margin-bottom: 10px;"
        )
        return label

    def _create_margins_section(self):
        group = QGroupBox()
        group.setTitle("")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 10, 0, 10)

        layout.addWidget(self._create_section_title("页面边距"))

        grid = QGridLayout()
        grid.setSpacing(10)

        margins = ['top', 'bottom', 'left', 'right', 'footer']
        labels = ['上边距', '下边距', '左边距', '右边距', '页脚距']
        for i, (key, label_text) in enumerate(zip(margins, labels)):
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 12px; color: #6b7280;")
            grid.addWidget(lbl, i // 2, i % 2 * 2)

            spin = QDoubleSpinBox()
            spin.setRange(0, 10)
            spin.setSingleStep(0.1)
            spin.setDecimals(2)
            spin.setStyleSheet(
                "QDoubleSpinBox { padding: 6px 8px; border: 1px solid #d1d5db; "
                "border-radius: 6px; font-size: 13px; }"
            )
            grid.addWidget(spin, i // 2, i % 2 * 2 + 1)
            self._widgets[f'margin_{key}'] = spin

        layout.addLayout(grid)
        return group

    def _create_title_section(self):
        group = QGroupBox()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 10, 0, 10)

        layout.addWidget(self._create_section_title("公文标题"))

        grid = QGridLayout()
        grid.setSpacing(10)

        # 字体
        lbl = QLabel("中文字体")
        lbl.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl, 0, 0)
        combo = self._create_font_combo(core.CHINESE_FONTS)
        grid.addWidget(combo, 0, 1)
        self._widgets['title_font'] = combo

        # 字号
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
        grid.addWidget(size_combo, 1, 1)
        self._widgets['title_size'] = size_combo

        # 行距
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
        grid.addWidget(spacing_combo, 2, 1)
        self._widgets['title_spacing'] = spacing_combo

        layout.addLayout(grid)
        return group

    def _create_body_section(self):
        group = QGroupBox()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 10, 0, 10)

        layout.addWidget(self._create_section_title("正文格式"))

        grid = QGridLayout()
        grid.setSpacing(10)

        # 中文字体
        lbl = QLabel("中文字体")
        lbl.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl, 0, 0)
        combo = self._create_font_combo(core.CHINESE_FONTS)
        grid.addWidget(combo, 0, 1)
        self._widgets['body_font'] = combo

        # 英数字体
        lbl2 = QLabel("英数字体")
        lbl2.setStyleSheet("font-size: 12px; color: #6b7280;")
        grid.addWidget(lbl2, 1, 0)
        combo2 = self._create_font_combo(core.ASCII_FONTS)
        grid.addWidget(combo2, 1, 1)
        self._widgets['body_ascii_font'] = combo2

        # 字号
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
        grid.addWidget(size_combo, 2, 1)
        self._widgets['body_size'] = size_combo

        # 行距
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
        grid.addWidget(spacing_combo, 3, 1)
        self._widgets['body_spacing'] = spacing_combo

        # 首行缩进
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
        grid.addWidget(indent_combo, 4, 1)
        self._widgets['body_indent'] = indent_combo

        # 提示
        hint = QLabel("正文行距和首行缩进同时应用于三级标题、四级标题、附件说明和成文日期")
        hint.setStyleSheet("font-size: 12px; color: #9ca3af; margin-top: 6px;")
        hint.setWordWrap(True)
        layout.addLayout(grid)
        layout.addWidget(hint)
        return group

    def _create_advanced_section(self):
        group = QGroupBox()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 10, 0, 10)

        layout.addWidget(self._create_section_title("高级设置（标题字体）"))

        hint = QLabel("一级、二级、三级标题统一在此配置中文字体、英数字体和字号")
        hint.setStyleSheet("font-size: 12px; color: #9ca3af;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # 三列布局
        for heading_key, heading_label in [('h1', '一级标题'), ('h2', '二级标题'), ('h3', '三级标题')]:
            sub_group = QGroupBox(heading_label)
            sub_group.setStyleSheet(
                "QGroupBox { border: 1px solid #e5e7eb; border-radius: 8px; "
                "margin-top: 12px; padding-top: 8px; }"
                "QGroupBox::title { color: #374151; font-weight: 500; "
                "subcontrol-origin: margin; left: 10px; padding: 0 5px; }"
            )
            sub_layout = QGridLayout(sub_group)
            sub_layout.setSpacing(8)

            # 中文字体
            lbl = QLabel("中文字体")
            lbl.setStyleSheet("font-size: 12px; color: #6b7280;")
            sub_layout.addWidget(lbl, 0, 0)
            combo = self._create_font_combo(core.CHINESE_FONTS)
            sub_layout.addWidget(combo, 0, 1)
            self._widgets[f'{heading_key}_font'] = combo

            # 英数字体
            lbl2 = QLabel("英数字体")
            lbl2.setStyleSheet("font-size: 12px; color: #6b7280;")
            sub_layout.addWidget(lbl2, 1, 0)
            combo2 = self._create_font_combo(core.ASCII_FONTS)
            sub_layout.addWidget(combo2, 1, 1)
            self._widgets[f'{heading_key}_ascii_font'] = combo2

            # 字号
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
            sub_layout.addWidget(size_combo, 2, 1)
            self._widgets[f'{heading_key}_size'] = size_combo

            layout.addWidget(sub_group)

        return group

    def _create_special_section(self):
        group = QGroupBox()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 10, 0, 10)

        layout.addWidget(self._create_section_title("特殊选项"))

        # 正文段落首句加粗
        cb1 = QCheckBox("正文段落首句加粗")
        cb1.setStyleSheet("font-size: 13px; color: #374151;")
        layout.addWidget(cb1)
        self._widgets['bold_first_sentence'] = cb1

        # 三级小标题加粗
        cb2 = QCheckBox("三级小标题加粗")
        cb2.setStyleSheet("font-size: 13px; color: #374151;")
        layout.addWidget(cb2)
        self._widgets['bold_heading3'] = cb2

        # 加盖印章
        cb3 = QCheckBox("加盖印章")
        cb3.setStyleSheet("font-size: 13px; color: #374151;")
        layout.addWidget(cb3)
        self._widgets['has_stamp'] = cb3

        return group

    def _create_header_section(self):
        group = QGroupBox()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 10, 0, 10)

        layout.addWidget(self._create_section_title("版头与版记 - 版头"))

        # 启用版头
        cb = QCheckBox("启用版头")
        cb.setStyleSheet("font-size: 13px; color: #374151;")
        layout.addWidget(cb)
        self._widgets['header_enabled'] = cb

        # 发文机关标志
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
        grid.addWidget(le3, 2, 1)
        self._widgets['header_signer'] = le3

        layout.addLayout(grid)
        return group

    def _create_footer_section(self):
        group = QGroupBox()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 10, 0, 10)

        layout.addWidget(self._create_section_title("版头与版记 - 版记"))

        # 启用版记
        cb = QCheckBox("启用版记")
        cb.setStyleSheet("font-size: 13px; color: #374151;")
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
        grid.addWidget(le3, 2, 1)
        self._widgets['footer_print_date'] = le3

        layout.addLayout(grid)
        return group

    def _create_page_number_section(self):
        group = QGroupBox()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 10, 0, 10)

        layout.addWidget(self._create_section_title("页码"))

        # 启用页码
        cb = QCheckBox("添加页码")
        cb.setStyleSheet("font-size: 13px; color: #374151;")
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
        grid.addWidget(combo2, 1, 1)
        self._widgets['page_number_style'] = combo2

        layout.addLayout(grid)
        return group

    def _create_font_combo(self, fonts):
        """创建字体选择下拉框"""
        combo = QComboBox()
        combo.setEditable(True)
        for label, value in fonts:
            combo.addItem(label, value)
        combo.setStyleSheet(
            "QComboBox { padding: 6px 8px; border: 1px solid #d1d5db; "
            "border-radius: 6px; font-size: 13px; }"
        )
        return combo

    def _load_config(self):
        """将配置加载到控件"""
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
        """通过 value 设置下拉框选中项"""
        idx = combo.findData(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        else:
            combo.setEditText(value)

    def _set_combo_by_data(self, combo, data):
        """通过 data 设置下拉框选中项"""
        idx = combo.findData(data)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def _reset_to_default(self):
        """恢复默认配置"""
        self.config = core.normalize_config(core.get_default_config())
        self._load_config()

    def get_config(self):
        """从控件收集配置"""
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
# 编辑器面板
# ============================================================

class EditorPanel(QWidget):
    """编辑器面板（左侧）"""

    textChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 头部
        header = QFrame()
        header.setStyleSheet(
            "QFrame { background: #fff; border-bottom: 1px solid #e5e7eb; }"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)

        label = QLabel("正文")
        label.setStyleSheet("font-size: 15px; font-weight: 600; color: #1f2937;")
        header_layout.addWidget(label)

        hint = QLabel("首行自动识别为标题，后续自动识别各级标题")
        hint.setStyleSheet("font-size: 12px; color: #9ca3af;")
        header_layout.addWidget(hint)
        header_layout.addStretch()

        layout.addWidget(header)

        # 文本编辑区
        self.text_edit = QTextEdit()
        # 禁用编辑器的拖拽接收，让事件冒泡到主窗口统一处理文件导入
        self.text_edit.setAcceptDrops(False)
        self.text_edit.setPlaceholderText("粘贴公文正文 或 拖入文件")
        self.text_edit.setStyleSheet(
            "QTextEdit { border: none; background: #fafafa; "
            "font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif; "
            "font-size: 14px; line-height: 1.8; color: #374151; padding: 16px; }"
        )
        self.text_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.text_edit)

    def _on_text_changed(self):
        self.textChanged.emit(self.text_edit.toPlainText())

    def set_text(self, text):
        self.text_edit.setPlainText(text)

    def get_text(self):
        return self.text_edit.toPlainText()

    def clear(self):
        self.text_edit.clear()


# ============================================================
# 主窗口
# ============================================================

class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.config = core.load_config()
        self.saved_text = core.load_text()
        self.settings_dialog = None
        self._setup_autosave()
        self._build_ui()
        self._load_saved_content()

    def _build_ui(self):
        self.setWindowTitle(f"公文排版工具 {VERSION} - GB/T 9704")
        self.setMinimumSize(1024, 768)

        # 设置图标
        self._set_window_icon()

        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 工具栏
        main_layout.addWidget(self._build_toolbar())

        # 编辑器
        self.editor = EditorPanel()
        self.editor.textChanged.connect(self._on_text_changed)
        main_layout.addWidget(self.editor, 1)

        # 应用整体样式
        self.setStyleSheet(
            "QMainWindow { background: #fff; }"
        )

        # 启用主窗口拖拽接收（整个窗口任意位置均可拖入文件导入）
        self.setAcceptDrops(True)

        # 更新按钮状态（编辑器已创建）
        self._update_buttons_state()

    # 拖拽文件导入支持
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                ext = os.path.splitext(urls[0].toLocalFile())[1].lower()
                if ext in ('.docx', '.txt'):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ('.docx', '.txt'):
                self.import_file(file_path)
                event.acceptProposedAction()
                return
        event.ignore()

    def _set_window_icon(self):
        """设置窗口图标（公文风格红色图标）"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass

    def _build_toolbar(self):
        """构建工具栏"""
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

        version = QLabel(VERSION)
        version.setStyleSheet("font-size: 13px; font-weight: 600; color: #64748b;")
        left.addWidget(version)

        layout.addLayout(left)
        layout.addStretch()

        # 右侧：按钮
        right = QHBoxLayout()
        right.setSpacing(12)

        # 统计
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("font-size: 13px; color: #6b7280;")
        right.addWidget(self.stats_label)

        # 设置按钮
        btn_settings = QPushButton("⚙ 设置")
        btn_settings.setStyleSheet(
            "QPushButton { background: #f3f4f6; color: #374151; border: none; "
            "border-radius: 6px; padding: 8px 16px; font-size: 14px; "
            "font-weight: 500; }"
            "QPushButton:hover { background: #e5e7eb; }"
        )
        btn_settings.clicked.connect(self._open_settings)
        right.addWidget(btn_settings)

        # 导入按钮
        btn_import = QPushButton("导入文件")
        btn_import.setStyleSheet(
            "QPushButton { background: #eff6ff; color: #2563eb; border: none; "
            "border-radius: 6px; padding: 8px 16px; font-size: 14px; "
            "font-weight: 500; }"
            "QPushButton:hover { background: #dbeafe; }"
            "QPushButton:disabled { background: #f3f4f6; color: #9ca3af; }"
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

    def _load_saved_content(self):
        """加载保存的文本"""
        if self.saved_text:
            self.editor.set_text(self.saved_text)

    def _setup_autosave(self):
        """设置自动保存"""
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save_content)
        self._save_timer.setInterval(500)

    def _on_text_changed(self, text):
        """文本变化时更新状态"""
        self._update_buttons_state()
        self._update_stats(text)

        # 防抖保存
        self._save_timer.start()

    def _update_buttons_state(self):
        """更新按钮状态"""
        has_text = bool(self.editor.get_text().strip())
        self.btn_clear.setEnabled(has_text)
        self.btn_export.setEnabled(has_text)

    def _update_stats(self, text):
        """更新统计信息"""
        if not text.strip():
            self.stats_label.setText("")
            return
        lines = [l for l in text.split('\n') if l.strip()]
        self.stats_label.setText(f"{len(lines)} 段")

    def _save_content(self):
        """保存内容"""
        core.save_text(self.editor.get_text())

    def _open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec_() == QDialog.Accepted:
            self.config = dialog.get_config()
            core.save_config(self.config)

    def _import_file_dialog(self):
        """导入文件对话框"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入文件", "",
            "Word 文档 (*.docx);;文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            self.import_file(file_path)

    def import_file(self, file_path):
        """导入文件"""
        try:
            text = core.import_file(file_path)
            if self.editor.get_text().strip():
                reply = QMessageBox.question(
                    self, "确认导入",
                    "导入文件将覆盖当前内容，是否继续？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            self.editor.set_text(text)
            self._save_content()
            self._update_buttons_state()
            self._update_stats(text)
        except Exception as e:
            QMessageBox.critical(self, "文件导入失败", str(e))

    def _clear_content(self):
        """清空内容"""
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空所有内容吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.editor.clear()
            self._save_content()
            self._update_buttons_state()

    def _export_word(self):
        """导出 Word"""
        text = self.editor.get_text()
        if not text.strip():
            return

        # 默认文件名（带版本号）
        default_name = f"公文_{VERSION}.docx"
        # 尝试从第一行获取标题
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
        """关闭时保存"""
        self._save_content()
        core.save_config(self.config)
        event.accept()


# ============================================================
# 入口
# ============================================================

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("公文排版工具")
    app.setApplicationVersion(VERSION)

    # 设置默认字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
