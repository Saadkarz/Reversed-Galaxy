#pragma once

#include "JSystem/J2DGraph/J2DPane.hpp"
#include "JSystem/JUtility/JUTTexture.hpp"
#include "JSystem/JUtility/TColor.hpp"

class J2DMaterial;
class JUTPalette;
struct ResTIMG;
struct ResTLUT;

enum J2DMirror {
    /* 0 */ MIRROR0,  // temp, figure out later
    /* 1 */ J2DMirror_Y = (1 << 0),
    /* 2 */ J2DMirror_X = (1 << 1),
};

enum J2DBinding {
    /* 1 */ J2DBind_Bottom = (1 << 0),
    /* 2 */ J2DBind_Top = (1 << 1),
    /* 4 */ J2DBind_Right = (1 << 2),
    /* 8 */ J2DBind_Left = (1 << 3),

    /* 0xF */ BIND15 = 15,  // temp, figure out later
};

struct J2DPicHeader {
    /* 0x0 */ u32 mTag;
    /* 0x4 */ u32 mSize;
};

/**
 * @ingroup jsystem-j2d
 *
 */
struct J2DScrnBlockPictureParameter {
    /* 0x00 */ u16 field_0x0;
    /* 0x02 */ u16 mMaterialNum;
    /* 0x04 */ u16 field_0x4;
    /* 0x06 */ u16 field_0x6;
    /* 0x08 */ u16 field_0x8[4];
    /* 0x10 */ JGeometry::TVec2< s16 > field_0x10[4];
    /* 0x20 */ u32 mCornerColor[4];
};  // Size: 0x30

class J2DPicture : public J2DPane {
public:
    J2DPicture(JUTTexture*);

    virtual ~J2DPicture();
    virtual u16 getTypeID() const;
    virtual void drawSelf(f32, f32);
    virtual void drawSelf(f32, f32, Mtx*);
    virtual void initiate(ResTIMG const*, ResTLUT const*);
    virtual bool prepareTexture(u8);
    virtual bool append(ResTIMG const* param_0, f32 param_1);
    virtual bool append(ResTIMG const* param_0, JUTPalette* param_1, f32 param_2);
    virtual bool append(char const* param_0, f32 param_1);
    virtual bool append(char const* param_0, JUTPalette* param_1, f32 param_2);
    virtual bool append(JUTTexture* param_0, f32 param_1);
    virtual void prepend(ResTIMG const* param_0, f32 param_1);
    virtual void prepend(ResTIMG const* param_0, JUTPalette* param_1, f32 param_2);
    virtual void prepend(char const* param_0, f32 param_1);
    virtual void prepend(char const* param_0, JUTPalette* param_1, f32 param_2);
    virtual void prepend(JUTTexture* param_0, f32 param_1);
    virtual bool insert(ResTIMG const* param_0, u8 param_1, f32 param_2);
    virtual bool insert(ResTIMG const*, JUTPalette*, u8, f32);
    virtual bool insert(char const* param_0, u8 param_1, f32 param_2);
    virtual bool insert(char const*, JUTPalette*, u8, f32);
    virtual bool insert(JUTTexture*, u8, f32);
    virtual bool remove(u8);
    virtual bool remove();
    virtual bool remove(JUTTexture*);
    virtual void draw(f32 param_0, f32 param_1, bool param_2, bool param_3, bool param_4);
    virtual void draw(f32 param_0, f32 param_1, u8 param_2, bool param_3, bool param_4, bool param_5) {
        if (param_2 < mTextureNum && mTexture[param_2] != NULL) {
            draw(param_0, param_1, mTexture[param_2]->getWidth(), mTexture[param_2]->getHeight(), param_3, param_4, param_5);
        }
    }
    virtual void draw(f32, f32, f32, f32, bool, bool, bool);
    virtual void drawOut(f32 param_0, f32 param_1, f32 param_2, f32 param_3, f32 param_4, f32 param_5);
    virtual void drawOut(f32 param_0, f32 param_1, f32 param_2, f32 param_3, f32 param_4, f32 param_5, f32 param_6, f32 param_7);
    virtual void drawOut(JGeometry::TBox2< f32 > const&, JGeometry::TBox2< f32 > const&);
    virtual void load(_GXTexMapID param_0, u8 param_1);
    virtual void load(u8 param_0);

