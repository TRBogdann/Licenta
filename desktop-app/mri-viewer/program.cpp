

#include "slicer/slicer.h"
#include <GameEngine/Files/files.h>
#include <GameEngine/Graphics/graphics.h>
#include <cstdlib>
#include <glm/trigonometric.hpp>
#include <string>

int main() {
    Program program;
    program.start();
    Window window("MRI Analyzer", 800, 800);
    program.useWindow(window);

    Renderer renderer;
    Event event;

    if (program.CheckForError()) {
        return 1;
    }

    window.setColor(0, 100, 100, 255);

    float fov = 45.0f;
    float far = 1000.0f;
    float near = 5.0f;
    glm::vec3 position(0.0f, 0.0f, 0.0f);
    glm::vec3 axis[3] = {glm::vec3(1.0f, 0.0f, 0.0f),
                         glm::vec3(0.0f, 1.0f, 0.0f),
                         glm::vec3(0.0f, 0.0f, 1.0f)};

    std::string path = std::getenv("HOME");
    Camera camera(position, axis, fov, near, far);
    Slicer slicer(path + "/mri-res", 500, camera);
    ToolBar tools(window.getContext(), slicer.getNofSlices());

    float lastFrame = 0.0f;
    float deltaTime = 0.0f;

    while (!window.isClosed()) {
        renderer.clear();
        window.clear();
        float currentFrame = glfwGetTime();
        deltaTime = currentFrame - lastFrame;
        lastFrame = currentFrame;

        window.pollEvents(event);
        slicer.handleEvent(event, deltaTime);
        slicer.checkToolBar(tools);

        slicer.render(camera);
        tools.render(deltaTime);

        window.swap();
    }
    return 0;
}
