#include "./tools.h"
#include <imgui.h>
#include <string>

ToolBar::ToolBar(GLFWwindow *context, int nOfSlices) {

    this->nOfSlices = nOfSlices;
    this->slicesX[0] = 0;
    this->slicesX[1] = nOfSlices - 1;
    this->slicesY[0] = 0;
    this->slicesY[1] = nOfSlices - 1;
    this->slicesZ[0] = 0;
    this->slicesZ[1] = nOfSlices - 1;

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO &io = ImGui::GetIO();
    (void)io;
    ImGui_ImplGlfw_InitForOpenGL(context, true);
    ImGui_ImplOpenGL3_Init("#version 330");
    ImGui::StyleColorsDark();
}

int ToolBar::currentMap = 0;
const char *ToolBar::cmaps[7] = {"normal", "viridis", "magma", "inferno",
                                 "plasma", "turbo",   "gray"};

void ToolBar::render(float deltatime) {
    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplGlfw_NewFrame();
    ImGui::NewFrame();

    this->innerTime += deltatime;
    if (innerTime > 1.0f) {
        FPS = 1.0f / deltatime;
        innerTime = 0.0f;
    }
    ImGui::Begin("Tools");
    ImGui::Text("FPS: %.1f", FPS);

    ImGui::SliderInt2("Slices X", slicesX, 0, this->nOfSlices);
    ImGui::SliderInt2("Slices Y", slicesY, 0, this->nOfSlices);
    ImGui::SliderInt2("Slices Z", slicesZ, 0, this->nOfSlices);

    const char *message = overlay ? "Turn Off Overlay" : "Turn On Overlay";
    overlay = ImGui::Button(message) ^ overlay;

    ImGui::Combo("Color Map", &currentMap, cmaps, IM_ARRAYSIZE(cmaps));
    ImGui::End();

    ImGui::Render();
    ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
}

ToolBar::~ToolBar() {
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
}

int ToolBar::getSliceIndex(unsigned int axis, unsigned char index) {
    if (axis == 0)
        return this->slicesX[index];

    if (axis == 1)
        return this->slicesY[index];

    if (axis == 2)
        return this->slicesZ[index];

    return 0;
}

int ToolBar::getCurrentMap() { return currentMap; }
