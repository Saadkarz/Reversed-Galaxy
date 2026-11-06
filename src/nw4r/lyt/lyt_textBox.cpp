#include "nw4r/lyt/drawInfo.h"
#include "nw4r/lyt/layout.h"
#include "nw4r/lyt/resourceAccessor.h"
#include "nw4r/lyt/textBox.h"
#include "nw4r/ut/Font.h"
#include "nw4r/ut/ResFont.h"
#include "nw4r/ut/WideTextWriter.h"
#include <cstdio>
extern "C" {
#include <wstring.h>
}

namespace nw4r {
    namespace lyt {
namespace {

    inline u8 ClampColor(s16 colVal) {
        return u8(colVal < 0 ? 0 : (colVal > 255 ? 255 : colVal));
    }

    ut::Color GetColor(const GXColorS10& src) {
        GXColor dst;
        dst.r = ClampColor(src.r);
        dst.g = ClampColor(src.g);
        dst.b = ClampColor(src.b);
        dst.a = ClampColor(src.a);
        return ut::Color(dst);
    }

    inline void ReverseYAxis(math::MTX34* pMtx) {
        pMtx->m[0][1] = -pMtx->m[0][1];
        pMtx->m[1][1] = -pMtx->m[1][1];
        pMtx->m[2][1] = -pMtx->m[2][1];
    }

    template < typename T >
    int CalcLineRectImpl(ut::Rect* pRect, ut::TextWriterBase< T >* pTextWriter, const T* str, int length, f32 maxWidth, bool* pbOver) {
        typedef ut::TagProcessorBase< T > TagProcessor;

        ut::PrintContext< T > context = {pTextWriter, str, 0, 0, 0};
        const ut::Font* const pFont = pTextWriter->GetFont();
        f32 x = 0.0f;
        bool bCharSpace = false;
        ut::CharStrmReader reader = pFont->GetCharStrmReader();
        const T* prStrPos = static_cast< const T* >(reader.GetCurrentPos());

        pRect->left = 0.0f;
        pRect->right = 0.0f;
        pRect->top = ut::Min(0.0f, pTextWriter->GetLineHeight());
        pRect->bottom = ut::Max(0.0f, pTextWriter->GetLineHeight());
        *pbOver = false;

        reader.Set(str);
        ut::Rect prMaxRect = *pRect;

        for (u16 code = reader.Next(); static_cast< const T* >(reader.GetCurrentPos()) - str <= length;
             prStrPos = static_cast< const T* >(reader.GetCurrentPos()), code = reader.Next(), prMaxRect = *pRect) {
            if (code < ' ') {
                ut::Rect rect(x, 0.0f, 0.0f, 0.0f);

                context.str = static_cast< const T* >(reader.GetCurrentPos());
                context.flags = !bCharSpace ? ut::TextWriterBase< T >::CONTEXT_NO_CHAR_SPACE : 0;
                pTextWriter->SetCursorX(x);

                const typename TagProcessor::Operation operation = pTextWriter->GetTagProcessor().CalcRect(&rect, code, &context);

                reader.Set(context.str);

                pRect->left = ut::Min(pRect->left, rect.left);
                pRect->top = ut::Min(pRect->top, rect.top);
                pRect->right = ut::Max(pRect->right, rect.right);
                pRect->bottom = ut::Max(pRect->bottom, rect.bottom);

                x = pTextWriter->GetCursorX();

                if (pRect->GetWidth() > maxWidth) {
                    *pbOver = true;
                    break;
                }

                if (operation == TagProcessor::OPERATION_END_DRAW) {
                    return length;
                } else if (operation == TagProcessor::OPERATION_NO_CHAR_SPACE) {
                    bCharSpace = false;
                } else if (operation == TagProcessor::OPERATION_CHAR_SPACE) {
                    bCharSpace = true;
                } else if (operation == TagProcessor::OPERATION_NEXT_LINE) {
                    break;
                }
            } else {
                if (bCharSpace) {
                    x += pTextWriter->GetCharSpace();
                }

                bCharSpace = true;

                if (pTextWriter->IsWidthFixed()) {
                    x += pTextWriter->GetFixedWidth();
                } else {
                    x += pTextWriter->GetFont()->GetCharWidth(code) * pTextWriter->GetScaleH();
                }

                pRect->left = ut::Min(pRect->left, x);
                pRect->right = ut::Max(pRect->right, x);

                if (pRect->GetWidth() > maxWidth) {
                    *pbOver = true;
                    break;
                }
            }
        }

        if (*pbOver && prStrPos) {
            *pRect = prMaxRect;
            return prStrPos - str;
        }

        return static_cast< const T* >(reader.GetCurrentPos()) - str;
    }

