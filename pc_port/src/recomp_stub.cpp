// Used when no main.dol was available at configure time: an empty lifted-code registry.
#include "dispatch.hpp"

void g2c_register_all() {}

const g2c::SymbolEntry g2c_symbols[] = {{nullptr, 0}};
const std::size_t g2c_symbol_count = 0;
const char* const g2c_lift_stats = "no lifted code (configure with -DG2C_DOL=<path to your main.dol>)";
