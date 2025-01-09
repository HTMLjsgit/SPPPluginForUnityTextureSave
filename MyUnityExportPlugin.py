import substance_painter
import substance_painter.project
import substance_painter.export
import os
import logging
from PySide6.QtWidgets import QApplication, QMenu
from PySide6.QtGui import QAction


class UnityExportSubmenu(QMenu):
    def __init__(self, parent=None):
        super(UnityExportSubmenu, self).__init__("Unity用テクスチャ書き出し", parent)
        self.add_specular_action()
        self.add_metalic_action()

    def add_specular_action(self):
        action = QAction("Specularで出力", self)
        action.triggered.connect(self.export_specular)
        self.addAction(action)

    def add_metalic_action(self):
        action = QAction("Metalicで出力", self)
        action.triggered.connect(self.export_metalic)
        self.addAction(action)

    def export_specular(self):
        self.export_textures("Unity Universal Render Pipeline (Specular)")

    def export_metalic(self):
        self.export_textures("Unity Universal Render Pipeline (Metallic Standard)")

    def export_textures(self, preset_name):
        """
        指定されたプリセット名でテクスチャを出力する処理
        """
        project_path = substance_painter.project.file_path()
        if not project_path:
            print("プロジェクトが開かれていません。")
            return

        project_dir = os.path.dirname(project_path)
        unity_dir = os.path.join(project_dir, "Unity")

        if not os.path.exists(unity_dir):
            os.makedirs(unity_dir)
            print(f"Unityフォルダを作成しました: {unity_dir}")

        try:
            # エクスポートプリセットと出力パスを指定して設定を構築
            export_path = unity_dir
            export_preset = substance_painter.resource.ResourceID(
                context="starter_assets",
                name=preset_name
            )

            export_config = {
                "exportPath": export_path,
                "defaultExportPreset": export_preset.url(),
                "exportPresets": [{"name": "default", "maps": []}],
                "exportList": [],
                "exportParameters": [{"parameters": {"paddingAlgorithm": "infinite"}}],
                "exportShaderParams": False
            }

            export_list = export_config.get("exportList")
            for texture_set in substance_painter.textureset.all_texture_sets():
                export_list.append({"rootPath": texture_set.name()})

            # エクスポート設定を反映 (実際には書き出さない)
            export_result = substance_painter.export.export_project_textures(export_config)
            print(f"{preset_name}でテクスチャを出力しました。")
        except Exception as e:
            print(f"{preset_name}のエクスポートに失敗しました: {e}")
            return


def start_plugin():
    """
    プラグインがロードされたときに呼び出されるメインのエントリポイント
    """
    print("MyUnityExportPlugin がロードされました。")

    # Substance Painter のメインウィンドウを取得
    main_window = QApplication.instance().activeWindow()
    if not main_window:
        print("Substance Painter のメインウィンドウを取得できませんでした。")
        return

    # プラグイン用メニューを作成
    menu_bar = main_window.menuBar()
    plugins_menu = menu_bar.findChild(QMenu, "Plugins")
    if not plugins_menu:
        plugins_menu = menu_bar.addMenu("Plugins")
        plugins_menu.setObjectName("Plugins")

    # Unity用のサブメニューを追加
    unity_submenu = UnityExportSubmenu(parent=plugins_menu)
    plugins_menu.addMenu(unity_submenu)
    print("メニュー項目 'Unity用テクスチャ書き出し' を追加しました。")


def close_plugin():
    """
    プラグインがアンロードされたときに呼び出されるクリーンアップ処理
    """
    print("MyUnityExportPlugin がアンロードされました。")

    # Substance Painter のメインウィンドウを取得
    main_window = QApplication.instance().activeWindow()
    if not main_window:
        return

    # Plugins メニューからカスタムアクションを削除
    menu_bar = main_window.menuBar()
    plugins_menu = menu_bar.findChild(QMenu, "Plugins")
    if plugins_menu:
        for action in plugins_menu.actions():
            if action.text() == "Unity用テクスチャ書き出し":
                plugins_menu.removeAction(action)
                print("メニュー項目 'Unity用テクスチャ書き出し' を削除しました。")