    template < typename T >
    inline int CalcLineStrNum(f32* pWidth, ut::TextWriterBase< T >* pTextWriter, const T* str, int length, f32 maxWidth, bool* pbOver) {
        ut::Rect rect;
        ut::TextWriterBase< T > myCopy = *pTextWriter;

        myCopy.SetCursor(0.0f, 0.0f);
        const int ret = CalcLineRectImpl(&rect, &myCopy, str, length, maxWidth, pbOver);

        *pWidth = rect.GetWidth();
        return ret;
    }

    template < typename T >
    void CalcStringRectImpl(ut::Rect* pRect, ut::TextWriterBase< T >* pTextWriter, const T* str, int length, f32 maxWidth) {
        pRect->left = 0.0f;
        pRect->right = 0.0f;
        pRect->top = 0.0f;
        pRect->bottom = 0.0f;

        pTextWriter->SetCursor(0.0f, 0.0f);

        int remain = length;
        const T* pos = str;

        do {
            ut::Rect rect;
            bool bOver;
            const int read = CalcLineRectImpl(&rect, pTextWriter, pos, remain, maxWidth, &bOver);
            pos += read;
            remain -= read;

            pRect->left = ut::Min(pRect->left, rect.left);
            pRect->top = ut::Min(pRect->top, rect.top);
            pRect->right = ut::Max(pRect->right, rect.right);
            pRect->bottom = ut::Max(pRect->bottom, rect.bottom);

            if (bOver) {
                CalcLineRectImpl(&rect, pTextWriter, L"\n", 1, maxWidth, &bOver);

                pRect->left = ut::Min(pRect->left, rect.left);
                pRect->top = ut::Min(pRect->top, rect.top);
                pRect->right = ut::Max(pRect->right, rect.right);
                pRect->bottom = ut::Max(pRect->bottom, rect.bottom);
            }
        } while (remain > 0);
    }

    template < typename T >
    inline void CalcStringRect(ut::Rect* pRect, ut::TextWriterBase< T >* pTextWriter, const T* str, int length, f32 maxWidth) {
        ut::TextWriterBase< T > myCopy = *pTextWriter;
        CalcStringRectImpl(pRect, &myCopy, str, length, maxWidth);
    }
};  // namespace
        NW4R_UT_RUNTIME_TYPEINFO_DEFINITION(TextBox, Pane);

        TextBox::TextBox(const res::TextBox* pBlock, const ResBlockSet& resBlockSet) : Pane(pBlock) {
            u16 allocStrBufLen = static_cast< u16 >(pBlock->textBufBytes / sizeof(wchar_t));
            if (allocStrBufLen > 0) {
                allocStrBufLen -= 1;
            }

            Init(allocStrBufLen);

            if (pBlock->textStrBytes >= sizeof(wchar_t) && mTextBuf) {
                const wchar_t* const pBlockText = detail::ConvertOffsToPtr< wchar_t >(pBlock, pBlock->textStrOffset);
                const u16 resStrLen = static_cast< u16 >(pBlock->textStrBytes / sizeof(wchar_t) - 1);
                SetString(pBlockText, 0, resStrLen);
            }

            for (int i = 0; i < 2; ++i) {
                mTextColors[i] = pBlock->textCols[i];
            }

            mFontSize = pBlock->fontSize;
            mTextPosition = pBlock->textPosition;
            mBits.textAlignment = pBlock->textAlignment;
            mCharSpace = pBlock->charSpace;
            mLineSpace = pBlock->lineSpace;

            const res::Font* const fonts = detail::ConvertOffsToPtr< res::Font >(resBlockSet.pFontList, sizeof(*resBlockSet.pFontList));
            const char* const fontName = detail::ConvertOffsToPtr< char >(fonts, fonts[pBlock->fontIdx].nameStrOffset);

            if (ut::Font* pFont = resBlockSet.pResAccessor->GetFont(fontName)) {
                mpFont = pFont;
            } else if (void* fontRes = resBlockSet.pResAccessor->GetResource('font', fontName, 0)) {
                if (ut::ResFont* pResFont = Layout::NewObj< ut::ResFont >()) {
                    pResFont->SetResource(fontRes);
                    mpFont = pResFont;
                    mBits.bAllocFont = true;
                }
            }

            const u32* const matOffsTbl = detail::ConvertOffsToPtr< u32 >(resBlockSet.pMaterialList, sizeof(*resBlockSet.pMaterialList));
            const res::Material* const pResMaterial =
                detail::ConvertOffsToPtr< res::Material >(resBlockSet.pMaterialList, matOffsTbl[pBlock->materialIdx]);
            mpMaterial = Layout::NewObj< Material >(pResMaterial, resBlockSet);
        }

