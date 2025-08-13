#pragma once
#include <GameEngine/Events/events.h>
#include <GameEngine/Graphics/camera.h>
#include <GameEngine/Graphics/mesh.h>

class Controller {
    public:
        Controller(float moveSpeed = 1.0f, float rotationSpeed = 1.0f);
        ~Controller();
        void handleEventFor(Actor &actor, Event &event, float deltaTime);

        void setRotationSpeed(float speed);
        void setMoveSpeed(float speed);

        float getMoveSpeed();
        float getRotationSpeed();

        bool handled = false;

    private:
        float rotationSpeed;
        float moveSpeed;
        bool keyDown[512];
};
