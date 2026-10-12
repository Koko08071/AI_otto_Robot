"""Rebuild Chinese file descriptions from reviewed labels and resource metadata."""
import argparse
import json
from pathlib import Path, PurePosixPath
import subprocess
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- FILE-INDEX:START -->'
END = '<!-- FILE-INDEX:END -->'
DIRECTORIES = {
    '': '项目入口、配置、安装启动与同事交接',
    'docs': '硬件通信、功能说明、维护文档和展示素材',
    'docs/media': 'README 中使用的实机视频、动图和编排器截图',
    'firmware': 'ESP32-S3 板端源码、分区和构建配置',
    'firmware/assets': 'storage 分区打包输入；不含完整表情动画分区',
    'firmware/components': 'ESP-IDF 本地组件与兼容层',
    'firmware/components/json': '旧 json 组件名到 espressif__cjson 的兼容层',
    'firmware/main': '主控启动、四舵机、屏幕、音频和无线协议',
    'gesture_recognition': '电脑摄像头识别、手势映射和指令发送',
    'tools': '模型下载、资源迁移、环境检查和便携包工具',
    'web': '网页服务、多轨组合、语音识别和机器人通信',
    'web/library': '已保存组合以及本地声音资源',
    'web/library/compositions': '按 UUID 保存的动作、表情、声音多轨组合',
    'web/static': '浏览器页面、样式、交互脚本和动作表情目录',
    'web/static/concepts': '彩色眼镜、面罩等概念表情预览',
    'web/static/official': '表情 GIF、缩略视频与候选素材',
    'web/static/official/thumbs': '表情资源卡片使用的 MP4 缩略预览',
    'web/static/official/_drafts': '待筛选的表情关键帧与打包候选稿',
    'web/static/official/_drafts/head_only': '头屏关键帧、过渡帧与视觉检查图',
    'web/static/official/_drafts/packer_named': '带循环时间标记的候选表情 GIF',
    'web/tests': '网页交互、协议、资源管理和识别接入测试',
    'web/library/audio': '随项目提供的演示音频与声音元数据',
    'models': 'GitHub Releases 手势模型下载说明',
    'voice-model': 'GitHub Releases 离线语音模型下载说明',
    'flash': '公开刷机文件、写入地址与镜像校验信息',
    'expressions': '机身动画分区构建输入',
    'expressions/official': '官方精简与头屏表情分区镜像',
    'licenses': '随项目保留的上游许可文本',
}
FILES = {
    '.gitignore': '忽略本地配置、模型、虚拟环境、音频、压缩包与构建产物，避免误提交',
    'config.example.json': '机器人 IP、设备 ID、蓝牙名、模型路径和网页端口的配置模板；复制为 config.local.json 后本地填写',
    'requirements.txt': '电脑端总依赖清单，包含网页服务、手势推理和音频处理',
    'setup.ps1': '创建仓库内 .venv、安装 Python 依赖并生成本地配置',
    'start.ps1': '使用 .venv 启动网页服务，适用于源码安装方式',
    'START.bat': '便携交接包双击启动入口，使用 runtime 内的 Python 并自动打开浏览器',
    'CHECK.bat': '便携交接包双击检查入口，报告缺少的依赖、模型或声音文件',
    'QUICKSTART.html': '无需编辑器即可在浏览器打开的同事图文快速指南',
    'HANDOFF.md': '同事交接详解：启动、Wi-Fi/BLE 连接、前端演示、故障排查与保存位置',
    'firmware/CMakeLists.txt': 'ESP-IDF 固件工程的顶层构建入口',
    'firmware/partitions.csv': 'Flash 分区布局：程序、存储和表情动画分区等',
    'firmware/dependencies.lock': 'ESP-IDF 组件版本与校验锁定文件，由组件管理器维护',
    'firmware/sdkconfig.defaults': '固件基础默认构建配置',
    'firmware/sdkconfig.demo': '演示固件的完整 ESP-IDF 配置快照',
    'firmware/sdkconfig.emote': '表情固件的完整 ESP-IDF 配置快照',
    'firmware/sdkconfig.emote.defaults': '表情播放器编译验证配置，默认禁用舵机输出，需核对候选引脚',
    'firmware/sdkconfig.network-camera.defaults': '带摄像头候选主板的联网默认配置，Wi-Fi 使用占位符，需实机核对',
    'firmware/sdkconfig.network-no-camera.defaults': '无摄像头主板的联网默认配置，Wi-Fi 使用占位符',
    'firmware/assets/README.txt': 'storage 与 emote_gen 分区资源边界及动作表情数据入口说明',
    'firmware/components/json/CMakeLists.txt': '将 json 组件依赖转接给 espressif__cjson',
    'firmware/main/CMakeLists.txt': '注册主控源文件、声明组件依赖并构建 storage 和动画资源分区',
    'firmware/main/Kconfig.projbuild': 'ESP-IDF menuconfig 中的主板、网络、表情与舵机配置项',
    'firmware/main/idf_component.yml': '主控组件所需的 ESP-IDF 第三方依赖声明',
    'firmware/main/board_profile.hpp': '主板类型和 GPIO 定义，包括舵机与屏幕引脚',
    'firmware/main/behavior_model.hpp': '动作帧、分段与组合程序等数据结构及辅助逻辑',
    'firmware/main/motion_types.hpp': '四轴舵机姿态 Pose 的类型定义',
    'gesture_recognition/recognize.py': '笔记本摄像头识别入口：YOLO 推理、类别显示、稳定判定及可选机器人响应',
    'gesture_recognition/video_worker.py': '网页视频推理子进程：接收图像帧并返回手势识别结果',
    'gesture_recognition/motion_bridge.py': '手势别名归一化、动作冷却、设备身份核验与 HTTP 指令发送',
    'gesture_recognition/robot_config.py': '统一读取本地配置和环境变量，按仓库位置解析模型路径',
    'gesture_recognition/gesture_actions.json': '手势对应动作与组合 ID：枪形侧倒、拳头后退、V 前进等',
    'gesture_recognition/test_recognize.py': '识别稳定判定、手势候选与确认逻辑测试',
    'gesture_recognition/test_motion_bridge.py': '手势映射、冷却、停止优先级、设备核验和组合调用测试',
    'gesture_recognition/test_video_input.py': '网页视频接入与识别流程的手势侧测试',
    'tools/download_models.py': '从本项目 GitHub Releases 下载并校验已验证的手势与语音模型',
    'tools/bootstrap_runtime.ps1': '源码包首次双击启动时下载、校验并安装 Windows 运行环境与模型',
    'release-assets.json': 'GitHub 发布附件名称、下载链接和 SHA256 校验清单',
    'web/tests/test_release_models.py': '发布模型包校验、按类型解压及路径越界拒绝测试',
    'flash/manifest.json': '公开固件构建来源、写入地址和每个镜像的 SHA256',
    'flash/bootloader.bin': '公开固件引导程序，写入 0x0',
    'flash/partition-table.bin': '16 MB Flash 分区表，写入 0x8000',
    'flash/otto_expression_motion.bin': '不含私人网络配置的公开主程序，写入 0x20000',
    'flash/storage.bin': 'storage SPIFFS 分区镜像，写入 0x700000',
    'flash/all_emote_assets.bin': '官方精简及 32 个头屏表情分区镜像，写入 0x800000',
    'expressions/official/all_emote_assets.bin': '固件 CMake 构建引用的动画分区输入，与 flash 中同名镜像一致',
    'licenses/OttoDIYLib-LICENSE.txt': 'OttoDIYLib 动作算法上游 GPL-3.0 许可文本',
    'licenses/esp-emote-gfx-LICENSE.txt': 'Espressif 表情图形组件上游许可文本',
    'tools/check_environment.py': '检查 Python 依赖、模型目录及组合引用的音频，不发送机器人动作',
    'tools/resources.py': '导入或导出声音和个人动作覆盖 ZIP，拒绝覆盖已有文件',
    'tools/windows_tts.ps1': '调用 Windows System.Speech 将中文文本合成为 WAV',
    'tools/build_handoff.py': '收集源码、模型、素材及 Python 运行库，生成 Windows 同事交接 ZIP',
    'tools/portable_launcher.py': '便携包启动器：选择空闲端口、启动服务、打开浏览器；支持无动作启动检查',
    'tools/update_file_index.py': '维护中文文件索引，按配置说明及组合、表情元数据生成各级 README 导航',
    'web/server.py': '本地 HTTP 服务入口，提供控制接口、资源目录及组合执行调度',
    'web/ble_link.py': 'BLE 扫描、连接、指令收发与断线恢复',
    'web/audio_tools.py': '查找系统 FFmpeg，或回退到 Python 依赖内置的 FFmpeg',
    'web/composer_store.py': '管理组合与音频的保存、校验、上传、合成、资源快照和触发词匹配',
    'web/video_input.py': '管理浏览器视频帧和识别子进程，将识别结果接入动作与组合调度',
    'web/voice_trigger.py': '离线语音转写、唤醒词与关键词监听，触发对应组合',
    'web/requirements.txt': '网页后端的基础 Python 依赖，根目录依赖清单会引用此文件',
    'web/static/actions.json': '可编辑的四舵机动作库，含角度、幅度、周期、时长和节奏变体',
    'web/static/expressions.json': '表情 ID、中文名称、预览、时长及分段循环元数据目录',
    'web/static/concepts.json': '彩色概念表情的名称、ID 和预览目录',
    'web/static/index.html': '机器人控制台页面：连接方式、舵机调试、动作和表情库',
    'web/static/app.js': '控制台交互：连接、状态刷新、动作编辑、舵机姿态与表情播放',
    'web/static/styles.css': '控制台基础布局、颜色、按钮和组件样式',
    'web/static/dashboard.css': '控制台面板和资源展示的补充样式',
    'web/static/composer.html': '多轨编排器页面：组合列表、资源库、预览、属性面板及时间轴',
    'web/static/composer.js': '多轨拖放、吸附、片段编辑、预览、保存、撤销及实机组合运行',
    'web/static/composer.css': '多轨编排器布局、轨道、片段与属性面板样式',
    'web/static/camera_labels.js': '控制台摄像头采集、视频帧上传及识别标签显示',
    'web/static/source_modes.js': '编排器语音/视频输入模式切换、摄像头上传和状态交互',
    'web/static/source_modes.css': '输入来源切换、识别状态和相关控件样式',
    'web/static/emo-preview.html': '彩色概念表情的独立展示预览页面',
    'web/static/concepts.css': '彩色概念表情预览页面样式',
    'web/tests/test_ble_recovery.py': '蓝牙断线、重连与错误处理测试',
    'web/tests/test_composer_store.py': '组合存储、声音上传、合成、资源引用和表情循环参数测试',
    'web/tests/test_composition_runner_sync.py': '组合动作、表情与声音调度同步测试',
    'web/tests/test_programs.py': '动作程序、角度边界、时长、协议容量、设备身份与表情预览测试',
    'web/tests/test_video_input.py': '网页视频帧会话、识别结果与控制接入测试',
    'web/tests/test_voice_trigger.py': '语音输入、唤醒词、关键词触发和识别模型接入测试',
    'web/tests/test_portable_runtime.py': '仓库相对路径、配置覆盖及非默认端口请求校验测试',
    'web/tests/test_composer_timeline.cjs': '时间轴片段吸附、位置冲突与移动规则测试',
    'web/tests/test_controls.cjs': '单次/连续动作按钮、状态恢复与停止切换测试',
    'web/tests/test_expression_loop.cjs': '表情循环时间及自定义表情元数据测试',
    'web/tests/test_motion_tempo.cjs': '动作节奏变体、默认节奏及前端选择控件测试',
    'docs/file-index.md': '全仓库逐目录、逐文件的中文用途总索引',
    'docs/media/robot-demo.mp4': '用户提供的原始实机展示视频，约 24 秒，保留原音轨',
    'docs/media/robot-demo-preview.gif': '实机视频的 6 秒无声节选，用于 README 自动播放',
    'docs/media/multitrack-composer.png': '多轨编排器真实截图，展示飞吻组合的动作与表情衔接',
}
MODULES = {
    'main': '固件启动入口与主任务', 'robot': '机器人模块初始化、状态和整体协调',
    'behavior': '动作程序解析、执行时序与分段调度', 'otto_motion': '四舵机 PWM 输出、姿态插值与周期摆动',
    'robot_face': '表情动画选择、播放与循环控制', 'board_display': '屏幕初始化、图像绘制与显示方向处理',
    'audio_input': '麦克风音频采集', 'audio_output': '扬声器音频播放',
    'protocol': '机器人控制协议、指令解析与状态响应',
    'wifi_http': 'Wi-Fi 初始化及 HTTP 控制服务', 'ble_control': 'BLE 广播、连接与控制指令通道',
}


