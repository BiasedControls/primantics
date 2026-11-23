#include "IHealth.h"


namespace pmatx::player::core
{

class IPlayer : public IHealth
{
public:
    ~IPlayer() = default;

    // Gets the prim including weapons, etc. Capsule is under the prim
    virtual void destroy() = 0;
    virtual const char* getCctPath() = 0;

    // virtual void setWeapon()
};
}
