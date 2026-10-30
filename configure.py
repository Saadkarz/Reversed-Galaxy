#!/usr/bin/env python3

###
# Generates build files for the project.
# This file also includes the project configuration,
# such as compiler flags and the object matching status.
#
# Usage:
#   python3 configure.py
#   ninja
#
# Append --help to see available options.
###

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

from tools.project import (
    Object,
    ProgressCategory,
    ProjectConfig,
    calculate_progress,
    generate_build,
    is_windows,
)

# Game versions
DEFAULT_VERSION = 0
VERSIONS = [
    "SB4E01",  # 0
]

parser = argparse.ArgumentParser()
parser.add_argument(
    "mode",
    choices=["configure", "progress"],
    default="configure",
    help="script mode (default: configure)",
    nargs="?",
)
parser.add_argument(
    "-v",
    "--version",
    choices=VERSIONS,
    type=str.upper,
    default=VERSIONS[DEFAULT_VERSION],
    help="version to build",
)
parser.add_argument(
    "--build-dir",
    metavar="DIR",
    type=Path,
    default=Path("build"),
    help="base build directory (default: build)",
)
parser.add_argument(
    "--binutils",
    metavar="BINARY",
    type=Path,
    help="path to binutils (optional)",
)
parser.add_argument(
    "--compilers",
    metavar="DIR",
    type=Path,
    help="path to compilers (optional)",
)
parser.add_argument(
    "--map",
    action="store_true",
    help="generate map file(s)",
)
parser.add_argument(
    "--debug",
    action="store_true",
    help="build with debug info (non-matching)",
)
if not is_windows():
    parser.add_argument(
        "--wrapper",
        metavar="BINARY",
        type=Path,
        help="path to wibo or wine (optional)",
    )
parser.add_argument(
    "--dtk",
    metavar="BINARY | DIR",
    type=Path,
    help="path to decomp-toolkit binary or source (optional)",
)
parser.add_argument(
    "--objdiff",
    metavar="BINARY | DIR",
    type=Path,
    help="path to objdiff-cli binary or source (optional)",
)
parser.add_argument(
    "--sjiswrap",
    metavar="EXE",
    type=Path,
    help="path to sjiswrap.exe (optional)",
)
parser.add_argument(
    "--verbose",
    action="store_true",
    help="print verbose output",
)
parser.add_argument(
    "--non-matching",
    dest="non_matching",
    action="store_true",
    help="builds equivalent (but non-matching) or modded objects",
)
parser.add_argument(
    "--no-progress",
    dest="progress",
    action="store_false",
    help="disable progress calculation",
)
args = parser.parse_args()

config = ProjectConfig()
config.version = str(args.version)
version_num = VERSIONS.index(config.version)

# Apply arguments
config.build_dir = args.build_dir
config.dtk_path = args.dtk
config.objdiff_path = args.objdiff
config.binutils_path = args.binutils
config.compilers_path = args.compilers
config.generate_map = args.map
config.non_matching = args.non_matching
config.sjiswrap_path = args.sjiswrap
config.progress = args.progress
if not is_windows():
    config.wrapper = args.wrapper
# Don't build asm unless we're --non-matching
if not config.non_matching:
    config.asm_dir = None

# Tool versions
config.binutils_tag = "2.42-2"
config.compilers_tag = "20251118"
config.dtk_tag = "v1.8.3"
config.objdiff_tag = "v3.6.1"
config.sjiswrap_tag = "v1.2.2"
config.wibo_tag = "1.0.3"

# Project
config.config_path = Path("config") / config.version / "config.yml"
config.check_sha_path = Path("config") / config.version / "build.sha1"
config.asflags = [
    "-mgekko",
    "--strip-local-absolute",
    "-I include",
    f"-I build/{config.version}/include",
    f"--defsym version={version_num}",
]
config.ldflags = ["-fp hardware", "-nodefaults", "-warn off"]
if args.debug:
    config.ldflags.append("-g")  # Or -gdwarf-2 for Wii linkers
if args.map:
    config.ldflags.append("-mapunused")
    # config.ldflags.append("-listclosure") # For Wii linkers

# Use for any additional files that should cause a re-configure when modified
config.reconfig_deps = []

# Optional numeric ID for decomp.me preset
# Can be overridden in libraries or objects
config.scratch_preset_id = None

# Base flags, common to most GC/Wii games.
# Generally leave untouched, with overrides added below.
cflags_base = [
    "-nodefaults",
    "-proc gekko",
    "-align powerpc",
    "-enum int",
    "-fp hardware",
    "-Cpp_exceptions off",
    # "-W all",
    "-O4,p",
    "-inline auto",
    '-pragma "cats off"',
    '-pragma "warn_notinlined off"',
    "-maxerrors 1",
    "-nosyspath",
    "-RTTI off",
    "-fp_contract on",
    "-str reuse",
    "-i include",
    f"-i build/{config.version}/include",
    f"-DVERSION={version_num}",
]

cflags_game = [
    "-nodefaults",
    "-proc gekko",
    "-align powerpc",
    "-enum int",
    "-fp hardware",
    "-Cpp_exceptions off",
    "-O4,s",
    "-inline auto",
    '-pragma "cats off"',
    '-pragma "warn_notinlined off"',
    "-maxerrors 1",
    "-nosyspath",
    "-RTTI off",
    "-str reuse",
    "-enc SJIS",
    "-sdata 4",
    "-sdata2 4",
    "-ipa file",
    "-sym on",
    "-i include",
    "-i libs/JSystem/include",
    "-i libs/nw4r/include",
    "-i libs/RVL_SDK",
    "-i libs/JSystem",
    "-i libs/MSL_C",
    "-i libs/MSL_C++",
    "-i libs/MSL_C++/include",
    "-i libs/Runtime",
    f"-i build/{config.version}/include",
    f"-DVERSION={version_num}",
]

cflags_sdk = [
    "-nodefaults",
    "-proc gekko",
    "-align powerpc",
    "-enum int",
    "-fp hardware",
    "-Cpp_exceptions off",
    "-O4,p",
    "-inline auto",
    '-pragma "cats off"',
    '-pragma "warn_notinlined off"',
    "-maxerrors 1",
    "-nosyspath",
    "-RTTI off",
    "-enc SJIS",
    "-i libs/RVL_SDK",
    "-i libs/MSL_C",
    "-i libs/Runtime",
    "-i libs/MetroTRK",
    "-i libs/RVLFaceLib",
    "-i src/RVL_SDK/bte",
    f"-i build/{config.version}/include",
    f"-DVERSION={version_num}",
    "-ir libs/RVL_SDK/revolution/bte",
    "-DREVOLUTION",
]

cflags_sdk_ipa = [
    *cflags_sdk,
    "-str reuse",
    "-lang=c",
    "-ipa file",
    "-fp_contract off",
    "-func_align 16",
]

cflags_sdk_exi = ["-O3" if flag == "-O4,p" else flag for flag in cflags_sdk]

cflags_sdk_gc = [
    "-nodefaults",
    "-proc gekko",
    "-align powerpc",
    "-enum int",
    "-fp hardware",
    "-Cpp_exceptions off",
    "-O4,p",
    "-inline auto,level=3",
    '-pragma "cats off"',
    '-pragma "warn_notinlined off"',
    "-maxerrors 1",
    "-nosyspath",
    "-RTTI off",
    "-str reuse",
    "-enc SJIS",
    "-ipa file",
    "-sdata 8",
    "-sdata2 8",
    "-i libs/RVL_SDK",
    "-i libs/MSL_C",
    "-i libs/Runtime",
    "-i libs/MetroTRK",
    "-i libs/RVLFaceLib",
    "-i src/RVL_SDK/bte",
    f"-i build/{config.version}/include",
    f"-DVERSION={version_num}",
    "-ir libs/RVL_SDK/revolution/bte",
    "-DREVOLUTION",
]

cflags_nw = [
    "-nodefaults",
    "-proc gekko",
    "-align powerpc",
    "-enum int",
    "-fp hardware",
    '-pragma "ppc_no_fp_blockmove on"',
    "-Cpp_exceptions off",
    "-O4,p",
    "-inline auto",
    '-pragma "cats off"',
    '-pragma "warn_notinlined off"',
    "-maxerrors 1",
    "-nosyspath",
    "-RTTI off",
    "-fp_contract off",
    "-str reuse",
    "-enc SJIS",
    "-ipa file",
    "-i libs/nw4r/include",
    "-i libs/MSL_C++/include",
    "-i libs/MSL_C",
    "-i libs/MetroTRK",
    "-i libs/RVL_SDK",
    "-i libs/Runtime",
    f"-i build/{config.version}/include",
    f"-DVERSION={version_num}",
]

cflags_jsys = [
    "-nodefaults",
    "-proc gekko",
    "-align powerpc",
    "-enum int",
    "-fp hardware",
    "-Cpp_exceptions off",
    "-O4,s",
    "-inline auto",
    '-pragma "cats off"',
    '-pragma "warn_notinlined off"',
    "-maxerrors 1",
    "-nosyspath",
    "-RTTI off",
    "-fp_contract off",
    "-str reuse",
    "-enc SJIS",
    "-sdata 4",
    "-sdata2 4",
    "-use_lmw_stmw off",
    "-i include",
    "-i libs/JSystem/include",
    "-i libs/RVL_SDK",
    "-i libs/MSL_C",
    "-i libs/MSL_C++/include",
    f"-i build/{config.version}/include",
    f"-DVERSION={version_num}",
]