        void TextBox::Init(u16 allocStrLen) {
            mTextBuf = 0;
            mTextBufBytes = 0;
            mTextLen = 0;
            mpFont = 0;
            mFontSize = Size(0, 0);
            SetTextPositionH(1);
            SetTextPositionV(1);
            mLineSpace = 0;
            mCharSpace = 0;
            mpTagProcessor = 0;
            memset(&mBits, 0, sizeof(mBits));

            if (allocStrLen > 0) {
                AllocStringBuffer(allocStrLen);
            }
        }

        TextBox::~TextBox() {
            SetFont(nullptr);

            if (mpMaterial != NULL && !mpMaterial->IsUserAllocated()) {
                Layout::DeleteObj(mpMaterial);
                mpMaterial = NULL;
            }

            FreeStringBuffer();
        }

        const ut::Color TextBox::GetVtxColor(u32 idx) const {
            return GetTextColor(idx / 2);
        }

        void TextBox::SetVtxColor(u32 idx, ut::Color color) {
            SetTextColor(idx / 2, color);
        }

        void TextBox::SetTextColor(u32 type, ut::Color value) {
            mTextColors[type] = value;
        }

        u8 TextBox::GetVtxColorElement(u32 idx) const {
            return reinterpret_cast< const u8* >(&mTextColors[idx / (4 * 2)])[idx % 4];
        }

        void TextBox::SetVtxColorElement(u32 idx, u8 value) {
            reinterpret_cast< u8* >(&mTextColors[idx / (4 * 2)])[idx % 4] = value;
        }

        const ut::Rect TextBox::GetTextDrawRect() const {
            ut::WideTextWriter writer;

            return GetTextDrawRect(&writer);
        }

        const ut::Rect TextBox::GetTextDrawRect(const DrawInfo& drawInfo) const {
            ut::WideTextWriter writer;

            return GetTextDrawRect(&writer);
        }

        void TextBox::DrawSelf(const DrawInfo& drawInfo) {
            if (!mTextBuf || !mpFont || !mpMaterial) {
                return;
            }

            LoadMtx(drawInfo);

            ut::WideTextWriter writer;
            ut::Rect textRect = GetTextDrawRect(&writer);

            ut::Color topCol = detail::MultipleAlpha(mTextColors[0], mGlbAlpha);
            ut::Color btmCol = detail::MultipleAlpha(mTextColors[1], mGlbAlpha);
            writer.SetGradationMode(topCol != btmCol ? ut::CharWriter::GRADMODE_V : ut::CharWriter::GRADMODE_NONE);
            writer.SetTextColor(topCol, btmCol);
            ut::Color minCol = GetColor(mpMaterial->GetTevColor(0));
            ut::Color maxCol = GetColor(mpMaterial->GetTevColor(1));
            writer.SetColorMapping(minCol, maxCol);
            writer.SetupGX();

            GXSetAlphaCompare(GX_ALWAYS, 0, GX_AOP_AND, GX_ALWAYS, 0);

            const f32 hMag = GetTextAlignMag();
            const wchar_t* strPos = mTextBuf;
            writer.SetCursor(textRect.left, -textRect.top);
            const f32 textWidth = textRect.GetWidth();

            int remain = mTextLen;
            while (remain > 0) {
                f32 lineWidth;
                bool bOver;
                const int lineStrNum = CalcLineStrNum(&lineWidth, &writer, strPos, remain, mSize.width, &bOver);

                writer.SetCursorX(textRect.left + (textWidth - lineWidth) * hMag);
                writer.PrintMutable(strPos, lineStrNum);
                if (bOver) {
                    writer.PrintMutable(L"\n", 1);
                }

                strPos += lineStrNum;
                remain -= lineStrNum;
            }
        }

        u16 TextBox::GetStringBufferLength() const {
            if (mTextBufBytes == 0) {
                return 0;
            }

            return mTextBufBytes / sizeof(wchar_t) - 1;
        }

        void TextBox::AllocStringBuffer(u16 minLen) {
            if (minLen == 0) {
                return;
            }

            const u32 allocBytes = (minLen + 1) * sizeof(wchar_t);

            if (allocBytes > mTextBufBytes) {
                FreeStringBuffer();
                mTextBuf = Layout::NewArray< wchar_t >(minLen + 1);

                if (mTextBuf != NULL) {
                    mTextBufBytes = allocBytes;
                }
            }
        }

        void TextBox::FreeStringBuffer() {
            if (mTextBuf != NULL) {
                Layout::DeletePrimArray(mTextBuf);
                mTextBuf = NULL;
                mTextBufBytes = 0;
            }
        }

