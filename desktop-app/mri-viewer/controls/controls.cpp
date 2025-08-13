#include "controls.h"
#include <GameEngine/Events/events.h>

Controller::Controller(float moveSpeed, float rotationSpeed) {
    this->moveSpeed = moveSpeed;
    this->rotationSpeed = rotationSpeed;
    for (int i = 0; i < 512; i++) {
        this->keyDown[i] = false;
    }
}

Controller::~Controller() {}

void Controller::setMoveSpeed(float speed) { this->moveSpeed = speed; }
void Controller::setRotationSpeed(float speed) { this->rotationSpeed = speed; }

float Controller::getMoveSpeed() { return this->moveSpeed; }
float Controller::getRotationSpeed() { return this->rotationSpeed; }

void Controller::handleEventFor(Actor &actor, Event &event, float deltaTime) {

    this->handled = false;
    if (keyDown[KEY_1]) {
        handled = true;
        glm::vec3 rotation = actor.getRotation();
        rotation[2] -= deltaTime * rotationSpeed;
        actor.setRotation(rotation);
    }

    if (keyDown[KEY_2]) {
        handled = true;
        glm::vec3 rotation = actor.getRotation();
        rotation[2] += deltaTime * rotationSpeed;
        actor.setRotation(rotation);
    }

    if (keyDown[KEY_LEFT]) {
        handled = true;
        glm::vec3 rotation = actor.getRotation();
        rotation[1] -= deltaTime * rotationSpeed;
        actor.setRotation(rotation);
    }

    if (keyDown[KEY_RIGHT]) {
        handled = true;
        glm::vec3 rotation = actor.getRotation();
        rotation[1] += deltaTime * rotationSpeed;
        actor.setRotation(rotation);
    }

    if (keyDown[KEY_DOWN]) {
        handled = true;
        glm::vec3 rotation = actor.getRotation();
        rotation[0] -= deltaTime * rotationSpeed;
        actor.setRotation(rotation);
    }

    if (keyDown[KEY_UP]) {
        handled = true;
        glm::vec3 rotation = actor.getRotation();
        rotation[0] += deltaTime * rotationSpeed;
        actor.setRotation(rotation);
    }

    if (keyDown[KEY_W]) {
        handled = true;
        glm::vec3 position = actor.getPosition();
        position[2] -= deltaTime * moveSpeed;
        actor.setPosition(position);
    }

    if (keyDown[KEY_S]) {
        handled = true;
        glm::vec3 position = actor.getPosition();
        position[2] += deltaTime * moveSpeed;
        actor.setPosition(position);
    }

    if (event.key.triggered) {
        if (event.key.keysym.key >= 0 && event.key.keysym.key < 512) {
            if (event.key.action == KEY_PRESSED) {
                keyDown[event.key.keysym.key] = true;
            }
            if (event.key.action == KEY_RELEASED) {
                keyDown[event.key.keysym.key] = false;
            }
        }
    }

    if (event.window.triggered) {
        this->handled = true;
    }
}