cflags_jsys_jaudio = [*cflags_jsys, "-ipa file", "-sym on"]
cflags_jsys_jpa = [*cflags_jsys, "-ipa file"]


cflags_rfl = [
    "-nodefaults",
    "-proc gekko",
    "-align powerpc",
    "-enum int",
    "-fp hardware",
    "-Cpp_exceptions on",
    "-O4,p",
    "-inline auto",
    '-pragma "cats off"',
    '-pragma "warn_notinlined off"',
    "-maxerrors 1",
    "-nosyspath",
    "-RTTI off",
    "-str reuse",
    "-enc SJIS",
    "-ipa file",
    "-i libs/MSL_C",
    "-i libs/MetroTRK",
    "-i libs/RVL_SDK",
    "-i libs/Runtime",
    "-i libs/RVLFaceLib",
    f"-i build/{config.version}/include",
    f"-DVERSION={version_num}",
]

cflags_msl = [
    *cflags_base,
    "-use_lmw_stmw on",
    "-str reuse,pool,readonly",
    "-fp_contract off",
    "-inline on",
    "-ipa file",
    "-func_align 4",
    "-i libs/MSL_C",
    "-i libs/RVL_SDK",
]

cflags_trk = [
    *cflags_base,
    "-use_lmw_stmw on",
    "-func_align 4",
    "-pool off",
    "-i libs/MetroTRK",
    "-i libs/RVL_SDK",
    "-i libs/MSL_C",
]

# Debug flags
if args.debug:
    # Or -sym dwarf-2 for Wii compilers
    cflags_base.extend(["-sym on", "-DDEBUG=1"])
else:
    cflags_base.append("-DNDEBUG=1")

# Metrowerks library flags
cflags_runtime = [
    *cflags_base,
    "-use_lmw_stmw on",
    "-str reuse,pool,readonly",
    "-gccinc",
    "-common off",
    "-inline auto",
    "-i libs/MSL_C",
    "-i libs/Runtime",
]

# REL flags
cflags_rel = [
    *cflags_base,
    "-sdata 0",
    "-sdata2 0",
]

config.linker_version = "GC/3.0a5"


def GameLib(lib_name: str, objects: List[Object]) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": "Wii/1.0",
        "cflags": cflags_game,
        "progress_category": "game",
        "objects": objects,
    }


def RVLLib(
    lib_name: str, objects: List[Object], cflags: List[str] = cflags_sdk_ipa
) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": "Wii/1.0",
        "cflags": cflags,
        "progress_category": "sdk",
        "objects": objects,
    }


def RVLLibGC(
    lib_name: str, objects: List[Object], mw_version: str = "GC/3.0a3"
) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": mw_version,
        "cflags": cflags_sdk_gc,
        "progress_category": "sdk",
        "objects": objects,
    }


def NWLib(lib_name: str, objects: List[Object]) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": "Wii/1.3",
        "cflags": cflags_nw,
        "progress_category": "nw4r",
        "objects": objects,
    }


def JSysLib(lib_name: str, objects: List[Object]) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": "Wii/1.0",
        "cflags": cflags_jsys,
        "progress_category": "jsys",
        "objects": objects,
    }


def JSys_JAudioLib(lib_name: str, objects: List[Object]) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": "Wii/1.0",
        "cflags": cflags_jsys_jaudio,
        "progress_category": "jsys",
        "objects": objects,
    }


def JSys_JParticleLib(lib_name: str, objects: List[Object]) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": "Wii/1.0",
        "cflags": cflags_jsys_jpa,
        "progress_category": "jsys",
        "objects": objects,
    }


def RFLib(lib_name: str, objects: List[Object]) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": "Wii/1.0",
        "cflags": cflags_rfl,
        "progress_category": "rfl",
        "objects": objects,
    }


def MSLLib(lib_name: str, objects: List[Object]) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": "Wii/1.1",
        "cflags": cflags_msl,
        "progress_category": "msl",
        "objects": objects,
    }


def TRKLib(lib_name: str, objects: List[Object]) -> Dict[str, Any]:
    return {
        "lib": lib_name,
        "mw_version": "Wii/1.0a",
        "cflags": cflags_trk,
        "progress_category": "trk",
        "objects": objects,
    }


Matching = True  # Object matches and should be linked
NonMatching = False  # Object does not match and should not be linked
Equivalent = (
    config.non_matching
)  # Object should be linked when configured with --non-matching


# Object is only matching for specific versions
def MatchingFor(*versions):
    return config.version in versions


