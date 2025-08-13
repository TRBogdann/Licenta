#include "controls/controls.h"
// #include "slicer/slicer.h"
#include "./cpu-math/math.h"
#include "./tools/tools.h"
#include <GameEngine/Files/files.h>
#include <GameEngine/Graphics/buffers/buffers.h>
#include <GameEngine/Graphics/graphics.h>
#include <GameEngine/Graphics/macros.h>
#include <GameEngine/Graphics/program/program.h>
#include <GameEngine/Graphics/renderer/renderer.h>
#include <GameEngine/Graphics/shaders/shaders.h>
#include <GameEngine/Graphics/surface/surface.h>
#include <charconv>
#include <fstream>
#include <glm/trigonometric.hpp>
#include <iomanip>
#include <sstream>
#include <string>

std::string numberToFile(int number) {
    std::ostringstream ss;
    ss << "slice_" << std::setw(3) << std::setfill('0') << number << ".png";
    return ss.str();
}

void updateMesh(Mesh *mesh, float value, unsigned int offset,
                unsigned int vertexSize, bool updateImediatly = true) {
    unsigned int size = mesh->getDataSize();
    float *data = mesh->Data();
    if (size <= 0 && !data)
        return;

    for (int i = 0; i < size; i += vertexSize) {
        data[i + offset] = value;
    }

    if (updateImediatly) {
        mesh->refresh();
    }
}

void rotateModel(Mesh *mesh, unsigned int vertexSize, Math::vec3f axis,
                 float angle, bool updateImediatly = true) {
    unsigned int size = mesh->getDataSize();
    float *data = mesh->Data();
    if (size <= 0 && !data)
        return;

    for (int i = 0; i < size; i += vertexSize) {
        Math::vec3f temp(data[i + 0], data[i + 1], data[i + 2]);
        Math::rotate3F(temp, axis, angle);
        data[i + 0] = temp.x;
        data[i + 1] = temp.y;
        data[i + 2] = temp.z;
    }

    if (updateImediatly) {
        mesh->refresh();
    }
}

