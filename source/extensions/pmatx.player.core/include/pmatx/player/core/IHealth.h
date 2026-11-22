// Health is its own interface that can be implemented, this way, objects as well
// as players can have health, so we can have things like targets, and obsticles that can
// be destroyed


#include <cstdint>
#include <functional>

namespace pmatx::player::core
{

struct HealthInfo
{
    float currentPct;
    uint16_t currentPoints;
    uint16_t currentCapacity;
};

// Health callbacks return void, and accept the current health points, and percent
using HealthChangeCallback = std::function<void(const HealthInfo)>;

class IHealth
{
public:
    virtual ~IHealth() = default;
    virtual void decrementHealth(const uint16_t amount) = 0;
    virtual void incrementHealth(const uint16_t amount) = 0;
    virtual uint16_t getHealthPoints() const = 0;
    virtual float getHealthPct() const = 0;

    // Callback for UI and other to subscribe to.
    // The implementation of this should only hold a weak pointer to the callback,
    // So we don't keep objects alive or call a stale function
    virtual uint64_t addHealthChangedCallback(HealthChangeCallback) = 0;
    virtual void removeHealthChangedCallback(uint64_t id) = 0;
};
}
