with open('config/SB4E01/splits.txt', 'r', encoding='utf-8') as f:
    text = f.read()

replacements = [
    # 1. TriangleFilter
    (
"""Game/Util/TriangleFilter.cpp:
\t.text       start:0x80068E60 end:0x80068EB0
\t.data       start:0x80669DE8 end:0x80669DF4""",
"""Game/Util/TriangleFilter.cpp:
\t.text       start:0x80068E60 end:0x80068F80 align:16
\t.data       start:0x80669DE8 end:0x80669E00"""
    ),
    # 2. J3DSkinDeform
    (
"""JSystem/J3DGraphAnimator/J3DSkinDeform.cpp:
\t.text       start:0x8052FB60 end:0x8052FBD0 align:16""",
"""JSystem/J3DGraphAnimator/J3DSkinDeform.cpp:
\t.text       start:0x8052FB60 end:0x8052FBF0 align:16"""
    ),
    # 3. JAISoundHandles
    (
"""JSystem/JAudio2/JAISoundHandles.cpp:
\t.text       start:0x805969C0 end:0x80596A60 align:16""",
"""JSystem/JAudio2/JAISoundHandles.cpp:
\t.text       start:0x805969C0 end:0x80596AF8 align:16"""
    ),
    # 4. ClippingJudge
    (
"""Game/LiveActor/ClippingJudge.cpp:
\t.text       start:0x80230F90 end:0x802315E0
\t.data       start:0x80694EC8 end:0x80694EF8""",
"""Game/LiveActor/ClippingJudge.cpp:
\t.text       start:0x80230F90 end:0x802315E0
\t.data       start:0x80694EC8 end:0x80694EF8
\t.sdata2     start:0x807DC3E0 end:0x807DC410"""
    ),
    # 5. RailObj
    (
"""Game/LiveActor/RailObj.cpp:
\t.text       start:0x8023D100 end:0x8023D280""",
"""Game/LiveActor/RailObj.cpp:
\t.text       start:0x8023D100 end:0x8023D280
\t.data       start:0x80695890 end:0x80695900"""
    ),
    # 6. JMath
    (
"""JSystem/JMath/JMath.cpp:
\t.text       start:0x8053A730 end:0x8053A9B0 align:16""",
"""JSystem/JMath/JMath.cpp:
\t.text       start:0x8053A730 end:0x8053A9B0 align:16
\t.rodata     start:0x80654590 end:0x80654598"""
    ),
    # 7. JASRegisterParam
    (
"""JSystem/JAudio2/JASRegisterParam.cpp:
\t.text       start:0x80587DD0 end:0x80588010 align:16""",
"""JSystem/JAudio2/JASRegisterParam.cpp:
\t.text       start:0x80587DD0 end:0x80588010 align:16
\t.data       start:0x80708220 end:0x80708270"""
    ),
    # 8. JPAKeyBlock
    (
"""JSystem/JParticle/JPAKeyBlock.cpp:
\t.text       start:0x80541AF0 end:0x80541BA0 align:16""",
"""JSystem/JParticle/JPAKeyBlock.cpp:
\t.text       start:0x80541AF0 end:0x80541BA0 align:16
\t.rodata     start:0x806545E8 end:0x806545F0"""
    ),
    # 9. nw4r/ut/ut_Font
    (
"""nw4r/ut/ut_Font.cpp:
\t.text       start:0x8059E0C0 end:0x8059E170 align:16""",
"""nw4r/ut/ut_Font.cpp:
\t.text       start:0x8059E0C0 end:0x8059E170 align:16
\t.data       start:0x8070C180 end:0x8070C1B0"""
    ),
    # 10. ActorLightCtrl
    (
"""Game/LiveActor/ActorLightCtrl.cpp:
\t.text       start:0x8022BF50 end:0x8022C550""",
"""Game/LiveActor/ActorLightCtrl.cpp:
\t.text       start:0x8022BF50 end:0x8022C550
\t.rodata     start:0x80648A68 end:0x80648A70"""
    ),
    # 11. ParabolicPath
    (
"""Game/Util/ParabolicPath.cpp:
\t.text       start:0x8004EA20 end:0x8004EFA0""",
"""Game/Util/ParabolicPath.cpp:
\t.text       start:0x8004EA20 end:0x8004EFA0
\t.rodata     start:0x80645268 end:0x80645270
\t.sdata2     start:0x807D70D8 end:0x807D70E8"""
    ),
    # 12. JMapLinkInfo
    (
"""Game/Util/JMapLinkInfo.cpp:
\t.text       start:0x80067950 end:0x80067BE0""",
"""Game/Util/JMapLinkInfo.cpp:
\t.text       start:0x80067950 end:0x80067BE0
\t.data       start:0x80669D08 end:0x80669D68"""
    ),
    # 13. WPadStick
    (
"""Game/System/WPadStick.cpp:
\t.text       start:0x804D0D30 end:0x804D0FB0""",
"""Game/System/WPadStick.cpp:
\t.text       start:0x804D0D30 end:0x804D0FB0
\t.sdata2     start:0x807E19E0 end:0x807E19F0"""
    ),
    # 14. WPadPointer
    (
"""Game/System/WPadPointer.cpp:
\t.text       start:0x804D0010 end:0x804D0460""",
"""Game/System/WPadPointer.cpp:
\t.text       start:0x804D0010 end:0x804D0510
\t.rodata     start:0x8064DF40 end:0x8064DF48
\t.sdata2     start:0x807E19C8 end:0x807E19E0"""
    ),
    # 15. CollisionPartsFilter
    (
"""Game/Util/CollisionPartsFilter.cpp:
\t.text       start:0x80063800 end:0x80063850""",
"""Game/Util/CollisionPartsFilter.cpp:
\t.text       start:0x80063800 end:0x800638C0 align:16
\t.data       start:0x80669CA0 end:0x80669CD0"""
    ),
    # 16. RumbleCalculator
    (
"""Game/Util/RumbleCalculator.cpp:
\t.text       start:0x80068B30 end:0x80068CC0
\t.data       start:0x80669DD0 end:0x80669DE8""",
"""Game/Util/RumbleCalculator.cpp:
\t.text       start:0x80068B30 end:0x80068D90 align:16
\t.rodata     start:0x806452A8 end:0x806452B0
\t.data       start:0x80669DD0 end:0x80669DE8
\t.sdata2     start:0x807D7270 end:0x807D7280"""
    ),
    # 17. JointRumbler
    (
"""Game/Util/JointRumbler.cpp:
\t.text       start:0x80067EE0 end:0x80068190""",
"""Game/Util/JointRumbler.cpp:
\t.text       start:0x80067EE0 end:0x800681D0
\t.sdata2     start:0x807D7260 end:0x807D7270"""
    )
]

for old, new in replacements:
    old_c = old.replace('\r\n', '\n')
    text_c = text.replace('\r\n', '\n')
    if old_c in text_c:
        text_c = text_c.replace(old_c, new.replace('\r\n', '\n'))
        text = text_c
        print(f"Applied replacement for {old.split(':')[0]}")
    else:
        print(f"FAILED to find {old.split(':')[0]}")

with open('config/SB4E01/splits.txt', 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
print("Updated splits.txt!")
