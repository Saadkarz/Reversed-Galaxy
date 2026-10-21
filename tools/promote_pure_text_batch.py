from test_single_promote import test_file

pure_text_candidates = [
    "Game/Map/RailGraph.cpp",
    "Game/System/ArchiveHolder.cpp",
    "Game/System/FileHolder.cpp",
    "JSystem/J3DGraphAnimator/J3DShapeTable.cpp",
    "JSystem/J3DGraphAnimator/J3DSkinDeform.cpp",
    "JSystem/J3DGraphBase/J3DVertex.cpp",
    "JSystem/J3DGraphLoader/J3DModelLoaderCalcSize.cpp",
    "JSystem/JAudio2/JAISoundHandles.cpp",
    "JSystem/JKernel/JKRArchivePub.cpp",
    "JSystem/JMath/random.cpp",
    "JSystem/JParticle/JPAEmitterManager.cpp",
    "RVL_SDK/bte/gki_time.c",
    "RVL_SDK/nwc24/NWC24MsgObj.c",
    "RVL_SDK/os/OSMutex.c",
    "nw4r/ut/ut_LinkList.cpp",
]

def main():
    promoted = []
    failed = []
    for c in pure_text_candidates:
        print(f"\n==========================================")
        print(f"Testing Pure Text Candidate: {c}")
        print(f"==========================================")
        if test_file(c):
            print(f">>> PROMOTED: {c}")
            promoted.append(c)
        else:
            print(f">>> FAILED: {c}")
            failed.append(c)

    print("\n==========================================")
    print(f"PURE TEXT RUN FINISHED:")
    print(f"  Promoted ({len(promoted)}): {promoted}")
    print(f"  Failed ({len(failed)}): {failed}")
    print("==========================================")

if __name__ == '__main__':
    main()
