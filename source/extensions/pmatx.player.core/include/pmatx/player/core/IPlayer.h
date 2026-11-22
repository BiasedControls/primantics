#include "IHealth.h"

#include <pxr/usd/usd/prim.h>


namespace pmatx::player::core
{

class IPlayer : IHealth
{
public:
    virtual IHealth* getHealthData() const;
    virtual pxr::UsdPrim getPrim() const;
};
}
