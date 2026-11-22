// Health is its own interface that can be implemented, this way, objects as well
// as players can have health, so we can have things like targets, and obsticles that can
// be destroyed


#include <functional>
namespace pmatx::player::core
{

struct HealthInfo
{
    float currentPct;
    float currentPoints;
    float currentCapacity;
};

// Health callbacks return void, and accept the current health points, and percent
using HealthChangeCallback = std::function<void(const HealthInfo)>;

class IHealth
{
public:
    virtual void decrementHealth(const float amount);
    virtual void incrementHealth(const float amount);
    virtual float getHealthPoints();
    virtual float getHealthPct();
    virtual float getHealthCapacity(); // Total health they are allowed to have

    // Callback for UI and other to subscribe to. Returns a handle for unsubscribing
    // The implementation of this should only hold a weak pointer to the callback,
    // So we don't keep objects alive or call a stale function
    virtual int addHealthChangedCallback(HealthChangeCallback);
};
}