        u16 TextBox::SetStringImpl(const wchar_t* pStr, u16 dstIdx, u32 strLen) {
            if (mTextBuf == NULL) {
                return 0;
            }

            const u16 bufLen = GetStringBufferLength();
            if (dstIdx >= bufLen) {
                return 0;
            }

            const u32 cpLen = ut::Min< u32 >(strLen, bufLen - dstIdx);
            memcpy(&mTextBuf[dstIdx], pStr, cpLen * sizeof(wchar_t));

            mTextLen = static_cast< u16 >(dstIdx + cpLen);
            mTextBuf[mTextLen] = L'\0';

            return static_cast< u16 >(cpLen);
        }

        u16 TextBox::SetString(const wchar_t* pStr, u16 dstIdx) {
            return SetStringImpl(pStr, dstIdx, wcslen(pStr));
        }

        u16 TextBox::SetString(const wchar_t* pStr, u16 dstIdx, u16 strLen) {
            return SetStringImpl(pStr, dstIdx, strLen);
        }

        const ut::Font* TextBox::GetFont() const {
            return mpFont;
        }

        void TextBox::SetFont(const ut::Font* pFont) {
            if (mBits.bAllocFont) {
                Layout::DeleteObj(const_cast< ut::Font* >(mpFont));
                mBits.bAllocFont = false;
            }

            mpFont = pFont;

            if (mpFont != NULL) {
                SetFontSize(Size(static_cast< f32 >(mpFont->GetWidth()), static_cast< f32 >(mpFont->GetHeight())));
            } else {
                SetFontSize(Size(0.0f, 0.0f));
            }
        }

        void TextBox::LoadMtx(const DrawInfo& drawInfo) {
            math::MTX34 mtx;

            if (drawInfo.IsMultipleViewMtxOnDraw()) {
                math::MTX34Mult(&mtx, &drawInfo.GetViewMtx(), &mGlbMtx);
            } else {
                math::MTX34Copy(&mtx, &mGlbMtx);
            }

            ReverseYAxis(&mtx);

            GXLoadPosMtxImm(mtx, GX_PNMTX0);
            GXSetCurrentMtx(GX_PNMTX0);
        }

        const ut::Rect TextBox::GetTextDrawRect(ut::WideTextWriter* pWriter) const {
            ut::Rect textRect;

            pWriter->SetCursor(0.0f, 0.0f);
            pWriter->SetFont(*mpFont);
            pWriter->SetFontSize(mFontSize.width, mFontSize.height);
            pWriter->SetLineSpace(mLineSpace);
            pWriter->SetCharSpace(mCharSpace);

            if (mpTagProcessor != NULL) {
                pWriter->SetTagProcessor(mpTagProcessor);
            }

            CalcStringRect(&textRect, pWriter, mTextBuf, mTextLen, mSize.width);

            const Size textSize(textRect.GetWidth(), textRect.GetHeight());
            math::VEC2 ltPos = GetVtxPos();

            ltPos.x += (mSize.width - textSize.width) * GetTextMagH();
            ltPos.y -= (mSize.height - textSize.height) * GetTextMagV();

            textRect.left = ltPos.x;
            textRect.top = ltPos.y;
            textRect.right = ltPos.x + textSize.width;
            textRect.bottom = ltPos.y - textSize.height;

            return textRect;
        }

        f32 TextBox::GetTextMagH() const {
            f32 mag;

            switch (GetTextPositionH()) {
            default:
            case 0:
                mag = 0.0f;
                break;
            case 1:
                mag = 0.5f;
                break;
            case 2:
                mag = 1.0f;
                break;
            }

            return mag;
        }

        f32 TextBox::GetTextMagV() const {
            f32 mag;

            switch (GetTextPositionV()) {
            default:
            case 0:
                mag = 0.0f;
                break;
            case 1:
                mag = 0.5f;
                break;
            case 2:
                mag = 1.0f;
                break;
            }

            return mag;
        }

        u32 TextBox::MakeDrawFlag() const {
            u32 flag = 0;

            switch (GetTextPositionH()) {
            case 1: {
                flag |= 1;
                break;
            }

            case 2: {
                flag |= 2;
                break;
            }

            default: {
                break;
            }
            }

            return flag;
        }

        f32 TextBox::GetTextAlignMag() const {
            switch (GetTextAlignment()) {
            case 0:
            default:
                return GetTextMagH();
            case 1:
                return 0;
            case 2:
                return 0.5f;
            case 3:
                return 1.0f;
            }
        }
    };  // namespace lyt
};  // namespace nw4r
