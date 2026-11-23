#include "runtime/cpu_context.h"

extern "C" void OSReport(nwii::runtime::CPUContext&);
extern "C" void IOS_Open(nwii::runtime::CPUContext&);
extern "C" void IOS_Ioctl(nwii::runtime::CPUContext&);
extern "C" void IOS_IoctlAsync(nwii::runtime::CPUContext&);
extern "C" void IOS_Ioctlv(nwii::runtime::CPUContext&);
extern "C" void IOS_IoctlvAsync(nwii::runtime::CPUContext&);

#define HLE_SHIM(fn, target)                                                  \
    void fn(nwii::runtime::CPUContext& ctx) { target(ctx); }

HLE_SHIM(func_80333190, OSReport)
HLE_SHIM(func_80338E80, OSReport)
HLE_SHIM(func_8039B750, OSReport)
HLE_SHIM(func_8039B820, OSReport)
HLE_SHIM(func_803CFC20, OSReport)
HLE_SHIM(func_8040BC50, OSReport)
HLE_SHIM(func_8040F720, OSReport)
HLE_SHIM(func_8044BFD0, OSReport)
HLE_SHIM(func_8047D8E0, OSReport)
HLE_SHIM(func_8056EC30, OSReport)

HLE_SHIM(func_80559600, IOS_Open)
HLE_SHIM(func_80559E90, IOS_IoctlAsync)
HLE_SHIM(func_80559FD0, IOS_Ioctl)
HLE_SHIM(func_80568200, IOS_IoctlvAsync)
HLE_SHIM(func_80568310, IOS_IoctlvAsync)
HLE_SHIM(func_80568400, IOS_Ioctlv)
HLE_SHIM(func_80568520, IOS_Ioctlv)
HLE_SHIM(func_80568B60, IOS_Ioctlv)