def escape(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def describe(name, labels):
    if name in FILES:
        return FILES[name]
    path = PurePosixPath(name)
    if str(path.parent) == 'web/library/audio' and path.suffix in {'.wav', '.mp3', '.json'}:
        if path.suffix == '.json':
            item = json.loads((ROOT / name).read_text(encoding='utf-8'))
            return f'声音“{item["label"]}”的元数据：音频地址、时长、来源和校验值'
        metadata = ROOT / path.parent / (path.stem[:36] + '.json')
        label = json.loads(metadata.read_text(encoding='utf-8'))['label'] if metadata.exists() else path.stem
        return f'“{label}”的{path.suffix.upper()[1:]}音频；可能被已保存组合的资源快照引用'
    if path.name == 'README.md':
        return DIRECTORIES[str(path.parent) if str(path.parent) != '.' else ''] + '：使用说明与当前目录文件导航'
    if str(path.parent) == 'firmware/main' and path.stem in MODULES:
        return MODULES[path.stem] + ('的接口声明' if path.suffix == '.hpp' else '的实现')
    if str(path.parent) == 'web/library/compositions' and path.suffix == '.json':
        item = json.loads((ROOT / name).read_text(encoding='utf-8'))
        count = sum(len(t.get('clips', [])) for t in item.get('tracks', []))
        return f'组合“{item["name"]}”：{count} 个片段；保存各轨时间与资源快照，文件名为组合 UUID'
    if path.suffix == '.md':
        heading = next((x.lstrip('# ').strip() for x in (ROOT / name).read_text(encoding='utf-8').splitlines() if x.startswith('# ')), path.stem)
        return heading + '：文档说明'
    if path.name == '_pending_ids.json':
        return '候选表情的隔离/待确认 ID 清单，不代表已烧录到机身'
    if path.name == '_qa_seed_strip.png':
        return '关键帧候选素材拼图，供视觉检查与对照'
    if path.name.startswith('qa_shot_'):
        return '中弹表情视觉检查帧：' + path.stem.removeprefix('qa_shot_') + '（帧号或阶段标记）'
    if path.name.startswith('shot_die_f'):
        stages = {'shot_die_f1_smile':'微笑起始帧','shot_die_f2_hit':'命中反应帧','shot_die_f3_crack':'裂纹过渡帧','shot_die_f4_xx':'叉眼结束帧'}
        return '中弹表情分镜：' + stages[path.stem]
    if path.suffix in {'.png', '.jpg', '.gif', '.mp4'}:
        key = path.stem.split('_[')[0]
        for suffix in ['_head_01','_head','_loop_01','_intro_00','_intro_01','_intro_02']:
            if key.endswith(suffix):
                key = key[:-len(suffix)]
                break
        if key == 'smile_default':
            label = '默认微笑'
        else:
            label = labels.get(key)
        if not label:
            raise ValueError(f'Missing asset label: {name} ({key})')
        if 'packer_named' in path.parts:
            return f'“{label}”候选 GIF；文件名方括号记录循环区间，尚需打包校验'
        if 'head_only' in path.parts:
            phase = '循环关键帧' if '_loop_' in path.stem else '入场过渡帧' if '_intro_' in path.stem else '头屏关键帧'
            return f'“{label}”{phase}，用于表情制作，不是可直接烧录的动画包'
        if 'thumbs' in path.parts:
            return f'“{label}”的 MP4 缩略预览，供网页资源卡片使用'
        return f'“{label}”的 GIF 网页预览；机身播放仍需对应固件动画资源'
    raise ValueError(f'Missing file description: {name}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tracked-only', action='store_true', help='Index staged/tracked files without unrelated unfinished work')
    args = parser.parse_args()
    command = ['git', 'ls-files', '-z', '--cached']
    if not args.tracked_only:
        command += ['--others', '--exclude-standard']
    raw = subprocess.check_output(command, cwd=ROOT)
    files = {x for x in raw.decode('utf-8').split('\0') if x and (ROOT / x).is_file()}
    dirs = {''}
    for name in files:
        dirs.update(str(p) for p in PurePosixPath(name).parents if str(p) != '.')
    if dirs - DIRECTORIES.keys():
        raise ValueError(f'Unmapped directories: {dirs - DIRECTORIES.keys()}')
    files.update((d + '/' if d else '') + 'README.md' for d in dirs)
    files.add('docs/file-index.md')
    labels = {}
    for catalog in ['web/static/expressions.json', 'web/static/concepts.json']:
        for item in json.loads((ROOT / catalog).read_text(encoding='utf-8')):
            labels[item['id']] = item['label']
            if item.get('preview'):
                labels[PurePosixPath(item['preview']).stem] = item['label']
    descriptions = {name: describe(name, labels) for name in sorted(files)}
    sections = []
    for directory in sorted(dirs):
        prefix = directory + '/' if directory else ''
        rows = ['| 文件或子目录 | 用途说明 |', '|---|---|']
        children = sorted(d for d in dirs if d and str(PurePosixPath(d).parent) == (directory or '.'))
        for child in children:
            basename = PurePosixPath(child).name
            rows.append(f'| [{basename}/]({quote(basename)}/) | {DIRECTORIES[child]} |')
        direct = [f for f in sorted(files) if str(PurePosixPath(f).parent) == (directory or '.')]
        for name in direct:
            basename = PurePosixPath(name).name
            rows.append(f'| [{escape(basename)}]({quote(basename)}) | {escape(descriptions[name])} |')
        target = ROOT / prefix / 'README.md'
        original = target.read_text(encoding='utf-8') if target.exists() else '# ' + DIRECTORIES[directory] + '\n'
        if START in original:
            before, rest = original.split(START, 1)
            _, after = rest.split(END, 1)
        else:
            before, after = original.rstrip() + '\n\n', '\n'
        target.write_text(before + START + '\n## 当前目录逐项说明\n\n' + '\n'.join(rows) + '\n' + END + after, encoding='utf-8')
        sections.append(f'## {directory or "仓库根目录"}\n\n{DIRECTORIES[directory]}\n\n| 文件 | 用途说明 |\n|---|---|\n')
        for name in direct:
            sections.append(f'| [{escape(PurePosixPath(name).name)}](../{quote(name)}) | {escape(descriptions[name])} |\n')
        sections.append('\n')
    intro = '# 全部目录与文件用途索引\n\n'
    intro += f'本索引覆盖 {len(files)} 个源码、配置、文档与素材文件，按 {len(dirs)} 个目录分组。每级 README 也列出直属文件和子目录。\n\n'
    intro += 'GitHub 文件列表中间一列是最近一次提交说明，并非固定备注；后续修改会更新它。固定用途说明请查看本索引或所在目录 README。组合名和表情名来自项目实际 JSON 元数据。模型与运行环境通过 GitHub Releases 提供；音频及公开刷机文件随源码提供，密码配置不公开。\n\n'
    intro += '维护时运行 `python tools/update_file_index.py` 更新索引；新增代码文件需先在脚本中补充用途，新增素材需补充对应资源目录元数据。\n\n'
    (ROOT / 'docs/file-index.md').write_text(intro + ''.join(sections), encoding='utf-8')
    print(f'Indexed {len(files)} files in {len(dirs)} directories')


if __name__ == '__main__':
    main()
