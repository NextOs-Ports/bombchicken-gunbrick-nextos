#!/usr/bin/env python3
"""Hermetic contract and public-surface checks for Bomb Chicken.

This suite never imports or executes the AArch64 game loader. Optional ELF
arguments are inspected with host binutils only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


PORT = Path(__file__).resolve().parents[1]
REPO = PORT.parents[1]
REL_PORT = PORT.relative_to(REPO).as_posix()

QUIRKS = [
    "game.bombchicken.menu-cursor-v44",
    "game.bombchicken.native-pause-v44",
    "game.bombchicken.nonnull-play-games-v44",
    "game.bombchicken.present-alpha-one",
    "game.bombchicken.progress-parser-v44",
    "game.bombchicken.stencil8-v44",
]

CAPABILITIES = [
    "host.portmaster",
    "host.aarch64-libs",
    "graphics.window",
    "graphics.gles2",
    "graphics.egl",
    "graphics.egl-config",
    "graphics.drawable",
    "input.controller-mapping",
    "input.controller-api",
]

REQUIRED_FILES = [
    "bombchicken-nextos",
    "lib/libmain.so",
    "lib/libunity.so",
    "lib/libil2cpp.so",
    "assets/bin/Data/boot.config",
    "assets/bin/Data/data.unity3d",
    "assets/bin/Data/Managed/Metadata/global-metadata.dat",
]

NXEXTRACT_HASHES = {
    "nxextract/nxextract.py":
        "a4a8e5d3bf2a1344491e27921c54430ee9b4e3fedd0160631da96734fa3d5170",
    "nxextract/nxextract-ui":
        "046afb583f5a211c946495e639409f81d9cfec706788eeccb7924b0e8e5a50b6",
    "nxextract/nxextract-runtime-env.sh":
        "332919a9960d4317563b647f9932d1a4367da147a425fe2f78eafd706f01563f",
    "nxextract/run-extractor.sh":
        "179b72f02b9dfdf3ed1bdc382d074fb4ef07f83e3d62cfccfc74a950e68679c2",
    "extractor.json":
        "add1a989f9db837c7ac591b95e257714ac508767381e58040e7edf2b17115bb5",
}

# Flexible recipe: owner libraries are accepted by a size RANGE (multiple APK
# builds), not a frozen byte/hash. Ranges mirror the extractor.json.
OWNER_LIBS = {
    "lib/libmain.so": (3364, 16820),
    "lib/libunity.so": (8592240, 42961200),
    "lib/libil2cpp.so": (20153596, 100767980),
}


class ContractFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractFailure(message)


def read_text(relative: str) -> str:
    return (PORT / relative).read_text(encoding="utf-8")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractFailure(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(relative: str) -> Any:
    try:
        return json.loads(read_text(relative), object_pairs_hook=unique_object)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ContractFailure(f"invalid {relative}: {error}") from error


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def output(*args: str) -> str:
    completed = subprocess.run(
        args,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "LC_ALL": "C"},
    )
    return completed.stdout


def check_nxport() -> None:
    manifest = load_json("nxport.json")
    expected = {
        "architecture": "aarch64",
        "argument_mode": "game-dir-and-passthrough",
        "enabled_quirks": QUIRKS,
        "executable": "bombchicken-nextos",
        "home_mode": "preserve",
        "id": "bombchicken",
        "launcher_name": "Bomb Chicken.sh",
        "nxextract": {"mode": "yes", "version": "1.2.6"},
        "prepare_script": "",
        "private_library_paths": [],
        "required_capabilities": CAPABILITIES,
        "required_files": REQUIRED_FILES,
        "runtime_report": "log-and-logo",
        "schema_version": 2,
        "title": "Bomb Chicken",
    }
    require(manifest == expected, "nxport.json differs from the frozen v2 contract")
    require(len(set(QUIRKS)) == len(QUIRKS), "duplicate declared quirk")
    require(len(set(CAPABILITIES)) == len(CAPABILITIES),
            "duplicate required capability")


def check_extractor() -> None:
    recipe = load_json("extractor.json")
    require(recipe.get("schema") == 1, "extractor schema must be 1")
    require(recipe.get("id") == "bombchicken-nextos", "extractor id drift")
    require(recipe.get("version") == "v44-build45-3", "payload version drift")
    input_contract = recipe.get("input", {})
    require(input_contract.get("packages") == ["com.nitrome.bombchicken"],
            "package allowlist drift")
    require(recipe.get("abi_order") == ["arm64-v8a"], "ABI allowlist drift")
    require(recipe.get("hooks") == [], "owner-data hooks must remain empty")
    require(recipe.get("commit") == ["assets", "lib"], "commit roots drift")
    require(recipe.get("marker") == ".nxextract-bombchicken.json",
            "marker drift")
    require(recipe.get("space", {}).get("safety_bytes") == 268435456,
            "free-space safety reserve drift")

    validators = {entry["path"]: entry for entry in recipe.get("validate", [])}
    require(set(validators) == {"assets", *OWNER_LIBS},
            "final owner-data validators drift")
    assets = validators["assets"]
    require(assets.get("type") == "tree", "assets validator is not a tree")
    require(assets.get("exact_files") == 11, "assets file count drift")
    require(assets.get("exact_bytes") == 120143454, "assets byte count drift")
    require(assets.get("tree_fingerprint") ==
            "f3d02727e90a908a52a9eba9308ace1d87c42640712f41c45c886f04ce92a2e4",
            "assets fingerprint drift")
    require(assets.get("required_paths") == [
        "bin/Data/boot.config",
        "bin/Data/data.unity3d",
        "bin/Data/Managed/Metadata/global-metadata.dat",
        "bin/Data/unity_app_guid",
    ], "assets anchors drift")
    for path, (min_size, max_size) in OWNER_LIBS.items():
        validator = validators[path]
        require(validator.get("type") == "file", f"{path}: not a file validator")
        require(validator.get("elf_machine") == "arm64-v8a",
                f"{path}: ELF ABI drift")
        require(validator.get("min_size") == min_size, f"{path}: min_size drift")
        require(validator.get("max_size") == max_size, f"{path}: max_size drift")

    extracted = recipe.get("extract", [])
    require(len(extracted) == 4, "extractor must publish exactly four roots/files")
    require({entry.get("destination") for entry in extracted} ==
            {"assets", *OWNER_LIBS}, "extract destinations drift")


def check_vendored_nxextract() -> None:
    pin_text = read_text("nxextract-version.txt")
    require(pin_text.splitlines()[0] == "1.2.6", "NXExtract pin version drift")
    recorded = dict(re.findall(
        r"^([^ ]+) sha256=([0-9a-f]{64})$", pin_text, re.MULTILINE))
    require(recorded == NXEXTRACT_HASHES, "NXExtract pin set differs from contract")
    for relative, expected in NXEXTRACT_HASHES.items():
        candidate = PORT / relative
        require(candidate.is_file() and not candidate.is_symlink(),
                f"pinned file missing or symlinked: {relative}")
        require(sha256(candidate) == expected, f"stale NXExtract pin: {relative}")

    canonical = REPO / "suportando_outros_devices/extrator-universal"
    canonical_map = {
        "nxextract/nxextract.py": canonical / "nxextract.py",
        "nxextract/nxextract-runtime-env.sh": canonical / "nxextract-runtime-env.sh",
        "nxextract/run-extractor.sh": canonical / "run-extractor.sh",
        "nxextract/nxextract-ui": canonical / "ui/build/nxextract-ui",
    }
    for relative, source in canonical_map.items():
        require(source.is_file(), f"canonical NXExtract source missing: {source}")
        require((PORT / relative).read_bytes() == source.read_bytes(),
                f"vendored NXExtract has local patches: {relative}")


def check_source_contract() -> None:
    main = read_text("src/main.c")
    contract = read_text("src/contract.c")
    input_source = read_text("src/input.c")
    jni = read_text("src/jni.c")
    egl = read_text("src/egl.c")
    egl_sdl = read_text("src/egl_sdl.c")
    all_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((PORT / "src").glob("*.[ch]"))
    )

    quirk_env = {
        QUIRKS[0]: "BC_CURSOR",
        QUIRKS[1]: "BC_PAUSE_NATIVE",
        QUIRKS[2]: "BC_NONNULL_OBJECT_FALLBACK",
        QUIRKS[3]: "BC_OPAQUE_BACKBUFFER",
        QUIRKS[4]: "BC_PROGRESS_FIX",
        QUIRKS[5]: "BC_FORCE_STENCIL",
    }
    for quirk, variable in quirk_env.items():
        require(f'{{ "{quirk}", "{variable}" }}' in contract or
                (quirk in contract and variable in contract),
                f"contract bridge is missing {quirk}")
    require("bc_apply_declared_contract();" in main,
            "main does not apply the manifest contract")
    require("if (!flag || !*flag || strcmp(flag, \"0\") == 0)" in input_source,
            "pause/progress corrections are not fail-closed")
    require("getenv(\"BC_NONNULL_OBJECT_FALLBACK\")" in jni,
            "JNI fallback lacks explicit opt-in")
    require("bc_env_flag(\"BC_OPAQUE_BACKBUFFER\")" in egl,
            "alpha-one present correction lacks explicit opt-in")
    require("bc_env_flag(\"BC_FORCE_STENCIL\")" in egl,
            "stencil correction lacks explicit opt-in")
    require("force_stencil && val < 8" in egl and
            "!saw_stencil && k < 60 && force_stencil" in egl,
            "every stencil-forcing path must share the explicit opt-in")
    require("cursor_enabled = getenv(\"BC_CURSOR\")" in input_source,
            "menu cursor is not opt-in")

    lifecycle = [
        "[bc] initJni...",
        "nativeRecreateGfxState(surfaceCreated)...",
        "nativeRecreateGfxState(surfaceChanged)...",
        "nativeSendSurfaceChangedEvent OK",
        "nativeFocusChanged(true) OK",
        "nativeResume OK",
        "[bc] nativeRender loop",
        "nativeFocusChanged(false) OK",
        "nativePause OK",
        "bc_input_close();",
        "bc_audio_stop();",
    ]
    positions = [main.find(token) for token in lifecycle]
    require(all(position >= 0 for position in positions),
            "native lifecycle token missing")
    require(positions == sorted(positions), "native lifecycle order changed")
    boot_order = [
        "nx_run_init(main_mod);",
        "main_onload(bc_jni_vm(), NULL)",
        'bc_jni_native("com/unity3d/player/NativeLoader", "load")',
        "NativeLoader.load completed: libunity -> libil2cpp",
        "run_unity();",
    ]
    positions = [main.find(token) for token in boot_order]
    require(all(position >= 0 for position in positions), "native boot token missing")
    require(positions == sorted(positions), "constructors/JNI_OnLoad order changed")

    require("0300605b100800000100000010010000" not in input_source,
            "fixed controller GUID returned")
    require('"GO-Super Gamepad"' not in input_source,
            "controller-name behavior returned")
    require('"nextos-gamepad"' not in input_source,
            "firmware-specific fallback controller identity returned")
    require(not re.search(r"strcasecmp\s*\([^;\n]*(?:mali|nextos|muos|arkos)",
                          egl_sdl, re.IGNORECASE),
            "graphics path is selected by a device/firmware name")
    require("if (create_window())\n        return 1;" in egl_sdl and
            "trying raw EGL" in egl_sdl,
            "SDL-owned to raw-EGL capability fallback is missing")
    require(not re.search(r"/proc/(?:\[[^]]*\]|[0-9*])", all_source),
            "global /proc process scan returned")
    require('/proc/self/exe' in main,
            "process-local single-instance lock disappeared")


def check_build_policy() -> None:
    build = read_text("build.sh")
    for token in (
        "playfetch-builder:buster",
        "sha256:036c7910ea53bc78cc213452afa92fa83d55de1c51ae54f315af58b5a41a45cf",
        "--network none",
        '"$NEXTOS_SYSROOT":/nxsr:ro',
        "-ffile-prefix-map=/repo=.",
        "-fdebug-prefix-map=/repo=.",
        "maximum GLIBC_2.30",
        "RPATH|RUNPATH",
        "unexpected DT_NEEDED",
        "g_bionic_guard_pad",
    ):
        require(token in build, f"public build policy token missing: {token}")
    require("-Werror" in build, "public source build is not warning-clean")
    require("NEXTOS_SYSROOT" in build and "-L/nxsr" not in build,
            "target sysroot must supply headers, not linked libraries")


def check_public_tree() -> None:
    require(read_text("version.txt").strip() == "1.1.4", "port version drift")
    for legacy in ("run.sh", "es_map.sh", "es2sdl.awk"):
        require(not (PORT / legacy).exists(), f"legacy helper remains: {legacy}")
    for path in PORT.rglob("*"):
        if path.is_file() and path.name.casefold() == "run.sh":
            raise ContractFailure(f"forbidden nested run.sh: {path.relative_to(PORT)}")

    tracked = output("git", "-C", str(REPO), "ls-files", "--", REL_PORT).splitlines()
    forbidden_suffixes = (".apk", ".apkm", ".apks", ".xapk", ".obb", ".so")
    for path in tracked:
        lower = path.casefold()
        require(not lower.endswith(forbidden_suffixes),
                f"proprietary/foreign binary is tracked: {path}")
        require("/stage/" not in lower and "/verify/" not in lower and
                "/home/" not in lower and "/build/" not in lower,
                f"private runtime artifact is tracked: {path}")

    ignored_apk = subprocess.run(
        ["git", "-C", str(REPO), "check-ignore", "-q", "--",
         f"{REL_PORT}/gamedata/game.apk"],
        check=False,
    ).returncode
    require(ignored_apk == 0, "owner APK path is not ignored")
    ignored_readme = subprocess.run(
        ["git", "-C", str(REPO), "check-ignore", "-q", "--",
         f"{REL_PORT}/gamedata/README.txt"],
        check=False,
    ).returncode
    require(ignored_readme != 0, "public gamedata README is ignored")

    public_text = [
        "README.md",
        "INSTALLATION.md",
        "HANDOFF.md",
        "STUDY.md",
        "NOTICE.md",
        "nxport.json",
        "extractor.json",
        "nxextract-version.txt",
        "gamedata/README.txt",
    ]
    for optional in (
        "Bomb Chicken.sh",
        "nxrelease.json",
        "package/build-package.sh",
    ):
        if (PORT / optional).is_file():
            public_text.append(optional)
    sensitive = re.compile(
        r"(?:/home/|/mnt/ARQUIVOS/|root@|(?:10|127|192\.168)\.\d+\.\d+\.\d+|"
        r"169\.254\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)",
        re.IGNORECASE,
    )
    for relative in public_text:
        require(not sensitive.search(read_text(relative)),
                f"public text contains a private path/address: {relative}")


def check_generated_framework() -> None:
    # 0.6.3: a single self-contained launcher. No bootstrap library, no
    # deployment receipt, no legacy migration helper.
    launcher = PORT / "Bomb Chicken.sh"
    require(launcher.is_file() and not launcher.is_symlink(),
            "generated launcher missing/symlinked")
    for retired in ("nxbootstrap-0.5.1.sh", "nxbootstrap.sh",
                    "nxdeployment.json", "migrate-legacy-overlay.sh", "run.sh"):
        require(not (PORT / retired).exists(),
                f"retired 0.5.1 artifact still present: {retired}")
    launcher_text = launcher.read_text(encoding="utf-8")
    require("nxbootstrap 0.6.3" in launcher_text,
            "launcher does not record the 0.6.3 generator")
    require("run.sh" not in launcher_text, "launcher references legacy run.sh")
    for guarantee in ("flock -n 9", 'wait "$game_pid"', "nxbootstrap_finish",
                      "pm_finish", "command ls -Lldn /proc/self/fd/9",
                      '"$NXBOOTSTRAP_LOCK_FILE" -ef /proc/self/fd/9'):
        require(guarantee in launcher_text,
                f"launcher lacks golden-port guarantee: {guarantee}")
    require("stat -L -c" not in launcher_text and
            "stat -L -t" not in launcher_text,
            "launcher regained an external stat dependency")


def check_release_manifest() -> None:
    release_tool = REPO / "framework/nxrelease/nxrelease.py"
    release_version = REPO / "framework/nxrelease/VERSION"
    require(release_version.read_text(encoding="utf-8").strip() == "0.2.5",
            "NXRelease version differs from the frozen package gate")
    require(sha256(release_tool) ==
            "097ef954261d7e31fb4a759caf2ebda9be02f069b1968e3f7b379d92f51e732f",
            "NXRelease 0.2.5 implementation pin drift")
    package_script = read_text("package/build-package.sh")
    require("NXRELEASE_VERSION=0.2.5" in package_script,
            "package script does not pin NXRelease 0.2.5")
    require("NXRELEASE_SHA256="
            "097ef954261d7e31fb4a759caf2ebda9be02f069b1968e3f7b379d92f51e732f"
            in package_script,
            "package script does not pin the NXRelease 0.2.5 implementation")
    release = load_json("nxrelease.json")
    require(release.get("schema_version") == 2, "NXRelease schema must be 2")
    require(release.get("source_root") == ".", "NXRelease source_root drift")
    package = release.get("package", {})
    require(package.get("id") == "bombchicken", "release package id drift")
    require(package.get("version") == "1.1.4", "release package version drift")
    require(package.get("profile") == "universal-portmaster",
            "release profile drift")
    require(package.get("launcher") == "Bomb Chicken.sh",
            "release launcher drift")
    require(package.get("launcher_chain") == ["Bomb Chicken.sh"],
            "release launcher chain drift")
    launcher_contract = package.get("launcher_contract", {})
    require(launcher_contract.get("version") == "0.6.3",
            "release bootstrap version drift")
    require(launcher_contract.get("config_sha256") == sha256(PORT / "nxport.json"),
            "release nxport pin is stale")
    require(package.get("license", {}).get("spdx_id") == "GPL-3.0-only",
            "release license drift")
    require(release.get("release", {}).get("max_glibc") == "2.30",
            "release GLIBC ceiling drift")

    entries = release.get("files")
    require(isinstance(entries, list) and entries, "release files list is empty")
    targets: set[str] = set()
    top_level_shell = []
    for index, entry in enumerate(entries):
        require(isinstance(entry, dict), f"release files[{index}] is not an object")
        source = entry.get("source")
        target = entry.get("target")
        require(isinstance(source, str) and isinstance(target, str),
                f"release files[{index}] lacks source/target")
        require(target not in targets, f"duplicate release target: {target}")
        targets.add(target)
        if target.casefold().endswith(".sh") and "/" not in target:
            top_level_shell.append(target)
        require(target.casefold() != "bombchicken/run.sh",
                "legacy nested launcher entered the release")
        require(not target.casefold().endswith(
            (".apk", ".apkm", ".apks", ".xapk", ".obb", ".so")),
            f"owner/foreign payload entered release manifest: {target}")
        candidate = PORT / source
        require(candidate.is_file() and not candidate.is_symlink(),
                f"release source missing/symlinked: {source}")
        expected_hash = entry.get("sha256")
        require(isinstance(expected_hash, str) and
                re.fullmatch(r"[0-9a-f]{64}", expected_hash) is not None,
                f"release source lacks SHA-256 pin: {source}")
        require(sha256(candidate) == expected_hash,
                f"stale release source pin: {source}")
    require(top_level_shell == ["Bomb Chicken.sh"],
            f"release must contain exactly one top-level .sh: {top_level_shell}")
    require("bombchicken/nxextract-version.txt" in targets,
            "normal public nxextract-version.txt name is missing")
    for retired in ("bombchicken/nxbootstrap-0.5.1.sh", "bombchicken/nxbootstrap.sh",
                    "bombchicken/nxdeployment.json",
                    "bombchicken/migrate-legacy-overlay.sh"):
        require(retired not in targets,
                f"retired 0.5.1 artifact in release manifest: {retired}")
    require(len(entries) == 16, "release allowlist count drift")


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(component) for component in value.split("."))


def audit_elf(path: Path, allowed_needed: set[str]) -> None:
    require(path.is_file() and not path.is_symlink(), f"ELF missing/symlinked: {path}")
    header = output("readelf", "-hW", str(path))
    require(re.search(r"Machine:\s+AArch64", header) is not None,
            f"not AArch64: {path}")
    require(re.search(r"Type:\s+DYN", header) is not None,
            f"not ET_DYN/PIE: {path}")
    program = output("readelf", "-lW", str(path))
    require("/lib/ld-linux-aarch64.so.1" in program,
            f"unexpected/missing AArch64 interpreter: {path}")
    dynamic = output("readelf", "-dW", str(path))
    require("RPATH" not in dynamic and "RUNPATH" not in dynamic,
            f"RPATH/RUNPATH in public ELF: {path}")
    needed = set(re.findall(r"\(NEEDED\).*?\[([^]]+)\]", dynamic))
    require(needed <= allowed_needed,
            f"unexpected DT_NEEDED in {path.name}: {sorted(needed - allowed_needed)}")
    versions = re.findall(r"GLIBC_([0-9]+(?:\.[0-9]+)+)",
                          output("readelf", "--version-info", str(path)))
    require(versions, f"no GLIBC symbol versions in {path}")
    maximum = max(map(version_tuple, versions))
    require(maximum <= (2, 30), f"{path.name} exceeds GLIBC_2.30: {maximum}")


def check_elfs(loader: Path) -> None:
    audit_elf(loader, {
        "libSDL2-2.0.so.0", "libc.so.6", "libdl.so.2", "libgcc_s.so.1",
        "libm.so.6", "libpthread.so.0", "libz.so.1",
    })
    symbols = output("readelf", "-sW", str(loader))
    require(re.search(
        r"0000000000000000\s+256\s+TLS\s+GLOBAL\s+DEFAULT\s+\d+\s+g_bionic_guard_pad",
        symbols) is not None, "Bionic TLS guard layout changed")
    strings = output("strings", str(loader))
    require(not re.search(r"/home/|/mnt/ARQUIVOS/|192\.168\.", strings),
            "loader contains a private build path/address")
    audit_elf(PORT / "nxextract/nxextract-ui", {"libc.so.6", "libdl.so.2"})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pre-freeze", action="store_true",
                        help="skip artifacts awaiting the final framework hash")
    parser.add_argument("--loader", type=Path,
                        help="audit this freshly built public loader")
    args = parser.parse_args()
    try:
        check_nxport()
        check_extractor()
        check_vendored_nxextract()
        check_source_contract()
        check_build_policy()
        check_public_tree()
        if not args.pre_freeze:
            check_generated_framework()
            check_release_manifest()
        if args.loader:
            check_elfs(args.loader.resolve())
    except (ContractFailure, OSError, subprocess.CalledProcessError) as error:
        print(f"bombchicken contract gate failed: {error}", file=sys.stderr)
        return 1
    print("bombchicken universal host contract/ELF tests passed")
    print("physical_device_evidence=0 guest_execution=0 network_calls=0 session_calls=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