config.warn_missing_config = True
config.warn_missing_source = False
config.libs = [
    JSysLib(
        "J2DGraph",
        [
            Object(
                NonMatching,
                "JSystem/J2DGraph/J2DGrafContext.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(NonMatching, "JSystem/J2DGraph/J2DOrthoGraph.cpp"),
            Object(Matching, "JSystem/J2DGraph/J2DMatBlock.cpp"),
            Object(NonMatching, "JSystem/J2DGraph/J2DPane.cpp"),
            Object(Matching, "JSystem/J2DGraph/J2DScreen.cpp"),
            Object(
                NonMatching,
                "JSystem/J2DGraph/J2DPicture.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(Matching, "JSystem/J2DGraph/J2DManage.cpp"),
        ],
    ),
    JSysLib(
        "J3DGraphAnimator",
        [
            Object(
                Matching,
                "JSystem/J3DGraphAnimator/J3DShapeTable.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                Matching,
                "JSystem/J3DGraphAnimator/J3DJointTree.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                Matching,
                "JSystem/J3DGraphAnimator/J3DModelData.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/J3DGraphAnimator/J3DMtxBuffer.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/J3DGraphAnimator/J3DModel.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/J3DGraphAnimator/J3DAnimation.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                Matching,
                "JSystem/J3DGraphAnimator/J3DMaterialAnm.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                Matching,
                "JSystem/J3DGraphAnimator/J3DSkinDeform.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/J3DGraphAnimator/J3DCluster.cpp",
                extra_cflags=["-ipa file"],
            ),
            Object(
                NonMatching,
                "JSystem/J3DGraphAnimator/J3DJoint.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                Matching,
                "JSystem/J3DGraphAnimator/J3DMaterialAttach.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
        ],
    ),
    JSysLib(
        "J3DGraphBase",
        [
            Object(
                NonMatching,
                "JSystem/J3DGraphBase/J3DGD.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                Matching, "JSystem/J3DGraphBase/J3DSys.cpp", extra_cflags=["-ipa file"]
            ),
            Object(
                Matching,
                "JSystem/J3DGraphBase/J3DVertex.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/J3DGraphBase/J3DTransform.cpp",
                extra_cflags=["-ipa file", "-sym on", "-opt nolifetimes,nocse"],
            ),
            Object(
                Matching,
                "JSystem/J3DGraphBase/J3DPacket.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                Matching,
                "JSystem/J3DGraphBase/J3DShapeMtx.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                Matching,
                "JSystem/J3DGraphBase/J3DShapeDraw.cpp",
                extra_cflags=["-ipa file"],
            ),
            Object(
                Matching,
                "JSystem/J3DGraphBase/J3DShape.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/J3DGraphBase/J3DMaterial.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/J3DGraphBase/J3DMatBlock.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                Matching,
                "JSystem/J3DGraphBase/J3DTevs.cpp",
                extra_cflags=["-ipa file"],
            ),
            Object(Matching, "JSystem/J3DGraphBase/J3DDrawBuffer.cpp",
                extra_cflags=["-ipa file"],
            ),
            Object(
                Matching,
                "JSystem/J3DGraphBase/J3DStruct.cpp",
                extra_cflags=["-ipa file"],
            ),
        ],
    ),
    JSysLib(
        "J3DGraphLoader",
        [
            Object(
                NonMatching,
                "JSystem/J3DGraphLoader/J3DMaterialFactory.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/J3DGraphLoader/J3DMaterialFactory_v21.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/J3DGraphLoader/J3DModelLoader.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                Matching,
                "JSystem/J3DGraphLoader/J3DModelLoaderCalcSize.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/J3DGraphLoader/J3DJointFactory.cpp",
                mw_version="Wii/1.3",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/J3DGraphLoader/J3DShapeFactory.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/J3DGraphLoader/J3DAnmLoader.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
        ],
    ),
    JSys_JAudioLib(
        "JAudio2",
        [
            Object(Matching, "JSystem/JAudio2/JASCalc.cpp", cflags=cflags_jsys),
            Object(Matching, "JSystem/JAudio2/JASTaskThread.cpp", extra_cflags=["-sym off"]),
            Object(Matching, "JSystem/JAudio2/JASDvdThread.cpp"),
            Object(Matching, "JSystem/JAudio2/JASCallback.cpp"),
            Object(Matching, "JSystem/JAudio2/JASHeapCtrl.cpp"),
            Object(Matching, "JSystem/JAudio2/JASResArcLoader.cpp"),
            Object(Matching, "JSystem/JAudio2/JASProbe.cpp"),
            Object(Matching, "JSystem/JAudio2/JASReport.cpp"),
            Object(Matching, "JSystem/JAudio2/JASCmdStack.cpp"),
            Object(
                NonMatching,
                "JSystem/JAudio2/JASTrack.cpp",
                cflags=[*cflags_jsys_jaudio, "-inline off"],
            ),
            Object(Matching, "JSystem/JAudio2/JASTrackPort.cpp"),
            Object(Matching, "JSystem/JAudio2/JASRegisterParam.cpp"),
            Object(NonMatching, "JSystem/JAudio2/JASSeqCtrl.cpp"),
            Object(NonMatching, "JSystem/JAudio2/JASSeqParser.cpp"),
            Object(Matching, "JSystem/JAudio2/JASSeqReader.cpp"),
            Object(NonMatching, "JSystem/JAudio2/JASAramStream.cpp"),
            Object(Matching, "JSystem/JAudio2/JASBank.cpp"),
            Object(Matching, "JSystem/JAudio2/JASBasicBank.cpp"),
            Object(Matching, "JSystem/JAudio2/JASVoiceBank.cpp"),
            Object(Matching, "JSystem/JAudio2/JASBasicInst.cpp"),
            Object(Matching, "JSystem/JAudio2/JASDrumSet.cpp"),
            Object(Matching, "JSystem/JAudio2/JASBasicWaveBank.cpp"),
            Object(NonMatching, "JSystem/JAudio2/JASSimpleWaveBank.cpp"),
            Object(Matching, "JSystem/JAudio2/JASInstSense.cpp"),
            Object(Matching, "JSystem/JAudio2/JASInstRand.cpp"),
            Object(Matching, "JSystem/JAudio2/JASWSParser.cpp"),
            Object(NonMatching, "JSystem/JAudio2/JASBNKParser.cpp"),
            Object(Matching, "JSystem/JAudio2/JASWaveArcLoader.cpp"),
            Object(NonMatching, "JSystem/JAudio2/JASChannel.cpp"),
            Object(Matching, "JSystem/JAudio2/JASLfo.cpp"),
            Object(Matching, "JSystem/JAudio2/JASOscillator.cpp"),
            Object(Matching, "JSystem/JAudio2/JASAiCtrl.cpp"),
            Object(Matching, "JSystem/JAudio2/JASAudioThread.cpp"),
            Object(Matching, "JSystem/JAudio2/JASAudioReseter.cpp"),
            Object(Matching, "JSystem/JAudio2/JASDSPChannel.cpp"),
            Object(Matching, "JSystem/JAudio2/JASDSPInterface.cpp"),
            Object(Matching, "JSystem/JAudio2/JASDriverIF.cpp"),
            Object(Matching, "JSystem/JAudio2/JASSoundParams.cpp"),
            Object(Matching, "JSystem/JAudio2/JAIAudible.cpp"),
            Object(Matching, "JSystem/JAudio2/JAIAudience.cpp"),
            Object(NonMatching, "JSystem/JAudio2/JAISe.cpp"),
            Object(NonMatching, "JSystem/JAudio2/JAISeMgr.cpp"),
            Object(Matching, "JSystem/JAudio2/JAISeq.cpp"),
            Object(Matching, "JSystem/JAudio2/JAISeqDataMgr.cpp"),
            Object(Matching, "JSystem/JAudio2/JAISeqMgr.cpp"),
            Object(NonMatching, "JSystem/JAudio2/JAISound.cpp"),
            Object(Matching, "JSystem/JAudio2/JAISoundChild.cpp"),
            Object(Matching, "JSystem/JAudio2/JAISoundHandles.cpp"),
            Object(Matching, "JSystem/JAudio2/JAISoundInfo.cpp"),
            Object(Matching, "JSystem/JAudio2/JAISoundParams.cpp"),
            Object(Matching, "JSystem/JAudio2/JAISoundStarter.cpp"),
            Object(Matching, "JSystem/JAudio2/JAIStream.cpp"),
            Object(Matching, "JSystem/JAudio2/JAIStreamDataMgr.cpp"),
            Object(Matching, "JSystem/JAudio2/JAIStreamMgr.cpp"),
            Object(Matching, "JSystem/JAudio2/JAUAudience.cpp"),
            Object(Matching, "JSystem/JAudio2/JAUAudioArcInterpreter.cpp"),
            Object(
                Matching,
                "JSystem/JAudio2/JAUAudioArcLoader.cpp",
                extra_cflags=["-sym off"],
            ),
            Object(Matching, "JSystem/JAudio2/JAUBankTable.cpp"),
            Object(Matching, "JSystem/JAudio2/JAUInitializer.cpp"),
            Object(NonMatching, "JSystem/JAudio2/JAUSectionHeap.cpp"),
            Object(Matching, "JSystem/JAudio2/JAUSeqCollection.cpp"),
            Object(Matching, "JSystem/JAudio2/JAUSeqDataBlockMgr.cpp"),
            Object(Matching, "JSystem/JAudio2/JAUSoundAnimator.cpp"),
            Object(Matching, "JSystem/JAudio2/JAUSoundMgr.cpp"),
            Object(Matching, "JSystem/JAudio2/JAUSoundObject.cpp"),
            Object(NonMatching, "JSystem/JAudio2/JAUSoundTable.cpp"),
            Object(Matching, "JSystem/JAudio2/JAUStdSoundInfo.cpp"),
            Object(Matching, "JSystem/JAudio2/JAUStreamFileTable.cpp"),
        ],
    ),
    JSysLib(
        "JGadget",
        [
            Object(
                Matching, "JSystem/JGadget/hashcode.cpp", extra_cflags=["-ipa file"]
            ),
            Object(
                Matching, "JSystem/JGadget/linklist.cpp", extra_cflags=["-ipa file", "-func_align 16"]
            ),
        ],
    ),
    JSysLib(
        "JKernel",
        [
            Object(
                NonMatching, "JSystem/JKernel/JKRHeap.cpp", extra_cflags=["-ipa file"]
            ),
            Object(Matching, "JSystem/JKernel/JKRExpHeap.cpp"),
            Object(NonMatching, "JSystem/JKernel/JKRSolidHeap.cpp"),
            Object(Matching, "JSystem/JKernel/JKRUnitHeap.cpp"),
            Object(Matching, "JSystem/JKernel/JKRDisposer.cpp"),
            Object(
                NonMatching,
                "JSystem/JKernel/JKRThread.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                Matching,
                "JSystem/JKernel/JKRAram.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                Matching,
                "JSystem/JKernel/JKRAramHeap.cpp",
                extra_cflags=["-ipa file", "-func_align 16"],
            ),
            Object(Matching, "JSystem/JKernel/JKRAramBlock.cpp"),
            Object(Matching, "JSystem/JKernel/JKRAramPiece.cpp"),
            Object(Matching, "JSystem/JKernel/JKRAramStream.cpp"),
            Object(
                Matching,
                "JSystem/JKernel/JKRFileLoader.cpp",
                extra_cflags=["-ipa file"],
            ),
            Object(Matching, "JSystem/JKernel/JKRFileFinder.cpp"),
            Object(Matching, "JSystem/JKernel/JKRArchivePub.cpp"),
            Object(Matching, "JSystem/JKernel/JKRArchivePri.cpp"),
            Object(Matching, "JSystem/JKernel/JKRMemArchive.cpp"),
            Object(Matching, "JSystem/JKernel/JKRAramArchive.cpp"),
            Object(Matching, "JSystem/JKernel/JKRDvdArchive.cpp"),
            Object(Matching, "JSystem/JKernel/JKRCompArchive.cpp"),
            Object(
                Matching,
                "JSystem/JKernel/JKRDvdFile.cpp",
                extra_cflags=["-ipa file", "-func_align 16"],
            ),
            Object(
                Matching, "JSystem/JKernel/JKRDvdRipper.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/JKernel/JKRDvdAramRipper.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(Matching, "JSystem/JKernel/JKRDecomp.cpp"),
        ],
    ),
    JSysLib(
        "JMath",
        [
            Object(Matching, "JSystem/JMath/JMath.cpp", extra_cflags=["-opt nocse"]),
            Object(Matching, "JSystem/JMath/random.cpp"),
            Object(
                Matching,
                "JSystem/JMath/JMATrigonometric.cpp",
                extra_cflags=["-opt nocse", "-ipa file"],
            ),
        ],
    ),
    JSys_JParticleLib(
        "JParticle",
        [
            Object(Matching, "JSystem/JParticle/JPAResourceManager.cpp"),
            Object(NonMatching, "JSystem/JParticle/JPAResource.cpp"),
            Object(
                NonMatching,
                "JSystem/JParticle/JPABaseShape.cpp",
                extra_cflags=["-sym on"],
            ),
            Object(
                NonMatching,
                "JSystem/JParticle/JPAExtraShape.cpp",
                extra_cflags=["-opt nocse"],
            ),
            Object(Matching, "JSystem/JParticle/JPAChildShape.cpp"),
            Object(Matching, "JSystem/JParticle/JPAExTexShape.cpp"),
            Object(
                NonMatching,
                "JSystem/JParticle/JPADynamicsBlock.cpp",
                extra_cflags=["-opt nolifetimes,nocse,noprop", "-sym on"],
            ),
            Object(Matching, "JSystem/JParticle/JPAFieldBlock.cpp"),
            Object(Matching, "JSystem/JParticle/JPAKeyBlock.cpp"),
            Object(Matching, "JSystem/JParticle/JPATexture.cpp", extra_cflags=["-ipa off"]
            ),
            Object(Matching, "JSystem/JParticle/JPAResourceLoader.cpp"),
            Object(Matching, "JSystem/JParticle/JPAEmitterManager.cpp"),
            Object(Matching, "JSystem/JParticle/JPAEmitter.cpp"),
            Object(NonMatching, "JSystem/JParticle/JPAParticle.cpp"),
            Object(
                Matching,
                "JSystem/JParticle/JPAMath.cpp",
                extra_cflags=["-opt nolifetimes,nocse"],
            ),
        ],
    ),
    JSysLib(
        "JSupport",
        [
            Object(Matching, "JSystem/JSupport/JSUList.cpp"),
            Object(
                Matching,
                "JSystem/JSupport/JSUInputStream.cpp",
                extra_cflags=["-ipa file"],
            ),
            Object(
                Matching,
                "JSystem/JSupport/JSUOutputStream.cpp",
                extra_cflags=["-ipa file"],
            ),
            Object(
                Matching,
                "JSystem/JSupport/JSUMemoryStream.cpp",
                extra_cflags=["-ipa file"],
            ),
            Object(
                Matching,
                "JSystem/JSupport/JSUFileStream.cpp",
                extra_cflags=["-ipa file"],
            ),
        ],
    ),
    JSysLib(
        "JUtility",
        [
            Object(Matching, "JSystem/JUtility/JUTTexture.cpp"),
            Object(Matching, "JSystem/JUtility/JUTPalette.cpp"),
            Object(Matching, "JSystem/JUtility/JUTNameTab.cpp"),
            Object(Matching, "JSystem/JUtility/JUTFont.cpp"),
            Object(
                NonMatching,
                "JSystem/JUtility/JUTException.cpp",
                extra_cflags=["-ipa file", "-sym on"],
            ),
            Object(NonMatching, "JSystem/JUtility/JUTDirectPrint.cpp"),
            Object(Matching, "JSystem/JUtility/JUTAssert.cpp"),
            Object(Matching, "JSystem/JUtility/JUTVideo.cpp"),
            Object(Matching, "JSystem/JUtility/JUTXfb.cpp"),
            Object(Matching, "JSystem/JUtility/JUTConsole.cpp"),
            Object(Matching, "JSystem/JUtility/JUTDbPrint.cpp"),
        ],
    ),
    RFLib(
        "RVLFaceLib",
        [
            Object(NonMatching, "RVLFaceLib/RFL_System.c"),
            Object(Matching, "RVLFaceLib/RFL_NANDLoader.c"),
            Object(NonMatching, "RVLFaceLib/RFL_NANDAccess.c"),
            Object(NonMatching, "RVLFaceLib/RFL_Model.c"),
            Object(NonMatching, "RVLFaceLib/RFL_MakeTex.c"),
            Object(NonMatching, "RVLFaceLib/RFL_Icon.c"),
            Object(Matching, "RVLFaceLib/RFL_HiddenDatabase.c"),
            Object(Matching, "RVLFaceLib/RFL_Database.c"),
            Object(Matching, "RVLFaceLib/RFL_Controller.c"),
            Object(Matching, "RVLFaceLib/RFL_MiddleDatabase.c"),
            Object(Matching, "RVLFaceLib/RFL_DefaultDatabase.c"),
            Object(NonMatching, "RVLFaceLib/RFL_DataUtility.c"),
            Object(Matching, "RVLFaceLib/RFL_Format.c"),
        ],
    ),
    {
        "lib": "Runtime.PPCEABI.H",
        "mw_version": config.linker_version,
        "cflags": cflags_runtime,
        "progress_category": "sdk",  # str | List[str]
        "objects": [
            Object(Matching, "Runtime/ptmf.c"),
            Object(Matching, "Runtime/runtime.c"),
            Object(Matching, "Runtime/global_destructor_chain.c"),
            Object(Matching, "Runtime/__init_cpp_exceptions.cpp"),
            Object(Matching, "Runtime/__mem.c"),
            Object(Matching, "Runtime/__va_arg.c", mw_version="Wii/1.0"),
            Object(Matching, "Runtime/Gecko_ExceptionPPC.cpp"),
        ],
    },
    GameLib(
        "LiveActor",
        [
            Object(NonMatching, "Game/LiveActor/ActorAnimKeeper.cpp"),
            Object(Matching, "Game/LiveActor/ActorCameraInfo.cpp"),
            Object(Matching, "Game/LiveActor/ActorLightCtrl.cpp"),
            Object(Matching, "Game/LiveActor/ActorStateKeeper.cpp"),
            Object(NonMatching, "Game/LiveActor/Binder.cpp"),
            Object(Matching, "Game/LiveActor/BreakModel.cpp"),
            Object(Matching, "Game/LiveActor/ChangeObj.cpp"),
            Object(Matching, "Game/LiveActor/ClippingActorHolder.cpp"),
            Object(Matching, "Game/LiveActor/ClippingActorInfo.cpp"),
            Object(Matching, "Game/LiveActor/ClippingDirector.cpp"),
            Object(Matching, "Game/LiveActor/ClippingGroupHolder.cpp"),
            Object(Matching, "Game/LiveActor/ClippingJudge.cpp"),
            Object(Matching, "Game/LiveActor/HitSensor.cpp"),
            Object(Matching, "Game/LiveActor/HitSensorInfo.cpp"),
            Object(Matching, "Game/LiveActor/HitSensorKeeper.cpp"),
            Object(Matching, "Game/LiveActor/IKJointCtrl.cpp"),
            Object(Matching, "Game/LiveActor/LiveActor.cpp"),
            Object(Matching, "Game/LiveActor/LiveActorFlag.cpp"),
            Object(Matching, "Game/LiveActor/LiveActorGroup.cpp"),
            Object(NonMatching, "Game/LiveActor/LiveActorGroupArray.cpp"),
            Object(Matching, "Game/LiveActor/LodCtrl.cpp"),
            Object(Matching, "Game/LiveActor/MaterialCtrl.cpp"),
            Object(Matching, "Game/LiveActor/MessageSensorHolder.cpp"),
            Object(NonMatching, "Game/LiveActor/MirrorActor.cpp"),
            Object(Matching, "Game/LiveActor/ModelObj.cpp"),
            Object(Matching, "Game/LiveActor/Nerve.cpp"),
            Object(Matching, "Game/LiveActor/PartsModel.cpp"),
            Object(Matching, "Game/LiveActor/RailObj.cpp"),
            Object(Matching, "Game/LiveActor/RailRider.cpp"),
            Object(NonMatching, "Game/LiveActor/SensorHitChecker.cpp"),
            Object(Matching, "Game/LiveActor/ShadowController.cpp"),
            Object(Matching, "Game/LiveActor/ShadowDrawer.cpp"),
            Object(Matching, "Game/LiveActor/ShadowSurfaceBox.cpp"),
            Object(NonMatching, "Game/LiveActor/ShadowSurfaceCircle.cpp"),
            Object(Matching, "Game/LiveActor/ShadowSurfaceDrawer.cpp"),
            Object(Matching, "Game/LiveActor/ShadowSurfaceOval.cpp"),
            Object(Matching, "Game/LiveActor/ShadowVolumeBox.cpp"),
            Object(Matching, "Game/LiveActor/ShadowVolumeCylinder.cpp"),
            Object(Matching, "Game/LiveActor/ShadowVolumeDrawer.cpp"),
            Object(Matching, "Game/LiveActor/ShadowVolumeFlatModel.cpp"),
            Object(Matching, "Game/LiveActor/ShadowVolumeLine.cpp"),
            Object(Matching, "Game/LiveActor/ShadowVolumeModel.cpp"),
            Object(Matching, "Game/LiveActor/ShadowVolumeOval.cpp"),
            Object(Matching, "Game/LiveActor/ShadowVolumeOvalPole.cpp"),
            Object(Matching, "Game/LiveActor/ShadowVolumeSphere.cpp"),
            Object(Matching, "Game/LiveActor/Spine.cpp"),
        ],
    ),
    GameLib(
        "Map",
        [
            Object(Matching, "Game/Map/BezierRail.cpp"),
            Object(NonMatching, "Game/Map/CollisionCode.cpp"),
            Object(Matching, "Game/Map/RailGraph.cpp"),
            Object(Matching, "Game/Map/RailGraphEdge.cpp"),
            Object(Matching, "Game/Map/RailGraphIter.cpp"),
            Object(Matching, "Game/Map/RailGraphNode.cpp"),
            Object(NonMatching, "Game/Map/RailPart.cpp"),
            Object(Matching, "Game/Map/StageSwitch.cpp"),
            Object(Matching, "Game/Map/SwitchSynchronizer.cpp"),
            Object(NonMatching, "Game/Map/SwitchWatcher.cpp"),
        ],
    ),
    GameLib(
        "NameObj",
        [
            Object(Matching, "Game/NameObj/MovementOnOffGroupHolder.cpp"),
            Object(Matching, "Game/NameObj/NameObj.cpp"),
            Object(Matching, "Game/NameObj/NameObjAdaptor.cpp"),
            Object(NonMatching, "Game/NameObj/NameObjCategoryList.cpp"),
            Object(Matching, "Game/NameObj/NameObjGroup.cpp"),
            Object(NonMatching, "Game/NameObj/NameObjHolder.cpp"),
            Object(Matching, "Game/NameObj/NameObjRegister.cpp"),
        ],
    ),
    GameLib(
        "Ride",
        [
            Object(NonMatching, "Game/Ride/TubeSlider.cpp"),
            Object(NonMatching, "Game/Ride/TubeSliderCoinCreator.cpp"),
            Object(Matching, "Game/Ride/TubeSliderCrystal.cpp"),
            Object(NonMatching, "Game/Ride/TubeSliderDamageObjCreator.cpp"),
            Object(NonMatching, "Game/Ride/TubeSliderFunction.cpp"),
        ],
    ),
    GameLib(
        "System",
        [
            Object(Matching, "Game/System/ArchiveHolder.cpp"),
            Object(Matching, "Game/System/DrawSyncManager.cpp"),
            Object(Matching, "Game/System/FileHolder.cpp"),
            Object(Matching, "Game/System/FileLoader.cpp"),
            Object(Matching, "Game/System/FileLoaderThread.cpp"),
            Object(Matching, "Game/System/FileRipper.cpp"),
            Object(Matching, "Game/System/FunctionAsyncExecutor.cpp"),
            Object(Matching, "Game/System/GameSystemDataHolder.cpp"),
            Object(Matching, "Game/System/GameSystemDimmingWatcher.cpp"),
            Object(Matching, "Game/System/GameSystemErrorWatcher.cpp"),
            Object(Matching, "Game/System/GameSystemException.cpp"),
            Object(Matching, "Game/System/GameSystemFontHolder.cpp"),
            Object(Matching, "Game/System/GameSystemFrameControl.cpp"),
            Object(Matching, "Game/System/GameSystemFunction.cpp"),
            Object(Matching, "Game/System/HeapMemoryWatcher.cpp"),
            Object(Matching, "Game/System/Language.cpp"),
            Object(Matching, "Game/System/MainLoopFramework.cpp"),
            Object(Matching, "Game/System/NerveExecutor.cpp"),
            Object(Matching, "Game/System/OSThreadWrapper.cpp"),
            Object(Matching, "Game/System/PauseButtonCheckerInGame.cpp"),
            Object(NonMatching, "Game/System/PlayResultInStageHolder.cpp"),
            Object(Matching, "Game/System/RenderMode.cpp"),
            Object(Matching, "Game/System/ResourceHolder.cpp"),
            Object(
                Matching,
                "Game/System/ResourceHolderManager.cpp",
                extra_cflags=["-func_align 16"],
            ),
            Object(Matching, "Game/System/ResourceInfo.cpp"),
            Object(NonMatching, "Game/System/ScenarioDataParser.cpp"),
            Object(Matching, "Game/System/StationedArchiveLoader.cpp"),
            Object(Matching, "Game/System/WPad.cpp"),
            Object(Matching, "Game/System/WPadAcceleration.cpp"),
            Object(Matching, "Game/System/WPadButton.cpp"),
            Object(Matching, "Game/System/WPadHVSwing.cpp"),
            Object(Matching, "Game/System/WPadHolder.cpp"),
            Object(Matching, "Game/System/WPadInfoChecker.cpp"),
            Object(Matching, "Game/System/WPadLeaveWatcher.cpp"),
            Object(Matching, "Game/System/WPadPointer.cpp"),
            Object(Matching, "Game/System/WPadRumble.cpp"),
            Object(Matching, "Game/System/WPadStick.cpp"),
        ],
    ),
    GameLib(
        "Util",
        [
            Object(Matching, "Game/Util/ActionSoundUtil.cpp"),
            Object(NonMatching, "Game/Util/ActorInitUtil.cpp"),
            Object(NonMatching, "Game/Util/ActorSensorUtil.cpp"),
            Object(Matching, "Game/Util/BaseMatrixFollowTargetHolder.cpp"),
            Object(Matching, "Game/Util/CollisionPartsFilter.cpp"),
            Object(Matching, "Game/Util/Color8.cpp"),
            Object(Matching, "Game/Util/HashUtil.cpp"),
            Object(Matching, "Game/Util/JMapIdInfo.cpp"),
            Object(Matching, "Game/Util/JMapInfo.cpp"),
            Object(Matching, "Game/Util/JMapLinkInfo.cpp"),
            Object(Matching, "Game/Util/JMapUtil.cpp"),
            Object(Matching, "Game/Util/JointController.cpp"),
            Object(Matching, "Game/Util/JointRumbler.cpp"),
            Object(NonMatching, "Game/Util/LiveActorUtil.cpp"),
            Object(NonMatching, "Game/Util/MathUtil.cpp"),
            Object(NonMatching, "Game/Util/MtxUtil.cpp"),
            Object(Matching, "Game/Util/NerveUtil.cpp"),
            Object(Matching, "Game/Util/ParabolicPath.cpp"),
            Object(Matching, "Game/Util/RumbleCalculator.cpp"),
            Object(Matching, "Game/Util/SequenceUtil.cpp"),
            Object(Matching, "Game/Util/SpringValue.cpp"),
            Object(Matching, "Game/Util/SwitchEventFunctorListener.cpp"),
            Object(Matching, "Game/Util/TriangleFilter.cpp"),
            Object(Matching, "Game/Util/TriggerChecker.cpp"),
            Object(Matching, "Game/Util/ValueControl.cpp"),
        ],
    ),
    RVLLib(
        "gd",
        [
            Object(Matching, "RVL_SDK/gd/GDBase.c"),
            Object(Matching, "RVL_SDK/gd/GDGeometry.c"),
            Object(Matching, "RVL_SDK/gd/GDIndirect.c"),
            Object(Matching, "RVL_SDK/gd/GDLight.c"),
            Object(Matching, "RVL_SDK/gd/GDPixel.c"),
            Object(Matching, "RVL_SDK/gd/GDTev.c"),
            Object(Matching, "RVL_SDK/gd/GDTexture.c"),
            Object(Matching, "RVL_SDK/gd/GDTransform.c"),
        ],
    ),
    RVLLib(
        "kpad",
        [
            Object(NonMatching, "RVL_SDK/kpad/KPAD.c"),
            Object(Matching, "RVL_SDK/kpad/KMPLS.c"),
            Object(Matching, "RVL_SDK/kpad/KZMplsTestSub.c"),
        ],
    ),
    RVLLib(
        "tpl",
        [
            Object(Matching, "RVL_SDK/tpl/TPL.c"),
        ],
    ),
    RVLLibGC(
        "wenc",
        [
            Object(Matching, "RVL_SDK/wenc/wenc.c"),
        ],
        "GC/3.0a5.2",
    ),
    RVLLib(
        "rso",
        [
            Object(NonMatching, "RVL_SDK/rso/RSOLink.c"),
        ],
    ),
    RVLLibGC(
        "net",
        [
            Object(Matching, "RVL_SDK/net/nettime.c"),
            Object(Matching, "RVL_SDK/net/NETVersion.c"),
            Object(NonMatching, "RVL_SDK/net/netmemcpy.c"),
            Object(Matching, "RVL_SDK/net/netmemset.c"),
        ],
        "GC/3.0a5.2",
    ),
    RVLLibGC(
        "nwc24",
        [
            Object(Matching, "RVL_SDK/nwc24/NWC24StdAPI.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24FileAPI.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24Config.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24Utils.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24Manage.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24MsgObj.c"),
            Object(NonMatching, "RVL_SDK/nwc24/NWC24MBoxCtrl.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24Mime.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24Parser.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24MsgCommit.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24Schedule.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24DateParser.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24FriendList.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24SecretFList.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24UserId.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24Time.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24Ipc.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24Download.c"),
            Object(Matching, "RVL_SDK/nwc24/NWC24System.c"),
        ],
        "GC/3.0a5.2",
    ),
    RVLLib(
        "vf",
        [
            Object(Matching, "RVL_SDK/vf/pf_clib.c"),
            Object(
                Matching,
                "RVL_SDK/vf/pf_code.c",
                mw_version="GC/3.0a3",
                cflags=cflags_sdk_gc,
                extra_cflags=["-func_align 16"],
            ),
            Object(Matching, "RVL_SDK/vf/pf_service.c"),
            Object(
                Matching,
                "RVL_SDK/vf/pf_str.c",
                mw_version="GC/3.0a3",
                cflags=cflags_sdk_gc,
                extra_cflags=["-func_align 16"],
            ),
            Object(Matching, "RVL_SDK/vf/pf_w_clib.c"),
            Object(
                Matching,
                "RVL_SDK/vf/pf_driver.c",
                mw_version="Wii/1.0",
                cflags=cflags_sdk_gc,
                extra_cflags=["-func_align 16"],
            ),
            Object(Matching, "RVL_SDK/vf/pdm_bpb.c"),
            Object(Matching, "RVL_SDK/vf/pdm_disk.c"),
            Object(Matching, "RVL_SDK/vf/pdm_partition.c"),
            Object(Matching, "RVL_SDK/vf/pdm_mbr.c"),
            Object(Matching, "RVL_SDK/vf/pdm_dskmng.c"),
            Object(Matching, "RVL_SDK/vf/pf_cache.c"),
            Object(Matching, "RVL_SDK/vf/pf_cluster.c"),
            Object(Matching, "RVL_SDK/vf/pf_dir.c"),
            Object(Matching, "RVL_SDK/vf/pf_entry.c"),
            Object(Matching, "RVL_SDK/vf/pf_entry_iterator.c"),
            Object(Matching, "RVL_SDK/vf/pf_fat.c"),
            Object(Matching, "RVL_SDK/vf/pf_fat12.c"),
            Object(Matching, "RVL_SDK/vf/pf_fat16.c"),
            Object(Matching, "RVL_SDK/vf/pf_fat32.c"),
            Object(Matching, "RVL_SDK/vf/pf_fatfs.c"),
            Object(Matching, "RVL_SDK/vf/pf_file.c"),
            Object(Matching, "RVL_SDK/vf/pf_path.c"),
            Object(Matching, "RVL_SDK/vf/pf_sector.c"),
            Object(Matching, "RVL_SDK/vf/pf_volume.c"),
            Object(Matching, "RVL_SDK/vf/pf_cp932.c"),
            Object(Matching, "RVL_SDK/vf/pf_api_util.c"),
            Object(Matching, "RVL_SDK/vf/pf_attach.c"),
            Object(Matching, "RVL_SDK/vf/pf_detach.c"),
            Object(Matching, "RVL_SDK/vf/pf_errnum.c"),
            Object(Matching, "RVL_SDK/vf/pf_fclose.c"),
            Object(Matching, "RVL_SDK/vf/pf_finfo.c"),
            Object(Matching, "RVL_SDK/vf/pf_fopen.c"),
            Object(Matching, "RVL_SDK/vf/pf_fread.c"),
            Object(Matching, "RVL_SDK/vf/pf_fseek.c"),
            Object(Matching, "RVL_SDK/vf/pf_fwrite.c"),
            Object(Matching, "RVL_SDK/vf/pf_getdev.c"),
            Object(Matching, "RVL_SDK/vf/pf_init_prfile2.c"),
            Object(Matching, "RVL_SDK/vf/pf_remove.c"),
            Object(Matching, "RVL_SDK/vf/pf_unmount.c"),
            Object(
                Matching,
                "RVL_SDK/vf/pf_filelock.c",
                mw_version="GC/3.0a3",
                cflags=cflags_sdk_gc,
                extra_cflags=["-func_align 16"],
            ),
            Object(Matching, "RVL_SDK/vf/pf_system.c"),
            Object(
                NonMatching,
                "RVL_SDK/vf/d_vf.c",
                mw_version="GC/3.0a3",
                cflags=cflags_sdk_gc,
                ),
            Object(NonMatching, "RVL_SDK/vf/d_vf_sys.c"),
            Object(Matching, "RVL_SDK/vf/d_hash.c"),
            Object(Matching, "RVL_SDK/vf/d_time.c"),
            Object(Matching, "RVL_SDK/vf/d_common.c"),
            Object(Matching, "RVL_SDK/vf/nand_drv.c"),
            Object(Matching, "RVL_SDK/vf/sd_drv.c"),
        ],
    ),
    RVLLibGC(
        "aralt",
        [
            Object(Matching, "RVL_SDK/aralt/aralt.c", extra_cflags=["-O4,s", "-func_align 16"]),
        ],
    ),
    RVLLib(
        "base",
        [
            Object(Matching, "RVL_SDK/base/PPCArch.c"),
        ],
    ),
    RVLLib(
        "os",
        [
            Object(NonMatching, "RVL_SDK/os/OS.c"),
            Object(Matching, "RVL_SDK/os/OSAlarm.c"),
            Object(Matching, "RVL_SDK/os/OSAlloc.c"),
            Object(Matching, "RVL_SDK/os/OSArena.c"),
            Object(Matching, "RVL_SDK/os/OSAudioSystem.c"),
            Object(
                NonMatching,
                "RVL_SDK/os/OSCache.c",
                mw_version="GC/3.0a5.2",
                cflags=cflags_sdk_gc,
            ),
            Object(Matching, "RVL_SDK/os/OSContext.c"),
            Object(Matching, "RVL_SDK/os/OSError.c"),
            Object(
                NonMatching,
                "RVL_SDK/os/OSExec.c",
                extra_cflags=["-opt nolifetimes,noloop"],
            ),
            Object(Matching, "RVL_SDK/os/OSFatal.c"),
            Object(Matching, "RVL_SDK/os/OSFont.c"),
            Object(Matching, "RVL_SDK/os/OSInterrupt.c"),
            Object(Matching, "RVL_SDK/os/OSLink.c"),
            Object(
                Matching,
                "RVL_SDK/os/OSMessage.c",
                mw_version="GC/3.0a5.2",
                cflags=cflags_sdk_gc,
                extra_cflags=["-func_align 16"],
            ),
            Object(NonMatching, "RVL_SDK/os/OSMemory.c"),
            Object(
                Matching,
                "RVL_SDK/os/OSMutex.c",
                mw_version="GC/3.0a5.2",
                cflags=cflags_sdk_gc,
                extra_cflags=["-func_align 16"],
            ),
            Object(Matching, "RVL_SDK/os/OSReboot.c"),
            Object(NonMatching, "RVL_SDK/os/OSReset.c"),
            Object(Matching, "RVL_SDK/os/OSRtc.c"),
            Object(Matching, "RVL_SDK/os/OSSync.c"),
            Object(NonMatching, "RVL_SDK/os/OSThread.c"),
            Object(Matching, "RVL_SDK/os/OSTime.c"),
            Object(Matching, "RVL_SDK/os/OSUtf.c"),
            Object(Matching, "RVL_SDK/os/OSIpc.c"),
            Object(
                Matching,
                "RVL_SDK/os/OSStateTM.c",
                extra_cflags=[
                    "-flag no-opt_generateconditionalassignments",
                    "-flag no-opt_rebuildconditionals",
                ],
            ),
            Object(Matching, "RVL_SDK/os/OSPlayRecord.c"),
            Object(Matching, "RVL_SDK/os/OSStateFlags.c"),
            Object(Matching, "RVL_SDK/os/OSNet.c"),
            Object(Matching, "RVL_SDK/os/OSNandbootInfo.c"),
            Object(
                NonMatching,
                "RVL_SDK/os/OSPlayTime.c",
                mw_version="GC/3.0a5.2",
                cflags=cflags_sdk_gc,
            ),
            Object(Matching, "RVL_SDK/os/OSCrc.c"),
            Object(Matching, "RVL_SDK/os/OSLaunch.c"),
            Object(Matching, "RVL_SDK/os/__ppc_eabi_init.c"),
            Object(
                NonMatching,
                "RVL_SDK/os/init/__start.c",
                mw_version="GC/3.0a3",
                cflags=cflags_sdk_gc,
            ),
            Object(
                Matching,
                "RVL_SDK/os/init/__ppc_eabi_init.cpp",
                mw_version="GC/3.0a3",
                cflags=cflags_sdk_gc,
                extra_cflags=["-func_align 16"],
            ),
        ],
    ),
    RVLLib(
        "exi",
        [
            Object(
                Matching,
                "RVL_SDK/exi/EXIBios.c",
                extra_cflags=["-func_align 16"],
            ),
            Object(Matching, "RVL_SDK/exi/EXIUart.c", cflags=cflags_sdk_ipa),
            Object(Matching, "RVL_SDK/exi/EXICommon.c", cflags=cflags_sdk_ipa),
        ],
        cflags_sdk_exi,
    ),
    RVLLib(
        "si",
        [
            Object(Matching, "RVL_SDK/si/SIBios.c"),
            Object(Matching, "RVL_SDK/si/SISamplingRate.c"),
        ],
    ),
    RVLLib(
        "vi",
        [
            Object(Matching, "RVL_SDK/vi/vi.c"),
            Object(NonMatching, "RVL_SDK/vi/i2c.c"),
            Object(NonMatching, "RVL_SDK/vi/vi3in1.c"),
        ],
    ),
    RVLLib(
        "mtx",
        [
            Object(Matching, "RVL_SDK/mtx/mtx.c"),
            Object(Matching, "RVL_SDK/mtx/mtxvec.c"),
            Object(Matching, "RVL_SDK/mtx/mtx44.c"),
            Object(
                Matching,
                "RVL_SDK/mtx/vec.c",
                mw_version="GC/3.0a3",
                cflags=cflags_sdk_gc,
                extra_cflags=["-func_align 16"],
            ),
            Object(Matching, "RVL_SDK/mtx/quat.c"),
        ],
    ),
    RVLLib(
        "gx",
        [
            Object(Matching, "RVL_SDK/gx/GXInit.c"),
            Object(Matching, "RVL_SDK/gx/GXFifo.c"),
            Object(Matching, "RVL_SDK/gx/GXAttr.c"),
            Object(Matching, "RVL_SDK/gx/GXMisc.c"),
            Object(Matching, "RVL_SDK/gx/GXGeometry.c"),
            Object(Matching, "RVL_SDK/gx/GXFrameBuf.c"),
            Object(Matching, "RVL_SDK/gx/GXLight.c"),
            Object(Matching, "RVL_SDK/gx/GXTexture.c"),
            Object(Matching, "RVL_SDK/gx/GXBump.c"),
            Object(Matching, "RVL_SDK/gx/GXTev.c"),
            Object(Matching, "RVL_SDK/gx/GXPixel.c", extra_cflags=["-sdata 8", "-sdata2 8"]),
            Object(Matching, "RVL_SDK/gx/GXDisplayList.c"),
            Object(Matching, "RVL_SDK/gx/GXTransform.c"),
            Object(Matching, "RVL_SDK/gx/GXPerf.c"),
        ],
    ),
    RVLLib(
        "dvd",
        [
            Object(
                NonMatching,
                "RVL_SDK/dvd/dvdfs.c",
                mw_version="GC/3.0a3",
                cflags=cflags_sdk_gc,
            ),
            Object(NonMatching, "RVL_SDK/dvd/dvd.c"),
            Object(Matching, "RVL_SDK/dvd/dvdqueue.c"),
            Object(NonMatching, "RVL_SDK/dvd/dvderror.c"),
            Object(Matching, "RVL_SDK/dvd/dvdidutils.c"),
            Object(Matching, "RVL_SDK/dvd/dvdFatal.c"),
            Object(Matching, "RVL_SDK/dvd/dvdDeviceError.c"),
            Object(NonMatching, "RVL_SDK/dvd/dvd_broadway.c"),
        ],
    ),
    RVLLibGC(
        "ai",
        [
            Object(Matching, "RVL_SDK/ai/ai.c", extra_cflags=["-func_align 16"]),
        ],
    ),
    RVLLib(
        "ax",
        [
            Object(Matching, "RVL_SDK/ax/AXAlloc.c"),
            Object(Matching, "RVL_SDK/ax/AXAux.c"),
            Object(Matching, "RVL_SDK/ax/AXCL.c"),
            Object(Matching, "RVL_SDK/ax/AXVPB.c"),
        ],
    ),
    RVLLib(
        "axfx",
        [
            Object(Matching, "RVL_SDK/axfx/AXFXReverbHi.c"),
            Object(Matching, "RVL_SDK/axfx/AXFXReverbHiExp.c"),
            Object(
                Matching,
                "RVL_SDK/axfx/AXFXHooks.c",
                mw_version="GC/3.0a3",
                cflags=cflags_sdk_gc,
                extra_cflags=["-func_align 16"],
            ),
        ],
    ),
    RVLLib(
        "mem",
        [
            Object(Matching, "RVL_SDK/mem/mem_heapCommon.c"),
            Object(NonMatching, "RVL_SDK/mem/mem_expHeap.c"),
            Object(Matching, "RVL_SDK/mem/mem_allocator.c"),
            Object(Matching, "RVL_SDK/mem/mem_list.c"),
        ],
    ),
    RVLLib(
        "dsp",
        [
            Object(Matching, "RVL_SDK/dsp/dsp.c"),
            Object(Matching, "RVL_SDK/dsp/dsp_debug.c"),
            Object(Matching, "RVL_SDK/dsp/dsp_task.c"),
        ],
    ),
    RVLLib(
        "nand",
        [
            Object(NonMatching, "RVL_SDK/nand/nand.c"),
            Object(Matching, "RVL_SDK/nand/NANDOpenClose.c"),
            Object(
                NonMatching,
                "RVL_SDK/nand/NANDCore.c",
                mw_version="GC/3.0a3",
                cflags=cflags_sdk_gc,
            ),
            Object(Matching, "RVL_SDK/nand/NANDCheck.c"),
            Object(NonMatching, "RVL_SDK/nand/NANDLogging.c"),
            Object(Matching, "RVL_SDK/nand/NANDErrorMessage.c"),
        ],
    ),
    RVLLib(
        "sc",
        [
            Object(NonMatching, "RVL_SDK/sc/scsystem.c"),
            Object(
                Matching,
                "RVL_SDK/sc/scapi.c",
                mw_version="GC/3.0a3",
                cflags=[*cflags_sdk_gc, "-func_align 16"],
            ),
            Object(Matching, "RVL_SDK/sc/scapi_prdinfo.c"),
        ],
    ),
    RVLLib(
        "arc",
        [
            Object(Matching, "RVL_SDK/arc/arc.c"),
        ],
    ),
    RVLLib(
        "esp",
        [
            Object(Matching, "RVL_SDK/esp/esp.c"),
        ],
    ),
    RVLLib(
        "ipc",
        [
            Object(
                Matching,
                "RVL_SDK/ipc/ipcMain.c",
                mw_version="GC/3.0a3",
                cflags=cflags_sdk_gc,
                extra_cflags=["-func_align 16"],
            ),
            Object(NonMatching, "RVL_SDK/ipc/ipcclt.c"),
            Object(Matching, "RVL_SDK/ipc/memory.c"),
            Object(NonMatching, "RVL_SDK/ipc/ipcProfile.c"),
        ],
    ),
    RVLLib(
        "fs",
        [
            Object(Matching, "RVL_SDK/fs/fs.c"),
        ],
    ),
    RVLLib(
        "pad",
        [
            Object(Matching, "RVL_SDK/pad/Pad.c"),
        ],
    ),
    RVLLib(
        "wpad",
        [
            Object(NonMatching, "RVL_SDK/wpad/WPAD.c", extra_cflags=["-fp off"]),
            Object(NonMatching, "RVL_SDK/wpad/WPADHIDParser.c"),
            Object(NonMatching, "RVL_SDK/wpad/WPADEncrypt.c"),
            Object(NonMatching, "RVL_SDK/wpad/WPADMem.c"),
            Object(Matching, "RVL_SDK/wpad/lint.c"),
        ],
    ),
    RVLLib(
        "wud",
        [
            Object(NonMatching, "RVL_SDK/wud/WUD.c"),
            Object(NonMatching, "RVL_SDK/wud/WUDHidHost.c"),
        ],
    ),
    RVLLib(
        "euart",
        [
            Object(Matching, "RVL_SDK/euart/euart.c"),
        ],
    ),
    RVLLib(
        "usb",
        [
            Object(NonMatching, "RVL_SDK/usb/usb.c"),
        ],
    ),
    RVLLibGC(
        "bte",
        [
            Object(
                Matching,
                "RVL_SDK/bte/gki_buffer.c",
                mw_version="Wii/1.0",
                cflags=cflags_sdk_ipa,
            ),
            Object(
                Matching,
                "RVL_SDK/bte/gki_time.c",
                mw_version="Wii/1.0",
                cflags=cflags_sdk_ipa,
                extra_cflags=["-func_align 16"],
            ),
            Object(
                Matching,
                "RVL_SDK/bte/gki_ppc.c",
                mw_version="Wii/1.0",
                cflags=cflags_sdk_ipa,
                extra_cflags=["-func_align 16"],
            ),
            Object(
                Matching,
                "RVL_SDK/bte/hcisu_h2.c",
                mw_version="Wii/1.0",
                cflags=cflags_sdk_ipa,
            ),
            Object(NonMatching, "RVL_SDK/bte/uusb_ppc.c", mw_version="GC/3.0a5.2"),
            Object(Matching, "RVL_SDK/bte/bta_dm_cfg.c"),
            Object(Matching, "RVL_SDK/bte/bta_hh_cfg.c"),
            Object(Matching, "RVL_SDK/bte/bta_sys_cfg.c"),
            Object(Matching, "RVL_SDK/bte/bte_hcisu.c", extra_cflags=["-func_align 16"]),
            Object(Matching, "RVL_SDK/bte/bte_init.c"),
            Object(
                Matching,
                "RVL_SDK/bte/bte_logmsg.c",
                mw_version="Wii/1.0",
                cflags=cflags_sdk_ipa,
            ),
            Object(
                Matching,
                "RVL_SDK/bte/bte_main.c",
                mw_version="Wii/1.0",
                cflags=cflags_sdk_ipa,
            ),
            Object(Matching, "RVL_SDK/bte/btu_task1.c", mw_version="Wii/1.0", cflags=cflags_sdk_ipa),
            Object(Matching, "RVL_SDK/bte/bd.c"),
            Object(Matching, "RVL_SDK/bte/bta_sys_conn.c"),
            Object(Matching, "RVL_SDK/bte/bta_sys_main.c"),
            Object(Matching, "RVL_SDK/bte/ptim.c"),
            Object(Matching, "RVL_SDK/bte/utl.c"),
            Object(Matching, "RVL_SDK/bte/bta_dm_act.c"),
            Object(Matching, "RVL_SDK/bte/bta_dm_api.c"),
            Object(Matching, "RVL_SDK/bte/bta_dm_main.c"),
            Object(Matching, "RVL_SDK/bte/bta_dm_pm.c"),
            Object(Matching, "RVL_SDK/bte/bta_hh_act.c"),
            Object(Matching, "RVL_SDK/bte/bta_hh_api.c"),
            Object(Matching, "RVL_SDK/bte/bta_hh_main.c"),
            Object(Matching, "RVL_SDK/bte/bta_hh_utils.c"),
            Object(Matching, "RVL_SDK/bte/btm_acl.c"),
            Object(Matching, "RVL_SDK/bte/btm_dev.c"),
            Object(Matching, "RVL_SDK/bte/btm_devctl.c"),
            Object(Matching, "RVL_SDK/bte/btm_discovery.c"),
            Object(Matching, "RVL_SDK/bte/btm_inq.c"),
            Object(Matching, "RVL_SDK/bte/btm_main.c"),
            Object(Matching, "RVL_SDK/bte/btm_pm.c"),
            Object(Matching, "RVL_SDK/bte/btm_sco.c"),
            Object(Matching, "RVL_SDK/bte/btm_sec.c"),
            Object(Matching, "RVL_SDK/bte/btu_hcif.c"),
            Object(Matching, "RVL_SDK/bte/btu_init.c"),
            Object(Matching, "RVL_SDK/bte/wbt_ext.c"),
            Object(Matching, "RVL_SDK/bte/gap_api.c"),
            Object(Matching, "RVL_SDK/bte/gap_conn.c"),
            Object(Matching, "RVL_SDK/bte/gap_utils.c"),
            Object(Matching, "RVL_SDK/bte/hcicmds.c"),
            Object(Matching, "RVL_SDK/bte/hidd_api.c"),
            Object(Matching, "RVL_SDK/bte/hidd_conn.c"),
            Object(Matching, "RVL_SDK/bte/hidd_mgmt.c"),
            Object(Matching, "RVL_SDK/bte/hidd_pm.c"),
            Object(Matching, "RVL_SDK/bte/hidh_api.c"),
            Object(Matching, "RVL_SDK/bte/hidh_conn.c"),
            Object(Matching, "RVL_SDK/bte/l2c_api.c"),
            Object(Matching, "RVL_SDK/bte/l2c_csm.c"),
            Object(Matching, "RVL_SDK/bte/l2c_link.c"),
            Object(Matching, "RVL_SDK/bte/l2c_main.c"),
            Object(Matching, "RVL_SDK/bte/l2c_utils.c"),
            Object(
                Matching,
                "RVL_SDK/bte/port_api.c",
                mw_version="Wii/1.0",
                cflags=cflags_sdk,
                extra_cflags=["-ipa file", "-func_align 4"],
            ),
            Object(Matching, "RVL_SDK/bte/port_rfc.c"),
            Object(Matching, "RVL_SDK/bte/port_utils.c"),
            Object(Matching, "RVL_SDK/bte/rfc_l2cap_if.c"),
            Object(Matching, "RVL_SDK/bte/rfc_mx_fsm.c"),
            Object(Matching, "RVL_SDK/bte/rfc_port_fsm.c"),
            Object(Matching, "RVL_SDK/bte/rfc_port_if.c"),
            Object(Matching, "RVL_SDK/bte/rfc_ts_frames.c"),
            Object(Matching, "RVL_SDK/bte/rfc_utils.c"),
            Object(Matching, "RVL_SDK/bte/sdp_api.c"),
            Object(Matching, "RVL_SDK/bte/sdp_db.c"),
            Object(Matching, "RVL_SDK/bte/sdp_discovery.c"),
            Object(Matching, "RVL_SDK/bte/sdp_main.c"),
            Object(Matching, "RVL_SDK/bte/sdp_server.c"),
            Object(Matching, "RVL_SDK/bte/sdp_utils.c"),
        ],
    ),
    NWLib(
        "libnw4r_ut",
        [
            Object(Matching, "nw4r/ut/ut_LinkList.cpp"),
            Object(Matching, "nw4r/ut/ut_binaryFileFormat.cpp"),
            Object(Matching, "nw4r/ut/ut_CharStrmReader.cpp"),
            Object(NonMatching, "nw4r/ut/ut_TagProcessorBase.cpp"),
            Object(Matching, "nw4r/ut/ut_Font.cpp"),
            Object(NonMatching, "nw4r/ut/ut_ResFontBase.cpp"),
            Object(Matching, "nw4r/ut/ut_ResFont.cpp"),
            Object(Matching, "nw4r/ut/ut_CharWriter.cpp"),
            Object(NonMatching, "nw4r/ut/ut_TextWriterBase.cpp"),
        ],
    ),
    NWLib(
        "libnw4r_db",
        [
            Object(Matching, "nw4r/db/db_console.cpp"),
            Object(Matching, "nw4r/db/db_assert.cpp"),
            Object(NonMatching, "nw4r/db/db_warning.cpp"),
        ],
    ),
    NWLib(
        "libnw4r_math",
        [
            Object(Matching, "nw4r/math/math_triangular.cpp"),
            Object(Matching, "nw4r/math/math_types.cpp"),
        ],
    ),
    NWLib(
        "libnw4r_lyt",
        [
            Object(Matching, "nw4r/lyt/lyt_init.cpp"),
            Object(NonMatching, "nw4r/lyt/lyt_pane.cpp"),
            Object(Matching, "nw4r/lyt/lyt_group.cpp"),
            Object(NonMatching, "nw4r/lyt/lyt_layout.cpp"),
            Object(NonMatching, "nw4r/lyt/lyt_picture.cpp"),
            Object(NonMatching, "nw4r/lyt/lyt_textBox.cpp"),
            Object(NonMatching, "nw4r/lyt/lyt_window.cpp"),
            Object(Matching, "nw4r/lyt/lyt_bounding.cpp"),
            Object(Matching, "nw4r/lyt/lyt_material.cpp"),
            Object(Matching, "nw4r/lyt/lyt_texMap.cpp"),
            Object(Matching, "nw4r/lyt/lyt_drawInfo.cpp"),
            Object(NonMatching, "nw4r/lyt/lyt_animation.cpp"),
            Object(Matching, "nw4r/lyt/lyt_resourceAccessor.cpp"),
            Object(NonMatching, "nw4r/lyt/lyt_common.cpp"),
        ],
    ),
    MSLLib(
        "MSL_C",
        [
            Object(Matching, "MSL_C/alloc.c"),
            Object(Matching, "MSL_C/errno.c"),
            Object(Matching, "MSL_C/ansi_files.c"),
            Object(Matching, "MSL_C/ansi_fp.c"),
            Object(Matching, "MSL_C/arith.c"),
            Object(Matching, "MSL_C/ctype.c"),
            Object(Matching, "MSL_C/locale.c"),
            Object(Matching, "MSL_C/buffer_io.c"),
            Object(Matching, "MSL_C/direct_io.c"),
            Object(Matching, "MSL_C/file_io.c"),
            Object(Matching, "MSL_C/FILE_POS.c"),
            Object(Matching, "MSL_C/mbstring.c"),
            Object(Matching, "MSL_C/mem.c"),
            Object(Matching, "MSL_C/mem_funcs.c"),
            Object(Matching, "MSL_C/math_api.c"),
            Object(Matching, "MSL_C/misc_io.c"),
            Object(Matching, "MSL_C/printf.c"),
            Object(Matching, "MSL_C/float.c"),
            Object(Matching, "MSL_C/scanf.c"),
            Object(Matching, "MSL_C/signal.c"),
            Object(Matching, "MSL_C/string.c"),
            Object(Matching, "MSL_C/strtold.c"),
            Object(Matching, "MSL_C/wctype.c"),
            Object(Matching, "MSL_C/strtoul.c"),
            Object(Matching, "MSL_C/wcstoul.c"),
            Object(Matching, "MSL_C/wmem.c"),
            Object(Matching, "MSL_C/wprintf.c"),
            Object(Matching, "MSL_C/wscanf.c"),
            Object(Matching, "MSL_C/wstring.c"),
            Object(Matching, "MSL_C/wchar_io.c"),
            Object(Matching, "MSL_C/uart_console_io_gcn.c"),
            Object(Matching, "MSL_C/abort_exit_ppc_eabi.c"),
            Object(Matching, "MSL_C/secure_error.c"),
            Object(Matching, "MSL_C/math_sun.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/e_acos.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/e_asin.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/e_atan2.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/e_fmod.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/e_log.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/e_log10.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/e_pow.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/e_rem_pio2.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/k_cos.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/k_rem_pio2.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/k_sin.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/k_tan.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/s_atan.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/s_ceil.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/s_copysign.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/s_cos.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/s_floor.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/s_frexp.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/s_ldexp.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/s_sin.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/s_tan.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/w_acos.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/w_asin.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/w_atan2.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/w_fmod.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/w_log10.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/w_pow.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/e_sqrt.c"),
            Object(Matching, "MSL_C/PPC_EABI/SRC/math_ppc.c"),
            Object(Matching, "MSL_C/MSL_Common_Embedded/Math/Double_precision/w_sqrt.c"),
            Object(Matching, "MSL_C/extras.c"),
        ],
    ),
    TRKLib(
        "MetroTRK",
        [
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Processor/ppc/Generic/exception.s"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Processor/ppc/Export/targsupp.s"),
            Object(Matching, "MetroTRK/gamedev/cust_connection/cc/exi2/GCN/EXI2_GDEV_GCN/main.c"),
            Object(Matching, "MetroTRK/gamedev/cust_connection/utils/gc/MWCriticalSection_gc.c"),
            Object(Matching, "MetroTRK/gamedev/cust_connection/utils/common/CircleBuffer.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Processor/ppc/Generic/flush_cache.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Portable/main_TRK.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Portable/mainloop.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Portable/mem_TRK.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Portable/dispatch.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Os/dolphin/dolphin_trk.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Os/dolphin/dolphin_trk_glue.c", extra_cflags=["-str pool"]),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Portable/notify.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Portable/nubevent.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Portable/nubinit.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Portable/serpoll.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Portable/string_TRK.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Portable/support.c", extra_cflags=["-str pool"]),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Os/dolphin/targcont.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Processor/ppc/Generic/mpc_7xx_603e.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Portable/msg.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Portable/msgbuf.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Portable/msghndlr.c", extra_cflags=["-str pool"]),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Export/mslsupp.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Processor/ppc/Generic/targimpl.c"),
            Object(Matching, "MetroTRK/debugger/embedded/MetroTRK/Os/dolphin/target_options.c"),
        ],
    ),
]

# Optional extra categories for progress tracking
# Adjust as desired for your project
config.progress_categories = [
    ProgressCategory("game", "Game Code"),
    ProgressCategory("sdk", "SDK Code"),
    ProgressCategory("nw4r", "NintendoWare Code"),
    ProgressCategory("jsys", "JSystem"),
    ProgressCategory("rfl", "RVLFaceLib"),
    ProgressCategory("msl", "MSL_C Code"),
    ProgressCategory("trk", "MetroTRK Code"),
]
config.progress_each_module = args.verbose

if args.mode == "configure":
    # Write build.ninja and objdiff.json
    generate_build(config)
elif args.mode == "progress":
    # Print progress and write progress.json
    calculate_progress(config)
else:
    sys.exit("Unknown mode: " + args.mode)
