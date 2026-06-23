import json
import os
from pathlib import Path


class MechanicalRunner:
    """负责封装 242+ PyMechanical 的批量特征识别与接触自动化接口。"""

    def __init__(self) -> None:
        # 中文说明：
        # 当前项目仍以 MAPDL 链路为主，这里新增的是独立的 Mechanical 能力层。
        # 为了不破坏现有 MVP，这里全部采用延迟导入和运行时检查。
        self.runtime_local_appdata = Path("runtime_data") / "localappdata"
        self.runtime_roaming_appdata = Path("runtime_data") / "appdata"
        self.runtime_mechanical_user_data = self.runtime_local_appdata / "Ansys" / "ansys_mechanical_core"
        self.runtime_tools_path_data = self.runtime_local_appdata / "Ansys" / "ansys_tools_path"
        self.default_workdir = Path("mechanical_workspace")

        # 中文说明：
        # 这里只保留 242+ 的能力方案，因为这是 PyMechanical 当前更稳定的范围。
        self.supported_versions = [242, 251, 252, 261, 271, 272]
        self.supported_contact_types = {
            "Bonded": "Bonded",
            "Frictional": "Frictional",
            "Frictionless": "Frictionless",
            "NoSeparation": "NoSeparation",
            "Rough": "Rough",
        }

    def get_environment_status(self) -> dict:
        """返回 PyMechanical 242+ 能力的环境状态。"""
        mechanical_exec, detected_version = self._find_mechanical_executable()
        pymechanical_importable, import_error = self._check_pymechanical_importable()

        return {
            "pymechanical_importable": pymechanical_importable,
            "pymechanical_import_error": import_error,
            "detected_mechanical_exec": str(mechanical_exec) if mechanical_exec else None,
            "detected_version": detected_version,
            "version_supported": detected_version in self.supported_versions if detected_version else False,
            "runtime_local_appdata": str(self.runtime_local_appdata.resolve()),
            "runtime_roaming_appdata": str(self.runtime_roaming_appdata.resolve()),
            "runtime_mechanical_user_data": str(self.runtime_mechanical_user_data.resolve()),
            "supported_versions": self.supported_versions,
            "message": self._build_status_message(
                pymechanical_importable=pymechanical_importable,
                mechanical_exec=mechanical_exec,
                detected_version=detected_version,
            ),
        }

    def get_capability_definition(self) -> dict:
        """返回 242+ Mechanical 批量特征识别与接触自动化方案。"""
        return {
            "success": True,
            "runner": "pymechanical",
            "target_versions": self.supported_versions,
            "recommended_strategy": "named_selection_pairing",
            "stable_capabilities": [
                "扫描现有 Named Selections",
                "扫描现有 Contact Regions",
                "按 Named Selection 前缀批量配对接触",
                "统一设置接触类型",
            ],
            "reserved_capabilities": [
                "按面类型创建特征型 Named Selections",
                "按圆柱面/平面等几何特征做规则识别",
                "按规则批量补全接触参数",
            ],
            "notes": [
                "第一版建议优先基于 Named Selection 做批量接触，这是最稳的工程路线。",
                "按几何特征直接识别面可以做，但建议作为第二阶段能力。",
                "接口已保留为 242+ 设计；在 241 环境下默认仅返回方案和脚本预览。",
            ],
        }

    def preview_batch_contact_plan(
        self,
        source_named_selection_prefix: str,
        target_named_selection_prefix: str,
        contact_type: str,
        contact_name_prefix: str = "AUTO_CONTACT_",
    ) -> dict:
        """预览按 Named Selection 前缀批量创建接触的方案。"""
        normalized_contact_type = self._normalize_contact_type(contact_type)

        return {
            "success": True,
            "mode": "preview_only",
            "strategy": "named_selection_pairing",
            "source_named_selection_prefix": source_named_selection_prefix,
            "target_named_selection_prefix": target_named_selection_prefix,
            "contact_type": normalized_contact_type,
            "contact_name_prefix": contact_name_prefix,
            "matching_rule": "把 source 前缀和 target 前缀后面的同名后缀视为同一特征对。",
            "generated_script_preview": self._build_named_selection_contact_script(
                source_named_selection_prefix=source_named_selection_prefix,
                target_named_selection_prefix=target_named_selection_prefix,
                contact_type=normalized_contact_type,
                contact_name_prefix=contact_name_prefix,
            ),
        }

    def execute_batch_contacts_by_named_selection(
        self,
        source_named_selection_prefix: str,
        target_named_selection_prefix: str,
        contact_type: str,
        contact_name_prefix: str = "AUTO_CONTACT_",
        launch_mechanical: bool = False,
        working_directory: str | None = None,
    ) -> dict:
        """执行基于 Named Selection 的批量接触创建。"""
        normalized_contact_type = self._normalize_contact_type(contact_type)

        # 中文说明：
        # 默认不真实启动 Mechanical，只保留接口和脚本。
        if not launch_mechanical:
            return self.preview_batch_contact_plan(
                source_named_selection_prefix=source_named_selection_prefix,
                target_named_selection_prefix=target_named_selection_prefix,
                contact_type=normalized_contact_type,
                contact_name_prefix=contact_name_prefix,
            )

        mechanical_exec, detected_version = self._find_mechanical_executable()
        if mechanical_exec is None:
            return {
                "success": False,
                "mode": "mechanical_not_found",
                "message": "未找到 242+ Mechanical 可执行文件，无法执行批量接触脚本。",
            }

        if detected_version not in self.supported_versions:
            return {
                "success": False,
                "mode": "mechanical_version_not_supported",
                "message": f"当前检测到的 Mechanical 版本为 {detected_version}，此接口仅为 242+ 设计。",
                "detected_mechanical_exec": str(mechanical_exec),
            }

        try:
            return self._run_named_selection_contact_script(
                mechanical_exec=mechanical_exec,
                source_named_selection_prefix=source_named_selection_prefix,
                target_named_selection_prefix=target_named_selection_prefix,
                contact_type=normalized_contact_type,
                contact_name_prefix=contact_name_prefix,
                working_directory=working_directory,
            )
        except Exception as exc:
            return {
                "success": False,
                "mode": "mechanical_execution_failed",
                "message": "PyMechanical 执行批量接触脚本失败。",
                "detail": str(exc),
                "detected_mechanical_exec": str(mechanical_exec),
                "detected_version": detected_version,
            }

    def _run_named_selection_contact_script(
        self,
        mechanical_exec: Path,
        source_named_selection_prefix: str,
        target_named_selection_prefix: str,
        contact_type: str,
        contact_name_prefix: str,
        working_directory: str | None,
    ) -> dict:
        """在 242+ Mechanical 中执行批量接触脚本。"""
        self._prepare_pymechanical_runtime()

        from ansys.mechanical.core import launch_mechanical

        resolved_workdir = Path(working_directory) if working_directory else self.default_workdir
        resolved_workdir.mkdir(parents=True, exist_ok=True)

        mechanical = launch_mechanical(
            exec_file=str(mechanical_exec),
            batch=True,
            cleanup_on_exit=True,
        )

        try:
            script = self._build_named_selection_contact_script(
                source_named_selection_prefix=source_named_selection_prefix,
                target_named_selection_prefix=target_named_selection_prefix,
                contact_type=contact_type,
                contact_name_prefix=contact_name_prefix,
            )
            result_text = mechanical.run_python_script(script)

            parsed_result = self._parse_json_result(result_text)

            return {
                "success": True,
                "mode": "mechanical_contacts_created",
                "message": "已在 242+ Mechanical 中执行批量接触脚本。",
                "working_directory": str(resolved_workdir.resolve()),
                "working_directory_note": "当前接口已保留 working_directory 参数，后续可用于项目文件和日志落盘策略；PyMechanical 启动参数本身暂未直接使用该值。",
                "used_mechanical_exec": str(mechanical_exec),
                "execution_result": parsed_result,
                "script_preview": script,
            }
        finally:
            mechanical.exit()

    def _build_named_selection_contact_script(
        self,
        source_named_selection_prefix: str,
        target_named_selection_prefix: str,
        contact_type: str,
        contact_name_prefix: str,
    ) -> str:
        """生成在 Mechanical 中执行的批量接触脚本。"""
        payload = {
            "source_prefix": source_named_selection_prefix,
            "target_prefix": target_named_selection_prefix,
            "contact_type": contact_type,
            "contact_name_prefix": contact_name_prefix,
        }
        payload_json = json.dumps(payload, ensure_ascii=False)

        # 中文说明：
        # 这里把第一版实现收敛到“按 Named Selection 前缀配对”。
        # 例如：
        # source 前缀 = NS_SRC_
        # target 前缀 = NS_TGT_
        # 那么 NS_SRC_BOLT_01 会和 NS_TGT_BOLT_01 自动配成一组。
        return f"""
import json
payload = json.loads(r'''{payload_json}''')

model = ExtAPI.DataModel.Project.Model
connections = model.Connections
named_selections = list(model.NamedSelections.Children)

source_prefix = payload["source_prefix"]
target_prefix = payload["target_prefix"]
contact_name_prefix = payload["contact_name_prefix"]
contact_type_name = payload["contact_type"]

source_map = {{}}
target_map = {{}}

for ns in named_selections:
    ns_name = ns.Name
    if ns_name.startswith(source_prefix):
        key = ns_name[len(source_prefix):]
        source_map[key] = ns
    elif ns_name.startswith(target_prefix):
        key = ns_name[len(target_prefix):]
        target_map[key] = ns

pair_keys = sorted(set(source_map.keys()) & set(target_map.keys()))
missing_source = sorted(set(target_map.keys()) - set(source_map.keys()))
missing_target = sorted(set(source_map.keys()) - set(target_map.keys()))

from Ansys.Mechanical.DataModel.Enums import ContactType

created_contacts = []

for key in pair_keys:
    source_ns = source_map[key]
    target_ns = target_map[key]

    contact_region = connections.AddContactRegion()
    contact_region.Name = contact_name_prefix + key
    contact_region.SourceLocation = source_ns.Location
    contact_region.TargetLocation = target_ns.Location
    contact_region.ContactType = getattr(ContactType, contact_type_name)
    created_contacts.append(contact_region.Name)

wb_script_result = json.dumps({{
    "strategy": "named_selection_pairing",
    "pair_count": len(pair_keys),
    "created_contacts": created_contacts,
    "missing_source_suffixes": missing_source,
    "missing_target_suffixes": missing_target
}}, ensure_ascii=False)
""".strip()

    def _normalize_contact_type(self, contact_type: str) -> str:
        """规范化接触类型，避免大小写差异影响接口。"""
        for candidate in self.supported_contact_types:
            if candidate.lower() == contact_type.lower():
                return candidate
        raise ValueError(
            f"不支持的 contact_type：{contact_type}。当前仅支持：{', '.join(self.supported_contact_types.keys())}"
        )

    def _prepare_pymechanical_runtime(self) -> None:
        """准备 PyMechanical 运行环境，避免系统目录写权限问题。"""
        self.runtime_local_appdata.mkdir(parents=True, exist_ok=True)
        self.runtime_roaming_appdata.mkdir(parents=True, exist_ok=True)
        self.runtime_mechanical_user_data.parent.mkdir(parents=True, exist_ok=True)
        self.runtime_tools_path_data.mkdir(parents=True, exist_ok=True)
        (self.runtime_roaming_appdata / "Ansys").mkdir(parents=True, exist_ok=True)

        os.environ["LOCALAPPDATA"] = str(self.runtime_local_appdata.resolve())
        os.environ["APPDATA"] = str(self.runtime_roaming_appdata.resolve())

        import appdirs
        import platformdirs

        runtime_local = self.runtime_local_appdata.resolve()

        def _patched_user_data_dir(*args, **kwargs) -> str:
            appname = kwargs.get("appname", "app")
            appauthor = kwargs.get("appauthor")
            if appauthor == "Ansys":
                return str(runtime_local / "Ansys" / appname)
            return str(runtime_local / appname)

        platformdirs.user_data_dir = _patched_user_data_dir
        appdirs.user_data_dir = _patched_user_data_dir

    def _check_pymechanical_importable(self) -> tuple[bool, str | None]:
        """检查当前环境是否能导入 PyMechanical。"""
        try:
            self._prepare_pymechanical_runtime()
            from ansys.mechanical.core import launch_mechanical  # noqa: F401

            return True, None
        except Exception as exc:
            return False, str(exc)

    def _find_mechanical_executable(self) -> tuple[Path | None, int | None]:
        """寻找 242+ Mechanical 可执行文件。"""
        explicit_exec = os.getenv("MECHANICAL_EXEC")
        if explicit_exec:
            explicit_path = Path(explicit_exec)
            if explicit_path.exists():
                return explicit_path, self._infer_version_from_path(explicit_path)

        candidates: list[tuple[Path, int]] = []

        for version in self.supported_versions:
            awp_root = os.getenv(f"AWP_ROOT{version}")
            if awp_root:
                candidate = Path(awp_root) / "aisol" / "bin" / "winx64" / "AnsysWBU.exe"
                candidates.append((candidate, version))

            default_candidate = Path(rf"D:\ANSYS Inc\v{version}") / "aisol" / "bin" / "winx64" / "AnsysWBU.exe"
            candidates.append((default_candidate, version))

        for candidate, version in candidates:
            if candidate.exists():
                return candidate, version

        return None, None

    def _infer_version_from_path(self, path: Path) -> int | None:
        """从路径字符串中推测版本号。"""
        text = str(path).lower()
        for version in self.supported_versions + [241]:
            if f"v{version}" in text:
                return version
        return None

    def _parse_json_result(self, result_text: str) -> dict:
        """解析 Mechanical 脚本返回的 JSON 结果。"""
        if not result_text:
            return {"raw_result": result_text}

        try:
            return json.loads(result_text)
        except Exception:
            return {"raw_result": result_text}

    def _build_status_message(
        self,
        pymechanical_importable: bool,
        mechanical_exec: Path | None,
        detected_version: int | None,
    ) -> str:
        """构造更易读的 Mechanical 状态信息。"""
        if not pymechanical_importable:
            return "PyMechanical 当前不可导入，暂时无法执行 242+ Mechanical 自动化。"
        if mechanical_exec is None:
            return "PyMechanical 已可导入，但未找到 242+ Mechanical 可执行文件。"
        if detected_version not in self.supported_versions:
            return f"检测到的 Mechanical 版本为 {detected_version}，此接口仅为 242+ 方案预留。"
        return f"PyMechanical 已可用，并检测到 {detected_version} 版本的 Mechanical。"
