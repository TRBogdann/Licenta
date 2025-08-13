#pragma once
#include <GLFW/glfw3.h>
#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>
#include <vector>
//{"normal", "viridis", "magma", "inferno",
//                         "plasma", "turbo",   "gray"};

class ToolBar {
    public:
        ToolBar(GLFWwindow *context, int nOfSlices);
        ~ToolBar();
        void render(float deltatime);
        int getSliceIndex(unsigned int axis, unsigned char index);
        static int getCurrentMap();
        bool overlay = false;

    private:
        float innerTime = 0.0f;
        float FPS = 0.0f;
        int nOfSlices;
        int slicesX[2];
        int slicesY[2];
        int slicesZ[2];
        static int currentMap;
        static const char *cmaps[7];
};