    virtual void setBlendRatio(f32 a1, f32 a2, f32 a3, f32 a4, f32 a5, f32 a6, f32 a7, f32 a8);

    /* NEW IN SMG1 */
    virtual void setBlendColorRatio(f32, f32, f32, f32, f32, f32, f32, f32);
    virtual void setBlendAlphaRatio(f32, f32, f32, f32, f32, f32, f32, f32);

    virtual const ResTIMG* changeTexture(ResTIMG const*, u8);
    virtual const ResTIMG* changeTexture(char const*, u8);
    virtual const ResTIMG* changeTexture(ResTIMG const*, u8, JUTPalette*);
    virtual const ResTIMG* changeTexture(char const*, u8, JUTPalette*);
    virtual JUTTexture* getTexture(u8 param_0) const;
    virtual u8 getTextureCount() const;
    /* vt 0x128 */ virtual bool setBlack(JUtility::TColor i_black);
    /* vt 0x12C */ virtual bool setWhite(JUtility::TColor i_white);

    virtual bool setBlackWhite(JUtility::TColor i_black, JUtility::TColor i_white);
    virtual JUtility::TColor getBlack() const;
    virtual JUtility::TColor getWhite() const;
    virtual J2DMaterial* getMaterial() const;
    virtual void drawFullSet(f32, f32, f32, f32, Mtx*);
    virtual void drawTexCoord(f32, f32, f32, f32, s16, s16, s16, s16, s16, s16, s16, s16, Mtx*);
    virtual u8 getUsableTlut(u8);
    virtual bool isUsed(ResTIMG const*);
    virtual bool isUsed(ResFONT const* param_0);
    virtual void rewriteAlpha();

    J2DPicture(u64, JGeometry::TBox2< f32 > const&, ResTIMG const*, ResTLUT const*);
    J2DPicture(ResTIMG const*);
    J2DPicture(J2DPane*, JSURandomInputStream*, JKRArchive*);
    J2DPicture();
    J2DPicture(J2DPane*, JSURandomInputStream*, J2DMaterial*);
    void private_readStream(J2DPane*, JSURandomInputStream*, JKRArchive*);
    void private_initiate(ResTIMG const*, ResTLUT const*);
    void initinfo();
    void setTevMode();
    static void swap(f32&, f32&);
    void setBlendKonstColor();
    void setBlendKonstAlpha();
    void getNewColor(JUtility::TColor*);
    void setTexCoord(JGeometry::TVec2< s16 >*, JUTTexture const*, J2DBinding, J2DMirror, bool);
    void setTexCoord(JUTTexture const*, J2DBinding, J2DMirror, bool);
    GXTlut getTlutID(ResTIMG const*, u8);

    void setCornerColor(JUtility::TColor c0, JUtility::TColor c1, JUtility::TColor c2, JUtility::TColor c3);
    void setCornerColor(JUtility::TColor c0) {
        setCornerColor(c0, c0, c0, c0);
    }

protected:
    /* CHANGED IN SMG1 -- supports 4 tex ptrs instead of 2 */
    /* 0x100 */ JUTTexture* mTexture[4];
    /* 0x108 */ u8 mTextureNum;
    /* 0x109 */ u8 field_0x109;
    /* 0x10A */ JGeometry::TVec2< s16 > field_0x10a[4];
    /* 0x11C */ f32 field_0x11c[4];
    /* 0x124 */ f32 field_0x124[4];
    /* 0x12C */ JUTPalette* mPalette;
    /* 0x130 */ JUtility::TColor mWhite;
    /* 0x134 */ JUtility::TColor mBlack;
    /* 0x138 */ JUtility::TColor mCornerColor[4];
    /* 0x148 */ JUtility::TColor mBlendKonstColor;
    /* 0x14C */ JUtility::TColor mBlendKonstAlpha;
};
