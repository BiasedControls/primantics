// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include <pmatx/player/core/IPmatxPlayerCoreInterface.h>
#include <pmatx/player/core/PmatxPlayerCoreObject.h>

#include <doctest/doctest.h>

#include <carb/BindingsUtils.h>

CARB_BINDINGS("pmatx.player.core.tests")

namespace pmatx::player::core
{

class ExampleCppObject : public PmatxPlayerCoreObject
{
public:
    static carb::ObjectPtr<IPmatxPlayerCoreObjectInterface> create(const char* id)
    {
        return carb::stealObject<IPmatxPlayerCoreObjectInterface>(new ExampleCppObject(id));
    }

    ExampleCppObject(const char* id)
        : PmatxPlayerCoreObject(id)
    {
    }
};

class ExamplePybindTestFixture
{
public:
    static constexpr const char* k_registeredObjectId = "example_bound_object";

    ExamplePybindTestFixture()
        : m_exampleBoundInterface(carb::getCachedInterface<pmatx::player::core::IPmatxPlayerCoreInterface>())
        , m_PmatxPlayerCoreObject(ExampleCppObject::create(k_registeredObjectId))
    {
        m_exampleBoundInterface->registerPmatxPlayerCoreObject(m_PmatxPlayerCoreObject);
    }

    ~ExamplePybindTestFixture()
    {
        m_exampleBoundInterface->deregisterPmatxPlayerCoreObject(m_PmatxPlayerCoreObject);
    }

protected:
    IPmatxPlayerCoreInterface* getExampleBoundInterface()
    {
        return m_exampleBoundInterface;
    }

    carb::ObjectPtr<IPmatxPlayerCoreObjectInterface> getPmatxPlayerCoreObject()
    {
        return m_PmatxPlayerCoreObject;
    }

private:
    IPmatxPlayerCoreInterface* m_exampleBoundInterface = nullptr;
    carb::ObjectPtr<IPmatxPlayerCoreObjectInterface> m_PmatxPlayerCoreObject;
};

}

TEST_SUITE("pmatx.player.core.tests")
{
    using namespace pmatx::player::core
;

    TEST_CASE_FIXTURE(ExamplePybindTestFixture, "Get Example Bound Interface")
    {
        CHECK(getExampleBoundInterface() != nullptr);
    }

    TEST_CASE_FIXTURE(ExamplePybindTestFixture, "Get Example Bound Object")
    {
        CHECK(getPmatxPlayerCoreObject().get() != nullptr);
    }

    TEST_CASE_FIXTURE(ExamplePybindTestFixture, "Find Example Bound Object")
    {
        SUBCASE("Registered")
        {
            carb::ObjectPtr<IPmatxPlayerCoreObjectInterface> foundObject = getExampleBoundInterface()->findPmatxPlayerCoreObject(k_registeredObjectId);
            CHECK(foundObject.get() == getPmatxPlayerCoreObject().get());
            CHECK(foundObject.get() != nullptr);
        }

        SUBCASE("Unregistered")
        {
            carb::ObjectPtr<IPmatxPlayerCoreObjectInterface> foundObject = getExampleBoundInterface()->findPmatxPlayerCoreObject("unregistered_object_id");
            CHECK(foundObject.get() != getPmatxPlayerCoreObject().get());
            CHECK(foundObject.get() == nullptr);
        }
    }
}
