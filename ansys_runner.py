import os
from pathlib import Path


class AnsysRunner:
    """封装最小可运行的 ANSYS / PyMAPDL 执行流程。"""

    def __init__(self) -> None:
        self.default_workdir = Path("ansys_workspace")
        self.runtime_local_appdata = Path("runtime_data") / "localappdata"
        self.runtime_roaming_appdata = Path("runtime_data") / "appdata"
        self.runtime_pymapdl_user_data = self.runtime_local_appdata / "Ansys" / "ansys_mapdl_core"

        self.ansys241_dir = Path(os.getenv("ANSYS241_DIR", r"D:\ANSYS Inc\v241\ANSYS"))
        self.ansyslic_dir = Path(os.getenv("ANSYSLIC_DIR", r"D:\ANSYS Inc\Shared Files\Licensing"))
        self.awp_root241 = Path(os.getenv("AWP_ROOT241", r"D:\ANSYS Inc\v241"))
        self.supported_input_suffixes = {".inp", ".dat", ".mac"}

    def get_environment_status(self) -> dict:
        self._prepare_pymapdl_runtime()

        try:
            from ansys.mapdl.core import launch_mapdl  # noqa: F401

            pymapdl_importable = True
            pymapdl_error = None
        except Exception as exc:
            pymapdl_importable = False
            pymapdl_error = str(exc)

        exec_file = self._find_mapdl_executable()
        status = {
            "pymapdl_importable": pymapdl_importable,
            "ansys241_dir": str(self.ansys241_dir),
            "ansys241_dir_exists": self.ansys241_dir.exists(),
            "ansyslic_dir": str(self.ansyslic_dir),
            "ansyslic_dir_exists": self.ansyslic_dir.exists(),
            "awp_root241": str(self.awp_root241),
            "awp_root241_exists": self.awp_root241.exists(),
            "runtime_local_appdata": str(self.runtime_local_appdata.resolve()),
            "runtime_roaming_appdata": str(self.runtime_roaming_appdata.resolve()),
            "runtime_pymapdl_user_data": str(self.runtime_pymapdl_user_data.resolve()),
            "detected_mapdl_exec": str(exec_file) if exec_file else None,
            "detected_mapdl_exec_exists": exec_file is not None,
            "supported_input_suffixes": sorted(self.supported_input_suffixes),
            "message": self._build_status_message(
                pymapdl_importable=pymapdl_importable,
                exec_file=exec_file,
            ),
            "notes": [
                "ANSYS241_DIR 和 AWP_ROOT241 用于定位 MAPDL 可执行文件。",
                "ANSYSLIC_DIR 仅用于补充环境信息，本身通常不是许可证服务器地址。",
                "PyMAPDL 的运行时用户目录已重定向到工作区内的 runtime_data，避免系统目录写权限问题。",
                "当前接口支持 .inp、.dat、.mac 等 MAPDL 输入文件，不直接支持 .wbpj。",
            ],
            "next_step": "可调用 /run-mapdl-input 执行真实 MAPDL 输入文件，或调用 /run-ansys-demo 验证最小示例。",
        }

        if pymapdl_error:
            status["pymapdl_error"] = pymapdl_error

        return status

    def get_demo_definition(self) -> dict:
        commands = self._build_demo_commands()
        exec_file = self._find_mapdl_executable()

        return {
            "success": True,
            "mode": "demo_definition",
            "description": "两节点拉杆静力分析示例，用于展示 Python 如何组织 ANSYS 调用。",
            "analysis_type": "static_structural",
            "element_type": "LINK180",
            "apdl_commands": commands,
            "detected_mapdl_exec": str(exec_file) if exec_file else None,
            "ansys_environment": {
                "ANSYS241_DIR": str(self.ansys241_dir),
                "ANSYSLIC_DIR": str(self.ansyslic_dir),
                "AWP_ROOT241": str(self.awp_root241),
            },
            "notes": [
                "该接口默认仅返回演示命令，不真实启动 MAPDL。",
                "当前代码会优先根据 ANSYS241_DIR 和 AWP_ROOT241 自动搜索 MAPDL.exe。",
                "接入真实工程时，建议优先传入 .inp、.dat 或 .mac 文件给 /run-mapdl-input。",
            ],
        }

    def run_demo(self, launch_mapdl: bool = False, working_directory: str | None = None) -> dict:
        resolved_workdir = Path(working_directory) if working_directory else self.default_workdir
        resolved_workdir.mkdir(parents=True, exist_ok=True)
        exec_file = self._find_mapdl_executable()

        if not launch_mapdl:
            return {
                "success": True,
                "mode": "preview_only",
                "message": "未启动 MAPDL，已返回最小 ANSYS 示例命令。",
                "working_directory": str(resolved_workdir.resolve()),
                "detected_mapdl_exec": str(exec_file) if exec_file else None,
                "apdl_commands": self._build_demo_commands(),
            }

        try:
            return self._run_with_commands(
                working_directory=resolved_workdir,
                exec_file=exec_file,
                commands=self._build_demo_commands(),
                source_name="internal_demo_commands",
            )
        except Exception as exc:
            return {
                "success": False,
                "mode": "mapdl_launch_failed",
                "message": "启动 MAPDL 失败，请检查 ANSYS 路径、许可证配置和相关环境变量。",
                "detail": str(exc),
                "working_directory": str(resolved_workdir.resolve()),
                "detected_mapdl_exec": str(exec_file) if exec_file else None,
                "apdl_commands": self._build_demo_commands(),
            }

    def run_input_file(self, input_file_path: str, working_directory: str | None = None) -> dict:
        input_path = Path(input_file_path)
        validation_error = self._validate_input_file(input_path)
        if validation_error:
            return validation_error

        resolved_workdir = Path(working_directory) if working_directory else self.default_workdir
        resolved_workdir.mkdir(parents=True, exist_ok=True)
        exec_file = self._find_mapdl_executable()

        try:
            return self._run_with_input_file(
                working_directory=resolved_workdir,
                exec_file=exec_file,
                input_path=input_path,
            )
        except Exception as exc:
            return {
                "success": False,
                "mode": "mapdl_input_failed",
                "message": "执行 MAPDL 输入文件失败。",
                "detail": str(exc),
                "input_file_path": str(input_path.resolve()),
                "working_directory": str(resolved_workdir.resolve()),
                "detected_mapdl_exec": str(exec_file) if exec_file else None,
                "candidate_log_files": self._collect_log_files(resolved_workdir),
            }

    def _run_with_input_file(
        self,
        working_directory: Path,
        exec_file: Path | None,
        input_path: Path,
    ) -> dict:
        self._prepare_pymapdl_runtime()

        from ansys.mapdl.core import launch_mapdl

        launch_kwargs = {
            "run_location": str(working_directory.resolve()),
            "override": True,
        }
        if exec_file is not None:
            launch_kwargs["exec_file"] = str(exec_file)

        mapdl = launch_mapdl(**launch_kwargs)
        try:
            output_text = str(mapdl.input(str(input_path.resolve())))
            log_files = self._collect_log_files(working_directory)
            primary_log_path = self._select_primary_log_file(log_files)
            engineering_results = self._extract_engineering_results(mapdl)

            return {
                "success": True,
                "mode": "mapdl_input_executed",
                "message": "MAPDL 输入文件执行完成。",
                "input_file_path": str(input_path.resolve()),
                "working_directory": str(working_directory.resolve()),
                "used_exec_file": str(exec_file) if exec_file else None,
                "input_file_suffix": input_path.suffix.lower(),
                "mapdl_output_preview": output_text[:4000],
                "candidate_log_files": log_files,
                "primary_log_path": primary_log_path,
                "engineering_results": engineering_results,
            }
        finally:
            mapdl.exit()

    def _run_with_commands(
        self,
        working_directory: Path,
        exec_file: Path | None,
        commands: list[str],
        source_name: str,
    ) -> dict:
        self._prepare_pymapdl_runtime()

        from ansys.mapdl.core import launch_mapdl

        launch_kwargs = {
            "run_location": str(working_directory.resolve()),
            "override": True,
        }
        if exec_file is not None:
            launch_kwargs["exec_file"] = str(exec_file)

        mapdl = launch_mapdl(**launch_kwargs)
        try:
            command_outputs: list[dict[str, str]] = []
            for command in commands:
                output_text = str(mapdl.run(command))
                command_outputs.append(
                    {
                        "command": command,
                        "output": output_text.strip(),
                    }
                )

            node_2_ux = mapdl.get_value("NODE", 2, "U", "X")
            log_files = self._collect_log_files(working_directory)
            engineering_results = self._extract_engineering_results(mapdl)

            return {
                "success": True,
                "mode": "mapdl_executed",
                "message": "MAPDL 示例执行完成。",
                "source_name": source_name,
                "working_directory": str(working_directory.resolve()),
                "used_exec_file": str(exec_file) if exec_file else None,
                "result_summary": {
                    "node_2_ux": node_2_ux,
                },
                "executed_commands": commands,
                "command_outputs": command_outputs,
                "candidate_log_files": log_files,
                "primary_log_path": self._select_primary_log_file(log_files),
                "engineering_results": engineering_results,
            }
        finally:
            mapdl.exit()

    def _prepare_pymapdl_runtime(self) -> None:
        self.runtime_local_appdata.mkdir(parents=True, exist_ok=True)
        self.runtime_roaming_appdata.mkdir(parents=True, exist_ok=True)
        (self.runtime_roaming_appdata / "Ansys").mkdir(parents=True, exist_ok=True)
        self.runtime_pymapdl_user_data.parent.mkdir(parents=True, exist_ok=True)

        os.environ["ANSYS241_DIR"] = str(self.ansys241_dir)
        os.environ["ANSYSLIC_DIR"] = str(self.ansyslic_dir)
        os.environ["AWP_ROOT241"] = str(self.awp_root241)
        os.environ["LOCALAPPDATA"] = str(self.runtime_local_appdata.resolve())
        os.environ["APPDATA"] = str(self.runtime_roaming_appdata.resolve())

        import platformdirs

        runtime_path = str(self.runtime_pymapdl_user_data.resolve())
        platformdirs.user_data_dir = lambda *args, **kwargs: runtime_path

    def _find_mapdl_executable(self) -> Path | None:
        candidates = [
            self.ansys241_dir / "bin" / "winx64" / "MAPDL.exe",
            self.ansys241_dir / "bin" / "winx64" / "MAPDL241.exe",
            self.ansys241_dir / "bin" / "winx64" / "ANSYS241.exe",
            self.awp_root241 / "ANSYS" / "bin" / "winx64" / "MAPDL.exe",
            self.awp_root241 / "ANSYS" / "bin" / "winx64" / "MAPDL241.exe",
            self.awp_root241 / "ANSYS" / "bin" / "winx64" / "ANSYS241.exe",
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        return None

    def _validate_input_file(self, input_path: Path) -> dict | None:
        if not input_path.exists():
            return {
                "success": False,
                "mode": "invalid_input_file",
                "message": f"输入文件不存在：{input_path}",
            }

        suffix = input_path.suffix.lower()
        if suffix == ".wbpj":
            return {
                "success": False,
                "mode": "unsupported_workbench_project",
                "message": "当前接口不直接支持 .wbpj 工程文件。",
                "detail": "如果工程来自 Workbench，建议先导出 MAPDL 输入文件，例如 .inp 或命令流，再接入当前接口。",
                "input_file_path": str(input_path.resolve()),
            }

        if suffix not in self.supported_input_suffixes:
            return {
                "success": False,
                "mode": "unsupported_input_type",
                "message": f"当前接口暂不支持 {suffix or '无后缀'} 文件。",
                "detail": f"当前仅支持：{', '.join(sorted(self.supported_input_suffixes))}",
                "input_file_path": str(input_path.resolve()),
            }

        return None

    def _collect_log_files(self, working_directory: Path) -> list[str]:
        log_files: list[Path] = []
        for suffix in ("*.out", "*.log", "*.err"):
            log_files.extend(working_directory.glob(suffix))

        unique_files = sorted({path.resolve() for path in log_files}, key=lambda item: item.name.lower())
        return [str(path) for path in unique_files]

    def _select_primary_log_file(self, log_files: list[str]) -> str | None:
        if not log_files:
            return None

        existing_paths = [Path(item) for item in log_files if Path(item).exists()]
        if not existing_paths:
            return None

        ranked_paths = sorted(existing_paths, key=self._score_log_file, reverse=True)
        return str(ranked_paths[0])

    def _score_log_file(self, path: Path) -> tuple[int, int, int, float]:
        """优先选择正式输出，而不是隐藏或临时日志。"""
        name = path.name.lower()
        suffix = path.suffix.lower()
        size = path.stat().st_size if path.exists() else 0
        modified_at = path.stat().st_mtime if path.exists() else 0.0

        is_out = 1 if suffix == ".out" else 0
        is_non_temp = 0 if self._looks_like_temp_log(name) else 1
        is_non_empty = 1 if size > 0 else 0

        return (is_out, is_non_temp, is_non_empty, modified_at)

    @staticmethod
    def _looks_like_temp_log(file_name: str) -> bool:
        temp_markers = ("__tmp__", ".tmp", "scratch")
        return file_name.startswith(".") or any(marker in file_name for marker in temp_markers)

    def _build_status_message(self, pymapdl_importable: bool, exec_file: Path | None) -> str:
        if not pymapdl_importable:
            return "当前无法导入 PyMAPDL，暂时不能执行真实 ANSYS 示例。"
        if exec_file is None:
            return "PyMAPDL 已可用，但当前路径配置下未找到 MAPDL.exe。"
        return "PyMAPDL 已可用，并已检测到 MAPDL 可执行文件。"

    def _extract_engineering_results(self, mapdl) -> dict:
        """求解完成后提取位移、应力、频率等工程物理量。"""
        results: dict = {}

        try:
            mapdl.post1()
            mapdl.set("LAST")
            mapdl.allsel()
        except Exception:
            results["extraction_error"] = "无法进入 POST1 后处理，可能求解未成功。"
            return results

        # 位移
        displacement: dict = {}
        try:
            mapdl.nsort("U", "SUM")
            displacement["max_usum"] = mapdl.get_value("SORT", 0, "MAX")
            displacement["label_usum"] = "合位移 (USUM)"
        except Exception:
            pass
        try:
            mapdl.nsort("U", "X")
            displacement["max_ux"] = mapdl.get_value("SORT", 0, "MAX")
            displacement["label_ux"] = "X 向位移 (UX)"
            mapdl.nsort("U", "Y")
            displacement["max_uy"] = mapdl.get_value("SORT", 0, "MAX")
            displacement["label_uy"] = "Y 向位移 (UY)"
            mapdl.nsort("U", "Z")
            displacement["max_uz"] = mapdl.get_value("SORT", 0, "MAX")
            displacement["label_uz"] = "Z 向位移 (UZ)"
        except Exception:
            pass
        if displacement:
            results["displacement"] = displacement

        # 应力 — 尝试节点解
        stress: dict = {}
        try:
            mapdl.nsort("S", "EQV")
            stress["max_von_mises"] = mapdl.get_value("SORT", 0, "MAX")
            stress["label_von_mises"] = "Von Mises (SEQV)"
        except Exception:
            pass
        try:
            mapdl.nsort("S", "1")
            stress["max_s1"] = mapdl.get_value("SORT", 0, "MAX")
            stress["label_s1"] = "第一主应力 (S1)"
            mapdl.nsort("S", "3")
            stress["max_s3"] = mapdl.get_value("SORT", 0, "MAX")
            stress["label_s3"] = "第三主应力 (S3)"
        except Exception:
            pass
        try:
            mapdl.nsort("S", "X")
            stress["max_sx"] = mapdl.get_value("SORT", 0, "MAX")
            stress["label_sx"] = "X 向正应力 (SX)"
        except Exception:
            pass
        if stress:
            results["stress"] = stress

        # 支反力
        reaction: dict = {}
        try:
            reaction["fx"] = mapdl.get_value("FSUM", 0, "FX")
            reaction["fy"] = mapdl.get_value("FSUM", 0, "FY")
            reaction["fz"] = mapdl.get_value("FSUM", 0, "FZ")
            results["reaction_forces"] = reaction
        except Exception:
            pass

        # 模态频率
        frequencies = self._extract_frequencies(mapdl)
        if frequencies:
            results["frequency"] = {"modes": frequencies}

        return results

    def _extract_frequencies(self, mapdl) -> list[dict]:
        """尝试从结果文件中提取模态频率列表。"""
        try:
            raw = str(mapdl.set("LIST"))
            parsed = []
            for line in raw.split("\n"):
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    try:
                        freq = float(parts[1])
                        parsed.append({"order": int(parts[0]), "frequency_hz": freq})
                    except ValueError:
                        continue
            return parsed[:20]
        except Exception:
            return []

    def _build_demo_commands(self) -> list[str]:
        return [
            "/CLEAR",
            "/PREP7",
            "ET,1,LINK180",
            "MP,EX,1,2.0E11",
            "MP,PRXY,1,0.3",
            "R,1,0.01",
            "N,1,0,0,0",
            "N,2,1,0,0",
            "TYPE,1",
            "REAL,1",
            "MAT,1",
            "E,1,2",
            "/SOLU",
            "ANTYPE,STATIC",
            "D,1,ALL,0",
            "F,2,FX,1000",
            "SOLVE",
            "FINISH",
            "/POST1",
            "SET,LAST",
        ]