void drawSlices(Renderer &renderer, Shader &sliceShader, Mesh *sliceMesh,
                Actor &brain, Camera &camera, unsigned int sliceIndex,
                unsigned int axisIndex) {
    if (axisIndex > 2)
        return;
    float angle = glm::radians(90.0f);
    float th = -1.0f + (2.0f * sliceIndex) / 239.0f;
    std::string path = "../slices/axis_" + std::to_string(2 - axisIndex) + "/" +
                       numberToFile(sliceIndex);
    Texture t1(path, 0, 1);
    t1.bind();
    Actor slice(brain.getPosition(), brain.getScale());
    slice.setRotation(brain.getRotation());
    slice.setUniqueShader(&sliceShader);
    updateMesh(sliceMesh, th, axisIndex, 5);
    renderer.draw(slice, *sliceMesh, camera);
}
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
    ToolBar tools(window.getContext());

    glDisable(GL_CULL_FACE);
    glDepthFunc(GL_LEQUAL);
    float fov = 45.0f;
    float far = 1000.0f;
    float near = 5.0f;
    glm::vec3 position(0.0f, 0.0f, 0.0f);
    glm::vec3 axis[3] = {glm::vec3(1.0f, 0.0f, 0.0f),
                         glm::vec3(0.0f, 1.0f, 0.0f),
                         glm::vec3(0.0f, 0.0f, 1.0f)};

    Camera camera(position, axis, fov, near, far);

    std::ifstream vertexBrainFile("./shaders/brain/vertex.glsl");
    std::ifstream fragmentBrainFile("./shaders/brain/fragment.glsl");
    std::string vertexBrainShader = FileToString(vertexBrainFile);
    std::string fragmentBrainShader = FileToString(fragmentBrainFile);

    std::ifstream vertexSliceFile("./shaders/slice/vertex.glsl");
    std::ifstream fragmentSliceFile("./shaders/slice/fragment.glsl");
    std::string vertexSliceShader = FileToString(vertexSliceFile);
    std::string fragmentSliceShader = FileToString(fragmentSliceFile);

    Shader brainShader(vertexBrainShader, fragmentBrainShader);
    Shader sliceShader(vertexSliceShader, fragmentSliceShader);
    GraphicalAtribute *atributes =
        GraphicalAtribute::getCreator()->createAtributes(SHADER_COLOR,
                                                         COORDINATES_XYZ);
    unsigned int nOfAtributes =
        GraphicalAtribute::getCreator()->getNOfAtributes();
    Shader *colorShader = Shader::getCreator()->createShader(
        CLIP_MODEL_SHADER, SHADER_COLOR, COORDINATES_XYZ);
    brainShader.bind();
    brainShader.setUniform4f("mnPoz", -1.0f, -1.0f, -1.0f, 0.0f);
    brainShader.setUniform4f("mxPoz", 1.0f, 1.0f, 1.0f, 0.0f);
    brainShader.setUniform1f("cmapIndex", 0.0f);

    Mesh *brain_mesh = Mesh::loadMesh("brain.obj", ENGINE_SIMPLE_FILE_FORMAT,
                                      &brainShader, nOfAtributes, atributes);

    Actor brain({0.0f, 0.0f, 50.0f}, {10.0f, 10.0f, 10.0f});
    Actor brain2({0.0f, 0.0f, 100.0f}, {10.0f, 10.0f, 10.0f});

    Shader *textureShader = Shader::getCreator()->createShader(
        CLIP_MODEL_SHADER, SHADER_TEXTURE, COORDINATES_XYZ);

    sliceShader.bind();
    sliceShader.setUniform4f("mnPoz", -1.0f, -1.0f, -1.0f, 0.0f);
    sliceShader.setUniform4f("mxPoz", 1.0f, 1.0f, 1.0f, 0.0f);
    sliceShader.setUniform1f("cmapIndex", 0.0f);
    sliceShader.setUniform1f("axis", 0.0f);
    // Slicer slicer(240, 100, colorShader, textureShader);

    Mesh *slices0 = Surface::generateFlatConstantSurface(
        500, 500, textureShader, SHADER_TEXTURE, true);
    Mesh *slices1 = Surface::generateFlatConstantSurface(
        500, 500, textureShader, SHADER_TEXTURE, true);
    rotateModel(slices1, 5, {1.0f, 0.0f, 0.0f}, 90.0f);
    Mesh *slices2 = Surface::generateFlatConstantSurface(
        500, 500, textureShader, SHADER_TEXTURE, true);
    rotateModel(slices2, 5, {1.0f, 0.0f, 0.0f}, 180.0f, false);
    rotateModel(slices2, 5, {0.0f, 0.0f, 1.0f}, 90.f);
    // Actor slice({0.0f, 0.0f, 60.0f}, {10.0f, 10.0f, 10.0f});
    // slice.setRotation({90.0f, 0.0f, 0.0f});
    Controller controller(20.0f, 5.0f);
    float lastFrame = 0.0f;
    float deltaTime = 0.0f;
    Texture t1("../slices/axis_0/slice_069.png", 0, 1);
    t1.bind(1);

    while (!window.isClosed()) {
        renderer.clear();
        window.clear();
        float currentFrame = glfwGetTime();
        deltaTime = currentFrame - lastFrame;
        lastFrame = currentFrame;

        window.pollEvents(event);
        controller.handleEventFor(brain, event, deltaTime);
        // slicer.handleEvent(event);

        float thXLeft = -1.0f + (2.0f * 1.0f) / 239.0f;
        float thYLeft = -1.0f + (2.0f * 1.0f) / 239.0f;
        float thZLeft = -1.0f + (2.0f * 1.0f) / 239.0f;

        float thXRight = -1.0f + (2.0f * 1.0f) / 239.0f;
        float thYRight = -1.0f + (2.0f * 1.0f) / 239.0f;
        float thZRight = -1.0f + (2.0f * 1.0f) / 239.0f;
        /*
        brainShader.bind();
        brainShader.setUniform4f("mnPoz", thXLeft, thYLeft, thZLeft, -1.0f);
        brainShader.setUniform4f("mxPoz", thXRight, thYRight, thZRight, 1.0f);
        */
        renderer.draw(brain, *brain_mesh, camera);

        /*

            sliceShader.bind();
            sliceShader.setUniform4f("mnPoz", thXLeft, thYLeft, -1.0f, 1.0f);
            sliceShader.setUniform4f("mxPoz", thXRight, thYRight,

                                     1.0f, 1.0f);

            sliceShader.setUniform1f("axis", 0.2f);
            sliceShader.setUniform1f("direction", -1.0f);
            // sliceShader.setUniform1i("textureSampler", 1);
            drawSlices(renderer, sliceShader, slices1, brain, camera,
           slicesZ[0], 2); sliceShader.setUniform1f("direction", 1.0f);

            drawSlices(renderer, sliceShader, slices1, brain, camera,
           slicesZ[1], 2);

            sliceShader.setUniform1f("axis", 0.1f);
            sliceShader.setUniform1f("direction", -1.0f);

            sliceShader.setUniform4f("mnPoz", thXLeft, -1.0f, thZLeft, 1.0f);
            sliceShader.setUniform4f("mxPoz", thXRight, 1.0f, thZRight, 1.0f);

            drawSlices(renderer, sliceShader, slices0, brain, camera,
           slicesY[0], 1); sliceShader.setUniform1f("direction", 1.0f);

            drawSlices(renderer, sliceShader, slices0, brain, camera,
           slicesY[1], 1);

            sliceShader.setUniform4f("mnPoz", -1.0f, thYLeft, thZLeft, 1.0f);
            sliceShader.setUniform4f("mxPoz", 1.0f, thYRight, thZRight, 1.0f);
            sliceShader.setUniform1f("axis", 0.0f);
            sliceShader.setUniform1f("direction", -1.0f);

            drawSlices(renderer, sliceShader, slices2, brain, camera,
           slicesX[0], 0); sliceShader.setUniform1f("direction", 1.0f);
            drawSlices(renderer, sliceShader, slices2, brain, camera,
           slicesX[1], 0);
          */
        tools.render();
        window.swap();
    }

    program.terminate();
    return 0;
}
