#include "IHealth.h"

#include <pxr/usd/usd/prim.h>


namespace pmatx::player::core
{

class IPlayer : public IHealth
{
public:
    virtual pxr::UsdPrim getPrim() const = 0;
    virtual void destroy() = 0;

    // virtual void setWeapon()
};
}
